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
    score: float = Field(description="How much you can contribute to the task. 0 <= score <= 1", ge=0, le=1)
    message: str = Field(description="Response message that describes how you can contribute to the task.")


class Agent(Client):
    def __init__(self, session, id, model, device):
        super().__init__(session, id)
        self.configuration = model
        self.device = device

        # RECRUIT
        screener_parser = PydanticOutputParser(pydantic_object=ScreeningResult)
        self.screener = ChatPromptTemplate([("user", SCREENER_PROMPT)]).partial(format=screener_parser.get_format_instructions()) | model.instantiate() | screener_parser
        # NATURAL
        self.controller = ChatPromptTemplate.from_template(CONTROLLER_PROMPT) | model.with_tools([device.get_tool()])

    async def connection_handler(self):
        await self.subscribe(MQTT_TOPIC_RECRUIT_CALL, "+")
        await self.subscribe(MQTT_TOPIC_NATURAL_CONTROL, self.id)
        await self.subscribe(MQTT_TOPIC_STRUCTURED_CONTROL, self.id)
        await self.publish(MQTT_TOPIC_CENTRALIZED_REGISTER, self.id, str(self.device))

    async def message_handler(self, topic, id, sender, message, request_id):
        if not self.busy and check_topic(topic, MQTT_TOPIC_RECRUIT_CALL):
            await self.screening(id, message)

        elif check_topic(topic, MQTT_TOPIC_NATURAL_CONTROL):
            await self.response(sender, request_id, await self.controlling(message))

        elif check_topic(topic, MQTT_TOPIC_STRUCTURED_CONTROL):
            await self.response(sender, request_id, [self.control_device(message)])

    @property
    def busy(self):
        return self.current_team_id is not None
    
    # RECRUIT methods

    async def screening(self, team_id, message):
        screening_result = await self.screener.ainvoke({"message": message, "device_description": str(self.device)})
        if screening_result.score >= RECRUIT_SCREENING_THRESHOLD:
            await self.join_team(team_id)
            await self.publish(MQTT_TOPIC_RECRUIT_TEAM, self.current_team_id, str(self.device))

    # NATURAL methods

    async def controlling(self, message):
        control_result = await self.controller.ainvoke({"message": message, "device_description": str(self.device)})
        return [self.control_device(tool_call["args"]) for tool_call in control_result.tool_calls if "control_device" in tool_call["name"]]
    
    # CENTRALIZED methods

    def control_device(self, arguments):
        return dict(self.device.control(**arguments))

def run_agent_process(session, id, model, device_description):
    if sys.platform.lower() == "win32" or os.name.lower() == "nt":
        from asyncio import set_event_loop_policy, WindowsSelectorEventLoopPolicy
        set_event_loop_policy(WindowsSelectorEventLoopPolicy())
    asyncio.run(Agent(session, id, model, instantiate_device(id, device_description)).loop())
