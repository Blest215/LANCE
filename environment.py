from settings import *
from schema import *
from copy import deepcopy
import json
from profiles import PROFILES
from pydantic import TypeAdapter

ARGUMENT_TYPES = {
    "integer": TypeAdapter(int),
    "number": TypeAdapter(float),
    "boolean": TypeAdapter(bool),
    "string": TypeAdapter(str, config={"coerce_numbers_to_str": True}),
}

IGNORED_EVALUATION_ARGUMENTS = {"DisplayString", "TransitionTime", "OptionsMask", "OptionsOverride", "Wrap", "LowestOff"}

def _device_actions(data):
    if data["protocol"] == "Matter":
        return [(command["name"].lower(), {field["name"]: field for field in command["fields"]})
                for endpoint in data["endpoints"] for cluster in endpoint["clusters"]
                for command in cluster.get("commands", [])]
    if data["protocol"] == "W3C":
        return [(action["title"].lower(), action["input"].get("properties", {}))
                for action in data["td"]["actions"].values()]
    return [(command["name"].lower(), {arg["name"]: arg["value_schema"] for arg in command.get("arguments", [])})
            for capability in data["capabilities"] for command in capability.get("commands", {}).values()]

def _resource_options(data, resources: List[Resource]):
    actions = _device_actions(data)
    bound = {}
    names = {name for name, _ in actions}
    grouped = {kind: [item for item in resources if item.type == kind]
               for kind in ("content", "channel", "cleaning_area", "input", "application")}
    supported = {"content": "launchurl", "cleaning_area": "selectareas",
                 "input": "selectinput", "application": "launchapp"}
    unsupported = [key for key, command in supported.items() if grouped[key] and command not in names]
    if any(("launchurl" not in names if channel.kind == "radio" else
            not names.intersection({"changechannel", "changechannelbynumber"})) for channel in grouped["channel"]):
        unsupported.append("channels")
    if unsupported:
        raise ValueError(f"Unsupported resources for {data['device_id']}: {', '.join(unsupported)}")

    def choices(field, entries, key):
        enum, labels = ("enum_values", "enum_labels") if data["protocol"] == "Matter" else ("enum", "x-enumLabels")
        values = list(dict.fromkeys(entry[key] for entry in entries))
        field[enum] = values
        field[labels] = {str(entry[key]): " · ".join(str(entry[part]) for part in
                        ("name", "kind", "artist", "provider") if entry.get(part)) for entry in entries}
        field["description"] = "Available resource choices: use the exact enum value matching the requested label."

    contents = [item.model_dump(exclude_none=True) for item in grouped["content"]]
    contents += [item.model_dump(exclude_none=True) for item in grouped["channel"] if item.kind == "radio"]
    media = [{key: value for key, value in item.items() if key not in ("url", "major_number", "minor_number")}
             | {"ContentURL": item["url"]} for item in contents]
    areas = [item.model_dump(exclude_none=True) | {"AreaID": i} for i, item in enumerate(grouped["cleaning_area"], 1)]
    tv_channels = [item for item in grouped["channel"] if item.kind == "tv"]
    used_numbers = {item.major_number for item in tv_channels if item.major_number is not None}
    channels = []
    for item in tv_channels:
        number = item.major_number
        if number is None:
            number = next(number for number in range(1, 65536) if number not in used_numbers)
            used_numbers.add(number)
        channels.append(item.model_dump(exclude_none=True) | {"MajorNumber": number,
                        "MinorNumber": item.minor_number if item.minor_number is not None else 0})
    inputs = [{"name": item.name, "Index": i} for i, item in enumerate(grouped["input"])]
    apps = [{"name": item.name, "ApplicationID": str(i), "CatalogVendorID": 65521}
            for i, item in enumerate(grouped["application"], 1)]

    bindings = {
        "launchurl": ("contents", media, ("ContentURL",)),
        "selectareas": ("cleaning_areas", areas, ("AreaID",)),
        "changechannelbynumber": ("channels", channels, ("MajorNumber", "MinorNumber")),
        "changechannel": ("channels", channels, ("Match",)),
        "selectinput": ("inputs", inputs, ("Index",)),
    } | {name: ("applications", apps, ("ApplicationID", "CatalogVendorID"))
         for name in ("launchapp", "stopapp", "hideapp")}
    for name, fields in actions:
        if name not in bindings:
            continue
        bucket, entries, keys = bindings[name]
        if not entries:
            continue
        if bucket == "applications":
            if "Application" not in fields:
                continue
            application = fields["Application"]
            fields = ({field["name"]: field for field in application["fields"]}
                      if data["protocol"] == "Matter" else application["properties"])
        elif name == "selectareas":
            fields = {"AreaID": fields["NewAreas"]["items"]}
        bound[bucket] = entries
        if name == "changechannel":
            entries = [{"name": entry["name"], "Match": entry["name"]} for entry in entries]
        for key in keys:
            choices(fields[key], entries, key)
    data["resources"] = bound

def generate_device(draft: DeviceDraft, protocol=None):
    protocol = protocol or draft.protocol
    data = deepcopy(PROFILES[draft.profile]["devices"][protocol]) | {
        "device_id": draft.device_id, "device_name": f"{draft.room}_{draft.profile}", "room": draft.room}
    if protocol == "W3C":
        data["td"]["title"] = data["device_name"]
    elif protocol == "SmartThings":
        for capability in data["capabilities"]:
            for command in capability.get("commands", {}).values():
                command.get("arguments", []).sort(key=lambda arg: (
                    arg.get("optional", False), arg.get("optional", False) and "default" not in arg["value_schema"]))
    _resource_options(data, draft.resources)

    return {"Matter": MatterDevice, "W3C": W3CDevice, "SmartThings": SmartThingsDevice}[protocol].model_validate(data)

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
        return {f"{capability.capability_name}/{name}": {
                    "name": name, "call": {"capability": capability.capability_name, "command": name},
                    "arguments": {arg.name: _schema_field(arg.value_schema, arg.name) | {"required": not arg.optional}
                                  for arg in command.arguments}}
                for capability in device.capabilities for name, command in capability.commands.items()}
    
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
    aliases = {"enum": "enum_values", "x-enumLabels": "enum_labels", "minLength": "min_length",
               "maxLength": "max_length", "minItems": "min_length", "maxItems": "max_length"}
    field.update({aliases.get(key, key): schema[key]
                  for key in ("minimum", "maximum", "unit", *aliases) if key in schema})
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
        if actual is not None and ((low in field and actual < field[low]) or (high in field and actual > field[high])):
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
    arguments = {name: value for name, value in arguments.items()
                 if value is not None or fields[name].get("nullable")}
    arguments = {name: deepcopy(field.get("default")) for name, field in fields.items()
                 if "default" in field or (field.get("required") and field.get("nullable"))} | arguments
    if {name for name, field in fields.items() if field.get("required")} - arguments.keys():
        raise ValueError("Missing required argument")
    return {name: _normalize(_coerce(value, fields[name]) if coerce else value, fields[name])
            for name, value in arguments.items()}

def _expected_value(value, field):
    if value is None:
        return None
    if isinstance(value, dict) and "fields" in field:
        fields = {item["name"]: item for item in field["fields"]}
        return {name: _expected_value(item, fields[name]) for name, item in value.items()}
    if isinstance(value, list) and "items" in field:
        return [_expected_value(item, field["items"]) for item in value]
    return _normalize(_coerce(value, field), field)

def _contains(actual, expected):
    if expected is None:
        return True
    if isinstance(expected, dict):
        return isinstance(actual, dict) and all(
            value is None or (name in actual and _contains(actual[name], value)) for name, value in expected.items())
    if isinstance(expected, list):
        return isinstance(actual, list) and len(actual) == len(expected) and all(
            _contains(a, e) for a, e in zip(actual, expected))
    return type(actual) is type(expected) and actual == expected

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
    def __init__(self, spec: Device):
        self.agent_id = spec.device_id
        self.spec = spec
        self.controls = device_controls(spec)
        self.handler = getattr(self, f"_{self.spec.protocol.lower()}_call")
        self.action_calls = []
        data = self.spec.model_dump(exclude_none=True, exclude={"resources"} if not self.spec.resources else None)
        if self.protocol == "Matter":
            for endpoint in data["endpoints"]:
                for cluster in endpoint["clusters"]:
                    cluster["attributes"] = [attr for attr in cluster["attributes"] if attr["writable"]]
        elif self.protocol == "W3C":
            data["td"]["properties"] = {name: prop for name, prop in data["td"]["properties"].items() if not prop["readOnly"]}
        else:
            for capability in data["capabilities"]:
                capability.pop("attributes", None)
        self._description_data = data
        self._descriptions = {}
        for control in [None, *self.controls]:
            self.describe(control)

    @property
    def description(self) -> str:
        return self.describe()

    def describe(self, control=None) -> str:
        if control in self._descriptions:
            return self._descriptions[control]
        data = deepcopy(self._description_data) if control is not None else self._description_data
        if control is not None:
            request = self.controls[control]["call"]
            if self.protocol == "Matter":
                data["endpoints"] = [endpoint for endpoint in data["endpoints"] if endpoint["endpoint_id"] == request["endpoint_id"]]
                for endpoint in data["endpoints"]:
                    endpoint["clusters"] = [cluster for cluster in endpoint["clusters"] if cluster["cluster_id"] == request["cluster_id"]]
                    for cluster in endpoint["clusters"]:
                        cluster["commands"] = [command for command in cluster["commands"] if command["command_id"] == request.get("command_id")]
                        cluster["attributes"] = [attribute for attribute in cluster["attributes"] if attribute["attribute_id"] == request.get("attribute_id")]
            elif self.protocol == "W3C":
                for kind, interaction in (("actions", "action"), ("properties", "property")):
                    data["td"][kind] = {name: spec for name, spec in data["td"][kind].items()
                                        if interaction == request["interaction"] and name == request["name"]}
            else:
                data["capabilities"] = [capability for capability in data["capabilities"]
                                        if capability["capability_name"] == request["capability"]]
                for capability in data["capabilities"]:
                    capability["commands"] = {request["command"]: capability["commands"][request["command"]]}
        self._descriptions[control] = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
        return self._descriptions[control]

    @property
    def protocol(self) -> str:
        return self.spec.protocol

    def call(self, **request):
        action = self.handler(**request)
        self.action_calls.append(action)
        return action

    def call_control(self, control, arguments):
        """Encode a named control's arguments using the device's existing API template."""
        spec = self.controls[control]
        request = spec["call"].copy()
        if "attribute_id" in request or request.get("interaction") == "property":
            request["value"] = arguments["value"]
        elif "capability" in request:
            arguments = arguments.copy()
            names = list(spec["arguments"])
            while names and names[-1] not in arguments:
                names.pop()
            for name in names:
                if name not in arguments and "default" in spec["arguments"][name]:
                    arguments[name] = deepcopy(spec["arguments"][name]["default"])
            if any(name not in arguments for name in names):
                raise ValueError("Cannot omit an intermediate SmartThings positional argument")
            request["arguments"] = [arguments[name] for name in names]
        else:
            request["arguments"] = arguments
        return self.call(**request)

    def validate_action(self, action: Action):
        if action.device_id != self.agent_id:
            raise ValueError(f"INVALID DEVICE ID: {action.device_id}")
        if action.action_name not in self.controls:
            raise ValueError(f"Unsupported control: {action.action_name}")
        spec = self.controls[action.action_name]
        arguments = _arguments(action.arguments, spec["arguments"], coerce=True)
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

def _protocol_control_ids(profile, device):
    if isinstance(device, MatterDevice):
        return {identifier: identifier for identifier in device_controls(device)}
    clusters = [(endpoint["endpoint_id"], cluster)
                for endpoint in PROFILES[profile]["devices"]["Matter"]["endpoints"] for cluster in endpoint["clusters"]]
    if isinstance(device, W3CDevice):
        names = {"invoke": iter(f"actions/{name}" for name in device.td.actions),
                 "write": iter(f"properties/{name}" for name, prop in device.td.properties.items() if not prop.readOnly)}
        return {control_id(endpoint, cluster["cluster_id"], operation, member[f"{kind}_id"]): next(names[operation])
                for endpoint, cluster in clusters
                for operation, kind, members in (("invoke", "command", cluster.get("commands", [])),
                                                  ("write", "attribute", [a for a in cluster.get("attributes", []) if a["writable"]]))
                for member in members}
    return {control_id(endpoint, cluster["cluster_id"], operation, member[f"{kind}_id"]):
                f"{capability.capability_name}/{member['name'][0].lower() + member['name'][1:] if operation == 'invoke' else 'write' + member['name']}"
            for (endpoint, cluster), capability in zip(clusters, device.capabilities)
            for operation, kind, members in (("invoke", "command", cluster.get("commands", [])),
                                              ("write", "attribute", [a for a in cluster.get("attributes", []) if a["writable"]]))
            for member in members}

class Environment:
    def __init__(self, devices: List[DeviceDraft], protocol: str | None = None):
        self.devices = [generate_device(draft, protocol) for draft in devices]
        self.rooms = list(dict.fromkeys(device.room for device in self.devices))
        self.control_maps = {
            device.device_id: _protocol_control_ids(draft.profile, device)
            for draft, device in zip(devices, self.devices)
        }
        self.agents = {device.device_id: DeviceAgent(device) for device in self.devices}
    
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

    def _resolve_action(self, action: Action) -> Action:
        return action.model_copy(update={"action_name":
            self.control_maps.get(action.device_id, {}).get(action.action_name, action.action_name)})

    def validate_action(self, action: Action):
        return self.get_agent(action.device_id).validate_action(self._resolve_action(action))

    def assemble_action(self, action: Action, expected=False) -> Action:
        action = self._resolve_action(action)
        agent = self.get_agent(action.device_id)
        if not expected:
            return agent.validate_action(action)
        fields = agent.controls[action.action_name]["arguments"]
        return action.model_copy(update={"arguments": {
            name: _expected_value(value, fields[name]) for name, value in action.arguments.items()}})

    def compile_criteria(self, criteria: Criteria) -> Criteria:
        return Criteria(expected_actions=[self.assemble_action(action, expected=True) for action in criteria.expected_actions])

    def validate_criteria_resources(self, criteria: Criteria):
        targets = {
            "launchurl": ("contents", ("ContentURL",)),
            "selectareas": ("cleaning_areas", ("AreaID",)),
            "changechannel": ("channels", ("name",)),
            "changechannelbynumber": ("channels", ("MajorNumber", "MinorNumber")),
            "selectinput": ("inputs", ("Index",)),
            "launchapp": ("applications", ("ApplicationID", "CatalogVendorID")),
            "stopapp": ("applications", ("ApplicationID", "CatalogVendorID")),
            "hideapp": ("applications", ("ApplicationID", "CatalogVendorID")),
        }
        for action in self.compile_criteria(criteria).expected_actions:
            agent = self.get_agent(action.device_id)
            name = re.sub(r"_?\d+$", "", agent.controls[action.action_name]["name"]).lower()
            if name not in targets:
                continue
            bucket, keys = targets[name]
            arguments = action.arguments
            if name == "selectareas":
                selections = [{"AreaID": value} for value in arguments.get("NewAreas") or []]
            elif name == "changechannel":
                selections = [{"name": arguments.get("Match")}]
            elif name in ("launchapp", "stopapp", "hideapp"):
                if name != "launchapp" and arguments.get("Application") is None:
                    continue
                selections = [arguments.get("Application") or {}]
            else:
                selections = [arguments]
            entries = agent.spec.resources.get(bucket, [])
            if not selections or any(not any(all(
                selection.get(key) is not None and selection[key] == entry[key] for key in keys
            ) for entry in entries) for selection in selections):
                raise ValueError(f"Unregistered resource target: {action.device_id}/{action.action_name}")

    def render(self) -> tuple[str, dict]:
        lines, lookup = ["* = required; {...} = options; [min..max] = range; omitted arguments use defaults.",
                         "Resources are available call targets; use their listed argument values, not names. ContentURL values are synthetic fixtures."], {}
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
        return self.get_agent(action.device_id).call_control(action.action_name, action.arguments)

    def discovery(self):
        return {agent.agent_id: agent.description for agent in self.agents.values()}

    def evaluate(self, criteria: Criteria, action_calls: List[Action] | None = None):
        consequence = [self.validate_action(action) for action in (self.action_calls if action_calls is None else action_calls)]
        expected = self.compile_criteria(Criteria(expected_actions=[
            action.model_copy(update={"arguments": {name: value for name, value in action.arguments.items()
                                                    if name not in IGNORED_EVALUATION_ARGUMENTS}})
            for action in criteria.expected_actions
        ])).expected_actions
        candidates = [[i for i, action in enumerate(consequence)
                       if (action.device_id, action.action_name) == (goal.device_id, goal.action_name)
                       and _contains(action.arguments, goal.arguments)] for goal in expected]

        matched = {}
        def match(goal, visited):
            for action in candidates[goal]:
                if action not in visited:
                    visited.add(action)
                    if action not in matched or match(matched[action], visited):
                        matched[action] = goal
                        return True
            return False

        correct = sum(match(goal, set()) for goal in range(len(expected)))
        return {
            "precision": correct / len(consequence) if consequence else 0.0,
            "recall": correct / len(expected),
            "accuracy": float(correct == len(expected) == len(consequence)),
        }
