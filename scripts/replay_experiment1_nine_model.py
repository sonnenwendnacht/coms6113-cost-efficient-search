#!/usr/bin/env python3
"""Replay a completed nine-model trace and write Table-7-style artifacts.

Search policies see only the first 200 questions.  The second 200 questions
are used only after a row has been selected, to attach held-out accuracy.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from retry_search.experiment1_report import write_report  # noqa: E402
from retry_search.selection_sweep import default_settings, run_sweep  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("trace_dir", type=Path, help="completed run directory under results/runs")
    ap.add_argument("--output-dir", type=Path, default=None)
    ap.add_argument("--seed", action="append", type=int, default=None)
    args = ap.parse_args()
    trace_dir = args.trace_dir
    traces = json.loads((trace_dir / "traces.json").read_text(encoding="utf-8"))
    if not traces:
        raise SystemExit("traces.json is empty")
    metadata = json.loads((trace_dir / "metadata.json").read_text(encoding="utf-8"))
    search_n = int(metadata.get("search_n", 200))
    evaluation_n = int(metadata.get("evaluation_n", 200))
    configs = sorted({str(row["config_id"]) for row in traces})
    config_index = {name: i for i, name in enumerate(configs)}
    search = [row for row in traces if int(row["question_id"]) < search_n]
    evaluation = [row for row in traces if search_n <= int(row["question_id"]) < search_n + evaluation_n]
    if len(search) != len(configs) * search_n or len(evaluation) != len(configs) * evaluation_n:
        raise SystemExit("trace does not contain exactly the declared search/evaluation rectangle")
    search.sort(key=lambda row: (config_index[str(row["config_id"])], int(row["question_id"])))
    rewards = [[float(row["final_correct"]) for row in search[i * search_n:(i + 1) * search_n]]
               for i in range(len(configs))]
    costs = [[float(row["cost_usd"]) for row in search[i * search_n:(i + 1) * search_n]]
             for i in range(len(configs))]
    evaluation_by_config: dict[str, list[float]] = {name: [] for name in configs}
    evaluation_cost_by_config: dict[str, list[float]] = {name: [] for name in configs}
    for row in evaluation:
        name = str(row["config_id"])
        evaluation_by_config[name].append(float(row["final_correct"]))
        evaluation_cost_by_config[name].append(float(row["cost_usd"]))
    seeds = args.seed if args.seed is not None else metadata.get("seeds", [6113, 6114, 6115, 6116, 6117, 6118, 6119, 6120])
    selector_runs = run_sweep(rewards, costs, configs, settings=default_settings(), seeds=seeds)
    for run in selector_runs:
        selected = str(run["selected_config_id"])
        run["heldout_accuracy"] = sum(evaluation_by_config[selected]) / len(evaluation_by_config[selected])
        run["heldout_mean_cost"] = sum(evaluation_cost_by_config[selected]) / len(evaluation_cost_by_config[selected])
    exhaustive_cost = sum(sum(row) for row in costs)
    oracle = max(configs, key=lambda name: (
        sum(rewards[config_index[name]]) / search_n,
        -sum(costs[config_index[name]]),
        name,
    ))
    exhaustive_accuracy = sum(evaluation_by_config[oracle]) / len(evaluation_by_config[oracle])
    output_dir = args.output_dir or (trace_dir / "selector-report")
    paths = write_report(
        selector_runs,
        exhaustive_search_cost=exhaustive_cost,
        output_dir=output_dir,
        exhaustive_accuracy=exhaustive_accuracy,
        metadata={"trace_dir": str(trace_dir), "search_n": search_n, "evaluation_n": evaluation_n,
                  "configs": len(configs), "settings": len(default_settings()), "seeds": list(seeds),
                  "exhaustive_reference_config": oracle, "exhaustive_search_cost": exhaustive_cost},
    )
    summary = {"output": paths, "configs": len(configs), "search_questions": search_n,
               "evaluation_questions": evaluation_n, "selector_runs": len(selector_runs),
               "exhaustive_search_cost": exhaustive_cost, "exhaustive_reference_config": oracle,
               "exhaustive_heldout_accuracy": exhaustive_accuracy}
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
