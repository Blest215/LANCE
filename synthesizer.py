from settings import *
from model import Model
from schema import *
from simulator import Simulator
from device_synthesizer import get_choices, get_details, device_api

SCENE_PROMPT = ChatPromptTemplate.from_template(
"""Create a realistic pure-control scene using exact catalog device types and cluster IDs.
Include only devices needed for the command and its dependencies, preserving the full survey intent.
Not every surveyed device is required.

[Catalog] {catalog}
[Space] {space}
[Command] {user_command}
[Expected] {expected_behavior}
""")

# ADDITIONAL_SCENE_PROMPT = ChatPromptTemplate.from_template(
# """Add {count} devices suited to existing rooms and unrelated to the command.
# Use unused surveyed devices first; introduce other devices only if none remain.

# [Catalog] {catalog}
# [Scene] {scene}
# [Space] {space}
# [Devices] {devices}
# [Command] {user_command}
# [Expected] {expected_behavior}
# """)

EFFECT_PROMPT = ChatPromptTemplate.from_template(
"""Convert the action into exact immediate property effects for all valid argument values, independently of initial state.
Use only supplied property and argument names, compatible types and raw Matter units.
Use set, add or subtract with supplied argument_name or action-defined constants; toggle only boolean properties.
Never use argument defaults as constants.
No timing, conditions, simulated measurements or unsupported transformations.

[Properties] {properties}
[Action] {action}
""")

TASK_PROMPT = ChatPromptTemplate.from_template(
"""Create a pure-control Task preserving the full survey intent and explicit device/room/content targets.
Use exact scene names and valid argument values. Argument keys are property_name values.
Add no unrelated goals.
Goals must be achieved by expected_actions and not all satisfied initially.

[Command] {user_command}
[Expected] {expected_behavior}
[Scene] {scene}
""")

class ValidationResult(BaseModel):
    valid: bool
    reason: str

VALIDATION_PROMPT = ChatPromptTemplate.from_template(
"""Check that utterance, actions and goals preserve the full survey intent using only scene APIs.
Reject omissions, substitutions, approximations, unrelated goals or automation.
Explicit room/content/temperature targets must be fulfilled; generic playback does not select requested content.
Not every surveyed device is required. Return valid and reason.

[Space] {space}
[Devices] {devices}
[Command] {user_command}
[Expected] {expected_behavior}
[Scene] {scene}
[Task] {task}
""")

def generate_device(device: DeviceSpecMatter, index: int):
    api = device_api(get_details(device.device_type, device.clusters))
    properties = [PropertySpec.model_validate(property) for property in api["properties"].values()]
    property_names = [property_spec.property_name for property_spec in properties]

    actions = []
    for action in api["actions"].values():
        if "effects" in action:
            actions.append(ActionSpec.model_validate(action))
            continue
        while True:
            try:
                print(action)
                effect_generator = effect_generator_arguments if action["arguments"] else effect_generator_not_arguments
                effect = effect_generator.invoke({"properties": properties, "action": action})
                print(effect)
                for effect_spec in effect.effects:
                    if effect_spec.target_property not in property_names:
                        raise ValueError("Invalid property name")
                actions.append(ActionSpec.model_validate(action | {"effects": effect.effects}))
                break
            except Exception as e:
                debug(e)
    return DeviceSpec.model_validate({
        "device_id": f"d{index}",
        "device_name": f"{device.room_id} {device.device_type} {index + 1}",
        "device_type": device.device_type,
        "room_id": device.room_id,
        "properties": properties,
        "actions": actions,
    })

def generate_scenario(answer_dict: dict, device_count=5):
    if device_count < 1:
        raise ValueError("device_count must be positive")
    debug(answer_dict)

    while True:
        try:
            scene_spec = scene_generator.invoke(answer_dict)
            if len(scene_spec.devices) > device_count:
                raise ValueError("Too many required devices")
            devices = [generate_device(device_spec, i) for i, device_spec in enumerate(scene_spec.devices)]
            scene = {"rooms": scene_spec.rooms, "devices": devices}
            debug(scene)

            task = task_generator.invoke(answer_dict | {"scene": scene})
            debug(task)

            simulator = Simulator(scene, None)

            if simulator.evaluate(task) >= 1:
                raise ValueError()
            for expected_action in task.expected_actions:
                simulator.call(**expected_action.model_dump())
            if simulator.evaluate(task) < 1:
                raise ValueError()
            # validation_result = validator.invoke(answer_dict | {
            #     "scene": scene, "task": task.model_dump()
            # })
            # if not validation_result.valid:
            #     debug(validation_result.reason)
            #     raise ValueError(validation_result.reason)

            break

        except Exception as e:
            debug(e)

    # while True:
    #     try:
    #         if count := device_count - len(devices):
    #             used_types = {device.device_type for device in scene_spec.devices}
    #             used_clusters = {cluster for device in scene_spec.devices for cluster in device.clusters}
    #             choices = {name: clusters for name, clusters in device_composer.choices().items()
    #                 if name not in used_types and not any(cluster["cluster_id"] in used_clusters and
    #                     any(rule["kind"] == "mandatoryConform" for rule in cluster["conformance"])
    #                     for cluster in clusters)}
    #             additional_generator = create_generator(ADDITIONAL_SCENE_PROMPT.partial(catalog=choices),
    #                 SceneSpec.with_choices(choices, device_count=count), model)
    #             additional_scene = additional_generator.invoke(answer_dict | {
    #                 "scene": {"rooms": scene_spec.rooms, "devices": scene_spec.devices}, "count": count})
    #             if {device.room_id for device in additional_scene.devices} - {room.room_id for room in scene_spec.rooms}:
    #                 raise ValueError("Additional devices must use existing rooms")
    #             scene = scene | {"devices": devices + generate_devices(additional_scene,
    #                 answer_dict | {"user_command": "", "expected_behavior": ""}, start_index=len(devices))}

    #             break

    #     except Exception as e:
    #         debug(e)
        
    return {"scene": scene, "task": task.model_dump()}

def rendering(scene_spec, task):
    # TODO
    return None

if __name__ == "__main__":
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument("--debug", action="store_true")
    argument_parser.add_argument("--model", type=str, required=False, default="gemma4:12b-it-q4_K_M", help="LLM to use")
    argument_parser.add_argument("--devices", type=int, default=5)
    args = argument_parser.parse_args()
    set_debug(args.debug)

    choices = get_choices()

    path = f"{DATASET_DIR}/dataset_D{args.devices}_M0.csv"
    model = Model(model=args.model, reasoning=False, temperature=None, context=32768)
    scene_generator = create_generator(SCENE_PROMPT.partial(catalog=choices), SceneSpec.with_choices(choices), model)
    effect_generator_not_arguments = create_generator(EFFECT_PROMPT, NotFromArgumentEffects, model)
    effect_generator_arguments = create_generator(EFFECT_PROMPT, FromArgumentEffects, model)
    task_generator = create_generator(TASK_PROMPT, Task, model)
    validator = create_generator(VALIDATION_PROMPT, ValidationResult, model)

    survey_df = pd.read_csv(SURVEY_PATH)
    survey_df = survey_df[survey_df["class"] == "Control"]
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
