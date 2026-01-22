import asyncio
import multiprocessing
import pandas as pd
import os
import argparse
import sys

from tqdm import tqdm
from tqdm.asyncio import tqdm as atqdm
from datetime import datetime
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.exceptions import OutputParserException

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

async def simulate_scenario(model, modes, scenario):
    session = get_random_session()
    user_id = "COORDINATOR"
    user = UserAgent(session, id=user_id, model=model)
    user_loop = asyncio.create_task(user.loop())
    while not user.is_connected:
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

    result = {}
    for mode in modes:
        await user.new_session(get_random_session())
        conversation, consequences = await user.main(mode, scenario.user_message)
        result[get_column_name("CONVERSATION", model, mode)] = conversation
        result[get_column_name("CONSEQUENCES", model, mode)] = consequences

    # Wrap up
    user_loop.cancel()
    registry.terminate()
    for p in processes:
        p.terminate()

    return result

async def simulation(code, dataset_path, models, modes):
    result_path = f"{RESULT_DIR}/{code}/{dataset_path.replace('dataset', 'result')}"
    df = pd.read_csv(result_path) if os.path.exists(result_path) else pd.read_csv(f"{DATASET_DIR}/{dataset_path}")
    df = df.head() if args.debug else df

    async def wait():
        await asyncio.sleep(1)
        gpu_utilizations.append(get_gpu_utilization())
        pbar.n = sum(1 for t in tasks if t.done())
        pbar.set_postfix({"running": len(tasks) - pbar.n})

    done_conversation_columns = [column for column in parse_column(df, "CONVERSATION")]
    for model in models:
        undone_modes = [mode for mode in modes if get_column_name("CONVERSATION", model, mode) not in done_conversation_columns]
        if not undone_modes or not model.setup():
            continue

        tasks = []
        simulation_results = []
        gpu_utilizations = [get_gpu_utilization()]
        with tqdm(total=len(df), mininterval=1, desc=f"Simulation {str(model):40}") as pbar:
            for scenario in df.itertuples():
                while moving_average(gpu_utilizations, SIMULATION_CONCURRENCY_DELAY) > SIMULATION_CONCURRENCY_GPU_MAX:
                    await wait()
                tasks.append(asyncio.create_task(simulate_scenario(model, undone_modes, scenario)))
                for _ in range(SIMULATION_CONCURRENCY_DELAY):
                    await wait()
            while not all(t.done() for t in tasks):
                await wait()
        simulation_results = await asyncio.gather(*tasks)

        for mode in undone_modes:
            df[get_column_name("CONVERSATION", model, mode)] = [result[get_column_name("CONVERSATION", model, mode)] for result in simulation_results]
            df[get_column_name("CONSEQUENCES", model, mode)] = [result[get_column_name("CONSEQUENCES", model, mode)] for result in simulation_results]
        model.wrapup()
        await save_dataframe(df, path=result_path)
    await save_dataframe(df, path=result_path, ensure=True)
    return result_path

# Evaluation

from pydantic import BaseModel, Field
class EvaluationResult(BaseModel):
    score: int = Field(description="How the agents behaved well upon user's command. 0 <= score <= 100", ge=0, le=100)
    reason: str = Field(description="Reasoning for the score")

def compare_consequence(expectation, consequence):
    if not consequence["success"]:
        return False
    if expectation["agent_id"] != consequence["agent_id"]:
        return False
    for key in expectation:
        if key == "agent_id":
            continue
        if key not in consequence["request"]:
            return False
        if expectation[key] != consequence["request"][key]:
            return False
    return True

def evaluate_scenario(scenario, columns):
    result = {}
    evaluation_criteria = eval(scenario.evaluation_criteria)
    for column in columns:
        consequences = eval(getattr(scenario, column))
        correct = sum([100 if any(compare_consequence(expectation, consequence) for consequence in consequences) else 0 for expectation in evaluation_criteria])
        result[column.replace("CONSEQUENCES", "ACCURACY")] = int(correct / len(evaluation_criteria)) if len(evaluation_criteria) > 0 else None
    return result

async def scoring_scenario(semaphore, evaluator, scenario, column_name):
    async with semaphore:
        while True:
            try:
                return await evaluator.ainvoke({
                    "device_descriptions": scenario.device_descriptions,
                    "user_message": scenario.user_message,
                    "evaluation_criteria": "\n".join([f"Agent {expectation['agent_id']}: {expectation}" for expectation in eval(scenario.evaluation_criteria)]),
                    "conversation": getattr(scenario, column_name),
                })
            except OutputParserException as e:
                continue

async def evaluation(result_path, evaluation_model=None):
    if not os.path.exists(result_path):
        return

    df = pd.read_csv(result_path)

    # Accuracy
    columns = parse_column(df, "CONSEQUENCES")
    evaluation_results = [evaluate_scenario(scenario, columns) for scenario in tqdm(df.itertuples(), total=len(df), desc="Evaluation")]
    for column in [column.replace("CONSEQUENCES", "ACCURACY") for column in columns]:
        df[column] = [result[column] for result in evaluation_results]
    
    await save_dataframe(df, path=result_path, ensure=True)

    # Score
    if evaluation_model:
        evaluation_model.setup()
        evaluator_parser = PydanticOutputParser(pydantic_object=EvaluationResult)
        evaluator = EVALUATOR_PROMPT.partial(format=evaluator_parser.get_format_instructions()) | evaluation_model.instantiate() | evaluator_parser
        
        semaphore = asyncio.Semaphore(EVALUATION_CONCURRENCY_MAX)

        columns = parse_column(df, "CONVERSATION")
        for column in columns:
            df[column.replace("CONVERSATION", "SCORE")] = None
            df[column.replace("CONVERSATION", "REASON")] = None
        for scenario in tqdm(df.itertuples(), total=len(df), desc="Evaluation"):
            evaluation_results = await asyncio.gather(*[scoring_scenario(semaphore, evaluator, scenario, column) for column in columns])
            for i, column in enumerate(columns):
                df.loc[scenario.Index, column.replace("CONVERSATION", "SCORE")] = evaluation_results[i].score
                df.loc[scenario.Index, column.replace("CONVERSATION", "REASON")] = evaluation_results[i].reason
            await save_dataframe(df, path=result_path)
        evaluation_model.wrapup()

    print(df.mean(numeric_only=True))
    await save_dataframe(df, path=result_path, ensure=True)


async def main(code, models: list[Model], modes: list[str], evaluation_model: Model):
    dataset_pattern = re.compile(r'dataset_(\w+)_(\d+)(?:_M\d+)?\.csv')
    
    datasets = [file for file in os.listdir(DATASET_DIR) if dataset_pattern.match(file)]
    for dataset_file in datasets:
        print(dataset_file)
        result_path = await simulation(code, dataset_file, models, modes)
        await evaluation(result_path, evaluation_model)

if __name__ == "__main__":
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument("--debug", action="store_true")
    argument_parser.add_argument("--code", type=str, required=False, default="")
    argument_parser.add_argument("--resume", action="store_true")
    argument_parser.add_argument("--scoring", action="store_true")
    args = argument_parser.parse_args()
    set_debug(args.debug)

    # Remove empty directories
    for result_code in os.listdir(RESULT_DIR):
        if not os.listdir(f"{RESULT_DIR}/{result_code}"):
            os.rmdir(f"{RESULT_DIR}/{result_code}")

    # Get experiment code
    code = args.code if args.code else get_last_result() if args.resume else datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    code = code if not args.debug or "DEBUG" in code else f"{code}-DEBUG"
    print(code)
    if not os.path.exists(f"{RESULT_DIR}/{code}"):
        os.mkdir(f"{RESULT_DIR}/{code}")

    modes = ["CENTRALIZED", "NATURAL", "RECRUIT", "CONVERSATIONAL"]
    
    models = [
        # Larger models
        Model("qwen3:4b-instruct-2507-q8_0", temperature=0.1),
        # Model("ministral-3:3b-instruct-2512-q8_0", temperature=0.1, reasoning=None),
        # Model("granite3.1-moe:3b-instruct-q8_0", temperature=0.1, reasoning=None),
        # Model("cogito:3b-v1-preview-llama-q8_0", temperature=0.1, reasoning=None),
        # Model("phi4-mini:3.8b-q8_0", temperature=0.1, reasoning=None),
        # Model("hermes3:3b-llama3.2-q8_0", temperature=0.1, reasoning=None),
        # Model("nemotron-mini:4b-instruct-q8_0", temperature=0.1, reasoning=None),
        # Model("llama3.2:3b-instruct-q8_0", temperature=0.1),
        # Model("gpt-oss:120b-cloud", temperature=0.1, reasoning=True),
        # Model("gpt-oss:20b", temperature=0.1, reasoning=False),

        Model("qwen3:0.6b-q8_0", temperature=0.1, reasoning=False),
        Model("qwen3:0.6b-q8_0", temperature=0.1, reasoning=True),
        Model("qwen3:1.7b-q8_0", temperature=0.1, reasoning=False),
        Model("qwen3:1.7b-q8_0", temperature=0.1, reasoning=True),
        # Model("Qwen/Qwen3-0.6B", backend="vllm", options="--enable-auto-tool-choice --tool-call-parser hermes --reasoning-parser qwen3", temperature=0.1, reasoning="high"),
        # Model("Qwen/Qwen2.5-Coder-0.5B-Instruct", backend="vllm", options="--enable-auto-tool-choice --tool-call-parser hermes", temperature=0.1),
        Model("granite4:350m-h-q8_0", temperature=0.1),
        Model("granite4:1b-h-q8_0", temperature=0.1),
        # Model("ibm-granite/granite-4.0-350m", backend="vllm", options="--enable-auto-tool-choice --tool-call-parser hermes", temperature=0.1),
        # Model("ibm-granite/granite-3.0-1b-a400m-instruct", backend="vllm", options="--enable-auto-tool-choice --tool-call-parser granite --chat-template examples/tool_chat_template_granite.jinja", temperature=0.1),
        Model("functiongemma:270m-it-q8_0", temperature=0.1),
        # Model("google/functiongemma-270m-it", backend="vllm", options="--enable-auto-tool-choice --tool-call-parser functiongemma --chat-template examples/tool_chat_template_functiongemma.jinja", temperature=0.1),
        # Model("google/gemma-3-270m-it", backend="vllm", options="--enable-auto-tool-choice --tool-call-parser hermes", temperature=0.1),
        # Model("smollm2:135m-instruct-q8_0", temperature=0.1),
        # Model("smollm2:360m-instruct-q8_0", temperature=0.1),
        # Model("smollm2:1.7b-instruct-q8_0", temperature=0.1),
        # Model("HuggingFaceTB/SmolLM2-135M-Instruct", backend="vllm", options="--enable-auto-tool-choice --tool-call-parser hermes", temperature=0.1),
        # Model("HuggingFaceTB/SmolLM2-360M-Instruct", backend="vllm", options="--enable-auto-tool-choice --tool-call-parser hermes", temperature=0.1),
        Model("llama3.2:1b-instruct-q8_0", temperature=0.1),
        # Model("meta-llama/Llama-3.2-1B-Instruct", backend="vllm", options="--enable-auto-tool-choice --tool-call-parser llama3_json --chat-template examples/tool_chat_template_llama3.2_json.jinja", temperature=0.1),
    ]
    evaluation_model = Model("gpt-oss:20b", temperature=0.1, reasoning=False) if args.scoring else None

    if sys.platform.lower() == "win32" or os.name.lower() == "nt":
        from asyncio import set_event_loop_policy, WindowsSelectorEventLoopPolicy
        set_event_loop_policy(WindowsSelectorEventLoopPolicy())
    asyncio.run(main(code=code, models=models if not args.debug else models[:2], modes=modes, evaluation_model=evaluation_model))
