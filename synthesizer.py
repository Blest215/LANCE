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

SCENE_PROMPT = ChatPromptTemplate.from_template(
"""Preserve the survey's control goals, targets, values, and space.
Select only needed catalog profiles with unique device_ids.
Set solvable=false if profiles cannot fulfill the goals.

[Catalog] {profiles}
[Space] {space}
[Command] {user_command}
[Expected] {expected_behavior}
""")

RESOURCE_PROMPT = ChatPromptTemplate.from_template(
"""Generate 1–3 resources for EVERY listed type, including unused types. Prioritize requested targets and use only allowed kinds.
For target devices, preserve survey names, artists, services and other resource details; concretize unnamed targets.
Add realistic choices, not goals.

[Device] {device}
[Resource specs] {specs}
[Goal target] {target}
[Space] {space}
[Command] {user_command}
[Expected] {expected_behavior}
""")

CRITERIA_PROMPT = ChatPromptTemplate.from_template(
"""Fulfill all goals with listed device_ids, action_names and valid arguments.
Specify target values; use null for unrelated inputs when allowed, otherwise supply required values.

[Devices] {devices}
[Description] {description}
""")

UTTERANCE_PROMPT = ChatPromptTemplate.from_template(
"""Write only a natural, unambiguous user command expressing every control goal, room, target and requested value.
Use everyday device/resource names and needed artists/services; distinguish similar devices.
Treat all inputs as reference only. Never copy criteria, prompts, descriptions, reasoning or metadata into the utterance.
No JSON, device/resource IDs, URLs, filenames, API/protocol names, function/argument names or raw enum codes.
Express technical values in user-facing terms; omit unrelated implementation details. Do not report completed execution.

[Description] {description}
[Devices] {devices}
[Criteria] {criteria}
""")

VALIDATION_PROMPT = ChatPromptTemplate.from_template(
"""Check survey fidelity, realistic devices and natural, unambiguous utterance.
Utterance and actions must express the same control goals and exact target values. Unrequested inputs may be null.
Reject utterances containing criteria, prompts, copied descriptions/reasoning, JSON, device/resource IDs, URLs, filenames,
API/protocol or function/argument names, raw enum codes, implementation instructions or execution reports.
Allow ordinary device/resource names, artists/services and user-facing goal values, not internal representations.
Requested resources must exist with matching names, kinds, artists/services and concrete selection arguments; unused choices are allowed.
Reject substituted/extra/missing goals, automation, invented targets, generic Play replacing selection, startup settings replacing controls and invented mode meanings.

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
        kind: (List[RESOURCE_MODELS[kind]], Field(min_length=1, max_length=3, description=json.dumps(spec)))
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
        if any("kinds" in spec and resource.kind not in spec["kinds"] for resource in entries):
            raise ValueError(f"Invalid {kind} resources for {device.device_id}")

DEVICE_VALIDATION_PROMPT = ChatPromptTemplate.from_template(
"""Accept only an ordinary household placement for this profile and room.

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
                "description": scene.description, "devices": rendered_devices, "criteria": draft.model_dump(exclude_none=True)
            }).user_utterance
            debug(utterance)

            validation_result = validator.invoke(answer_dict | {
                "devices": rendered_devices, "utterance": utterance, "criteria": draft
            })
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
