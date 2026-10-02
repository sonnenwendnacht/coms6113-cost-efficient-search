#!/usr/bin/env python3
"""Plot Experiment 1 with search cost on x and held-out accuracy on y.

The source selector table is already aggregated over allocation seeds. This
plot keeps the report's descriptive PCHIP convention and changes only the
axis orientation; it is not a statistical fit or an uncertainty band.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path


def render(table_path: Path, output_path: Path) -> None:
    try:
        import matplotlib.pyplot as plt
        from scipy.interpolate import PchipInterpolator
    except ImportError as exc:  # pragma: no cover
        raise SystemExit("plotting requires matplotlib and scipy") from exc

    table = json.loads(table_path.read_text(encoding="utf-8"))
    rows = table["rows"]
    grouped: dict[str, list[dict]] = defaultdict(list)
    references: list[dict] = []
    incomplete = 0
    for row in rows:
        incomplete += int(row.get("no_recommendation_count") or 0)
        if row.get("is_reference"):
            references.append(row)
        elif row.get("mean_accuracy") is not None:
            grouped[str(row["algorithm"])].append(row)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(11, 7), constrained_layout=True)
    colors = plt.get_cmap("tab20")
    for index, (algorithm, values) in enumerate(sorted(grouped.items())):
        values = sorted(values, key=lambda row: (float(row["mean_search_cost"]), repr(row["parameter_value"])))
        x = [float(row["mean_search_cost"]) for row in values]
        y = [100.0 * float(row["mean_accuracy"]) for row in values]
        color = colors(index % 20)
        ax.scatter(x, y, s=35, color=color, label=algorithm, zorder=3)
        if len(values) >= 2:
            t = list(range(len(values)))
            dense = [t[-1] * i / 199 for i in range(200)]
            ax.plot(
                PchipInterpolator(t, x, extrapolate=False)(dense),
                PchipInterpolator(t, y, extrapolate=False)(dense),
                color=color,
                linewidth=1.4,
            )

    for reference in references:
        if reference.get("mean_accuracy") is not None:
            ax.scatter(
                [float(reference["mean_search_cost"])],
                [100.0 * float(reference["mean_accuracy"])],
                marker="*",
                s=140,
                color="black",
                label="Exhaustive search reference",
                zorder=4,
            )

    ax.set_xlabel("Mean search cost (proxy USD; coefficient × input tokens)")
    ax.set_ylabel("Mean held-out accuracy (%)")
    ax.set_title("Gold-labeled offline profiling: search cost versus held-out accuracy")
    ax.set_xlim(left=0)
    ax.set_ylim(bottom=0)
    ax.grid(alpha=0.25)
    if grouped or references:
        ax.legend(fontsize="small", ncol=2)
    caption = "Points: algorithm/parameter means. Curves: descriptive PCHIP interpolation, not a statistical fit."
    if incomplete:
        caption += f"\n{incomplete} runs had no recommendation; accuracy is conditional on recommendation."
    fig.supxlabel(caption, fontsize=8)
    try:
        fig.savefig(output_path, dpi=180)
    finally:
        plt.close(fig)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--table",
        type=Path,
        default=Path("results/runs/exp1-nine-local-20260930/full-gold/selector-table.json"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results/experiment1-cost-accuracy.png"),
    )
    args = parser.parse_args()
    render(args.table, args.output)
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

