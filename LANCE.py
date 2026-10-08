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
        calls = self.plan(descriptions, user_utterance).tool_calls
        self.control(simulator, calls)

    @timed
    def discovery(self, simulator: Simulator, user_utterance: str):
        return "\n".join(self.discovery_handler(simulator, user_utterance))

    @abstractmethod
    def discovery_handler(self, simulator: Simulator, user_utterance: str) -> List[str]:
        pass

    @timed
    def plan(self, descriptions: str, user_utterance: str):
        return self.plan_handler(descriptions, user_utterance)

    @abstractmethod
    def plan_handler(self, descriptions: str, user_utterance: str):
        pass

    @timed
    def control(self, simulator: Simulator, calls):
        return self.control_handler(simulator, calls)

    @abstractmethod
    def control_handler(self, simulator: Simulator, calls: List[dict]):
        pass


class CENTRALIZED(UserAgent):
    def setup(self):
        self.controller = CONTROLLER_PROMPT | self.model.with_tools([call_device_matter, call_device_w3c, call_device_smartthings])

    def discovery_handler(self, simulator, user_utterance):
        return simulator.discovery()

    def plan_handler(self, descriptions, user_utterance):
        return self.controller.invoke({"description": descriptions, "request": user_utterance})

    def control_handler(self, simulator, calls):
        return [simulator.call(**call["args"]) for call in calls]

class NATURAL(UserAgent):
    def setup(self):
        self.controller = CONTROLLER_PROMPT | self.model.with_tools([instruct_agent])

    def discovery_handler(self, simulator, user_utterance):
        return simulator.discovery()

    def plan_handler(self, descriptions, user_utterance):
        return self.controller.invoke({"description": descriptions, "request": user_utterance})

    def control_handler(self, simulator, calls):
        return [simulator.instruct(**call["args"]) for call in calls]


class RECRUIT(UserAgent):
    def setup(self):
        self.controller = CONTROLLER_PROMPT | self.model.with_tools([call_device_matter, call_device_w3c, call_device_smartthings])

    def discovery_handler(self, simulator, user_utterance):
        return simulator.recruit(user_utterance, structured=True)

    def plan_handler(self, descriptions, user_utterance):
        return self.controller.invoke({"description": descriptions, "request": user_utterance})

    def control_handler(self, simulator, calls):
        return [simulator.call(**call["args"]) for call in calls]

class CONVERSATIONAL(UserAgent):
    def setup(self):
        self.controller = CONTROLLER_PROMPT | self.model.with_tools([instruct_agent])

    def discovery_handler(self, simulator, user_utterance):
        return simulator.recruit(user_utterance, structured=False)

    def plan_handler(self, descriptions, user_utterance):
        return self.controller.invoke({"description": descriptions, "request": user_utterance})

    def control_handler(self, simulator, calls):
        return [simulator.instruct(**(call["args"])) for call in calls]
