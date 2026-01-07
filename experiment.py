import asyncio
import multiprocessing
import pandas as pd
import os
import itertools
import argparse

from tqdm import tqdm
from datetime import datetime
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.exceptions import OutputParserException
from langchain_core.prompts import ChatPromptTemplate

from model import Model
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

async def simulate_scenario(model, modes, scenario):
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

async def simulation(now, models, modes):
    result_path = f"{RESULT_PATH.format(now=now)}/result.csv"
    if os.path.exists(result_path):
        return
    
    df = pd.read_csv(DATASET_PATH)
    batches = batch_dataframe(df, SIMULATION_BATCH_SIZE)
    for model in models:
        if not model.setup():
            continue
        simulation_results = sum([await asyncio.gather(*[simulate_scenario(model, modes, scenario) for scenario in batch.itertuples()]) for batch in tqdm(batches, desc="Simulation")], [])
        for i, mode in enumerate(modes):
            df[get_column_name("conversation", model, mode)] = [result[i] for result in simulation_results]
        model.wrapup()
        await save_dataframe(df, path=result_path)
    await save_dataframe(df, path=result_path, ensure=True)


async def evaluate_scenario(evaluator, model, mode, scenario):
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

async def evaluation(now, models, modes, evaluation_model):
    result_path = f"{RESULT_PATH.format(now=now)}/result.csv"
    if not os.path.exists(result_path):
        return
    
    df = pd.read_csv(result_path)
    batches = batch_dataframe(df, EVALUATION_BATCH_SIZE)
    evaluation_model.setup()
    evaluator_parser = PydanticOutputParser(pydantic_object=EvaluationResult)
    evaluator = ChatPromptTemplate([("user", EVALUATOR_PROMPT)]).partial(format=evaluator_parser.get_format_instructions()) | evaluation_model.instantiate() | evaluator_parser
    for model, mode in tqdm(list(itertools.product(models, modes)), desc="Evaluation"):
        evaluation_results = sum([await asyncio.gather(*[evaluate_scenario(evaluator, model, mode, scenario) for scenario in batch.itertuples()]) for batch in batches], [])
        df[get_column_name("score", model, mode)] = [result.score for result in evaluation_results]
        df[get_column_name("reason", model, mode)] = [result.reason for result in evaluation_results]
    evaluation_model.wrapup()

    await save_dataframe(df, path=result_path, ensure=True)


async def main(now, models: list[Model], modes: list[str], evaluation_model: Model):
    await simulation(now, models, modes)
    await evaluation(now, models, modes, evaluation_model)    

if __name__ == "__main__":
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument("--now", type=str, required=False, default="")
    args = argument_parser.parse_args()

    now = args.now if args.now else datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    if not os.path.exists(RESULT_PATH.format(now=now)):
        os.mkdir(RESULT_PATH.format(now=now))
    now = "2026-01-06-19-38-54"

    temperature = 0.8

    modes = ["CENTRALIZED", "NATURAL", "LANCE"]
    models = [
        Model("Qwen/Qwen3-0.6B", backend="vllm", options="--enable-auto-tool-choice --tool-call-parser hermes --reasoning-parser qwen3", temperature=temperature, reasoning="high"),
        Model("qwen3:0.6b", backend="ollama", temperature=temperature, reasoning=True),
        # Model("Qwen/Qwen2.5-Coder-0.5B-Instruct", backend="vllm", options="--enable-auto-tool-choice --tool-call-parser hermes", temperature=temperature),
        Model("ibm-granite/granite-4.0-350m", backend="vllm", options="--enable-auto-tool-choice --tool-call-parser hermes", temperature=temperature),
        # Model("ibm-granite/granite-3.0-1b-a400m-instruct", backend="vllm", options="--enable-auto-tool-choice --tool-call-parser granite --chat-template examples/tool_chat_template_granite.jinja", temperature=temperature),
        # Model("google/functiongemma-270m-it", backend="vllm", options="--enable-auto-tool-choice --tool-call-parser functiongemma --chat-template examples/tool_chat_template_functiongemma.jinja", temperature=temperature),
        # Model("google/gemma-3-270m-it", backend="vllm", options="--enable-auto-tool-choice --tool-call-parser hermes", temperature=temperature),
        # Model("HuggingFaceTB/SmolLM2-360M-Instruct", backend="vllm", options="--enable-auto-tool-choice --tool-call-parser hermes", temperature=temperature),
        # Model("HuggingFaceTB/SmolLM2-135M-Instruct", backend="vllm", options="--enable-auto-tool-choice --tool-call-parser hermes", temperature=temperature),
        Model("meta-llama/Llama-3.2-1B-Instruct", backend="vllm", options="--enable-auto-tool-choice --tool-call-parser llama3_json --chat-template examples/tool_chat_template_llama3.2_json.jinja", temperature=temperature),
        # Model("gpt-oss:120b-cloud", backend="ollama", temperature=0.8, reasoning=True),
    ]
    evaluation_model = Model("gpt-oss:20b", backend="ollama", temperature=0.0, reasoning=True, num_predict=4096)

    asyncio.run(main(now=now, models=models, modes=modes, evaluation_model=evaluation_model))
