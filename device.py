from settings import *

# W3C WoT TD

class TDProperty(BaseModel):
    type: Literal["integer", "string"]

class TDObjectProperty(BaseModel):
    type: Literal["object"]
    properties: Dict[str, TDProperty] = Field(description="The properties of the object.")
    required: List[str] = Field(default=[], description="The required properties of the object.")

class TDAction(BaseModel):
    title: str = Field(description="Title of the action that the device can perform.")
    description: str = Field(description="Description of the action.")
    input: Optional[TDObjectProperty] = Field(description="The input to the action.")
    # TODO output
    # TODO forms

class TDDevice(BaseModel):
    # AUTOCOMPLETION format: Literal["W3C"]
    # AUTOCOMPLETION id: Annotated[UUID, PlainSerializer(serialize_id)]
    title: str = Field(description="Title of the device, e.g., light, TV, air_conditioner.")
    # TODO properties
    actions: Dict[str, TDAction] = Field(description="Actions the device can perform with optional arguments.")

# SmartThings

class STSchema(BaseModel):
    type: Literal["integer", "string"]

class STArgument(BaseModel):
    name: str = Field(description="Argument name.")
    optional: bool = Field(description="Whether this argument is optional or mandatory.")
    schema_: STSchema = Field(description="Schema of the argument.")

class STCommand(BaseModel):
    arguments: List[STArgument] = Field(default=[], description="Required arguments for the command.")

class STCapability(BaseModel):
    id: str = Field(description="Name of the capability.")
    # AUTOCOMPLETION version: Literal[1]
    # AUTOCOMPLETION status: Literal["live"]
    # TODO attributes
    commands: Dict[str, STCommand] = Field(description="Available commands to the capability.")

class STComponent(BaseModel):
    # AUTOCOMPLETION id: Literal["main"]
    # AUTOCOMPLETION label: Literal["main"]
    # AUTOCOMPLETION optional: Literal[False]
    capabilities: List[STCapability] = Field(description="The capabilities that the device can control.")
    # categories
    # restrictions

class STDevice(BaseModel):
    # AUTOCOMPLETION format: Literal["SmartThings"]
    # AUTOCOMPLETION deviceId: Annotated[UUID, PlainSerializer(serialize_id)]
    name: str = Field(description="Name of the device, e.g., light, TV, air_conditioner.")
    label: str = Field(description="User-custom label of the device.")
    # manufacturerName
    # presentationId
    # deviceManufacturerCode
    # locationId
    # ownerId
    # roomId
    # deviceTypeId
    # deviceTypeName
    # deviceNetworkType
    # productId
    # brandId
    components: List[STComponent] = Field(min_length=1, max_length=1)
    # createTime
    # parentDeviceId
    # childDevices
    # profile
    # app
    # ble
    # bleD2D
    # dth
    # lan
    # zigbee
    # zwave
    # matter
    # hub
    # edgeChild
    # ir
    # irOcf
    # ocf
    # viper
    # group
    # virtual
    # mqtt
    # type
    # restrictionTier
    # allowed
    # indoorMap
    # executionContext
    # relationships

# Matter

class MTEndpoint(BaseModel):
    endpoint_id: str
    device_type_name: str = Field(description="Device type name.")
    device_type_id: str = Field(description="Device type id associated with the name.")
    # AUTOCOMPLETION clusters: Dict

class MTDevice(BaseModel):
    # AUTOCOMPLETION format: Literal["Matter"]
    # AUTOCOMPLETION id: Annotated[UUID, PlainSerializer(serialize_id)]
    endpoints: Dict[str, MTEndpoint] = Field(description="Endpoints of the device node.")

class Device(ABC):
    def __init__(self, agent_id, description: dict, experiment=True):
        self.agent_id = agent_id # One-to-one
        if experiment:
            self.description = str(description["natural"]) if "natural" in description else str(description["structured"])
            self.dict = description["structured"]
        else:
            self.description = str(description)
            self.dict = description
        self.experiment = experiment

    @property
    def structured(self):
        return str(self.dict)
    
    def control(self, **kwargs) -> Response:
        try:
            validation_result = self.validate_input(**kwargs)
            if validation_result == "VALID":
                return self.execute(**kwargs) if self.experiment else self.request(**kwargs)
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

def instantiate_device(id, description, experiment) -> Device:
    return getattr(sys.modules[__name__], f"{description['format']}Device")(id, description, experiment)

class W3CInput(BaseModel):
    agent_id: str = Field(description="The unique ID of the agent associated with the W3C device")
    action: str = Field(description="The action name to execute on the device (must be one of the device's available actions)")
    inputs: Dict[str, Any] = Field(default={}, description="Kwarg dictionary of input parameters required for the action")

@tool("control_device_w3c", args_schema=W3CInput)
def control_device_w3c(agent_id: str, action: str, inputs: Dict[str, Any]):
    """Control a W3C-format device by executing an action. Use this tool only for W3C-format devices."""

class W3CDevice(Device):
    @staticmethod
    def get_tool():
        return control_device_w3c
    
    def validate_input(self, **kwargs):
        if "action" not in kwargs:
            return "NO ACTION NAME"
        if kwargs["action"] not in self.dict["actions"]:
            return "INVALID ACTION NAME"
        if "required" in self.dict["actions"][kwargs["action"]]:
            for required in self.dict["actions"][kwargs["action"]]["required"]:
                if "inputs" not in kwargs or required not in kwargs["inputs"]:
                    return "REQUIREMENT MISSING"
        # TODO ARGUMENT TYPE
        return "VALID"
    
    def execute(self, **kwargs):
        return Response(agent_id=self.agent_id, request=kwargs, success=True, message="")

    def request(self, **kwargs):
        pass

class SmartThingsInput(BaseModel):
    agent_id: str = Field(description="The unique ID of the agent associated with the SmartThings device")
    capability: str = Field(description="The capability ID to target (e.g., 'switch', 'temperatureMeasurement')")
    command: str = Field(description="The command name to execute within the capability")
    arguments: Dict[str, Any] = Field(default={}, description="Kwarg dictionary of arguments required for the command")

@tool("control_device_smartthings", args_schema=SmartThingsInput)
def control_device_smartthings(agent_id: str, capability: str, command: str, arguments: Dict[str, Any]):
    """Control a SmartThings device by executing a command within a specific capability. Use this tool only for SmartThings devices."""

class SmartThingsDevice(Device):
    @staticmethod
    def get_tool():
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
        if self.experiment:
            if kwargs["command"] not in capability["commands"]:
                return "INVALID COMMAND NAME"
            for argument in capability["commands"][kwargs["command"]]["arguments"]:
                if not argument["optional"] and argument["name"] not in kwargs["arguments"]:
                    return "REQUIREMENT MISSING"
            # TODO ARGUMENT TYPE
        return "VALID"
    
    def execute(self, **kwargs):
        return Response(agent_id=self.agent_id, request=kwargs, success=True, message="")
    
    def request(self, **kwargs):
        try:
            command = {"component": "main", "capability": kwargs["capability"], "command": kwargs["command"]}
            # TODO arguments control
            result = requests.post(
                f"{SMARTTHINGS_API_URL}/{self.agent_id}/commands", 
                headers={"Authorization": f"Bearer {os.getenv('SMARTTHINGS_API_KEY')}", "Accept": "application/json"}, 
                json={"commands": [command]},
            ).json()
            return Response(
                agent_id=self.agent_id,
                request=kwargs,
                success="error" not in result,
                message=str(result)
            )
        except Exception as e:
            # TODO
            return Response(agent_id=self.agent_id, request=kwargs, success=False, message=str(e))

class MatterInput(BaseModel):
    agent_id: str = Field(description="The unique ID of the agent associated with the Matter device")
    endpoint_id: str = Field(description="The hexcode ID of the endpoint to control")
    cluster_id: str = Field(description="The hexcode ID of the cluster within the endpoint")
    command_id: str = Field(description="The hexcode ID of the command to execute")
    fields: Dict[str, Any] = Field(default={}, description="Kwarg dictionary of field values required for the command")

@tool("control_device_matter", args_schema=MatterInput)
def control_device_matter(agent_id: str, endpoint_id: str, cluster_id: str, command_id: str, fields: Dict[str, Any]):
    """Control a Matter device by executing a command on a specific cluster within an endpoint. Use this tool only for Matter-protocol devices."""

class MatterDevice(Device):
    @staticmethod
    def get_tool():
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
                return "REQUIREMENT MISSING"
        # TODO ARGUMENT TYPE
        return "VALID"
    
    def execute(self, **kwargs):
        endpoint = self.dict['endpoints'][kwargs['endpoint_id']]
        cluster = endpoint['clusters'][kwargs['cluster_id']]
        command = cluster['commands'][kwargs['command_id']]
        return Response(agent_id=self.agent_id, request=kwargs, success=True, message=f"Endpoint {endpoint['device_type_name']} Cluster {cluster['cluster_name']} Command {command['command_name']}")

    def request(self, **kwargs):
        pass
