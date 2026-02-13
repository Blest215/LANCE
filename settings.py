import uuid
import secrets
import asyncio
import re
import os
import subprocess
import json

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from dotenv import load_dotenv
load_dotenv()

# Settings

DATASET_FILENAME_PATTERN = r'^dataset_D(\d+)_M(\d+)\.csv$' 
RESULT_FILENAME_PATTERN = r'^result_D(\d+)_M(\d+)\.csv$'

VLLM_URL = "http://localhost:8000/v1"

DATASET_DIR = "dataset"
DB_PATH = f"{DATASET_DIR}/db"
RESULT_DIR = "results"
SURVEY_PATH = f"{DB_PATH}/survey_result.csv"
MATTER_CLUSTERS_PATH = f"{DB_PATH}/matter_clusters.json"
MATTER_DEVICE_TYPES_PATH = f"{DB_PATH}/matter_device_types.json"
SETTING_PATH = RESULT_DIR + "/{code}/settings.txt"

SYNTHESIZE_RETRY = 3
TIMEOUT_LIMIT = 600
TICK = 0.1

REGISTRY_ID = "REGISTRY"

ALLOWED_MODES = ["CENTRALIZED", "NATURAL", "RECRUIT", "CONVERSATIONAL"]

DEBUG = False

# LLM

MAX_OUTPUT_TOKENS = 2048
MAX_MODEL_LEN = 4096
GPU_MEMORY_UTILIZATION = 0.8

# RECRUIT

RECRUIT_SCREENING_THRESHOLD = 0.3

# MQTT

MQTT_RECONNECT_DELAY = 1
MQTT_BROKER_ADDRESS = "localhost"
MQTT_TOPIC_RESET = "reset"
MQTT_TOPIC_RESPONSE = "response"
# mode CONVERSATIONAL topics
MQTT_TOPIC_CONVERSATIONAL_CALL = "call"
# mode RECRUIT topics
MQTT_TOPIC_RECRUIT_CALL = "recruit"
# mode NATURAL topics
MQTT_TOPIC_NATURAL_CONTROL = "natural"
# mode CENTRALIZED topics (BASELINE)
MQTT_TOPIC_STRUCTURED_CONTROL = "structured"
MQTT_TOPIC_CENTRALIZED_DISCOVERY = "discovery"
MQTT_TOPIC_CENTRALIZED_REGISTER = "register"
# mode CLOUD topics
# mode ONTOLOGY topics

# Devices

DEVICE_FORMATS = ["W3C", "SmartThings", "Matter"]

SMARTTHINGS_API_URL = "https://api.smartthings.com/v1/devices"

# User

COORDINATOR_PROMPT = ChatPromptTemplate.from_messages([
    ("system", "You are an orchestrator who controls multiple devices to accomplish a user's task."),
    ("system", "[Available Devices]\n{descriptions}"),
    ("system", "(1) Analyze the user task and identify relevant devices."),
    ("system", "(2) Control each relevant device using the appropriate tool."),
    ("user", "{user_message}"),
])

# Agents

SCREENER_PROMPT = ChatPromptTemplate.from_messages([
    ("system", "You are a screener who determines if this device can contribute to completing the following task based on the following specification."),
    ("system", "[Device Specification]\n{description}"),
    ("system", "[Format]\n{format}"),
    ("system", "Can you contribute to the following user message?"),
    ("user", "{message}"),
])

CONTROLLER_PROMPT = ChatPromptTemplate.from_messages([
    ("system", "You are an orchestrator who controls this device to accomplish a user's task based on the following specification."),
    ("system", "[Device Specification]\n{description}"),
    ("system", "Control the device according to its specification using the appropriate tool."),
    ("user", "{message}"),
])

from pydantic import BaseModel, Field
class Response(BaseModel):
    agent_id: str
    request: dict
    success: bool
    message: str

def save_settings(code):
    with open(SETTING_PATH.format(code=code), "w") as f:
        f.write(json.dumps({
            "COORDINATOR_PROMPT": [str(message) for message in COORDINATOR_PROMPT.messages],
            "SCREENER_PROMPT": [str(message) for message in SCREENER_PROMPT.messages],
            "CONTROLLER_PROMPT": [str(message) for message in CONTROLLER_PROMPT.messages],
            "RECRUIT_SCREENING_THRESHOLD": RECRUIT_SCREENING_THRESHOLD,
            "MAX_OUTPUT_TOKENS": MAX_OUTPUT_TOKENS,
            "MAX_MODEL_LEN": MAX_MODEL_LEN,
            "GPU_MEMORY_UTILIZATION": GPU_MEMORY_UTILIZATION,
        }, indent=4))

def get_random_device_id():
    return str(uuid.uuid4())

def get_random_request_id():
    return uuid.uuid4().hex

def get_random_session():
    return secrets.token_hex(16)

def check_topic(formatted, unformatted):
    return formatted == unformatted.split("/")[0]    

def get_agent_id(device_description):
    if "id" in device_description["structured"]:
        return device_description["structured"]["id"]
    if "deviceId" in device_description["structured"]:
        return device_description["structured"]["deviceId"]

def get_column_name(name, model, mode):
    return f"{name}_{model}_{mode}"

async def save_dataframe(df, path, ensure=False):
    if df is None or len(df) == 0:
        return
    while True:
        try:
            df.to_csv(path, index=False, encoding="utf-8-sig")
            break
        except Exception:
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
    for code in sorted(os.listdir(RESULT_DIR), reverse=True):
        if os.listdir(f"{RESULT_DIR}/{code}"):
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

def debug(*text):
    if DEBUG:
        print(*text)

def set_debug(debug):
    global DEBUG
    DEBUG = debug

def remove_empty_results():
    if not os.path.exists(RESULT_DIR):
        os.mkdir(RESULT_DIR)
    for result_code in os.listdir(RESULT_DIR):
        files = os.listdir(f"{RESULT_DIR}/{result_code}")
        if len(files) == 1 and files[0] == "settings.txt":
            os.remove(SETTING_PATH.format(code=result_code))
            os.rmdir(f"{RESULT_DIR}/{result_code}")
        elif not files:            
            os.rmdir(f"{RESULT_DIR}/{result_code}")
