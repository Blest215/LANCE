import subprocess
from contextlib import contextmanager
from time import perf_counter
from uuid import uuid4

from langchain_core.callbacks import BaseCallbackHandler
from langchain_ollama import ChatOllama, OllamaEmbeddings

from settings import *

@contextmanager
def record_call(token_log, stage, model, kind, device_id=None, **details):
    started = perf_counter()
    record = dict(call_id=str(uuid4()), stage=stage, model=model, kind=kind, device_id=device_id,
                  input_tokens=0, output_tokens=0, total_tokens=0, status="running", **details)
    token_log.setdefault(stage, []).append(record)
    try:
        yield record
        record["status"] = "success"
    except BaseException as error:
        record.update(status="error", error=str(error))
        raise
    finally:
        record["elapsed"] = perf_counter() - started

class CallLogger(BaseCallbackHandler):
    def __init__(self, records, stage, model, device_id=None):
        self.records = records
        self.details = dict(stage=stage, model=model, kind="llm", device_id=device_id,
                            input_tokens=0, output_tokens=0, total_tokens=0)

    def on_chat_model_start(self, serialized, messages, *, run_id, metadata=None, **kwargs):
        self.started = perf_counter()
        self.record = self.details | dict(call_id=str(run_id), elapsed=None, status="running")
        self.record["model"] = (metadata or {}).get("ls_model_name") or self.record["model"]
        self.records.append(self.record)

    def on_llm_end(self, response, **kwargs):
        self.record.update(response.generations[0][0].message.usage_metadata or {})
        self.record.update(elapsed=perf_counter() - self.started, status="success")

    def on_llm_error(self, error, **kwargs):
        self.record.update(elapsed=perf_counter() - self.started, status="error", error=str(error))

class LoggedOllamaEmbeddings(OllamaEmbeddings):
    token_log: Any = Field(exclude=True)

    def _embed(self, texts, stage):
        with record_call(self.token_log, stage, self.model, "embedding", batch_size=len(texts)) as record:
            response = self._client.embed(self.model, texts, dimensions=self.dimensions,
                                          options=self._default_params, keep_alive=self.keep_alive)
            record.update(input_tokens=response.prompt_eval_count, output_tokens=0, total_tokens=response.prompt_eval_count)
            return response["embeddings"]

    def embed_documents(self, texts):
        return self._embed(texts, "setup")

    def embed_query(self, text):
        return self._embed([text], "discovery")[0]

class Model:
    def __init__(self, model: str, temperature=0.0, reasoning=None, context=MAX_CONTEXT, max_output_tokens=MAX_OUTPUT_TOKENS):
        self.model = model
        self.temperature = temperature
        self.reasoning = reasoning
        self.context = context
        self.max_output_tokens = max_output_tokens
        
        self.name = model.split("/")[-1] + ("_reasoning" if self.reasoning else "")

        self.instance = None

    def __str__(self):
        return self.name.replace("-", "_").replace(".", "_").replace(":", "_")
    
    def instantiate(self):
        if not self.instance:
            self.instance = ChatOllama(model=self.model, temperature=self.temperature, reasoning=self.reasoning, num_ctx=self.context, num_predict=self.max_output_tokens, validate_model_on_init=True, keep_alive="1h")
        return self.instance
    
    def with_tools(self, tools: list):
        return self.instantiate().bind_tools(tools)
    
    def with_structured_output(self, pydantic_object: BaseModel):
        return self.instantiate().with_structured_output(pydantic_object)

    def decide(self, state: str | dict[str, Any] | list[Any], question: dict[str, Any],
               token_log: dict[str, list[dict[str, Any]]], stage: str,
               device_id: str | None = None) -> dict[str, Any]:
        base_url = os.getenv("OLLAMA_HOST", "http://localhost:11434").rstrip("/")
        with record_call(token_log, stage, self.model, "decision", device_id) as record:
            response = requests.post(f"{base_url}/v1/systemone", json={
                "model": self.model, "state": state, "questions": {"decision": question}, "keep_alive": "1h",
            })
            response.raise_for_status()
            result = response.json()
            record["question_type"] = question["type"]
            record["question"] = question["instructions"]
            if "criteria" in question:
                record["criteria"] = question["criteria"]
            record["answer"] = result.get("answers", {}).get("decision")
            usage = result.get("usage", {})
            record["input_tokens"] = usage.get("input_tokens", 0)
            record["output_tokens"] = usage.get("output_tokens", 0)
            record["total_tokens"] = record["input_tokens"] + record["output_tokens"]
            return result
    
    def setup(self) -> bool:
        try:
            return self.instantiate().invoke("Hello, are you alive?").response_metadata["done"]
        except Exception:
            return False
    
    def wrapup(self):
        subprocess.run(['ollama', 'stop', self.model], check=False)
        self.instance = None

    def copy(self):
        return Model(self.model, self.temperature, self.reasoning, self.context, self.max_output_tokens)
