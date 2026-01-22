import asyncio

from settings import *
from client import Client
from device import *

class MessageInput(BaseModel):
    agent_id: str = Field(description="The ID of the agent associated with the device to control.")
    order: str = Field(description="An imperative sentence to order the device control.")

@tool("control_device", args_schema=MessageInput)
def control_device(agent_id: str, order: str):
    """Send an order to control a device associated with agent_id. Use this tool to control devices regardless of the formats."""

control_device_tools = [W3CDevice.get_tool(), SmartThingsDevice.get_tool(), MatterDevice.get_tool()]


class UserAgent(Client):
    def __init__(self, session, id, model):
        super().__init__(session, id)
        # TODO multi user situation
        self.configuration = model
        self.wait = set()
        self.agents = set()

        # NATURAL
        self.natural = COORDINATOR_PROMPT | model.with_tools([control_device])
        # CENTRALIZED
        self.centralized = COORDINATOR_PROMPT | model.with_tools(control_device_tools)

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

    async def recruit(self, user_message, conversational):
        self.log(f"Agent recruiting start for user message: {user_message} ({RECRUIT_TIME_TO_WAIT}s)")
        await self.join_team(get_random_team_id())
        await self.publish(MQTT_TOPIC_CONVERSATIONAL_CALL if conversational else MQTT_TOPIC_RECRUIT_CALL, self.current_team_id, f"Can you contribute to the following user message?: {user_message}")

        await asyncio.sleep(RECRUIT_TIME_TO_WAIT)

        self.log("Agent recruiting end")
        await self.leave_team()

        return [("system", description) for description in self.team_messages]

    # CENTRALIZED methods

    async def discovery(self):
        return [("system", description) for description in eval(await self.request(MQTT_TOPIC_CENTRALIZED_DISCOVERY, "REGISTRY", "")).values()]
    
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
                    self.consequences.append(dict(Response(agent_id=id, request=tool_call["args"], success=False, message="NO AGENT ID")))
                    continue
                tasks.append(asyncio.create_task(self.control(topic, **tool_call["args"])))
                await asyncio.sleep(TICK)
            self.consequences += sum(await asyncio.gather(*tasks), [])

    async def control(self, topic, agent_id, **kwargs):
        response = await self.request(topic, agent_id, kwargs)
        return eval(response)

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
