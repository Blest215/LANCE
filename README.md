# LANCE

This artifact contains the (1) data synthesizer, (2) synthesized dataset, (3) experiment codes, and (4) testbed codes for the reproducibility of the paper titled: _**LANCE**: Linguistic Agent Network for Cooperative Ecosystems of Heterogeneous Services_

## Main structure

- **synthesizer.py**: LLM-based synthesis of realistic datasets. Requires survey data to be in `./survey_result.csv`, which is excluded from the repository to protect participants' privacy.
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

| Type | Model | Parameters | Quantization | Release Date | Developer | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| LLM | [Nemotron 3.5 Bolt E4B](https://ollama.com/library/nemotron-3.5-bolt:e4b-q4_K_M) | Q4\_K\_M | 2026-10-23 | NVIDIA | Total 7.52B |
| LLM | [MiniMax M3.1 Flash](https://ollama.com/library/minimax-m3.1-flash:cloud) | 428B | Native | 2026-10-19 | MiniMax | Cloud |
| LLM | [Beam](https://ollama.com/library/beam:cloud) | 501.3B | Native | 2026-10-16 | Reflection | MoE (23.4B active); cloud |
| LLM | [Granite 4.2](https://ollama.com/library/granite4.2:3b-q4_K_M) | 3B | Q4\_K\_M | 2026-08-25 | IBM Research |  |
| LLM | [Ornith 1.5](https://ollama.com/library/ornith-1.5:9b) | 9B | Q4\_K\_M | 2026-08-19 | DeepReinforce |  |
| LLM | [Gemma 4](https://ollama.com/library/gemma4:12b-it-q4_K_M) | 12B | Q4\_K\_M | 2026-06-03 | Google DeepMind | Instruct |
| LLM | [Gemma 4](https://ollama.com/library/gemma4:e2b-it-q4_K_M) | E2B | Q4\_K\_M | 2026-03-31 | Google DeepMind | Instruct; total 5.12B |
| LLM | [Gemma 4](https://ollama.com/library/gemma4:e4b-it-q4_K_M) | E4B | Q4\_K\_M | 2026-03-31 | Google DeepMind | Instruct; total 8.00B |
| LLM | [Gemma 4](https://ollama.com/library/gemma4:31b-cloud) | 31B | Native | 2026-03-31 | Google DeepMind | Instruct; cloud |
| LLM | [Qwen 3.5](https://ollama.com/library/qwen3.5:0.8b-q8_0) | 0.8B | Q8\_0 | 2026-03-02 | Alibaba Cloud |  |
| LLM | [Qwen 3.5](https://ollama.com/library/qwen3.5:2b-q4_K_M) | 2B | Q4\_K\_M | 2026-03-02 | Alibaba Cloud |  |
| LLM | [Qwen 3.5](https://ollama.com/library/qwen3.5:4b-q4_K_M) | 4B | Q4\_K\_M | 2026-03-02 | Alibaba Cloud |  |
| LLM | [Qwen 3.5](https://ollama.com/library/qwen3.5:9b-q4_K_M) | 9B | Q4\_K\_M | 2026-03-02 | Alibaba Cloud |  |
| LLM | [Ministral 3](https://ollama.com/library/ministral-3:3b-instruct-2512-q4_K_M) | 3B | Q4\_K\_M | 2025-12-02 | Mistral AI | Instruct |
| LLM | [Llama 3.2](https://ollama.com/library/llama3.2:3b-instruct-q4_K_M) | 3B | Q4\_K\_M | 2024-09-25 | Meta | Instruct |
| Decision | [D1](https://ollama.com/library/d1:3b-q8_0) | 3B | Q8\_0 | 2026-10-07 | Liquid AI |  |
| Decision | [Nimble v3](https://ollama.com/library/nimble-v3:9b-q4_K_M) | 9B | Q4\_K\_M | 2026-09-30 | Bespoke Labs |  |
| Decision | [Tev1](https://ollama.com/library/tev1:0.8b-q8_0) | 0.8B | Q8\_0 | 2026-09-25 | Together AI |  |
| Decision | [Tev1](https://ollama.com/library/tev1:4b-q4_K_M) | 4B | Q4\_K\_M | 2026-09-23 | Together AI |  |
| Decision | [Kev](https://ollama.com/library/kev:0.8b-q8_0) | 0.8B | Q8\_0 | 2026-09-24 | Jared Palmer |  |
| Embedding | [Nomic Embed Text v1.5](https://ollama.com/library/nomic-embed-text:137m-v1.5-fp16) | 137M | FP16 | 2024-02-14 | Nomic AI |  |
