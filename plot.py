import argparse
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import json
import ast
import re

from settings import *

modes = ["CENTRALIZED", "NATURAL", "RECRUIT", "CONVERSATIONAL"]
mode_labels = ["Baseline", "LANCE (orchestration)", "LANCE (discovery)", "LANCE"]
stages = {"discovery": "#FF6B6B", "plan": "#3498DB", "control": "#2ECC71"}
stage_labels = ["Discovery", "Plan", "Control"]

model_names = [
    "ministral-3:8b-instruct-2512",
    "ministral-3:3b-instruct-2512",
    "functiongemma:270m-it",
    "granite4:3b-h",
    "granite4:1b-h",
    "granite4:350m-h",
    "gpt-oss:20b",
    "qwen3:0.6b",
    "qwen3:1.7b",
    "qwen3:4b-instruct-2507",
    "qwen3:4b-thinking-2507",
    "qwen3:8b",
    "qwen3:30b-a3b-instruct-2507",
    "phi4-mini:3.8b",
    "cogito:3b-v1-preview-llama",
    "smollm2:1.7b-instruct",
    "rnj-1:8b-instruct",
    "llama3.1:8b-instruct",
    "llama3.2:3b-instruct",
    "llama3.2:1b-instruct",
]

def get_model_name(model_name):
    for key in model_names:
        underbar = key.replace("-", "_").replace(".", "_").replace(":", "_")
        if underbar in model_name:
            return f"{key}{model_name.replace(f'{underbar}_', '-').replace(f'{underbar}', '')}"
    return model_name


def prepare_plot_data(df, models_or_labels=None, is_model_list=True):
    """Prepare accuracy, time, and metric data from a dataframe."""
    accuracy_columns = [c for c in df.columns if c.startswith("ACCURACY_")]
    acc = {}
    for col in accuracy_columns:
        model_name, mode = col.replace("ACCURACY_", "").rsplit("_", 1)
        model_name = get_model_name(model_name) if is_model_list else model_name
        if model_name not in acc:
            acc[model_name] = {}
        acc[model_name][mode] = df[col].astype(float).mean()

    time_columns = [c for c in df.columns if c.startswith("TIME_")]
    times = {}
    for col in time_columns:
        model_name, mode = col.replace("TIME_", "").rsplit("_", 1)
        model_name = get_model_name(model_name) if is_model_list else model_name
        if model_name not in times:
            times[model_name] = {}

        discovery_vals = sum([ast.literal_eval(value)["discovery"] for value in df[col]], [])
        plan_vals = sum([ast.literal_eval(value)["plan"] for value in df[col]], [])
        control_vals = sum([ast.literal_eval(value)["control"] for value in df[col]], [])

        times[model_name][mode] = {
            "discovery": float(np.mean(discovery_vals)) if len(discovery_vals) > 0 else 0.0,
            "plan": float(np.mean(plan_vals)) if len(plan_vals) > 0 else 0.0,
            "control": float(np.mean(control_vals)) if len(control_vals) > 0 else 0.0,
        }

    models = models_or_labels if models_or_labels else list(acc.keys())
    metric = {}
    for m in models:
        metric[m] = {}
        for mode in modes:
            a = acc.get(m, {}).get(mode, 0.0)
            t_parts = times.get(m, {}).get(mode, {"discovery": 0.0, "plan": 0.0, "control": 0.0})
            t_total = t_parts.get("discovery", 0.0) + t_parts.get("plan", 0.0) + t_parts.get("control", 0.0)
            metric[m][mode] = (a / t_total) if t_total > 0 else 0.0

    return {"acc": acc, "times": times, "metric": metric}, models


def plot_by_models(path, selected_models=None, name="models"):
    """Plot accuracy, time, and accuracy/time for models with 3-column layout."""
    df = pd.read_csv(path)
    data, all_models = prepare_plot_data(df, selected_models, is_model_list=True)
    
    models = selected_models if selected_models else all_models
    n_cols = 3
    n_models_per_col = (len(models) + n_cols - 1) // n_cols
    
    xlabels = [m.replace(":", "\n").replace("-q8_0", "").replace("-2512", "").replace("-2507", "") for m in models]
    col_titles = ["Mid-size (<=8b)", "Small-size (<=4b)", "Tiny-size (<=2b)"]
    
    fig_width = n_cols * 5
    fig, axes = plt.subplots(3, n_cols, figsize=(fig_width, 9), squeeze=False, sharey="row")
    
    bw = 0.2
    rows_data = [
        (data["acc"], "Accuracy", False, mode_labels),
        (data["times"], "Time (seconds)", True, stage_labels),
        (data["metric"], "Accuracy / Time", False, mode_labels),
    ]
    
    for row_idx, (row_data, ylabel, is_stacked, legend_labels) in enumerate(rows_data):
        for col_idx in range(n_cols):
            start = col_idx * n_models_per_col
            end = min(start + n_models_per_col, len(models))
            models_slice = models[start:end]
            xlabels_slice = xlabels[start:end]
            ax = axes[row_idx, col_idx]

            x = np.arange(len(models_slice))

            if is_stacked:
                for i, mode in enumerate(modes):
                    xpos = x + (i - 1.5) * bw
                    bottom = np.zeros(len(models_slice))
                    for stage_name, stage_color in stages.items():
                        vals = [row_data.get(m, {}).get(mode, {}).get(stage_name, 0.0) for m in models_slice]
                        ax.bar(xpos, vals, bw, bottom=bottom, color=stage_color, 
                               label=stage_name if (i == 0 and col_idx == n_cols - 1) else None)
                        bottom += np.array(vals)
            else:
                for i, mode in enumerate(modes):
                    vals = [row_data.get(m, {}).get(mode, 0.0) for m in models_slice]
                    ax.bar(x + (i - 1.5) * bw, vals, bw, label=mode if col_idx == n_cols - 1 else None)

            ax.set_xticks(x)
            ax.set_xticklabels(xlabels_slice, rotation=0)
            if col_idx == 0:
                ax.set_ylabel(ylabel)
            if row_idx == 0:
                ax.set_title(col_titles[col_idx], fontsize=10, fontweight='bold')
            if col_idx == n_cols - 1:
                if legend_labels:
                    ax.legend(legend_labels, loc="upper right", reverse=True)
                else:
                    ax.legend(loc="upper right")
            ax.grid(axis="y", alpha=0.3)

    output_path = path.replace(".csv", f"_{name}.png")
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    print(f"Saved plot to {output_path}")
    plt.close()


def plot_by_mutation(directory_path, selected_model, devices):
    """Plot accuracy for different mutation values (grouped by device count)."""
    result_files = {}
    for filename in os.listdir(directory_path):
        match = re.match(RESULT_FILENAME_PATTERN, filename)
        if match:
            device_count = int(match.group(1))
            mutation_value = int(match.group(2)) if match.group(2) else 0
            if device_count == devices:
                result_files[mutation_value] = os.path.join(directory_path, filename)
    sorted_configs = sorted(result_files.keys())
    
    data = {}
    for config in sorted_configs:
        data[config] = {selected_model: {}}
        df = pd.read_csv(result_files[config])

        for column in df.columns:
            if "ACCURACY_" in column:
                model_name, mode = column.replace("ACCURACY_", "").rsplit("_", 1)
                model_name = get_model_name(model_name)
                if model_name == selected_model:
                    data[config][selected_model][mode] = df[column].astype(float).mean()
    
    fig, ax = plt.subplots(figsize=(max(14, len(data) * 1.2), 4))
    x_pos = np.arange(len(sorted_configs))
    bar_width = 0.2

    for mode_idx, mode in enumerate(modes):
        values = [data[config][selected_model][mode] for config in sorted_configs]        
        ax.bar(x_pos + (mode_idx - 1.5) * bar_width, values, bar_width, label=mode)
    
    ax.set_xticks(x_pos)
    ax.set_xticklabels([f"{c}% mutations" for c in sorted_configs])
    ax.set_ylim(0, 100)
    ax.set_ylabel("Accuracy")
    ax.legend(loc="upper right")
    ax.grid(axis="y", alpha=0.3)
    
    plot_path = f"{directory_path}/result_by_mutation.png"
    plt.tight_layout()
    plt.savefig(plot_path, dpi=300, bbox_inches="tight")
    print(f"Saved plot to {plot_path}")
    plt.close()


def plot_by_devices(directory_path, selected_model):
    """Plot accuracy for different device counts where mutation value == 0.
    Expects filenames matching RESULT_FILENAME_PATTERN which capture device count and optional mutation.
    """
    result_files = {}
    for filename in os.listdir(directory_path):
        match = re.match(RESULT_FILENAME_PATTERN, filename)
        if match:
            device_count = int(match.group(1))
            mutation_value = int(match.group(2)) if match.group(2) else 0
            if mutation_value == 0:
                result_files[device_count] = os.path.join(directory_path, filename)

    sorted_devices = sorted(result_files.keys())
    if not sorted_devices:
        print(f"No files found with mutation=0 in {directory_path}")
        return

    data = {}
    for dev in sorted_devices:
        data[dev] = {}
        df = pd.read_csv(result_files[dev])
        for column in df.columns:
            if "ACCURACY_" in column:
                model_name, mode = column.replace("ACCURACY_", "").rsplit("_", 1)
                model_name = get_model_name(model_name)
                if model_name == selected_model:
                    data[dev][mode] = df[column].astype(float).mean()

    fig_width = max(8, len(data) * 0.8)
    fig, ax = plt.subplots(figsize=(fig_width, 5))
    x_pos = np.arange(len(sorted_devices))
    bar_width = 0.2

    for i, mode in enumerate(modes):
        values = [data[d].get(mode, 0.0) for d in sorted_devices]
        ax.bar(x_pos + (i - 1.5) * bar_width, values, bar_width, label=mode)

    ax.set_xticks(x_pos)
    ax.set_xticklabels([f"{d} devices" for d in sorted_devices])
    ax.set_ylim(0, 100)
    ax.set_ylabel("Accuracy")
    ax.legend(loc="upper right")
    ax.grid(axis="y", alpha=0.3)

    plot_path = f"{directory_path}/result_by_devices.png"
    plt.tight_layout()
    plt.savefig(plot_path, dpi=300, bbox_inches="tight")
    print(f"Saved plot to {plot_path}")
    plt.close()


if __name__ == "__main__":
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument("--code", type=str, required=False, default="")
    args = argument_parser.parse_args()

    remove_empty_results()
    code = args.code if args.code else get_last_result()
    print(code)

    for image_file in os.listdir(f"{RESULT_DIR}/{code}"):
        if image_file.endswith(".png"):
            os.remove(f"{RESULT_DIR}/{code}/{image_file}")

    result_files = [f"{RESULT_DIR}/{code}/{filename}" for filename in os.listdir(f"{RESULT_DIR}/{code}") if re.match(RESULT_FILENAME_PATTERN, filename)]

    plot_by_models(f"{RESULT_DIR}/{code}/result_D5_M0.csv", selected_models=[
        "rnj-1:8b-instruct-q4_K_M",
        "ministral-3:8b-instruct-2512-q4_K_M",
        "qwen3:8b-q4_K_M",
        "ministral-3:3b-instruct-2512-q8_0",
        "granite4:3b-h",
        "qwen3:4b-instruct-2507-q8_0",
        "functiongemma:270m-it-q8_0",
        "granite4:1b-h-q8_0",
        "qwen3:0.6b-q8_0",
    ], name="models")
    plot_by_models(f"{RESULT_DIR}/{code}/result_D5_M0.csv", selected_models=[
        "qwen3:8b-q4_K_M",
        "qwen3:8b-q8_0",
        "qwen3:8b-q8_0_reasoning",
        "qwen3:4b-instruct-2507-q4_K_M",
        "qwen3:4b-instruct-2507-q8_0",
        "qwen3:4b-thinking-2507-q4_K_M",
        "qwen3:0.6b-q4_K_M",
        "qwen3:0.6b-q8_0",
        "qwen3:0.6b-q8_0_reasoning",
    ], name="settings")
    
    plot_by_mutation(f"{RESULT_DIR}/{code}", "qwen3:4b-instruct-2507-q8_0", devices=5)
    plot_by_devices(f"{RESULT_DIR}/{code}", "qwen3:4b-instruct-2507-q8_0")

