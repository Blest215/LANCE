from settings import *
from schema import *
from model import Model
from collections import Counter
from copy import deepcopy
import json
from pydantic import TypeAdapter

ARGUMENT_TYPES = {
    "integer": TypeAdapter(int),
    "number": TypeAdapter(float),
    "boolean": TypeAdapter(bool),
    "string": TypeAdapter(str),
}

class ScreeningResult(BaseModel):
    relevant: bool = Field(description="Whether you can contribute to the task.", ge=0, le=1)
    proposal: str = Field(description="Short response message that describes what you can contribute to the task.")

SCREENER_PROMPT = ChatPromptTemplate.from_template(
"""You are an AI agent controlling: {description}
Can you contribute to this request? {request}""")

CONTROLLER_PROMPT = ChatPromptTemplate.from_template(
"""You are an AI agent controlling: {description}
Fulfill the request: {request}""")

def control_id(endpoint_id, cluster_id, operation, member_id):
    return f"{endpoint_id}/{cluster_id}/{operation}/{member_id}"

def device_controls(device):
    controls = {}

    if isinstance(device, W3CDevice):
        for name, action in device.td.actions.items():
            controls[f"actions/{name}"] = {"name": name, "arguments": _schema_arguments(action.input),
                                          "call": {"interaction": "action", "name": name}}
        for name, prop in device.td.properties.items():
            if not prop.readOnly:
                schema = prop.model_dump()
                controls[f"properties/{name}"] = {"name": f"write_{name}", "arguments": {"value": _schema_field(schema, "value") | {"required": True}},
                                                 "call": {"interaction": "property", "name": name}}
        return controls
    
    if isinstance(device, SmartThingsDevice):
        for capability in device.capabilities:
            for name, command in capability.commands.items():
                controls[f"{capability.capability_name}/{name}"] = {
                    "name": name,
                    "call": {"capability": capability.capability_name, "command": name},
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
                    "call": {"endpoint_id": endpoint.endpoint_id, "cluster_id": cluster.cluster_id,
                             "command_id": command["command_id"]},
                    "arguments": {field["name"]: field for field in command["fields"]}
                }
            for attribute in cluster.attributes:
                if attribute["writable"]:
                    key = control_id(endpoint.endpoint_id, cluster.cluster_id, "write", attribute["attribute_id"])
                    controls[key] = {"name": f"write_{attribute['name']}", "arguments": {"value": attribute | {"required": True}},
                                     "call": {"endpoint_id": endpoint.endpoint_id, "cluster_id": cluster.cluster_id,
                                              "attribute_id": attribute["attribute_id"]}}
    return controls

def _schema_field(schema, name):
    default = {"default": schema["default"]} if "default" in schema else {}
    nullable = any(branch.get("type") == "null" for branch in schema.get("oneOf", []))
    if nullable:
        schema = next(branch for branch in schema["oneOf"] if branch.get("type") != "null")
    field = {"name": name, "property_type": schema.get("type", "opaque"), "nullable": nullable} | default
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

def _coerce(value, field):
    if value is None and field.get("nullable"):
        return None
    labels = field.get("enum_labels", {})
    if isinstance(value, str):
        value = next((option for option in field.get("enum_values", [])
                      if str(option) in labels and labels[str(option)].casefold() == value.casefold()), value)
    kind = field["property_type"]
    if kind in ARGUMENT_TYPES:
        return ARGUMENT_TYPES[kind].validate_python(value)
    if kind in ("object", "array") and isinstance(value, str):
        value = json.loads(value)
    if kind == "array" and isinstance(value, list):
        return [_coerce(item, field["items"]) for item in value]
    if kind == "object" and isinstance(value, dict) and "fields" in field:
        return _arguments(value, {member["name"]: member for member in field["fields"]}, coerce=True)
    return value

def _arguments(arguments, fields, coerce=False):
    if type(arguments) is not dict:
        raise ValueError("Invalid arguments")
    if arguments.keys() - fields.keys():
        raise ValueError("Unknown argument")
    arguments = {name: deepcopy(field.get("default")) for name, field in fields.items()
                 if "default" in field or (field.get("required") and field.get("nullable"))} | arguments
    if {name for name, field in fields.items() if field.get("required")} - arguments.keys():
        raise ValueError("Missing required argument")
    return {name: _normalize(_coerce(value, fields[name]) if coerce else value, fields[name])
            for name, value in arguments.items()}

def _render_argument(name, field):
    text = name + ("*" if field.get("required") and "default" not in field else "")
    if "default" in field:
        text += f"(default={field['default']!r})"
    if "enum_values" in field:
        labels = field.get("enum_labels", {})
        text += "={" + ", ".join(repr(value) + (f"={labels[str(value)]}" if str(value) in labels else "")
                                   for value in field["enum_values"]) + "}"
    elif field["property_type"] == "boolean":
        text += "={true, false}"
    elif "minimum" in field or "maximum" in field:
        text += f"=[{field.get('minimum', '*')}..{field.get('maximum', '*')}]"
    if "fields" in field:
        text += "{" + ", ".join(_render_argument(member["name"], member) for member in field["fields"]) + "}"
    if "items" in field:
        text += "[" + _render_argument("item", field["items"]) + "]"
    return text

def _named_controls(controls):
    actions = {}
    reserved = {spec["name"] for spec in controls.values()}
    for identifier, spec in controls.items():
        name, suffix = spec["name"], 2
        while name in actions or (name != spec["name"] and name in reserved):
            name = f"{spec['name']}_{suffix}"
            suffix += 1
        actions[name] = spec | {"control_id": identifier}
    return actions

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
        return self.spec.model_dump_json(exclude_none=True, exclude={"resources"} if not self.spec.resources else None)
    
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
        if action.action_name not in self.controls:
            raise ValueError(f"Unsupported control: {action.action_name}")
        spec = self.controls[action.action_name]
        arguments = _arguments(action.arguments, spec["arguments"])
        channels = self.spec.resources.get("channels", [])
        if spec["name"].lower() == "changechannelbynumber" and channels and not any(
            arguments["MajorNumber"] == channel["MajorNumber"] and arguments["MinorNumber"] == channel["MinorNumber"]
            for channel in channels
        ):
            raise ValueError("Unsupported channel")
        return action.model_copy(update={"arguments": arguments})

    def _action(self, identifier, arguments):
        return self.validate_action(Action(device_id=self.agent_id,
            action_name=identifier, arguments=arguments))

    def _matter_call(self, endpoint_id, cluster_id, command_id=None, attribute_id=None, arguments=None, **request) -> Action:
        if command_id is not None and attribute_id is None and (not request or request == {"value": None}):
            operation, member_id, payload = "invoke", command_id, {} if arguments is None else arguments
        elif attribute_id is not None and command_id is None and not arguments and set(request) == {"value"}:
            operation, member_id, payload = "write", attribute_id, {"value": request["value"]}
        else:
            raise ValueError("Invalid Matter call")
        return self._action(control_id(endpoint_id, cluster_id, operation, member_id), payload)

    def _w3c_call(self, interaction, name, arguments=None, **request) -> Action:
        if interaction == "action" and (not request or request == {"value": None}):
            identifier, payload = f"actions/{name}", {} if arguments is None else arguments
        elif interaction == "property" and not arguments and set(request) == {"value"}:
            identifier, payload = f"properties/{name}", {"value": request["value"]}
        else:
            raise ValueError("Invalid W3C call")
        return self._action(identifier, payload)

    def _smartthings_call(self, capability, command, arguments) -> Action:
        identifier = f"{capability}/{command}"
        fields = self.controls.get(identifier, {}).get("arguments")
        if fields is None or type(arguments) is not list or len(arguments) > len(fields):
            raise ValueError("Invalid SmartThings call")
        return self._action(identifier, dict(zip(fields, arguments)))

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

    def assemble_action(self, action: Action) -> Action:
        spec = self.get_agent(action.device_id).controls[action.action_name]
        return self.validate_action(action.model_copy(update={
            "arguments": _arguments(action.arguments, spec["arguments"], coerce=True)}))

    def render(self) -> tuple[str, dict]:
        lines, lookup = ["* = required; {...} = options; [min..max] = range; omitted arguments use defaults."], {}
        for device in self.devices:
            lines.append(f"device_id={device.device_id}, room={device.room}")
            if device.resources:
                lines.append("  resources=" + json.dumps(device.resources, ensure_ascii=False, separators=(",", ":")))
            actions = lookup[device.device_id] = _named_controls(self.get_agent(device.device_id).controls)
            for name, spec in actions.items():
                arguments = ", ".join(_render_argument(key, field) for key, field in spec["arguments"].items())
                lines.append(f"  {name}({arguments})")
        return "\n".join(lines), lookup

    def call(self, device_id, **request):
        return self.get_agent(device_id).call(**request)

    def execute_action(self, action: Action) -> Action:
        action = self.validate_action(action)
        spec = self.get_agent(action.device_id).controls[action.action_name]
        request = spec["call"].copy()
        if "attribute_id" in request or request.get("interaction") == "property":
            request["value"] = action.arguments["value"]
        elif "capability" in request:
            names = list(spec["arguments"])
            while names and names[-1] not in action.arguments:
                names.pop()
            request["arguments"] = [action.arguments[name] for name in names]
        else:
            request["arguments"] = action.arguments
        return self.call(action.device_id, **request)

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
            return call.device_id, call.action_name, freeze(call.arguments)
        actual = Counter(map(key, self.action_calls))
        expected = Counter(map(key, task.expected_actions))
        return sum((actual & expected).values()) / len(task.expected_actions)
