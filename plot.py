import argparse
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import json
import ast
import re

from settings import *

result_filename_pattern = r'^result_[A-Za-z_]+_(\d+)(_M(\d+))?\.csv$'
modes = ["CENTRALIZED", "NATURAL", "RECRUIT", "CONVERSATIONAL"]
stages = {"discovery": "#FF6B6B", "plan": "#4ECDC4", "control": "#45B7D1"}

model_list = [
    "ministral-3:3b-instruct-2512-q8_0",
    "functiongemma:270m-it-q8_0",
    "granite4:350m-h-q8_0",
    "granite4:1b-h-q8_0",
    "gpt-oss:20b",
    "qwen3:4b-instruct-2507-q8_0",
    "qwen3:0.6b-q8_0",
    "qwen3:1.7b-q8_0",
    "phi4-mini:3.8b-q8_0",
    "smollm2:1.7b-instruct-q8_0",
    "llama3.2:3b-instruct-q8_0",
    "llama3.2:1b-instruct-q8_0",
]

def get_model_name(model_name):
    for key in model_list:
        if key.replace("-", "_").replace(".", "_").replace(":", "_") in model_name:
            return key
    return model_name

def plot_accuracy(path):
    df = pd.read_csv(path)

    accuracy_columns = [column for column in df.columns if column.startswith("ACCURACY_") and "T1" in column]
    data = {}
    for column in accuracy_columns:
        model_name, mode = column.replace("ACCURACY_", "").rsplit("_", 1)
        model_name = get_model_name(model_name).replace("-q8_0", "").replace("_T1", "")
        if model_name not in data:
            data[model_name] = {}
        data[model_name][mode] = df[column].astype(float).mean()
    
    fig_width = max(14, len(data) * 1.2)
    fig, ax = plt.subplots(figsize=(fig_width, 4))
    
    x_pos = np.arange(len(data))
    bar_width = 0.2
    
    for i, mode in enumerate(modes):
        values = [data[model][mode] for model in data.keys()]
        ax.bar(x_pos + (i - 1.5) * bar_width, values, bar_width, label=mode)
    
    ax.set_xticks(x_pos)
    ax.set_xticklabels([model_name.replace(":", "\n") for model_name in data.keys()], rotation=0)
    ax.set_ylabel("Accuracy")
    ax.legend(loc="upper right")
    ax.grid(axis="y", alpha=0.3)
    
    plot_path = result_path.replace(".csv", ".png")
    plt.tight_layout()
    plt.savefig(plot_path, dpi=300, bbox_inches="tight")
    print(f"Saved plot to {plot_path}")
    plt.close()


def plot_accuracy_by_heterogeneity(directory_path, selected_model):
    result_files = {}
    for filename in os.listdir(directory_path):
        match = re.match(result_filename_pattern, filename)
        if match:
            device_count = int(match.group(1))
            m_value = int(match.group(3)) if match.group(3) else 0
            result_files[m_value, device_count] = os.path.join(directory_path, filename)
    sorted_configs = sorted(result_files.keys())
    
    data = {}
    for config in sorted_configs:
        data[config] = {selected_model: {}}
        
        file_path = result_files[config]
        df = pd.read_csv(file_path)

        for column in df.columns:
            if "ACCURACY_" in column and "_T1" in column:
                model_name, mode = column.replace("ACCURACY_", "").rsplit("_", 1)
                model_name = get_model_name(model_name).replace("_T1", "")
                if model_name == selected_model:
                    data[config][selected_model][mode] = df[column].astype(float).mean()
    
    fig_width = max(14, len(data) * 1.2)
    fig, ax = plt.subplots(figsize=(fig_width, 4))
    x_pos = np.arange(len(sorted_configs))
    bar_width = 0.2
    
    for mode_idx, mode in enumerate(modes):
        values = [data[config][selected_model][mode] for config in sorted_configs]        
        ax.bar(x_pos + (mode_idx - 1.5) * bar_width, values, bar_width, label=mode)
    
    ax.set_xticks(x_pos)
    ax.set_xticklabels([f"{c[1]} devices\n{c[0]} mutations" if c[0] > 0 else f"{c[1]} devices" for c in sorted_configs])
    ax.set_ylabel("Accuracy")
    ax.legend(loc="upper right")
    ax.grid(axis="y", alpha=0.3)
    
    # Save figure
    plot_path = f"{directory_path}/result_by_heterogeneity.png"
    plt.tight_layout()
    plt.savefig(plot_path, dpi=300, bbox_inches="tight")
    print(f"Saved plot to {plot_path}")
    plt.close()


def plot_time(path, selected_model):
    df = pd.read_csv(path)
    
    time_columns = [column for column in df.columns if column.startswith("TIME_") and "T1" in column]
    data = {selected_model: {}}
    for column in time_columns:
        model_name, mode = column.replace("TIME_", "").rsplit("_", 1)
        model_name = get_model_name(model_name).replace("_T1", "")
        if model_name == selected_model:
            data[model_name][mode] = {
                "discovery": np.mean(sum([ast.literal_eval(value)["discovery"] for value in df[column]], [])),
                "plan": np.mean(sum([ast.literal_eval(value)["plan"] for value in df[column]], [])),
                "control": np.mean(sum([ast.literal_eval(value)["control"] for value in df[column]], [])),
            }
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    x_pos = np.arange(len(modes))
    bar_width = 0.6
    bottom = np.zeros(len(modes))
    
    for stage, stage_color in stages.items():
        values = [data[selected_model][mode][stage] for mode in modes]        
        ax.bar(x_pos, values, bar_width, label=stage, bottom=bottom, color=stage_color)
        bottom += np.array(values)
    
    ax.set_xticks(x_pos)
    ax.set_xticklabels(modes)
    ax.set_ylabel("Time (seconds)")
    ax.legend(loc="upper left", fontsize=10)
    ax.grid(axis="y", alpha=0.3)
    
    output_path = path.replace(".csv", "_time.png")
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    print(f"Saved plot to {output_path}")
    plt.close()


if __name__ == "__main__":
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument("--code", type=str, required=False, default="")
    argument_parser.add_argument("--option", type=str, required=False, default="")
    args = argument_parser.parse_args()

    code = args.code if args.code else get_last_result()
    print(code)

    result_files = [f"{RESULT_DIR}/{code}/{filename}" for filename in os.listdir(f"{RESULT_DIR}/{code}") if re.match(result_filename_pattern, filename)]

    if not args.option or args.option == "accuracy":
        for result_path in result_files:
            plot_accuracy(result_path)
    
    if not args.option or args.option == "heterogeneity":
        plot_accuracy_by_heterogeneity(f"{RESULT_DIR}/{code}", "qwen3:4b-instruct-2507-q8_0")

    if not args.option or args.option == "time":
        for result_path in result_files:
            plot_time(result_path, "qwen3:4b-instruct-2507-q8_0")
