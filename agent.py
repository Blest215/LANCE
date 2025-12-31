import asyncio

from langchain_ollama import ChatOllama
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.exceptions import OutputParserException
from langchain_core.prompts import ChatPromptTemplate

from settings import *
from utils import *
from client import Client


from pydantic import BaseModel, Field
class ScreeningResult(BaseModel):
    score: float = Field(description="How the agent can contribute to the task. 0 <= score <= 1", ge=0, le=1)
    message: str = Field(description="Response message that describes the agent's capability to contribute to the task.")


# TODO other formats
control_device_tool = {
    'type': 'function',
    'function': {
        'name': 'control_device',
        'description': 'control the associated device',
        'parameters': {
            'type': 'object',
            'required': ['capability', 'command'],
            'properties': {
                'capability': {'type': 'string', 'description': 'the capability of the device to control'},
                'command': {'type': 'string', 'description': 'the command for the action'},
                'arguments': {'type': 'list', 'description': 'the arguments for the command'},
            },
        },
    },
}


class Agent(Client):
    def __init__(self, session, id, configuration, device_information):
        super().__init__(session, id)
        self.configuration = configuration
        self.device_information = device_information
        self.current_team_id = None

        brain = ChatOllama(**configuration)

        # Screener
        screener_parser = PydanticOutputParser(pydantic_object=ScreeningResult)
        self.screener = ChatPromptTemplate([("user", SCREENER_PROMPT)]).partial(format=screener_parser.get_format_instructions()) | brain | screener_parser

        # Controller
        self.controller = ChatPromptTemplate.from_template(CONTROLLER_PROMPT) | brain.bind_tools([control_device_tool])

    def connection_handler(self):
        self.subscribe(MQTT_TOPIC_LANCE_CALL, "+")
        self.subscribe(MQTT_TOPIC_NATURAL_AGENT, self.id)
        self.subscribe(MQTT_TOPIC_CENTRALIZED_CONTROL, self.id)
        self.publish(MQTT_TOPIC_CENTRALIZED_REGISTER, self.id, self.device_information)

    async def message_handler(self, topic, id, sender, message, request_id=""):
        if not self.busy and check_topic(topic, MQTT_TOPIC_LANCE_CALL):
            await self.screening(id, message)
        
        elif check_topic(topic, MQTT_TOPIC_LANCE_TEAM):
            # TODO handle team messages
            pass

        elif check_topic(topic, MQTT_TOPIC_NATURAL_AGENT):
            self.response(sender, request_id, await self.controlling(sender, request_id, message))

        elif check_topic(topic, MQTT_TOPIC_CENTRALIZED_CONTROL):
            self.response(sender, request_id, await self.control_device(sender, request_id, message))

    @property
    def busy(self):
        return self.current_team_id is not None
    
    # LANCE methods

    async def screening(self, team_id, message):
        while True:
            try:
                screening_result = await self.screener.ainvoke({"message": message, "device_information": self.device_information})
                if screening_result.score >= SCREENING_THRESHOLD:
                    self.join_team(team_id)
                    self.proposal(screening_result.message)
                return
            except OutputParserException:
                continue

    def join_team(self, team_id):
        self.current_team_id = team_id
        self.subscribe(MQTT_TOPIC_LANCE_TEAM, team_id)

    def proposal(self, message):
        self.log(message)
        self.publish(MQTT_TOPIC_LANCE_TEAM, self.current_team_id, message)

    # NATURAL methods

    async def controlling(self, sender, request_id, message):
        control_result = await self.controller.ainvoke({"message": message, "device_information": self.device_information})
        return await asyncio.gather(*[self.control_device(sender, request_id, tool_call["args"]) for tool_call in control_result.tool_calls if tool_call["name"] == "control_device"])
    
    # CENTRALIZED methods

    async def control_device(self, sender, request_id, message):
        self.log(f"Control device with arguments {message} for request {request_id} from {sender}")
        # result = smartthings_request(self.id, args)
        # TODO repair
        return "SUCCESS"

def run_agent_process(session, id, configuration, device_information):
    Agent(session, id, configuration, device_information).loop_forever()
