import asyncio
import pandas as pd
import os
import argparse
import sys
import time

from tqdm import tqdm
from tqdm.asyncio import tqdm as atqdm
from datetime import datetime
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.exceptions import OutputParserException

from model import Model
from settings import *
from registry import Registry
from agent import Agent
from user import UserAgent

# Simulation

async def simulate_scenario(model, modes, scenario):
    user_id = "COORDINATOR"
    user = UserAgent(id=user_id, model=model)
    user_loop = asyncio.create_task(user.loop())
    while not user.is_connected:
        await asyncio.sleep(TICK)
    
    # Set the registry
    registry = Registry()
    registry_task = asyncio.create_task(registry.loop())
    while not registry.is_connected:
        await asyncio.sleep(TICK)

    # Set the device agents
    agents = [Agent(get_agent_id(device_description), model, device_description) for device_description in eval(scenario.device_descriptions)]
    agent_tasks = [asyncio.create_task(agent.loop()) for agent in agents]
    while not all(agent.is_connected for agent in agents):
        await asyncio.sleep(TICK)

    result = {}
    for mode in modes:
        new_session = get_random_session()
        await user.reset(new_session)
        await registry.reset(new_session)
        for agent in agents:
            await agent.reset(new_session)
        user.set_agents([agent.id for agent in agents])

        conversation, consequences = await user.main(mode, scenario.user_message)
        result["CONVERSATION"] = conversation
        result["CONSEQUENCES"] = consequences

    # Wrap up
    user_loop.cancel()
    registry_task.cancel()
    for agent_task in agent_tasks:
        agent_task.cancel()

    return result

async def simulation(code, dataset_path, models, modes):
    result_path = f"{RESULT_DIR}/{code}/{dataset_path.replace('dataset', 'result')}"
    result_df = pd.read_csv(result_path) if os.path.exists(result_path) else pd.read_csv(f"{DATASET_DIR}/{dataset_path}")
    result_df = result_df.head() if args.debug else result_df

    done_conversation_columns = [column for column in parse_column(result_df, "CONVERSATION")]
    for model in models:
        undone_modes = [mode for mode in modes if get_column_name("CONVERSATION", model, mode) not in done_conversation_columns]
        if not undone_modes or not model.setup():
            continue

        simulation_results = [await simulate_scenario(model, undone_modes, scenario) for scenario in tqdm(result_df.itertuples(), total=len(result_df), maxinterval=1, desc=f"Simulation {str(model):40}")]

        for mode in undone_modes:
            result_df[get_column_name("CONSEQUENCES", model, mode)] = [result["CONSEQUENCES"] for result in simulation_results]
        model.wrapup()
        await save_dataframe(result_df, path=result_path)
    await save_dataframe(result_df, path=result_path, ensure=True)
    return result_path

# Evaluation

def compare_consequence(expectation, consequence):
    if not consequence["success"]:
        return False
    if expectation["agent_id"] != consequence["agent_id"]:
        return False
    for key, value in expectation.items():
        if key == "agent_id":
            continue
        if value and (key not in consequence["request"] or value != consequence["request"][key]):
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

async def evaluation(result_path):
    if not os.path.exists(result_path):
        return

    df = pd.read_csv(result_path)

    # Accuracy
    columns = parse_column(df, "CONSEQUENCES")
    evaluation_results = [evaluate_scenario(scenario, columns) for scenario in tqdm(df.itertuples(), total=len(df), desc="Evaluation")]
    for column in [column.replace("CONSEQUENCES", "ACCURACY") for column in columns]:
        df[column] = [result[column] for result in evaluation_results]

    print(df.mean(numeric_only=True))
    await save_dataframe(df, path=result_path, ensure=True)


async def main(code, models: list[Model], modes: list[str]):
    dataset_pattern = re.compile(r'dataset_(\w+)_(\d+)(?:_M\d+)?\.csv')
    
    datasets = [file for file in os.listdir(DATASET_DIR) if dataset_pattern.match(file)]
    datasets = datasets if not args.debug else datasets[:1]
    for dataset_file in datasets:
        print(dataset_file)
        result_path = await simulation(code, dataset_file, models, modes)
        await evaluation(result_path)

if __name__ == "__main__":
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument("--debug", action="store_true")
    argument_parser.add_argument("--code", type=str, required=False, default="")
    argument_parser.add_argument("--resume", action="store_true")
    args = argument_parser.parse_args()
    assert not (args.debug and args.resume)
    set_debug(args.debug)

    # Remove empty directories
    for result_code in os.listdir(RESULT_DIR):
        files = os.listdir(f"{RESULT_DIR}/{result_code}")
        if len(files) == 1 and files[0] == "settings.txt":
            os.remove(SETTING_PATH.format(code=result_code))
            os.rmdir(f"{RESULT_DIR}/{result_code}")
        elif not files:            
            os.rmdir(f"{RESULT_DIR}/{result_code}")

    # Get experiment code
    code = args.code if args.code else get_last_result() if args.resume else datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    code = code if not args.debug or "DEBUG" in code else f"{code}-DEBUG"
    print(code)
    if not os.path.exists(f"{RESULT_DIR}/{code}"):
        os.mkdir(f"{RESULT_DIR}/{code}")

    save_settings(code)

    modes = ["CENTRALIZED", "NATURAL", "RECRUIT", "CONVERSATIONAL"]
    
    models = [
        # Larger models
        Model("qwen3:4b-instruct-2507-q8_0", temperature=0.1),
        # Model("ministral-3:3b-instruct-2512-q8_0", temperature=0.1),
        # Model("granite3.1-moe:3b-instruct-q8_0", temperature=0.1),
        # Model("cogito:3b-v1-preview-llama-q8_0", temperature=0.1),
        # Model("phi4-mini:3.8b-q8_0", temperature=0.1),
        # Model("hermes3:3b-llama3.2-q8_0", temperature=0.1),
        # Model("nemotron-mini:4b-instruct-q8_0", temperature=0.1),
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
        Model("smollm2:1.7b-instruct-q8_0", temperature=0.1),
        # Model("HuggingFaceTB/SmolLM2-135M-Instruct", backend="vllm", options="--enable-auto-tool-choice --tool-call-parser hermes", temperature=0.1),
        # Model("HuggingFaceTB/SmolLM2-360M-Instruct", backend="vllm", options="--enable-auto-tool-choice --tool-call-parser hermes", temperature=0.1),
        Model("llama3.2:1b-instruct-q8_0", temperature=0.1),
        # Model("meta-llama/Llama-3.2-1B-Instruct", backend="vllm", options="--enable-auto-tool-choice --tool-call-parser llama3_json --chat-template examples/tool_chat_template_llama3.2_json.jinja", temperature=0.1),
    ]

    if sys.platform.lower() == "win32" or os.name.lower() == "nt":
        from asyncio import set_event_loop_policy, WindowsSelectorEventLoopPolicy
        set_event_loop_policy(WindowsSelectorEventLoopPolicy())
    asyncio.run(main(code=code, models=models if not args.debug else models[:2], modes=modes))
