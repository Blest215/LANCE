import requests
import os
import json
import sys

from abc import ABC, abstractmethod

from settings import *

from pydantic import BaseModel, Field
class ResponseMessage(BaseModel):
    request: dict
    success: bool
    message: str

class Device(ABC):
    def __init__(self, description):
        # TODO natural language descriptions
        self.description = description
        self.dict = description
        # TODO experiment control
        self.experiment = True

    def __str__(self):
        return str(self.description)
    
    def control(self, **kwargs) -> ResponseMessage:
        try:
            validation_result = self.validate_input(**kwargs)
            if validation_result == "VALID":
                return self.execute(**kwargs) if self.experiment else self.request(kwargs)
            return ResponseMessage(request=kwargs, success=False, message=validation_result)
        except Exception as e:
            return ResponseMessage(request=kwargs, success=False, message=str(e))
        
    @staticmethod
    @abstractmethod
    def get_tool() -> dict:
        pass

    @abstractmethod
    def validate_input(self, **kwargs) -> str:
        pass

    @abstractmethod
    def execute(self, **kwargs) -> ResponseMessage:
        pass

    @abstractmethod
    def request(self, **kwargs) -> ResponseMessage:
        pass

def instantiate_device(description) -> Device:
    try:
        return getattr(sys.modules[__name__], f"{description['format']}Device")(description)
    except:
        return


class W3CDevice(Device):
    @staticmethod
    def get_tool():
        return {
            'type': 'function',
            'function': {
                'name': 'control_device_w3c',
                'description': 'control the W3C WoT device associated with agent_id',
                'parameters': {
                    'type': 'object',
                    'required': ['agent_id', 'action'],
                    'properties': {
                        'agent_id': {'type': 'string', 'description': 'the ID of the agent associated with the device to control'},
                        'action': {'type': 'string', 'description': 'the action to perform'},
                        'arguments': {'type': 'list', 'description': 'the arguments for the action'},
                    },
                },
            },
        }
    
    def validate_input(self, **kwargs):
        if "action" not in kwargs:
            return "NO ACTION NAME"
        if kwargs["action"] not in self.dict["actions"]:
            return "INVALID ACTION NAME"
        if "required" in self.dict["actions"][kwargs["action"]] and self.dict["actions"][kwargs["action"]]["required"] not in kwargs["arguments"]:
            return "REQUIRED ARGUMENTS MISSING"
        return "VALID"
    
    def execute(self, **kwargs):
        return ResponseMessage(request=kwargs, success=True, message="")

    def request(self, **kwargs):
        pass


class SmartThingsDevice(Device):
    @staticmethod
    def get_tool():
        return {
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
                        'command': {'type': 'string', 'description': 'the command for the action'},
                        'arguments': {'type': 'list', 'description': 'the arguments for the command'},
                    },
                },
            },
        }
        
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
        return ResponseMessage(request=kwargs, success=True, message="")
    
    def request(self, **kwargs):
        try:
            command = {"component": "main", "capability": kwargs["capability"], "command": kwargs["command"]}
            # TODO arguments control
            return ResponseMessage(
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
            return ResponseMessage(request=kwargs, success=False, message=str(e))


class MatterDevice(Device):
    @staticmethod
    def get_tool() -> dict:
        return {
            'type': 'function',
            'function': {
                'name': 'control_device_matter',
                'description': 'control the matter device associated with agent_id',
                'parameters': {
                    'type': 'object',
                    'required': ['agent_id', 'endpoint_id', 'cluster_id', 'command_id'],
                    'properties': {
                        'agent_id': {'type': 'string', 'description': 'the ID of the agent associated with the device to control'},
                        'endpoint_id': {'type': 'str', 'description': 'the hexcode ID of the endpoint to control'},
                        'cluster_id': {'type': 'str', 'description': 'the hexcode ID of the cluster to control'},
                        'command_id': {'type': 'str', 'description': 'the hexcode ID of the command'}
                    }
                }
            }
        }

    def validate_input(self, **kwargs) -> str:
        if "endpoint_id" not in kwargs:
            return "NO ENDPOINT ID"
        if "cluster_id" not in kwargs:
            return "NO CLUSTER ID"
        if "command_id" not in kwargs:
            return "NO COMMAND ID"
        if kwargs["endpoint_id"] not in self.dict["endpoints"]:
            return "INVALID ENDPOINT ID"
        if kwargs["cluster_id"] not in self.dict["endpoints"][int(kwargs["endpoint_id"])]["clusters"]:
            return "INVALID CLUSTER ID"
        if kwargs["command_id"] not in self.dict["endpoints"][int(kwargs["endpoint_id"])]["clusters"][kwargs["cluster_id"]]["commands"]:
            return "INVALID COMMAND ID"
        return "VALID"
    
    def execute(self, **kwargs):
        endpoint = self.dict['endpoints'][kwargs['endpoint_id']]
        cluster = endpoint['clusters'][kwargs['cluster_id']]
        command = cluster['commands'][kwargs['command_id']]
        return ResponseMessage(request=kwargs, success=True, message=f"Endpoint {endpoint['device_type_name']} Cluster {cluster['cluster_name']} Command {command['command_name']}")

    def request(self, **kwargs):
        pass
