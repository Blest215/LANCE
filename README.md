# LANCE

This artifact contains the (1) data synthesizer, (2) synthesized dataset, and (3) experiment codes for the reproducibility of the paper titled: _**LANCE**: Linguistic Agent Network for Cooperative Ensemble of Heterogeneous Physical AI Services_

## Main structure

- **synthesizer.py**: LLM-based synthesis of realistic datasets. Requires survey data to be in ./dataset/db/survey_result.csv, which is excluded in the repository to protect the participants' privacy.
- **experiment.py**: main code for the experiments.
- **dataset/**: the directory contains the synthesized datasets, which are converted from the survey results. (`dataset_D{device numbers}_M{mutation level}.csv`)

## Dependencies

- python >= 3.11
- [Ollama](https://ollama.com/) >= 0.18
- [Mosquitto](https://mosquitto.org/) >= 2.0.22
- NVIDIA or AMD GPU required (VRAM >= 12GB)
- `pip install -r requirements.txt`

## How to reproduce the experiments

1. Install the above dependencies
2. Pull the following SLMs from the Ollama repository `ollama pull {model_name}`
3. Ensure the Mosquitto broker is running (MQTT_BROKER_ADDRESS can be changed in `settings.py`)
4. Run the experiments: `python experiment.py`
5. After done, plot the results: `python plot.py` (The results used in the paper are in ./results/2026-02-10-01-48-36)

## SLMs used in the experiments

### Main

- ministral-3:8b-instruct-2512-q8_0
- qwen3:8b-q8_0
- llama3.1:8b-instruct-q8_0
- ibm/granite4:tiny-h-q8_0
- qwen3:4b-instruct-2507-q8_0
- ministral-3:3b-instruct-2512-q8_0
- ibm/granite4:micro-h-q8_0
- llama3.2:3b-instruct-q8_0
- tomng/lfm2.5-instruct:1.2b-q8_0
- granite4:1b-h-q8_0
- qwen3.5:0.8b-q8_0
- functiongemma:270m-it-q8_0

### In-depth analysis

- qwen3:0.6b-q8_0
- qwen3:0.6b-q4_K_M
- qwen3:1.7b-q8_0
- qwen3:1.7b-q4_K_M
- qwen3:4b-instruct-2507-q4_K_M
- qwen3:4b-thinking-2507-q8_0
- qwen3:8b-q4_K_M
- qwen3:8b-q8_0

### etc.

- granite4:350m-h-q8_0
- rnj-1:8b-instruct-q8_0
- mistral:7b-instruct-v0.3-q8_0
- cogito:8b-v1-preview-llama-q8_0
- cogito:3b-v1-preview-llama-q8_0
- phi4-mini:3.8b-q8_0
- smollm2:1.7b-instruct-q8_0
- nemotron-3-nano:4b-q8_0
- llama3.2:1b-instruct-q8_0
- qwen3.5:2b-q8_0
- qwen3.5:4b-q8_0
- qwen3.5:9b-q8_0
