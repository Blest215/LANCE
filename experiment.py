import asyncio
import multiprocessing
import pandas as pd

from tqdm import tqdm
from tqdm.asyncio import tqdm as atqdm

from datetime import datetime
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.exceptions import OutputParserException
from langchain_core.prompts import ChatPromptTemplate

from model import Model
from utils import *
from settings import *
from registry import run_registry_process
from agent import run_agent_process
from user import UserAgent

from pydantic import BaseModel, Field
class EvaluationResult(BaseModel):
    score: float = Field(description="How the agents behaved well upon user's command. 0 <= score <= 1", ge=0, le=1)
    reason: str = Field(description="Reasoning for the score")


async def setup_agent(session, user, agent_id, agent_configuration, device_description):
    p = multiprocessing.Process(target=run_agent_process, args=(session, agent_id, agent_configuration, device_description))
    p.start()
    await user.wait_for_client(agent_id)
    return p

async def simulate(model, modes, scenario):
    session = get_random_session()
    user_id = "COORDINATOR"
    user = UserAgent(session, id=user_id, model=model)
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
        agent_id=get_agent_id(device_description),
        agent_configuration=model,
        device_description=device_description
    ) for device_description in eval(scenario.device_descriptions)])        

    assert not user.wait

    # Start simulations
    results = [await user.command(mode, scenario.user_command) for mode in modes]

    # Wrap up
    registry.terminate()
    for p in processes:
        p.terminate()
    
    return results


async def evaluate(evaluator, model, mode, scenario):
    while True:
        try:
            return await evaluator.ainvoke({
                "time": scenario.time,
                "device_descriptions": scenario.device_descriptions,
                "user_command": scenario.user_command,
                "evaluation_criteria": scenario.evaluation_criteria,
                "conversation": getattr(scenario, get_column_name("conversation", model, mode)),
            })
        except OutputParserException:
            continue


async def main(now, models, modes, evaluation_model: Model):
    df = pd.read_csv(DATASET_PATH)

    # Simulation
    for model in models:
        model.setup()
        simulation_results = await atqdm.gather(*[simulate(model, modes, row) for row in df.itertuples()], desc="Simulation")
        for i, mode in enumerate(modes):
            df[get_column_name("conversation", model, mode)] = [result[i] for result in simulation_results]
        model.wrapup()

    df.to_csv(f"{RESULT_PATH.format(now=now)}/result.csv", index=False, encoding="utf-8-sig")

    # Evaluation
    evaluation_model.setup()
    evaluator_parser = PydanticOutputParser(pydantic_object=EvaluationResult)
    evaluator = ChatPromptTemplate([("user", EVALUATOR_PROMPT)]).partial(format=evaluator_parser.get_format_instructions()) | evaluation_model.instantiate() | evaluator_parser
    for model in models:
        for mode in modes:
            evaluation_results = await atqdm.gather(*[evaluate(evaluator, model, mode, row) for row in df.itertuples()], desc="Evaluation")
            df[get_column_name("score", model, mode)] = [result.score for result in evaluation_results]
            df[get_column_name("reason", model, mode)] = [result.reason for result in evaluation_results]
    evaluation_model.wrapup()

    while True:
        try:
            df.to_csv(f"{RESULT_PATH.format(now=now)}/result.csv", index=False, encoding="utf-8-sig")
            break
        except PermissionError:
            await asyncio.sleep(1)


if __name__ == "__main__":
    now = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    os.mkdir(RESULT_PATH.format(now=now))

    modes = ["LANCE", "NATURAL", "CENTRALIZED"]
    models = [
        Model("Qwen/Qwen3-0.6B", backend="openai", options="--enable-auto-tool-choice --tool-call-parser hermes --reasoning-parser qwen3", temperature=0.8, reasoning="high"),
        Model("ibm-granite/granite-4.0-350m", backend="openai", options="--enable-auto-tool-choice --tool-call-parser hermes", temperature=0.8),
    ]
    evaluation_model = Model("gpt-oss:20b", backend="ollama", temperature=0.0, reasoning=True)

    asyncio.run(main(now=now, models=models, modes=modes, evaluation_model=evaluation_model))
