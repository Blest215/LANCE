from abc import ABC, abstractmethod
from functools import wraps
from time import perf_counter

from settings import *
from environment import *
from model import Model

def timed(method):
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        start = perf_counter()
        try:
            return method(self, *args, **kwargs)
        finally:
            self.time_log[method.__name__].append(perf_counter() - start)
    return wrapper

class UserAgent(ABC):
    def __init__(self, model: Model):
        self.model = model
        self.time_log = {"discovery": [], "plan": [], "control": []}
        self.setup()

    def setup(self):
        pass

    def main(self, environment: Environment, user_utterance: str):
        descriptions = self.discovery(environment, user_utterance)
        calls = self.plan(descriptions, user_utterance)
        self.control(environment, calls)

    @timed
    def discovery(self, environment: Environment, user_utterance: str):
        return self.discovery_handler(environment, user_utterance)

    @abstractmethod
    def discovery_handler(self, environment: Environment, user_utterance: str) -> Dict[str, str]:
        pass

    @timed
    def plan(self, descriptions: Dict[str, str], user_utterance: str):
        return self.plan_handler(descriptions, user_utterance)

    def plan_handler(self, descriptions: Dict[str, str], user_utterance: str) -> List[dict]:
        return self.controller.invoke({"description": descriptions, "request": user_utterance}).tool_calls
        results = self.controller.batch([
            {"description": description, "request": user_utterance}
            for description in descriptions.values()
        ])
        return sum([inject_id(device_id, result.tool_calls) for device_id, result in zip(descriptions, results)], [])

    @timed
    def control(self, environment: Environment, calls: List[dict]):
        return [self.control_handler(environment, call["args"]) for call in calls]

    @abstractmethod
    def control_handler(self, environment: Environment, call: dict):
        pass

class CENTRALIZED(UserAgent):
    def setup(self):
        self.controller = CONTROLLER_PROMPT | self.model.with_tools(TOOLS.values())

    def discovery_handler(self, environment, user_utterance):
        return environment.discovery()

    def control_handler(self, environment, call):
        return environment.call(**call)

class NATURAL(UserAgent):
    def setup(self):
        self.controller = CONTROLLER_PROMPT | self.model.with_tools([instruct_agent])

    def discovery_handler(self, environment, user_utterance):
        return environment.discovery()

    def control_handler(self, environment, call):
        return environment.instruct(**call)

class RECRUIT(UserAgent):
    def setup(self):
        self.controller = CONTROLLER_PROMPT | self.model.with_tools(TOOLS.values())

    def discovery_handler(self, environment, user_utterance):
        return environment.recruit(user_utterance, structured=True)

    def control_handler(self, environment, call):
        return environment.call(**call)

class CONVERSATIONAL(UserAgent):
    def setup(self):
        self.controller = CONTROLLER_PROMPT | self.model.with_tools([instruct_agent])

    def discovery_handler(self, environment, user_utterance):
        return environment.recruit(user_utterance, structured=False)

    def control_handler(self, environment, call):
        return environment.instruct(**call)
