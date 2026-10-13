from model import Model
from settings import *
from environment import *
from LANCE import LANCE
from baseline import CENTRALIZED, Sasha, LLMind

def simulate_scenarios(model: Model, mode, scenarios: List[pd.core.frame.pandas]):
    consequences = []
    times = []
    tokens = []
    scores = []

    for scenario in tqdm(scenarios, total=len(scenarios), desc=f"Simulation {str(model):40} {mode.__name__}"):
        environment = Environment([DeviceDraft.model_validate(draft) for draft in eval(scenario.devices)])
        task = environment.compile_task(Task.model_validate(eval(scenario.task)))
        user = mode(model)

        consequence = user.main(environment, scenario.utterance)

        consequences.append(consequence)
        times.append(user.time_log)
        tokens.append(user.token_log)
        scores.append(environment.evaluate(task))

    return consequences, times, tokens, scores

def simulation(code, dataset_file, models, modes):
    dataset_df = pd.read_csv(f"{DATASET_DIR}/{dataset_file}").dropna()
    result_path = f"{RESULT_DIR}/{code}/{dataset_file.replace('dataset', 'result')}"
    result_df = pd.read_csv(result_path) if os.path.exists(result_path) else pd.DataFrame()

    done_columns = [column for column in parse_column(result_df, "CONSEQUENCES")]
    for model in models:
        if not model.setup():
            continue
        for mode in modes:
            if get_column_name("CONSEQUENCES", model, mode.__name__) in done_columns:
                continue

            consequences, times, tokens, scores = simulate_scenarios(model, mode, list(dataset_df.itertuples()))

            result_df = pd.concat([result_df, pd.DataFrame({
                get_column_name("CONSEQUENCES", model, mode.__name__): consequences,
                get_column_name("TIME", model, mode.__name__): times,
                get_column_name("TOKEN", model, mode.__name__): tokens,
                get_column_name("SCORE", model, mode.__name__): scores,
            })], axis=1)
            save_dataframe(result_df, path=result_path)
        model.wrapup()
    
    save_dataframe(result_df, path=result_path, ensure=True)
    return result_path

if __name__ == "__main__":
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument("--debug", action="store_true")
    argument_parser.add_argument("--code", type=str, required=False, default="")
    argument_parser.add_argument("--edge", action="store_true")
    argument_parser.add_argument("--resume", action="store_true")
    args = argument_parser.parse_args()
    set_debug(args.debug)

    # Get experiment code
    remove_empty_results()
    code = args.code if args.code else get_last_result() if args.resume else datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    print(code)
    if not os.path.exists(f"{RESULT_DIR}/{code}"):
        os.mkdir(f"{RESULT_DIR}/{code}")

    representative_model = Model("qwen3.5:9b-q4_K_M", reasoning=False)

    configurations = [
        ("dataset_D0_M0.csv", [CENTRALIZED, LANCE], [
            representative_model,
        ]),
        ("dataset_D5_M0.csv", [CENTRALIZED, Sasha, LLMind, LANCE], [
            # Small-size <=8b
            Model("qwen3.5:9b-q4_K_M", reasoning=False),
            Model("gemma4:e4b-it-q4_K_M", reasoning=False),
            Model("granite4.2:8b-q4_K_M", reasoning=False),
            Model("lfm2.5:8b-a1b-q4_K_M", reasoning=False),
            Model("ministral-3:8b-instruct-2512-q4_K_M", reasoning=False),
            Model("ornith:9b-q4_K_M", reasoning=False),
            Model("rnj-1:8b-instruct-q4_K_M"),
            # Tiny-size <=4b
            Model("qwen3.5:4b-q4_K_M", reasoning=False),
            Model("gemma4:e2b-it-q4_K_M", reasoning=False),
            Model("granite4.2:3b-q4_K_M", reasoning=False),
            Model("ministral-3:3b-instruct-2512-q4_K_M", reasoning=False),
            Model("llama3.2:3b-instruct-q4_K_M"),
            # Micro-size <=2b
            Model("qwen3.5:2b-q4_K_M", reasoning=False),
            Model("qwen3.5:0.8b-q8_0", reasoning=False),
            Model("llama3.2:1b-instruct-q4_K_M"),
        ]),
        ("dataset_D10_M0.csv", [CENTRALIZED, LANCE], [
            representative_model,
        ]),
        ("dataset_D15_M0.csv", [CENTRALIZED, LANCE], [
            representative_model,
        ]),
        ("dataset_D20_M0.csv", [CENTRALIZED, LANCE], [
            representative_model,
        ]),
    ]

    try:
        for dataset_file, modes, models in configurations:
            if DATASET_FILENAME_PATTERN.match(dataset_file) and os.path.exists(f"{DATASET_DIR}/{dataset_file}"):
                print(dataset_file)
                simulation(code, dataset_file, models, modes)
    except KeyboardInterrupt:
        pass
