from abc import ABC, abstractmethod
from functools import wraps
from time import perf_counter

from settings import *
from simulator import *
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

    def main(self, simulator: Simulator, user_utterance: str):
        descriptions = self.discovery(simulator, user_utterance)
        calls = self.plan(descriptions, user_utterance)
        self.control(simulator, calls)

    @timed
    def discovery(self, simulator: Simulator, user_utterance: str):
        return self.discovery_handler(simulator, user_utterance)

    @abstractmethod
    def discovery_handler(self, simulator: Simulator, user_utterance: str) -> Dict[str, str]:
        pass

    @timed
    def plan(self, descriptions: Dict[str, str], user_utterance: str) -> List[dict]:
        return self.controller.invoke({"description": descriptions, "request": user_utterance}).tool_calls
        results = self.controller.batch([
            {"description": description, "request": user_utterance}
            for description in descriptions.values()
        ])
        return sum([inject_id(device_id, result.tool_calls) for device_id, result in zip(descriptions, results)], [])

    @timed
    def control(self, simulator: Simulator, calls: List[dict]):
        return [self.control_handler(simulator, call["args"]) for call in calls]

    @abstractmethod
    def control_handler(self, simulator: Simulator, call: dict):
        pass

class CENTRALIZED(UserAgent):
    def setup(self):
        self.controller = CONTROLLER_PROMPT | self.model.with_tools(TOOLS.values())

    def discovery_handler(self, simulator, user_utterance):
        return simulator.discovery()

    def control_handler(self, simulator, call):
        return simulator.call(**call)

class NATURAL(UserAgent):
    def setup(self):
        self.controller = CONTROLLER_PROMPT | self.model.with_tools([instruct_agent])

    def discovery_handler(self, simulator, user_utterance):
        return simulator.discovery()

    def control_handler(self, simulator, call):
        return simulator.instruct(**call)

class RECRUIT(UserAgent):
    def setup(self):
        self.controller = CONTROLLER_PROMPT | self.model.with_tools(TOOLS.values())

    def discovery_handler(self, simulator, user_utterance):
        return simulator.recruit(user_utterance, structured=True)

    def control_handler(self, simulator, call):
        return simulator.call(**call)

class CONVERSATIONAL(UserAgent):
    def setup(self):
        self.controller = CONTROLLER_PROMPT | self.model.with_tools([instruct_agent])

    def discovery_handler(self, simulator, user_utterance):
        return simulator.recruit(user_utterance, structured=False)

    def control_handler(self, simulator, call):
        return simulator.instruct(**call)
