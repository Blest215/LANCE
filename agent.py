import asyncio
import sys

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.exceptions import OutputParserException
from langchain_core.prompts import ChatPromptTemplate

from settings import *
from client import Client
from device import instantiate_device

from pydantic import BaseModel, Field
class ScreeningResult(BaseModel):
    score: float = Field(description="How the agent can contribute to the task. 0 <= score <= 1", ge=0, le=1)
    message: str = Field(description="Response message that describes the agent's capability to contribute to the task.")


class Agent(Client):
    def __init__(self, session, id, model, device):
        super().__init__(session, id)
        self.configuration = model
        self.device = device
        self.current_team_id = None

        # LANCE
        screener_parser = PydanticOutputParser(pydantic_object=ScreeningResult)
        self.screener = ChatPromptTemplate([("user", SCREENER_PROMPT)]).partial(format=screener_parser.get_format_instructions()) | model.instantiate() | screener_parser
        # NATURAL
        self.controller = ChatPromptTemplate.from_template(CONTROLLER_PROMPT) | model.with_tools([device.get_tool()])

    async def connection_handler(self):
        await self.subscribe(MQTT_TOPIC_LANCE_CALL, "+")
        await self.subscribe(MQTT_TOPIC_NATURAL_AGENT, self.id)
        await self.subscribe(MQTT_TOPIC_CENTRALIZED_CONTROL, self.id)
        await self.publish(MQTT_TOPIC_CENTRALIZED_REGISTER, self.id, str(self.device))

    async def message_handler(self, topic, id, sender, message, request_id=""):
        if not self.busy and check_topic(topic, MQTT_TOPIC_LANCE_CALL):
            await self.screening(id, message)
        
        elif check_topic(topic, MQTT_TOPIC_LANCE_TEAM):
            # TODO handle team messages
            pass

        elif check_topic(topic, MQTT_TOPIC_NATURAL_AGENT):
            await self.response(sender, request_id, await self.controlling(sender, request_id, message))

        elif check_topic(topic, MQTT_TOPIC_CENTRALIZED_CONTROL):
            await self.response(sender, request_id, self.control_device(sender, request_id, message))

    @property
    def busy(self):
        return self.current_team_id is not None
    
    # LANCE methods

    async def screening(self, team_id, message):
        screening_result = await self.screener.ainvoke({"message": message, "device_description": str(self.device)})
        if screening_result.score >= SCREENING_THRESHOLD:
            await self.join_team(team_id)
            await self.proposal(screening_result.message)

    async def join_team(self, team_id):
        self.current_team_id = team_id
        await self.subscribe(MQTT_TOPIC_LANCE_TEAM, team_id)

    async def proposal(self, message):
        await self.publish(MQTT_TOPIC_LANCE_TEAM, self.current_team_id, message)

    # NATURAL methods

    async def controlling(self, sender, request_id, message):
        control_result = await self.controller.ainvoke({"message": message, "device_description": str(self.device)})
        return [self.control_device(sender, request_id, tool_call["args"]) for tool_call in control_result.tool_calls if "control_device" in tool_call["name"]]
    
    # CENTRALIZED methods

    def control_device(self, sender, request_id, arguments):
        return str(self.device.control(**arguments))

def run_agent_process(session, id, model, device_description):
    if sys.platform.lower() == "win32" or os.name.lower() == "nt":
        from asyncio import set_event_loop_policy, WindowsSelectorEventLoopPolicy
        set_event_loop_policy(WindowsSelectorEventLoopPolicy())
    asyncio.run(Agent(session, id, model, instantiate_device(device_description)).loop())
