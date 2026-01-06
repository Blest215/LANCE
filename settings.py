from dotenv import load_dotenv
load_dotenv()

# Settings

VLLM_URL = "http://localhost:8000/v1"

DATASET_PATH = "dataset/dataset_synthetic.csv"
SURVEY_PATH = "dataset/survey_result.csv"
RESULT_PATH = "results/{now}"

SIMULATION_BATCH_SIZE = 10
EVALUATION_BATCH_SIZE = 20
SYNTHESIZE_BATCH_SIZE = 5
TIMEOUT_LIMIT = 5
TICK = 0.01

ALLOWED_MODES = ["LANCE", "NATURAL", "CENTRALIZED", "ONTOLOGY"]

# LANCE

SCREENING_THRESHOLD = 0.3

# MQTT

MQTT_BROKER_ADDRESS = "localhost"
MQTT_TOPIC_LOG = "log"
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
