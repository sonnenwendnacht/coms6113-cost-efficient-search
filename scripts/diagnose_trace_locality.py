#!/usr/bin/env python3
"""Measure row similarity from a completed Experiment 1 trace.

This reports a descriptive same-question diagnostic only.  It does not choose
an algorithm, read answer keys, or treat a neighboring row as a cache hit.
"""

from __future__ import annotations

import argparse
import json
import statistics
from collections import defaultdict
from itertools import combinations
from pathlib import Path


def _read_traces(path: Path) -> list[dict]:
    if path.suffix == ".jsonl":
        return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    value = json.loads(path.read_text())
    if not isinstance(value, list):
        raise ValueError("trace file must contain a JSON list or JSONL records")
    return value


def diagnose(run_dir: Path) -> dict:
    trace_path = run_dir / "traces.jsonl"
    if not trace_path.exists():
        trace_path = run_dir / "traces.json"
    traces = _read_traces(trace_path)
    by_row: dict[str, dict[int, float]] = defaultdict(dict)
    for trace in traces:
        if "config_id" not in trace or "question_id" not in trace or "final_correct" not in trace:
            continue
        value = trace["final_correct"]
        if value is None:
            continue
        by_row[str(trace["config_id"])][int(trace["question_id"])] = float(value)
    if len(by_row) < 2:
        raise ValueError("need at least two rows with final_correct values")
    row_slots = {row: tuple(row.split("/")) for row in by_row}
    grouped: dict[int, dict[str, list[float]]] = defaultdict(lambda: {"squared_diff": [], "correlation": []})
    for left, right in combinations(sorted(by_row), 2):
        questions = sorted(set(by_row[left]) & set(by_row[right]))
        if not questions:
            continue
        distance = sum(a != b for a, b in zip(row_slots[left], row_slots[right]))
        left_values = [by_row[left][q] for q in questions]
        right_values = [by_row[right][q] for q in questions]
        grouped[distance]["squared_diff"].append(
            statistics.mean((a - b) ** 2 for a, b in zip(left_values, right_values))
        )
        if len(questions) >= 2:
            try:
                grouped[distance]["correlation"].append(statistics.correlation(left_values, right_values))
            except statistics.StatisticsError:
                pass
    summary = {}
    for distance, values in sorted(grouped.items()):
        summary[str(distance)] = {
            "pairs": len(values["squared_diff"]),
            "mean_squared_difference": statistics.mean(values["squared_diff"]),
            "mean_pearson_correlation": (
                statistics.mean(values["correlation"]) if values["correlation"] else None
            ),
        }
    return {
        "run_dir": str(run_dir),
        "rows": len(by_row),
        "questions_per_row_min": min(len(values) for values in by_row.values()),
        "questions_per_row_max": max(len(values) for values in by_row.values()),
        "by_hamming_distance": summary,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("run_dir", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = diagnose(args.run_dir)
    rendered = json.dumps(result, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
