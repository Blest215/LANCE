# LANCE

This artifact contains the (1) data synthesizer, (2) synthesized dataset, (3) experiment codes, and (4) testbed codes for the reproducibility of the paper titled: _**LANCE**: Linguistic Agent Network for Cooperative Ecosystems of Heterogeneous Services_

## Main structure

- **synthesizer.py**: LLM-based synthesis of realistic datasets. Requires survey data to be in `./dataset/db/survey_result.csv`, which is excluded from the repository to protect participants' privacy.
- **dataset/**: the directory contains the synthesized datasets, which are converted from the survey results. (`dataset_D{device numbers}_M{mutation level}.csv`)
- **experiment.py**: main code for the experiments.
- **testbed.py**: code for the testbed.

## Dependencies

- python >= 3.13
- [Ollama](https://ollama.com/) >= 0.40.12
- NVIDIA or AMD GPU required (VRAM >= 16GB)
- `pip install -r requirements.txt`

## How to reproduce the experiments

1. Install the above dependencies
2. Pull the following SLMs from the Ollama repository `ollama pull {model_name}`
3. Run the experiments: `python experiment.py`
4. After done, plot the results: `python plot.py` (The results used in the paper are in `./results/2026-10-28-00-00-00`)

## Models used in the experiments

### Language models

- qwen3.5:0.8b-q8_0
- qwen3.5:2b-q4_K_M
- llama3.2:3b-instruct-q4_K_M
- granite4.2:3b-q4_K_M
- ministral-3:3b-instruct-2512-q4_K_M
- qwen3.5:4b-q4_K_M
- gemma4:e2b-it-q4_K_M
- gemma4:e4b-it-q4_K_M
- nemotron-3.5-bolt:e4b-q4_K_M
- ornith-1.5:9b
- qwen3.5:9b-q4_K_M
- gemma4:12b-it-q4_K_M
- gemma4:31b-cloud
- minimax-m3.1-flash:cloud
- beam:cloud

### Decision models

- kev:0.8b-q8_0
- tev1:0.8b-q8_0
- d1:3b-q8_0
- tev1:4b-q4_K_M
- nimble-v3:9b-q4_K_M

### Embedding models

- nomic-embed-text:137m-v1.5-fp16
