#!/usr/bin/env python3
"""Measure whether Hamming neighbors are actually more similar.

This is a synthetic diagnostic only. It does not run or inspect MathQA traces.
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from retry_search.selection_sweep import _hamming_distance  # noqa: E402
from scripts.benchmark_pairwise_local_racing import make_matrix  # noqa: E402


def summarize(rewards: list[list[float]], side: int) -> dict[str, dict[str, float]]:
    by_distance: dict[int, list[float]] = {1: [], 2: [], 3: []}
    k, n = len(rewards), len(rewards[0])
    for left in range(k):
        for right in range(left + 1, k):
            distance = _hamming_distance(left, right, k)
            if distance in by_distance:
                by_distance[distance].extend(
                    rewards[right][q] - rewards[left][q] for q in range(n)
                )
    return {
        str(distance): {
            "pairs": sum(1 for left in range(k) for right in range(left + 1, k)
                          if _hamming_distance(left, right, k) == distance),
            "residual_variance": statistics.pvariance(values) if values else None,
            "mean_abs_residual": statistics.mean(abs(value) for value in values) if values else None,
        }
        for distance, values in by_distance.items()
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--side", type=int, default=3)
    parser.add_argument("--questions", type=int, default=200)
    args = parser.parse_args()
    rewards, _ = make_matrix(args.side, args.questions, 0)
    print(json.dumps({"synthetic": True, "settings": vars(args), "by_hamming_distance": summarize(rewards, args.side)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
