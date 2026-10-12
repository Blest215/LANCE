import random
import json
from copy import deepcopy
from urllib.parse import quote

from settings import *
from model import Model
from schema import *
from profiles import PROFILES
from simulator import Simulator

class ValidationResult(BaseModel):
    valid: bool
    reason: str

INTENT_PROMPT = ChatPromptTemplate.from_template(
"""Extract the survey intent and select catalog profiles needed to fulfill it.
Set solvable as False if the intent cannot be fulfilled with the profiles.
Extract requested content, providers, cleaning areas, channels, inputs and apps into resources; no presets or aliases.
Keep stated channel numbers; do not invent IDs or URLs. Choose the device location, not the user's remote location.

[Catalog] {profiles}
[Space] {space}
[Command] {user_command}
[Expected] {expected_behavior}
""")

TASK_PROMPT = ChatPromptTemplate.from_template(
"""Select device_id, action_name and arguments to fulfill the survey intent.
Use listed names, options and ranges.
Use device resources to select identifiers; * marks required arguments, not part of their names.

[Scene] {scene}
[Description] {description}
""")

UTTERANCE_PROMPT = ChatPromptTemplate.from_template(
"""You are a user in a smart home.
Express the full intent as a natural, self-contained command with clear targets and values.

[Intent] {intent}
""")

VALIDATION_PROMPT = ChatPromptTemplate.from_template(
"""Validate the scenario; explain within 100 words.
Intent, utterance and expected actions MUST preserve all goals in the survey command and expected behavior; do not omit, reverse or replace them.
The utterance MUST be natural, self-contained and unambiguous.
Expected actions MUST match the full intent and utterance: targets, actions and values.
Devices MUST have realistic capabilities, names and room placements.

[Space] {space}
[Command] {user_command}
[Expected] {expected_behavior}
[Intent] {intent}
[Task] {task}
[Utterance] {utterance}
""")

def _device_actions(data):
    if data["protocol"] == "Matter":
        return [(command["name"].lower(), {field["name"]: field for field in command["fields"]})
                for endpoint in data["endpoints"] for cluster in endpoint["clusters"]
                for command in cluster.get("commands", [])]
    if data["protocol"] == "W3C":
        return [(action["title"].lower(), action["input"].get("properties", {}))
                for action in data["td"]["actions"].values()]
    return [(command["name"].lower(), {arg["name"]: arg["value_schema"] for arg in command.get("arguments", [])})
            for capability in data["capabilities"] for command in capability.get("commands", {}).values()]

def _resource_options(data, resources: ScenarioResources):
    actions = _device_actions(data)
    bound = {}

    def choices(field, entries, key):
        enum, labels = ("enum_values", "enum_labels") if data["protocol"] == "Matter" else ("enum", "x-enumLabels")
        values = list(dict.fromkeys(entry[key] for entry in entries))
        field[enum] = values
        field[labels] = {str(entry[key]): entry["name"] for entry in entries}

    contents = [item.model_dump(exclude_none=True) for item in resources.contents]
    contents += [{"name": item.name, "kind": "radio"} for item in resources.channels if item.kind == "radio"]
    media = [item | {"ContentURL": item["name"] if item["name"].startswith(("http://", "https://")) else
             f"https://media.example.test/{quote(data['device_id'], safe='')}/{i}"} for i, item in enumerate(contents, 1)]
    areas = [item.model_dump(exclude_none=True) | {"AreaID": i} for i, item in enumerate(resources.cleaning_areas, 1)]
    tv_channels = [item for item in resources.channels if item.kind == "tv"]
    used_numbers = {item.major_number for item in tv_channels if item.major_number is not None}
    channels = []
    for item in tv_channels:
        number = item.major_number
        if number is None:
            number = next(number for number in range(1, 65536) if number not in used_numbers)
            used_numbers.add(number)
        channels.append(item.model_dump(exclude_none=True) | {"MajorNumber": number,
                        "MinorNumber": item.minor_number if item.minor_number is not None else 0})
    inputs = [{"name": item.name, "Index": i} for i, item in enumerate(resources.inputs)]
    apps = [{"name": item.name, "ApplicationID": str(i), "CatalogVendorID": 65521}
            for i, item in enumerate(resources.applications, 1)]
    maps = list(dict.fromkeys(item.map_name for item in resources.cleaning_areas if item.map_name))
    for area in areas:
        if "map_name" in area:
            area["MapID"] = maps.index(area["map_name"]) + 1

    for name, fields in actions:
        if name == "launchurl" and media:
            choices(fields["ContentURL"], media, "ContentURL")
            bound["contents"] = media
        elif name == "selectareas" and areas:
            choices(fields["NewAreas"]["items"], areas, "AreaID")
            bound["cleaning_areas"] = areas
        elif name == "changechannelbynumber" and channels:
            choices(fields["MajorNumber"], channels, "MajorNumber")
            choices(fields["MinorNumber"], channels, "MinorNumber")
            bound["channels"] = channels
        elif name == "changechannel" and channels:
            choices(fields["Match"], [{"name": item["name"], "Match": item["name"]} for item in channels], "Match")
        elif name == "selectinput" and inputs:
            choices(fields["Index"], inputs, "Index")
            bound["inputs"] = inputs
        elif name in ("launchapp", "stopapp", "hideapp") and apps and "Application" in fields:
            application = fields["Application"]
            if data["protocol"] == "Matter":
                members = {field["name"]: field for field in application["fields"]}
            else:
                members = application["properties"]
            choices(members["ApplicationID"], apps, "ApplicationID")
            choices(members["CatalogVendorID"], apps, "CatalogVendorID")
            bound["applications"] = apps
    data["resources"] = bound

def generate_device(profile_id: str, room: str, index: int, protocol=None, resources: ScenarioResources | None = None):
    profile = PROFILES[profile_id]
    protocol = protocol or random.choice(tuple(profile["devices"]))
    template = profile["devices"][protocol]
    data = deepcopy(template)

    data["device_id"] = f"{profile_id}_{index}"
    data["device_name"] = f"{room}_{profile_id}"
    data["room"] = room
    if protocol == "W3C":
        data["td"]["title"] = data["device_name"]
    if resources is not None:
        _resource_options(data, resources)

    return {"Matter": MatterDevice, "W3C": W3CDevice, "SmartThings": SmartThingsDevice}[protocol].model_validate(data)

def generate_scenario(answer_dict: dict):
    debug(answer_dict)

    while True:
        try:
            intent = intent_extractor.invoke(answer_dict)
            debug(intent)
            if not intent.solvable:
                return

            devices = [generate_device(profile_id, intent.room, i, resources=intent.resources)
                       for i, profile_id in enumerate(intent.devices)]
            debug(devices)

            scene = Scene.model_validate({"rooms": [intent.room], "devices": devices})
            simulator = Simulator(scene)
            rendered_scene, action_lookup = simulator.render()
            debug(rendered_scene)

            draft = task_generator.invoke({"scene": rendered_scene, "description": intent.description})
            task = Task(expected_actions=[simulator.assemble_action(Action(
                device_id=action.device_id,
                action_name=action_lookup[action.device_id][action.action_name]["control_id"],
                arguments=action.arguments,
            )) for action in draft.expected_actions])
            debug(task)

            for action in task.expected_actions:
                simulator.execute_action(action)
            if simulator.evaluate(task) < 1:
                continue

            utterance = utterance_generator.invoke({"intent": intent.description + "\n" + "\n".join([
                f"Device [{action.device_id}]: action [{action.action_name}] with arguments ({action.arguments})"
                for action in task.expected_actions
            ])}).user_utterance
            debug(utterance)

            validation_result = validator.invoke(answer_dict | {"intent": intent, "utterance": utterance, "task": task})
            debug(validation_result.reason)
            if not validation_result.valid:
                continue

            return {"model": model.name, "intent": intent.model_dump(), "scene": scene.model_dump(),
                    "utterance": utterance, "task": task.model_dump()}

        except Exception as e:
            debug(e)

if __name__ == "__main__":
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument("--debug", action="store_true")
    argument_parser.add_argument("--model", type=str, required=False, default="gemma4:12b-it-q4_K_M", help="LLM to use")
    args = argument_parser.parse_args()
    set_debug(args.debug)

    profiles = json.dumps({name: profile["description"] for name, profile in PROFILES.items()}, ensure_ascii=False)
    debug(profiles)
    path = f"{DATASET_DIR}/dataset_D5_M0.csv"
    model = Model(model=args.model, reasoning=False, temperature=None, context=32768)

    intent_extractor = create_generator(INTENT_PROMPT.partial(profiles=profiles), Intent, model)
    task_generator = create_generator(TASK_PROMPT, Task, model)
    utterance_generator = create_generator(UTTERANCE_PROMPT, UserUtterance, model)

    validator = create_generator(VALIDATION_PROMPT, ValidationResult, model)

    survey_df = pd.read_csv(SURVEY_PATH)
    df = pd.DataFrame()

    try:
        model.setup()
        for answer in tqdm(survey_df.itertuples(index=False), total=len(survey_df), desc=f"Synthesize ({model.name})"):
            scenario = generate_scenario(answer._asdict())
            df = pd.concat([df, pd.DataFrame([scenario])], ignore_index=True)
            save_dataframe(df, path, ensure=False)
        save_dataframe(df, path, ensure=True)
        model.wrapup()
    except KeyboardInterrupt:
        pass
