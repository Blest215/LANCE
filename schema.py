from pydantic import BaseModel, Field, model_validator
from typing import Annotated, List, Dict, Optional, Literal
from profiles import ProfileId
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
    devices: List[DeviceDraft] = Field(min_length=1)
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
    profile_id: Optional[ProfileId] = None

class MatterCluster(BaseModel):
    cluster_id: int
    name: str
    # revision: int
    # feature_map: int
    attributes: List[Dict[str, Value]] = Field(default_factory=list)
    commands: List[Dict[str, Value]] = Field(default_factory=list)

class MatterEndpoint(BaseModel):
    endpoint_id: int
    device_types: List[Dict[str, Value]] = Field(min_length=1)
    clusters: List[MatterCluster] = Field(min_length=1)

class MatterDevice(Device):
    protocol: Literal["Matter"] = "Matter"
    # node_id: int = Field(ge=1)
    endpoints: List[MatterEndpoint] = Field(min_length=1)

class W3CForm(BaseModel):
    # href: str
    op: List[Literal["readproperty", "writeproperty", "invokeaction"]]
    # contentType: str = "application/json"

class W3CProperty(BaseModel):
    model_config = {"extra": "allow"}
    forms: List[W3CForm] = Field(min_length=1)
    readOnly: bool = False
    writeOnly: bool = False

class W3CAction(BaseModel):
    title: str
    input: Dict[str, Value]
    forms: List[W3CForm] = Field(min_length=1)

class W3CThingDescription(BaseModel):
    # context: str = Field(default="https://www.w3.org/2022/wot/td/v1.1", alias="@context")
    # id: str
    title: str
    # securityDefinitions: Dict[str, Dict[str, Value]]
    # security: List[str]
    properties: Dict[str, W3CProperty] = Field(default_factory=dict)
    actions: Dict[str, W3CAction] = Field(default_factory=dict)

class W3CDevice(Device):
    protocol: Literal["W3C"] = "W3C"
    td: W3CThingDescription

class SmartThingsArgument(BaseModel):
    name: str
    optional: bool = False
    value_schema: Dict[str, Value]

class SmartThingsCommand(BaseModel):
    name: str
    arguments: List[SmartThingsArgument] = Field(default_factory=list)

class SmartThingsCapability(BaseModel):
    # id: str
    capability_name: str
    # version: int = 1
    # status: Literal["proposed"] = "proposed"
    attributes: Dict[str, Dict[str, Value]] = Field(default_factory=dict)
    commands: Dict[str, SmartThingsCommand] = Field(default_factory=dict)

class SmartThingsCapabilityRef(BaseModel):
    id: str
    version: int = 1

class SmartThingsComponent(BaseModel):
    id: str
    label: str
    capabilities: List[SmartThingsCapabilityRef] = Field(min_length=1)
    categories: List[Dict[str, Value]] = Field(default_factory=list)

class SmartThingsProfile(BaseModel):
    name: str
    components: List[SmartThingsComponent] = Field(min_length=1)

class SmartThingsDevice(Device):
    protocol: Literal["SmartThings"] = "SmartThings"
    # profile: SmartThingsProfile
    capabilities: List[SmartThingsCapability] = Field(min_length=1)

class Scene(BaseModel):
    rooms: List[RoomSpec] = Field(min_length=1)
    devices: List[
        Annotated[MatterDevice | W3CDevice | SmartThingsDevice, Field(discriminator="protocol")]
    ] = Field(min_length=1)

# Task

class Action(BaseModel):
    device_id: str
    control_id: str
    arguments: Dict[str, Value] = Field(default_factory=dict)

class Task(BaseModel):
    user_utterance: str
    expected_actions: List[Action] = Field(min_length=1)

@tool
def call_device_matter(
    device_id: str, 
    endpoint_id: int, 
    cluster_id: int,
    command_id: Optional[int] = None, 
    attribute_id: Optional[int] = None,
    arguments: Optional[Dict[str, Value]] = None, 
    value: Value = None
):
    """Invoke command_id with arguments or write attribute_id with value; specify exactly one member ID."""

@tool
def call_device_w3c(
    device_id: str, 
    interaction: Literal["action", "property"], 
    name: str,
    arguments: Optional[Dict[str, Value]] = None, 
    value: Value = None
):
    """Invoke a TD action with named arguments, or write a TD property with value."""

@tool
def call_device_smartthings(
    device_id: str, 
    capability: str, 
    command: str,
    arguments: List[Value]
):
    """Invoke a capability command with positional arguments in its declared order."""

TOOLS = {"Matter": call_device_matter, "W3C": call_device_w3c, "SmartThings": call_device_smartthings}

class AgentInstruction(BaseModel):
    device_id: str
    instruction: str = Field(description="A natural language instruction describing the task or action to perform on the device.")

@tool(args_schema=AgentInstruction)
def instruct_agent(
    device_id: str, 
    instruction: str
):
    """Send an instruction to an agent to control its device."""
