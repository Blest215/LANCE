import argparse
import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import json
import ast
import re

from settings import *

plt.rcParams['font.size'] = 13

figure_width = 15
accuracy_label = "Accuracy Score"
time_label = "Time (second)"
dpi = 600

bar_width = 0.19
gap = 0.01

modes = {"CENTRALIZED": "#1f77b4", "NATURAL": "#ff7f0e", "RECRUIT": "#2ca02c", "CONVERSATIONAL": "#984ea3"}
mode_labels = {"CENTRALIZED": "Baseline", "NATURAL": "LANCE (natural)", "RECRUIT": "LANCE (recruit)", "CONVERSATIONAL": "LANCE"}
stages = {"discovery": "#2ca02c", "plan": "#1f77b4", "control": "#ff7f0e"}
stage_labels = {"discovery": "Discovery", "plan": "Composition", "control": "Orchestration"}

model_names = [
    "ministral-3:8b-instruct-2512",
    "ministral-3:3b-instruct-2512",
    "functiongemma:270m-it",
    "granite4:tiny-h",
    "granite4:7b-a1b-h",
    "granite4:micro-h",
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
        underbar = key.lower().replace("-", "_").replace(".", "_").replace(":", "_")
        if underbar in model_name:
            return f"{key}{model_name.replace(f'{underbar}_', '-').replace(f'{underbar}', '')}"
    return model_name


def prepare_plot_data(df):
    accuracy_columns = [c for c in df.columns if c.startswith("ACCURACY_")]
    accuracy_data = {}
    for col in accuracy_columns:
        model_name, mode = col.replace("ACCURACY_", "").rsplit("_", 1)
        model_name = get_model_name(model_name)
        if model_name not in accuracy_data:
            accuracy_data[model_name] = {}
        accuracy_data[model_name][mode] = df[col].astype(float).mean()

    time_columns = [c for c in df.columns if c.startswith("TIME_")]
    time_data = {}
    for col in time_columns:
        model_name, mode = col.replace("TIME_", "").rsplit("_", 1)
        model_name = get_model_name(model_name)
        if model_name not in time_data:
            time_data[model_name] = {}

        discovery_vals = sum([ast.literal_eval(value)["discovery"] for value in df[col]], [])
        plan_vals = sum([ast.literal_eval(value)["plan"] for value in df[col]], [])
        control_vals = sum([ast.literal_eval(value)["control"] for value in df[col]], [])

        time_data[model_name][mode] = {
            "discovery": float(np.mean(discovery_vals)) if len(discovery_vals) > 0 else 0.0,
            "plan": float(np.mean(plan_vals)) if len(plan_vals) > 0 else 0.0,
            "control": float(np.mean(control_vals)) if len(control_vals) > 0 else 0.0,
        }

    all_models = list(accuracy_data.keys())
    metric_data = {}
    for model in all_models:
        metric_data[model] = {}
        for mode in modes.keys():
            time_total = sum(time_data[model][mode].values())
            metric_data[model][mode] = (accuracy_data[model][mode] / time_total) if time_total > 0 else 0.0

    return {"accuracy": accuracy_data, "time": time_data, "metric": metric_data}, all_models


def plot_by_models(path, col_titles, xlabels=None, selected_models=None, name="models"):
    df = pd.read_csv(path)
    data, all_models = prepare_plot_data(df)
    
    models = selected_models if selected_models else all_models
    n_cols = 3
    n_models_per_col = (len(models) + n_cols - 1) // n_cols
    
    xlabels = [m.replace(":", "\n").replace("-q8_0", "").replace("-2512", "").replace("-2507", "").replace("tiny", "7b-a1b").replace("micro", "3b") for m in models] if not xlabels else xlabels
    
    rows_data = [
        (data["accuracy"], accuracy_label, False, [mode_labels[mode] for mode in modes]),
        (data["time"], time_label, True, [stage_labels[stage] for stage in stages]),
        # (data["metric"], f"{accuracy_label} / Time", False, mode_labels),
    ]

    fig, axes = plt.subplots(len(rows_data), n_cols, figsize=(figure_width, 4 * len(rows_data)), squeeze=False, sharey="row", sharex="col")
    
    for row_idx, (row_data, ylabel, is_stacked, legend_labels) in enumerate(rows_data):
        for col_idx in range(n_cols):
            start = col_idx * n_models_per_col
            end = min(start + n_models_per_col, len(models))
            models_slice = models[start:end]
            x = np.arange(len(models_slice))

            if is_stacked:
                for i, mode in enumerate(modes.keys()):
                    bottom = np.zeros(len(models_slice))
                    for stage_name, stage_color in stages.items():
                        values = [row_data.get(model, {}).get(mode, {}).get(stage_name, 0.0) for model in models_slice]
                        axes[row_idx, col_idx].bar(x + (i - 1.5) * (bar_width + gap), values, bar_width, bottom=bottom, color=stage_color, label=stage_name if (i == 0 and col_idx == n_cols - 1) else None)
                        bottom += np.array(values)
            else:
                for i, mode in enumerate(modes.keys()):
                    values = [row_data.get(model, {}).get(mode, 0.0) for model in models_slice]
                    axes[row_idx, col_idx].bar(x + (i - 1.5) * (bar_width + gap), values, bar_width, color=modes[mode], label=mode if col_idx == n_cols - 1 else None)

            axes[row_idx, col_idx].set_xticks(x)
            axes[row_idx, col_idx].set_xticklabels(xlabels[start:end], rotation=0)
            if col_idx == 0:
                axes[row_idx, col_idx].set_ylabel(ylabel)
            if row_idx == 0:
                axes[row_idx, col_idx].set_title(col_titles[col_idx], fontweight='bold')
            if col_idx == n_cols - 1:
                if legend_labels:
                    axes[row_idx, col_idx].legend(legend_labels, loc="upper right", reverse=True)
                else:
                    axes[row_idx, col_idx].legend(loc="upper right")
            axes[row_idx, col_idx].grid(axis="y", alpha=0.3)

    output_path = path.replace(".csv", f"_{name}.png")
    plt.tight_layout()
    plt.savefig(output_path, dpi=dpi, bbox_inches="tight")
    print(f"Saved plot to {output_path}")
    plt.close()


def plot_by_heterogeneity(directory_path, selected_model, devices=None, mutations=None):
    result_files = {}
    for filename in os.listdir(directory_path):
        match = re.match(RESULT_FILENAME_PATTERN, filename)
        if match:
            result_files[int(match.group(1)), int(match.group(2)) if match.group(2) else 0] = os.path.join(directory_path, filename)
    data = {config: prepare_plot_data(pd.read_csv(result_files[config]))[0] for config in result_files}
    
    if isinstance(devices, list) and isinstance(mutations, int):
        name = "devices"
        width = 1 + figure_width // 2
        x_pos = np.arange(len(modes)) * 1.5
        configs = [(device, mutations) for device in devices]
        config_labels = [f"{d} devices" for d in devices]
        cmap = plt.cm.YlOrRd
    elif isinstance(devices, int) and isinstance(mutations, list):
        name = "mutations"
        width = figure_width
        x_pos = np.arange(len(modes)) * 1.5
        configs = [(devices, mutation) for mutation in mutations]
        config_labels = [f"{m}% mutation" for m in mutations]
        cmap = plt.cm.YlOrBr
    else:
        return
    
    fig, ax = plt.subplots(figsize=(width, 4))
    colors = cmap(np.linspace(0.4, 1.0, len(configs)))

    group_width = 1.2
    per_bar_width = group_width / len(configs)

    inner_gap_frac = 0.08
    inner_gap = per_bar_width * inner_gap_frac
    actual_bar_width = per_bar_width - inner_gap

    offsets = (np.arange(len(configs)) - (len(configs) - 1) / 2) * per_bar_width

    for config_idx, config in enumerate(configs):
        values = [data[config]['accuracy'][selected_model][mode] for mode in modes]
        ax.bar(x_pos + offsets[config_idx], values, actual_bar_width, label=config_labels[config_idx], color=colors[config_idx])

    ax.set_xticks(x_pos)
    ax.set_xticklabels([mode_labels[mode] for mode in modes])
    ax.set_ylim(0, 100)
    ax.set_ylabel(accuracy_label)
    ax.legend(loc="upper right", ncol=len(configs))
    ax.grid(axis="y", alpha=0.3)
    
    plot_path = f"{directory_path}/result_by_{name}.png"
    plt.tight_layout()
    plt.savefig(plot_path, dpi=dpi, bbox_inches="tight")
    print(f"Saved plot to {plot_path}")
    plt.close()


def plot_by_hardwares(result_path, selected_models):
    files = {
        "Pi": result_path.replace(".csv", "_pi.csv"),
        "Jetson": result_path.replace(".csv", "_jetson.csv"), 
        "Desktop": result_path,
    }
    times_data = {}
    
    for hardware_label, file_path in files.items():
        data, all_models = prepare_plot_data(pd.read_csv(file_path))
        times_data[hardware_label] = { model: { mode: data["time"][model][mode] for mode in data["time"][model] } for model in all_models }
    
    hardware_aliases = ['Raspberry Pi 5', 'Jetson Orin Nano', 'Desktop']
    
    fig, axes = plt.subplots(1, len(files), figsize=(figure_width, 4), squeeze=False, sharey=None)
    model_labels = [m.replace(":", "\n").replace("-q4_K_M", "\nq4_K_M").replace("-q8_0", "").replace("-2512", "").replace("-2507", "") for m in selected_models]
        
    for col_idx, hardware in enumerate(files.keys()):        
        x = np.arange(len(selected_models))
        for stage_idx, stage_name in enumerate(stages.keys()):
            values = [times_data[hardware].get(model, {}).get("CONVERSATIONAL", {}).get(stage_name, 0.0) for model in selected_models]
            axes[0, col_idx].bar(x + (stage_idx - (len(stages) - 1) / 2) * (bar_width + gap), values, bar_width, color=stages[stage_name], label=stage_name)
        
        axes[0, col_idx].set_xticks(x)
        axes[0, col_idx].set_xticklabels(model_labels, rotation=0)
        if col_idx == 0:
            axes[0, col_idx].set_ylabel(time_label)
        axes[0, col_idx].set_title(hardware_aliases[col_idx], fontweight='bold')
        axes[0, col_idx].grid(axis="y", alpha=0.3)
        
        if col_idx == 2:
            axes[0, col_idx].legend([stage_labels[stage] for stage in stages], loc="upper right", reverse=True)
    
    plt.tight_layout()
    plot_path = result_path.replace(".csv", "_hardwares.png")
    plt.savefig(plot_path, dpi=dpi, bbox_inches="tight")
    print(f"Saved plot to {plot_path}")
    plt.close()


def plot_failure(result_path, selected_models=None):
    df = pd.read_csv(result_path)
    
    consequence_columns = [col for col in df.columns if col.startswith("CONSEQUENCES_")]
    
    failure_messages = {}
    for col in consequence_columns:
        model_name, mode = col.replace("CONSEQUENCES_", "").rsplit("_", 1)
        model_name = get_model_name(model_name)
        if selected_models is not None and model_name not in selected_models:
            continue
        for consequence_str in df[col]:
            consequences = ast.literal_eval(consequence_str)
            if len(consequences) <= 0:
                failure_messages["NO CONSEQUENCES"] = failure_messages.get("NO CONSEQUENCES", 0) + 1
            for item in consequences:
                if isinstance(item, dict) and item.get('success') is False:
                    message = item.get('message', 'Unknown Error')
                    if not message or message.strip() == '':
                        message = 'Unknown Error'
                    if len(message) > 30:
                        message = 'NO TOOL CALL BY AGENTS'
                    failure_messages[message] = failure_messages.get(message, 0) + 1
    
    sorted_messages = sorted(failure_messages.items(), key=lambda x: x[1], reverse=True)
    
    if len(sorted_messages) > 10:
        top_messages = sorted_messages[:10]
        others_count = sum(count for _, count in sorted_messages[10:])
        display_messages = top_messages + [("Others", others_count)]
    else:
        display_messages = sorted_messages
    
    labels = [msg for msg, _ in display_messages]
    sizes = [count for _, count in display_messages]
    total = sum(sizes)

    for failure, count in display_messages:
        print(f"{failure} & {(count / total)*100:.2f}\\% &  \\\\")


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

    main_models = [
        "ministral-3:8b-instruct-2512-q8_0",
        "granite4:tiny-h-q8_0",
        "qwen3:8b-q8_0",
        "ministral-3:3b-instruct-2512-q8_0",
        "granite4:micro-h-q8_0",
        "qwen3:4b-instruct-2507-q8_0",
        "functiongemma:270m-it-q8_0",
        "granite4:1b-h-q8_0",
        "qwen3:1.7b-q8_0",
    ]

    plot_failure(f"{RESULT_DIR}/{code}/result_D5_M0.csv", selected_models=main_models)

    plot_by_models(f"{RESULT_DIR}/{code}/result_D5_M0.csv", col_titles=["Small-size (<=8b)", "Tiny-size (<=4b)", "Micro-size (<=2b)"], selected_models=main_models, name="models")
    plot_by_models(f"{RESULT_DIR}/{code}/result_D5_M0.csv", col_titles=["Small-size (qwen3:8b)", "Tiny-size (qwen3:4b-instruct)", "Micro-size (qwen3:1.7b)"], selected_models=[
        "qwen3:8b-q8_0_reasoning",
        "qwen3:8b-q8_0",
        "qwen3:8b-q4_K_M",
        "qwen3:4b-thinking-2507-q8_0",
        "qwen3:4b-instruct-2507-q8_0",
        "qwen3:4b-instruct-2507-q4_K_M",
        "qwen3:1.7b-q8_0_reasoning",
        "qwen3:1.7b-q8_0",
        "qwen3:1.7b-q4_K_M",
    ], name="settings", xlabels=["q8_0 (reasoning)", "q8_0", "q4_K_M"] * 3)
    
    plot_by_hardwares(f"{RESULT_DIR}/{code}/result_D5_M0.csv", ["qwen3:8b-q4_K_M", "qwen3:4b-instruct-2507-q4_K_M", "qwen3:0.6b-q4_K_M"])
    
    plot_by_heterogeneity(f"{RESULT_DIR}/{code}", "qwen3:4b-instruct-2507-q8_0", devices=5, mutations=[0, 20, 40, 60, 80, 100])
    plot_by_heterogeneity(f"{RESULT_DIR}/{code}", "qwen3:4b-instruct-2507-q8_0", devices=[5, 10, 15], mutations=0)
