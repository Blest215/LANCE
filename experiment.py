import asyncio
import multiprocessing
import pandas as pd
import os
import argparse
import random

from tqdm import tqdm
from tqdm.asyncio import tqdm as atqdm
from datetime import datetime
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.exceptions import OutputParserException
from langchain_core.prompts import ChatPromptTemplate

from model import Model
from settings import *
from registry import run_registry_process
from agent import run_agent_process
from user import UserAgent

# Simulation

async def setup_agent(session, user, agent_id, agent_configuration, device_description):
    p = multiprocessing.Process(target=run_agent_process, args=(session, agent_id, agent_configuration, device_description))
    p.start()
    await user.wait_for_client(agent_id)
    return p

async def simulate_scenario(semaphore, model, modes, scenario):
    results = []
    async with semaphore:
        await asyncio.sleep(random.randint(0, SIMULATION_CONCURRENCY_DELAY))
        for mode in modes:
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
            results.append(await user.command(mode, scenario.user_command))

            # Wrap up
            registry.terminate()
            for p in processes:
                p.terminate()
        
    return results

async def simulation(code, models, modes):
    result_path = f"{RESULT_PATH.format(code=code)}/result.csv"
    df = pd.read_csv(result_path) if os.path.exists(result_path) else pd.read_csv(DATASET_PATH)

    semaphore = asyncio.Semaphore(SIMULATION_CONCURRENCY_MAX)

    done_conversation_columns = [column for column in parse_column(df, "conversation")]
    for model in models:
        undone_modes = [mode for mode in modes if get_column_name("conversation", model, mode) not in done_conversation_columns]
        if not undone_modes or not model.setup():
            continue
        simulation_results = await atqdm.gather(*[simulate_scenario(semaphore, model, undone_modes, scenario) for scenario in df.itertuples()], desc=f"Simulation {str(model):30}")
        for i, mode in enumerate(undone_modes):
            df[get_column_name("conversation", model, mode)] = [result[i] for result in simulation_results]
        model.wrapup()
        await save_dataframe(df, path=result_path)
    await save_dataframe(df, path=result_path, ensure=True)

# Evaluation

from pydantic import BaseModel, Field
class EvaluationResult(BaseModel):
    score: float = Field(description="How the agents behaved well upon user's command. 0 <= score <= 100", ge=0, le=100)
    reason: str = Field(description="Reasoning for the score")

async def evaluate_scenario(semaphore, evaluator, scenario, column_name):
    async with semaphore:
        while True:
            try:
                return await evaluator.ainvoke({
                    "time": scenario.time,
                    "device_descriptions": scenario.device_descriptions,
                    "user_command": scenario.user_command,
                    "evaluation_criteria": scenario.evaluation_criteria,
                    "conversation": getattr(scenario, column_name),
                })
            except OutputParserException:
                continue

async def evaluation(code, evaluation_model):
    result_path = f"{RESULT_PATH.format(code=code)}/result.csv"
    if not os.path.exists(result_path):
        return

    df = pd.read_csv(result_path)
    evaluation_model.setup()
    evaluator_parser = PydanticOutputParser(pydantic_object=EvaluationResult)
    evaluator = ChatPromptTemplate([("user", EVALUATOR_PROMPT)]).partial(format=evaluator_parser.get_format_instructions()) | evaluation_model.instantiate() | evaluator_parser
    
    semaphore = asyncio.Semaphore(EVALUATION_CONCURRENCY_MAX)

    columns = parse_column(df, "conversation")
    for column in columns:
        df[column.replace("conversation", "score")] = None
        df[column.replace("conversation", "reason")] = None
    for scenario in tqdm(df.itertuples(), total=len(df), desc="Evaluation"):
        evaluation_results = await asyncio.gather(*[evaluate_scenario(semaphore, evaluator, scenario, column) for column in columns])
        for i, column in enumerate(columns):
            df.loc[scenario.Index, column.replace("conversation", "score")] = evaluation_results[i].score
            df.loc[scenario.Index, column.replace("conversation", "reason")] = evaluation_results[i].reason
        await save_dataframe(df, path=result_path)
    evaluation_model.wrapup()

    await save_dataframe(df, path=result_path, ensure=True)


async def main(code, models: list[Model], modes: list[str], evaluation_model: Model):
    await simulation(code, models, modes)
    await evaluation(code, evaluation_model)    

if __name__ == "__main__":
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument("--resume", action="store_true")
    argument_parser.add_argument("--code", type=str, required=False, default="")
    args = argument_parser.parse_args()

    # Remove empty directories
    for result_code in os.listdir(RESULT_PATH.split("/")[0]):
        if not os.listdir(RESULT_PATH.format(code=result_code)):
            os.rmdir(RESULT_PATH.format(code=result_code))

    # Get experiment code
    code = args.code if args.code else get_last_result() if args.resume else datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    if not os.path.exists(RESULT_PATH.format(code=code)):
        os.mkdir(RESULT_PATH.format(code=code))

    temperature = 0.8

    modes = ["CENTRALIZED", "NATURAL", "LANCE"]
    models = [
        # Model("Qwen/Qwen3-0.6B", backend="vllm", options="--enable-auto-tool-choice --tool-call-parser hermes --reasoning-parser qwen3", temperature=temperature, reasoning="high"),
        Model("qwen3:0.6b", backend="ollama", temperature=temperature, reasoning=True),
        Model("qwen3:1.7b", backend="ollama", temperature=temperature, reasoning=True),
        Model("qwen3:4b", backend="ollama", temperature=temperature, reasoning=True),
        # Model("qwen3:8b", backend="ollama", temperature=temperature, reasoning=True),
        # Model("Qwen/Qwen2.5-Coder-0.5B-Instruct", backend="vllm", options="--enable-auto-tool-choice --tool-call-parser hermes", temperature=temperature),
        # Model("ibm-granite/granite-4.0-350m", backend="vllm", options="--enable-auto-tool-choice --tool-call-parser hermes", temperature=temperature),
        # Model("ibm-granite/granite-3.0-1b-a400m-instruct", backend="vllm", options="--enable-auto-tool-choice --tool-call-parser granite --chat-template examples/tool_chat_template_granite.jinja", temperature=temperature),
        # Model("google/functiongemma-270m-it", backend="vllm", options="--enable-auto-tool-choice --tool-call-parser functiongemma --chat-template examples/tool_chat_template_functiongemma.jinja", temperature=temperature),
        # Model("google/gemma-3-270m-it", backend="vllm", options="--enable-auto-tool-choice --tool-call-parser hermes", temperature=temperature),
        # Model("HuggingFaceTB/SmolLM2-360M-Instruct", backend="vllm", options="--enable-auto-tool-choice --tool-call-parser hermes", temperature=temperature),
        # Model("HuggingFaceTB/SmolLM2-135M-Instruct", backend="vllm", options="--enable-auto-tool-choice --tool-call-parser hermes", temperature=temperature),
        # Model("meta-llama/Llama-3.2-1B-Instruct", backend="vllm", options="--enable-auto-tool-choice --tool-call-parser llama3_json --chat-template examples/tool_chat_template_llama3.2_json.jinja", temperature=temperature),
        # Model("gpt-oss:120b-cloud", backend="ollama", temperature=0.8, reasoning=True),
    ]
    evaluation_model = Model("gpt-oss:20b", backend="ollama", temperature=0.0, reasoning=True)

    asyncio.run(main(code=code, models=models, modes=modes, evaluation_model=evaluation_model))
