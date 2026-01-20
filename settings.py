import uuid
import secrets
import asyncio
import re
import os
import subprocess

from dotenv import load_dotenv
load_dotenv()

# Settings

VLLM_URL = "http://localhost:8000/v1"

DATASET_PATH = "dataset/dataset_synthetic.csv"
SURVEY_PATH = "dataset/survey_result.csv"
RESULT_PATH = "results/{code}"

SIMULATION_CONCURRENCY_GPU_MAX = 50
SIMULATION_CONCURRENCY_DELAY = 7
EVALUATION_CONCURRENCY_MAX = 10
SYNTHESIZE_EXPECTATION_RETRY = 3
TIMEOUT_LIMIT = None
TICK = 0.1

ALLOWED_MODES = ["CENTRALIZED", "NATURAL", "RECRUIT", "CONVERSATIONAL"]

# LLM

MAX_OUTPUT_TOKENS = 2048
MAX_MODEL_LEN = 4096
GPU_MEMORY_UTILIZATION = 0.8
DB_PATH = "dataset/db"
MATTER_CLUSTERS_PATH = f"{DB_PATH}/matter_clusters.json"
MATTER_DEVICE_TYPES_PATH = f"{DB_PATH}/matter_device_types.json"

# RECRUIT

RECRUIT_SCREENING_THRESHOLD = 0.3
RECRUIT_TIME_TO_WAIT = 20

# MQTT

MQTT_RECONNECT_DELAY = 1
MQTT_BROKER_ADDRESS = "localhost"
MQTT_TOPIC_ALIVE = "alive"
MQTT_TOPIC_RESET = "reset"
MQTT_TOPIC_RESPONSE = "response"
# mode RECRUIT topics
MQTT_TOPIC_RECRUIT_CALL = "call"
MQTT_TOPIC_RECRUIT_TEAM = "team"
# mode NATURAL topics
MQTT_TOPIC_NATURAL_CONTROL = "natural"
# mode CENTRALIZED topics
MQTT_TOPIC_STRUCTURED_CONTROL = "structured"
MQTT_TOPIC_CENTRALIZED_DISCOVERY = "discovery"
MQTT_TOPIC_CENTRALIZED_REGISTER = "register"
# mode CLOUD topics
# mode ONTOLOGY topics

# Devices

SMARTTHINGS_API_URL = "https://api.smartthings.com/v1/devices"

# User

COORDINATOR_PROMPT = """
You are a coordinator who can control devices in the descriptions by using the given tool.
Instruct each agent or control each device by using the given tool to accomplish the user's message.

[User Message]
{user_message}

[Descriptions]
{descriptions}
"""

# Agents

SCREENER_PROMPT = """
You are an AI agent that controls the following device.

[Device Description]
{description}

Answer the recruiting message with how well you can contribute to the task.

[Message]
{message}

[Format]
{format}
"""

CONTROLLER_PROMPT = """
You are an AI agent that controls the following device.

[Device Description]
{description}

Control the device according to the given message.

[Message]
{message}
"""

# EVALUATION

EVALUATOR_PROMPT = """
Evaluate the behavior of the agents in the conversation whether the user's task is accomplished or not.

[Device Descriptions]
{device_descriptions}

[User Message]
{user_message}

[Evaluation Criteria]
{evaluation_criteria}

[Conversation]
{conversation}

[Format]
{format}
"""

from pydantic import BaseModel, Field
class Response(BaseModel):
    agent_id: str
    request: dict
    success: bool
    message: str

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
    return f"{name}_{model}_{mode}"

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

def parse_column(df, value=""):
    pattern = r"^(?P<value>.*?)_(?P<model_name>.*)_(?P<method>.*?)$"
    matches = []
    for column in df.columns.tolist():
        match = re.match(pattern, column)
        if match and value in match.group():
            matches.append(match.group())
    return matches

def get_last_result():
    for code in reversed(os.listdir(RESULT_PATH.split("/")[0])):
        if os.path.exists(f"{RESULT_PATH.format(code=code)}/result.csv"):
            return code
    return ""

def get_gpu_utilization():
    try:
        result = subprocess.run(['nvidia-smi', '--query-gpu=utilization.gpu', '--format=csv,noheader,nounits'], capture_output=True, text=True)
        return int(result.stdout.strip().split('\n')[0])
    except:
        return 0
    
def moving_average(l: list, window: int):
    while len(l) > window:
        l.pop(0)
    return sum(l) / len(l)
