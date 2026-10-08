from pydantic import BaseModel, Field, model_validator, create_model
from typing import Annotated, List, Dict, Optional, Literal, Union
from operator import getitem
from catalog import DEVICE_TYPES, DeviceType, ClusterId, ProfileId
from langchain.tools import tool
from pydantic import JsonValue as Value

# Spec

class PropertySpec(BaseModel):
    property_name: str
    property_type: Literal["string", "integer", "number", "boolean", "object", "array", "opaque"]
    fields: Dict[str, "PropertySpec"] = Field(default_factory=dict)
    items: Optional["PropertySpec"] = None

class ActionSpec(BaseModel):
    action_name: str
    arguments: Dict[str, PropertySpec] = Field(default_factory=dict)
    required: List[str] = Field(default_factory=list)

class DeviceDraft(BaseModel):
    device_id: str
    device_name: str
    room_id: str
    profile_id: ProfileId
    options: List[str]

class RoomSpec(BaseModel):
    room_id: str
    room_name: str

class SceneSpec(BaseModel):
    rooms: List[RoomSpec] = Field(min_length=1)
    devices: List[DeviceDraft] = Field(default_factory=list)
    solvable: bool
    reason: str

    @model_validator(mode="after")
    def validate_ids(self) -> "SceneSpec":
        if self.solvable and not self.devices:
            raise ValueError("Solvable scene requires devices")
        room_ids = [room.room_id for room in self.rooms]
        if len(room_ids) != len(set(room_ids)):
            raise ValueError("Not unique room ID")
        if {device.room_id for device in self.devices} - set(room_ids):
            raise ValueError("Invalid room ID")
        return self

# Devices

class Device(BaseModel):
    device_id: str
    device_name: str
    room_id: str

class MatterEndpointSpec(BaseModel):
    device_type: DeviceType
    clusters: List[ClusterId] = Field(min_length=1)
    commands: Dict[ClusterId, List[str]] = Field(default_factory=dict)
    properties: Dict[ClusterId, List[str]] = Field(default_factory=dict)
    allowed_features: Dict[ClusterId, List[str]] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_selection(self) -> "MatterEndpointSpec":
        if set(self.clusters) - DEVICE_TYPES[self.device_type]["clusters"].keys():
            raise ValueError("Cluster is not available for this device type")
        if (self.commands.keys() | self.properties.keys()) - set(self.clusters):
            raise ValueError("Controls must belong to selected clusters")
        return self

class MatterDeviceSpec(BaseModel):
    endpoints: List[MatterEndpointSpec] = Field(min_length=1)

    @classmethod
    def with_catalog(cls, catalog=DEVICE_TYPES):
        endpoints = tuple(create_model(f"MatterEndpointSpec{index}", __base__=MatterEndpointSpec,
            device_type=(getitem(Literal, name), ...),
            clusters=(getitem(List, getitem(Literal, tuple(device["clusters"]))), Field(min_length=1)),
            commands=(getitem(Dict, (getitem(Literal, tuple(device["clusters"])), List[str])), Field(default_factory=dict)),
            properties=(getitem(Dict, (getitem(Literal, tuple(device["clusters"])), List[str])), Field(default_factory=dict)))
            for index, (name, device) in enumerate(catalog.items()))
        endpoint = getitem(Annotated, (getitem(Union, endpoints), Field(discriminator="device_type"))) if len(endpoints) > 1 else endpoints[0]
        return create_model(cls.__name__, __base__=cls, endpoints=(getitem(List, endpoint), Field(min_length=1)))

class MatterCluster(BaseModel):
    cluster_id: int
    name: str
    revision: int
    feature_map: int
    attributes: List[Dict[str, Value]] = Field(default_factory=list)
    commands: List[Dict[str, Value]] = Field(default_factory=list)

class MatterEndpoint(BaseModel):
    endpoint_id: int
    device_types: List[Dict[str, Value]] = Field(min_length=1)
    clusters: List[MatterCluster] = Field(min_length=1)

class MatterDevice(Device):
    protocol: Literal["Matter"] = "Matter"
    node_id: int = Field(ge=1)
    endpoints: List[MatterEndpoint] = Field(min_length=1)
    profile_id: Optional[ProfileId] = None

class W3CDevice(Device):
    pass

class SmartThingsDevice(Device):
    pass

class Scene(BaseModel):
    rooms: List[RoomSpec] = Field(min_length=1)
    devices: List[MatterDevice | W3CDevice | SmartThingsDevice] = Field(min_length=1)

# Task

class ExpectedAction(BaseModel):
    device_id: str
    control_id: str
    arguments: Dict[str, Value] = Field(default_factory=dict)

class AgentInstruction(BaseModel):
    device_id: str
    instruction: str = Field(description="A natural language instruction describing the task or action to perform on the device.")

class Task(BaseModel):
    user_utterance: str
    expected_actions: List[ExpectedAction] = Field(min_length=1)

@tool
def call_device_matter(device_id: str, endpoint_id: int, cluster_id: int,
                       command_id: Optional[int] = None, attribute_id: Optional[int] = None,
                       arguments: Optional[Dict[str, Value]] = None, value: Value = None):
    """Invoke command_id with arguments or write attribute_id with value; specify exactly one member ID."""

@tool
def call_device_w3c():
    """TODO: Call a W3C Thing Description interaction."""
    pass

@tool
def call_device_smartthings():
    """TODO: Call a SmartThings capability command."""
    pass

@tool(args_schema=AgentInstruction)
def instruct_agent(device_id: str, instruction: str):
    """Send an instruction to an agent to control its device."""

# Rendering

class DeviceRendering(BaseModel):
    device_id: str
    protocol: Literal["W3C", "SmartThings", "Matter"]
