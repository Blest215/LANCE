from abc import ABC, abstractmethod
from functools import wraps
from hashlib import sha256
from time import perf_counter
import json
import re

from settings import *
from environment import *
from model import Model, CallLogger

CONTROLLER_PROMPT = ChatPromptTemplate.from_template(
"""Accomplish the requested tasks with the available devices for the intended targets, locations, and resources.
using exact device_ids and supported calls.

[Request] {request}
[Available Devices] {description}""")

TOOL_CONTROLLER_PROMPT = ChatPromptTemplate.from_template(
    CONTROLLER_PROMPT.messages[0].prompt.template.removesuffix("\n[Available Devices] {description}"))

def log(method):
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        start = perf_counter()
        stage = method.__name__
        calls = self.token_log.setdefault(stage, [])
        durations = self.time_log.setdefault(stage, [])
        first_call = len(calls)
        try:
            return method(self, *args, **kwargs)
        finally:
            self.wall_time_log.setdefault(stage, []).append(perf_counter() - start)
            durations.extend(record["elapsed"] for record in calls[first_call:]
                             if record.get("elapsed") is not None)
    return wrapper

class UserAgent(ABC):
    def __init__(self, model: Model):
        self.model = model
        self.time_log = {}
        self.token_log = {}
        self.wall_time_log = {}

    def llm_config(self, stage, device_id=None):
        return {"callbacks": [CallLogger(
            self.token_log.setdefault(stage, []), stage, str(self.model), device_id
        )]}

    @log
    def setup(self, environment: Environment):
        self.setup_handler(environment)

    def setup_handler(self, environment: Environment):
        pass

    def main(self, environment: Environment, user_utterance: str):
        log = {}
        try:
            self.setup(environment)
            
            discovery = self.discovery(environment, user_utterance)
            log["discovery"] = list(discovery.keys())
            debug(discovery)

            calls = self.composition(discovery, user_utterance)
            log["calls"] = calls
            debug(calls)

            results = self.orchestration(environment, calls)
            log["results"] = results
            debug(results)
        except Exception as e:
            debug(e)
            log["exception"] = str(e)
        log["wall_time"] = self.wall_time_log
        log["timing_mode"] = "per_call"
        return log

    @log
    def discovery(self, environment: Environment, user_utterance: str):
        return self.discovery_handler(environment, user_utterance)

    @abstractmethod
    def discovery_handler(self, environment: Environment, user_utterance: str) -> Dict[str, str]:
        pass

    @log
    def composition(self, descriptions: Dict[str, str], user_utterance: str) -> List[dict]:
        return self.composition_handler(descriptions, user_utterance)

    def composition_handler(self, descriptions: Dict[str, str], user_utterance: str) -> List[dict]:
        return self.composer.invoke({
            "description": descriptions, 
            "request": user_utterance
        }, config=self.llm_config("composition")).tool_calls

    @log
    def orchestration(self, environment: Environment, calls: List[dict]) -> List:
        results = []
        for call in calls:
            try:
                arguments = call["args"].copy()
                agent = environment.get_agent(arguments.pop("device_id"))
                results.append(self.orchestration_handler(agent, arguments))
            except Exception as e:
                results.append(str(e))
        return results

    @abstractmethod
    def orchestration_handler(self, agent: DeviceAgent, call: dict) -> List:
        pass

SCREENER_QUESTION = {
    "type": "noul",
    "instructions": "Can this device contribute to some of the requested tasks?",
    "criteria": {
        "true": "Can contribute to at least one requested task within its constraints",
        "false": "Cannot contribute to any requested task within its constraints",
    },
}

class LANCE(UserAgent):
    def __init__(self, model, decision_model="tev1:4b-q4_K_M", noul_threshold=0.5):
        super().__init__(model)
        self.decision_model = decision_model
        self.noul_threshold = noul_threshold

    def _get_orchestrators(self, environment):
        orchestrators = {}
        for device_id, agent in environment.agents.items():
            if not agent.controls:
                continue
            tools = [_descriptive_tool(agent, control, spec) for control, spec in agent.controls.items()]
            mapping = {tool["function"]["name"]: control for tool, control in zip(tools, agent.controls)}
            orchestrators[device_id] = TOOL_CONTROLLER_PROMPT | self.model.with_tools(tools), mapping
        return orchestrators

    def setup_handler(self, environment):
        self.composer = CONTROLLER_PROMPT | self.model.with_tools([instruct_agent])
        self.screener = Model(self.decision_model)
        self.orchestrators = self._get_orchestrators(environment)

    def discovery_handler(self, environment, user_utterance):
        descriptions = environment.discovery()
        selected = {}
        for device_id, description in descriptions.items():
            decision = self.screener.decide(
                state={"request": user_utterance, "device": description},
                question=SCREENER_QUESTION, token_log=self.token_log,
                stage="discovery", device_id=device_id,
            )
            if decision["answers"]["decision"]["noul"] >= self.noul_threshold:
                selected[device_id] = description
        return selected

    def orchestration_handler(self, agent, call):
        if not agent.controls:
            return []
        orchestrator, mapping = self.orchestrators[agent.agent_id]
        result = orchestrator.invoke({"request": call["instruction"]},
                                     config=self.llm_config("orchestration", agent.agent_id))
        return [agent.call_control(mapping[call["name"]], call["args"]) for call in result.tool_calls]

SCREENER_PROMPT = ChatPromptTemplate.from_template(
"""Can this device contribute to some of the requested tasks?
true: Can contribute to at least one requested task within its constraints
false: Cannot contribute to any requested task within its constraints

[Request] {request}
[Device] {description}""")

class Screen(BaseModel):
    decision: bool

class LANCE_no_decision(LANCE):
    def setup_handler(self, environment):
        self.composer = CONTROLLER_PROMPT | self.model.with_tools([instruct_agent])
        self.screener = create_generator(SCREENER_PROMPT, Screen, self.model)
        self.orchestrators = self._get_orchestrators(environment)

    def discovery_handler(self, environment, user_utterance):
        descriptions = environment.discovery()
        selected = {}
        for device_id, description in descriptions.items():
            if self.screener.invoke(
                {"request": user_utterance, "description": description},
                config=self.llm_config("discovery", device_id),
            ).decision:
                selected[device_id] = description
        return selected

class LANCE_no_discovery(LANCE):
    def discovery_handler(self, environment, user_utterance):
        return environment.discovery()

class LANCE_no_separation(LANCE):
    def setup_handler(self, environment):
        self.composer = CONTROLLER_PROMPT | self.model.with_tools([instruct_agent])
        self.screener = Model(self.decision_model)
        self.orchestrators = {
            protocol: CONTROLLER_PROMPT | self.model.with_tools([tool])
            for protocol, tool in TOOLS.items()
        }

    def orchestration_handler(self, agent, call):
        result = self.orchestrators[agent.protocol].invoke(
            {"description": agent.description, "request": call["instruction"]},
            config=self.llm_config("orchestration", agent.agent_id)
        )
        return [
            agent.call(**{name: value for name, value in tool_call["args"].items() if name != "device_id"})
            for tool_call in result.tool_calls
        ]

class LANCE_no_instruction(LANCE):
    def setup_handler(self, environment):
        self.screener = Model(self.decision_model)
        self.tools, self.controls = {}, {}
        for device_id, agent in environment.agents.items():
            self.tools[device_id] = []
            for control, spec in agent.controls.items():
                tool = _descriptive_tool(agent, control, spec)
                tool["function"]["name"] = f"d{sha256(device_id.encode()).hexdigest()[:8]}_{tool['function']['name']}"
                self.tools[device_id].append(tool)
                self.controls[tool["function"]["name"]] = device_id, control

    def composition_handler(self, descriptions, user_utterance):
        tools = [tool for device_id in descriptions for tool in self.tools[device_id]]
        if not tools:
            return []
        composer = TOOL_CONTROLLER_PROMPT | self.model.with_tools(tools)
        calls = composer.invoke({"request": user_utterance}, config=self.llm_config("composition")).tool_calls
        return [call | {"args": {
            "device_id": self.controls[call["name"]][0],
            "control": self.controls[call["name"]][1], "arguments": call["args"],
        }} for call in calls]

    def orchestration_handler(self, agent, call):
        return agent.call_control(call["control"], call["arguments"])

def _argument_schema(field):
    schema = {"type": field["property_type"]} if field["property_type"] != "opaque" else {}
    for source, target in (("enum_values", "enum"), ("minimum", "minimum"), ("maximum", "maximum"),
                           ("default", "default"), ("min_length", "minItems" if field["property_type"] == "array" else "minLength"),
                           ("max_length", "maxItems" if field["property_type"] == "array" else "maxLength")):
        if source in field:
            schema[target] = field[source]
    if "fields" in field:
        schema.update(type="object", properties={f["name"]: _argument_schema(f) for f in field["fields"]},
                      required=[f["name"] for f in field["fields"] if f.get("required")], additionalProperties=False)
    if "items" in field:
        schema["items"] = _argument_schema(field["items"])
    if "title" in field:
        schema["title"] = field["title"]
    details = {key: field[key] for key in ("description", "semantics", "unit", "enum_labels") if key in field}
    if details:
        schema["description"] = json.dumps(details, ensure_ascii=False)
    if field.get("nullable"):
        schema = {"anyOf": [schema, {"type": "null"}]}
    return schema

def _control_tool(control, spec):
    name = re.sub(r"[^a-zA-Z0-9_-]", "_", spec["name"])[:40]
    fields = [field | {"name": key, "title": field.get("title") or (
        re.sub(r"^write_?", "", spec["name"], flags=re.I) if key == "value" else field.get("name", key))}
        for key, field in spec["arguments"].items()]
    operation = spec["name"].replace("_", "").lower()
    for field in fields:
        key = field["name"]
        if ((operation == "movetolevel" and key == "Level")
                or (operation == "step" and key == "StepSize")
                or (operation in ("writeonlevel", "writestartupcurrentlevel") and key == "value")):
            mode = "Relative brightness change" if key == "StepSize" else "Absolute brightness"
            field["semantics"] = f"{mode} on a raw 0–254 scale: percentage * 254 / 100, rounded to an integer. Preserve explicitly requested raw or sentinel values."
        elif operation == "setpointraiselower" and key == "Amount":
            field["semantics"] = "Signed relative temperature change in 0.1 Celsius units: Celsius change * 10. Positive raises, negative lowers; not an absolute setpoint."
        elif "setpoint" in operation and key == "value" and "unit" in field:
            field["semantics"] = f"Absolute temperature setpoint in {field['unit']} per raw unit; convert the requested temperature to this scale."
    return {"type": "function", "function": {
        "name": f"{name}_{sha256(control.encode()).hexdigest()[:12]}", "description": f"{spec['name']} ({control})",
        "parameters": _argument_schema({"property_type": "object", "fields": fields}),
    }}


def _resource_arguments(fields, resource):
    arguments = {}
    for name, field in fields.items():
        if name in resource:
            arguments[name] = resource[name]
        elif "fields" in field:
            nested = _resource_arguments({f["name"]: f for f in field["fields"]}, resource)
            if nested:
                arguments[name] = nested
    return arguments


def _descriptive_tool(agent, control, spec):
    tool = _control_tool(control, spec)
    device, request = agent.spec, spec["call"]
    context = {"device_id": agent.agent_id, "device_name": device.device_name, "room": device.room}
    if agent.protocol == "Matter":
        endpoint = next(e for e in device.endpoints if e.endpoint_id == request["endpoint_id"])
        cluster = next(c for c in endpoint.clusters if c.cluster_id == request["cluster_id"])
        context.update(endpoint=endpoint.device_types, service=cluster.name)
    elif agent.protocol == "W3C":
        item = getattr(device.td, "actions" if request["interaction"] == "action" else "properties")[request["name"]]
        context.update(service=request["interaction"], title=item.model_dump().get("title", request["name"]))
    else:
        context["service"] = request["capability"]
    resources = {"launchurl": "contents", "selectareas": "cleaning_areas",
                 "changechannel": "channels", "changechannelbynumber": "channels", "selectinput": "inputs",
                 "launchapp": "applications", "stopapp": "applications", "hideapp": "applications"}
    operation = (context.get("title") or spec["name"]).lower()
    bucket = resources.get(operation)
    if bucket in device.resources:
        context["resources"] = []
        for resource in device.resources[bucket]:
            values = resource
            if operation == "changechannel":
                values = resource | {"Match": resource["name"]}
            elif operation == "selectareas":
                values = resource | {"NewAreas": [resource["AreaID"]]}
            context["resources"].append({
                "label": " · ".join(str(resource[k]) for k in ("name", "kind", "artist", "provider") if resource.get(k)),
                "arguments": _resource_arguments(spec["arguments"], values),
            })
    tool["function"]["description"] += "\n" + json.dumps(context, ensure_ascii=False, separators=(",", ":"))
    return tool
