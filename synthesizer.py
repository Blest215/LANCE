from settings import *
from model import Model
from schema import *
from prompts import *
from simulator import *

def generate_scenario(answer_dict: dict, num_devices: int):
    while True:
        try:
            scene_spec = scene_generator.invoke(answer_dict | {"num_devices": num_devices})
            if len(scene_spec.devices) != num_devices:
                continue

            task = task_generator.invoke(answer_dict | {"scene": scene_spec})

            if not validate_task(scene_spec, task):
                continue

            rendering(scene_spec, task)

            return {"scene": scene_spec.model_dump(), "task": task.model_dump()}

        except Exception as e:
            debug(e)        

def validate_task(scene_spec: SceneSpec, task: Task) -> bool:
    simulator = Simulator(scene_spec.model_dump(), None)
    for goal_state in task.goal_states:
        if goal_state.entity_id not in simulator.agents:
            return False
        if goal_state.attribute not in simulator.agents[goal_state.entity_id].properties:
            return False
    return True

def rendering(scene_spec, task):
    return None

if __name__ == "__main__":
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument("--debug", action="store_true")
    argument_parser.add_argument("--model", type=str, required=False, default="gemma4:12b-it-q4_K_M", help="LLM to use")
    argument_parser.add_argument("--devices", type=int, required=False, default=5, help="Number of devices for each scenario")
    argument_parser.add_argument("--mutation", action="store_true")
    argument_parser.add_argument("--scale", action="store_true", help="Scale from less devices dataset")
    args = argument_parser.parse_args()
    set_debug(args.debug)

    path = f"{DATASET_DIR}/dataset_D{args.devices}_M0.csv"

    # TODO models
    model = Model(model=args.model, reasoning=False, temperature=0.7)
    scene_generator = create_generator(SCENE_PROMPT, SceneSpec, model)
    task_generator = create_generator(TASK_PROMPT, Task, model)

    survey_df = pd.read_csv(SURVEY_PATH)
    survey_df = survey_df[survey_df["class"] == "Control"]
    df = pd.read_csv(path) if os.path.exists(path) else pd.DataFrame()

    synthesize_df = survey_df[len(df):] if len(survey_df) > len(df) else pd.DataFrame()

    try:
        synthesize_df = survey_df[len(df):]
        for answer in tqdm(synthesize_df.itertuples(index=False), total=len(synthesize_df), desc=f"Synthesize ({model.name})"):
            scenario = generate_scenario(answer._asdict(), args.devices)

            df = pd.concat([df, pd.DataFrame([scenario])], ignore_index=True)
            save_dataframe(df, path, ensure=False)
        save_dataframe(df, path, ensure=True)

        # TODO scale

        # TODO mutation

    except KeyboardInterrupt:
        pass
