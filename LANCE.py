from abc import ABC, abstractmethod
from functools import wraps
from time import perf_counter

from settings import *
from environment import *
from model import Model, CallLogger

class Proposal(BaseModel):
    relevance: bool

SCREENER_PROMPT = ChatPromptTemplate.from_template(
"""Determine whether you can contribute to the request \"{request}\" by using this device: {description}""")

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

            calls = self.plan(discovery, user_utterance)
            log["calls"] = calls
            debug(calls)

            results = self.control(environment, calls)
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
    def plan(self, descriptions: Dict[str, str], user_utterance: str) -> List[dict]:
        return self.plan_handler(descriptions, user_utterance)

    def plan_handler(self, descriptions: Dict[str, str], user_utterance: str) -> List[dict]:
        return self.planner.invoke({
            "description": descriptions, 
            "request": user_utterance
        }, config=self.llm_config("plan")).tool_calls

    @log
    def control(self, environment: Environment, calls: List[dict]) -> List:
        results = []
        for call in calls:
            try:
                results.append(self.control_handler(environment, call["args"]))
            except Exception as e:
                results.append(str(e))
        return results

    @abstractmethod
    def control_handler(self, environment: Environment, call: dict) -> List:
        pass

class LANCE(UserAgent):
    def setup_handler(self, environment):
        self.planner = CONTROLLER_PROMPT | self.model.with_tools([instruct_agent])
        self.screener = create_generator(SCREENER_PROMPT, Proposal, self.model)
        self.controller = {
            protocol: CONTROLLER_PROMPT | self.model.with_tools([tool])
            for protocol, tool in TOOLS.items()
        }

    def discovery_handler(self, environment, user_utterance):
        descriptions = environment.discovery()
        result = self.screener.batch(
            [{"description": description, "request": user_utterance} for description in descriptions.values()],
            config=[self.llm_config("setup", device_id) for device_id in descriptions]
        )
        return {device_id: descriptions[device_id] for device_id, proposal in zip(descriptions.keys(), result) if proposal.relevance}

    def control_handler(self, environment, call):
        agent = environment.get_agent(call["device_id"])
        result = self.controller[agent.protocol].invoke(
            {"description": agent.description, "request": call["instruction"]},
            config=self.llm_config("control", agent.agent_id)
        )
        return [
            agent.call(**{name: value for name, value in tool_call["args"].items() if name != "device_id"})
            for tool_call in result.tool_calls
        ]
