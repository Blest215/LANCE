from pydantic import BaseModel, Field, model_validator
from typing import List, Dict, Any, Optional, Literal
from langchain.tools import tool

# Spec

class PropertySpec(BaseModel):
    property_name: str
    value_type: Literal["string", "integer", "number", "boolean"]
    minimum: Optional[float] = None
    maximum: Optional[float] = None
    unit: Optional[str] = None
    initial_value: str | int | float | bool

class ArgumentSpec(BaseModel):
    value: PropertySpec
    required: bool = True

class EffectSpec(BaseModel):
    target_property: str
    operation: Literal["set", "add", "subtract", "toggle"]
    constant: str | int | float | bool | None = None
    from_argument: str | None = None

    @model_validator(mode="after")
    def validate_source(self) -> "EffectSpec":
        has_constant = self.constant is not None
        if self.operation == "toggle":
            if self.from_argument is not None or has_constant:
                raise ValueError("toggle does not accept a value source")
        elif has_constant == (self.from_argument is not None):
            raise ValueError("provide exactly one of constant or from_argument")
        return self

class ActionSpec(BaseModel):
    action_name: str
    description: str
    arguments: List[ArgumentSpec] = Field(default_factory=list)
    effects: List[EffectSpec] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_effects(self) -> "ActionSpec":
        argument_names = {argument.value.property_name for argument in self.arguments}
        for effect in self.effects:
            if effect.from_argument is not None and effect.from_argument not in argument_names:
                raise ValueError("provide a valid argument name for from_argument")
        return self

class DeviceSpec(BaseModel):
    device_id: str
    device_name: str
    device_type: str
    room_id: str
    properties: List[PropertySpec] = Field(min_length=1)
    actions: List[ActionSpec] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_effects(self) -> "DeviceSpec":
        property_names = {property_spec.property_name for property_spec in self.properties}
        for action_spec in self.actions:
            for effect_spec in action_spec.effects:
                if effect_spec.target_property not in property_names:
                    raise ValueError("Invalid property name")
        return self

class RoomSpec(BaseModel):
    room_id: str
    room_name: str
    # properties: List[PropertySpec] = Field(default_factory=list)

class State(BaseModel):
    entity_type: Literal["device"]
    entity_id: str
    attribute: str
    value: str | int | float | bool

class SceneSpec(BaseModel):
    rooms: List[RoomSpec] = Field(min_length=1)
    devices: List[DeviceSpec] = Field(min_length=5, max_length=5)

    @model_validator(mode="after")
    def validate_ids(self) -> "SceneSpec":
        room_ids = [room.room_id for room in self.rooms]
        device_ids = [device.device_id for device in self.devices]
        if len(room_ids) != len(set(room_ids)):
            raise ValueError("Not unique room ID")
        if len(device_ids) != len(set(device_ids)):
            raise ValueError("Not unique device ID")
        if {device.room_id for device in self.devices} - set(room_ids):
            raise ValueError("Invalid room ID")
        return self

# Task

class PropertyCall(BaseModel):
    device_id: str
    property_name: str

class ActionCall(BaseModel):
    device_id: str
    action_name: str
    arguments: Dict[str, str | int | float | bool] = Field(default_factory=dict)

class AgentInstruction(BaseModel):
    agent_id: str
    instruction: str = Field(description="A natural language instruction describing the task or action to perform on the device.")

class Task(BaseModel):
    user_utterance: str
    expected_actions: List[ActionCall] = Field(min_length=1)
    goal_states: List[State] = Field(min_length=1)

@tool(args_schema=PropertyCall)
def get_device_property(device_id: str, property_name: str):
    """Call a device API for reading properties."""

@tool(args_schema=ActionCall)
def call_device_action(device_id: str, action_name: str, arguments: Dict[str, str | int | float | bool] = {}):
    """Call a device API for invoking actions."""

@tool(args_schema=AgentInstruction)
def instruct_agent(agent_id: str, instruction: str):
    """Send an instruction to an agent to control its device."""

# Rendering

class DeviceRendering(BaseModel):
    device_id: str
    protocol: Literal["W3C", "SmartThings", "Matter"]
