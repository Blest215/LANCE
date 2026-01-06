import uuid
import secrets
import asyncio

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
    return f"{name}_{model}_{mode}".replace("-", "_").replace(".", "_").replace(":", "_")

async def save_dataframe(df, path, ensure=False):
    while True:
        try:
            df.to_csv(path, index=False, encoding="utf-8-sig")
            break
        except PermissionError:
            if ensure:
                await asyncio.sleep(1)
            else:
                break

def batch_dataframe(df, batch_size):
    return [df.iloc[i * batch_size:(i + 1) * batch_size] for i in range(len(df) // batch_size + (1 if len(df) % batch_size else 0))]
