import json
import random
from copy import deepcopy
from typing import get_args

from settings import *
from model import Model
from schema import *
from profiles import PROFILES
from environment import Environment

class ValidationResult(BaseModel):
    valid: bool
    reason: str

SCENE_PROMPT = ChatPromptTemplate.from_template(
"""Describe every survey goal and select needed catalog profiles with unique device_ids and realistic rooms.
Set solvable=false if profiles cannot fulfill the goals.
Put requested content, providers, cleaning areas, channels, inputs and apps in device resources.
Preserve channel numbers; do not invent resource IDs, URLs, presets or aliases.

[Catalog] {profiles}
[Space] {space}
[Command] {user_command}
[Expected] {expected_behavior}
""")

TASK_PROMPT = ChatPromptTemplate.from_template(
"""Fulfill every described goal using listed device_ids, action_names and arguments within their options and ranges.

[Devices] {devices}
[Description] {description}
""")

UTTERANCE_PROMPT = ChatPromptTemplate.from_template(
"""You are a smart-home user.
Express the task as a natural, self-contained smart-home command with explicit rooms, targets and values.

[Description] {description}
[Devices] {devices}
[Task] {task}
""")

VALIDATION_PROMPT = ChatPromptTemplate.from_template(
"""Validate the scenario; explain within 100 words.
Devices, utterance and expected actions must preserve all survey goals, targets and values.
The utterance must be natural, self-contained, unambiguous and semantically match the expected actions.

[Space] {space}
[Command] {user_command}
[Expected] {expected_behavior}

[Devices] {devices}
[Task] {task}
[Devices] {devices}
[Utterance] {utterance}
""")

DEVICE_VALIDATION_PROMPT = ChatPromptTemplate.from_template(
"""Check whether the profile's device is realistically placed in the room; explain briefly.

[Room] {room}
[Profile] {profile}
""")


def generate_scenario(answer_dict: dict):
    debug(answer_dict)
    count = 0

    while count < MAX_RETRY:
        try:
            count += 1

            scene = scene_generator.invoke(answer_dict)
            debug(scene)
            if not scene.solvable:
                return

            environment = Environment(scene.devices, protocol="Matter")
            rendered_devices, action_lookup = environment.render()
            debug(rendered_devices)

            draft = task_generator.invoke({"devices": rendered_devices, "description": scene.description})
            task = Task(expected_actions=[environment.assemble_action(Action(
                device_id=action.device_id,
                action_name=action_lookup[action.device_id][action.action_name]["control_id"],
                arguments=action.arguments,
            )) for action in draft.expected_actions])
            debug(task)

            for action in task.expected_actions:
                environment.execute_action(action)
            if environment.evaluate(task) < 1:
                continue

            utterance = utterance_generator.invoke({
                "description": scene.description, "devices": rendered_devices, "task": draft
            }).user_utterance
            debug(utterance)

            validation_result = validator.invoke(answer_dict | {
                "devices": scene.devices, "utterance": utterance, "task": draft, "devices": rendered_devices
            })
            debug(validation_result.reason)
            if not validation_result.valid:
                continue

            return {"model": model.name, "description": scene.description, 
                    "devices": [device.model_dump() for device in scene.devices],
                    "utterance": utterance, "task": task.model_dump()}

        except Exception as e:
            debug(e)

def select_distractors(devices: List[dict]) -> list[tuple[str, str]]:
    used = {device["room"] for device in devices}
    rooms = [room for room in get_args(DeviceDraft.model_fields["room"].annotation) if room not in used]
    return [(room, profile) for room in rooms for profile in PROFILES]

def scale_scenario(base_scenario: dict, num_device: int, candidates: list[tuple[str, str]]) -> dict:
    devices = base_scenario["devices"]
    while len(devices) < num_device:
        used = {(device["room"], device["profile"]) for device in devices}
        available = sorted(set(candidates) - used)
        ids = {device["device_id"] for device in devices}
        room, profile = random.choice(available)
        candidates[:] = [candidate for candidate in candidates if candidate != (room, profile)]
        validation = device_validator.invoke(
            {"room": room, "profile": {"name": profile, "description": PROFILES[profile]["description"]}}
        )
        debug(validation.reason)
        if not validation.valid:
            continue
        device_id = next(f"{room}_{profile}_{i}" for i in range(1, len(ids) + 2) if f"{room}_{profile}_{i}" not in ids)
        ids.add(device_id)
        devices.append(DeviceDraft(device_id=device_id, room=room, profile=profile).model_dump())
    random.shuffle(devices)
    return base_scenario

if __name__ == "__main__":
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument("--debug", action="store_true")
    argument_parser.add_argument("--model", type=str, required=False, default="gemma4:12b-it-q4_K_M", help="LLM to use")
    args = argument_parser.parse_args()
    set_debug(args.debug)

    profiles = json.dumps({name: profile["description"] for name, profile in PROFILES.items()}, ensure_ascii=False)
    debug(profiles)
    model = Model(model=args.model, reasoning=False, temperature=None, context=32768)

    scene_generator = create_generator(SCENE_PROMPT.partial(profiles=profiles), Scene, model)
    task_generator = create_generator(TASK_PROMPT, Task, model)
    utterance_generator = create_generator(UTTERANCE_PROMPT, UserUtterance, model)

    validator = create_generator(VALIDATION_PROMPT, ValidationResult, model)
    device_validator = create_generator(DEVICE_VALIDATION_PROMPT, ValidationResult, model)

    survey_df = pd.read_csv(SURVEY_PATH)
    df = pd.DataFrame()

    num_devices = [0, 5, 10, 15, 20]
    dfs = {num: pd.DataFrame() for num in num_devices}
    paths = {num: f"{DATASET_DIR}/dataset_D{num}_M0.csv" for num in num_devices}

    try:
        model.setup()
        for answer in tqdm(survey_df.itertuples(index=True), total=len(survey_df), desc=f"Synthesize ({model.name})"):
            answer_dict = answer._asdict()
            base_scenario = generate_scenario(answer_dict)
            debug(base_scenario)
            if base_scenario:

                candidates = select_distractors(base_scenario["devices"])
                for num in num_devices:
                    dfs[num] = pd.concat([dfs[num], pd.DataFrame([
                        {"ID": f"S{answer.Index}"} | deepcopy(scale_scenario(base_scenario, num, candidates))
                    ])], ignore_index=True)
                    save_dataframe(dfs[num], paths[num], ensure=False)
        model.wrapup()
        for num in num_devices:
            save_dataframe(dfs[num], paths[num], ensure=True)
    except KeyboardInterrupt:
        pass
