import requests
import os
import json
import sys

from abc import ABC, abstractmethod

from settings import *


class Device(ABC):
    def __init__(self, description):
        # TODO natural language descriptions
        self.description = description
        self.dict = description
        # TODO experiment control
        self.experiment = True

    def __str__(self):
        return str(self.description)
    
    def control(self, **kwargs):
        try:
            validation_result = self.validate_input(**kwargs)
            if validation_result == "VALID" and not self.experiment:
                return self.request(**kwargs)
            return validation_result
        except Exception as e:
            return type(e).__name__
        
    @abstractmethod
    def request(self, **kwargs):
        pass

    @abstractmethod
    def validate_input(self, **kwargs) -> str:
        pass

    @staticmethod
    @abstractmethod
    def get_tool() -> dict:
        pass


class W3CDevice(Device):
    def request(self, **kwargs):
        return
    
    def validate_input(self, **kwargs):
        if "action" not in kwargs:
            return "NO ACTION NAME"
        if kwargs["action"] not in self.dict["actions"]:
            return "INVALID ACTION NAME"
        if "required" in self.dict["actions"][kwargs["action"]] and self.dict["actions"][kwargs["action"]]["required"] not in kwargs["arguments"]:
            return "REQUIRED ARGUMENTS MISSING"
        return "VALID"
    
    @staticmethod
    def get_tool():
        return {
            'type': 'function',
            'function': {
                'name': 'control_device_w3c',
                'description': 'control the associated W3C WoT device',
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


class SmartThingsDevice(Device):
    def request(self, **kwargs):
        try:
            command = {"component": "main", "capability": kwargs["capability"], "command": kwargs["command"]}
            # TODO arguments control
            return requests.post(
                f"{SMARTTHINGS_API_URL}/{self.dict['id']}/commands", 
                headers={"Authorization": f"Bearer {os.getenv('SMARTTHINGS_API_KEY')}", "Accept": "application/json"}, 
                json={"commands": [command]},
            ).json()
        except requests.exceptions.JSONDecodeError as e:
            # TODO
            return {}
        
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
    
    @staticmethod
    def get_tool():
        return {
            'type': 'function',
            'function': {
                'name': 'control_device_smartthings',
                'description': 'control the associated smartthings device',
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
    

def instantiate_device(description) -> Device:
    try:
        return getattr(sys.modules[__name__], f"{description['format']}Device")(description)
    except:
        return
