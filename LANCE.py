from abc import ABC, abstractmethod
from functools import wraps
from time import perf_counter
from langchain_core.callbacks import get_usage_metadata_callback

from settings import *
from environment import *
from model import Model

class ScreeningResult(BaseModel):
    relevant: bool = Field(description="Whether you can contribute to the task.")
    proposal: str = Field(description="Short response message that describes what you can contribute to the task.")

SCREENER_PROMPT = ChatPromptTemplate.from_template(
"""You are an AI agent controlling: {description}
Can you contribute to this request? {request}""")

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
                self.time_log[method.__name__].append(perf_counter() - start)
                self.token_log[method.__name__].extend(list(usage.usage_metadata.values()))
    return wrapper

class UserAgent(ABC):
    def __init__(self, model: Model):
        self.model = model
        self.time_log = {"discovery": [], "plan": [], "control": []}
        self.token_log = {"discovery": [], "plan": [], "control": []}
        self.setup()

    def setup(self):
        pass

    def main(self, environment: Environment, user_utterance: str):
        consequence = {}
        try:
            discovery = self.discovery(environment, user_utterance)
            consequence["discovery"] = list(discovery.keys())
            debug(discovery)

            calls = self.plan(discovery, user_utterance)
            consequence["calls"] = calls
            debug(calls)

            results = self.control(environment, calls)
            consequence["results"] = results
            debug(results)
        except Exception as e:
            consequence["exception"] = str(e)
        return consequence

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
    def setup(self):
        self.planner = CONTROLLER_PROMPT | self.model.with_tools([instruct_agent])
        self.screener = create_generator(SCREENER_PROMPT, ScreeningResult, self.model)
        self.controller = {
            protocol: CONTROLLER_PROMPT | self.model.with_tools([tool])
            for protocol, tool in TOOLS.items()
        }

    def discovery_handler(self, environment, user_utterance):
        descriptions = environment.discovery()
        result = self.screener.batch([
            {"description": description, "request": user_utterance}
            for description in descriptions.values()
        ])
        return {
            agent_id: screen.proposal for agent_id, screen in zip(descriptions.keys(), result) if screen.relevant
        }

    def control_handler(self, environment, call):
        agent = environment.get_agent(call["device_id"])
        result = self.controller[agent.protocol].invoke({"description": agent.description, "request": call["instruction"]})
        return [
            agent.call(**{name: value for name, value in tool_call["args"].items() if name != "device_id"})
            for tool_call in result.tool_calls
        ]
