import asyncio

from langchain_core.prompts import ChatPromptTemplate

from settings import *
from client import Client
from device import *

class AgentInput(BaseModel):
    agent_id: str = Field(description="the ID of the agent associated with the device to control")
    message: str = Field(description="the instructing message to send to the agent")

@tool("control_device_agent", args_schema=AgentInput)
def control_device_agent(agent_id: str, message: str):
    """Control a device by sending a message to the associated agent."""

control_device_tools = [W3CDevice.get_tool(), SmartThingsDevice.get_tool(), MatterDevice.get_tool()]


class UserAgent(Client):
    def __init__(self, session, id, model):
        super().__init__(session, id)
        # TODO multi user situation
        self.configuration = model
        self.wait = set()
        self.agents = set()

        # NATURAL
        self.natural = ChatPromptTemplate.from_template(COORDINATOR_PROMPT) | model.with_tools([control_device_agent])
        # CENTRALIZED
        self.centralized = ChatPromptTemplate.from_template(COORDINATOR_PROMPT) | model.with_tools(control_device_tools)

    async def command(self, mode, user_command):
        self.log(f"User asked: {user_command}")
        
        try:
            if mode == "CENTRALIZED":
                await self.control_device(await self.centralized.ainvoke({"user_command": user_command, "descriptions": await self.discovery()}))
            
            elif mode == "NATURAL":
                await self.instruct_agent(await self.natural.ainvoke({"user_command": user_command, "descriptions": await self.discovery()}))
            
            elif mode == "RECRUIT":
                await self.control_device(await self.centralized.ainvoke({"user_command": user_command, "descriptions": await self.recruit_team(user_command)}))
            
            elif mode == "CONVERSATIONAL":
                pass
        
        except Exception as e:
            self.log(e)
        
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

        elif check_topic(topic, MQTT_TOPIC_RECRUIT_TEAM) and id == self.current_team_id:
            text = f"{message}"
            self.log(text)
            self.team_messages.append(text)

        elif check_topic(topic, MQTT_TOPIC_RESPONSE):
            if request_id and request_id in self.requests:
                self.requests[request_id]["status"] = "done"
                self.requests[request_id]["response"] = message

    # RECRUIT methods

    async def recruit_team(self, user_command):
        self.log(f"Agent recruiting start for user command: {user_command} ({RECRUIT_TIME_TO_WAIT}s)")
        await self.join_team(get_random_team_id())
        await self.publish(MQTT_TOPIC_RECRUIT_CALL, self.current_team_id, f"Can you contribute to the following user command?: {user_command}")

        await asyncio.sleep(RECRUIT_TIME_TO_WAIT)

        self.log("Agent recruiting end")
        await self.leave_team()

        return "\n".join(self.team_messages)

    # NATURAL methods

    async def instruct_agent(self, result):
        self.log_result(result)
        self.consequences += sum(await asyncio.gather(*[self.control(MQTT_TOPIC_NATURAL_CONTROL, **tool_call["args"]) for tool_call in result.tool_calls]), []) if hasattr(result, "tool_calls") else []

    # CENTRALIZED methods

    async def discovery(self):
        return "\n".join(eval(await self.request(MQTT_TOPIC_CENTRALIZED_DISCOVERY, "REGISTRY", "")).values())

    async def control_device(self, result):
        self.log_result(result)
        self.consequences += sum(await asyncio.gather(*[self.control(MQTT_TOPIC_STRUCTURED_CONTROL, **tool_call["args"]) for tool_call in result.tool_calls]), []) if hasattr(result, "tool_calls") else []
    
    # etc

    def log_result(self, result):
        if hasattr(result, "content") and result.content:
            self.log(result.content)
        if hasattr(result, "additional_kwargs") and "reasoning_content" in result.additional_kwargs:
            self.log(f"<Reasoning> {result.additional_kwargs['reasoning_content']}")
        if hasattr(result, "tool_calls"):
            self.log(f"<Tool calls> {result.tool_calls}")

    async def control(self, topic, agent_id, **kwargs):
        return eval(await self.request(topic, agent_id, kwargs))

    async def wait_for_client(self, client_id):
        self.wait.add(client_id)
        while client_id in self.wait:
            await asyncio.sleep(TICK)

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
