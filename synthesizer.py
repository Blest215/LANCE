import random
import json
from urllib.parse import quote
from copy import deepcopy

from time import perf_counter

from settings import *
from model import Model
from schema import *
from profiles import PROFILES
from simulator import Simulator

SCENE_PROMPT = ChatPromptTemplate.from_template(
"""Create realistic rooms and devices by selecting profile_id from the catalog, and explain the reason within 100 words.
The devices MUST include the profiles needed for the user's full intent.
Use options only for user-specific content, cleaning areas, appliance modes or lighting presets supported by the profile.
The solvable flag MUST be false if the user's command cannot be fulfilled by the device profiles in the catalog.
The solvable flag MUST be false if the user's command is about scheduled, conditioned, or informational commands.

[Catalog] {profiles}
[Space] {space}
[Command] {user_command}
[Expected] {expected_behavior}
""")

TASK_PROMPT = ChatPromptTemplate.from_template(
"""Create a device-control task preserving the full survey intent.
The user_utterance MUST be natural, self-contained, and unambiguous utterance that the user would say to the AI agent.
The expected_actions MUST cover every goal stated in the user_utterance.

[Scene] {scene}
[Command] {user_command}
[Expected] {expected_behavior}
""")

class ValidationResult(BaseModel):
    valid: bool
    reason: str

VALIDATION_PROMPT = ChatPromptTemplate.from_template(
"""Validate the generated scenario, and explain the reason within 100 words.
The user_utterance MUST be a natural, self-contained, and unambiguous device-control request with clear targets and values.
The expected_actions MUST match its full meaning with the user_utterance: rooms, devices, actions, and arguments.
The devices MUST be realistic products with plausible capabilities, names and room placements.

[Scene] {scene}
[Task] {task}
""")

def get_profiles():
    return json.dumps({name: profile["description"] for name, profile in PROFILES.items()}, ensure_ascii=False)

def generate_device(draft: DeviceDraft, protocol=None):
    profile = PROFILES[draft.profile_id]
    protocol = protocol or random.choice(tuple(profile["devices"]))
    template = profile["devices"][protocol]
    data = deepcopy(template)
    data.update(draft.model_dump(include={"device_id", "device_name", "room_id", "profile_id"}))
    if protocol == "W3C":
        data["td"]["title"] = draft.device_name
    if draft.options:
        for path, kind in profile["options"][protocol]:
            field = data
            for key in path:
                field = field[key]
            if kind == "content":
                values = [name if name.startswith(("https://", "http://")) else
                          f"https://media.example.test/{quote(draft.device_id, safe='')}/{index}"
                          for index, name in enumerate(draft.options)]
            else:
                values = list(range(len(draft.options)))
                if "maximum" in field and values[-1] > field["maximum"]:
                    raise ValueError("Too many options for the catalog argument domain")
            enum, labels = ("enum_values", "enum_labels") if protocol == "Matter" else ("enum", "x-enumLabels")
            field[enum] = values
            field[labels] = {str(value): name for value, name in zip(values, draft.options)}
    return {"Matter": MatterDevice, "W3C": W3CDevice, "SmartThings": SmartThingsDevice}[protocol].model_validate(data)

def generate_scenario(answer_dict: dict):
    start = perf_counter()
    debug(answer_dict)

    while True:
        try:
            scene = None
            task = None

            scene_spec = scene_generator.invoke(answer_dict)
            reason = scene_spec.reason
            if not scene_spec.solvable:
                break
            
            if len(scene_spec.devices) > 5:
                reason = "Too many devices are required"
                break

            devices = [generate_device(device) for device in scene_spec.devices]
            scene = Scene.model_validate({
                "rooms": scene_spec.rooms,
                "devices": devices
            })
            debug(scene)

            simulator = Simulator(scene)
            rendered_scene = simulator.render()
            task = task_generator.invoke(answer_dict | {"scene": rendered_scene})
            debug(task)
            for action in task.expected_actions:
                simulator.validate_action(action)

            validation_result = validator.invoke({"scene": rendered_scene, "task": task})
            if not validation_result.valid:
                reason = validation_result.reason
                break

            scene = scene.model_dump()
            task = task.model_dump()
            break

        except Exception as e:
            debug(e)

    # TODO scale

    # TODO mutation

    debug(reason)

    return {"model": model.name, "time": perf_counter() - start, "reason": reason, "scene": scene, "task": task}

if __name__ == "__main__":
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument("--debug", action="store_true")
    argument_parser.add_argument("--model", type=str, required=False, default="gemma4:12b-it-q4_K_M", help="LLM to use")
    args = argument_parser.parse_args()
    set_debug(args.debug)

    profiles = get_profiles()
    debug(profiles)
    path = f"{DATASET_DIR}/dataset_D5_M0.csv"
    model = Model(model=args.model, reasoning=False, temperature=None, context=32768)
    scene_generator = create_generator(SCENE_PROMPT.partial(profiles=profiles), SceneSpec, model)
    task_generator = create_generator(TASK_PROMPT, Task, model)

    validator = create_generator(VALIDATION_PROMPT, ValidationResult, model)

    survey_df = pd.read_csv(SURVEY_PATH)
    df = pd.read_csv(path) if os.path.exists(path) else pd.DataFrame()
    synthesize_df = survey_df[len(df):]

    try:
        model.setup()
        for answer in tqdm(synthesize_df.itertuples(index=False), total=len(synthesize_df), desc=f"Synthesize ({model.name})"):
            scenario = generate_scenario(answer._asdict())
            df = pd.concat([df, pd.DataFrame([scenario])], ignore_index=True)
            save_dataframe(df, path, ensure=False)
        save_dataframe(df, path, ensure=True)
        model.wrapup()
    except KeyboardInterrupt:
        pass
