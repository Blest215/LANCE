from settings import *
from schema import *
from model import Model

class ScreeningResult(BaseModel):
    relevance: float = Field(description="How much you can contribute to the task. 0 <= score <= 1", ge=0, le=1)
    proposal: str = Field(description="Short response message that describes what you can contribute to the task. Do not mention what you cannot do.")

SCREENER_PROMPT = ChatPromptTemplate.from_template(
"""You are an AI agent that controls the following device: {description}
Can you contribute to the following request? {request}""")

CONTROLLER_PROMPT = ChatPromptTemplate.from_template(
"""You are an AI agent that controls the following device: {description}
Control the device for the request: {request}
Use argument property_name keys.""")

class DeviceAgent:
    def __init__(self, spec: DeviceSpec, model: Model | None):
        self.agent_id = spec.device_id
        self.spec = spec
        self.properties = {property_spec.property_name: property_spec.initial_value for property_spec in self.spec.properties}
        self.property_specs = {property_spec.property_name: property_spec for property_spec in self.spec.properties}
        self.actions = {action_spec.action_name: action_spec for action_spec in self.spec.actions}

        self.model = model
        if self.model is not None:
            self.screener = create_generator(SCREENER_PROMPT, ScreeningResult, model)
            # TODO ReAct
            self.controller = CONTROLLER_PROMPT | model.with_tools([get_device_property, call_device_action])

    @property
    def description(self) -> str:
        properties = []
        for prop in self.spec.properties:
            domain = prop.model_dump(exclude_none=True, exclude={"initial_value"})
            domain["value"] = self.properties[prop.property_name]
            properties.append(domain)
        actions = []
        for action in self.spec.actions:
            actions.append({"action_name": action.action_name, "description": action.description,
                            "arguments": [argument.model_dump(exclude_none=True, exclude={"initial_value"})
                                          for argument in action.arguments], "required": action.required})
        return json.dumps({"device_id": self.spec.device_id, "device_name": self.spec.device_name,
                           "device_type": self.spec.device_type, "room_id": self.spec.room_id,
                           "properties": properties, "actions": actions}, ensure_ascii=False)
    
    def screen(self, request: str, structured: bool):
        result = self.screener.invoke({"description": self.description, "request": request})
        return f"[{self.agent_id}] {self.description if structured else result.proposal}" if result.relevance >= RECRUIT_SCREENING_THRESHOLD else ""

    def instruct(self, instruction: str):
        result = self.controller.invoke({"description": self.description, "request": instruction})
        return [self.call(tool_call["args"]["action_name"], tool_call["args"].get("arguments", {})) for tool_call in result.tool_calls]

    def get(self, property_name: str):    
        if property_name in self.properties:
            return self.properties[property_name]
        raise ValueError(f"UNKNOWN NAME: {property_name} for {self.spec.device_name}")

    def call(self, action_name: str, arguments: Dict[str, str | int | float | bool] | None = None):
        arguments = {} if arguments is None else arguments
        if action_name in self.actions:
            action = self.actions[action_name]
            allowed = {argument.property_name for argument in action.arguments}
            if set(arguments) - allowed:
                raise ValueError(f"UNKNOWN_ARGUMENT: {sorted(set(arguments) - allowed)}")
            missing = set(action.required) - set(arguments)
            if missing:
                raise ValueError(f"MISSING_ARGUMENT: {sorted(missing)}")
            for argument_spec in action.arguments:
                name = argument_spec.property_name
                if name in arguments:
                    argument_spec.validate_value(arguments[name])

            updates = dict(self.properties)
            for effect_spec in action.effects:
                original_value = updates[effect_spec.target_property]
                if isinstance(effect_spec, ToggleEffectSpec):
                    if type(original_value) is not bool:
                        raise ValueError("toggle requires a boolean property")
                    update = not original_value
                else:
                    if isinstance(effect_spec, FromArgumentEffectSpec):
                        if effect_spec.argument_name not in arguments:
                            raise ValueError(f"MISSING_ARGUMENT: {effect_spec.argument_name}")
                        value = arguments[effect_spec.argument_name]
                    else:
                        value = effect_spec.constant
                    if effect_spec.operation == "set":
                        update = value
                    else:
                        if type(original_value) not in (int, float) or type(value) not in (int, float):
                            raise ValueError("only numeric values can be added or subtracted")
                        update = original_value + value if effect_spec.operation == "add" else original_value - value
                updates[effect_spec.target_property] = update
            for name, value in updates.items():
                self.property_specs[name].validate_value(value)
            self.properties = updates
            return
        raise ValueError(f"UNKNOWN NAME: {action_name} for {self.spec.device_name}")

class Simulator:
    def __init__(self, scene: dict, model: Model | None):
        self.rooms = scene["rooms"]
        self.devices = [DeviceSpec.model_validate(device) for device in scene["devices"]]
        self.reset(model)

    def reset(self, model):
        self.agents = {device_spec.device_id: DeviceAgent(device_spec, model) for device_spec in self.devices}

    def get(self, device_id: str, property_name: str):
        if device_id not in self.agents:
            raise ValueError(f"UNKNOWN_DEVICE_ID: {device_id}")
        return self.agents[device_id].get(property_name)

    def call(self, device_id: str, action_name: str, arguments: Dict[str, str | int | float | bool] | None = None):
        if device_id not in self.agents:
            raise ValueError(f"UNKNOWN_DEVICE_ID: {device_id}")
        return self.agents[device_id].call(action_name, arguments)

    def instruct(self, agent_id: str, instruction: str):
        if agent_id not in self.agents:
            raise ValueError(f"UNKNOWN_DEVICE_ID: {agent_id}")
        return self.agents[agent_id].instruct(instruction)

    def discovery(self):
        return [f"{agent.agent_id}: {agent.description}" for agent in self.agents.values()]

    def recruit(self, request: str, structured: bool):
        return [agent.screen(request, structured) for agent in self.agents.values()]

    def evaluate(self, task: Task):
        scores = []
        for goal_state in task.goal_states:
            try:
                if goal_state.entity_type == "device":
                    agent = self.agents[goal_state.entity_id]
                    agent.property_specs[goal_state.attribute].validate_value(goal_state.value)
                    scores.append(1 if agent.properties[goal_state.attribute] == goal_state.value else 0)
            except (KeyError, ValueError):
                scores.append(0)
        return sum(scores) / len(scores)        

    def render(self):
        return {device_id: device.properties for device_id, device in self.agents.items()}

    def print(self):
        for device_id, device in self.agents.items():
            for name, value in device.properties.items():
                print(f"[{device_id}] {name}: {value}")
            for name, value in device.actions.items():
                print(f"[{device_id}] {name}: {value}")
