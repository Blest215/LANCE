import asyncio

from datetime import datetime
from langchain_core.prompts import ChatPromptTemplate

from settings import *
from utils import *
from client import Client
from device import W3CDevice, SmartThingsDevice

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

control_device_tools = [W3CDevice.get_tool(), SmartThingsDevice.get_tool()]


class UserAgent(Client):
    def __init__(self, session, id, model):
        super().__init__(session, id)
        # TODO multi user situation
        self.configuration = model
        self.current_team_id = None
        self.team_messages = []
        self.wait = set()
        self.logs = []

        # LANCE
        self.organizer = ChatPromptTemplate.from_template(ORGANIZER_PROMPT)| model.with_tools([initiate_task_tool])
        self.coordinator = ChatPromptTemplate.from_template(COORDINATOR_PROMPT) | model.with_tools([ask_agent_tool])
        # NATURAL
        self.natural = ChatPromptTemplate.from_template(MASTERMIND_PROMPT) | model.with_tools([ask_agent_tool])
        # CENTRALIZED
        self.centralized = ChatPromptTemplate.from_template(MASTERMIND_PROMPT) | model.with_tools(control_device_tools)

        self.client.loop_start()

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
            
            elif mode == "CLOUD":
                pass
            
            elif mode == "ONTOLOGY":
                pass

            await self.tool_call(result)
        
        except Exception as e:
            self.log(type(e).__name__)
        
        finally:
            await asyncio.sleep(TIMEOUT_LIMIT)
            logs = self.logs
            self.logs = []
            return "\n".join(logs)

    def connection_handler(self):
        self.subscribe(MQTT_TOPIC_ALIVE, "+")
        self.subscribe(MQTT_TOPIC_LOG, "+")

    async def message_handler(self, topic, id, sender, message, request_id=""):
        if check_topic(topic, MQTT_TOPIC_ALIVE):
            if id in self.wait:
                self.wait.remove(id)

        elif check_topic(topic, MQTT_TOPIC_LOG):
            self.logs.append(f"[{datetime.now().strftime('%Y%m%d_%H%M%S')}] {sender}: {message}")

        elif check_topic(topic, MQTT_TOPIC_LANCE_TEAM) and id == self.current_team_id:
            self.team_messages.append(f"{sender}: {message}")

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
        self.subscribe(MQTT_TOPIC_LANCE_TEAM, self.current_team_id)
        self.publish(MQTT_TOPIC_LANCE_CALL, self.current_team_id, message)
        self.team_messages = [message]
        await asyncio.sleep(time_to_wait)
        self.log("Agent call-for-proposal end")

    async def control(self, team_messages):        
        result = await self.coordinator.ainvoke({"user_command": team_messages[0], "team_messages": "\n".join(team_messages[1:])})
        await self.tool_call(result)

    # NATURAL methods

    async def ask_agent(self, agent_id, message):
        return await self.request(MQTT_TOPIC_NATURAL_AGENT, agent_id, message)

    # CENTRALIZED methods

    async def discovery(self):
        return await self.request(MQTT_TOPIC_CENTRALIZED_DISCOVERY, "REGISTRY", "")

    async def control_device(self, agent_id, **kwargs):
        return await self.request(MQTT_TOPIC_CENTRALIZED_CONTROL, agent_id, kwargs)
    
    async def control_device_w3c(self, agent_id, **kwargs):
        return await self.control_device(agent_id, **kwargs)
    
    async def control_device_smartthings(self, agent_id, **kwargs):
        return await self.control_device(agent_id, **kwargs)
    
    # etc

    async def wait_for_client(self, client_id):
        assert self.client.is_connected()
        self.wait.add(client_id)
        while client_id in self.wait:
            await asyncio.sleep(TICK)

    async def tool_call(self, result):
        await asyncio.gather(*[getattr(self, tool_call["name"])(**tool_call["args"]) for tool_call in result.tool_calls if hasattr(self, tool_call["name"])] if result and hasattr(result, "tool_calls") else [], return_exceptions=True)
