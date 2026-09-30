"""Table-7-style summaries of labeled profiling or verifier-proxy searches.

Held-out outcomes are attached only after selection. Seed standard deviations
describe selector variability on the fixed question split, not uncertainty
about population accuracy. Full per-run records accompany every report.
"""

from __future__ import annotations

import csv
import json
import math
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


def _mean(values: Sequence[float]) -> float | None:
    return sum(values) / len(values) if values else None


def _sd(values: Sequence[float]) -> float | None:
    if not values:
        return None
    if len(values) < 2:
        return 0.0
    mean = sum(values) / len(values)
    return math.sqrt(sum((x - mean) ** 2 for x in values) / (len(values) - 1))


def _number(value: Any, field: str, *, upper: float | None = None) -> float:
    result = float(value)
    if not math.isfinite(result) or result < 0 or (upper is not None and result > upper):
        raise ValueError(f"{field} must be finite and nonnegative" +
                         (f" and at most {upper}" if upper is not None else ""))
    return result


def _sort_key(row: Mapping[str, Any]) -> tuple[str, str, str, tuple[int, Any]]:
    value = row["parameter_value"]
    # Numeric parameters retain their numeric order, while named settings and
    # the reference row remain supported without float-conversion failures.
    parameter = (0, float(value)) if isinstance(value, (int, float)) else (1, str(value))
    return str(row["algorithm"]), str(row["budget_basis"]), str(row["parameter_name"]), parameter


def aggregate_runs(
    runs: Iterable[Mapping[str, Any]],
    exhaustive_search_cost: float,
) -> list[dict[str, Any]]:
    """Summarize each (algorithm, parameter, budget basis) across seeds.

Costs and evaluation counts include every run, including runs with no
recommendation. Accuracy and deployment cost are conditional on obtaining a
recommendation; their denominator and missing-recommendation count are
explicit. A missing budget basis is recorded as ``unspecified``.
    """

    exhaustive_search_cost = _number(exhaustive_search_cost, "exhaustive_search_cost")
    if exhaustive_search_cost == 0:
        raise ValueError("exhaustive_search_cost must be positive and finite")
    groups: dict[tuple[str, str, str, str], list[Mapping[str, Any]]] = defaultdict(list)
    for run in runs:
        missing = [key for key in (
            "algorithm", "parameter_name", "parameter_value", "search_evaluations", "search_cost",
        ) if key not in run]
        if missing:
            raise ValueError(f"run is missing fields: {missing}")
        if "heldout_accuracy" not in run and run.get("selected_config_id") is not None:
            raise ValueError("a run with a recommendation must have heldout_accuracy")
        basis = str(run.get("budget_basis", "unspecified"))
        key = (str(run["algorithm"]), str(run["parameter_name"]),
               repr(run["parameter_value"]), basis)
        groups[key].append(run)
    rows: list[dict[str, Any]] = []
    for (_, _, _, basis), values in groups.items():
        first = values[0]
        accuracy: list[float] = []
        deployment_cost: list[float] = []
        runtimes: list[float] = []
        for run in values:
            measured_accuracy = run.get("heldout_accuracy")
            if "selected_config_id" in run and run["selected_config_id"] is None and measured_accuracy is not None:
                raise ValueError("a run without a selected_config_id cannot have heldout_accuracy")
            if measured_accuracy is not None:
                accuracy.append(_number(measured_accuracy, "heldout_accuracy", upper=1.0))
                if run.get("heldout_mean_cost") is not None:
                    deployment_cost.append(_number(run["heldout_mean_cost"], "heldout_mean_cost"))
            runtime = run.get("selection_time_seconds", run.get("runtime_seconds"))
            if runtime is not None:
                runtimes.append(_number(runtime, "selection_time_seconds"))
        evaluations = [_number(v["search_evaluations"], "search_evaluations") for v in values]
        costs = [_number(v["search_cost"], "search_cost") for v in values]
        mean_cost = sum(costs) / len(costs)
        rows.append({
            "algorithm": str(first["algorithm"]),
            "parameter_name": str(first["parameter_name"]),
            "parameter_value": first["parameter_value"],
            "budget_basis": basis,
            "label": f"{first['algorithm']} ({first['parameter_name']}={first['parameter_value']}; {basis})",
            "is_reference": False,
            "repeats": len(values),
            "recommendation_count": len(accuracy),
            "no_recommendation_count": len(values) - len(accuracy),
            "no_recommendation_rate": 1.0 - len(accuracy) / len(values),
            "mean_accuracy": _mean(accuracy),
            "std_accuracy": _sd(accuracy),
            "mean_evaluations": _mean(evaluations),
            "std_evaluations": _sd(evaluations),
            "mean_search_cost": mean_cost,
            "std_search_cost": _sd(costs),
            "mean_selection_time_seconds": _mean(runtimes),
            "std_selection_time_seconds": _sd(runtimes),
            "selection_time_count": len(runtimes),
            "mean_heldout_cost": _mean(deployment_cost),
            "std_heldout_cost": _sd(deployment_cost),
            "heldout_cost_count": len(deployment_cost),
            "cost_savings": 1.0 - mean_cost / exhaustive_search_cost,
            "exhaustive_search_cost": exhaustive_search_cost,
        })
    return sorted(rows, key=_sort_key)


def _reference_row(
    metadata: Mapping[str, Any], exhaustive_search_cost: float, exhaustive_accuracy: float | None,
) -> dict[str, Any]:
    evaluations = None
    if metadata.get("search_n") is not None and metadata.get("configs") is not None:
        search_n = metadata["search_n"]
        configs = metadata["configs"]
        if any(isinstance(value, bool) or not isinstance(value, int) or value <= 0
               for value in (search_n, configs)):
            raise ValueError("metadata.search_n and metadata.configs must be positive integers")
        evaluations = search_n * configs
    accuracy = (None if exhaustive_accuracy is None else
                _number(exhaustive_accuracy, "exhaustive_accuracy", upper=1.0))
    deployment_cost = metadata.get("exhaustive_reference_heldout_mean_cost")
    if deployment_cost is not None:
        deployment_cost = _number(deployment_cost, "exhaustive_reference_heldout_mean_cost")
    return {
        "algorithm": "Brute force (reference)", "parameter_name": "none",
        "parameter_value": None, "budget_basis": "all_search_cells",
        "label": "Brute force (reference)", "is_reference": True,
        "repeats": 1, "recommendation_count": int(accuracy is not None),
        "no_recommendation_count": None, "no_recommendation_rate": None,
        "mean_accuracy": accuracy, "std_accuracy": None,
        "mean_evaluations": evaluations, "std_evaluations": None,
        "mean_search_cost": float(exhaustive_search_cost), "std_search_cost": None,
        "mean_selection_time_seconds": None, "std_selection_time_seconds": None,
        "selection_time_count": 0,
        "mean_heldout_cost": deployment_cost, "std_heldout_cost": None,
        "heldout_cost_count": int(deployment_cost is not None),
        "cost_savings": 0.0, "exhaustive_search_cost": float(exhaustive_search_cost),
        "selected_config_id": metadata.get("exhaustive_reference_config"),
    }


def render_markdown(rows: Sequence[Mapping[str, Any]], title: str = "Experiment 1 selector comparison") -> str:
    """Render a Table-7-style table; dollar signs denote proxy USD only."""

    lines = [f"## {title}", "",
             "| Selector | Parameter | Budget basis | Mean Acc. | Mean Evals | Mean Search Cost (proxy USD) | Cost Savings | Repeats | No recommendation |",
             "|---|---|---|---:|---:|---:|---:|---:|---:|"]
    for row in rows:
        parameter = "—" if row.get("is_reference") else f"{row['parameter_name']}={row['parameter_value']}"
        accuracy = "—" if row["mean_accuracy"] is None else f"{100 * row['mean_accuracy']:.2f}%"
        evaluations = "—" if row["mean_evaluations"] is None else f"{row['mean_evaluations']:.1f}"
        no_recommendation = row.get("no_recommendation_count", 0)
        missing = "—" if no_recommendation is None else f"{no_recommendation}/{row['repeats']}"
        lines.append(
            f"| {row['algorithm']} | {parameter} | {row.get('budget_basis', 'unspecified')} | {accuracy} | "
            f"{evaluations} | ${row['mean_search_cost']:.5f} | "
            f"{100 * row['cost_savings']:.1f}% | {row['repeats']} | {missing} |"
        )
    lines.extend(["", "Accuracy uses held-out questions after selection. Mean Evals counts complete "
                  "configuration/question cells. Search cost sums the simulated input-token charges; "
                  "it is not an API invoice or selector CPU time.", "",
                  "CSV/JSON standard deviations are sample SDs across selector seeds on this fixed "
                  "split, not accuracy confidence intervals. If a run has no recommendation, its "
                  "cost and evaluation count remain included; accuracy and deployment cost are "
                  "conditional on the reported recommendation count."])
    return "\n".join(lines) + "\n"


_CSV_FIELDS = [
    "algorithm", "parameter_name", "parameter_value", "budget_basis", "is_reference", "repeats",
    "recommendation_count", "no_recommendation_count", "no_recommendation_rate",
    "mean_accuracy", "std_accuracy", "mean_evaluations", "std_evaluations",
    "mean_search_cost", "std_search_cost", "mean_selection_time_seconds",
    "std_selection_time_seconds", "selection_time_count", "mean_heldout_cost",
    "std_heldout_cost", "heldout_cost_count", "cost_savings", "exhaustive_search_cost",
    "selected_config_id",
]


def write_csv(rows: Sequence[Mapping[str, Any]], path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=_CSV_FIELDS)
        writer.writeheader()
        writer.writerows({field: row.get(field) for field in _CSV_FIELDS} for row in rows)


def render_plot(
    rows: Sequence[Mapping[str, Any]],
    path: str | Path,
    exhaustive_accuracy: float | None = None,
    title: str = "Accuracy versus search cost",
) -> None:
    """Draw one descriptive PCHIP curve per algorithm, without extrapolation.

Both coordinates are interpolated over settings ordered by measured search
cost. This permits repeated or nonmonotone accuracy. Lines do not imply an
attainable frontier, a fitted response model, or statistical uncertainty.
    """

    try:
        import matplotlib.pyplot as plt
        from scipy.interpolate import PchipInterpolator
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError("plotting requires matplotlib and scipy") from exc
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    grouped: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    references: list[Mapping[str, Any]] = []
    incomplete = 0
    for row in rows:
        if row.get("is_reference"):
            references.append(row)
        elif row["mean_accuracy"] is not None:
            grouped[str(row["algorithm"])].append(row)
        incomplete += int(row.get("no_recommendation_count") or 0)
    fig, ax = plt.subplots(figsize=(11, 7), constrained_layout=True)
    colors = plt.get_cmap("tab20")
    for index, (algorithm, values) in enumerate(sorted(grouped.items())):
        values = sorted(values, key=lambda r: (float(r["mean_search_cost"]), repr(r["parameter_value"])))
        x = [100.0 * float(r["mean_accuracy"]) for r in values]
        y = [float(r["mean_search_cost"]) for r in values]
        color = colors(index % 20)
        ax.scatter(x, y, s=35, color=color, label=algorithm, zorder=3)
        if len(values) >= 2:
            t = list(range(len(values)))
            dense = [t[-1] * i / 199 for i in range(200)]
            ax.plot(PchipInterpolator(t, x, extrapolate=False)(dense),
                    PchipInterpolator(t, y, extrapolate=False)(dense), color=color, linewidth=1.4)
    for reference in references:
        if reference["mean_accuracy"] is not None:
            ax.scatter([100.0 * reference["mean_accuracy"]], [reference["mean_search_cost"]],
                       marker="*", s=140, color="black", label="Exhaustive search reference", zorder=4)
    if not references and exhaustive_accuracy is not None:
        ax.axvline(100.0 * float(exhaustive_accuracy), color="black", linestyle="--",
                   linewidth=1.0, label="Exhaustive reference accuracy")
    ax.set_xlabel("Mean held-out accuracy (%)")
    ax.set_ylabel("Mean search cost (proxy USD; coefficient × input tokens)")
    ax.set_title(title)
    ax.set_ylim(bottom=0)
    ax.grid(alpha=0.25)
    if grouped or references or exhaustive_accuracy is not None:
        ax.legend(fontsize="small", ncol=2)
    caption = "Points: algorithm/parameter means. Curves: descriptive PCHIP interpolation, not a statistical fit."
    if incomplete:
        caption += f"\n{incomplete} runs had no recommendation; accuracy is conditional on recommendation."
    fig.supxlabel(caption, fontsize=8)
    try:
        fig.savefig(path, dpi=180)
    finally:
        plt.close(fig)


def _report_context(metadata: Mapping[str, Any]) -> tuple[str, list[str]]:
    reward = metadata.get("selector_reward")
    if reward == "final_correct":
        scenario = "Gold-labeled offline profiling"
        contract = ("Selectors observe correctness labels on revealed search questions, a valid "
                    "labeled profiling setting. Held-out labels are used only after a row is selected. "
                    "The workflow verifier remains answer-key-blind.")
    elif reward == "verifier_pass":
        scenario = "Verifier-proxy search"
        contract = ("Selectors observe answer-key-blind verifier acceptance on revealed search "
                    "questions. This is a separate label-free search scenario; optimizing acceptance "
                    "does not imply optimizing gold correctness. Held-out accuracy uses gold labels.")
    else:
        scenario = "Experiment 1"
        contract = "The selector reward contract was not supplied; consult the run configuration."
    notes = [contract,
             "The exhaustive reference selects using the complete search matrix, then reports that "
             "row's held-out accuracy. It does not choose the best row on held-out questions.",
             "All search costs are local proxy USD: sum of coefficient_model × input_tokens across "
             "solver and verifier calls, including retries. Output tokens and cache discounts are excluded. "
             "Held-out mean deployment cost and selector CPU time are reported separately.",
             "Budget bases are distinct: row_fraction, cell_fraction, realized_cost_fraction, and "
             "parameter_only settings do not impose the same spending constraint.",
             "Each curve is a descriptive PCHIP interpolation through parameter-setting means in "
             "measured-cost order, without extrapolation. It is not a statistical fit or uncertainty band."]
    return scenario, notes


def write_report(
    runs: Sequence[Mapping[str, Any]],
    exhaustive_search_cost: float,
    output_dir: str | Path,
    metadata: Mapping[str, Any] | None = None,
    exhaustive_accuracy: float | None = None,
) -> dict[str, str]:
    """Write aggregate and per-run data, Table 7, and PNG/PDF/SVG figures."""

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    metadata = dict(metadata or {})
    scenario, notes = _report_context(metadata)
    rows = aggregate_runs(runs, exhaustive_search_cost)
    reference = _reference_row(metadata, exhaustive_search_cost, exhaustive_accuracy)
    rows.insert(0, reference)
    payload = {"metadata": metadata, "scenario": scenario, "notes": notes,
               "standard_deviation_basis": "sample SD across selector seeds on a fixed split; not a confidence interval",
               "rows": rows}
    json_path = output_dir / "selector-table.json"
    json_path.write_text(json.dumps(payload, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    runs_path = output_dir / "selector-runs.json"
    runs_path.write_text(json.dumps({"metadata": metadata, "scenario": scenario, "runs": list(runs)},
                                    indent=2, allow_nan=False) + "\n", encoding="utf-8")
    csv_path = output_dir / "selector-table.csv"
    write_csv(rows, csv_path)
    markdown_path = output_dir / "selector-table.md"
    markdown_path.write_text(render_markdown(rows, title=f"{scenario}: selector comparison") +
                             "\n" + "\n\n".join(notes) + "\n", encoding="utf-8")
    paths = {"json": str(json_path), "runs_json": str(runs_path),
             "csv": str(csv_path), "markdown": str(markdown_path)}
    for extension in ("png", "pdf", "svg"):
        plot_path = output_dir / f"accuracy-search-cost.{extension}"
        render_plot(rows, plot_path, exhaustive_accuracy=exhaustive_accuracy,
                    title=f"{scenario}: held-out accuracy versus search cost")
        paths["plot" if extension == "png" else f"plot_{extension}"] = str(plot_path)
    return paths


__all__ = ["aggregate_runs", "render_markdown", "render_plot", "write_csv", "write_report"]
