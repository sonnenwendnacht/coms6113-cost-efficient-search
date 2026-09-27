#!/usr/bin/env python3
"""Sanity-check similarity_annealed_ucb on a smooth categorical landscape.

This is deliberately synthetic.  It tests whether graph transfer can help
when the smoothness assumption is true; it is not a benchmark result for the
MathQA experiment.
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from retry_search.selection_sweep import run_sweep  # noqa: E402


def make_landscape(side: int, questions: int) -> tuple[list[list[float]], list[list[float]], list[float]]:
    k = side ** 3
    rewards: list[list[float]] = []
    costs: list[list[float]] = []
    means: list[float] = []
    for arm in range(k):
        digits = ((arm // (side * side)) % side, (arm // side) % side, arm % side)
        distance = sum(abs(value - (side - 1)) for value in digits)
        mean = max(0.0, 0.95 - 0.16 * distance)
        means.append(mean)
        rewards.append([
            float(((question * 13 + arm * 7) % 100) / 100.0 < mean)
            for question in range(questions)
        ])
        costs.append([1.0 + 0.2 * sum(digits) for _ in range(questions)])
    return rewards, costs, means


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--side", type=int, default=3)
    parser.add_argument("--questions", type=int, default=50)
    parser.add_argument("--seeds", type=int, default=20)
    parser.add_argument("--fraction", type=float, default=0.1)
    args = parser.parse_args()
    rewards, costs, means = make_landscape(args.side, args.questions)
    ids = [str(i) for i in range(args.side ** 3)]
    settings = [
        {"algorithm": name, "parameter_name": "fraction", "parameter_value": args.fraction}
        for name in ("random", "bayesian_opt", "similarity_annealed_ucb")
    ]
    runs = run_sweep(rewards, costs, ids, settings=settings, seeds=range(args.seeds))
    summary = {}
    for name in ("random", "bayesian_opt", "similarity_annealed_ucb"):
        selected = [row["selected_config_index"] for row in runs if row["algorithm"] == name]
        summary[name] = {
            "mean_selected_landscape_reward": statistics.mean(means[index] for index in selected),
            "optimal_selection_rate": sum(index == len(means) - 1 for index in selected) / len(selected),
            "mean_search_evaluations": statistics.mean(
                row["search_evaluations"] for row in runs if row["algorithm"] == name
            ),
        }
    print(json.dumps({"synthetic": True, "settings": vars(args), "summary": summary}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
