import asyncio
import multiprocessing
import pandas as pd

from tqdm import tqdm
from tqdm.asyncio import tqdm as atqdm

from datetime import datetime
from langchain_ollama import ChatOllama
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.exceptions import OutputParserException
from langchain_core.prompts import ChatPromptTemplate

from utils import *
from settings import *
from registry import run_registry_process
from agent import run_agent_process
from user import UserAgent

from pydantic import BaseModel, Field
class EvaluationResult(BaseModel):
    score: float = Field(description="How the agents behaved well upon user's command. 0 <= score <= 1", ge=0, le=1)
    reason: str = Field(description="Reasoning for the score")

agent_configuration = {"model": "qwen3:8b", "reasoning": True, "temperature": 0.8, "num_predict": 2048}


async def setup_agent(session, user, agent_id, agent_configuration, device_information):
    p = multiprocessing.Process(target=run_agent_process, args=(session, agent_id, agent_configuration, device_information))
    p.start()
    await user.wait_for_client(agent_id)
    return p

async def simulate(mode, scenario):
    _, time, device_informations, user_command, evaluation_criteria = scenario

    session = get_random_session()
    user_id = "COORDINATOR"
    user = UserAgent(session, id=user_id, configuration=agent_configuration)
    while not user.is_connected():
        await asyncio.sleep(TICK)

    # Set the registry
    registry_id = "REGISTRY"
    registry = multiprocessing.Process(target=run_registry_process, args=(session, registry_id))
    registry.start()
    await user.wait_for_client(registry_id)

    # Set the device agents
    processes = await asyncio.gather(*[setup_agent(
        session=session,
        user=user,
        agent_id=device_information["deviceId"] if "deviceId" in device_information else get_random_device_id(),
        agent_configuration=agent_configuration,
        device_information=device_information
    ) for device_information in eval(device_informations)])        

    assert not user.wait

    # Start a simulation
    await user.command(mode=mode, user_command=user_command)
    await asyncio.sleep(TIMEOUT_LIMIT)

    # Wrap up
    registry.terminate()
    for p in processes:
        p.terminate()
    
    return user.get_logs()


async def evaluate(scenario):
    _, time, device_informations, user_command, evaluation_criteria, conversation = scenario
    while True:
        try:
            return await evaluator.ainvoke({
                "time": time,
                "device_informations": device_informations,
                "user_command": user_command,
                "evaluation_criteria": evaluation_criteria,
                "conversation": conversation,
            })
        except OutputParserException:
            continue


async def main(now, mode, evaluator):
    assert mode in ALLOWED_MODES

    df = pd.read_csv(DATASET_PATH)

    # Simulation
    simulation_results = [await simulate(mode, row) for row in tqdm(df.itertuples(), total=len(df), desc="Simulation")]
    df["conversation"] = simulation_results

    # Evaluation
    evaluation_results = await atqdm.gather(*[evaluate(row) for row in df.itertuples()], desc="Evaluation")
    df["score"] = [result.score for result in evaluation_results]
    df["reason"] = [result.reason for result in evaluation_results]

    df.to_csv(f"{RESULT_PATH.format(now=now)}/result.csv", index=False, encoding="utf-8-sig")


if __name__ == "__main__":
    now = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    os.mkdir(RESULT_PATH.format(now=now))

    evaluator_parser = PydanticOutputParser(pydantic_object=EvaluationResult)
    evaluator = ChatPromptTemplate([("user", EVALUATOR_PROMPT)]).partial(format=evaluator_parser.get_format_instructions()) | ChatOllama(
        model="gpt-oss-safeguard:20b",
        temperature=0,
        reasoning=True,
    ) | evaluator_parser

    asyncio.run(main(now=now, mode="NATURAL", evaluator=evaluator))
