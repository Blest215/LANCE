from LANCE import *

class CENTRALIZED(UserAgent):
    def setup_handler(self, environment):
        self.planner = CONTROLLER_PROMPT | self.model.with_tools(TOOLS.values())

    def discovery_handler(self, environment, user_utterance):
        return environment.discovery()

    def control_handler(self, environment, call):
        return environment.call(**call)

class RAG(UserAgent):
    pass

class Sasha(UserAgent):
    def setup_handler(self, environment):
        self.planner = CONTROLLER_PROMPT | self.model.with_tools(TOOLS.values())

    def discovery_handler(self, environment, user_utterance):
        return environment.discovery()

    def plan_handler(self, descriptions, user_utterance):
        results = self.planner.batch([
            {"description": description, "request": user_utterance}
            for description in descriptions.values()
        ])
        tool_calls = []
        for device_id, result in zip(descriptions.keys(), results):
            for tool_call in result.tool_calls:
                tool_call["args"]["device_id"] = device_id
                tool_calls.append(tool_call)
        return tool_calls

    def control_handler(self, environment, call):
        return environment.call(**call)

class LLMind(UserAgent):
    def setup_handler(self, environment):
        self.planner = CONTROLLER_PROMPT | self.model.with_tools([instruct_agent])
        self.controller = {
            protocol: CONTROLLER_PROMPT | self.model.with_tools([tool])
            for protocol, tool in TOOLS.items()
        }

    def discovery_handler(self, environment, user_utterance):
        return environment.discovery()

    def control_handler(self, environment, call):
        agent = environment.get_agent(call["device_id"])
        result = self.controller[agent.protocol].invoke({"description": agent.description, "request": call["instruction"]})
        return [
            agent.call(**{name: value for name, value in tool_call["args"].items() if name != "device_id"})
            for tool_call in result.tool_calls
        ]
