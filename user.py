import json
import asyncio
import paho.mqtt.client as mqtt

from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate

from settings import *
from utils import *

initiate_task_tool = {
    'type': 'function',
    'function': {
        'name': 'initiate_task',
        'description': 'initiate a new task',
        'parameters': {
            'type': 'object',
            'required': ['message'],
            'properties': {
                'message': {'type': 'string', 'description': 'a fluent message describing the requirements for the task'},
            },
        },
    },
}

call_agent_tool = {
    'type': 'function',
    'function': {
        'name': 'call_agent',
        'description': 'send a direct message to a specific agent for asking device control',
        'parameters': {
            'type': 'object',
            'required': ['agent_id', 'message'],
            'properties': {
                'agent_id': {'type': 'string', 'description': 'the ID of the agent to call'},
                'message': {'type': 'string', 'description': 'the message to send to the agent'},
            },
        },
    },
}

control_device_tool = {
    'type': 'function',
    'function': {
        'name': 'control_device',
        'description': 'control a device specified by the agent id',
        'parameters': {
            'type': 'object',
            'required': ['agent_id', 'capability', 'command'],
            'properties': {
                'agent_id': {'type': 'string', 'description': 'the ID of the agent associated with the device to control'},
                'capability': {'type': 'string', 'description': 'the capability of the device to control'},
                'command': {'type': 'string', 'description': 'the command for the action'},
                'arguments': {'type': 'list', 'description': 'the arguments for the command'},
            }
        }
    }
}


class UserAgent:
    def __init__(self, configuration):
        self.configuration = configuration
        self.device_registry = {}
        self.current_team_id = None
        self.team_messages = []

        brain = ChatOllama(**configuration)
        # LANCE
        self.organizer = ChatPromptTemplate.from_template(ORGANIZER_PROMPT)| brain.bind_tools([initiate_task_tool])
        self.coordinator = ChatPromptTemplate.from_template(COORDINATOR_PROMPT) | brain.bind_tools([call_agent_tool])
        # CENTRALIZED
        self.centralized = ChatPromptTemplate.from_template(MASTERMIND_PROMPT) | brain.bind_tools([control_device_tool])

        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(MQTT_BROKER_ADDRESS, 1883, 60)
        self.client.loop_start()

    async def ask(self, mode, user_command):
        print(f"User asked: {user_command}")
        if mode == "LANCE":
            coordinator_result = await self.organizer.ainvoke({"user_command": user_command})
            
            for tool_call in coordinator_result.tool_calls:
                if tool_call["name"] == "initiate_task":
                    await self.initiate_task(tool_call["args"]["message"])
        
        elif mode == "CENTRALIZED":
            centralized_result = await self.centralized.ainvoke({"user_command": user_command, "device_informations": self.device_registry})

            for tool_call in centralized_result.tool_calls:
                if tool_call["name"] == "control_device":
                    self.control_device(**tool_call["args"])
        
        elif mode == "CLOUD":
            pass
        
        elif mode == "ONTOLOGY":
            pass

    async def initiate_task(self, message):
        await self.discovery(10, message)
        # TODO Negotiation
        await self.control(10, self.team_messages)

    async def discovery(self, time_to_wait, message):
        print(f"{message} ({time_to_wait}s)")
        self.current_team_id = get_random_team_id()
        self.client.subscribe(MQTT_TOPIC_LANCE_TEAM.format(team_id=self.current_team_id))
        self.client.publish(MQTT_TOPIC_LANCE_DISCOVERY.format(team_id=self.current_team_id), message)
        self.team_messages = [message]
        await asyncio.sleep(time_to_wait)
        print(self.team_messages)

    async def control(self, time_to_wait, team_messages):
        controller_result = await self.coordinator.ainvoke({"user_task": team_messages[0], "team_messages": "\n".join(team_messages[1:])})

        for tool_call in controller_result.tool_calls:
            if tool_call["name"] == "call_agent":
                self.call_agent(tool_call["args"]["agent_id"], tool_call["args"]["message"])

        # TODO Wait for completion
        await asyncio.sleep(time_to_wait)

    def call_agent(self, agent_id, message):
        self.client.publish(MQTT_TOPIC_LANCE_AGENT.format(agent_id=agent_id), message)

    def control_device(self, agent_id, capability, command, arguments={}):
        print(f"{agent_id}")
        self.client.publish(MQTT_TOPIC_CENTRALIZED_CONTROL.format(agent_id=agent_id), json.dumps({"capability": capability, "command": command, "arguments": arguments}))

    def on_connect(self, client, userdata, flags, reason_code, properties):
        self.client.subscribe(MQTT_TOPIC_CENTRALIZED_REGISTER.format(agent_id="+"))

    def on_message(self, client, userdata, message):
        mode, topic, id = message.topic.split("/")

        if check_topic(topic, MQTT_TOPIC_LANCE_TEAM) and id == self.current_team_id:
            self.team_messages.append(message.payload.decode("utf-8"))

        elif check_topic(topic, MQTT_TOPIC_CENTRALIZED_REGISTER):
            self.device_registry[id] = message.payload.decode("utf-8")
