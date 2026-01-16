import requests
import os
import json
import sys

from langchain_core.utils.function_calling import convert_to_openai_tool

from abc import ABC, abstractmethod

from settings import *

class Device(ABC):
    def __init__(self, agent_id, description):
        # TODO natural language descriptions
        self.agent_id = agent_id # One-to-one
        self.description = description
        self.dict = description
        # TODO experiment control
        self.experiment = True

    def __str__(self):
        return str(self.description)
    
    def control(self, **kwargs) -> Response:
        try:
            validation_result = self.validate_input(**kwargs)
            if validation_result == "VALID":
                return self.execute(**kwargs) if self.experiment else self.request(kwargs)
            return Response(agent_id=self.agent_id, request=kwargs, success=False, message=validation_result)
        except Exception as e:
            return Response(agent_id=self.agent_id, request=kwargs, success=False, message=str(e))
        
    @staticmethod
    @abstractmethod
    def get_tool():
        pass

    @abstractmethod
    def validate_input(self, **kwargs) -> str:
        pass

    @abstractmethod
    def execute(self, **kwargs) -> Response:
        pass

    @abstractmethod
    def request(self, **kwargs) -> Response:
        pass

def instantiate_device(id, description) -> Device:
    return getattr(sys.modules[__name__], f"{description['format']}Device")(id, description)


class W3CDevice(Device):
    @staticmethod
    def get_tool():
        return convert_to_openai_tool({
            'type': 'function',
            'function': {
                'name': 'control_device_w3c',
                'description': 'control the W3C device associated with agent_id',
                'parameters': {
                    'type': 'object',
                    'required': ['agent_id', 'action'],
                    'properties': {
                        'agent_id': {'type': 'string', 'description': 'the ID of the agent associated with the device to control'},
                        'action': {'type': 'string', 'description': 'the action to perform'},
                        'arguments': {'type': 'dict', 'description': 'the arguments for the action'},
                    },
                },
            },
        })
    
    def validate_input(self, **kwargs):
        if "action" not in kwargs:
            return "NO ACTION NAME"
        if kwargs["action"] not in self.dict["actions"]:
            return "INVALID ACTION NAME"
        if "required" in self.dict["actions"][kwargs["action"]] and self.dict["actions"][kwargs["action"]]["required"] not in kwargs["arguments"]:
            return "REQUIRED ARGUMENTS MISSING"
        # TODO ARGUMENTS
        return "VALID"
    
    def execute(self, **kwargs):
        return Response(agent_id=self.agent_id, request=kwargs, success=True, message="")

    def request(self, **kwargs):
        pass


class SmartThingsDevice(Device):
    @staticmethod
    def get_tool():
        return convert_to_openai_tool({
            'type': 'function',
            'function': {
                'name': 'control_device_smartthings',
                'description': 'control the smartthings device associated with agent_id',
                'parameters': {
                    'type': 'object',
                    'required': ['agent_id', 'capability', 'command'],
                    'properties': {
                        'agent_id': {'type': 'string', 'description': 'the ID of the agent associated with the device to control'},
                        'capability': {'type': 'string', 'description': 'the capability of the device to control'},
                        'command': {'type': 'string', 'description': 'the command to apply to the capability'},
                        'arguments': {'type': 'dict', 'description': 'the arguments for the command'},
                    },
                },
            },
        })
        
    def validate_input(self, **kwargs):
        if "capability" not in kwargs:
            return "NO CAPABILITY NAME"
        if "command" not in kwargs:
            return "NO COMMAND NAME"
        if kwargs["capability"] not in [capability["id"] for capability in self.dict["components"][0]["capabilities"]]:
            return "INVALID CAPABILITY NAME"
        # TODO INVALID COMMAND NAME
        # TODO ARGUMENTS
        return "VALID"
    
    def execute(self, **kwargs):
        return Response(agent_id=self.agent_id, request=kwargs, success=True, message="")
    
    def request(self, **kwargs):
        try:
            command = {"component": "main", "capability": kwargs["capability"], "command": kwargs["command"]}
            # TODO arguments control
            return Response(
                agent_id=self.agent_id,
                request=kwargs,
                success=True,
                message=requests.post(
                    f"{SMARTTHINGS_API_URL}/{self.dict['id']}/commands", 
                    headers={"Authorization": f"Bearer {os.getenv('SMARTTHINGS_API_KEY')}", "Accept": "application/json"}, 
                    json={"commands": [command]},
                ).json()
            )
        except Exception as e:
            # TODO
            return Response(agent_id=self.agent_id, request=kwargs, success=False, message=str(e))


class MatterDevice(Device):
    @staticmethod
    def get_tool() -> dict:
        return convert_to_openai_tool({
            'type': 'function',
            'function': {
                'name': 'control_device_matter',
                'description': 'control the matter device associated with agent_id',
                'parameters': {
                    'type': 'object',
                    'required': ['agent_id', 'endpoint_id', 'cluster_id', 'command_id'],
                    'properties': {
                        'agent_id': {'type': 'string', 'description': 'the ID of the agent associated with the device to control'},
                        'endpoint_id': {'type': 'string', 'description': 'the hexcode ID of the endpoint to control'},
                        'cluster_id': {'type': 'string', 'description': 'the hexcode ID of the cluster to control'},
                        'command_id': {'type': 'string', 'description': 'the hexcode ID of the command'}
                    }
                }
            }
        })

    def validate_input(self, **kwargs) -> str:
        if "endpoint_id" not in kwargs:
            return "NO ENDPOINT ID"
        if "cluster_id" not in kwargs:
            return "NO CLUSTER ID"
        if "command_id" not in kwargs:
            return "NO COMMAND ID"
        if kwargs["endpoint_id"] not in self.dict["endpoints"]:
            return "INVALID ENDPOINT ID"
        if kwargs["cluster_id"] not in self.dict["endpoints"][kwargs["endpoint_id"]]["clusters"]:
            return "INVALID CLUSTER ID"
        if kwargs["command_id"] not in self.dict["endpoints"][kwargs["endpoint_id"]]["clusters"][kwargs["cluster_id"]]["commands"]:
            return "INVALID COMMAND ID"
        return "VALID"
    
    def execute(self, **kwargs):
        endpoint = self.dict['endpoints'][kwargs['endpoint_id']]
        cluster = endpoint['clusters'][kwargs['cluster_id']]
        command = cluster['commands'][kwargs['command_id']]
        return Response(agent_id=self.agent_id, request=kwargs, success=True, message=f"Endpoint {endpoint['device_type_name']} Cluster {cluster['cluster_name']} Command {command['command_name']}")

    def request(self, **kwargs):
        pass
