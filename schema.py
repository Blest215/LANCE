from pydantic import BaseModel, Field, model_validator
from typing import Annotated, List, Dict, Optional, Literal
from profiles import ProfileId
from langchain.tools import tool
from pydantic import JsonValue as Value

class ContentResource(BaseModel):
    name: str
    kind: Literal["song", "album", "playlist", "show", "video", "podcast", "other"]
    provider: Optional[str] = None

class CleaningAreaResource(BaseModel):
    name: str
    map_name: Optional[str] = None

class ChannelResource(BaseModel):
    name: str
    kind: Literal["tv", "radio"]
    major_number: Optional[int] = Field(default=None, ge=0, le=65535)
    minor_number: Optional[int] = Field(default=None, ge=0, le=65535)

class InputResource(BaseModel):
    name: str

class ApplicationResource(BaseModel):
    name: str

class ScenarioResources(BaseModel):
    contents: List[ContentResource] = Field(default_factory=list)
    cleaning_areas: List[CleaningAreaResource] = Field(default_factory=list)
    channels: List[ChannelResource] = Field(default_factory=list)
    inputs: List[InputResource] = Field(default_factory=list)
    applications: List[ApplicationResource] = Field(default_factory=list)

class Intent(BaseModel):
    solvable: bool
    room: Literal[
        "living_room", "bedroom", "kitchen", "bathroom", "dining_room", "office", "study",
        "playroom", "family_room", "tv_room", "garage", "hallway", "entryway", "landing",
        "stairway", "garden", "backyard", "driveway", "pool_area", "upstairs", "downstairs",
        "first_floor", "second_floor", "unspecified",
    ]
    devices: List[ProfileId] = Field(min_length=1)
    resources: ScenarioResources = Field(default_factory=ScenarioResources)
    description: str

# Devices

class Device(BaseModel):
    device_id: str
    device_name: str
    room: str
    resources: Dict[str, List[Dict[str, Value]]] = Field(default_factory=dict)

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
    rooms: List[str] = Field(min_length=1)
    devices: List[
        Annotated[MatterDevice | W3CDevice | SmartThingsDevice, Field(discriminator="protocol")]
    ] = Field(min_length=1)

# Task

class Action(BaseModel):
    device_id: str
    action_name: str
    arguments: Dict[str, Value] = Field(default_factory=dict)

class Task(BaseModel):
    expected_actions: List[Action] = Field(min_length=1)

class UserUtterance(BaseModel):
    user_utterance: str

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
