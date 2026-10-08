import uuid
import secrets
import asyncio
import re
import os
import subprocess
import json
import time
import argparse
import pandas as pd
import sys
import requests

from tqdm import tqdm
from datetime import datetime

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import JsonOutputParser, PydanticOutputParser, StrOutputParser
from langchain_core.exceptions import OutputParserException
from langchain.tools import tool
from typing import List, Dict, Any, Optional, Literal
from abc import ABC, abstractmethod
from pydantic import BaseModel, Field, model_validator

from dotenv import load_dotenv
load_dotenv()

# Settings

DATASET_FILENAME_PATTERN = re.compile(r'^dataset_D(\d+)_M(\d+)\.csv$')
RESULT_FILENAME_PATTERN = r'^result_D(\d+)_M(\d+)\.csv$'

DATASET_DIR = "dataset"
RESULT_DIR = "results"
SURVEY_PATH = "survey_result.csv"
SETTING_PATH = RESULT_DIR + "/{code}/settings.txt"

ALLOWED_MODES = ["CENTRALIZED", "NATURAL", "RECRUIT", "CONVERSATIONAL"]

DEBUG = False

# LLM

MAX_CONTEXT = 32768
MAX_OUTPUT_TOKENS = 2048

# RECRUIT

RECRUIT_SCREENING_THRESHOLD = 0.0

# Devices

DEVICE_FORMATS = ["W3C", "SmartThings", "Matter"]

SMARTTHINGS_API_URL = "https://api.smartthings.com/v1/devices"

def get_random_device_id():
    return str(uuid.uuid4())

def get_random_request_id():
    return uuid.uuid4().hex

def check_topic(formatted, unformatted):
    return formatted == unformatted.split("/")[0]    

def get_agent_id(device_description):
    if "structured" in device_description:
        if "id" in device_description["structured"]:
            return device_description["structured"]["id"]
        if "deviceId" in device_description["structured"]:
            return device_description["structured"]["deviceId"]
    if "id" in device_description:
        return device_description["id"]
    if "deviceId" in device_description:
        return device_description["deviceId"]

def get_column_name(name, model, mode):
    return f"{name}_{model}_{mode}"

def save_dataframe(df, path, ensure=False):
    if df is None or len(df) == 0:
        return
    while True:
        try:
            df.to_csv(path, index=False, encoding="utf-8-sig")
            break
        except Exception:
            if ensure:
                time.sleep(1)
            else:
                break

def parse_column(df, value=""):
    pattern = r"^(?P<value>.*?)_(?P<model_name>.*)_(?P<method>.*?)$"
    matches = []
    for column in df.columns.tolist():
        match = re.match(pattern, column)
        if match and value in match.group():
            matches.append(match.group())
    return matches

def get_last_result():
    for code in sorted(os.listdir(RESULT_DIR), reverse=True):
        if os.listdir(f"{RESULT_DIR}/{code}"):
            return code
    return ""
    
def moving_average(l: list, window: int):
    while len(l) > window:
        l.pop(0)
    return sum(l) / len(l)

def debug(*text):
    if DEBUG:
        print(*text)

def set_debug(debug):
    global DEBUG
    DEBUG = debug

def remove_empty_results():
    if not os.path.exists(RESULT_DIR):
        os.mkdir(RESULT_DIR)
    for result_code in os.listdir(RESULT_DIR):
        files = os.listdir(f"{RESULT_DIR}/{result_code}")
        if len(files) == 1 and files[0] == "settings.txt":
            os.remove(SETTING_PATH.format(code=result_code))
            os.rmdir(f"{RESULT_DIR}/{result_code}")
        elif not files:            
            os.rmdir(f"{RESULT_DIR}/{result_code}")

def create_generator(prompt: str | ChatPromptTemplate, pydantic_object: BaseModel | dict | str, model):
    prompt_template = prompt if isinstance(prompt, ChatPromptTemplate) else ChatPromptTemplate.from_template(prompt)
    if pydantic_object == str:
        return prompt_template | model.instantiate() | StrOutputParser()
    if "qwen3.5" in model.model:
        parser = JsonOutputParser() if isinstance(pydantic_object, dict) else PydanticOutputParser(pydantic_object=pydantic_object)
        return ChatPromptTemplate.from_messages([
            ("system", "[Format]\n{format}"),
            *prompt_template.messages,
        ]).partial(format=json.dumps(pydantic_object) if isinstance(pydantic_object, dict)
                   else parser.get_format_instructions()) | model.instantiate() | parser
        
    return prompt_template | model.with_structured_output(pydantic_object)
