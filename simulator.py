from settings import *
from schema import *
from model import Model
from collections import Counter

class ScreeningResult(BaseModel):
    relevance: float = Field(description="How much you can contribute to the task. 0 <= score <= 1", ge=0, le=1)
    proposal: str = Field(description="Short response message that describes what you can contribute to the task. Do not mention what you cannot do.")

SCREENER_PROMPT = ChatPromptTemplate.from_template(
"""You are an AI agent that controls the following device: {description}
Can you contribute to the following request? {request}""")

CONTROLLER_PROMPT = ChatPromptTemplate.from_template(
"""You are an AI agent that controls the following device: {description}
Control the device for the request: {request}
Use native device_id, endpoint_id and cluster_id. Invoke command_id with named arguments, or write a writable attribute_id with value.""")

class DeviceAgent:
    def __init__(self, spec: Device, model: Model | None, simulator):
        self.agent_id = spec.device_id
        self.spec = spec
        self.simulator = simulator

        self.model = model
        if self.model is not None:
            self.screener = create_generator(SCREENER_PROMPT, ScreeningResult, model)
            # TODO ReAct
            self.controller = CONTROLLER_PROMPT | model.with_tools([call_device_matter])

    @property
    def description(self) -> str:
        return self.spec.model_dump_json(exclude={"provenance"}, exclude_none=True)
    
    def screen(self, request: str, structured: bool):
        result = self.screener.invoke({"description": self.description, "request": request})
        return f"[{self.agent_id}] {self.description if structured else result.proposal}" if result.relevance >= RECRUIT_SCREENING_THRESHOLD else ""

    def instruct(self, instruction: str):
        result = self.controller.invoke({"description": self.description, "request": instruction})
        return [self.call(**tool_call["args"]) for tool_call in result.tool_calls]

    def call(self, device_id, **request):
        if device_id != self.agent_id:
            raise ValueError(f"UNSUPPORTED_DEVICE: {device_id}")
        return self.simulator.call(device_id=device_id, **request)

class Simulator:
    def __init__(self, scene: Scene | dict, model: Model | None = None):
        parsed = Scene.model_validate(scene)
        self.rooms = [room.model_dump() for room in parsed.rooms]
        self.devices = parsed.devices
        if len({device.device_id for device in self.devices}) != len(self.devices):
            raise ValueError("device IDs must be unique within a scene")
        self.controls = {device.device_id: self.device_controls(device) for device in self.devices}
        self.reset(model)

    @staticmethod
    def control_id(endpoint_id, cluster_id, operation, member_id):
        return f"{endpoint_id}/{cluster_id}/{operation}/{member_id}"

    @classmethod
    def device_controls(cls, device):
        if not isinstance(device, MatterDevice):
            raise NotImplementedError("W3C and SmartThings control mappings are not implemented")
        controls = {}
        for endpoint in device.endpoints:
            for cluster in endpoint.clusters:
                for command in cluster.commands:
                    key = cls.control_id(endpoint.endpoint_id, cluster.cluster_id, "invoke", command["command_id"])
                    controls[key] = {"name": command["name"],
                        "arguments": {field["name"]: field for field in command["fields"]}}
                for attribute in cluster.attributes:
                    if attribute["writable"]:
                        key = cls.control_id(endpoint.endpoint_id, cluster.cluster_id, "write", attribute["attribute_id"])
                        controls[key] = {"name": attribute["name"],
                            "arguments": {"value": attribute | {"required": True}}}
        return controls

    @classmethod
    def _normalize(cls, value, field):
        if value is None and field.get("nullable"):
            return None
        kind = field["property_type"]
        types = {"boolean": (bool,), "integer": (int,), "number": (int, float),
                 "string": (str,), "array": (list,), "object": (dict,)}
        if kind in types and type(value) not in types[kind]:
            raise ValueError(f"Invalid type for {field['name']}")
        if "enum_values" in field and value not in field["enum_values"]:
            raise ValueError(f"Invalid choice for {field['name']}")
        for bound, compare in (("minimum", lambda a, b: a < b), ("maximum", lambda a, b: a > b)):
            if bound in field and compare(value, field[bound]):
                raise ValueError(f"Out of range: {field['name']}")
        for bound, compare in (("min_length", lambda a, b: a < b), ("max_length", lambda a, b: a > b)):
            if bound in field and compare(len(value), field[bound]):
                raise ValueError(f"Invalid length: {field['name']}")
        if kind == "array":
            return [cls._normalize(item, field["items"]) for item in value]
        if kind == "object" and "fields" in field:
            return cls._arguments(value, {member["name"]: member for member in field["fields"]})
        return float(value) if kind == "number" else value

    @classmethod
    def _arguments(cls, arguments, fields):
        if arguments.keys() - fields.keys():
            raise ValueError("Unknown argument")
        if {name for name, field in fields.items() if field.get("required")} - arguments.keys():
            raise ValueError("Missing required argument")
        return {name: cls._normalize(value, fields[name]) for name, value in arguments.items()}

    def validate_action(self, action: ExpectedAction):
        if action.device_id not in self.controls:
            raise ValueError(f"UNSUPPORTED_DEVICE: {action.device_id}")
        controls = self.controls[action.device_id]
        if action.control_id not in controls:
            raise ValueError(f"Unsupported control: {action.control_id}")
        arguments = self._arguments(action.arguments, controls[action.control_id]["arguments"])
        return action.model_copy(update={"arguments": arguments})

    def task_scene(self):
        return {"rooms": self.rooms, "devices": [
            {"device_id": device.device_id, "device_name": device.device_name, "room_id": device.room_id,
             "controls": self.controls[device.device_id]} for device in self.devices]}

    def reset(self, model):
        self.action_calls = []
        self.agents = {device.device_id: DeviceAgent(device, model, self) for device in self.devices}

    def call(self, device_id, endpoint_id, cluster_id,
             command_id=None, attribute_id=None, arguments=None, **request):
        if command_id is not None and attribute_id is None and (not request or request == {"value": None}):
            operation, member_id, payload = "invoke", command_id, arguments or {}
        elif attribute_id is not None and command_id is None and not arguments and set(request) == {"value"}:
            operation, member_id, payload = "write", attribute_id, {"value": request["value"]}
        else:
            raise ValueError("Invalid Matter call")
        action = ExpectedAction(device_id=device_id,
            control_id=self.control_id(endpoint_id, cluster_id, operation, member_id), arguments=payload)
        self.action_calls.append(self.validate_action(action))

    def instruct(self, device_id: str, instruction: str):
        if device_id not in self.agents:
            raise ValueError(f"UNSUPPORTED_DEVICE: {device_id}")
        return self.agents[device_id].instruct(instruction)

    def discovery(self):
        return [f"{agent.agent_id}: {agent.description}" for agent in self.agents.values()]

    def recruit(self, request: str, structured: bool):
        return [agent.screen(request, structured) for agent in self.agents.values()]

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
