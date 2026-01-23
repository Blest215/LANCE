import requests
import os
import json
import sys

from typing import Optional
from pydantic import BaseModel
from langchain.tools import tool
from typing import List, Dict, Any, Optional

from abc import ABC, abstractmethod

from settings import *
from settings import BaseModel

class Device(ABC):
    def __init__(self, agent_id, description):
        self.agent_id = agent_id # One-to-one
        self.description = str(description["natural"]) if "natural" in description else str(description["structured"])
        self.dict = description["structured"]
        # TODO experiment control
        self.experiment = True

    @property
    def structured(self):
        return str(self.dict)
    
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

class W3CInput(BaseModel):
    agent_id: str = Field(description="the ID of the agent associated with the device to control")
    action: str = Field(description="the action to perform")
    inputs: Optional[Dict[str, Any]] = Field(description="the input value dictionary for the action")

class W3CDevice(Device):
    @staticmethod
    def get_tool():
        @tool("control_device_w3c", args_schema=W3CInput)
        def control_device_w3c(agent_id: str, action: str, inputs: Optional[Dict[str, Any]]):
            """Send a control request to a W3C device associated with agent_id. Use this tool to control only W3C devices."""
        return control_device_w3c
    
    def validate_input(self, **kwargs):
        if "action" not in kwargs:
            return "NO ACTION NAME"
        if kwargs["action"] not in self.dict["actions"]:
            return "INVALID ACTION NAME"
        if "required" in self.dict["actions"][kwargs["action"]]:
            for required in self.dict["actions"][kwargs["action"]]["required"]:
                if "inputs" not in kwargs or required not in kwargs["inputs"]:
                    return f"REQUIRED INPUT {required} MISSING"
        # TODO ARGUMENT TYPE
        return "VALID"
    
    def execute(self, **kwargs):
        return Response(agent_id=self.agent_id, request=kwargs, success=True, message="")

    def request(self, **kwargs):
        pass

class SmartThingsInput(BaseModel):
    agent_id: str = Field(description="the ID of the agent associated with the device to control")
    capability: str = Field(description="the capability of the device to control")
    command: str = Field(description="the command to apply to the capability")
    arguments: Optional[Dict[str, Any]] = Field(description="the arguments for the command")

class SmartThingsDevice(Device):
    @staticmethod
    def get_tool():
        @tool("control_device_smartthings", args_schema=SmartThingsInput)
        def control_device_smartthings(agent_id: str, capability: str, command: str, arguments: Optional[Dict[str, Any]]):
            """Send a control request to a SmartThings device associated with agent_id. Use this tool to control only SmartThings devices."""
        return control_device_smartthings
        
    def validate_input(self, **kwargs):
        if "capability" not in kwargs:
            return "NO CAPABILITY NAME"
        if "command" not in kwargs:
            return "NO COMMAND NAME"
        capability = None
        for c in self.dict["components"][0]["capabilities"]:
            if kwargs["capability"] == c["id"]:
                capability = c
        if not capability:
            return "INVALID CAPABILITY NAME"
        if kwargs["command"] not in capability["commands"]:
            return "INVALID COMMAND NAME"
        for argument in capability["commands"][kwargs["command"]]["arguments"]:
            if not argument["optional"] and argument["name"] not in kwargs["arguments"]:
                return f"REQUIRED ARGUMENT {argument['name']} MISSING"
        # TODO ARGUMENT TYPE
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

class MatterInput(BaseModel):
    agent_id: str = Field(description="the ID of the agent associated with the device to control")
    endpoint_id: str = Field(description="the hexcode ID of the endpoint to control")
    cluster_id: str = Field(description="the hexcode ID of the cluster to control")
    command_id: str = Field(description="the hexcode ID of the command")
    fields: Optional[Dict[str, Any]] = Field(description="the field for the command")

class MatterDevice(Device):
    @staticmethod
    def get_tool():
        @tool("control_device_matter", args_schema=MatterInput)
        def control_device_matter(agent_id: str, endpoint_id: str, cluster_id: str, command_id: str, fields: Optional[Dict[str, Any]]):
            """Send a control request to a Matter device associated with agent_id. Use this tool to control only Matter devices."""
        return control_device_matter

    def validate_input(self, **kwargs) -> str:
        if "endpoint_id" not in kwargs:
            return "NO ENDPOINT ID"
        if "cluster_id" not in kwargs:
            return "NO CLUSTER ID"
        if "command_id" not in kwargs:
            return "NO COMMAND ID"
        if kwargs["endpoint_id"] not in self.dict["endpoints"]:
            return "INVALID ENDPOINT ID"
        endpoint = self.dict["endpoints"][kwargs["endpoint_id"]]
        if kwargs["cluster_id"] not in endpoint["clusters"]:
            return "INVALID CLUSTER ID"
        cluster = endpoint["clusters"][kwargs["cluster_id"]]
        if kwargs["command_id"] not in cluster["commands"]:
            return "INVALID COMMAND ID"
        command = cluster["commands"][kwargs["command_id"]]
        for field in command["fields"]:
            if field["name"] not in kwargs["fields"]:
                return f"REQUIRED FIELD {field['name']} MISSING"
        # TODO ARGUMENT TYPE
        return "VALID"
    
    def execute(self, **kwargs):
        endpoint = self.dict['endpoints'][kwargs['endpoint_id']]
        cluster = endpoint['clusters'][kwargs['cluster_id']]
        command = cluster['commands'][kwargs['command_id']]
        return Response(agent_id=self.agent_id, request=kwargs, success=True, message=f"Endpoint {endpoint['device_type_name']} Cluster {cluster['cluster_name']} Command {command['command_name']}")

    def request(self, **kwargs):
        pass
