from settings import *
from schema import *
from model import Model
from collections import Counter

class ScreeningResult(BaseModel):
    relevant: bool = Field(description="Whether you can contribute to the task.", ge=0, le=1)
    proposal: str = Field(description="Short response message that describes what you can contribute to the task.")

SCREENER_PROMPT = ChatPromptTemplate.from_template(
"""You are an AI agent that controls the following device: {description}
Can you contribute to the following request? {request}""")

CONTROLLER_PROMPT = ChatPromptTemplate.from_template(
"""You are an AI agent that controls the following device: {description}
Control the device for the request: {request}""")

def control_id(endpoint_id, cluster_id, operation, member_id):
    return f"{endpoint_id}/{cluster_id}/{operation}/{member_id}"

def device_controls(device):
    controls = {}

    if isinstance(device, W3CDevice):
        for name, action in device.td.actions.items():
            controls[f"actions/{name}"] = {"name": action.title, "arguments": _schema_arguments(action.input)}
        for name, prop in device.td.properties.items():
            if not prop.readOnly:
                schema = prop.model_dump()
                controls[f"properties/{name}"] = {"name": schema.get("title", name), "arguments": {"value": _schema_field(schema, "value") | {"required": True}}}
        return controls
    
    if isinstance(device, SmartThingsDevice):
        for capability in device.capabilities:
            for name, command in capability.commands.items():
                controls[f"{capability.capability_name}/{name}"] = {
                    "name": name,
                    "arguments": {
                        arg.name: _schema_field(arg.value_schema, arg.name) | {"required": not arg.optional}
                        for arg in command.arguments
                    }
                }
        return controls
    
    for endpoint in device.endpoints:
        for cluster in endpoint.clusters:
            for command in cluster.commands:
                key = control_id(endpoint.endpoint_id, cluster.cluster_id, "invoke", command["command_id"])
                controls[key] = {
                    "name": command["name"], 
                    "arguments": {field["name"]: field for field in command["fields"]}
                }
            for attribute in cluster.attributes:
                if attribute["writable"]:
                    key = control_id(endpoint.endpoint_id, cluster.cluster_id, "write", attribute["attribute_id"])
                    controls[key] = {"name": attribute["name"], "arguments": {"value": attribute | {"required": True}}}
    return controls

def _schema_field(schema, name):
    nullable = any(branch.get("type") == "null" for branch in schema.get("oneOf", []))
    if nullable:
        schema = next(branch for branch in schema["oneOf"] if branch.get("type") != "null")
    field = {"name": name, "property_type": schema.get("type", "opaque"), "nullable": nullable}
    for source, target in (("minimum", "minimum"), ("maximum", "maximum"), ("unit", "unit"),
                            ("enum", "enum_values"), ("x-enumLabels", "enum_labels"),
                            ("minLength", "min_length"), ("maxLength", "max_length"),
                            ("minItems", "min_length"), ("maxItems", "max_length")):
        if source in schema:
            field[target] = schema[source]
    if "properties" in schema:
        field["fields"] = list(_schema_arguments(schema).values())
    if "items" in schema:
        field["items"] = _schema_field(schema["items"], "item")
    return field

def _schema_arguments(schema):
    return {
        name: _schema_field(field, name) | {"required": name in schema.get("required", [])}
        for name, field in schema.get("properties", {}).items()
    }

def _normalize(value, field):
    if value is None and field.get("nullable"):
        return None
    kind = field["property_type"]
    types = {"boolean": (bool,), "integer": (int,), "number": (int, float),
                "string": (str,), "array": (list,), "object": (dict,)}
    if kind in types and type(value) not in types[kind]:
        raise ValueError(f"Invalid type for {field['name']}")
    if "enum_values" in field and value not in field["enum_values"]:
        raise ValueError(f"Invalid choice for {field['name']}")
    for low, high, actual in (("minimum", "maximum", value),
                                ("min_length", "max_length", len(value) if isinstance(value, (str, list, dict)) else None)):
        if (low in field and actual < field[low]) or (high in field and actual > field[high]):
            raise ValueError(f"Out of range: {field['name']}")
    if kind == "array":
        return [_normalize(item, field["items"]) for item in value]
    if kind == "object" and "fields" in field:
        return _arguments(value, {member["name"]: member for member in field["fields"]})
    return float(value) if kind == "number" else value

def _arguments(arguments, fields):
    if type(arguments) is not dict:
        raise ValueError("Invalid arguments")
    if arguments.keys() - fields.keys():
        raise ValueError("Unknown argument")
    if {name for name, field in fields.items() if field.get("required")} - arguments.keys():
        raise ValueError("Missing required argument")
    return {name: _normalize(value, fields[name]) for name, value in arguments.items()}

class DeviceAgent:
    def __init__(self, spec: Device, model: Model | None = None):
        self.agent_id = spec.device_id
        self.spec = spec
        self.controls = device_controls(spec)
        self.handler = getattr(self, f"_{self.spec.protocol.lower()}_call")
        self.action_calls = []

        self.model = model
        if self.model is not None:
            self.screener = create_generator(SCREENER_PROMPT, ScreeningResult, model)
            self.controller = CONTROLLER_PROMPT | model.with_tools([TOOLS[spec.protocol]])

    @property
    def description(self) -> str:
        return self.spec.model_dump_json(exclude_none=True)
    
    def screen(self, request: str, structured: bool):
        result = self.screener.invoke({"description": self.description, "request": request})
        return (self.description if structured else result.proposal) if result.relevant else None

    def instruct(self, instruction: str):
        result = self.controller.invoke({"description": self.description, "request": instruction})
        return [
            self.call(**{name: value for name, value in tool_call["args"].items() if name != "device_id"})
            for tool_call in result.tool_calls
        ]

    def call(self, **request):
        action = self.handler(**request)
        self.action_calls.append(action)
        return action

    def validate_action(self, action: Action):
        if action.device_id != self.agent_id:
            raise ValueError(f"INVALID DEVICE ID: {action.device_id}")
        if action.control_id not in self.controls:
            raise ValueError(f"Unsupported control: {action.control_id}")
        arguments = _arguments(action.arguments, self.controls[action.control_id]["arguments"])
        return action.model_copy(update={"arguments": arguments})

    def _matter_call(self, endpoint_id, cluster_id, command_id=None, attribute_id=None, arguments=None, **request) -> Action:
        if command_id is not None and attribute_id is None and (not request or request == {"value": None}):
            operation, member_id, payload = "invoke", command_id, {} if arguments is None else arguments
        elif attribute_id is not None and command_id is None and not arguments and set(request) == {"value"}:
            operation, member_id, payload = "write", attribute_id, {"value": request["value"]}
        else:
            raise ValueError("Invalid Matter call")
        return self.validate_action(Action(device_id=self.agent_id,
            control_id=control_id(endpoint_id, cluster_id, operation, member_id), arguments=payload))

    def _w3c_call(self, interaction, name, arguments=None, **request) -> Action:
        if interaction == "action" and (not request or request == {"value": None}):
            identifier, payload = f"actions/{name}", {} if arguments is None else arguments
        elif interaction == "property" and not arguments and set(request) == {"value"}:
            identifier, payload = f"properties/{name}", {"value": request["value"]}
        else:
            raise ValueError("Invalid W3C call")
        return self.validate_action(Action(device_id=self.agent_id, control_id=identifier, arguments=payload))

    def _smartthings_call(self, capability, command, arguments) -> Action:
        identifier = f"{capability}/{command}"
        fields = self.controls.get(identifier, {}).get("arguments")
        if fields is None or type(arguments) is not list or len(arguments) > len(fields):
            raise ValueError("Invalid SmartThings call")
        return self.validate_action(Action(device_id=self.agent_id,
            control_id=identifier, arguments=dict(zip(fields, arguments))))

class Simulator:
    def __init__(self, scene: Scene | dict, model: Model | None = None):
        parsed = Scene.model_validate(scene)
        self.rooms = parsed.rooms
        self.devices = parsed.devices
        if len({device.device_id for device in self.devices}) != len(self.devices):
            raise ValueError("device IDs must be unique within a scene")
        self.agents = {device.device_id: DeviceAgent(device, model) for device in self.devices}

    @property
    def controls(self):
        return {device_id: agent.controls for device_id, agent in self.agents.items()}

    @property
    def action_calls(self):
        return [action for agent in self.agents.values() for action in agent.action_calls]

    def get_agent(self, device_id: str):
        if device_id not in self.agents:
            raise ValueError(f"INVALID DEVICE ID: {device_id}")
        return self.agents[device_id]

    def validate_action(self, action: Action):
        return self.get_agent(action.device_id).validate_action(action)

    def render(self):
        return {"rooms": self.rooms, "devices": self.discovery()}

    def call(self, device_id, **request):
        return self.get_agent(device_id).call(**request)

    def instruct(self, device_id: str, instruction: str):
        return self.get_agent(device_id).instruct(instruction)

    def discovery(self):
        return {agent.agent_id: agent.description for agent in self.agents.values()}

    def recruit(self, request: str, structured: bool):
        result = {agent.agent_id: agent.screen(request, structured) for agent in self.agents.values()}
        return {key: value for key, value in result.items() if value is not None}

    def evaluate(self, task: Task):
        def freeze(value):
            if isinstance(value, dict):
                return dict, tuple((tag, freeze(item)) for tag, item in sorted(value.items()))
            if isinstance(value, list):
                return list, tuple(map(freeze, value))
            return type(value), value

        def key(call):
            call = self.validate_action(call)
            return call.device_id, call.control_id, freeze(call.arguments)
        actual = Counter(map(key, self.action_calls))
        expected = Counter(map(key, task.expected_actions))
        return sum((actual & expected).values()) / len(task.expected_actions)
