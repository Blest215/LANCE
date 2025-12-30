import json
import asyncio
import paho.mqtt.client as mqtt

from datetime import datetime
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate

from settings import *
from utils import *
from client import Client

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


class UserAgent(Client):
    def __init__(self, configuration):
        super().__init__()

        # TODO multi user situation
        self.id = "USER"
        self.configuration = configuration
        self.current_team_id = None
        self.team_messages = []
        self.logs = []

        brain = ChatOllama(**configuration)
        # LANCE
        self.organizer = ChatPromptTemplate.from_template(ORGANIZER_PROMPT)| brain.bind_tools([initiate_task_tool])
        self.coordinator = ChatPromptTemplate.from_template(COORDINATOR_PROMPT) | brain.bind_tools([call_agent_tool])
        # CENTRALIZED
        self.centralized = ChatPromptTemplate.from_template(MASTERMIND_PROMPT) | brain.bind_tools([control_device_tool])

        self.client.loop_start()

    async def command(self, mode, user_command):
        self.log(f"User asked: {user_command}")
        if mode == "LANCE":
            coordinator_result = await self.organizer.ainvoke({"user_command": user_command})
            
            for tool_call in coordinator_result.tool_calls:
                if tool_call["name"] == "initiate_task":
                    await self.initiate_task(**tool_call["args"])
        
        elif mode == "NATURAL":
            pass

        elif mode == "CENTRALIZED":
            # TODO discovery
            centralized_result = await self.centralized.ainvoke({"user_command": user_command, "device_informations": await self.discovery()})

            for tool_call in centralized_result.tool_calls:
                if tool_call["name"] == "control_device":
                    await self.control_device(**tool_call["args"])
        
        elif mode == "CLOUD":
            pass
        
        elif mode == "ONTOLOGY":
            pass

    # LANCE methods

    async def initiate_task(self, message):
        self.log(f"Initiate a new task: {message}")
        await self.call_for_proposal(20, message)
        # TODO Negotiation
        await self.control(20, self.team_messages)

    async def call_for_proposal(self, time_to_wait, message):
        self.log(f"Agent call-for-proposal start ({time_to_wait}s)")
        self.current_team_id = get_random_team_id()
        self.subscribe(MQTT_TOPIC_LANCE_TEAM, self.current_team_id)
        self.publish(MQTT_TOPIC_LANCE_CALL, self.current_team_id, message)
        self.team_messages = [message]
        await asyncio.sleep(time_to_wait)
        self.log("Agent call-for-proposal end")

    async def control(self, time_to_wait, team_messages):        
        controller_result = await self.coordinator.ainvoke({"user_command": team_messages[0], "team_messages": "\n".join(team_messages[1:])})

        for tool_call in controller_result.tool_calls:
            if tool_call["name"] == "call_agent":
                await self.ask_agent(tool_call["args"]["agent_id"], tool_call["args"]["message"])

    # NATURAL methods

    async def ask_agent(self, agent_id, message):
        self.log(f"Ask agent {agent_id} {message}")
        await self.request(MQTT_TOPIC_NATURAL_AGENT, agent_id, message)

    # CENTRALIZED methods

    async def discovery(self):
        return await self.request(MQTT_TOPIC_CENTRALIZED_DISCOVERY, "REGISTRY", "")

    async def control_device(self, agent_id, capability, command, arguments={}):
        await self.request(MQTT_TOPIC_CENTRALIZED_CONTROL, agent_id, {"capability": capability, "command": command, "arguments": arguments})

    def connection_handler(self):
        self.subscribe(MQTT_TOPIC_RESPONSE, self.id)
        self.subscribe(MQTT_TOPIC_LOG, "+")

    def message_handler(self, topic, id, payload):
        if check_topic(topic, MQTT_TOPIC_LOG):
            print(f"[{datetime.now().strftime('%Y%m%d_%H%M%S')}] {payload['sender']:<36}: {payload['message']}")
            self.logs.append(f"[{datetime.now().strftime('%Y%m%d_%H%M%S')}] {payload['sender']:<36}: {payload['message']}")

        elif check_topic(topic, MQTT_TOPIC_LANCE_TEAM) and id == self.current_team_id:
            self.team_messages.append(f"{payload['sender']}: {payload['message']}")

        elif check_topic(topic, MQTT_TOPIC_RESPONSE):
            assert "request_id" in payload and payload["request_id"] in self.requests
            self.requests[payload["request_id"]]["status"] = "done"
            self.requests[payload["request_id"]]["response"] = payload["message"]
            self.log(f"Request {payload['request_id']} resulted {payload['message']}")
    