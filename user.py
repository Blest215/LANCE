import asyncio

from langchain_core.prompts import ChatPromptTemplate

from settings import *
from client import Client
from device import *

initiate_task_tool = {
    'type': 'function',
    'function': {
        'name': 'initiate_task',
        'description': 'initiate a new task',
        'parameters': {
            'type': 'object',
            'required': ['message'],
            'properties': {
                'message': {'type': 'string', 'description': 'a fluent message describing the requirements for the task'},
            },
        },
    },
}

ask_agent_tool = {
    'type': 'function',
    'function': {
        'name': 'ask_agent',
        'description': 'send a natural language message to a specific agent for asking device control',
        'parameters': {
            'type': 'object',
            'required': ['agent_id', 'message'],
            'properties': {
                'agent_id': {'type': 'string', 'description': 'the ID of the agent to call'},
                'message': {'type': 'string', 'description': 'the message to send to the agent'},
            },
        },
    },
}

control_device_tools = [W3CDevice.get_tool(), SmartThingsDevice.get_tool(), MatterDevice.get_tool()]


class UserAgent(Client):
    def __init__(self, session, id, model):
        super().__init__(session, id)
        # TODO multi user situation
        self.configuration = model
        self.wait = set()
        self.agents = set()

        # LANCE
        self.organizer = ChatPromptTemplate.from_template(ORGANIZER_PROMPT)| model.with_tools([initiate_task_tool])
        self.coordinator = ChatPromptTemplate.from_template(COORDINATOR_PROMPT) | model.with_tools([ask_agent_tool])
        # NATURAL
        self.natural = ChatPromptTemplate.from_template(MASTERMIND_PROMPT) | model.with_tools([ask_agent_tool])
        # CENTRALIZED
        self.centralized = ChatPromptTemplate.from_template(MASTERMIND_PROMPT) | model.with_tools(control_device_tools)

    async def command(self, mode, user_command):
        self.log(f"User asked: {user_command}")
        
        try:
            result = None
            if mode == "LANCE":
                result = await self.organizer.ainvoke({"user_command": user_command})
            
            elif mode == "NATURAL":
                result = await self.natural.ainvoke({"user_command": user_command, "device_descriptions": await self.discovery()})

            elif mode == "CENTRALIZED":
                result = await self.centralized.ainvoke({"user_command": user_command, "device_descriptions": await self.discovery()})
            
            elif mode == "ONTOLOGY":
                pass

            await self.tool_call(result)
        
        except Exception as e:
            self.log(type(e).__name__)
        
        finally:
            return "\n".join(self.logs), self.consequences

    async def connection_handler(self):
        await self.subscribe(MQTT_TOPIC_ALIVE, "+")

    async def message_handler(self, topic, id, sender, message, request_id):
        if check_topic(topic, MQTT_TOPIC_ALIVE):
            if id in self.wait:
                if id != "REGISTRY":
                    self.agents.add(id)
                self.wait.remove(id)

        elif check_topic(topic, MQTT_TOPIC_LANCE_TEAM) and id == self.current_team_id:
            text = f"Agent {sender} suggested: {message}"
            self.log(text)
            self.team_messages.append(text)

        elif check_topic(topic, MQTT_TOPIC_RESPONSE):
            if request_id and request_id in self.requests:
                self.requests[request_id]["status"] = "done"
                self.requests[request_id]["response"] = message

    # LANCE methods

    async def initiate_task(self, message):
        self.log(f"Initiate a new task: {message}")
        await self.call_for_proposal(20, message)
        # TODO Negotiation
        await self.control(self.team_messages)

    async def call_for_proposal(self, time_to_wait, message):
        self.log(f"Agent call-for-proposal start ({time_to_wait}s)")
        self.current_team_id = get_random_team_id()
        await self.subscribe(MQTT_TOPIC_LANCE_TEAM, self.current_team_id)
        await self.publish(MQTT_TOPIC_LANCE_CALL, self.current_team_id, message)
        self.team_messages = [message]
        await asyncio.sleep(time_to_wait)
        self.log("Agent call-for-proposal end")

    async def control(self, team_messages):        
        result = await self.coordinator.ainvoke({"user_command": team_messages[0], "team_messages": "\n".join(team_messages[1:])})
        await self.tool_call(result)

    # NATURAL methods

    async def ask_agent(self, agent_id, message):
        self.consequences += eval(await self.request(MQTT_TOPIC_NATURAL_AGENT, agent_id, message))

    # CENTRALIZED methods

    async def discovery(self):
        return await self.request(MQTT_TOPIC_CENTRALIZED_DISCOVERY, "REGISTRY", "")

    async def control_device(self, agent_id, **kwargs):
        self.consequences += eval(await self.request(MQTT_TOPIC_CENTRALIZED_CONTROL, agent_id, kwargs))
    
    async def control_device_w3c(self, agent_id, **kwargs):
        await self.control_device(agent_id, **kwargs)
    
    async def control_device_smartthings(self, agent_id, **kwargs):
        await self.control_device(agent_id, **kwargs)
    
    async def control_device_matter(self, agent_id, **kwargs):
        await self.control_device(agent_id, **kwargs)
    
    # etc

    async def wait_for_client(self, client_id):
        self.wait.add(client_id)
        while client_id in self.wait:
            await asyncio.sleep(TICK)

    async def tool_call(self, result):
        await asyncio.gather(*[getattr(self, tool_call["name"])(**tool_call["args"]) for tool_call in result.tool_calls if hasattr(self, tool_call["name"])] if result and hasattr(result, "tool_calls") else [], return_exceptions=True)

    async def new_session(self, new_session):
        old_session = self.session
        await self.reset(new_session)
        await self.client.publish(f"{old_session}/{MQTT_TOPIC_RESET}/{'REGISTRY'}", json.dumps({"sender": self.id, "message": new_session}))
        await self.wait_for_client("REGISTRY")
        agents = self.agents
        for agent_id in agents:
            await self.client.publish(f"{old_session}/{MQTT_TOPIC_RESET}/{agent_id}", json.dumps({"sender": self.id, "message": new_session}))
            await self.wait_for_client(agent_id)
        self.agents = agents
