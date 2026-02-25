import sys
import time
import os

import docker
from docker.types import DeviceRequest

from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI

from settings import *

class Model:
    def __init__(self, model, backend="ollama", options="", temperature=0.0, reasoning=None, base_url=None, context=MAX_CONTEXT, max_output_tokens=MAX_OUTPUT_TOKENS, **kwargs):
        assert backend in ["ollama", "vllm"]
        self.model = model
        self.backend = backend
        self.options = options
        self.temperature = temperature
        self.reasoning = reasoning
        self.base_url = f"http://{base_url}:11434" if base_url is not None else None
        self.context = context
        self.max_output_tokens = max_output_tokens
        self.kwargs = kwargs

        if self.backend == "ollama":
            self.instance = ChatOllama(model=self.model, temperature=self.temperature, reasoning=self.reasoning, base_url=self.base_url if self.base_url else None, num_ctx=self.context, num_predict=self.max_output_tokens, validate_model_on_init=True, keep_alive="1h", **self.kwargs)
        else:
            self.instance = ChatOpenAI(model=self.model, temperature=self.temperature, reasoning_effort=self.reasoning, base_url=self.base_url if self.base_url else VLLM_URL, max_completion_tokens=self.max_output_tokens, **self.kwargs)

    def __str__(self):
        return f"{self.name}".replace("-", "_").replace(".", "_").replace(":", "_")

    @property
    def name(self):
        return self.model.split("/")[-1] + ("_reasoning" if self.reasoning else "")

    def __getitem__(self, key):
        return self.__dict__[key]

    def instantiate(self):
        return self.instance
    
    def with_tools(self, tools: list):
        return self.instantiate().bind_tools(tools)

    def get_container(self):
        docker_client = docker.from_env()
        for container in docker_client.containers.list(all=True):
            if container.name == self.name:
                return container

    def wrapup(self):
        if self.backend == "ollama":
            subprocess.run(['ollama', 'stop', self.model])
        elif self.backend == "vllm":
            container = self.get_container()
            if container:
                container.stop()

    def setup(self) -> bool:
        if self.backend == "ollama":
            try:
                return self.instance.invoke("Hello, are you alive?").response_metadata["done"]
            except Exception:
                return False

        print(f"Startup vLLM container for {self.name}", end="")

        docker_client = docker.from_env()
        container = self.get_container()
        if not container:
            docker_client.volumes.create("models")
            container = docker_client.containers.run(
                name=self.name,
                image="vllm/vllm-openai:latest",
                command=f"{self.model} --max-model-len {self.context} --gpu-memory-utilization {GPU_MEMORY_UTILIZATION} {self.options} ",
                ports={"8000/tcp": "8000"},
                environment={"TZ": "Asia/Seoul", "HF_TOKEN": os.getenv("HF_TOKEN")},
                device_requests=[DeviceRequest(device_ids=["all"], capabilities=[["gpu"]])],
                volumes=["models:/root/.cache/huggingface"],
                ipc_mode="host",
                detach=True,
            )
        container.start()

        test_brain = self.instantiate()
        while True:
            print(".", end="")
            sys.stdout.flush()
            try:
                test_brain.invoke("are you alive?")
                break
            except Exception:
                if docker_client.containers.get(container.id).status == "exited":
                    print("fail")
                    return False
                time.sleep(1)
        print("complete")
        return True
