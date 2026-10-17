from model import Model
from settings import *
from environment import *
from LANCE import LANCE
from baseline import Centralized, RAG, Sasha, LLMind
from ast import literal_eval

def simulate_scenario(model: Model, mode, scenario):
    environment = Environment([DeviceDraft.model_validate(draft) for draft in literal_eval(scenario.devices)])
    user = mode(model)
    log = user.main(environment, scenario.utterance)
    return log, user.time_log, user.token_log, [action.model_dump() for action in environment.action_calls]

def simulate_scenarios(model: Model, mode, scenarios):
    return tuple(map(list, zip(*[
        simulate_scenario(model, mode, scenario) 
        for scenario in tqdm(scenarios, total=len(scenarios), desc=f"Simulation {str(model):40} {mode.__name__:15}")
    ])))

def evaluate_scenario(scenario, consequence):
    environment = Environment([DeviceDraft.model_validate(draft) for draft in literal_eval(scenario.devices)])
    criteria = Criteria.model_validate(literal_eval(scenario.criteria))
    action_calls = [Action.model_validate(action) for action in json.loads(consequence)]
    return environment.evaluate(criteria, action_calls=action_calls)

def evaluate_scenarios(scenarios, consequences):
    assert len(scenarios) == len(consequences)
    return [evaluate_scenario(scenario, consequence) for scenario, consequence in zip(scenarios, consequences)]

def simulation(code, dataset_file, models, modes, head=None, rerun_modes=[]):
    dataset_df = pd.read_csv(f"{DATASET_DIR}/{dataset_file}").dropna()
    dataset_df = dataset_df[:head if head else len(dataset_df)]
    result_path = f"{RESULT_DIR}/{code}/{dataset_file.replace('dataset', 'result')}"
    result_df = pd.read_csv(result_path) if os.path.exists(result_path) else pd.DataFrame()

    scenarios = list(dataset_df.itertuples())
    assert "ID" not in result_df or result_df["ID"].tolist() == dataset_df["ID"].tolist()
    result_df["ID"] = dataset_df["ID"].tolist()
    
    for model in models:
        pending = [mode for mode in modes
                   if get_column_name("CONSEQUENCES", model, mode.__name__) not in result_df
                   or mode.__name__ in rerun_modes]
        if pending and not model.setup():
            continue
        for mode in modes:
            column = get_column_name("CONSEQUENCES", model, mode.__name__)
            if mode in pending:
                logs, times, tokens, consequences = simulate_scenarios(model, mode, scenarios)
                for key, values in (("LOGS", logs), ("TIME", times), ("TOKEN", tokens)):
                    result_df[get_column_name(key, model, mode.__name__)] = values
                result_df[column] = [json.dumps(actions, ensure_ascii=False) for actions in consequences]
                save_dataframe(result_df, path=result_path)
            evaluations = evaluate_scenarios(scenarios, result_df[column])
            column = get_column_name("EVALUATION", model, mode.__name__)
            result_df[column] = [json.dumps(value) for value in evaluations]
            result_df = result_df.copy()
            save_dataframe(result_df, path=result_path)
        if pending:
            model.wrapup()
    
    save_dataframe(result_df, path=result_path, ensure=True)
    return result_path

if __name__ == "__main__":
    modes = [Centralized, RAG, Sasha, LLMind, LANCE]
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument("--debug", action="store_true")
    argument_parser.add_argument("--code", type=str, required=False, default="")
    argument_parser.add_argument("--edge", action="store_true")
    argument_parser.add_argument("--resume", action="store_true")
    argument_parser.add_argument("--rerun", nargs="+", choices=[mode.__name__ for mode in modes], default=[])
    argument_parser.add_argument("--head", type=int, required=False, default=None)
    args = argument_parser.parse_args()
    set_debug(args.debug)

    # Get experiment code
    remove_empty_results()
    code = args.code if args.code else get_last_result() if args.resume else datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    print(code)
    if not os.path.exists(f"{RESULT_DIR}/{code}"):
        os.mkdir(f"{RESULT_DIR}/{code}")

    representative_model = Model("qwen3.5:4b-q4_K_M", reasoning=False)

    configurations = [
        ("dataset_D0_M0.csv", modes, [representative_model]),
        ("dataset_D5_M0.csv", modes, [representative_model]),
        ("dataset_D10_M0.csv", modes, [representative_model]),
        ("dataset_D15_M0.csv", modes, [representative_model]),
        ("dataset_D20_M0.csv", modes, [representative_model]),
        ("dataset_D5_M0.csv", modes, [
            # Micro-size <=2b
            Model("qwen3.5:0.8b-q8_0", reasoning=False),
            Model("llama3.2:1b-instruct-q4_K_M"),
            Model("qwen3.5:2b-q4_K_M", reasoning=False),
            # Tiny-size <=4b
            Model("gemma4:e2b-it-q4_K_M", reasoning=False),
            Model("llama3.2:3b-instruct-q4_K_M"),
            Model("ministral-3:3b-instruct-2512-q4_K_M", reasoning=False),
            Model("granite4.2:3b-q4_K_M", reasoning=False),
            Model("qwen3.5:4b-q4_K_M", reasoning=False),
            Model("nemotron-3-nano:4b-q8_0", reasoning=False),
            # Small-size <=8b
            Model("gemma4:e4b-it-q4_K_M", reasoning=False),
            Model("granite4.2:8b-q4_K_M", reasoning=False),
            Model("ministral-3:8b-instruct-2512-q4_K_M", reasoning=False),
            Model("rnj-1:8b-instruct-q4_K_M"),
            Model("qwen3.5:9b-q4_K_M", reasoning=False),
            Model("ornith:9b-q4_K_M", reasoning=False),
        ]),
    ]

    try:
        for dataset_file, modes, models in configurations:
            if DATASET_FILENAME_PATTERN.match(dataset_file) and os.path.exists(f"{DATASET_DIR}/{dataset_file}"):
                print(dataset_file)
                simulation(code, dataset_file, models, modes, args.head, args.rerun)
    except KeyboardInterrupt:
        pass
