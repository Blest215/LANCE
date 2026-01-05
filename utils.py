import uuid
import secrets
import requests
import os

from settings import *

from typing import Annotated
from typing_extensions import TypedDict
class AgentState(TypedDict):
    messages: Annotated[list, lambda x, y: x + y]

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

def get_agent_id(device_description):
    if isinstance(device_description, dict):
        if "id" in device_description:
            return device_description["id"]
        if "deviceId" in device_description:
            return device_description["deviceId"]
    return get_random_device_id()

def get_column_name(name, model, mode):
    return f"{name}_{model}_{mode}".replace("-", "_").replace(".", "_")
