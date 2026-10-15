from LANCE import *
from langchain_core.documents import Document
from langchain_core.vectorstores import InMemoryVectorStore
from model import LoggedOllamaEmbeddings

class Centralized(UserAgent):
    def setup_handler(self, environment):
        self.planner = CONTROLLER_PROMPT | self.model.with_tools(TOOLS.values())

    def discovery_handler(self, environment, user_utterance):
        return environment.discovery()

    def control_handler(self, environment, call):
        return environment.call(**call)

class RAG(UserAgent):
    def setup_handler(self, environment):
        self.planner = CONTROLLER_PROMPT | self.model.with_tools(TOOLS.values())
        descriptions = environment.discovery()
        self.vector_db = InMemoryVectorStore(LoggedOllamaEmbeddings(model=RAG_EMBEDDING_MODEL, num_ctx=MAX_CONTEXT, token_log=self.token_log))
        self.num_devices = len(descriptions)
        self.vector_db.add_documents([
            Document(page_content=description, metadata={"device_id": device_id})
            for device_id, description in descriptions.items()
        ])

    def discovery_handler(self, environment, user_utterance):
        return {
            document.metadata["device_id"]: document.page_content
            for document, score in self.vector_db.similarity_search_with_score(user_utterance, k=self.num_devices)
            if score >= RAG_SIMILARITY_THRESHOLD
        }

    def control_handler(self, environment, call):
        return environment.call(**call)

class SashaSelection(BaseModel):
    device_ids: List[str] = Field(default_factory=list)

SASHA_FILTER_PROMPT = ChatPromptTemplate.from_template(
"""Select the minimal set of devices needed to fulfill this request: {request}
Available devices: {description}""")

class Sasha(UserAgent):
    def setup_handler(self, environment):
        self.filter = create_generator(SASHA_FILTER_PROMPT, SashaSelection, self.model)
        self.planner = CONTROLLER_PROMPT | self.model.with_tools(TOOLS.values())

    def discovery_handler(self, environment, user_utterance):
        descriptions = environment.discovery()
        selection = self.filter.invoke(
            {"description": descriptions, "request": user_utterance}, 
            config=self.llm_config("discovery")
        )
        return {device_id: descriptions[device_id] for device_id in selection.device_ids if device_id in descriptions}

    def plan_handler(self, descriptions, user_utterance):
        results = self.planner.batch([
            {"description": description, "request": user_utterance}
            for description in descriptions.values()
        ], config=[self.llm_config("plan", device_id) for device_id in descriptions])
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
        result = self.controller[agent.protocol].invoke(
            {"description": agent.description, "request": call["instruction"]},
            config=self.llm_config("control", agent.agent_id)
        )
        return [
            agent.call(**{name: value for name, value in tool_call["args"].items() if name != "device_id"})
            for tool_call in result.tool_calls
        ]
