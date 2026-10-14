import json
import random
from copy import deepcopy
from typing import get_args

from settings import *
from model import Model
from schema import *
from profiles import PROFILES
from environment import Environment
from pydantic import create_model

class ValidationResult(BaseModel):
    valid: bool
    reason: str

SCENE_PROMPT = ChatPromptTemplate.from_template(
"""Describe every survey goal and select needed catalog profiles with unique device_ids and realistic rooms.
Set solvable=false if profiles cannot fulfill the goals.
Leave device resources empty; they will be generated separately. Preserve requested resource names and details in the goal description.

[Catalog] {profiles}
[Space] {space}
[Command] {user_command}
[Expected] {expected_behavior}
""")

RESOURCE_PROMPT = ChatPromptTemplate.from_template(
"""Populate this device's resources with at least one entry for EVERY listed resource type, even when unused by the goal.
For target devices, preserve survey content, artists, providers, stations, areas, inputs and apps. Fill other choices with realistic examples; do not add goals.
Use only listed kinds. Providers are services, not artists or titles. Give unnamed requested content a concrete natural title.
Leave URLs null for automatic completion. Retain supplied channel numbers; otherwise leave them null. Cleaning areas must be plausible home zones.

[Device] {device}
[Resource specs] {specs}
[Goal target] {target}
[Space] {space}
[Command] {user_command}
[Expected] {expected_behavior}
""")

CRITERIA_PROMPT = ChatPromptTemplate.from_template(
"""Fulfill every described goal using listed device_ids, action_names and arguments within their options and ranges.
Use only registered resource choices (including exact ContentURL); do not invent targets or replace selection with Play. Resource-target arguments must be concrete, not null.
Specify requested values; use null for unrequested inputs when omission, defaults or null are allowed; supply other required executable values.

[Devices] {devices}
[Description] {description}
""")

UTTERANCE_PROMPT = ChatPromptTemplate.from_template(
"""You are a smart-home user.
Express the criteria as a natural, self-contained smart-home command with explicit rooms, targets and values.
Express only the user's goals; do not invent constraints for null arguments.
Identify selected content by its resource name and artist/provider when needed, not its URL or ID.

[Description] {description}
[Devices] {devices}
[Criteria] {criteria}
""")

VALIDATION_PROMPT = ChatPromptTemplate.from_template(
"""Validate the scenario; explain within 100 words.
Devices, utterance and expected actions must preserve all survey goals, targets and values.
The utterance must be natural, self-contained, unambiguous and semantically match the expected actions.
Requested values and target resources must have concrete arguments; unrequested inputs may be null.
Every resource needed by the survey and utterance must exist on the target device, with matching title/kind/artist/provider and a concrete expected argument selecting it.
Additional profile resource options need not be used; they must be realistic and must not introduce extra goals.
Reject missing resources, invented URLs/IDs, or generic Play replacing a requested selection. Device names/settings are not resources. Reject unsupported lookup goals replaced with playback.

[Space] {space}
[Command] {user_command}
[Expected] {expected_behavior}

[Devices] {devices}
[Criteria] {criteria}
[Utterance] {utterance}
""")

RESOURCE_MODELS = {"content": ContentResource, "channel": ChannelResource, "cleaning_area": CleaningAreaResource,
                   "input": InputResource, "application": ApplicationResource}

def resource_schema(profile):
    return create_model(f"{profile}Resources", **{
        kind: (List[RESOURCE_MODELS[kind]], Field(min_length=1, description=json.dumps(spec)))
        for kind, spec in PROFILES[profile]["resources"].items()
    })

def generate_resources(device: DeviceDraft, survey: dict, target=True):
    specs = PROFILES[device.profile]["resources"]
    if not specs:
        device.resources = []
        return
    generated = resource_generators[device.profile].invoke({
        "device": device.model_dump(exclude={"resources"}), "specs": specs, "target": target,
        **{key: survey.get(key, "") for key in ("space", "user_command", "expected_behavior")},
    })
    device.resources = [resource for kind in specs for resource in getattr(generated, kind)]
    for kind, spec in specs.items():
        entries = [resource for resource in device.resources if resource.type == kind]
        if not entries or any("kinds" in spec and resource.kind not in spec["kinds"] for resource in entries):
            raise ValueError(f"Missing or invalid {kind} resources for {device.device_id}")

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
            if len(scene.devices) > 5:
                continue

            for device in scene.devices:
                generate_resources(device, answer_dict)
            environment = Environment(scene.devices, protocol="Matter")
            rendered_devices, action_lookup = environment.render()
            debug(rendered_devices)

            draft = criteria_generator.invoke({"devices": rendered_devices, "description": scene.description})
            criteria = Criteria(expected_actions=[environment.assemble_action(Action(
                device_id=action.device_id,
                action_name=action_lookup[action.device_id][action.action_name]["control_id"],
                arguments=action.arguments,
            ), expected=True) for action in draft.expected_actions])
            debug(criteria)

            environment.validate_criteria_resources(criteria)
            for action in criteria.expected_actions:
                environment.execute_action(action)

            utterance = utterance_generator.invoke({
                "description": scene.description, "devices": rendered_devices, "criteria": draft
            }).user_utterance
            debug(utterance)

            validation_result = validator.invoke(answer_dict | {
                "devices": rendered_devices, "utterance": utterance, "criteria": draft
            })
            debug(validation_result.reason)
            if not validation_result.valid:
                continue

            return {"model": model.name, "description": scene.description, 
                    "devices": [device.model_dump() for device in scene.devices],
                    "utterance": utterance, "criteria": criteria.model_dump()}

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
        device = DeviceDraft(device_id=device_id, room=room, profile=profile)
        generate_resources(device, {"space": list({draft["room"] for draft in devices}) + [room]}, target=False)
        devices.append(device.model_dump())
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
    resource_generators = {
        profile: create_generator(RESOURCE_PROMPT, resource_schema(profile), model)
        for profile in PROFILES if PROFILES[profile]["resources"]
    }
    criteria_generator = create_generator(CRITERIA_PROMPT, Criteria, model)
    utterance_generator = create_generator(UTTERANCE_PROMPT, UserUtterance, model)

    validator = create_generator(VALIDATION_PROMPT, ValidationResult, model)
    device_validator = create_generator(DEVICE_VALIDATION_PROMPT, ValidationResult, model)

    survey_df = pd.read_csv(SURVEY_PATH)

    num_devices = [0, 5, 10, 15, 20]
    paths = {num: f"{DATASET_DIR}/dataset_D{num}_M0.csv" for num in num_devices}
    dfs = {num: pd.DataFrame() for num in num_devices}

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
