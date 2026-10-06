from settings import *
from model import Model
from schema import *
from simulator import *

SCENE_PROMPT = ChatPromptTemplate.from_template(
"""Convert the below survey response into a realistic scene.

Where were you? {space}
What devices were in the space? {devices}""")

TASK_PROMPT = ChatPromptTemplate.from_template(
"""Convert the below survey response into a realistic utterance and evaluation goal in the scene.

What did you command the AI assistant? {user_command}
What behavior did you expect from the AI assistant and devices? {expected_behavior}

[Scene] {scene}""")

class ValidationResult(BaseModel):
    valid: bool
    reason: str

VALIDATION_PROMPT = ChatPromptTemplate.from_template(
"""Validate whether the generated task is consistent with the survey response, using the generated scene as context.

Validation criteria:
- The scene does not need to include every device mentioned in the survey response.
- The device properties and actions need to be realistic.
- The task's user_utterance must preserve the full intent of the survey's user_command and expected_behavior.
- The task's expected_actions and goal_states must cover all requested operations and expected outcomes, without omitting subrequests, contradicting the survey response, or introducing unrelated requirements.

[Survey response]
Where were you? {space}
What devices were in the space? {devices}
What did you command the AI assistant? {user_command}
What behavior did you expect from the AI assistant and devices? {expected_behavior}

[Generated scenario]
Scene: {scene}
Task: {task}
""")

def generate_scenario(answer_dict: dict):
    debug(answer_dict)
    while True:
        try:
            debug("Generating scene")
            scene_spec = scene_generator.invoke(answer_dict)
            
            debug("Generating task")
            task = task_generator.invoke(answer_dict | {"scene": scene_spec})

            debug("Validating")
            if not validate_task(answer_dict, scene_spec, task):
                continue

            # rendering(scene_spec, task)

            return {"scene": scene_spec.model_dump(), "task": task.model_dump()}

        except Exception as e:
            debug(e)

def validate_task(answer_dict: dict, scene_spec: SceneSpec, task: Task) -> bool:
    simulator = Simulator(scene_spec.model_dump(), None)

    try:
        if simulator.evaluate(task) >= 1:
            return False
        
        for expected_action in task.expected_actions:
            simulator.call(**expected_action.model_dump())

        if simulator.evaluate(task) < 1:
            return False

        validation_result = validator.invoke(answer_dict | {"scene": scene_spec, "task": task})
        if not validation_result.valid:
            debug(validation_result.reason)
            return False
    except Exception as e:
        debug(e)
        return False
    
    return True

def rendering(scene_spec, task):
    # TODO
    return None

if __name__ == "__main__":
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument("--debug", action="store_true")
    argument_parser.add_argument("--model", type=str, required=False, default="gemma4:12b-it-q4_K_M", help="LLM to use")
    args = argument_parser.parse_args()
    set_debug(args.debug)

    path = f"{DATASET_DIR}/dataset_D5_M0.csv"

    # TODO models
    model = Model(model=args.model, reasoning=False, temperature=None)
    scene_generator = create_generator(SCENE_PROMPT, SceneSpec, model)
    task_generator = create_generator(TASK_PROMPT, Task, model)
    validator = create_generator(VALIDATION_PROMPT, ValidationResult, model)

    survey_df = pd.read_csv(SURVEY_PATH)
    survey_df = survey_df[survey_df["class"] == "Control"]
    df = pd.read_csv(path) if os.path.exists(path) else pd.DataFrame()

    synthesize_df = survey_df[len(df):] if len(survey_df) > len(df) else pd.DataFrame()

    try:
        synthesize_df = survey_df[len(df):]
        for answer in tqdm(synthesize_df.itertuples(index=False), total=len(synthesize_df), desc=f"Synthesize ({model.name})"):
            scenario = generate_scenario(answer._asdict())

            df = pd.concat([df, pd.DataFrame([scenario])], ignore_index=True)
            save_dataframe(df, path, ensure=False)
        save_dataframe(df, path, ensure=True)

        # TODO scale

        # TODO mutation

    except KeyboardInterrupt:
        pass
