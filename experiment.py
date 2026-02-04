import asyncio
import pandas as pd
import os
import argparse
import sys

from tqdm import tqdm
from datetime import datetime
from typing import List, Dict, Any, Optional

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

        conversation, consequences, time_log = await user.main(mode, scenario.user_message)
        result[mode] = {
            "CONVERSATION": conversation,
            "CONSEQUENCES": consequences,
            "TIME": time_log,
        }

    # Wrap up
    user_loop.cancel()
    registry_task.cancel()
    for agent_task in agent_tasks:
        agent_task.cancel()

    return result

async def simulation(code, dataset_path, models, modes):
    result_path = f"{RESULT_DIR}/{code}/{dataset_path.replace('dataset', 'result')}"
    result_df = pd.read_csv(result_path) if os.path.exists(result_path) else pd.read_csv(f"{DATASET_DIR}/{dataset_path}")
    result_df = result_df.head() if args.debug else (result_df.head(args.head) if args.head else result_df)

    log_path = f"{RESULT_DIR}/{code}/{dataset_path.replace('dataset', 'log')}"
    log_df = pd.read_csv(log_path) if os.path.exists(log_path) else pd.DataFrame()

    done_columns = [column for column in parse_column(result_df, "CONSEQUENCES")]
    for model in models:
        undone_modes = [mode for mode in modes if get_column_name("CONSEQUENCES", model, mode) not in done_columns]
        if not undone_modes or not model.setup():
            continue

        simulation_results = [await simulate_scenario(model, undone_modes, scenario) for scenario in tqdm(result_df.itertuples(), total=len(result_df), maxinterval=1, desc=f"Simulation {str(model):40}")]

        for mode in undone_modes:
            log_df = pd.concat([log_df, pd.DataFrame({get_column_name("CONVERSATION", model, mode): [result[mode]["CONVERSATION"] for result in simulation_results]})], axis=1)
            result_df = pd.concat([result_df, pd.DataFrame({get_column_name("CONSEQUENCES", model, mode): [result[mode]["CONSEQUENCES"] for result in simulation_results]})], axis=1)
            result_df = pd.concat([result_df, pd.DataFrame({get_column_name("TIME", model, mode): [result[mode]["TIME"] for result in simulation_results]})], axis=1)
        model.wrapup()
        await save_dataframe(result_df, path=result_path)
        await save_dataframe(log_df, path=log_path)
    
    await save_dataframe(result_df, path=result_path, ensure=True)
    await save_dataframe(log_df, path=log_path, ensure=True)
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


async def main(code, configurations: List[Dict[str, Model]], modes: list[str]):
    dataset_pattern = re.compile(DATASET_FILENAME_PATTERN)
    
    for configuration in configurations:
        for dataset_file, models in configuration.items():
            if dataset_pattern.match(dataset_file) and os.path.exists(f"{DATASET_DIR}/{dataset_file}"):
                print(dataset_file)
                await evaluation(await simulation(code, dataset_file, models[:2] if args.debug else models, modes))

if __name__ == "__main__":
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument("--debug", action="store_true")
    argument_parser.add_argument("--code", type=str, required=False, default="")
    argument_parser.add_argument("--edge", action="store_true")
    argument_parser.add_argument("--resume", action="store_true")
    argument_parser.add_argument("--head", type=int, required=False)
    args = argument_parser.parse_args()
    set_debug(args.debug)

    # Get experiment code
    remove_empty_results()
    code = args.code if args.code else get_last_result() if args.resume else datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    code = code if not args.debug or "DEBUG" in code else f"{code}-DEBUG"
    print(code)
    if not os.path.exists(f"{RESULT_DIR}/{code}"):
        os.mkdir(f"{RESULT_DIR}/{code}")

    save_settings(code)

    configurations = [
        {"dataset_D5_M0.csv":[
            Model("qwen3:8b-q4_K_M", reasoning=False),
            Model("qwen3:4b-instruct-2507-q4_K_M"),
            Model("qwen3:0.6b-q4_K_M", reasoning=False),
        ]}
    ] if args.edge else [
        {"dataset_D5_M0.csv": [
            # Mid-size <=8b
            Model("rnj-1:8b-instruct-q8_0"),
            Model("ministral-3:8b-instruct-2512-q8_0"),
            Model("qwen3:8b-q8_0", reasoning=False),
            # Small-size <=4b
            Model("ministral-3:3b-instruct-2512-q8_0"),
            Model("granite4:3b-h"),
            Model("qwen3:4b-instruct-2507-q8_0"),
            # Tiny-size <=1b
            Model("functiongemma:270m-it-q8_0"),
            Model("granite4:1b-h-q8_0"),
            Model("qwen3:0.6b-q8_0", reasoning=False),
            # Settings
            Model("qwen3:0.6b-q4_K_M", reasoning=False),
            Model("qwen3:0.6b-q8_0", reasoning=True),
            Model("qwen3:4b-instruct-2507-q4_K_M"),
            Model("qwen3:4b-thinking-2507-q8_0"),
            Model("qwen3:8b-q4_K_M", reasoning=False),
            Model("qwen3:8b-q8_0", reasoning=True),
        ]},
        # Mutations
        {"dataset_D5_M20.csv": [Model("qwen3:4b-instruct-2507-q8_0")]},
        {"dataset_D5_M40.csv": [Model("qwen3:4b-instruct-2507-q8_0")]},
        {"dataset_D5_M60.csv": [Model("qwen3:4b-instruct-2507-q8_0")]},
        {"dataset_D5_M80.csv": [Model("qwen3:4b-instruct-2507-q8_0")]},
        {"dataset_D5_M100.csv": [Model("qwen3:4b-instruct-2507-q8_0")]},
        # Devices
        {"dataset_D10_M0.csv": [Model("qwen3:4b-instruct-2507-q8_0")]},
        {"dataset_D15_M0.csv": [Model("qwen3:4b-instruct-2507-q8_0")]},
        # etc
        {"dataset_D5_M0.csv": [
            Model("functiongemma:270m-it-q8_0"),
            Model("granite4:350m-h-q8_0"),
            Model("llama3.1:8b-instruct-q8_0"),
            Model("llama3.2:3b-instruct-q8_0"),
            Model("llama3.2:1b-instruct-q8_0"),
            Model("qwen3:1.7b-q4_K_M", reasoning=False),
            Model("qwen3:1.7b-q8_0", reasoning=False),
            Model("qwen3:1.7b-q8_0", reasoning=True),
        ]}
    ]

    if sys.platform.lower() == "win32" or os.name.lower() == "nt":
        from asyncio import set_event_loop_policy, WindowsSelectorEventLoopPolicy
        set_event_loop_policy(WindowsSelectorEventLoopPolicy())
    asyncio.run(main(code=code, configurations=configurations[:1] if args.debug else configurations, modes=ALLOWED_MODES))
