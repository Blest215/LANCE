from model import Model
from settings import *
from environment import *
from LANCE import *
from baseline import *
from ast import literal_eval
from functools import partial

DECISION_MODELS = ["d1-omni:600m-q8_0", "tev1:0.8b-q8_0", "tev1:4b-q4_K_M", "nimble-v3:9b-q4_K_M"]
NOUL_THRESHOLDS = [i / 10 for i in range(1, 10)]
LANCE_SETTINGS_RESULT = "result_D20_M0_LANCE_settings.csv"

def simulate_scenario(model: Model, mode, scenario):
    environment = Environment([DeviceDraft.model_validate(draft) for draft in literal_eval(scenario.devices)])
    user = mode(model)
    log = user.main(environment, scenario.utterance)
    if isinstance(user, LANCE) and not isinstance(user, LANCE_no_decision):
        log["configuration"] = {"decision_model": user.screener.model, "noul_threshold": user.noul_threshold}
    return log, user.time_log, user.token_log, [action.model_dump() for action in environment.action_calls]

def simulate_scenarios(model: Model, mode, scenarios):
    return tuple(map(list, zip(*[
        simulate_scenario(model, mode, scenario) 
        for scenario in tqdm(scenarios, total=len(scenarios), desc=f"Simulation {str(model):40} {mode.__name__:20}")
    ])))

def evaluate_scenario(scenario, consequence):
    environment = Environment([DeviceDraft.model_validate(draft) for draft in literal_eval(scenario.devices)])
    criteria = Criteria.model_validate(literal_eval(scenario.criteria))
    action_calls = [Action.model_validate(action) for action in json.loads(consequence)]
    return environment.evaluate(criteria, action_calls=action_calls)

def evaluate_scenarios(scenarios, consequences):
    assert len(scenarios) == len(consequences)
    return [evaluate_scenario(scenario, consequence) for scenario, consequence in zip(scenarios, consequences)]

def simulation(code, dataset_file, models: List[Model], modes, head=None, rerun_modes=[], result_file=None):
    dataset_df = pd.read_csv(f"{DATASET_DIR}/{dataset_file}").dropna()
    dataset_df = dataset_df[:head if head else len(dataset_df)]
    result_path = f"{RESULT_DIR}/{code}/{result_file or dataset_file.replace('dataset', 'result')}"
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

def lance_settings_sweep(code, models: List[Model], head=None, rerun=False):
    for decision_model_name in DECISION_MODELS:
        decision_model = Model(decision_model_name)
        modes = []        
        for threshold in NOUL_THRESHOLDS:
            mode = partial(LANCE, decision_model=decision_model_name, noul_threshold=threshold)
            mode.__name__ = f"LANCE_{decision_model}_noul_{threshold:.1f}".replace(".", "_")
            modes.append(mode)
        if not decision_model.setup():
            continue
        simulation(code, "dataset_D20_M0.csv", models, modes, head,
                rerun_modes=[mode.__name__ for mode in modes] if rerun else [],
                result_file=LANCE_SETTINGS_RESULT)
        decision_model.wrapup()

if __name__ == "__main__":
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument("--debug", action="store_true")
    argument_parser.add_argument("--code", type=str, required=False, default="")
    argument_parser.add_argument("--edge", action="store_true")
    argument_parser.add_argument("--resume", action="store_true")
    argument_parser.add_argument("--rerun", nargs="+", default=[])
    argument_parser.add_argument("--head", type=int, required=False, default=None)
    argument_parser.add_argument("--lance-sweep", action="store_true")
    argument_parser.add_argument("--models", action="store_true")
    argument_parser.add_argument("--ablation", action="store_true")
    args = argument_parser.parse_args()
    set_debug(args.debug)

    modes = [Centralized, RAG, Sasha, LLMind, LANCE] if not args.edge else [LANCE_no_decision]

    # Get experiment code
    remove_empty_results()
    code = args.code if args.code else get_last_result() if args.resume else datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    print(code)
    if not os.path.exists(f"{RESULT_DIR}/{code}"):
        os.mkdir(f"{RESULT_DIR}/{code}")

    representative_models = [
        Model("gemma4:e2b-it-q4_K_M", reasoning=False),
        Model("qwen3.5:4b-q4_K_M", reasoning=False),
        Model("ornith-1.5:9b", reasoning=False),
    ] if not args.edge else [Model("gemma4:e2b-it-q4_K_M", reasoning=False)]

    try:
        configurations = [(
            ["dataset_D0_M0.csv", "dataset_D5_M0.csv", "dataset_D10_M0.csv", "dataset_D15_M0.csv", "dataset_D20_M0.csv"],
            modes,
            representative_models
        )]
        if args.models:
            configurations.append((
                ["dataset_D5_M0.csv"], modes, [
                    # Micro-size <=2b
                    Model("qwen3.5:0.8b-q8_0", reasoning=False),
                    Model("functiongemma:270m-it-q8_0"),
                    Model("qwen3.5:2b-q4_K_M", reasoning=False),
                    # Tiny-size <=4b
                    Model("gemma4:e2b-it-q4_K_M", reasoning=False),
                    Model("llama3.2:3b-instruct-q4_K_M"),
                    Model("ministral-3:3b-instruct-2512-q4_K_M", reasoning=False),
                    Model("granite4.2:3b-q4_K_M", reasoning=False),
                    Model("qwen3.5:4b-q4_K_M", reasoning=False),
                    Model("nemotron-3-nano:4b-q4_K_M", reasoning=False),
                    # Small-size <=8b
                    Model("gemma4:e4b-it-q4_K_M", reasoning=False),
                    Model("granite4.2:8b-q4_K_M", reasoning=False),
                    Model("ministral-3:8b-instruct-2512-q4_K_M", reasoning=False),
                    Model("qwen3.5:9b-q4_K_M", reasoning=False),
                    Model("ornith-1.5:9b", reasoning=False),
                ]
            ))
        if args.ablation:
            configurations.append((
                ["dataset_D0_M0.csv", "dataset_D5_M0.csv", "dataset_D10_M0.csv", "dataset_D15_M0.csv", "dataset_D20_M0.csv"],
                [LANCE_no_decision, LANCE_no_discovery, LANCE_no_separation, LANCE_no_instruction],
                representative_models
            ))

        for dataset_files, modes, models in configurations:
            for dataset_file in dataset_files:
                print(dataset_file)
                simulation(code, dataset_file, models, modes, args.head, args.rerun)

        if args.lance_sweep:
            lance_settings_sweep(code, representative_models, args.head, "LANCE" in args.rerun)
    except KeyboardInterrupt:
        pass
