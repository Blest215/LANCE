import subprocess

from langchain_ollama import ChatOllama

from settings import *

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
