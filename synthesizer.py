import os
import pandas as pd
import argparse
import asyncio
import requests
import xml.etree.ElementTree as ET
import json
import random

from tqdm import tqdm
from tqdm.asyncio import tqdm as atqdm
from uuid import UUID, uuid4
from dotenv import load_dotenv
load_dotenv()

from langchain_core.documents import Document
from langchain_community.retrievers import BM25Retriever

from langchain_core.output_parsers import PydanticOutputParser
from typing import Optional, Literal, Annotated
from pydantic import BaseModel, Field, PlainSerializer, create_model
from typing import List, Dict, Any, Optional

from settings import *
from device import *
from model import Model

def serialize_id(id: UUID) -> str:
    return str(id)

# W3C WoT TD

class TDProperty(BaseModel):
    type: Literal["integer", "string"]

class TDObjectProperty(BaseModel):
    type: Literal["object"]
    properties: Dict[str, TDProperty] = Field(description="The properties of the object.")
    required: List[str] = Field(default=[], description="The required properties of the object.")

class TDAction(BaseModel):
    title: str = Field(description="Title of the action that the device can perform.")
    description: str = Field(description="Description of the action.")
    input: Optional[TDObjectProperty] = Field(description="The input to the action.")
    # TODO output
    # TODO forms

class TDDevice(BaseModel):
    # AUTOCOMPLETION format: Literal["W3C"]
    # AUTOCOMPLETION id: Annotated[UUID, PlainSerializer(serialize_id)]
    title: str = Field(description="Title of the device, e.g., light, TV, air_conditioner.")
    # TODO properties
    actions: Dict[str, TDAction] = Field(description="Actions the device can perform with optional arguments.")

# SmartThings

class STSchema(BaseModel):
    type: Literal["integer", "string"]

class STArgument(BaseModel):
    name: str = Field(description="Argument name.")
    optional: bool = Field(description="Whether this argument is optional or mandatory.")
    schema_: STSchema = Field(description="Schema of the argument.")

class STCommand(BaseModel):
    arguments: List[STArgument] = Field(default=[], description="Required arguments for the command.")

class STCapability(BaseModel):
    id: str = Field(description="Name of the capability.")
    # AUTOCOMPLETION version: Literal[1]
    # AUTOCOMPLETION status: Literal["live"]
    # TODO attributes
    commands: Dict[str, STCommand] = Field(description="Available commands to the capability.")

class STComponent(BaseModel):
    # AUTOCOMPLETION id: Literal["main"]
    # AUTOCOMPLETION label: Literal["main"]
    # AUTOCOMPLETION optional: Literal[False]
    capabilities: List[STCapability] = Field(description="The capabilities that the device can control.")
    # categories
    # restrictions

class STDevice(BaseModel):
    # AUTOCOMPLETION format: Literal["SmartThings"]
    # AUTOCOMPLETION deviceId: Annotated[UUID, PlainSerializer(serialize_id)]
    name: str = Field(description="Name of the device, e.g., light, TV, air_conditioner.")
    label: str = Field(description="User-custom label of the device.")
    # manufacturerName
    # presentationId
    # deviceManufacturerCode
    # locationId
    # ownerId
    # roomId
    # deviceTypeId
    # deviceTypeName
    # deviceNetworkType
    # productId
    # brandId
    components: List[STComponent] = Field(min_length=1, max_length=1)
    # createTime
    # parentDeviceId
    # childDevices
    # profile
    # app
    # ble
    # bleD2D
    # dth
    # lan
    # zigbee
    # zwave
    # matter
    # hub
    # edgeChild
    # ir
    # irOcf
    # ocf
    # viper
    # group
    # virtual
    # mqtt
    # type
    # restrictionTier
    # allowed
    # indoorMap
    # executionContext
    # relationships

# Matter

class MTEndpoint(BaseModel):
    endpoint_id: str
    device_type_name: str = Field(description="Device type name.")
    device_type_id: str = Field(description="Device type id associated with the name.")
    # AUTOCOMPLETION clusters: Dict

class MTDevice(BaseModel):
    # AUTOCOMPLETION format: Literal["Matter"]
    # AUTOCOMPLETION id: Annotated[UUID, PlainSerializer(serialize_id)]
    endpoints: Dict[str, MTEndpoint] = Field(description="Endpoints of the device node.")

class MatterRetriever:
    def __init__(self, version=1.5):
        self.version = version

        if not os.path.exists(DB_PATH):
            os.mkdir(DB_PATH)

        # Get clusters
        if not os.path.exists(MATTER_CLUSTERS_PATH):
            files = requests.get(f"https://api.github.com/repos/project-chip/connectedhomeip/contents/data_model/{version}/clusters").json()
            clusters = {}
            for file in files:
                if file['name'].endswith('.xml'):
                    cluster_xml = ET.fromstring(requests.get(file['download_url']).text)
                    clusters[cluster_xml.get('id')] = {
                        "name": cluster_xml.get('name'),
                        # TODO attributes
                        "commands": {
                            command.get("id"): {
                                "name": command.get("name"),
                                "id": command.get("id"),
                                "mandatory": command.find("mandatoryConform") is not None,
                                "fields": [
                                    {"id": field.get("id"), "name": field.get("name"), "type": field.get("type"), "mandatory": field.find("mandatoryConform") is not None} for field in command.findall(".//field")
                                ]
                            }
                            for command in cluster_xml.findall(".//command")
                        }
                    }
            json.dump(clusters, open(MATTER_CLUSTERS_PATH, 'w', encoding='utf-8'), ensure_ascii=False, indent=4)
        self.clusters = json.load(open(MATTER_CLUSTERS_PATH, 'r', encoding='utf-8'))

        # Get device types
        if not os.path.exists(MATTER_DEVICE_TYPES_PATH):
            files = requests.get(f"https://api.github.com/repos/project-chip/connectedhomeip/contents/data_model/{version}/device_types").json()
            device_types = {}
            for file in files:
                if file['name'].endswith('.xml'):
                    device_type_xml = ET.fromstring(requests.get(file['download_url']).text)
                    device_types[device_type_xml.get('id')] = {
                        "name": device_type_xml.get('name'),
                        "clusters": {
                            cluster.get('id'): {
                                "name": cluster.get("name"),
                                "id": cluster.get("id"),
                                "mandatory": cluster.find("mandatoryConform") is not None,
                            }
                            for cluster in device_type_xml.findall('.//cluster') if cluster.get('id') in self.clusters
                        }
                    }
            json.dump(device_types, open(MATTER_DEVICE_TYPES_PATH, 'w', encoding='utf-8'), ensure_ascii=False, indent=4)
        self.device_types = json.load(open(MATTER_DEVICE_TYPES_PATH, 'r', encoding='utf-8'))

        documents = [Document(page_content=f"Device type name: {self.device_types[id]['name']} (device type id: {id})", metadata={"device_type_name": self.device_types[id]["name"], "device_type_id": id}) for id in self.device_types]
        
        self.retriever = BM25Retriever.from_documents(documents)
        self.retriever.k = 20
    
    def invoke(self, input, **kwargs):
        return [("system", document.page_content) for document in self.retriever.invoke(input, **kwargs)]
    
    def autocomplete(self, device):
        if device["format"] != "Matter":
            raise Exception("NOT MATTER DEVICE")
        count = 1
        endpoints = {}
        # TODO descriptor cluster
        for endpoint in device["endpoints"].values():
            if not endpoint["device_type_name"] or endpoint["device_type_id"] == "null":
                raise Exception("NO DEVICE_TYPE_NAME OR DEVICE_TYPE_ID")
            if endpoint["device_type_id"] not in self.device_types or self.device_types[endpoint["device_type_id"]]["name"] != endpoint["device_type_name"]:
                raise Exception(f"INVALID DEVICE_TYPE_NAME {endpoint['device_type_name']} or DEVICE_TYPE_ID {endpoint['device_type_id']}")
            device_type = self.device_types[endpoint["device_type_id"]]
            endpoints[str(count)] = {
                "endpoint_id": str(count),
                "device_type_name": endpoint["device_type_name"],
                "device_type_id": endpoint["device_type_id"],
                "clusters": {
                    cluster_id: {
                        "cluster_name": cluster["name"],
                        "cluster_id": cluster["id"],
                        # TODO attributes
                        # TODO features
                        # TODO dataTypes
                        "commands": {
                            command_id: {
                                "command_name": command["name"],
                                "command_id": command["id"],
                                "fields": [{"id": field["id"], "name": field["name"], "type": field["type"]} for field in command["fields"] if field["mandatory"]]
                            } for command_id, command in self.clusters[cluster_id]["commands"].items() if command["mandatory"]
                        } if "commands" in self.clusters[cluster_id] else []
                    } for cluster_id, cluster in device_type["clusters"].items() if cluster["mandatory"]
                } if "clusters" in device_type else {}
            }
            count += 1
        if not endpoints:
            raise Exception("EMPTY ENDPOINTS")
        device["endpoints"] = endpoints

GENERATOR_PROMPT = ChatPromptTemplate.from_messages([
    ("system", "You are a system designer creating realistic scenarios to test AI agents that control smart devices."),
    ("system", """[Rules]
- You MUST not reveal the private information.
- The device_types MUST include every device type required to accomplish the user_message.
- The device_types MAY include the device types in the survey answer.
- The user_message MUST be a fluent natural language imperative sentence for controlling some of the devices in the device_descriptions.
- The user_message MUST clearly specify the device to control, command, and arguments.
"""),
    ("system", "[Format]\n{format}"),
    ("assistant", "Where were you?"),
    ("user", "{space}"),
    ("assistant", "What devices were in the space? (Select all that apply.)"),
    ("user", "{devices}"),
    ("assistant", "What did you command the AI assistant?"),
    ("user", "{user_command}"),
    ("user", "Convert the above survey answers into a realistic scenario where a user sends a message to various devices.")
])

FACTORY_PROMPT = ChatPromptTemplate.from_messages([
    ("system", "You are a device developer who is writing a description document."),
    ("system", "[Rules]\nIf the device type is relevant to the user's message, the device should provide relevant functions."),
    ("system", "[Format]\n{format}"),
    MessagesPlaceholder(variable_name="matter_specifications"),
    ("user", "[User Message]\n{user_message}"),
    ("user", "Generate a device of the given type: {device_type}"),
])

PLANNER_PROMPT = ChatPromptTemplate.from_messages([
    ("system", "You are a secretary who controls smart devices. Control the devices upon the following user's message. Carefully revise the output according to your previous failure."),
    ("system", "[Format]\n{format}"),
    MessagesPlaceholder(variable_name="device_descriptions"),
    ("system", "[Expected behavior]\n{expected_behavior}"),
    ("system", "[Previous failure]\n{previous_failure}"),
    ("user", "{user_message}"),
])

VALIDATOR_PROMPT = ChatPromptTemplate.from_messages([
    ("system", "You are a validator who evaluates whether the device control orders accomplish the user's goal."),
    ("system", "[Format]\n{format}"),
    MessagesPlaceholder(variable_name="device_descriptions"),
    ("user", "{user_message}"),
    MessagesPlaceholder(variable_name="device_controls"),
    ("user", "Did the devices accomplish the user's goal?"),
])

class ValidationResult(BaseModel):
    valid: bool
    reason: str

async def validate_scenario(device_descriptions, user_message, expectations):
    return await validator.ainvoke({
        "device_descriptions": [("system", str(device)) for device in device_descriptions],
        "user_message": user_message,
        "device_controls": [("assistant", str(dict(expectation))) for expectation in expectations]
    })

async def generate_expectations(device_descriptions, user_message, expected_behavior):
    previous_failure = None
    for _ in range(SYNTHESIZE_RETRY):
        try:
            expectations = await planner.ainvoke({
                "device_descriptions": [("system", str(device)) for device in device_descriptions],
                "expected_behavior": expected_behavior,
                "previous_failure": previous_failure,
                "user_message": user_message,
            })

            # Syntatic validation
            for expectation in expectations.inputs:
                description = None
                for d in device_descriptions:
                    if expectation.agent_id == (d["deviceId"] if d["format"] == "SmartThings" else d["id"]):
                        description = d
                        break
                if description is None:
                    debug(expectation, description)
                    raise Exception("INVALID AGENT ID")
                
                validation_result = instantiate_device("", description).validate_input(**dict(expectation))
                if  validation_result != "VALID":
                    debug(expectation, description)
                    raise Exception(validation_result)
            
            # Semantic validation
            validation_result = await validate_scenario(device_descriptions, user_message, expectations.inputs)
            if not validation_result.valid:
                raise Exception(validation_result.reason)

            return expectations.model_dump(exclude_none=True)["inputs"]
        except Exception as e:
            debug(e)
            previous_failure = str(e)
            continue
    raise Exception("EXPECTATION FAILURE")

async def create_device(device_format, device_type, device_id, user_message):
    debug(f"Create device: {device_format} {device_type} {device_id}")
    for _ in range(SYNTHESIZE_RETRY):
        try:
            if device_format == "W3C":
                device = (await w3c_factory.ainvoke({"device_type": device_type, "user_message": user_message})).model_dump(exclude_none=True)
                device["format"] = "W3C"
                device["id"] = device_id
                return device
            elif device_format == "SmartThings":
                device = (await smartthings_factory.ainvoke({"device_type": device_type, "user_message": user_message})).model_dump(exclude_none=True)
                device["format"] = "SmartThings"
                device["deviceId"] = device_id
                for component in device["components"]:
                    component["id"] = "main"
                    component["label"] = "main"
                    component["optional"] = False
                    for capability in component["capabilities"]:
                        capability["version"] = 1
                        capability["status"] = "live"
                return device
            elif device_format == "Matter":
                device = (await matter_factory.ainvoke({"device_type": device_type, "user_message": user_message, "matter_specifications": retriever.invoke(device_type)})).model_dump(exclude_none=True)
                device["format"] = "Matter"
                device["id"] = device_id
                retriever.autocomplete(device)
                return device
        except Exception as e:
            debug(e)
            continue
    raise Exception("DEVICE CREATION FAILURE")

async def generate_scenario(answer, pbar):
    tries = 0
    while True:
        try:
            tries += 1

            # Scenario
            pbar.set_postfix({"tries": tries, "progress": "scenario"})
            scenario = await generator.ainvoke(answer._asdict())
            debug(scenario)

            # Create devices
            pbar.set_postfix({"tries": tries, "progress": "devices"})
            device_ids = [get_random_device_id() for _ in scenario.device_types]
            while len(device_ids) != len(set(device_ids)):
                device_ids = [get_random_device_id() for _ in scenario.device_types]
            device_descriptions = [await create_device(random.choice(device_formats), device_type, device_ids[i], scenario.user_message) for i, device_type in enumerate(scenario.device_types)]
            debug(device_descriptions)

            # Expectations
            pbar.set_postfix({"tries": tries, "progress": "expectations"})
            expectations = await generate_expectations(device_descriptions, scenario.user_message, answer.expected_behavior)
            debug(expectations)

            return {
                "user_message": scenario.user_message,
                "device_descriptions": device_descriptions,
                "evaluation_criteria": expectations
            }
        except Exception as e:
            debug(e)
            continue

async def main(path: str, iterate: int, reset: bool):
    # Load survey results
    survey_df = pd.read_csv(SURVEY_PATH)
    survey_df = survey_df.loc[survey_df.index.repeat(iterate)]
    survey_df = survey_df.reset_index(drop=True)

    # Synthesize dataset
    df = pd.read_csv(path) if os.path.exists(path) and not reset else pd.DataFrame()
    with tqdm(total=len(survey_df), desc="Synthesize") as pbar:
        done = 0
        for answer in survey_df.itertuples():
            task = asyncio.create_task(generate_scenario(answer, pbar))
            while not task.done():
                await asyncio.sleep(1)
                pbar.n = done
                pbar.refresh()
            df = pd.concat([df, pd.DataFrame([task.result()])], ignore_index=True)
            await save_dataframe(df, path)
            done += 1
        pbar.n = done
        pbar.refresh()

    # Save dataset
    await save_dataframe(df, path, ensure=True)


if __name__ == "__main__":
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument("--debug", action="store_true")
    argument_parser.add_argument("--reset", action="store_true")
    argument_parser.add_argument("--model", type=str, required=False, default="gpt-oss:20b", help="LLM to use")
    argument_parser.add_argument("--iterate", type=int, required=False, default=1, help="Number of iterations over the survey result")
    argument_parser.add_argument("--devices", type=int, required=False, default=3, help="Number of devices for each scenario")
    argument_parser.add_argument("--format", type=str, required=False, default="Full", choices=["W3C", "SmartThings", "Matter", "Full"], help="Device formats")
    args = argument_parser.parse_args()

    def debug(*text):
        if args.debug:
            print(*text)

    # Models

    device_formats = ["W3C", "SmartThings", "Matter"] if args.format == "Full" else [args.format]
    
    Expectations = create_model(
        'Expectations',
        inputs=(
            {"W3C": List[W3CInput], "SmartThings": List[SmartThingsInput], "Matter": List[MatterInput]}.get(args.format, List[W3CInput | SmartThingsInput | MatterInput]), 
            Field(min_length=1, description="The list of the correct control of the devices upon the user's message.")
        )
    )

    debug(f"{device_formats} {args.devices} devices")

    class Scenario(BaseModel):
        device_types: List[str] = Field(description="The types of the devices in the space.", min_length=args.devices, max_length=args.devices)
        user_message: str = Field(description="The message the user gives to the AI agent.")

    # LLM

    model = Model(model=args.model, backend="ollama", reasoning=False, temperature=0.7, max_output_tokens=4096)

    scenario_parser = PydanticOutputParser(pydantic_object=Scenario)
    generator = GENERATOR_PROMPT.partial(format=scenario_parser.get_format_instructions()) | model.instantiate() | scenario_parser

    expectation_parser = PydanticOutputParser(pydantic_object=Expectations)
    planner = PLANNER_PROMPT.partial(format=expectation_parser.get_format_instructions()) | model.instantiate() | expectation_parser

    retriever = MatterRetriever()

    w3c_parser = PydanticOutputParser(pydantic_object=TDDevice)
    w3c_factory = FACTORY_PROMPT.partial(format=w3c_parser.get_format_instructions(), matter_specifications=[]) | model.instantiate() | w3c_parser
    smartthings_parser = PydanticOutputParser(pydantic_object=STDevice)
    smartthings_factory = FACTORY_PROMPT.partial(format=smartthings_parser.get_format_instructions(), matter_specifications=[]) | model.instantiate() | smartthings_parser
    matter_parser = PydanticOutputParser(pydantic_object=MTDevice)
    matter_factory = FACTORY_PROMPT.partial(format=matter_parser.get_format_instructions()) | model.instantiate() | matter_parser

    validator_parser = PydanticOutputParser(pydantic_object=ValidationResult)
    validator = VALIDATOR_PROMPT.partial(format=validator_parser.get_format_instructions()) | model.instantiate() | validator_parser

    asyncio.run(main(path=f"{DATASET_DIR}/dataset_{args.format}_{args.devices}.csv", iterate=args.iterate, reset=args.reset))
