from abc import ABC, abstractmethod
from functools import wraps
from time import perf_counter
from langchain_core.callbacks import get_usage_metadata_callback

from settings import *
from environment import *
from model import Model
from schema import clean_text

class Proposal(BaseModel):
    description: str

    @field_validator("description")
    @classmethod
    def clean_description(cls, value: str) -> str:
        return clean_text(value)

SCREENER_PROMPT = ChatPromptTemplate.from_template(
"""You are an AI agent controlling: {description}
Describe what can be done with the device.""")

CONTROLLER_PROMPT = ChatPromptTemplate.from_template(
"""You are an AI agent controlling: {description}
Fulfill the request: {request}""")

def log(method):
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        start = perf_counter()
        with get_usage_metadata_callback() as usage:
            try:
                return method(self, *args, **kwargs)
            finally:
                if method.__name__ not in self.time_log:
                    self.time_log[method.__name__] = []
                self.time_log[method.__name__].append(perf_counter() - start)
                if method.__name__ not in self.token_log:
                    self.token_log[method.__name__] = []
                self.token_log[method.__name__].extend(list(usage.usage_metadata.values()))
    return wrapper

class UserAgent(ABC):
    def __init__(self, model: Model):
        self.model = model
        self.time_log = {}
        self.token_log = {}

    @log
    def setup(self, environment: Environment):
        self.setup_handler(environment)

    def setup_handler(self, environment: Environment):
        pass

    def main(self, environment: Environment, user_utterance: str):
        self.setup(environment)
        log = {}
        try:
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
        return self.planner.invoke({"description": descriptions, "request": user_utterance}).tool_calls

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
        self.proposer = create_generator(SCREENER_PROMPT, Proposal, self.model)
        
        descriptions = environment.discovery()
        result = self.proposer.batch([{"description": description} for description in descriptions.values()])
        self.proposals = {device_id: proposal.description for device_id, proposal in zip(descriptions.keys(), result)}
        self.controller = {
            protocol: CONTROLLER_PROMPT | self.model.with_tools([tool])
            for protocol, tool in TOOLS.items()
        }

    def discovery_handler(self, environment, user_utterance):
        return self.proposals

    def control_handler(self, environment, call):
        agent = environment.get_agent(call["device_id"])
        result = self.controller[agent.protocol].invoke({"description": agent.description, "request": call["instruction"]})
        return [
            agent.call(**{name: value for name, value in tool_call["args"].items() if name != "device_id"})
            for tool_call in result.tool_calls
        ]
