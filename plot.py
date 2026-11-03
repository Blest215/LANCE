"""Manuscript figures and tables: python plot.py [--code RUN].

Missing experiments remain pending. Input conventions: docs/tsc_plots.md.
"""
import argparse
import ast
import csv
import json
import re
from pathlib import Path
from time import perf_counter

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import numpy as np
import pandas as pd

METHODS = ["Centralized", "RAG", "Sasha", "LLMind", "LANCE"]
DEVICES, TARGET_D = [0, 5, 10, 15, 20], 10
STAGES = ["setup", "discovery", "composition", "orchestration"]
SCORE_FIELDS = ["precision", "recall", "f1", "accuracy"]
PERCENT_FIELDS = SCORE_FIELDS + ["error", "api_error", "discovery_precision", "discovery_recall",
                                "discovery_coverage", "assignment_coverage"]
DETAIL_FIELDS = PERCENT_FIELDS + ["selected_count", "sequential_time", "parallel_time", "llm_input", "llm_output",
                                 "llm_calls", "decision_calls", "decision_input", "embedding_calls", "embedding_input"]

METHOD_LABELS = {method: "LANCE (ours)" if method == "LANCE" else method for method in METHODS}
PALETTE = [matplotlib.colors.to_hex(c) for c in plt.rcParamsDefault["axes.prop_cycle"].by_key()["color"]]
COLORS = dict(zip(METHODS, PALETTE))
COLORS["LLMind"], COLORS["LANCE"] = COLORS["LANCE"], COLORS["LLMind"]
ALPHAS = {method: 1. if method == "LANCE" else .8 for method in METHODS}
ABLATIONS = ["LANCE", "LANCE_no_decision", "LANCE_no_discovery", "LANCE_no_separation", "LANCE_no_instruction"]
ABLATION_MODELS = ["qwen3_5_4b_q4_K_M"]
PROTOCOL_MODELS = ["qwen3_5_4b_q4_K_M"]
REPRESENTATIVE_MODELS = ["gemma4_e2b_it_q4_K_M", "qwen3_5_4b_q4_K_M", "gemma4_e4b_it_q4_K_M",
                         "minimax_m3_1_flash_cloud", "beam_cloud"]
DEVICE_MODELS = ["qwen3_5_4b_q4_K_M", "gemma4_e2b_it_q4_K_M", "gemma4_e4b_it_q4_K_M",
                 "gemma4_12b_it_q4_K_M"]
STABILITY_MODELS = DEVICE_MODELS
MODEL_NAMES = {"qwen3_5": "Qwen 3.5", "gemma4": "Gemma 4", "llama3_2": "Llama 3.2",
               "granite4_2": "Granite 4.2", "ministral_3": "Ministral 3", "tev1": "Tev1",
               "nimble_v3": "Nimble v3", "nimble": "Nimble", "ornith_1_5": "Ornith 1.5",
               "nemotron_3_5_bolt": "Nemotron 3.5 Bolt", "kev": "Kev", "d1_omni": "D1 Omni", "d1": "D1"}
# Total parameters from installed Ollama metadata (updated 2026-10-25).
MODEL_PARAMETERS = dict(zip([
    "qwen3_5_0_8b_q8_0", "qwen3_5_2b_q4_K_M", "llama3_2_3b_instruct_q4_K_M", "granite4_2_3b_q4_K_M",
    "ministral_3_3b_instruct_2512_q4_K_M", "qwen3_5_4b_q4_K_M", "gemma4_e2b_it_q4_K_M",
    "gemma4_e4b_it_q4_K_M", "ornith_1_5_9b", "qwen3_5_9b_q4_K_M", "nemotron_3_5_bolt_e4b_q4_K_M",
], [873438784, 2274069824, 3212749888, 3659737600, 3849090048, 4659865088,
    5123179235, 7996157674, 8953803264, 9653104368, 7518069290]))
# Published parameter counts (12B rounded to Ollama's 11.9B model size).
# Cloud models remain in their own group.
MODEL_PARAMETERS.update(gemma4_12b_it_q4_K_M=11_900_000_000, gemma4_31b_cloud=30_700_000_000,
                        minimax_m3_1_flash_cloud=428_000_000_000, beam_cloud=501_300_000_000)
# Installed Ollama general.parameter_count (2026-10-26).
DECISION_PARAMETERS = {"kev_0_8b_q8_0": 752917824, "tev1_0_8b_q8_0": 772845888,
                       "d1_3b_q8_0": 2697198592, "tev1_4b_q4_K_M": 4326350848,
                       "nimble_v3_9b_q4_K_M": 8953803264}
FILE_PATTERN = re.compile(r"result_D(\d+)_M0\.csv$")


class _SavedLiteral(ast.NodeTransformer):
    def visit_Call(self, node):
        if not isinstance(node.func, ast.Name) or node.func.id != "Action" or node.args or any(k.arg is None for k in node.keywords):
            raise ValueError("Unexpected expression in saved trace")
        return ast.Dict(keys=[ast.Constant(k.arg) for k in node.keywords], values=[k.value for k in node.keywords])


def parse_literal(value):
    tree = ast.parse(value, mode="eval")
    try:
        return ast.literal_eval(tree)
    except ValueError:
        return ast.literal_eval(_SavedLiteral().visit(tree))


def _errors(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, list):
        for item in value:
            yield from _errors(item)


def parallel_stage_time(wall, calls):
    """Estimated barrier: serial overhead + unassigned calls + longest device branch."""
    if not np.isfinite(wall):
        return np.nan
    devices, serial = {}, 0.
    for call in calls:
        elapsed, device = call.get("elapsed"), call.get("device_id")
        if elapsed is None or not np.isfinite(elapsed) or elapsed < 0:
            return np.nan
        if device is None:
            serial += elapsed
        else:
            devices[device] = devices.get(device, 0.) + elapsed
    return max(0., wall - serial - sum(devices.values())) + serial + max(devices.values(), default=0.)


def mean_device_decision_time(calls):
    devices = {}
    for call in calls:
        if call.get("kind") != "decision":
            continue
        elapsed, device = call.get("elapsed"), call.get("device_id")
        if device is None or elapsed is None or not np.isfinite(elapsed) or elapsed < 0:
            return np.nan
        devices[device] = devices.get(device, 0.) + elapsed
    return float(np.mean(list(devices.values()))) if devices else np.nan


def scores(value):
    result = json.loads(value) if isinstance(value, str) else value
    p, r = (float(result[k]) for k in ["precision", "recall"])
    accuracy = float(result.get("accuracy", np.nan))
    if not all(np.isfinite(v) and 0 <= v <= 1 for v in [p, r]) or not (np.isnan(accuracy) or accuracy in [0, 1]):
        raise ValueError("Invalid evaluation scores")
    return dict(precision=p, recall=r, f1=2*p*r/(p+r) if p+r else 0., accuracy=accuracy)


def discovery_scores(value, consequence, selected, scenario, protocol=None):
    actions = json.loads(consequence)
    retained = [action for action in actions if action["device_id"] in selected]
    if len(retained) == len(actions):
        return scores(value)
    if not retained:
        return scores(dict(precision=0., recall=0., accuracy=0.))
    from environment import Environment, DeviceDraft, Criteria, Action
    environment = Environment([DeviceDraft.model_validate(d) for d in parse_literal(scenario["devices"])], protocol=protocol)
    criteria = Criteria.model_validate(parse_literal(scenario["criteria"]))
    return scores(environment.evaluate(criteria, [Action.model_validate(a) for a in retained]))


def discovered_execution(log, tokens):
    """Filter downstream execution in memory; retain screening and shared composer costs."""
    selected = set(log.get("discovery", []))
    dispatches = log.get("calls", [])
    def allowed(call):
        args = call.get("args", {})
        device = args.get("device_id") if isinstance(args, dict) else None
        return not isinstance(device, str) or device in selected
    retained = [call for call in dispatches if allowed(call)]
    results = log.get("results", [])
    if isinstance(results, list) and len(results) == len(dispatches):
        results = [result for call, result in zip(dispatches, results) if allowed(call)]
    filtered = {}
    walls = {}
    for stage in STAGES:
        entries = tokens.get(stage, [])
        filtered[stage] = [c for c in entries if stage in ["setup", "discovery"]
                           or c.get("device_id") is None or c["device_id"] in selected]
        wall = sum(log["wall_time"].get(stage, [])) if "wall_time" in log else np.nan
        elapsed = lambda calls: sum(c.get("elapsed") or 0. for c in calls)
        wall -= elapsed(entries) - elapsed(filtered[stage])
        if stage == "orchestration" and len(retained) < len(dispatches):
            original = sum(log.get("wall_time", {}).get(stage, []))
            overhead = max(0., original-elapsed(entries))
            wall -= overhead*(1-len(retained)/len(dispatches))
        walls[stage] = [max(0., wall) if np.isfinite(wall) else np.nan]
    return dict(log, calls=retained, results=results, wall_time=walls), filtered


def load_results(directory, dataset_dir, models=None, methods=METHODS, devices=DEVICES, files=None, allow_partial=False):
    """Only complete conditions; pair IDs per figure instead of shrinking all models globally."""
    records, status = [], []
    csv.field_size_limit(2**30)
    for path in sorted(Path(directory).glob("result_D*_M0.csv") if files is None else files):
        match = re.fullmatch(r"result_D(\d+)_M0(?:_(pi|jetson|Matter|W3C|SmartThings|LANCE_with_descriptive_tools))?\.csv", path.name)
        if not match or int(match[1]) not in devices:
            continue
        d = int(match[1])
        protocol = match[2] if match[2] in ["Matter", "W3C", "SmartThings"] else None
        with (Path(dataset_dir) / f"dataset_D{d}_M0.csv").open(encoding="utf-8-sig", newline="") as stream:
            scenarios = {row["ID"]: row for row in csv.DictReader(stream)}
            gold = {key: parse_literal(row["criteria"])["expected_actions"] for key, row in scenarios.items()}
        with path.open(encoding="utf-8-sig", newline="") as stream:
            reader = csv.DictReader(stream)
            columns, rows = reader.fieldnames or [], list(reader)
        ids = [row["ID"] for row in rows]
        if len(ids) != len(set(ids)) or not set(ids) <= gold.keys():
            raise ValueError(f"Duplicate/unknown request IDs: {path}")
        for column in columns:
            if not column.startswith("EVALUATION_"):
                continue
            suffix = column.removeprefix("EVALUATION_")
            method = next((m for m in methods if suffix.endswith("_" + m)), None)
            if method is None:
                continue
            model = suffix[:-(len(method)+1)]
            if models is not None and model not in models:
                continue
            available = [row for row in rows if all(row.get(f"{key}_{suffix}") for key in ["EVALUATION", "LOGS", "TOKEN", "CONSEQUENCES"])]
            complete = len(available) == len(gold)
            status.append(dict(source=str(path.resolve()), D=d, model=model, method=method,
                               available=len(available), expected=len(gold), complete=complete))
            if not complete and not allow_partial:
                continue
            for row in available:
                try:
                    log, tokens = (parse_literal(row[f"{key}_{suffix}"]) for key in ["LOGS", "TOKEN"])
                    log, tokens = discovered_execution(log, tokens)
                    actions = gold[row["ID"]]
                    targets, selected = {a["device_id"] for a in actions}, set(log.get("discovery", []))
                    addressed = {args["device_id"] for c in log.get("calls", [])
                                 if isinstance(args := c.get("args"), dict) and isinstance(args.get("device_id"), str)}
                    errors = list(_errors(log.get("results", []))) + ([str(log["exception"])] if log.get("exception") else [])
                    calls = [call for entries in tokens.values() for call in entries]
                    api_error = any(re.search(r"(?:status code|HTTP)[:\s]*(?:4\d\d|5\d\d)", str(e), re.I) for e in errors)
                    quality = discovery_scores(row[column], row[f"CONSEQUENCES_{suffix}"], selected, scenarios[row["ID"]], protocol)
                    record = dict(D=d, model=model, method=method, ID=row["ID"], **quality,
                                  expected_actions=len(actions), target_devices=len(targets),
                                  error=bool(errors) and not api_error, api_error=api_error,
                                  discovery_precision=len(targets & selected)/len(selected) if selected else 0.,
                                  discovery_recall=len(targets & selected)/len(targets), selected_count=len(selected),
                                  discovery_coverage=np.mean([a["device_id"] in selected for a in actions]),
                                  assignment_coverage=np.mean([a["device_id"] in selected & addressed for a in actions]),
                                  decision_model=log.get("configuration", {}).get("decision_model", ""))
                    for stage in STAGES:
                        record[stage] = sum(log["wall_time"].get(stage, [])) if "wall_time" in log else np.nan
                        record[f"parallel_{stage}"] = parallel_stage_time(record[stage], tokens.get(stage, []))
                    record["mean_device_decision"] = mean_device_decision_time(tokens.get("discovery", []))
                    decisions = [c for c in tokens.get("discovery", []) if c.get("kind") == "decision"]
                    record["discovery_decision_input"] = sum(c.get("input_tokens") or np.nan for c in decisions) if decisions else np.nan
                    record["discovery_decision_elapsed"] = sum(c.get("elapsed") or np.nan for c in decisions) if decisions else np.nan
                    if not np.isfinite(record["discovery_decision_input"] + record["discovery_decision_elapsed"]):
                        record["discovery_decision_input"] = record["discovery_decision_elapsed"] = np.nan
                    record["sequential_time"] = sum(record[s] for s in STAGES)
                    record["parallel_time"] = sum(record[f"parallel_{s}"] for s in STAGES)
                    for kind in ["llm", "decision", "embedding"]:
                        record[f"{kind}_calls"] = sum(c.get("kind") == kind for c in calls)
                        record[f"{kind}_input"] = sum((c.get("input_tokens") or 0) for c in calls if c.get("kind") == kind)
                    record["llm_output"] = sum((c.get("output_tokens") or 0) for c in calls if c.get("kind") == "llm")
                    records.append(record)
                except (KeyError, ValueError, TypeError, SyntaxError) as error:
                    raise ValueError(f"{path}: {row['ID']} / {suffix}: {error}") from error
    columns = ["D", "model", "method", "ID", "expected_actions", "target_devices", *DETAIL_FIELDS, "decision_model", "mean_device_decision",
               "discovery_decision_input", "discovery_decision_elapsed", *STAGES, *[f"parallel_{s}" for s in STAGES]]
    return pd.DataFrame(records, columns=columns), status


def matched(data, groups):
    if data.empty:
        return data
    shared = set.intersection(*(set(g.ID) for _, g in data.groupby(groups)))
    return data[data.ID.isin(shared)].copy()


def interval(values, samples=2000, quantile=None):
    values = np.asarray(values, dtype=float)
    values = values[np.isfinite(values)]
    if not len(values):
        return np.nan, np.nan, np.nan
    rng = np.random.default_rng(20261024)
    draws = values[rng.integers(len(values), size=(samples, len(values)))]
    estimate = values.mean() if quantile is None else np.quantile(values, quantile)
    draws = draws.mean(axis=1) if quantile is None else np.quantile(draws, quantile, axis=1)
    return float(estimate), *np.quantile(draws, [.025, .975]).tolist()


def summarize(data, groups):
    if data.empty:
        return pd.DataFrame(columns=[*groups, "n", *DETAIL_FIELDS, "wall_p50", "wall_p95"])
    grouped = data.groupby(groups, sort=False)
    table = grouped[DETAIL_FIELDS].mean()
    table["n"] = grouped.size()
    for name, q in [("wall_p50", .5), ("wall_p95", .95)]:
        table[name] = grouped.sequential_time.quantile(q)
    return table.reset_index()


def model_name(model):
    if model.endswith("_cloud"):
        return {"beam_cloud": "Beam", "minimax_m3_1_flash_cloud": "MiniMax M3.1 Flash",
                "gemma4_31b_cloud": "Gemma 4 31B"}.get(model, model)
    for prefix, label in MODEL_NAMES.items():
        if model.startswith(prefix + "_"):
            size = re.match(r"e?\d+(?:_\d+)?b", model[len(prefix) + 1:])
            return label + (" " + size[0].replace("_", ".").upper() if size else "")
    return model


def save_figure(fig, output, name):
    if fig.legends and fig.get_layout_engine() is not None:
        fig.get_layout_engine().set(h_pad=.12)
    for ax in fig.axes:
        if ax.get_label() == "<colorbar>":
            continue
        ax.set_axisbelow(True)
        ax.title.set_fontweight("bold")
        ax.grid(False)
        if not ax.images:
            ax.grid(axis="y", color=".88", linewidth=.6)
        for spine in ax.spines.values():
            spine.set_color("black")
            spine.set_linewidth(.8)
    path = output / f"{name}.png"
    fig.savefig(path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return dict(status="ready", files=[str(path.resolve())])


def completeness(result, data, models, devices, methods=METHODS):
    present = set(data[["model", "D", "method"]].itertuples(index=False, name=None))
    missing = [dict(model=m, D=d, method=method) for m in models for d in devices for method in methods
               if (m, d, method) not in present]
    if missing:
        result.update(status="partial" if present else "pending", missing=missing)
    return result


def format_table(latex):
    latex = re.sub(r"(?m)^\\begin\{tabular\}\{([lcr])([^\n]*)\}",
                   lambda match: r"\begin{tabularx}{\linewidth}{" +
                   (match[1]+match[2] if "X" in match[2] else "X"+match[2]) + "}", latex)
    latex = latex.replace(r"\end{tabular}", r"\end{tabularx}")
    if r"\begin{tabularx}{\linewidth}{X" in latex:
        latex = re.sub(r"(?m)^(\\multirow\[[ctb]\]\{[^}]+\})\{\*\}",
                       lambda match: match[1] + "{=}", latex)
    latex = latex.replace(r"\textbf{LANCE}", r"\textbf{LANCE (ours)}")
    latex = re.sub(r"(?m)(^| & )LANCE(?= & | \\\\)", lambda match: match[1] + METHOD_LABELS["LANCE"], latex)
    def format_header(match):
        lines = []
        for line in match[1].splitlines():
            if line.endswith(r"\\"):
                cells = line[:-2].rstrip().split(" & ")
                line = " & ".join(r"\textbf{" + c + "}" if c.strip() and not c.startswith((r"\textbf{", r"\multicolumn{", r"\multirow[")) else c for c in cells) + r" \\"
            lines.append(line)
        return "\\toprule\n" + "\n".join(lines) + "\n\\midrule"
    return re.sub(r"\\toprule\n(.*?)\\midrule", format_header, latex, flags=re.S)


def save_table(table, output, name):
    if table.empty:
        return None
    alignment = "".join("c" if pd.api.types.is_numeric_dtype(table[c]) else "l" for c in table)
    token_columns = ["llm_input", "llm_output", "decision_input", "embedding_input"]
    formats = {c: "{:.0f}".format for c in token_columns if c in table}
    latex = table.to_latex(index=False, column_format=alignment, escape=True, na_rep="", float_format="%.2f", formatters=formats)
    return write_table(latex, output, name)


def write_table(latex, output, name, **metadata):
    path = output / f"{name}.txt"
    path.write_text(format_table(latex), encoding="utf-8")
    return dict(status="ready", files=[str(path.resolve())], **metadata)


def metric_style(table, higher, seconds=(), group_level=None, bold=True):
    """Use displayed precision for best-value ties, optionally within each model."""
    def highlight(column):
        values = column.round(0 if column.name == "LLM Input" else 2)
        direction = "max" if column.name in higher else "min"
        best = values.groupby(level=group_level, observed=True).transform(direction) if group_level is not None else values.agg(direction)
        return np.where(values.eq(best), "textbf:--rwrap;", "")
    formats = {c: "{:.0f}" if c == "LLM Input" else "{:.2f} s" if c in seconds else "{:.2f}" for c in table}
    style = table.style.format(formats, na_rep="", escape="latex").format_index(escape="latex")
    return style.apply(highlight) if bold else style


def legend(fig, colors=COLORS, frameon=True):
    fig.legend(handles=[Patch(color=colors[m], alpha=ALPHAS[m], label=METHOD_LABELS[m]) for m in METHODS],
               loc="outside upper center", ncol=len(METHODS), frameon=frameon)


def bars(ax, data, categories, field="f1"):
    for i, method in enumerate(METHODS):
        groups = [data[(data.model == c) & (data.method == method)][field] for c in categories]
        if field == "f1":
            mean, low, high = np.array([interval(g) for g in groups]).T*100
            errors = dict(yerr=np.maximum(0, [mean-low, high-mean]), capsize=1, error_kw={"elinewidth": .6, "alpha": ALPHAS[method]})
        else:
            mean, errors = [g.mean() for g in groups], {}
        ax.bar(np.arange(len(categories))+(i-2)*.16, mean, .15, color=COLORS[method], alpha=ALPHAS[method], **errors)
    ax.set_xticks(range(len(categories)), categories)
    ax.set_axisbelow(True)
    ax.grid(axis="y", alpha=.25)


def device_curves(axes, data, foreground=False, fields=("f1", "error"), show_interval=True):
    """Shared device curves; missing D conditions remain NaN gaps."""
    values = []
    for method, marker in zip(METHODS, ["s", "^", "D", "o", "*"]):
        group = data[data.method == method]
        ours = method == "LANCE"
        for ax, field in zip(axes, fields):
            factor = 1 if field == "llm_input" else 100
            mean, low, high = np.array([interval(group[group.D == d][field]) for d in DEVICES]).T*factor
            ax.plot(DEVICES, mean, color=COLORS[method], marker=marker, label=METHOD_LABELS[method],
                    alpha=ALPHAS[method],
                    linewidth=2.8 if ours else 1.1, markersize=6 if ours else 4,
                    **({"zorder": 4 if ours else 2} if foreground else {}))
            if show_interval:
                ax.fill_between(DEVICES, low, high, color=COLORS[method], alpha=.12 if ours else .06, linewidth=0)
            values.extend(dict(method=method, metric=field, D=d, value=float(m), low=float(lo), high=float(hi))
                          for d, m, lo, hi in zip(DEVICES, mean, low, high) if np.isfinite(m))
    axes[-1].set_xlabel("Devices")
    for ax in axes:
        ax.set_xticks(DEVICES, [f"D{d}" for d in DEVICES])
        ax.yaxis.set_major_locator(plt.MaxNLocator(nbins=5))
    return values


def plot_by_model(data, output):
    subset = data[data.D == TARGET_D]
    if subset.empty:
        return None
    models = sorted(subset.model.unique(), key=lambda m: (m.endswith("_cloud"), MODEL_PARAMETERS.get(m, np.inf), model_name(m)))
    colors = COLORS
    groups = [(label, [m for m in models if rule(m)]) for label, rule in [
        ("≤4B", lambda m: not m.endswith("_cloud") and MODEL_PARAMETERS.get(m, np.inf) <= 4e9),
        (">4B", lambda m: not m.endswith("_cloud") and 4e9 < MODEL_PARAMETERS.get(m, np.inf) < np.inf),
        ("Cloud / unspecified", lambda m: m.endswith("_cloud") or m not in MODEL_PARAMETERS)]]
    groups = [(label, ms) for label, ms in groups if ms]
    fig, axes = plt.subplots(2, len(groups), figsize=(14, 5.8), squeeze=False,
                             sharey="row", sharex="col", width_ratios=[len(ms) for _, ms in groups], layout="constrained")
    for j, (label, ms) in enumerate(groups):
        part = pd.concat([matched(subset[subset.model == m], ["method"]) for m in ms])
        bars(axes[0, j], part, ms)
        bars(axes[1, j], part, ms, field="parallel_time")
        for ax in axes[:, j]:
            ax.set_xticks(range(len(ms)), ["\n".join(model_name(m).rsplit(" ", 1)).replace(" Bolt\n", "\nBolt ")
                                          for m in ms], fontsize=8)
            ax.set_xlim(-.5, len(ms)-.5)
            ax.grid(False, axis="x")
            ax.grid(axis="y", color=".88", alpha=.8, linewidth=.6)
        axes[0, j].tick_params(labelbottom=False)
        axes[0, j].set_title("Cloud" if all(m.endswith("_cloud") for m in ms) else label, fontweight="bold")
    axes[0, 0].set_ylabel("F1 Score (%)")
    axes[1, 0].set_ylabel("Latency (s)")
    legend(fig, colors, frameon=True)
    for text in fig.findobj(matplotlib.text.Text):
        text.set_fontsize(text.get_fontsize()*1.25)
    result = completeness(save_figure(fig, output, "result_by_model"), subset, models, [TARGET_D])
    result["colors"] = colors
    return result


def plot_by_devices(data, output):
    models = DEVICE_MODELS
    data = data[data.model.isin(models) & data.method.isin(METHODS) & data.D.isin(DEVICES)]
    present = set(zip(data.model, data.method, data.D))
    if not all((m, method, d) in present for m in models for method in METHODS for d in DEVICES):
        return None
    data = matched(data, ["model", "D", "method"])
    if data.empty:
        return None
    averages = data.groupby(["D", "method", "ID"], as_index=False)[["f1", "llm_input", "error"]].mean()
    fig, axes = plt.subplots(3, 1, figsize=(5.2, 8.448), sharex=True, layout="constrained")
    values = device_curves(axes, averages, foreground=True, fields=("f1", "error", "llm_input"), show_interval=False)
    for ax in axes:
        ax.set_xlim(-1, 21)
        for line in ax.lines:
            line.set_markersize(line.get_markersize()*1.3)
    axes[0].set_ylabel("F1 Score (%)")
    axes[1].set(ylabel="Execution error rate (%)", ylim=(0, None))
    axes[2].set(ylabel="LLM Input", ylim=(0, None))
    axes[2].ticklabel_format(axis="y", style="plain", useOffset=False)
    fig.legend(*axes[0].get_legend_handles_labels(), loc="outside upper center", ncol=3, frameon=True)
    result = completeness(save_figure(fig, output, "result_by_devices"), data, models, DEVICES)
    result.update(models=models, values=values, shared_requests=int(data.ID.nunique()), definitions={
        "error": "Fraction of requests with execution/parsing errors; HTTP API failures excluded; lower is better",
        "f1": "Absolute mean per-request F1",
        "llm_input": "Mean LLM input tokens per request after discovery-boundary filtering; excludes decision and embedding inputs",
        "aggregation": "Equal-weight mean across four models within each request, then mean across requests; matched IDs across all models, D and methods",
        "interval": "Pointwise request-bootstrap 95% intervals recorded but not plotted",
        "models": "Qwen 3.5 4B and Gemma 4 E2B, E4B and 12B; local Q4_K_M weights",
        "stability": "Within-run robustness to device-count changes, not repeated-run variance"})
    return result


def plot_by_tasks(data, output):
    models = DEVICE_MODELS
    data = data[data.model.isin(models) & data.method.isin(METHODS) & data.D.isin(DEVICES)].copy()
    if data.empty:
        return None
    present = set(zip(data.model, data.method, data.D))
    if not all((m, method, d) in present for m in models for method in METHODS for d in DEVICES):
        return None
    data = matched(data, ["model", "D", "method"])
    data["task_group"] = np.select([data.target_devices.gt(1), data.expected_actions.gt(1)], [2, 1], default=0)
    if data.groupby("ID").task_group.nunique().gt(1).any():
        raise ValueError("Request structure changes across models or D")
    labels = ["Single device\nSingle action", "Single device\nMultiple actions", "Multiple devices\nMultiple actions"]
    colors = ["#4C78A8", "#F2A541", "#59A14F"]
    requests = data.groupby(["model", "method", "ID", "task_group"], as_index=False)[["f1", "error"]].mean()
    requests = requests.groupby(["method", "ID", "task_group"], as_index=False)[["f1", "error"]].mean()
    sizes = requests.groupby("task_group").ID.nunique()
    fig, axes = plt.subplots(2, 1, figsize=(5.2, 3.7), sharex=True, layout="constrained")
    values = []
    for ax, metric in zip(axes, ["f1", "error"]):
        for i, method in enumerate(METHODS):
            groups = [requests[(requests.method == method) & requests.task_group.eq(g)][metric] for g in range(3)]
            mean, low, high = np.array([interval(g) for g in groups]).T*100
            ax.bar(i+(np.arange(3)-1)*.24, mean, width=.22, color=colors, alpha=ALPHAS[method],
                   yerr=np.maximum(0, [mean-low, high-mean]), capsize=2,
                   error_kw={"elinewidth": .8, "alpha": ALPHAS[method]})
            values.extend(dict(model="Four-model average", method=method, task_group=labels[g].replace("\n", "; "), metric=metric,
                               n=len(groups[g]), value=float(mean[g]), low=float(low[g]), high=float(high[g])) for g in range(3))
        ax.set_xticks(range(len(METHODS)), [METHOD_LABELS[m] for m in METHODS], fontsize=8.5)
        for tick in ax.get_xticklabels():
            if tick.get_text() == METHOD_LABELS["LANCE"]:
                tick.set_fontweight("bold")
        ax.set_xlim(-.5, len(METHODS)-.5)
        ax.set_ylim(bottom=0)
        ax.tick_params(labelsize=8.5)
    axes[1].set_xlabel("Approach", fontsize=8.5)
    axes[0].set_ylabel("F1 Score (%)", fontsize=8.5)
    axes[1].set_ylabel("Execution error rate (%)", fontsize=8.5)
    fig.legend(handles=[Patch(facecolor=color, label=f"{label}\n(n={sizes.get(g, 0)})") for g, (color, label) in enumerate(zip(colors, labels))],
               loc="outside upper center", ncol=3, frameon=True, fontsize=8.5)
    result = completeness(save_figure(fig, output, "result_by_tasks"), data, models, DEVICES)
    result.update(models=models, datasets=DEVICES, values=values, definitions={
        "groups": "Ground-truth unique target devices and expected API action count, not linguistic subtask count",
        "aggregation": "Average D0/D5/D10/D15/D20 within each request/model, then average the four models equally, then macro mean within each request group; matched IDs across all models/D/methods",
        "interval": "95% bootstrap intervals over unique request IDs after averaging D and models; n is unique requests, not repeated model/D observations",
        "filter": "Existing discovery-boundary execution filter; HTTP failures retained in F1, excluded from execution-error rate",
        "interpretation": "Descriptive subgroup comparison; task structures differ in request content, so differences are not isolated causal effects"})
    save_table(pd.DataFrame(values), output, "task_structure_summary")
    return result


def plot_by_protocol(data, directory, dataset_dir, output):
    model = PROTOCOL_MODELS[0]
    protocols = ["Mixed", "Matter", "W3C", "SmartThings"]
    parts = [data[(data.model == model) & data.method.isin(METHODS)].assign(protocol="Mixed")]
    conditions = []
    for protocol in protocols[1:]:
        paths = list(directory.glob(f"result_D*_M0_{protocol}.csv"))
        part, status = load_results(directory, dataset_dir, [model], files=paths)
        conditions.extend(dict(item, protocol=protocol) for item in status)
        parts.append(part.assign(protocol=protocol))
    frame = pd.concat(parts, ignore_index=True)
    if frame.empty:
        return None
    frame = matched(frame, ["protocol", "method", "D"])
    save_table(summarize(frame, ["protocol", "D", "model", "method"]), output, "protocol_summary")
    per_d = frame.groupby(["protocol", "method", "D"])[["f1", "error"]].mean()
    averages = per_d.groupby(level=["protocol", "method"]).mean()*100
    averages.loc[per_d.groupby(level=["protocol", "method"]).size().lt(len(DEVICES))] = np.nan
    fig, axes = plt.subplots(2, 1, figsize=(5.2, 4.68), sharey=True, layout="constrained")
    fig.get_layout_engine().set(hspace=.12)
    for ax, metric, title, color in zip(axes, ["f1", "error"],
            ["F1 Score (%)", "Execution Error Rate (%)"], ["Blues", "YlOrRd"]):
        matrix = averages[metric].unstack("protocol").reindex(index=METHODS, columns=protocols)
        finite = matrix.to_numpy()[np.isfinite(matrix.to_numpy())]
        low = np.floor(finite.min()/5)*5 if metric == "f1" and len(finite) else 0
        high = max(low+5, np.ceil(finite.max()/5)*5) if len(finite) else 100
        cmap = plt.get_cmap(color).with_extremes(bad=".94")
        cells = ax.imshow(matrix, cmap=cmap, vmin=low, vmax=high, aspect="auto")
        ax.set_xticks(range(len(protocols)), protocols)
        ax.set_yticks(range(len(METHODS)), [METHOD_LABELS[m] for m in METHODS])
        ax.set_title(title, pad=12)
        ax.tick_params(length=0, pad=7)
        best = matrix.max() if metric == "f1" else matrix.min()
        for i, j in np.ndindex(matrix.shape):
            value = matrix.iloc[i, j]
            if np.isfinite(value):
                rgb = np.array(cells.cmap(cells.norm(value))[:3])
                ax.text(j, i, f"{value:.2f}", ha="center", va="center",
                        color="white" if rgb @ [.2126, .7152, .0722] < .5 else "black",
                        fontweight="bold" if np.isclose(value, best.iloc[j]) else "normal")
        fig.colorbar(cells, ax=ax, shrink=.9, pad=.025)
    for ax in axes:
        ax.get_yticklabels()[-1].set_fontweight("bold")
    result = save_figure(fig, output, "result_by_protocol")
    present = set(zip(frame.protocol, frame.method, frame.D))
    missing = [dict(protocol=p, method=m, D=d) for p in protocols for m in METHODS for d in DEVICES if (p, m, d) not in present]
    result.update(status="partial" if missing else "ready", model=model, datasets=DEVICES,
                  shared_requests=int(frame.ID.nunique()), missing=missing, conditions=conditions,
                  values=[dict(protocol=p, method=m, D=int(d), metric=k, value=float(v*100))
                          for (p, m, d), row in per_d.iterrows() for k, v in row.items()],
                  averages=averages.reset_index().to_dict("records"),
                  definitions={"scope": "Equal-weight mean across D0/D5/D10/D15/D20; common request IDs; absolute percentages",
                               "metrics": "Mean request-level F1 and execution-parsing error rate (%); HTTP failures excluded from error rate but retained in quality scores",
                               "missing": "Cells require all five completed D conditions; otherwise blank, never extrapolated or zero-filled",
                               "filter": "Same discovery-boundary action/cost filter as other manuscript artifacts"})
    return result


def plot_by_settings(directory, output, dataset_dir=Path("dataset")):
    path = directory / "result_D10_M0_LANCE_settings.csv"
    if not path.exists():
        return None
    raw = pd.read_csv(path, dtype=str, keep_default_na=False,
                      usecols=lambda column: column == "ID" or column.startswith(("EVALUATION_", "LOGS_", "CONSEQUENCES_")))
    pattern = re.compile(r"EVALUATION_(.+)_LANCE_(.+)_noul_(0_[1-9])$")
    records = []
    if raw.ID.duplicated().any():
        raise ValueError(f"Duplicate request IDs: {path}")
    with (dataset_dir / "dataset_D10_M0.csv").open(encoding="utf-8-sig", newline="") as stream:
        scenarios = {row["ID"]: row for row in csv.DictReader(stream)}
        targets = {key: {a["device_id"] for a in parse_literal(row["criteria"])["expected_actions"]}
                   for key, row in scenarios.items()}
    for column in raw:
        match = pattern.fullmatch(column)
        if not match:
            continue
        if raw[column].eq("").any():
            return None
        log_column = column.replace("EVALUATION_", "LOGS_", 1)
        consequence_column = column.replace("EVALUATION_", "CONSEQUENCES_", 1)
        if any(c not in raw or raw[c].eq("").any() for c in [log_column, consequence_column]):
            return None
        for i, (request, value) in enumerate(zip(raw.ID, raw[column])):
            log = parse_literal(raw.at[i, log_column])
            selected = len(set(log["discovery"])) if "discovery" in log else np.nan
            recall = len(targets[request] & set(log["discovery"]))/len(targets[request]) if "discovery" in log else np.nan
            quality = discovery_scores(value, raw.at[i, consequence_column], set(log.get("discovery", [])), scenarios[request])
            records.append(dict(model=match[1], decision=match[2], threshold=float(match[3].replace("_", ".")),
                                ID=request, selected_count=selected, discovery_recall=recall, **quality))
    if not records:
        return None
    frame = pd.DataFrame(records)
    table = frame.groupby(["model", "decision", "threshold"])[SCORE_FIELDS + ["selected_count", "discovery_recall"]].mean().reset_index()
    save_table(table, output, "settings_summary")
    models = list(frame.model.unique())
    fig, axes = plt.subplots(len(models), 3, figsize=(12.6, 2.8*len(models)), sharey=True,
                             squeeze=False, layout="constrained")
    decisions = sorted(frame.decision.unique(), key=lambda d: (DECISION_PARAMETERS[d], model_name(d)))
    for row, model in enumerate(models):
        for ax, metric, title, factor, cmap in zip(axes[row], ["discovery_recall", "selected_count", "f1"],
                ["Discovery Recall (%)", "Selected Devices", "F1 Score (%)"],
                [100, 1, 100], ["Greens", "YlOrBr", "Blues"]):
            values = table[metric].dropna()*factor
            low, high = (values.min(), values.max()) if len(values) else (0, 1)
            if high <= low:
                high = low + 1
            matrix = table[table.model == model].pivot(index="decision", columns="threshold", values=metric).reindex(columns=np.arange(1, 10)/10)*factor
            matrix = matrix.reindex(decisions)
            cells = ax.imshow(matrix, cmap=cmap, vmin=low, vmax=high, aspect="auto")
            ax.set_xticks(range(len(matrix.columns)), [f"{v:.1f}" for v in matrix.columns])
            ax.set_yticks(range(len(matrix.index)), ["\n".join(model_name(d).rsplit(" ", 1)) for d in matrix.index])
            for i in range(len(matrix.index)):
                for j, value in enumerate(matrix.iloc[i]):
                    if np.isfinite(value):
                        dark = cells.norm(value) > .6
                        label = f"{value:.2f}" if metric == "selected_count" else ("100" if f"{value:.1f}" == "100.0" else f"{value:.1f}")
                        ax.text(j, i, label,
                                ha="center", va="center", color="white" if dark else "black", fontsize=8)
            fig.colorbar(cells, ax=ax)
            ax.set_title(title)
            ax.set_xlabel(r"Discovery threshold ($\epsilon$)"); ax.set_ylabel("")
    result = save_figure(fig, output, "result_by_settings")
    result["selected_count_definition"] = "Mean number of unique devices passing discovery per request"
    result["recall_definition"] = "Mean per-request fraction of unique gold target devices included in discovery; independent of downstream execution"
    result["status"] = "partial" if table.groupby(["model", "decision"]).threshold.nunique().lt(9).any() else "ready"
    return result


def plot_by_phase(data, output):
    models = STABILITY_MODELS
    outcomes = {"exact": ("Successful Completion", "#2A9D8F"),
                "discovery": ("Discovery Omission", "#264653"),
                "assignment": ("Assignment Omission", "#E9C46A"),
                "error": ("Execution Error", "#E76F51"),
                "mismatch": ("Action Mismatch", "#9DA9B5")}
    data = data[data.D.isin(DEVICES) & data.method.isin(METHODS)]
    fig, axes = plt.subplots(1, len(models), figsize=(12.6, 3.8), sharex=True, sharey=True,
                             squeeze=False, layout="constrained")
    counts = []
    for ax, model in zip(axes[0], models):
        part = matched(data[data.model == model], ["D", "method"])
        part["outcome"] = np.select([
            part.api_error, part.accuracy.eq(1) & ~part.error,
            part.discovery_coverage.lt(1), part.assignment_coverage.lt(1), part.error],
            ["error", "exact", "discovery", "assignment", "error"], default="mismatch")
        bottom = np.zeros(len(METHODS))
        for outcome, (label, color) in outcomes.items():
            rates = part.assign(share=part.outcome.eq(outcome)).groupby(["method", "D"]).share.mean()
            values = rates.unstack("D").reindex(index=METHODS, columns=DEVICES).mean(axis=1, skipna=False).to_numpy()*100
            bars = ax.barh(range(len(METHODS)), values, left=bottom, color=color, height=.7,
                           edgecolor="white", linewidth=.5)
            for bar, method in zip(bars, METHODS):
                bar.set_alpha(ALPHAS[method])
            rgb = np.array(matplotlib.colors.to_rgb(color))
            linear = np.where(rgb <= .04045, rgb/12.92, ((rgb+.055)/1.055)**2.4)
            text_color = "white" if linear @ [.2126, .7152, .0722] < .179 else "black"
            ax.bar_label(bars, labels=[f"{v:.0f}%" if v >= 8 else "" for v in values],
                         label_type="center", fontsize=8, color=text_color)
            bottom += np.array(values)
        for method in METHODS:
            for d in DEVICES:
                group = part[(part.method == method) & (part.D == d)]
                counts.append(dict(model=model, method=method, D=d, n=len(group),
                                   **{key: int(group.outcome.eq(key).sum()) for key in outcomes}))
        ax.set_title(model_name(model))
        ax.set_xlim(0, 100)
        ax.set_xticks([0, 25, 50, 75, 100])
        ax.set_yticks(range(len(METHODS)), [METHOD_LABELS[m] for m in METHODS])
        ax.set_ylim(len(METHODS)-.5, -.5)
        ax.set_xlabel("User requests (%)")
        for label in ax.get_yticklabels():
            if label.get_text() == METHOD_LABELS["LANCE"]:
                label.set_fontweight("bold")
        if part.empty:
            ax.text(.5, .5, "Pending", transform=ax.transAxes, ha="center")
    fig.legend(handles=[Patch(facecolor=color, label=label) for label, color in outcomes.values()],
               loc="outside upper center", ncol=3, frameon=True)
    result = completeness(save_figure(fig, output, "result_by_phase"), data, models, DEVICES)
    result["counts"] = counts
    result["datasets"] = DEVICES
    result["definitions"] = {
        "classification": "Exclusive request categories: HTTP API failures included in execution errors; otherwise error-free exact match, missing discovery targets, missing assignment targets, execution/parsing error, remaining mismatch; not chronological causal attribution",
        "denominator": "All matched input user requests (scenarios), not expected action count; API failures remain in the denominator",
        "aggregation": "Equal-weight mean of outcome percentages across D0/D5/D10/D15/D20; common request IDs across D and methods within each model; missing D leaves that method blank",
        "mismatch": "May reflect instruction meaning, controller decisions, or gold ambiguity; not an isolated orchestration loss",
        "coverage": "Assignment coverage checks target devices, not completeness of instruction meaning"}
    return result


def table_ablation(data, output):
    devices = [0, 10, 20]
    data = data[data.method.isin(ABLATIONS) & data.D.isin(devices)]
    if data.empty:
        return None
    if data.model.nunique() != 1:
        raise ValueError("The ablation table expects one generator model")
    data = matched(data, ["method", "D"])
    metrics = {"discovery_recall": "Discovery Recall", "f1": "F1 Score", "error": "Error Rate",
               "llm_input": "LLM Input", "parallel_discovery": "Discovery",
               "parallel_composition": "Composition", "parallel_orchestration": "Orchestration",
               "parallel_time": "Total"}
    latency_columns = ["Discovery", "Composition", "Orchestration", "Total"]
    labels = {"LANCE": "LANCE", "LANCE_no_decision": "w/o decision models",
              "LANCE_no_discovery": "w/o selection", "LANCE_no_separation": "w/o service-tailored tools",
              "LANCE_no_instruction": "w/o natural instruction"}
    index = pd.MultiIndex.from_product([ABLATIONS, devices], names=["method", "D"])
    table = data.groupby(["method", "D"])[list(metrics)].mean().reindex(index)
    table[["discovery_recall", "error", "f1"]] *= 100
    table = table.rename(columns=metrics)
    table.index = pd.MultiIndex.from_tuples([(labels[m], f"D{d}") for m, d in table.index])
    style = metric_style(table, [], latency_columns, bold=False)
    caption = f"Ablation study of LANCE with {model_name(data.model.iloc[0])} on D0, D10, and D20."
    latex = style.to_latex(hrules=True, column_format="lc"+"c"*len(table.columns), multirow_align="c",
                          clines="skip-last;data", caption=caption, label="tab:ablation")
    latex = re.sub(r"\\cline\{\d+-\d+\}", lambda _: r"\midrule", latex)
    latex = latex.replace("\\midrule\n\\bottomrule", r"\bottomrule").replace("{LANCE}", r"{\textbf{LANCE (vanilla)}}")
    boundary = f"\\midrule\n\\multirow[c]{{{len(devices)}}}{{*}}{{{labels[ABLATIONS[1]]}}}"
    latex = latex.replace(boundary, "\\midrule\n" + boundary, 1)
    headers = ["Configuration", "D", *list(metrics.values())[:-4]]
    header = " & ".join([""]*6) + r" & \multicolumn{4}{c}{\textbf{Latency}} \\" + "\n" + r"\cmidrule(lr){7-10}" + "\n"
    header += " & ".join(r"\textbf{" + name + "}" for name in [*headers, *latency_columns]) + r" \\"
    latex = latex.replace(" & ".join(["", "", *metrics.values()]) + r" \\", header, 1)
    result = write_table(latex, output, "table2_ablation")
    result["recall_definition"] = "Mean per-request fraction of unique gold target devices included in discovery (%)"
    return completeness(result, data, list(data.model.unique()), devices, ABLATIONS)


def table_by_model(data, output):
    if data.empty:
        return None
    models = [m for m in DEVICE_MODELS if m in set(data.model)]
    if not models:
        return None
    paired = pd.concat([matched(data[data.model == model], ["method"]) for model in models])
    table = summarize(paired, ["model", "method"])
    table[SCORE_FIELDS] *= 100
    table["model"] = pd.Categorical(table.model, categories=models, ordered=True)
    table["method"] = pd.Categorical(table.method, categories=METHODS, ordered=True)
    table = table.sort_values(["model", "method"])
    table["model"] = table.model.map(model_name)
    metrics = {"precision": "Precision", "recall": "Recall", "f1": "F1 Score", "accuracy": "Accuracy",
               "error": "Error Rate", "llm_input": "LLM Input", "llm_calls": "LLM Calls", "parallel_time": "Latency"}
    table["error"] *= 100
    table = table.rename(columns={"model": "Model", "method": "Method", **metrics})
    table = table.set_index(["Model", "Method"])[list(metrics.values())]
    table.index.names = [None, None]
    style = metric_style(table, list(metrics.values())[:4], ["Latency"], group_level=0)
    latex = style.to_latex(hrules=True, column_format="ll"+"c"*len(table.columns), multirow_align="c", clines="skip-last;data",
                   caption=f"Performance and inference cost comparison on D{TARGET_D}. Best results for each model are in bold.",
                   label="tab:details")
    latex = re.sub(r"\\cline\{\d+-\d+\}", lambda _: r"\midrule", latex)
    latex = latex.replace("\\midrule\n\\bottomrule", r"\bottomrule").replace(" & LANCE &", r" & \textbf{LANCE} &")
    return write_table(latex.replace(" &  & Precision", "Model & Method & Precision", 1), output, "table1_details", models=models)


HARDWARE_LABELS = {"desktop": "Desktop", "jetson": "Jetson Orin Nano Super", "pi": "Raspberry Pi 5 (16GB)"}


def table_models(output):
    catalog = json.loads(Path(__file__).with_name("model_catalog.json").read_text(encoding="utf-8"))
    references, rows = catalog["references"], []
    counts = MODEL_PARAMETERS | DECISION_PARAMETERS
    for model in catalog["models"]:
        key = re.sub(r"[^a-zA-Z0-9]", "_", model["code"])
        reference = references[model["reference"]]
        quantization = re.search(r"(q\d+_[A-Za-z0-9_]+|fp16)$", model["code"])
        quantization = model.get("quantization", quantization[0].upper() if quantization else "Native")
        notes = model.get("notes", "Instruct" if "instruct" in model["code"] else
                          "Post-trained" if model["type"] == "LLM" else "")
        if model["reference"] == "minimax31flash":
            notes = "Cloud"
        rows.append({"Type": model["type"],
                     "Model": model["name"],
                     "Parameters": model["parameters"], "Quantization": quantization.replace("_", r"\_"),
                     "Release Date": model.get("release", reference["release"]), "Developer": reference.get("group", reference["author"]), "Notes": notes,
                     "count": model.get("parameter_count", counts.get(key, np.inf))})
    table = pd.DataFrame(rows)
    table["Type"] = pd.Categorical(table.Type, categories=["LLM", "Decision", "Embedding"], ordered=True)
    table["latest"] = table.groupby(["Type", "Model"], observed=True)["Release Date"].transform("max")
    table = table.sort_values(["Type", "latest", "Model", "Release Date", "count"], ascending=[True, False, True, False, True])
    citations = {name: ",".join(dict.fromkeys(references[m["reference"]].get("citation_key", m["reference"])
                 for m in catalog["models"] if m["name"] == name)) for name in table.Model.unique()}
    table["Model"] = table.Model.map(lambda name: name + r"~\cite{" + citations[name] + "}")
    table = table.drop(columns=["count", "latest"]).set_index(["Type", "Model"])
    caption = "Models used for dataset synthesis and experimental evaluation."
    latex = table.style.to_latex(hrules=True, column_format="llccccX", multirow_align="c", sparse_index=True,
                                environment="table*", position="t", caption=caption, label="tab:models")
    latex = latex.replace(r"\begin{table*}[t]", "\\begin{table*}[t]\n\\centering\n\\scriptsize\n\\setlength{\\tabcolsep}{3pt}")
    # Keep a single header row when grouping models by type and name.
    latex = latex.replace(" &  & Parameters", "Type & Model & Parameters", 1)
    latex = latex.replace("Type & Model" + " & "*len(table.columns) + " \\\\\n", "")
    for (_, name), group in table.groupby(level=["Type", "Model"], sort=False, observed=True):
        if len(group) > 1:
            cell = f" & {name} &"
            latex = latex.replace(cell, f" & \\multirow[c]{{{len(group)}}}{{*}}{{{name}}} &", 1).replace(cell, " &  &")
    previous_type = None
    for kind, name in table.index.unique():
        if kind == previous_type:
            latex = re.sub(r"(?m)^(?=.*" + re.escape(name) + r")", lambda _: f"\\cmidrule(lr){{2-{len(table.columns)+2}}}\n", latex, count=1)
        previous_type = kind
    for group in ["Decision", "Embedding"]:
        latex = re.sub(r"(?m)^(?=(?:\\multirow\[c\]\{\d+\}\{\*\}\{" + group + r"\}|" + group + r" &))",
                       lambda _: "\\midrule\n", latex, count=1)
    # Top-align type labels independently of spacing added by model separators.
    latex = re.sub(r"\\multirow\[c\](\{\d+\}\{\*\}\{(?:LLM|Decision|Embedding)\})",
                   lambda match: r"\multirow[t]" + match[1], latex)
    # Merge adjacent developers within each type, without reordering release dates.
    developers = table.reset_index()[["Type", "Developer"]]
    runs = developers.ne(developers.shift()).any(axis=1).cumsum()
    lines = latex.splitlines()
    row_lines = [i for i, line in enumerate(lines) if line.endswith(r"\\")][1:]
    for _, group in developers.groupby(runs):
        if len(group) < 2:
            continue
        for offset, row in enumerate(group.index):
            cells = lines[row_lines[row]].split(" & ")
            cells[5] = f"\\multirow[c]{{{len(group)}}}{{*}}{{{cells[5]}}}" if offset == 0 else ""
            lines[row_lines[row]] = " & ".join(cells)
        for i in range(row_lines[group.index[0]]+1, row_lines[group.index[-1]]):
            if lines[i].startswith(r"\cmidrule"):
                lines[i] = r"\cmidrule(lr){2-5}\cmidrule(lr){7-7}"
    latex = "\n".join(lines) + "\n"
    write_table(latex, output, "table_models")
    entries, sources = [], [f"Checked: {catalog['checked']}", f"Scope: current experiment.py/settings.py and synthesizer.py defaults; {len(catalog['models'])} model tags.",
                            "Synthesis roles are code defaults, not immutable provenance recorded in the generated dataset.",
                            "Sorting: latest release date per model name, descending within type; variants by release date descending, then installed parameter count ascending.",
                            "Citation policy: official supplied citation where available; otherwise official announcement/model card."]
    sources.append("Quantization: explicit experiment tags; Ornith 1.5 9B default Q4_K_M verified at https://ollama.com/library/ornith-1.5:9b . Cloud weights are displayed as Native per the experiment reporting convention.")
    bib_references = {r.get("citation_key", key): key for key, r in references.items()}
    for key, reference in references.items():
        citation_key = reference.get("citation_key", key)
        citation = reference | reference.get("bibtex", {})
        author = citation["author"]
        author = author if " and " in author or author == "Jared Palmer" else "{" + author + "}"
        fields = dict(author=author, title="{" + citation["title"] + "}", year=citation["year"], url=citation["url"])
        if citation.get("eprint"):
            fields.update(eprint=citation["eprint"], archivePrefix="arXiv", primaryClass="cs.CL")
        if bib_references[citation_key] == key:
            entries.append("@misc{" + citation_key + ",\n" + "\n".join(f"  {k} = {{{v}}}," for k, v in fields.items()) + "\n}")
        codes = ", ".join(m["code"] for m in catalog["models"] if m["reference"] == key)
        sources.append(f"\n[{key}] {codes}\nCitation key: {citation_key}\nCitation: {citation['url']}\nRelease: {reference['release']}\nSource: {reference.get('release_source', reference['url'])}\nBasis: {reference['basis']}")
        sources.extend(f"Variant release: {m['code']} — {m['release']}" for m in catalog["models"]
                       if m["reference"] == key and "release" in m)
        if reference.get("parameter_source"):
            sources.append(f"Parameters: {reference['parameter_source']}")
        if reference.get("developer_source"):
            sources.append(f"Developer: {reference['group']}\nDeveloper source: {reference['developer_source']}")
    (output / "model_citations.bib").write_text("\n\n".join(entries) + "\n", encoding="utf-8")
    (output / "model_sources.txt").write_text("\n".join(sources) + "\n", encoding="utf-8")
    return dict(status="ready", files=[str((output / name).resolve()) for name in ["table_models.txt", "model_citations.bib", "model_sources.txt"]])


def load_hardware(directory, dataset_dir):
    records, conditions = [], []
    for hardware in HARDWARE_LABELS:
        paths = list(directory.glob("result_D*_M0.csv" if hardware == "desktop" else f"result_D*_M0_{hardware}.csv"))
        frame, status = load_results(directory, dataset_dir, ["beam_cloud"], ["LANCE"],
                                     files=paths, devices=DEVICES, allow_partial=True)
        conditions.extend(dict(item, hardware=hardware) for item in status)
        if not frame.empty:
            if not frame.decision_model.eq("tev1:4b-q4_K_M").all():
                raise ValueError(f"Expected local Tev1 4B Q4_K_M for {hardware}")
            records.append(frame.assign(hardware=hardware))
    if not records:
        return pd.DataFrame(), {}
    frame = matched(pd.concat(records), ["hardware", "D"])
    present = set(zip(frame.hardware, frame.D))
    metadata = dict(status="partial" if any((h, d) not in present for h in HARDWARE_LABELS for d in DEVICES)
                    or any(not c["complete"] for c in conditions) else "ready",
                    shared_requests=int(frame.ID.nunique()), conditions=conditions)
    return frame, metadata


def table_hardware(directory, dataset_dir, output):
    frame, metadata = load_hardware(directory, dataset_dir)
    if frame.empty:
        return None
    groups = frame.groupby(["hardware", "D"])
    table = groups.mean_device_decision.mean().to_frame("Decision Latency")
    totals = groups[["discovery_decision_input", "discovery_decision_elapsed"]].sum(min_count=1)
    table["Decision Throughput"] = totals.discovery_decision_input / totals.discovery_decision_elapsed.where(totals.discovery_decision_elapsed > 0)
    table = table.groupby(level="hardware").mean()
    table = table.reindex(list(HARDWARE_LABELS)).rename(index=HARDWARE_LABELS)
    table.index.name = None
    caption = "Discovery performance of LANCE across hardware platforms."
    latex = table.style.format({"Decision Latency": "{:.2f} s", "Decision Throughput": "{:.2f} tokens/s"}, na_rep="--").format_index(escape="latex").to_latex(
        hrules=True, column_format="lcc", caption=caption, label="tab:hardware")
    result = write_table(latex.replace(" & Decision Latency", "Hardware & Decision Latency", 1), output, "table3_hardware")
    result.update(metadata)
    result["definitions"] = {"setup": "LANCE with cloud Beam and local Tev1 4B Q4_K_M; identical request IDs across available hardware/D conditions",
                             "time": "Decision Latency: average across requests of mean per-device decision invoke elapsed time. Multiple calls on the same device are summed before averaging devices. Includes all screened devices, even rejected ones; excludes stage overhead and LLM/embedding calls. Assumes concurrent devices; not the maximum completion time or measured distributed latency",
                             "aggregation": "Equal-weight mean across D0/D5/D10/D15/D20; within each D, Decision Latency is request-average per-device decision elapsed seconds",
                             "throughput": "For each D: total discovery decision input tokens / total discovery decision invoke elapsed seconds; then equal-weight mean across D. Input processing, not output generation or summed parallel throughput"}
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--code", default="", help="Result folder; default: latest")
    args = parser.parse_args()
    folders = sorted(p for p in Path("results").iterdir() if p.is_dir() and any(FILE_PATTERN.fullmatch(f.name) for f in p.glob("*.csv")))
    if not args.code and not folders:
        parser.error("No result folders found")
    directory = Path("results") / args.code if args.code else folders[-1]
    if not directory.is_dir():
        parser.error(f"Result folder not found: {directory}")
    output = directory / "plots_tsc"
    output.mkdir(exist_ok=True)
    plt.style.use("default")
    print(f"Reading {directory}", flush=True)
    started = perf_counter()
    data, conditions = load_results(directory, Path("dataset"), methods=METHODS + ABLATIONS[1:])
    regular = data[data.method.isin(METHODS)]
    print(f"Loaded {len(data):,} complete evaluations in {perf_counter()-started:.2f}s", flush=True)
    figures = {"figure1_by_model": plot_by_model(regular, output),
               "figure2_by_devices": plot_by_devices(regular, output),
               "figure3_by_protocol": plot_by_protocol(regular, directory, Path("dataset"), output),
               "figure4_by_settings": plot_by_settings(directory, output),
               "figure5_by_phase": plot_by_phase(regular, output),
               "figure7_by_tasks": plot_by_tasks(regular, output)}
    ablation = data[data.model.isin(ABLATION_MODELS) & data.method.isin(ABLATIONS)]
    tables = {"table1_details": table_by_model(regular[regular.D == TARGET_D], output),
              "table2_ablation": table_ablation(ablation, output) if ablation.method.isin(ABLATIONS[1:]).any() else None,
              "table3_hardware": table_hardware(directory, Path("dataset"), output),
              "table_models": table_models(output)}
    if tables["table1_details"] is not None:
        completeness(tables["table1_details"], regular[regular.D == TARGET_D], tables["table1_details"]["models"], [TARGET_D])
    save_table(summarize(data, ["D", "model", "method"]), output, "summary")
    manifest = dict(figures=figures, tables=tables, conditions=conditions, colors=COLORS, alphas=ALPHAS,
                    representative_models=REPRESENTATIVE_MODELS, target_D=TARGET_D,
                    definitions={"quality": "Macro request P/R/F1 and exact match after removing actions outside discovery; saved evaluations reused when no action is removed, original CSV unchanged",
                                 "execution_filter": "Downstream calls, results, tokens and call counts outside discovery are excluded. Discovery screening and shared composer costs remain.",
                                 "time": "Excluded downstream invoke durations are subtracted; unattributed orchestration overhead is prorated by retained dispatches. parallel_time uses estimated device barriers, not measured deployment latency.",
                                 "phase": "Equal-weight mean of exclusive request outcome percentages across D0/D5/D10/D15/D20; missing discovery/assignment targets, errors and post-assignment mismatches. Observational categories, not causal phase attribution.",
                                 "D0": "Base environment, not zero devices",
                                 "missing": "Incomplete conditions omitted; absent results never zero-filled",
                                 "api_error": "HTTP 4xx/5xx failures kept in quality scores and reported separately"})
    (output / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    for name, result in {**figures, **tables}.items():
        print(f"{name}: {result['status'] if result is not None else None}")
    print(f"Output: {output.resolve()}")


if __name__ == "__main__":
    main()
