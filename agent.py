import asyncio
import sys

from langchain_core.output_parsers import PydanticOutputParser

from settings import *
from client import Client
from device import instantiate_device

from pydantic import BaseModel, Field
class ScreeningResult(BaseModel):
    score: float = Field(description="How much you can contribute to the task. 0 <= score <= 1", ge=0, le=1)
    message: str = Field(description="Short response message that describes what you can contribute to the task. Do not mention what you cannot do.")

class Agent(Client):
    def __init__(self, id, model, device_description):
        super().__init__(id)
        self.configuration = model
        self.device = instantiate_device(id, device_description)

        # RECRUIT
        screener_parser = PydanticOutputParser(pydantic_object=ScreeningResult)
        self.screener = SCREENER_PROMPT.partial(format=screener_parser.get_format_instructions()) | model.instantiate() | screener_parser
        # NATURAL
        self.controller = CONTROLLER_PROMPT | model.with_tools([self.device.get_tool()])

    async def connection_handler(self):
        await self.subscribe(MQTT_TOPIC_CONVERSATIONAL_CALL, self.id)
        await self.subscribe(MQTT_TOPIC_RECRUIT_CALL, self.id)
        await self.subscribe(MQTT_TOPIC_NATURAL_CONTROL, self.id)
        await self.subscribe(MQTT_TOPIC_STRUCTURED_CONTROL, self.id)
        await self.publish(MQTT_TOPIC_CENTRALIZED_REGISTER, self.id, self.device.description)

    async def message_handler(self, topic, id, sender, message, request_id):
        if check_topic(topic, MQTT_TOPIC_CONVERSATIONAL_CALL):
            await self.response(sender, request_id, await self.screening(message, True))

        elif check_topic(topic, MQTT_TOPIC_RECRUIT_CALL):
            await self.response(sender, request_id, await self.screening(message, False))

        elif check_topic(topic, MQTT_TOPIC_NATURAL_CONTROL):
            await self.response(sender, request_id, await self.controlling(message))

        elif check_topic(topic, MQTT_TOPIC_STRUCTURED_CONTROL):
            await self.response(sender, request_id, [self.control_device(message)])
    
    # RECRUIT methods

    async def screening(self, message, conversational):
        screening_result = await self.screener.ainvoke({"message": message, "description": self.device.structured})
        return f"Device {self.id}: {screening_result.message if conversational else self.device.description}" if screening_result.score > RECRUIT_SCREENING_THRESHOLD else ""

    # NATURAL methods

    async def controlling(self, message):
        control_result = await self.controller.ainvoke({"message": message["instruction"], "description": self.device.structured})
        if not control_result.tool_calls:
            return [dict(Response(agent_id=self.id, request=message, success=False, message="NO TOOL CALL BY AGENTS"))]
        return [self.control_device(tool_call["args"]) for tool_call in control_result.tool_calls if "control_device" in tool_call["name"]]
    
    # CENTRALIZED methods

    def control_device(self, arguments):
        return dict(self.device.control(**arguments))
