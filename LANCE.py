from abc import ABC, abstractmethod
from functools import wraps
from time import perf_counter

from settings import *
from environment import *
from model import Model, CallLogger

CONTROLLER_PROMPT = ChatPromptTemplate.from_template(
"""Accomplish the user's request with the avilable devices, using exact device_ids and supported calls.

[Request] {request}
[Available Devices] {description}""")

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
    "instructions": "Can this device carry out a some of the requested tasks, matching its intended target, location, and resources?",
    "criteria": {
        "true": "Can carry out at least one requested task within its constraints",
        "false": "Cannot carry out any requested task within its constraints",
    },
}

class LANCE(UserAgent):
    def setup_handler(self, environment):
        self.composer = CONTROLLER_PROMPT | self.model.with_tools([instruct_agent])
        self.screener = Model("tev1:4b-q4_K_M")
        self.orchestrators = {
            protocol: CONTROLLER_PROMPT | self.model.with_tools([tool])
            for protocol, tool in TOOLS.items()
        }

    def discovery_handler(self, environment, user_utterance):
        descriptions = environment.discovery()
        selected = {}
        for device_id, description in descriptions.items():
            decision = self.screener.decide(
                state={"request": user_utterance, "description": description},
                question=SCREENER_QUESTION, token_log=self.token_log,
                stage="discovery", device_id=device_id,
            )
            if decision["answers"]["decision"]["noul"] >= 0.5:
                selected[device_id] = description
        return selected

    def orchestration_handler(self, agent, call):
        result = self.orchestrators[agent.protocol].invoke(
            {"description": agent.description, "request": call["instruction"]},
            config=self.llm_config("orchestration", agent.agent_id)
        )
        return [
            agent.call(**{name: value for name, value in tool_call["args"].items() if name != "device_id"})
            for tool_call in result.tool_calls
        ]
