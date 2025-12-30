from dotenv import load_dotenv
load_dotenv()

# Settings

SMARTTHINGS_API_URL = "https://api.smartthings.com/v1/devices"

SCREENING_THRESHOLD = 0.3

ALLOWED_MODES = ["LANCE", "CENTRALIZED", "CLOUD", "ONTOLOGY"]

MQTT_BROKER_ADDRESS = "localhost"
# mode LANCE topics
MQTT_TOPIC_LANCE_DISCOVERY = "lance/discovery/{team_id}"
MQTT_TOPIC_LANCE_TEAM = "lance/team/{team_id}"
MQTT_TOPIC_LANCE_AGENT = "lance/agent/{agent_id}"
# mode CENTRALIZED topics
MQTT_TOPIC_CENTRALIZED_REGISTER = "centralized/register/{agent_id}"
MQTT_TOPIC_CENTRALIZED_CONTROL = "centralized/control/{agent_id}"
# mode CLOUD topics
# mode ONTOLOGY topics

# User agent

ORGANIZER_PROMPT = """
You are an AI assistant that helps users to accomplish their tasks by coordinating other agents.
Ask other agents to contribute to the user's task.

[User command]
{user_command}
"""

COORDINATOR_PROMPT = """
You are an AI assistant that organizes other agents to accomplish a user's task.

[User command]
{user_command}

[Team messages]
{team_messages}
"""

MASTERMIND_PROMPT = """
You are an AI assistant that controls devices to accomplish a user's task.

[User command]
{user_command}

[Device informations]
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
