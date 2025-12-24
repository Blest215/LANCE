from dotenv import load_dotenv
load_dotenv()

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

# User agent

ORGANIZER_PROMPT = """
You are an AI assistant that helps users to accomplish their tasks by coordinating other agents.
Ask other agents to contribute to the user's task.

[User task]
{user_task}
"""

COORDINATOR_PROMPT = """
You are an AI assistant that organizes other agents to accomplish a user's task.

[User task]
{user_task}

[Team messages]
{team_messages}
"""

SMARTTHINGS_API_URL = "https://api.smartthings.com/v1/devices"

SCREENING_THRESHOLD = 0.3

MQTT_BROKER_ADDRESS = "localhost"
MQTT_TOPIC_DISCOVERY = "discovery/{team_id}"
MQTT_TOPIC_TEAM = "team/{team_id}"
MQTT_TOPIC_AGENT = "agent/{agent_id}"