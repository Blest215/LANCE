from LANCE import *
from langchain_core.documents import Document
from langchain_core.vectorstores import InMemoryVectorStore
from model import LoggedOllamaEmbeddings

class Centralized(UserAgent):
    def setup_handler(self, environment):
        self.composer = CONTROLLER_PROMPT | self.model.with_tools(TOOLS.values())

    def discovery_handler(self, environment, user_utterance):
        return environment.discovery()

    def orchestration_handler(self, agent, call):
        return agent.call(**call)

class RAG(UserAgent):
    def setup_handler(self, environment):
        self.composer = CONTROLLER_PROMPT | self.model.with_tools(TOOLS.values())
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

    def orchestration_handler(self, agent, call):
        return agent.call(**call)

class SashaSelection(BaseModel):
    device_ids: List[str] = Field(default_factory=list)

SASHA_FILTER_PROMPT = ChatPromptTemplate.from_template(
"""Select the minimal set of devices needed to fulfill this request: {request}
Available devices: {description}""")

class Sasha(UserAgent):
    def setup_handler(self, environment):
        self.filter = create_generator(SASHA_FILTER_PROMPT, SashaSelection, self.model)
        self.composer = CONTROLLER_PROMPT | self.model.with_tools(TOOLS.values())

    def discovery_handler(self, environment, user_utterance):
        descriptions = environment.discovery()
        selection = self.filter.invoke(
            {"description": descriptions, "request": user_utterance}, 
            config=self.llm_config("discovery")
        )
        return {device_id: descriptions[device_id] for device_id in selection.device_ids if device_id in descriptions}

    def composition_handler(self, descriptions, user_utterance):
        results = []
        for device_id, description in descriptions.items():
            results.append(self.composer.invoke(
                {"description": description, "request": user_utterance},
                config=self.llm_config("composition", device_id),
            ))
        tool_calls = []
        for device_id, result in zip(descriptions.keys(), results):
            for tool_call in result.tool_calls:
                tool_call["args"]["device_id"] = device_id
                tool_calls.append(tool_call)
        return tool_calls

    def orchestration_handler(self, agent, call):
        return agent.call(**call)

class LLMind(UserAgent):
    def setup_handler(self, environment):
        self.composer = CONTROLLER_PROMPT | self.model.with_tools([instruct_agent])
        self.orchestrators = {
            protocol: CONTROLLER_PROMPT | self.model.with_tools([tool])
            for protocol, tool in TOOLS.items()
        }

    def discovery_handler(self, environment, user_utterance):
        return environment.discovery()

    def orchestration_handler(self, agent, call):
        result = self.orchestrators[agent.protocol].invoke(
            {"description": agent.description, "request": call["instruction"]},
            config=self.llm_config("orchestration", agent.agent_id)
        )
        return [
            agent.call(**{name: value for name, value in tool_call["args"].items() if name != "device_id"})
            for tool_call in result.tool_calls
        ]
