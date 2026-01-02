import sys
import time

import docker
from docker.types import DeviceRequest

from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI

from settings import BASE_URL

class Model:
    def __init__(self, model, backend="openai", options="", temperature=0.8, reasoning=None):
        assert backend in ["ollama", "openai"]
        self.model = model
        self.backend = backend
        self.options = options
        self.temperature = temperature
        self.reasoning = reasoning

    @property
    def name(self):
        return self.model.split("/")[-1]

    def __getitem__(self, key):
        return self.__dict__[key]

    def instantiate(self):
        if self.backend == "ollama":
            return ChatOllama(model=self.model, temperature=self.temperature, reasoning=self.reasoning)
        return ChatOpenAI(model=self.model, temperature=self.temperature, reasoning_effort=self.reasoning, base_url=BASE_URL)

    def wrapup(self):
        docker_client = docker.from_env()
        for container in docker_client.containers.list(all=True):
            if container.name == self.name:
                container.stop()
                container.remove()
                return

    def setup(self):
        if self.backend == "ollama":
            return

        print("Startup vLLM container", end="")

        self.wrapup()

        docker_client = docker.from_env()
        docker_client.volumes.create("models")
        container = docker_client.containers.run(
            name=self.name,
            image="vllm/vllm-openai:latest",
            command=f"{self.model} --max-model-len 4096 {self.options} ",
            ports={"8000/tcp": "8000"},
            environment={"TZ": "Asia/Seoul"},
            device_requests=[DeviceRequest(device_ids=["all"], capabilities=[["gpu"]])],
            volumes=["models:/root/.cache/huggingface"],
            ipc_mode="host",
            detach=True,
        )

        test_brain = self.instantiate()
        while True:
            print(".", end="")
            sys.stdout.flush()
            try:
                container = docker_client.containers.get(container.id)
                test_brain.invoke("are you alive?")
                break
            except Exception:
                if container.status == "exited":
                    raise Exception
                time.sleep(1)
        print("complete")