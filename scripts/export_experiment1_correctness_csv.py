#!/usr/bin/env python3
"""Export the completed Experiment 1 binary correctness matrix.

The input trace contains one record for every complete configuration/question
cell.  The output has one named configuration per row and separate columns for
the 200 search and 200 audit questions.  It intentionally exports only the
final workflow correctness bit, not model responses or answer text.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def export(trace_path: Path, output_path: Path, search_n: int = 200, audit_n: int = 200) -> tuple[int, int]:
    records = json.loads(trace_path.read_text(encoding="utf-8"))
    if not isinstance(records, list):
        raise ValueError("trace must be a JSON list")

    expected_questions = search_n + audit_n
    by_config: dict[str, dict[int, int]] = {}
    for record in records:
        config_id = record["config_id"]
        question_id = int(record["question_id"])
        correctness = record["final_correct"]
        if question_id < 0 or question_id >= expected_questions:
            raise ValueError(f"question id outside declared split: {question_id}")
        if correctness not in (0, 1):
            raise ValueError(f"final_correct is not binary for {config_id}, q={question_id}")
        row = by_config.setdefault(config_id, {})
        if question_id in row:
            raise ValueError(f"duplicate cell: {config_id}, q={question_id}")
        row[question_id] = int(correctness)

    if len(by_config) != 729:
        raise ValueError(f"expected 729 configurations, found {len(by_config)}")
    expected = set(range(expected_questions))
    for config_id, row in by_config.items():
        if set(row) != expected:
            missing = sorted(expected - set(row))
            extra = sorted(set(row) - expected)
            raise ValueError(f"incomplete row {config_id}: missing={missing[:3]}, extra={extra[:3]}")

    config_ids = sorted(by_config)
    header = ["config_id"]
    header.extend(f"search_q{i:03d}" for i in range(search_n))
    header.extend(f"audit_q{i:03d}" for i in range(audit_n))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(header)
        for config_id in config_ids:
            row = by_config[config_id]
            values = [config_id]
            values.extend(row[i] for i in range(search_n))
            values.extend(row[search_n + i] for i in range(audit_n))
            writer.writerow(values)
    return len(config_ids), expected_questions


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
        default=Path("results/experiment1-nine-model-correctness.csv"),
    )
    args = parser.parse_args()
    rows, questions = export(args.trace, args.output)
    print(f"wrote {args.output}: {rows} configurations x {questions} questions")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
