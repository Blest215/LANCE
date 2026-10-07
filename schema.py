from pydantic import BaseModel, Field, model_validator, create_model
from typing import Annotated, List, Dict, Any, Optional, Literal, Union
from operator import getitem
from catalog import DeviceType, ClusterId
from langchain.tools import tool
import math

# Spec

class PropertySpec(BaseModel):
    property_name: str
    value_type: Literal["string", "integer", "number", "boolean"]
    minimum: Optional[float] = None
    maximum: Optional[float] = None
    unit: Optional[str] = None
    initial_value: str | int | float | bool
    enum_values: Optional[List[str | int | float | bool]] = None

    def validate_value(self, value: Any) -> None:
        types = {"string": (str,), "integer": (int,), "number": (int, float), "boolean": (bool,)}
        if type(value) not in types[self.value_type]:
            raise ValueError(f"INVALID_TYPE: {self.property_name} requires {self.value_type}")
        if self.value_type in ("integer", "number"):
            if not math.isfinite(value):
                raise ValueError(f"INVALID_VALUE: {self.property_name} must be finite")
            if self.minimum is not None and value < self.minimum:
                raise ValueError(f"BELOW_MINIMUM: {self.property_name}")
            if self.maximum is not None and value > self.maximum:
                raise ValueError(f"ABOVE_MAXIMUM: {self.property_name}")
        if self.enum_values is not None and not any(
            type(value) is type(item) and value == item for item in self.enum_values
        ):
            raise ValueError(f"INVALID_ENUM: {self.property_name}")

    @model_validator(mode="after")
    def validate_domain(self) -> "PropertySpec":
        if self.minimum is not None and self.maximum is not None and self.minimum > self.maximum:
            raise ValueError("minimum must not exceed maximum")
        if self.value_type not in ("integer", "number") and (self.minimum is not None or self.maximum is not None):
            raise ValueError("only numeric values may have bounds")
        self.validate_value(self.initial_value)
        return self

class EffectSpec(BaseModel):
    target_property: str

class FromConstantEffectSpec(EffectSpec):
    operation: Literal["set", "add", "subtract"]
    constant: str | int | float | bool

    @model_validator(mode="after")
    def validate_operation(self) -> "FromConstantEffectSpec":
        if self.operation in ["add", "subtract"] and (isinstance(self.constant, str) or isinstance(self.constant, bool)):
            raise ValueError("only numeric values can be added or subtracted")
        return self

class FromArgumentEffectSpec(EffectSpec):
    operation: Literal["set", "add", "subtract"]
    argument_name: str

class ToggleEffectSpec(EffectSpec):
    operation: Literal["toggle"]

class NotFromArgumentEffects(BaseModel):
    effects: List[
        FromConstantEffectSpec |
        ToggleEffectSpec
    ] = Field(min_length=1)

class FromArgumentEffects(BaseModel):
    effects: List[
        FromArgumentEffectSpec |
        FromConstantEffectSpec |
        ToggleEffectSpec
    ] = Field(min_length=1)

class ActionSpec(BaseModel):
    action_name: str
    description: str
    arguments: List[PropertySpec] = Field(default_factory=list)
    required: List[str] = Field(default_factory=list)
    effects: List[
        FromConstantEffectSpec |
        FromArgumentEffectSpec |
        ToggleEffectSpec
    ] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_effects(self) -> "ActionSpec":
        argument_names = {argument.property_name for argument in self.arguments}
        if len(argument_names) != len(self.arguments):
            raise ValueError("argument names must be unique")
        if len(self.required) != len(set(self.required)) or set(self.required) - argument_names:
            raise ValueError("required must contain unique declared argument names")
        for effect in self.effects:
            if isinstance(effect, FromArgumentEffectSpec) and effect.argument_name not in argument_names:
                raise ValueError(f"Invalid effect argument: {effect.argument_name} not in {argument_names}")
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
        if len(property_names) != len(self.properties):
            raise ValueError("property names must be unique")
        action_names = {action.action_name for action in self.actions}
        if len(action_names) != len(self.actions):
            raise ValueError("action names must be unique")
        for action_spec in self.actions:
            for effect_spec in action_spec.effects:
                if effect_spec.target_property not in property_names:
                    raise ValueError("Invalid property name")
        return self

class DeviceSpecMatter(BaseModel):
    room_id: str
    device_type: DeviceType
    clusters: List[ClusterId] = Field(min_length=1)

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
    devices: List[DeviceSpecMatter] = Field(min_length=1)

    @classmethod
    def with_choices(cls, choices, device_count=None):
        devices = tuple(create_model(f"DeviceSpecMatter{index}", __base__=DeviceSpecMatter,
            device_type=(getitem(Literal, name), ...),
            clusters=(getitem(List, getitem(Literal, tuple(cluster["cluster_id"] for cluster in clusters))), Field(min_length=1)))
            for index, (name, clusters) in enumerate(choices.items()))
        device = getitem(Annotated, (getitem(Union, devices), Field(discriminator="device_type"))) if len(devices) > 1 else devices[0]
        return create_model(cls.__name__, __base__=cls, devices=(getitem(List, device),
            Field(min_length=device_count or 1, max_length=device_count)))

    @model_validator(mode="after")
    def validate_ids(self) -> "SceneSpec":
        room_ids = [room.room_id for room in self.rooms]
        device_ids = [device.device_id for device in self.devices if isinstance(device, DeviceSpec)]
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
