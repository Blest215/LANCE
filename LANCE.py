from abc import ABC, abstractmethod
from functools import wraps
from time import perf_counter
from langchain_core.runnables import RunnableLambda

from settings import *
from environment import *
from model import Model, CallLogger

SCREENER_QUESTION = {
    "type": "noul",
    "instructions": "Can this device contribute to the user's request using its supported controls?",
    "criteria": {"true": "Can fulfill at least part of the request", "false": "Cannot contribute to the request"},
}

CONTROLLER_PROMPT = ChatPromptTemplate.from_template(
"""Accomplish \"{request}\" with this device, using exact device_ids and supported calls: {description}""")

def log(method):
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        start = perf_counter()
        stage = method.__name__
        self.token_log.setdefault(stage, [])
        try:
            return method(self, *args, **kwargs)
        finally:
            self.time_log.setdefault(stage, []).append(perf_counter() - start)
    return wrapper

class UserAgent(ABC):
    def __init__(self, model: Model):
        self.model = model
        self.time_log = {}
        self.token_log = {}

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
                results.append(self.orchestration_handler(environment, call["args"]))
            except Exception as e:
                results.append(str(e))
        return results

    @abstractmethod
    def orchestration_handler(self, environment: Environment, call: dict) -> List:
        pass

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
        result = RunnableLambda(lambda device_id: self.screener.decide(
            state={"request": user_utterance, "description": descriptions[device_id]},
            question=SCREENER_QUESTION, token_log=self.token_log, stage="discovery", device_id=device_id,
        )).batch(list(descriptions))
        return {device_id: description for (device_id, description), decision in zip(descriptions.items(), result)
                if decision["answers"]["decision"]["noul"] >= 0.5}

    def orchestration_handler(self, environment, call):
        agent = environment.get_agent(call["device_id"])
        result = self.orchestrators[agent.protocol].invoke(
            {"description": agent.description, "request": call["instruction"]},
            config=self.llm_config("orchestration", agent.agent_id)
        )
        return [
            agent.call(**{name: value for name, value in tool_call["args"].items() if name != "device_id"})
            for tool_call in result.tool_calls
        ]
