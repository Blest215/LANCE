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

def check_topic(formatted, unformatted):
    return formatted.split("/")[0] == unformatted.split("/")[0]

def smartthings_request(id, args):
    return requests.post(
        f"{SMARTTHINGS_API_URL}/{id}/commands", 
        headers={"Authorization": f"Bearer {os.getenv('SMARTTHINGS_API_KEY')}", "Accept": "application/json"}, 
        json={
            "commands": [
                {"component": "main", "capability": args["capability"], "command": args["command"], "arguments": args.get("arguments", [])}
            ]
        }
    ).json()
