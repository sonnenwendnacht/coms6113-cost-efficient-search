#!/usr/bin/env python3
"""Plot the distribution of per-row Experiment 1 accuracy.

The input is the compact correctness CSV exported by
``export_experiment1_correctness_csv.py``.  Each configuration contributes one
accuracy on the search questions and one on the audit questions.
"""

from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


def read_accuracy(path: Path) -> tuple[list[str], np.ndarray, np.ndarray]:
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != 729:
        raise ValueError(f"expected 729 rows, found {len(rows)}")
    search_cols = [f"search_q{i:03d}" for i in range(200)]
    audit_cols = [f"audit_q{i:03d}" for i in range(200)]
    names = [row["config_id"] for row in rows]
    search = np.array([[int(row[col]) for col in search_cols] for row in rows], dtype=np.int8)
    audit = np.array([[int(row[col]) for col in audit_cols] for row in rows], dtype=np.int8)
    if not np.isin(search, [0, 1]).all() or not np.isin(audit, [0, 1]).all():
        raise ValueError("correctness matrix contains values other than 0 and 1")
    return names, search.mean(axis=1) * 100.0, audit.mean(axis=1) * 100.0


def describe(values: np.ndarray) -> dict[str, float | int]:
    counts = Counter(np.round(values, 6))
    best = float(values.max())
    return {
        "mean": float(values.mean()),
        "median": float(np.median(values)),
        "min": float(values.min()),
        "max": best,
        "best_count": counts[round(best, 6)],
    }


def plot(input_path: Path, output_path: Path) -> tuple[dict[str, float | int], dict[str, float | int]]:
    _, search, audit = read_accuracy(input_path)
    search_stats = describe(search)
    audit_stats = describe(audit)

    # Accuracy is discrete in 0.5 percentage-point increments because each
    # split has 200 questions.  Center one bar on every possible increment.
    edges = np.arange(-0.25, 100.26, 0.5)
    fig, axes = plt.subplots(1, 2, figsize=(13, 5.4), sharex=True, sharey=True)
    for ax, values, stats, label, color in [
        (axes[0], search, search_stats, "Search split", "#3568a8"),
        (axes[1], audit, audit_stats, "Audit split", "#c45a36"),
    ]:
        ax.hist(values, bins=edges, color=color, alpha=0.86, edgecolor="white", linewidth=0.25)
        ax.axvline(stats["mean"], color="#222222", linestyle="--", linewidth=1.2, label=f"mean {stats['mean']:.2f}%")
        ax.axvline(stats["max"], color="#111111", linestyle=":", linewidth=1.2, label=f"best {stats['max']:.2f}% ({stats['best_count']} rows)")
        ax.set_title(label)
        ax.set_xlabel("Final workflow accuracy (%)")
        ax.grid(axis="y", alpha=0.25)
        ax.legend(frameon=False, fontsize=9, loc="upper left")
        ax.text(
            0.98,
            0.95,
            f"median {stats['median']:.2f}%\nrange {stats['min']:.2f}–{stats['max']:.2f}%",
            transform=ax.transAxes,
            ha="right",
            va="top",
            fontsize=9,
            bbox={"facecolor": "white", "alpha": 0.8, "edgecolor": "none"},
        )
    axes[0].set_ylabel("Number of configurations (out of 729)")
    upper = max(float(search.max()), float(audit.max())) + 2.0
    axes[0].set_xlim(max(0.0, min(float(search.min()), float(audit.min())) - 1.0), upper)
    fig.suptitle("Experiment 1: distribution of accuracy across 729 retry rows", fontsize=15)
    fig.text(
        0.5,
        0.01,
        "Each row is evaluated on 200 questions; bars therefore occur in 0.5-point increments. "
        "Accuracy is final workflow correctness after the verifier's stopping rule.",
        ha="center",
        fontsize=9,
    )
    fig.tight_layout(rect=(0, 0.05, 1, 0.94))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=220, bbox_inches="tight")
    plt.close(fig)
    return search_stats, audit_stats


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("results/experiment1-nine-model-correctness.csv"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results/experiment1-accuracy-distribution.png"),
    )
    args = parser.parse_args()
    search_stats, audit_stats = plot(args.input, args.output)
    print(f"wrote {args.output}")
    print(f"search: {search_stats}")
    print(f"audit: {audit_stats}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
