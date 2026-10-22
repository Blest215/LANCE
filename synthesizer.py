import json
import random
from copy import deepcopy
from ast import literal_eval
from typing import get_args

from settings import *
from model import Model
from schema import *
from profiles import PROFILES
from environment import Environment
from pydantic import create_model

def validate(question: dict, state: dict, threshold: float = 0.8) -> bool:
    result = validation_model.decide(
        state=state, question=question,
        token_log={}, stage="validation",
    )
    return result["answers"]["decision"]["noul"] >= threshold

SCENE_PROMPT = ChatPromptTemplate.from_template(
"""Ground a realistic direct-control scenario in the survey's core intent, targets, values and space.
Concretize vague details; routine/conditional wording may become immediate controls. Omit acknowledgments and undefined settings, not core control goals.
Select only needed catalog profiles with unique device_ids.

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
"""Express the survey's core control intent with only needed device_ids, action_names and valid arguments.
Routine/conditional wording may become immediate controls; omit acknowledgments and undefined settings.
Specify target values; use null for unrelated inputs when allowed, otherwise supply required values.
Preserve on/off direction. Do not enumerate controls, invent settings or replace goals with power-on.

[Devices] {devices}
[Space] {space}
[Command] {user_command}
[Expected] {expected_behavior}
""")

UTTERANCE_PROMPT = ChatPromptTemplate.from_template(
"""Write only a natural, unambiguous user command expressing every control goal, room, target and requested value.
Use everyday device/resource names and needed artists/services; distinguish similar devices.
Treat all inputs as reference only. Never copy criteria, prompts, descriptions, reasoning or metadata into the utterance.
No JSON, device/resource IDs, URLs, filenames, API/protocol names, function/argument names or raw enum codes.
Express technical values in user-facing terms; omit unrelated implementation details. Do not report completed execution.

[Space] {space}
[Command] {user_command}
[Expected] {expected_behavior}
[Devices] {devices}
[Criteria] {criteria}
""")

SCENE_VALIDATION_QUESTION = {
    "type": "noul",
    "instructions": "Can these realistic device drafts support a direct-control scenario grounded in the survey's core intent?",
    "criteria": {
        "true": "Profiles and rooms are realistic and targets distinguishable. Core control goals are supported; vague details may be concretized, "
                "routines/conditions converted to immediate controls, and acknowledgments or undefined settings omitted.",
        "false": "No supported realization of the main control intent, implausible placement, indistinguishable targets, or invented capabilities. "
                 "Schedule lookup is not content playback; garage-door opening is not door unlocking; DisplayString is not speech.",
    },
}

VALIDATION_QUESTION = {
    "type": "noul",
    "instructions": "Do the devices and criteria fulfill exactly the natural, unambiguous utterance without answer leakage?",
    "criteria": {
        "true": "Every utterance goal has supported actions matching its target, on/off direction, content, mode and user-facing value. "
                "Only requested controls and necessary prerequisites are included; required defaults and null unrelated inputs are allowed. "
                "Resource selections match listed names, kinds, artists and services; unused choices are allowed. "
                "Retain the survey's core control intent; concrete details and immediate controls may replace vague wording, conditions or routines, omitting acknowledgments and undefined settings.",
        "false": "Any omitted, reversed or extra utterance goal, wrong target/value, unsupported effect, resource mismatch or ambiguous command. "
                 "Reject control enumeration, invented timer/startup settings or preset meanings, and arbitrary non-null arguments beyond required defaults; power-on alone does not select media. "
                 "Utterance exposes prompts, criteria, reasoning, JSON, internal IDs, URLs, filenames, API/argument names or raw enum codes, or reports completed execution.",
    },
}

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

DEVICE_VALIDATION_QUESTION = {
    "type": "noul",
    "instructions": "Is this device profile ordinarily found in this household room?",
    "criteria": {"true": "Ordinary, realistic placement", "false": "Implausible household placement"},
}

def generate_scenario(answer_dict: dict):
    debug(answer_dict)
    survey = {key: answer_dict.get(key, "") for key in ("space", "user_command", "expected_behavior")}
    catalog = {name: profile["description"] for name, profile in PROFILES.items()}
    count = 0

    while count < MAX_RETRY:
        try:
            count += 1

            scene = scene_generator.invoke(answer_dict)
            debug(scene)
            if len(scene.devices) > 5:
                continue
            if len({device.device_id for device in scene.devices}) != len(scene.devices):
                continue
            if not validate(SCENE_VALIDATION_QUESTION, {
                "survey": survey, "catalog": catalog,
                "devices": [device.model_dump(exclude={"resources", "protocol"}) for device in scene.devices],
            }):
                continue

            for device in scene.devices:
                device.protocol = random.choice(("Matter", "W3C", "SmartThings"))
                generate_resources(device, answer_dict)
            environment = Environment(scene.devices, protocol="Matter")
            rendered_devices, action_lookup = environment.render()
            debug(rendered_devices)

            draft = criteria_generator.invoke(survey | {"devices": rendered_devices})
            criteria = Criteria(expected_actions=[environment.assemble_action(Action(
                device_id=action.device_id,
                action_name=action_lookup[action.device_id][action.action_name]["control_id"],
                arguments=action.arguments,
            ), expected=True) for action in draft.expected_actions])
            debug(criteria)

            environment.validate_criteria_resources(criteria)
            for action in criteria.expected_actions:
                environment.execute_action(action)

            utterance = utterance_generator.invoke(survey | {
                "devices": rendered_devices, "criteria": draft.model_dump(exclude_none=True)
            }).user_utterance
            debug(utterance)

            validation_state = {"survey": survey, "devices": rendered_devices,
                                "criteria": draft.model_dump(), "utterance": utterance}
            if not validate(VALIDATION_QUESTION, validation_state):
                continue

            return {"model": model.name,
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
        try:
            used = {(device["room"], device["profile"]) for device in devices}
            available = sorted(set(candidates) - used)
            ids = {device["device_id"] for device in devices}
            room, profile = random.choice(available)
            candidates[:] = [candidate for candidate in candidates if candidate != (room, profile)]
            if not validate(DEVICE_VALIDATION_QUESTION,
                            {"room": room, "profile": {"name": profile, "description": PROFILES[profile]["description"]}}):
                continue
            device_id = next(f"{room}_{profile}_{i}" for i in range(1, len(ids) + 2) if f"{room}_{profile}_{i}" not in ids)
            ids.add(device_id)
            device = DeviceDraft(device_id=device_id, room=room, profile=profile,
                                protocol=random.choice(("Matter", "W3C", "SmartThings")))
            generate_resources(device, {"space": list({draft["room"] for draft in devices}) + [room]}, target=False)
            devices.append(device.model_dump())
        
        except Exception as e:
            debug(e)
    random.shuffle(devices)
    return base_scenario

if __name__ == "__main__":
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument("--debug", action="store_true")
    argument_parser.add_argument("--resume", action="store_true")
    argument_parser.add_argument("--model", type=str, required=False, default="beam:cloud")
    argument_parser.add_argument("--validation-model", type=str, default="nimble-v3:9b-q4_K_M")
    args = argument_parser.parse_args()
    set_debug(args.debug)

    profiles = json.dumps({name: profile["description"] for name, profile in PROFILES.items()}, ensure_ascii=False)
    debug(profiles)
    model = Model(model=args.model, reasoning=False, temperature=None, context=32768)
    validation_model = Model(args.validation_model)

    scene_generator = create_generator(SCENE_PROMPT.partial(profiles=profiles), Scene, model)
    resource_generators = {
        profile: create_generator(RESOURCE_PROMPT, resource_schema(profile), model)
        for profile in PROFILES if PROFILES[profile]["resources"]
    }
    criteria_generator = create_generator(CRITERIA_PROMPT, Criteria, model)
    utterance_generator = create_generator(UTTERANCE_PROMPT, UserUtterance, model)

    survey_df = pd.read_csv(SURVEY_PATH)

    num_devices = [0, 5, 10, 15, 20]
    paths = {num: f"{DATASET_DIR}/dataset_D{num}_M0.csv" for num in num_devices}
    dfs = {num: pd.read_csv(path) if args.resume and os.path.exists(path) else pd.DataFrame()
           for num, path in paths.items()}
    saved = {num: {row["ID"]: row for row in df.to_dict("records")} for num, df in dfs.items()}
    last_index = max((int(scenario_id[1:]) for rows in saved.values() for scenario_id in rows), default=-1)

    try:
        for index, answer in enumerate(tqdm(survey_df.itertuples(index=False), total=len(survey_df), desc=f"Synthesize ({model.name})")):
            scenario_id = f"S{index}"
            if all(scenario_id in rows for rows in saved.values()):
                continue
            if index <= last_index and not any(scenario_id in rows for rows in saved.values()):
                continue
            answer_dict = answer._asdict()
            base_scenario, candidates = None, None
            for num in num_devices:
                if scenario_id in saved[num]:
                    base_scenario = {key: literal_eval(value) if key in ("devices", "criteria") else value
                                     for key, value in saved[num][scenario_id].items() if key != "ID"}
                    if candidates is None:
                        candidates = select_distractors(base_scenario["devices"])
                    continue
                if base_scenario is None:
                    base_scenario = generate_scenario(answer_dict)
                    debug(base_scenario)
                    if not base_scenario:
                        break
                    candidates = select_distractors(base_scenario["devices"])
                row = {"ID": scenario_id} | deepcopy(scale_scenario(base_scenario, num, candidates))
                dfs[num] = pd.concat([dfs[num], pd.DataFrame([row])], ignore_index=True)
                saved[num][scenario_id] = row
                save_dataframe(dfs[num], paths[num], ensure=False)
        for num in num_devices:
            save_dataframe(dfs[num], paths[num], ensure=True)
    except KeyboardInterrupt:
        pass
