import uuid
import secrets
import asyncio
import re
import os

from dotenv import load_dotenv
load_dotenv()

# Settings

VLLM_URL = "http://localhost:8000/v1"

DATASET_PATH = "dataset/dataset_synthetic.csv"
SURVEY_PATH = "dataset/survey_result.csv"
RESULT_PATH = "results/{now}"

SIMULATION_CONCURRENCY_MAX = 5
SIMULATION_CONCURRENCY_DELAY = 10 * SIMULATION_CONCURRENCY_MAX
EVALUATION_CONCURRENCY_MAX = 10
SYNTHESIZE_CONCURRENCY_MAX = 5
TIMEOUT_LIMIT = 5
TICK = 0.1

ALLOWED_MODES = ["LANCE", "NATURAL", "CENTRALIZED", "ONTOLOGY"]

# LLM

MAX_OUTPUT_TOKENS = 1024
MAX_MODEL_LEN = 4096
GPU_MEMORY_UTILIZATION = 0.8
DB_PATH = "dataset/db"
CLUSTERS_PATH = f"{DB_PATH}/matter_clusters.json"
DEVICE_TYPES_PATH = f"{DB_PATH}/matter_device_types.json"

# LANCE

SCREENING_THRESHOLD = 0.3

# MQTT

MQTT_BROKER_ADDRESS = "localhost"
MQTT_TOPIC_ALIVE = "alive"
MQTT_TOPIC_RESPONSE = "response"
# mode LANCE topics
MQTT_TOPIC_LANCE_CALL = "call"
MQTT_TOPIC_LANCE_TEAM = "team"
# mode NATURAL topics
MQTT_TOPIC_NATURAL_AGENT = "agent"
# mode CENTRALIZED topics
MQTT_TOPIC_CENTRALIZED_DISCOVERY = "discovery"
MQTT_TOPIC_CENTRALIZED_REGISTER = "register"
MQTT_TOPIC_CENTRALIZED_CONTROL = "control"
# mode CLOUD topics
# mode ONTOLOGY topics

# Devices

SMARTTHINGS_API_URL = "https://api.smartthings.com/v1/devices"

# User agent

ORGANIZER_PROMPT = """
You are an AI assistant that helps users to accomplish their tasks by coordinating other agents.
Ask other agents to contribute to the user's task.

[User Command]
{user_command}
"""

COORDINATOR_PROMPT = """
You are an AI assistant that organizes other agents to accomplish a user's task.

[User Command]
{user_command}

[Team Messages]
{team_messages}
"""

MASTERMIND_PROMPT = """
You are an AI assistant that controls devices to accomplish a user's task.

[Rules]
- You MUST select the appropriate tool to control a device, according to the description format.

[User Command]
{user_command}

[Device Descriptions]
{device_descriptions}
"""

# LANCE agents

SCREENER_PROMPT = """
You are an AI assistant that controls the following device.

[Device Description]
{device_description}

Judge how well you can contribute to the given task.

[Message]
{message}

[Format]
{format}
"""

CONTROLLER_PROMPT = """
You are an AI assistant that controls the following device.

[Device Description]
{device_description}

Control the device based on the given message.

[Message]
{message}
"""

# EVALUATION

EVALUATOR_PROMPT = """
Evaluate the behavior of the agents in the conversation whether the user's task is accomplished or not.

[Time]
{time}

[Device Descriptions]
{device_descriptions}

[User Command]
{user_command}

[Evaluation Criteria]
{evaluation_criteria}

[Conversation]
{conversation}

[Format]
{format}
"""


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

def parse_column(df, value=""):
    pattern = r"^(?P<value>.*?)_(?P<model_name>.*)_(?P<method>.*?)$"
    matches = []
    for column in df.columns.tolist():
        match = re.match(pattern, column)
        if match and value in match.group():
            matches.append(match.group())
    return matches

def get_last_result():
    for now in reversed(os.listdir(RESULT_PATH.split("/")[0])):
        if os.path.exists(f"{RESULT_PATH.format(now=now)}/result.csv"):
            return now
    return ""
