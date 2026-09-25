"""Table-7-style aggregation and accuracy/search-cost plots.

The input is one record per (selector, parameter setting, seed), with
``heldout_accuracy`` attached only after the selector has finished.  The
reporter never changes a selected row or uses held-out values to tune a
selector.  Plotting dependencies are imported only when a figure is asked
for; aggregation and Markdown rendering remain standard-library only.
"""

from __future__ import annotations

import csv
import json
import math
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


def _mean(values: Sequence[float]) -> float:
    return sum(values) / len(values) if values else float("nan")


def _sd(values: Sequence[float]) -> float:
    if len(values) < 2:
        return 0.0
    mean = _mean(values)
    return math.sqrt(sum((x - mean) ** 2 for x in values) / (len(values) - 1))


def _label(row: Mapping[str, Any]) -> str:
    return f"{row['algorithm']} ({row['parameter_name']}={row['parameter_value']})"


def aggregate_runs(
    runs: Iterable[Mapping[str, Any]],
    exhaustive_search_cost: float,
) -> list[dict[str, Any]]:
    """Aggregate seeds into the columns used by AgentOpt Table 7.

    Required run fields are ``algorithm``, ``parameter_name``,
    ``parameter_value``, ``heldout_accuracy``, ``search_evaluations``, and
    ``search_cost``.  The exhaustive cost is a reference measured from the
    same search matrix, not from the held-out matrix.
    """

    if exhaustive_search_cost <= 0 or not math.isfinite(float(exhaustive_search_cost)):
        raise ValueError("exhaustive_search_cost must be positive and finite")
    groups: dict[tuple[str, str, str], list[Mapping[str, Any]]] = defaultdict(list)
    for run in runs:
        missing = [
            key for key in (
                "algorithm", "parameter_name", "parameter_value",
                "heldout_accuracy", "search_evaluations", "search_cost",
            ) if key not in run
        ]
        if missing:
            raise ValueError(f"run is missing fields: {missing}")
        key = (str(run["algorithm"]), str(run["parameter_name"]), repr(run["parameter_value"]))
        groups[key].append(run)
    rows: list[dict[str, Any]] = []
    for (_, _, _), values in groups.items():
        first = values[0]
        accuracy = [float(v["heldout_accuracy"]) for v in values]
        evaluations = [float(v["search_evaluations"]) for v in values]
        costs = [float(v["search_cost"]) for v in values]
        mean_cost = _mean(costs)
        rows.append({
            "algorithm": str(first["algorithm"]),
            "parameter_name": str(first["parameter_name"]),
            "parameter_value": first["parameter_value"],
            "label": _label(first),
            "repeats": len(values),
            "mean_accuracy": _mean(accuracy),
            "std_accuracy": _sd(accuracy),
            "mean_evaluations": _mean(evaluations),
            "mean_search_cost": mean_cost,
            "std_search_cost": _sd(costs),
            "cost_savings": 1.0 - mean_cost / exhaustive_search_cost,
            "exhaustive_search_cost": float(exhaustive_search_cost),
        })
    return sorted(rows, key=lambda r: (r["algorithm"], float(r["parameter_value"])))


def render_markdown(rows: Sequence[Mapping[str, Any]], title: str = "Experiment 1 selector comparison") -> str:
    """Render a Table-7-style Markdown table from aggregate rows."""

    lines = [f"## {title}", "", "| Selector | Parameter | Mean Acc. | Mean Evals | Mean Search Cost | Cost Savings | Repeats |",
             "|---|---:|---:|---:|---:|---:|---:|"]
    for row in rows:
        parameter = f"{row['parameter_name']}={row['parameter_value']}"
        lines.append(
            f"| {row['algorithm']} | {parameter} | {100 * row['mean_accuracy']:.2f}% | "
            f"{row['mean_evaluations']:.1f} | ${row['mean_search_cost']:.5f} | "
            f"{100 * row['cost_savings']:.1f}% | {row['repeats']} |"
        )
    return "\n".join(lines) + "\n"


def write_csv(rows: Sequence[Mapping[str, Any]], path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = ["algorithm", "parameter_name", "parameter_value", "repeats",
              "mean_accuracy", "std_accuracy", "mean_evaluations", "mean_search_cost",
              "std_search_cost", "cost_savings", "exhaustive_search_cost"]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field) for field in fields})


def render_plot(
    rows: Sequence[Mapping[str, Any]],
    path: str | Path,
    exhaustive_accuracy: float | None = None,
    title: str = "Accuracy versus search cost",
) -> None:
    """Plot raw parameter points and descriptive within-family fitted curves.

    The lines interpolate observed parameter settings only.  They are visual
    guides, not statistical fits and are never extrapolated beyond the data.
    """

    try:
        import matplotlib.pyplot as plt
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError("plotting requires matplotlib") from exc
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    grouped: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[str(row["algorithm"])].append(row)
    fig, ax = plt.subplots(figsize=(10, 6), constrained_layout=True)
    for algorithm, values in sorted(grouped.items()):
        values = sorted(values, key=lambda r: (float(r["mean_search_cost"]), repr(r["parameter_value"])))
        x = [float(r["mean_search_cost"]) for r in values]
        y = [100.0 * float(r["mean_accuracy"]) for r in values]
        ax.scatter(x, y, s=35, label=algorithm)
        if len(values) >= 3:
            # A monotone cubic interpolator is optional. Linear interpolation
            # is the fallback and keeps the curve honest when scipy is absent.
            try:
                from scipy.interpolate import PchipInterpolator

                unique = {}
                for xx, yy in zip(x, y):
                    unique.setdefault(xx, yy)
                if len(unique) >= 3:
                    xx = sorted(unique)
                    interp = PchipInterpolator(xx, [unique[v] for v in xx])
                    dense = [xx[0] + (xx[-1] - xx[0]) * i / 99 for i in range(100)]
                    ax.plot(dense, interp(dense), linewidth=1.4)
            except ImportError:  # pragma: no cover
                ax.plot(x, y, linewidth=1.2)
    if exhaustive_accuracy is not None:
        ax.axhline(100.0 * float(exhaustive_accuracy), color="black", linestyle="--",
                   linewidth=1.0, label="exhaustive reference")
    ax.set_xlabel("Mean search cost (USD proxy)")
    ax.set_ylabel("Mean held-out accuracy (%)")
    ax.set_title(title)
    ax.grid(alpha=0.25)
    ax.legend(fontsize="small", ncol=2)
    fig.savefig(path, dpi=180)
    plt.close(fig)


def write_report(
    runs: Sequence[Mapping[str, Any]],
    exhaustive_search_cost: float,
    output_dir: str | Path,
    metadata: Mapping[str, Any] | None = None,
    exhaustive_accuracy: float | None = None,
) -> dict[str, str]:
    """Write JSON, CSV, Markdown, and PNG artifacts without raw traces."""

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    rows = aggregate_runs(runs, exhaustive_search_cost)
    json_path = output_dir / "selector-table.json"
    json_path.write_text(json.dumps({"metadata": dict(metadata or {}), "rows": rows}, indent=2), encoding="utf-8")
    csv_path = output_dir / "selector-table.csv"
    write_csv(rows, csv_path)
    markdown_path = output_dir / "selector-table.md"
    markdown_path.write_text(render_markdown(rows), encoding="utf-8")
    plot_path = output_dir / "accuracy-search-cost.png"
    render_plot(rows, plot_path, exhaustive_accuracy=exhaustive_accuracy)
    return {"json": str(json_path), "csv": str(csv_path), "markdown": str(markdown_path), "plot": str(plot_path)}


__all__ = ["aggregate_runs", "render_markdown", "render_plot", "write_csv", "write_report"]
