import asyncio
import sys
import argparse

from langchain_core.output_parsers import PydanticOutputParser

from model import Model
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


async def register(agent):
    while True:
        await agent.publish(MQTT_TOPIC_CENTRALIZED_REGISTER, agent.id, agent.device.description)
        await asyncio.sleep(1)


async def main(broker_address: str, session: str, model: Model, device_description: str):
    agent = Agent(get_agent_id(device_description), model, device_description)
    loop = asyncio.create_task(agent.loop(broker_address))
    while not agent.is_connected:
        await asyncio.sleep(TICK)
    await agent.reset(session)

    print(f"{session}\n{device_description}")
    await asyncio.gather(loop, asyncio.create_task(register(agent)))


if __name__ == "__main__":
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument("--model", type=str, required=False, default="qwen3:4b-instruct-2507-q8_0")
    argument_parser.add_argument("--broker", type=str, required=False, default="192.168.0.2")
    argument_parser.add_argument("--session", type=str, required=False, default="0000000000000000")
    args = argument_parser.parse_args()

    if sys.platform.lower() == "win32" or os.name.lower() == "nt":
        from asyncio import set_event_loop_policy, WindowsSelectorEventLoopPolicy
        set_event_loop_policy(WindowsSelectorEventLoopPolicy())

    description = None
    if os.path.exists(DESCRIPTION_PATH):
        with open(DESCRIPTION_PATH, 'r', encoding='utf-8') as f:
            content = f.read()
        try:
            description = eval(content)
        except Exception:
            try:
                description = json.loads(content)
            except Exception:
                description = content
    else:
        description = {}

    asyncio.run(main(broker_address=args.broker, session=args.session, model=Model(args.model), device_description=description))
