import json
import paho.mqtt.client as mqtt

from langchain_ollama import ChatOllama
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate

from settings import *
from utils import *


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


class LanceAgent:
    def __init__(self, configuration, device_information):
        self.configuration = configuration
        self.device_information = json.loads(device_information)
        self.id = self.device_information["deviceId"] if "deviceId" in self.device_information else get_random_device_id()
        self.current_team_id = None

        brain = ChatOllama(**configuration)

        # Screener
        screener_parser = PydanticOutputParser(pydantic_object=ScreeningResult)
        self.screener = ChatPromptTemplate([("user", SCREENER_PROMPT)]).partial(format=screener_parser.get_format_instructions()) | brain | screener_parser

        # Controller
        self.controller = ChatPromptTemplate.from_template(CONTROLLER_PROMPT) | brain.bind_tools([control_device_tool])

        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(MQTT_BROKER_ADDRESS, 1883, 60)

    def loop_forever(self):
        self.client.loop_forever()

    def on_connect(self, client, userdata, flags, reason_code, properties):
        self.client.subscribe(MQTT_TOPIC_DISCOVERY.format(team_id="+"))
        self.client.subscribe(MQTT_TOPIC_AGENT.format(agent_id=self.id))

    def on_message(self, client, userdata, message):
        topic, id = message.topic.split("/")

        if not self.busy and check_topic(topic, MQTT_TOPIC_DISCOVERY):
            self.screening(id, message.payload.decode("utf-8"))
            
        elif check_topic(topic, MQTT_TOPIC_TEAM):
            # TODO handle team messages
            pass

        elif check_topic(topic, MQTT_TOPIC_AGENT):
            self.controlling(message.payload.decode("utf-8"))

    @property
    def busy(self):
        return self.current_team_id is not None
    
    def screening(self, team_id, message):
        screening_result = self.screener.invoke({"message": message, "device_information": self.device_information})

        if screening_result.score >= SCREENING_THRESHOLD:
            self.join_team(team_id)
            self.proposal(screening_result.message)

    def controlling(self, message):
        control_result = self.controller.invoke({"message": message, "device_information": self.device_information})
        for tool_call in control_result.tool_calls:
            if tool_call["name"] == "control_device":
                self.control_device(tool_call["args"])

    def join_team(self, team_id):
        self.current_team_id = team_id
        self.client.subscribe(MQTT_TOPIC_TEAM.format(team_id=team_id))

    def proposal(self, message):
        self.client.publish(MQTT_TOPIC_TEAM.format(team_id=self.current_team_id), f"[{self.id}] {message}")

    def control_device(self, args):
        print(f"[{self.id}] {args}")
        result = smartthings_request(self.id, args)
        print(result)
        # TODO repair

def run_agent_process(configuration, device_information):
    LanceAgent(configuration, device_information).loop_forever()
