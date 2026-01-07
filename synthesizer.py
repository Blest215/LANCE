import os
import pandas as pd
import argparse
import time
import asyncio

from tqdm.asyncio import tqdm
from uuid import UUID, uuid4
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.exceptions import OutputParserException
from typing import Optional, Literal, Annotated
from pydantic import BaseModel, Field, PlainSerializer
from typing import List, Dict, Any, Optional

from model import Model
from settings import *

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
    output: Optional[TDProperty] = Field(description="The output from the action.")
    # TODO forms: list[]

class TDDevice(BaseModel):
    format: Literal["W3C"]
    id: Annotated[UUID, PlainSerializer(serialize_id)] = Field(description="Unique identifier for the device.", default_factory=uuid4)
    title: str = Field(description="Title of the device, e.g., light, TV, air_conditioner.")
    # TODO properties
    actions: Dict[str, TDAction] = Field(description="Actions the device can perform with optional arguments.")

# SmartThings

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

# Scenario

class Scenario(BaseModel):
    time: datetime = Field(description="Timestamp of the scenario.")
    device_descriptions: List[TDDevice | STDevice] = Field(description="The descriptions of the devices in the space.", min_length=5)
    user_command: str = Field(description="The command the user gives to the AI agent.")
    evaluation_criteria: str = Field(description="Simple criteria to evaluate the AI agent's reaction upon user's command according to the context.")

GENERATOR_PROMPT = """
You are a system designer creating realistic scenarios to test AI agents that control smart devices.
The given answers are from the survey of "Use Cases of AI Assistants to Control Smart Home or IoT Devices."
Convert the given survey answers into a random and realistic scenario to test the behavior of AI agents.

[Rules]
- You MUST not reveal the private information.
- The device_descriptions MUST include the devices in the answer.
- The device_descriptions MAY include additional devices to reflect realistic home settings containing heterogeneous devices.
- The user_command MUST be in fluent and short natural language.
- The user_command MAY not be specific enough and MAY contain indirect needs.
- The user_command MAY include multiple concatenated commands specified in the answer, not necessarily.
- The evaluation_criteria MUST reflect the expected behavior in the answer.
- The evaluation_criteria MUST not include inaccurate details not specified in the answer.

[Where were you?]
{space}

[What devices were in the space? (Select all that apply.)]
{devices}

[Which AI assistant did you used to control smart devices?]
{assistant}

[What did you command the AI assistant?]
{user_command}

[What behavior did you expect from the AI assistant and devices?]
{expected_behavior}    

[Format]
{format}
"""

async def generate_scenario(generator, answer):
    while True:
        try:
            scenario = await generator.ainvoke(answer._asdict())
            return scenario.model_dump(exclude_none=True)
        except OutputParserException:
            continue

async def main(model: Model, iterate: int, reset: bool):
    parser = PydanticOutputParser(pydantic_object=Scenario)
    scenario_generator = PromptTemplate.from_template(GENERATOR_PROMPT).partial(format=parser.get_format_instructions()) | model.instantiate() | parser

    # Load survey results
    survey_df = pd.read_csv(SURVEY_PATH)
    survey_df = survey_df.loc[survey_df.index.repeat(iterate)]
    survey_df = survey_df.reset_index(drop=True)

    # Synthesize dataset
    scenarios = pd.DataFrame(sum([await asyncio.gather(*[generate_scenario(scenario_generator, answer) for answer in batch.itertuples(index=False)]) for batch in tqdm(batch_dataframe(survey_df, SYNTHESIZE_BATCH_SIZE))], []))

    # Save dataset
    df = pd.concat([pd.read_csv(DATASET_PATH), scenarios], ignore_index=True) if os.path.exists(DATASET_PATH) and not reset else scenarios
    await save_dataframe(df, DATASET_PATH, ensure=True)


if __name__ == "__main__":
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument("--reset", action="store_true")
    argument_parser.add_argument("--model", type=str, required=False, default="gpt-oss-safeguard:20b", help="LLM to use")
    argument_parser.add_argument("--iterate", type=int, required=False, default=1, help="Number of iterations over the survey result")
    args = argument_parser.parse_args()
    
    model = Model(model=args.model, backend="ollama", reasoning=True, temperature=1.0)

    asyncio.run(main(model=model, iterate=args.iterate, reset=args.reset))
