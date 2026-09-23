from abc import ABC, abstractmethod

from settings import *
from simulator import *
from model import Model

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

    def discovery(self, simulator: Simulator, user_utterance: str):
        start = time.time()
        result = self.discovery_handler(simulator, user_utterance)
        self.time_log["discovery"].append(time.time() - start)
        return "\n".join(result)

    @abstractmethod
    def discovery_handler(self, simulator: Simulator, user_utterance: str) -> List[str]:
        pass

    def plan(self, descriptions: str, user_utterance: str):
        start = time.time()
        result = self.plan_handler(descriptions, user_utterance)
        self.time_log["plan"].append(time.time() - start)
        return result

    @abstractmethod
    def plan_handler(self, descriptions: str, user_utterance: str):
        pass

    def control(self, simulator: Simulator, calls):
        start = time.time()
        result = self.control_handler(simulator, calls)
        self.time_log["control"].append(time.time() - start)
        return result

    @abstractmethod
    def control_handler(self, simulator: Simulator, calls):
        pass


class CENTRALIZED(UserAgent):
    def setup(self):
        self.controller = CONTROLLER_PROMPT | self.model.with_tools([call_device_api])

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
        self.controller = CONTROLLER_PROMPT | self.model.with_tools([call_device_api])

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