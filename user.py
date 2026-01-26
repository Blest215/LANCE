import asyncio

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
                await self.control_device(MQTT_TOPIC_STRUCTURED_CONTROL, await self.centralized.ainvoke({"user_message": user_message, "descriptions": await self.discovery()}))
            
            elif mode == "NATURAL":
                await self.control_device(MQTT_TOPIC_NATURAL_CONTROL, await self.natural.ainvoke({"user_message": user_message, "descriptions": await self.discovery()}))
            
            elif mode == "RECRUIT":
                await self.control_device(MQTT_TOPIC_STRUCTURED_CONTROL, await self.centralized.ainvoke({"user_message": user_message, "descriptions": await self.recruit(user_message, False)}))
            
            elif mode == "CONVERSATIONAL":
                await self.control_device(MQTT_TOPIC_NATURAL_CONTROL, await self.natural.ainvoke({"user_message": user_message, "descriptions": await self.recruit(user_message, True)}))
        
        except Exception as e:
            self.log(e)
        
        finally:
            return "\n".join(self.logs), self.consequences

    async def connection_handler(self):
        pass

    async def message_handler(self, topic, id, sender, message, request_id):
        pass

    # RECRUIT methods

    async def recruit(self, user_message, conversational):
        self.log(f"Agent recruiting start for user message: {user_message}")

        tasks = []
        for agent_id in self.agents:
            tasks.append(asyncio.create_task(self.call_for_proposal(MQTT_TOPIC_CONVERSATIONAL_CALL if conversational else MQTT_TOPIC_RECRUIT_CALL, agent_id, user_message)))
            await asyncio.sleep(TICK)
        proposals = await asyncio.gather(*tasks)

        self.log(f"Agent recruiting end")

        return "\n".join(proposals)

    async def call_for_proposal(self, topic, agent_id, user_message):
        return await self.request(topic, agent_id, user_message)

    # CENTRALIZED methods

    async def discovery(self):
        return "\n".join(eval(await self.request(MQTT_TOPIC_CENTRALIZED_DISCOVERY, REGISTRY_ID, "")).values())
    
    # etc

    def log_result(self, result):
        if hasattr(result, "content") and result.content:
            self.log(result.content)
        if hasattr(result, "additional_kwargs") and "reasoning_content" in result.additional_kwargs:
            self.log(f"<Reasoning> {result.additional_kwargs['reasoning_content']}")
        if hasattr(result, "tool_calls"):
            self.log(f"<Tool calls> {result.tool_calls}")

    async def control_device(self, topic, result):
        self.log_result(result)
        if hasattr(result, "tool_calls"):
            tasks = []
            for tool_call in result.tool_calls:
                if "agent_id" not in tool_call["args"]:
                    self.consequences.append(dict(Response(agent_id="", request=tool_call["args"], success=False, message="NO AGENT ID")))
                    continue
                tasks.append(asyncio.create_task(self.control(topic, **tool_call["args"])))
                await asyncio.sleep(TICK)
            self.consequences += sum(await asyncio.gather(*tasks), [])

    async def control(self, topic, agent_id, **kwargs):
        response = await self.request(topic, agent_id, kwargs)
        return eval(response)
