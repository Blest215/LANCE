from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

SCENE_PROMPT = ChatPromptTemplate.from_template(
"""Convert the below survey response into a realistic scene.

The number of devices must be {num_devices}.

Where were you? {space}
What devices were in the space? {devices}""")

TASK_PROMPT = ChatPromptTemplate.from_template(
"""Convert the below survey response into a realistic utterance and evaluation goal in the scene.

What did you command the AI assistant? {user_command}
What behavior did you expect from the AI assistant and devices? {expected_behavior}

[Scene] {scene}""")

SCREENER_PROMPT = ChatPromptTemplate.from_template(
"""You are an AI agent that controls the following device: {description}
Can you contribute to the following request? {request}""")

CONTROLLER_PROMPT = ChatPromptTemplate.from_template(
"""You are an AI agent that controls the following device: {description}
Control the device for the request: {request}""")
