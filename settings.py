from dotenv import load_dotenv
load_dotenv()

# Settings

SMARTTHINGS_API_URL = "https://api.smartthings.com/v1/devices"

SCREENING_THRESHOLD = 0.3

ALLOWED_MODES = ["LANCE", "NATURAL", "CENTRALIZED", "CLOUD", "ONTOLOGY"]

MQTT_BROKER_ADDRESS = "localhost"
MQTT_TOPIC_LOG = "log/{id}"
MQTT_TOPIC_RESPONSE = "response/{id}"
# mode LANCE topics
MQTT_TOPIC_LANCE_CALL = "call/{id}"
MQTT_TOPIC_LANCE_TEAM = "team/{id}"
# mode NATURAL topics
MQTT_TOPIC_NATURAL_AGENT = "agent/{id}"
# mode CENTRALIZED topics
MQTT_TOPIC_CENTRALIZED_DISCOVERY = "discovery/{id}"
MQTT_TOPIC_CENTRALIZED_REGISTER = "register/{id}"
MQTT_TOPIC_CENTRALIZED_CONTROL = "control/{id}"
# mode CLOUD topics
# mode ONTOLOGY topics

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

[User Command]
{user_command}

[Device Informations]
{device_informations}
"""

# LANCE agents

SCREENER_PROMPT = """
You are an AI assistant that controls the following device.

[Device Information]
{device_information}

Judge how well you can contribute to the given task.

[Message]
{message}

[Format]
{format}
"""

CONTROLLER_PROMPT = """
You are an AI assistant that controls the following device.

[Device Information]
{device_information}

Control the device based on the given message.

[Message]
{message}
"""

# EVALUATION

EVALUATOR_PROMPT = """
Evaluate the behavior of the agents in the conversation whether the user's task is accomplished or not.

[User Command]
{user_command}

[Conversation]
{conversation}

[Format]
{format}
"""
