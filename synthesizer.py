from settings import *
from model import Model
from schema import *
from device_synthesizer import get_profiles, complete_profile_device
from simulator import Simulator

SCENE_PROMPT = ChatPromptTemplate.from_template(
"""Create realistic rooms and DeviceDrafts by selecting profile_id from the catalog.
Include only independently controlled devices needed for the full intent, covering every requested room. Equipment sharing one controlled plug needs no separate controls.
Follow profile capabilities, not device names: a cooling-only AC is not a heater. Speaker On/Off is mute/unmute, not power.
DeviceDraft.options lists user-specific information: plain content names (include artist/provider), robot cleaning areas, appliance modes or lighting presets. Preserve names or descriptive aliases such as 'my favorite Spotify playlist'; use [] otherwise. Do not list platform brands alone or invent preset capabilities.
Pure control only: reject schedules, conditions, queries, shopping and pairing; ordinary assistant acknowledgements are not device requirements. Immediate preset activation is not scheduling.
Content App supports content launch/playback, not shuffle, playlist edits or content recognition.
Set solvable=false if any required function is unsupported; do not silently drop it. Unspecified ordinary control values may be concretized consistently in the task.
Always explain the device/profile choices and any unsupported requirements in reason.

[Catalog] {catalog}
[Space] {space}
[Command] {user_command}
[Expected] {expected_behavior}
""")

TASK_PROMPT = ChatPromptTemplate.from_template(
"""Create a pure-control Task preserving the full survey intent and explicit device/room/content targets.
Cover every requested target with only necessary actions. Preserve explicit values; concretize unspecified ordinary values consistently and make those choices explicit in user_utterance.
Use declared control_id and named arguments with their exact types, required fields and configured choices. Command scalars are direct values, never wrapped in a value object; only property writes use arguments.value.
Select named content via its configured enum_labels/URL binding or matching search fields; a provider name alone is not content. Play resumes playback; presets use RecallScene, not brightness levels or startup settings.
Respect units and enum meanings: SetpointRaiseLower.Amount uses 0.1 Celsius (increase 2 Celsius = 20); thermostat setpoints use 0.01 Celsius. Resolve unspecified temperature units plausibly and state the unit. Use relative commands for relative requests, not invented initial states.
Return user_utterance and expected_actions, without automation or assistant acknowledgement actions.

[Scene] {scene}
[Command] {user_command}
[Expected] {expected_behavior}
""")

class ValidationResult(BaseModel):
    valid: bool
    reason: str

VALIDATION_PROMPT = ChatPromptTemplate.from_template(
"""Check user_utterance and expected_actions against the survey and declared scene APIs.
Reject missing targets/functions, unrelated actions, unsupported substitutions, schedules, conditions or queries. Not every surveyed device is needed; ordinary assistant acknowledgements need no action.
Check control IDs, argument types, required fields, choices, units and enum meanings. Scalars must not be value objects. Heating requires heating capability; presets are not startup settings or brightness numbers. A 2 Celsius relative change needs SetpointRaiseLower.Amount=20.
Accept reasonable concretization of unspecified ordinary values when explicit in user_utterance; do not demand an original numeric value for 'dim'. Preserve all explicit targets and relative changes.
Configured enum_labels and synthetic URLs are valid dataset bindings: LaunchURL can select the named content without LaunchContent or an extra Play. Bare Play does not identify named content. Do not demand live provider access or prefer one equivalent API arbitrarily.
Reject only concrete mismatches. Return valid and a brief reason identifying the unmet requirement or invalid action.

Survey Response:
[Space] {space}
[Command] {user_command}
[Expected] {expected_behavior}

Generated:
[Scene] {scene}
[Task] {task}
""")

def generate_device(device_spec: DeviceDraft, index: int) -> Device:
    return complete_profile_device(device_spec, index)

def generate_scenario(answer_dict: dict, device_count=5):
    if device_count < 1:
        raise ValueError("device_count must be positive")
    debug(answer_dict)

    while True:
        try:
            scene_spec = scene_generator.invoke(answer_dict)
            if not scene_spec.solvable:
                return {"model": model.name, "scene": scene_spec.reason}
            
            if len(scene_spec.devices) > device_count:
                return {"model": model.name, "scene": "Too many devices are required"}

            devices = [generate_device(device, index) for index, device in enumerate(scene_spec.devices)]
            scene = Scene.model_validate({
                "rooms": scene_spec.rooms,
                "devices": devices
            })
            debug(scene)

            simulator = Simulator(scene)
            rendered_scene = simulator.task_scene()
            task = task_generator.invoke(answer_dict | {"scene": rendered_scene})
            debug(task)
            for action in task.expected_actions:
                simulator.validate_action(action)

            validation_result = validator.invoke(answer_dict | {"scene": rendered_scene, "task": task})
            if not validation_result.valid:
                return {"model": model.name, "scene": validation_result.reason}

            return {"model": model.name, "scene": scene.model_dump(), "task": task.model_dump()}

        except Exception as e:
            debug(e)

def rendering(scene_spec, task):
    # TODO: Matter, W3C TD, SmartThings.
    return None

def validate_scenario(scene, task):
    # TODO: Validate rendered interfaces and task fulfillment.
    return None

if __name__ == "__main__":
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument("--debug", action="store_true")
    argument_parser.add_argument("--model", type=str, required=False, default="gemma4:12b-it-q4_K_M", help="LLM to use")
    argument_parser.add_argument("--devices", type=int, default=5)
    args = argument_parser.parse_args()
    set_debug(args.debug)

    catalog = get_profiles()
    path = f"{DATASET_DIR}/dataset_D{args.devices}_M0.csv"
    model = Model(model=args.model, reasoning=False, temperature=None, context=32768)
    scene_generator = create_generator(SCENE_PROMPT.partial(catalog=catalog), SceneSpec, model)
    task_generator = create_generator(TASK_PROMPT, Task, model)

    validator = create_generator(VALIDATION_PROMPT, ValidationResult, model)

    survey_df = pd.read_csv(SURVEY_PATH)
    df = pd.read_csv(path) if os.path.exists(path) else pd.DataFrame()
    synthesize_df = survey_df[len(df):]

    try:
        for answer in tqdm(synthesize_df.itertuples(index=False), total=len(synthesize_df), desc=f"Synthesize ({model.name})"):
            scenario = generate_scenario(answer._asdict(), device_count=args.devices)
            df = pd.concat([df, pd.DataFrame([scenario])], ignore_index=True)
            save_dataframe(df, path, ensure=False)
        save_dataframe(df, path, ensure=True)
    except KeyboardInterrupt:
        pass
