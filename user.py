import asyncio
import time

from settings import *
from client import Client
from device import *

class MessageInput(BaseModel):
    agent_id: str = Field(description="The unique ID of the agent associated with the device to control")
    instruction: str = Field(description="A natural language instruction describing the task or action to perform on the device")

@tool("control_device", args_schema=MessageInput)
def control_device(agent_id: str, instruction: str):
    """Send an instruction to an agent to control its device. Use this tool to control devices."""

control_device_tools = [W3CDevice.get_tool(), SmartThingsDevice.get_tool(), MatterDevice.get_tool()]


class UserAgent(Client):
    def __init__(self, id, model):
        super().__init__(id)
        # TODO multi user situation
        self.configuration = model
        self.agents = set()

        self.time = {"discovery": [], "plan": [], "control": []}

        # NATURAL
        self.natural = COORDINATOR_PROMPT | model.with_tools([control_device])
        # CENTRALIZED
        self.centralized = COORDINATOR_PROMPT | model.with_tools(control_device_tools)

    def set_agents(self, agents):
        self.agents = set(agents)

    async def main(self, mode, user_message):
        self.log(f"User asked: {user_message}")
        
        try:
            if mode == "CENTRALIZED":
                await self.control(MQTT_TOPIC_STRUCTURED_CONTROL, await self.plan(self.centralized, user_message, await self.discovery()))
            
            elif mode == "NATURAL":
                await self.control(MQTT_TOPIC_NATURAL_CONTROL, await self.plan(self.natural, user_message, await self.discovery()))
            
            elif mode == "RECRUIT":
                await self.control(MQTT_TOPIC_STRUCTURED_CONTROL, await self.plan(self.centralized, user_message, await self.recruit(user_message, False)))
            
            elif mode == "CONVERSATIONAL":
                await self.control(MQTT_TOPIC_NATURAL_CONTROL, await self.plan(self.natural, user_message, await self.recruit(user_message, True)))
        
        except Exception as e:
            self.consequences.append(dict(Response(agent_id="", request={}, success=False, message=type(e).__name__)))
            self.log(e)
        
        finally:
            time_log = self.time
            self.time = {"discovery": [], "plan": [], "control": []}
            return "\n".join(self.logs), self.consequences, time_log

    async def plan(self, model, user_message, descriptions):
        start = time.time()
        result = await model.ainvoke({"user_message": user_message, "descriptions": descriptions})
        self.time["plan"].append(time.time() - start)
        return result

    # RECRUIT methods

    async def recruit(self, user_message, conversational):
        return "\n".join([await self.call_for_proposal(MQTT_TOPIC_CONVERSATIONAL_CALL if conversational else MQTT_TOPIC_RECRUIT_CALL, agent_id, user_message) for agent_id in self.agents])

    async def call_for_proposal(self, topic, agent_id, user_message):
        start = time.time()
        response = await self.request(topic, agent_id, user_message)
        self.time["discovery"].append(time.time() - start)
        return response

    # CENTRALIZED methods

    async def discovery(self):
        start = time.time()
        response = await self.request(MQTT_TOPIC_CENTRALIZED_DISCOVERY, REGISTRY_ID, "")
        self.time["discovery"].append(time.time() - start)
        return "\n".join(eval(response).values())
    
    # etc

    def log_result(self, result):
        if hasattr(result, "content") and result.content:
            self.log(result.content)
        if hasattr(result, "additional_kwargs") and "reasoning_content" in result.additional_kwargs:
            self.log(f"<Reasoning> {result.additional_kwargs['reasoning_content']}")
        if hasattr(result, "tool_calls"):
            self.log(f"<Tool calls> {result.tool_calls}")

    async def control(self, topic, result):
        self.log_result(result)
        if hasattr(result, "tool_calls"):
            for tool_call in result.tool_calls:
                if "agent_id" not in tool_call["args"]:
                    self.consequences.append(dict(Response(agent_id="", request=tool_call["args"], success=False, message="NO AGENT ID")))
                else:
                    self.consequences += await self.control_device(topic, **tool_call["args"])

    async def control_device(self, topic, agent_id, **kwargs):
        start = time.time()
        response = await self.request(topic, agent_id, kwargs)
        self.time["control"].append(time.time() - start)
        return eval(response)
