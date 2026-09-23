from model import Model
from settings import *
from simulator import *
from LANCE import *

def evaluate_scenario(simulator: Simulator, task: Task):
    scores = [
        100 if simulator.agents[goal_state.entity_id].properties[goal_state.attribute] == goal_state.value else 0 
        for goal_state in task.goal_states if goal_state.entity_type == "device"
    ]
    return sum(scores) / len(scores)

def simulate_scenarios(model: Model, mode: UserAgent, scenarios: List[pd.core.frame.pandas]):
    consequences = []
    times = []
    scores = []

    for scenario in tqdm(scenarios, total=len(scenarios), desc=f"Simulation {str(model):40} {mode.__name__}"):
        simulator = Simulator(eval(scenario.scene), model)
        task = Task.model_validate(eval(scenario.task))
        user = mode(model)

        try:
            user.main(simulator, task.user_utterance)
        except Exception as e:
            debug(e)

        consequences.append(simulator.render())
        times.append(user.time_log)
        scores.append(evaluate_scenario(simulator, task))

    return consequences, times, scores

def simulation(code, dataset_path, models, modes):
    result_path = f"{RESULT_DIR}/{code}/{dataset_path.replace('dataset', 'result')}"
    result_df = pd.read_csv(result_path) if os.path.exists(result_path) else pd.read_csv(f"{DATASET_DIR}/{dataset_path}")

    done_columns = [column for column in parse_column(result_df, "CONSEQUENCES")]
    for model in models:
        if not model.setup():
            continue
        for mode in modes:
            if get_column_name("CONSEQUENCES", model, mode.__name__) in done_columns:
                continue

            consequences, times, scores = simulate_scenarios(model, mode, list(result_df.itertuples()))

            result_df = pd.concat([result_df, pd.DataFrame({
                get_column_name("CONSEQUENCES", model, mode.__name__): consequences,
                get_column_name("TIME", model, mode.__name__): times,
                get_column_name("SCORE", model, mode.__name__): scores,
            })], axis=1)

        model.wrapup()
        save_dataframe(result_df, path=result_path)
    
    save_dataframe(result_df, path=result_path, ensure=True)
    return result_path

if __name__ == "__main__":
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument("--debug", action="store_true")
    argument_parser.add_argument("--code", type=str, required=False, default="")
    argument_parser.add_argument("--edge", action="store_true")
    argument_parser.add_argument("--resume", action="store_true")
    argument_parser.add_argument("--baseline-config", help="JSON with per-baseline resources and budgets")
    args = argument_parser.parse_args()
    set_debug(args.debug)

    # Get experiment code
    remove_empty_results()
    code = args.code if args.code else get_last_result() if args.resume else datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    print(code)
    if not os.path.exists(f"{RESULT_DIR}/{code}"):
        os.mkdir(f"{RESULT_DIR}/{code}")

    configurations = [
        ("dataset_D5_M0.csv", [
            Model("qwen3:8b-q4_K_M", reasoning=False),
            Model("qwen3:4b-instruct-2507-q4_K_M"),
            Model("qwen3:1.7b-q4_K_M", reasoning=False),
            Model("qwen3:0.6b-q4_K_M", reasoning=False),
        ])
    ] if args.edge else [
        ("dataset_D5_M0.csv", [
            # Small-size <=8b
            Model("ministral-3:8b-instruct-2512-q8_0"),
            Model("qwen3:8b-q8_0", reasoning=False),
            Model("llama3.1:8b-instruct-q8_0"),
            Model("ibm/granite4:tiny-h-q8_0"),
            # Tiny-size <=4b
            Model("qwen3:4b-instruct-2507-q8_0"),
            Model("ministral-3:3b-instruct-2512-q8_0"),
            Model("ibm/granite4:micro-h-q8_0"),
            Model("llama3.2:3b-instruct-q8_0"),
            # Micro-size <=2b
            Model("tomng/lfm2.5-instruct:1.2b-q8_0"),
            Model("granite4:1b-h-q8_0"),
            Model("qwen3.5:0.8b-q8_0", reasoning=False),
            Model("functiongemma:270m-it-q8_0"),
        ]),
        # Mutations
        ("dataset_D5_M20.csv", [Model("qwen3:4b-instruct-2507-q8_0")]),
        ("dataset_D5_M40.csv", [Model("qwen3:4b-instruct-2507-q8_0")]),
        ("dataset_D5_M60.csv", [Model("qwen3:4b-instruct-2507-q8_0")]),
        ("dataset_D5_M80.csv", [Model("qwen3:4b-instruct-2507-q8_0")]),
        ("dataset_D5_M100.csv", [Model("qwen3:4b-instruct-2507-q8_0")]),
        # Devices
        ("dataset_D10_M0.csv", [Model("qwen3:4b-instruct-2507-q8_0")]),
        ("dataset_D15_M0.csv", [Model("qwen3:4b-instruct-2507-q8_0")]),
        ("dataset_D20_M0.csv", [Model("qwen3:4b-instruct-2507-q8_0")]),
        # Settings
        ("dataset_D5_M0.csv", [
            Model("qwen3:0.6b-q8_0", reasoning=False),
            Model("qwen3:0.6b-q4_K_M", reasoning=False),
            Model("qwen3:0.6b-q8_0", reasoning=True),
            Model("qwen3:1.7b-q8_0", reasoning=False),
            Model("qwen3:1.7b-q4_K_M", reasoning=False),
            Model("qwen3:1.7b-q8_0", reasoning=True),
            Model("qwen3:4b-instruct-2507-q4_K_M"),
            Model("qwen3:4b-thinking-2507-q8_0"),
            Model("qwen3:8b-q4_K_M", reasoning=False),
            Model("qwen3:8b-q8_0", reasoning=True),
        ]),
        # etc
        ("dataset_D5_M0.csv", [
            Model("granite4:350m-h-q8_0"),
            Model("rnj-1:8b-instruct-q8_0"),
            Model("mistral:7b-instruct-v0.3-q8_0"),
            Model("cogito:8b-v1-preview-llama-q8_0"),
            Model("cogito:3b-v1-preview-llama-q8_0"),
            Model("phi4-mini:3.8b-q8_0"),
            Model("smollm2:1.7b-instruct-q8_0"),
            Model("nemotron-3-nano:4b-q8_0", reasoning=False),
            Model("llama3.2:1b-instruct-q8_0"),
            Model("qwen3.5:2b-q8_0", reasoning=False),
            Model("qwen3.5:4b-q8_0", reasoning=False),
            Model("qwen3.5:9b-q8_0", reasoning=False),
        ]), 
    ]

    configurations = [("dataset_D5_M0.csv", [Model("qwen3:4b-instruct-2507-q4_K_M")])]
    modes = [CENTRALIZED, NATURAL, RECRUIT, CONVERSATIONAL]

    for dataset_file, models in configurations:
        if DATASET_FILENAME_PATTERN.match(dataset_file) and os.path.exists(f"{DATASET_DIR}/{dataset_file}"):
            print(dataset_file)
            simulation(code, dataset_file, models, modes)
