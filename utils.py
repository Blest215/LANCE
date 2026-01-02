import sys
import asyncio
import uuid
import secrets
import requests
import os

import docker
from docker.types import DeviceRequest

from langchain_openai import ChatOpenAI

from settings import *

from typing import Annotated
from typing_extensions import TypedDict
class AgentState(TypedDict):
    messages: Annotated[list, lambda x, y: x + y]

class Model:
    def __init__(self, model, options="", temperature=0.8, reasoning_effort=None, base_url=BASE_URL):
        self.model = model
        self.options = options
        self.temperature = temperature
        self.reasoning_effort = reasoning_effort
        self.base_url = base_url

    def __getitem__(self, key):
        return self.__dict__[key]

    def to_dict(self):
        return {"model": self.model, "temperature": self.temperature, "reasoning_effort": self.reasoning_effort, "base_url": self.base_url}

def get_random_device_id():
    return str(uuid.uuid4())

def get_random_team_id():
    return secrets.token_hex(8)

def get_random_request_id():
    return uuid.uuid4().hex

def get_random_session():
    return secrets.token_hex(16)

def check_topic(formatted, unformatted):
    return formatted == unformatted.split("/")[0]

def smartthings_request(id, args):
    try:
        return requests.post(
            f"{SMARTTHINGS_API_URL}/{id}/commands", 
            headers={"Authorization": f"Bearer {os.getenv('SMARTTHINGS_API_KEY')}", "Accept": "application/json"}, 
            json={
                "commands": [
                    {"component": "main", "capability": args["capability"], "command": args["command"], "arguments": args.get("arguments", [])}
                ]
            }
        ).json()
    except requests.exceptions.JSONDecodeError as e:
        # TODO
        return {}

async def startup_vllm_container(model: Model):
    print("Startup vLLM container", end="")
    docker_client = docker.from_env()
    container = docker_client.containers.run(
        name=model['model'].split("/")[-1],
        image="vllm/vllm-openai:latest",
        command=f"{model['model']} {model['options']}",
        ports={"8000/tcp": "8000"},
        environment={"TZ": "Asia/Seoul"},
        device_requests=[DeviceRequest(device_ids=["all"], capabilities=[["gpu"]])],
        volumes=["~/.cache/huggingface:/root/.cache/huggingface"],
        ipc_mode="host",
        detach=True,
    )
    test_brain = ChatOpenAI(**model.to_dict())
    while True:
        print(".", end="")
        sys.stdout.flush()
        try:
            test_brain.invoke("are you alive?")
            break
        except Exception:
            await asyncio.sleep(1)
    print("complete")
    return container