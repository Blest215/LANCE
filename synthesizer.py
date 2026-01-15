import os
import pandas as pd
import argparse
import time
import asyncio
import requests
import xml.etree.ElementTree as ET
import json

from tqdm.asyncio import tqdm as atqdm
from uuid import UUID, uuid4
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

from langchain_core.documents import Document
from langchain_community.retrievers import BM25Retriever

from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.exceptions import OutputParserException
from typing import Optional, Literal, Annotated
from pydantic import BaseModel, Field, PlainSerializer
from typing import List, Dict, Any, Optional

from settings import *
from device import instantiate_device
from model import Model

def serialize_id(id: UUID) -> str:
    return str(id)

# W3C WoT TD

class TDExpectation(BaseModel):
    action: str

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
    output: Optional[TDProperty] = Field(description="The output from the action.")
    # TODO forms: list[]

class TDDevice(BaseModel):
    format: Literal["W3C"]
    id: Annotated[UUID, PlainSerializer(serialize_id)] = Field(description="Unique identifier for the device.", default_factory=uuid4)
    title: str = Field(description="Title of the device, e.g., light, TV, air_conditioner.")
    # TODO properties
    actions: Dict[str, TDAction] = Field(description="Actions the device can perform with optional arguments.")

# SmartThings

class STExpectation(BaseModel):
    capability: str
    command: str

class STCapability(BaseModel):
    id: str = Field(description="Name of the capability.")
    version: Literal[1]

class STComponent(BaseModel):
    id: Literal["main"]
    label: Literal["main"]
    capabilities: List[STCapability] = Field(description="The capabilities that the device can control.")
    # TODO categories
    # TODO optional

class STDevice(BaseModel):
    format: Literal["SmartThings"]
    deviceId: Annotated[UUID, PlainSerializer(serialize_id)] = Field(description="Unique identifier for the device.", default_factory=uuid4)
    name: str = Field(description="Name of the device, e.g., light, TV, air_conditioner.")
    label: str = Field(description="User-custom label of the device.")
    # TODO manufacturerName
    # TODO presentationId
    # TODO deviceManufacturerCode
    components: List[STComponent] = Field(min_length=1, max_length=1)
    # TODO profile
    # TODO ocf
    # TODO type
    # TODO restrictionTier
    # TODO allowed
    # TODO executionContext
    # TODO relationships

# Matter

class MTExpectation(BaseModel):
    endpoint_id: str
    cluster_id: str
    command_id: str

class MTEndpoint(BaseModel):
    endpoint_id: str
    device_type_name: str = Field(description="Device type name.")
    device_type_id: str = Field(description="Device type id associated with the name.")
    clusters: Dict = Field(default={})

class MTDevice(BaseModel):
    format: Literal["Matter"]
    id: Annotated[UUID, PlainSerializer(serialize_id)] = Field(description="Unique identifier for the device.", default_factory=uuid4)
    endpoints: Dict[str, MTEndpoint] = Field(description="Endpoints of the device node.")

class MatterRetriever:
    def __init__(self, version=1.5):
        self.version = version

        if not os.path.exists(DB_PATH):
            os.mkdir(DB_PATH)

        # Get clusters
        if not os.path.exists(CLUSTERS_PATH):
            files = requests.get(f"https://api.github.com/repos/project-chip/connectedhomeip/contents/data_model/{version}/clusters").json()
            clusters = {}
            for file in files:
                if file['name'].endswith('.xml'):
                    cluster_xml = ET.fromstring(requests.get(file['download_url']).text)
                    clusters[cluster_xml.get('id')] = {
                        "name": cluster_xml.get('name'),
                        "commands": {
                            command.get("id"): {
                                "name": command.get("name"),
                                "id": command.get("id"),
                                "mandatory": command.find("mandatoryConform") is not None,
                            }
                            for command in cluster_xml.findall(".//command")
                        }
                    }
            json.dump(clusters, open(CLUSTERS_PATH, 'w', encoding='utf-8'), ensure_ascii=False, indent=4)
        self.clusters = json.load(open(CLUSTERS_PATH, 'r', encoding='utf-8'))

        # Get device types
        if not os.path.exists(DEVICE_TYPES_PATH):
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
            json.dump(device_types, open(DEVICE_TYPES_PATH, 'w', encoding='utf-8'), ensure_ascii=False, indent=4)
        self.device_types = json.load(open(DEVICE_TYPES_PATH, 'r', encoding='utf-8'))

        documents = [Document(page_content=f"Device type: {self.device_types[id]['name']} (ID: {id})", metadata={"device_type": self.device_types[id]["name"], "device_type_id": id}) for id in self.device_types]
        
        self.retriever = BM25Retriever.from_documents(documents)
        self.retriever.k = 10
    
    def invoke(self, input, **kwargs):
        return "\n".join(document.page_content for document in self.retriever.invoke(input, **kwargs))
    
    def autocomplete(self, device: MTDevice):
        count = 1
        endpoints = {}
        # TODO descriptor cluster
        for endpoint in device.endpoints.values():
            if not endpoint.device_type_name or endpoint.device_type_id == "null":
                continue
            if endpoint.device_type_id not in self.device_types or self.device_types[endpoint.device_type_id]["name"] != endpoint.device_type_name:
                return False
            device_type = self.device_types[endpoint.device_type_id]
            endpoints[str(count)] = MTEndpoint(
                endpoint_id=str(count),
                device_type_name=endpoint.device_type_name,
                device_type_id=endpoint.device_type_id,
                clusters={
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
                            } for command_id, command in self.clusters[cluster_id]["commands"].items() if command["mandatory"]
                        } if "commands" in self.clusters[cluster_id] else []
                    } for cluster_id, cluster in device_type["clusters"].items() if cluster["mandatory"]
                } if "clusters" in device_type else {}
            )
            count += 1
        device.endpoints = endpoints
        return True

GENERATOR_PROMPT = """
You are a software engineer creating realistic scenarios to test AI agents that control smart devices.
The given answers are from the survey of "Use Cases of AI Assistants to Control Smart Home or IoT Devices."
Convert the given survey answers into a random and realistic scenario to test the behavior of AI agents.

[Rules]
- You MUST not reveal the private information.
- The device_descriptions MUST include the device types in the survey answer.
- The device_descriptions MAY include additional devices to reflect realistic home settings.
- In device_descriptions, each MTEndpoint MUST have correct names and ids following the given Matter specifications.
- The user_command MUST be in fluent and short natural language.
- The user_command MUST be a command that can be accomplished with the devices in the device_descriptions.
- The user_command MAY not be specific enough and MAY contain indirect needs.
- The user_command MAY include multiple concatenated commands specified in the survey answer, not necessarily.

[Where were you?]
{space}

[What devices were in the space? (Select all that apply.)]
{devices}

[What did you command the AI assistant?]
{user_command}

[Matter specifications]
{matter_specifications}

[Format]
{format}
"""

class Expectations(BaseModel):
    expectations: Dict[str, TDExpectation | STExpectation | MTExpectation] = Field(description="The pairs of device ID and their correct reaction upon the user's command according to the context.")

PLANNER_PROMPT = """
You are a secretary who controls smart devices. How would you control the devices upon the following user's command?

[Space]
{space}

[Device descriptions]
{device_descriptions}

[User command]
{user_command}

[Expected behavior]
{expected_behavior}

[Format]
{format}
"""

async def generate_expectation(planner, answer_dict, scenario):
    while True:
        try:
            # Expectation
            expectations = await planner.ainvoke({
                "space": answer_dict["space"],
                "device_descriptions": scenario.device_descriptions,
                "user_command": answer_dict["user_command"],
                "expected_behavior": answer_dict["expected_behavior"],
            })

            # Validation
            for agent_id, expectation in expectations.expectations.items():
                description = None
                for d in scenario.device_descriptions:
                    if agent_id == (str(d.deviceId) if isinstance(d, STDevice) else str(d.id)):
                        description = d
                        break
                if description is None:
                    raise Exception
                
                device = instantiate_device("", description.model_dump(exclude_none=True))
                if device.validate_input(**dict(expectation)) != "VALID":
                    raise Exception
            
            return expectations.model_dump(exclude_none=True)["expectations"]
        except Exception:
            continue

async def generate_scenario(semaphore, generator, retriever, planner, answer):
    async with semaphore:
        while True:
            try:
                # Scenario
                answer_dict = answer._asdict()
                answer_dict["matter_specifications"] = retriever.invoke(f"{answer_dict['devices']}")
                scenario = await generator.ainvoke(answer_dict)

                # Matter autocompletion
                autocompleted_descriptions = [retriever.autocomplete(device) for device in scenario.device_descriptions if isinstance(device, MTDevice)]
                if not all(autocompleted_descriptions):
                    continue

                expectations = await generate_expectation(planner, answer_dict, scenario)

                scenario = scenario.model_dump(exclude_none=True)
                scenario["evaluation_criteria"] = expectations
                
                return scenario
            except OutputParserException:
                continue

async def main(model: Model, iterate: int, reset: bool):
    parser = PydanticOutputParser(pydantic_object=Scenario)
    scenario_generator = PromptTemplate.from_template(GENERATOR_PROMPT).partial(format=parser.get_format_instructions()) | model.instantiate() | parser
    retriever = MatterRetriever()
    expectation_parser = PydanticOutputParser(pydantic_object=Expectations)
    planner = PromptTemplate.from_template(PLANNER_PROMPT).partial(format=expectation_parser.get_format_instructions()) | model.instantiate() | expectation_parser

    # Load survey results
    survey_df = pd.read_csv(SURVEY_PATH)
    survey_df = survey_df.loc[survey_df.index.repeat(iterate)]
    survey_df = survey_df.reset_index(drop=True)

    # Synthesize dataset
    semaphore = asyncio.Semaphore(SYNTHESIZE_CONCURRENCY_MAX)
    scenarios = pd.DataFrame(await atqdm.gather(*[generate_scenario(semaphore, scenario_generator, retriever, planner, answer) for answer in survey_df.itertuples(index=False)], desc="Synthesize"))

    # Save dataset
    df = pd.concat([pd.read_csv(DATASET_PATH), scenarios], ignore_index=True) if os.path.exists(DATASET_PATH) and not reset else scenarios
    await save_dataframe(df, DATASET_PATH, ensure=True)


if __name__ == "__main__":
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument("--reset", action="store_true")
    argument_parser.add_argument("--model", type=str, required=False, default="gpt-oss-safeguard:20b", help="LLM to use")
    argument_parser.add_argument("--iterate", type=int, required=False, default=1, help="Number of iterations over the survey result")
    args = argument_parser.parse_args()

    class Scenario(BaseModel):
        time: datetime = Field(description="Timestamp of the scenario.")
        device_descriptions: List[TDDevice | STDevice | MTDevice] = Field(description="The descriptions of the devices in the space.", min_length=5)
        user_command: str = Field(description="The command the user gives to the AI agent.")

    model = Model(model=args.model, backend="ollama", reasoning=True, temperature=1.0, max_output_tokens=16384)

    asyncio.run(main(model=model, iterate=args.iterate, reset=args.reset))
