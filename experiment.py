import json
import asyncio
import multiprocessing

from langchain_ollama import ChatOllama
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langgraph.errors import GraphRecursionError

from utils import *
from settings import *
from registry import run_registry_process
from agent import run_agent_process
from user import UserAgent

from pydantic import ValidationError
from pydantic import BaseModel, Field
class EvaluationResult(BaseModel):
    score: float = Field(description="How the agents behaved well upon user's command. 0 <= score <= 1", ge=0, le=1)
    reason: str = Field(description="Reasoning for the score")

agent_configuration = {"model": "qwen3:8b", "reasoning": True, "temperature": 0.8, "num_predict": 2048}
device_informations = [l for l in open("example.txt", "r", encoding="utf-8")]

async def main(mode: str, evaluator):
    assert mode in ALLOWED_MODES
    queue = multiprocessing.Queue()

    # Set the registry
    registry = multiprocessing.Process(target=run_registry_process, args=(queue, ))
    registry.start()
    if queue.get() == "REGISTRY":
        pass

    # Set the device agents
    processes = []
    for d in device_informations:
        device_information = json.loads(d)
        agent_id = device_information["deviceId"] if "deviceId" in device_information else get_random_device_id()
        p = multiprocessing.Process(target=run_agent_process, args=(queue, agent_id, agent_configuration, device_information))
        processes.append(p)
        p.start()
        if queue.get() == agent_id:
            pass

    # Start a simulation
    user_command = "It's too dark, and I need to focus on reading."

    user = UserAgent(configuration=agent_configuration)
    while not user.is_connected():
        await asyncio.sleep(0.1)
    await user.command(mode=mode, user_command=user_command)

    # Evaluation
    while True:
        try:
            evaluation_result = evaluator.invoke({
                "user_command": user_command,
                "conversation": user.get_logs(),
            })
            break
        except ValidationError as e:
            continue
    print(evaluation_result)

    # Wrap up
    registry.terminate()
    for p in processes:
        p.terminate()

if __name__ == "__main__":
    evaluator_parser = PydanticOutputParser(pydantic_object=EvaluationResult)
    evaluator = ChatPromptTemplate([("user", EVALUATOR_PROMPT)]).partial(format=evaluator_parser.get_format_instructions()) | ChatOllama(
        model="gpt-oss-safeguard:20b", 
        temperature=0, 
        reasoning=True, 
    ) | evaluator_parser

    asyncio.run(main(mode="LANCE", evaluator=evaluator))
