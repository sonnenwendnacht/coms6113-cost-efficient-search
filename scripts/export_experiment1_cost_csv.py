#!/usr/bin/env python3
"""Export the realized Experiment 1 per-cell cost matrix.

Each output value is the complete workflow's realized proxy charge for one
named configuration and one question.  The charge includes every reached
solver and verifier call, including failed attempts; it excludes output-token
charges, cache discounts, and latency because those were not part of
Experiment 1's registered cost formula.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path


def export(trace_path: Path, output_path: Path, search_n: int = 200, audit_n: int = 200) -> tuple[int, int]:
    records = json.loads(trace_path.read_text(encoding="utf-8"))
    if not isinstance(records, list):
        raise ValueError("trace must be a JSON list")
    questions = search_n + audit_n
    by_config: dict[str, dict[int, float]] = {}
    for record in records:
        config_id = record["config_id"]
        question_id = int(record["question_id"])
        if not 0 <= question_id < questions:
            raise ValueError(f"question id outside declared split: {question_id}")
        calls = record.get("calls", [])
        recomputed = sum(
            float(call["input_tokens"]) * float(call["coefficient_usd_per_token"])
            for call in calls
        )
        recorded = float(record["cost_usd"])
        if not math.isclose(recorded, recomputed, rel_tol=1e-10, abs_tol=1e-15):
            raise ValueError(f"cost mismatch for {config_id}, q={question_id}")
        row = by_config.setdefault(config_id, {})
        if question_id in row:
            raise ValueError(f"duplicate cell: {config_id}, q={question_id}")
        row[question_id] = recorded

    if len(by_config) != 729:
        raise ValueError(f"expected 729 configurations, found {len(by_config)}")
    expected = set(range(questions))
    for config_id, row in by_config.items():
        if set(row) != expected:
            raise ValueError(f"incomplete row {config_id}")

    header = ["config_id"]
    header.extend(f"search_q{i:03d}" for i in range(search_n))
    header.extend(f"audit_q{i:03d}" for i in range(audit_n))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(header)
        for config_id in sorted(by_config):
            row = by_config[config_id]
            values = [config_id]
            values.extend(f"{row[i]:.12g}" for i in range(search_n))
            values.extend(f"{row[search_n + i]:.12g}" for i in range(audit_n))
            writer.writerow(values)
    return len(by_config), questions


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--trace",
        type=Path,
        default=Path("results/runs/exp1-nine-local-20260927-proper/traces.json"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results/experiment1-nine-model-cost-usd.csv"),
    )
    args = parser.parse_args()
    rows, questions = export(args.trace, args.output)
    print(f"wrote {args.output}: {rows} configurations x {questions} questions")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
