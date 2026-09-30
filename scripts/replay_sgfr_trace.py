#!/usr/bin/env python3
"""Replay the SGFR prototype on a completed Experiment 1 trace.

The selector sees only the declared search split. Gold correctness and audit
cost are attached after each complete recommendation, as in the standard
Table-7 replay. This is an exploratory fixed-trace experiment, not a live
provider benchmark.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from retry_search.experiment1_report import write_report  # noqa: E402
from retry_search.slot_gated_factorial_racing import run_sgfr  # noqa: E402
from retry_search.selection_sweep import row_slots_from_config_ids  # noqa: E402

REPLAY = __import__("replay_experiment1_nine_model", fromlist=["validate_trace_rectangle", "selector_reward", "_digest", "load_completed_runs", "append_completed_run", "output_directory_lock"])


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("trace_dir", type=Path)
    ap.add_argument("--output-dir", type=Path, required=True)
    ap.add_argument("--selector-reward", choices=("final_correct", "verifier_pass"), default="final_correct")
    ap.add_argument("--seed", action="append", type=int, default=None)
    ap.add_argument("--resume", action="store_true")
    args = ap.parse_args()
    metadata = json.loads((args.trace_dir / "metadata.json").read_text())
    traces = json.loads((args.trace_dir / "traces.json").read_text())
    search_n = int(metadata.get("search_n", 200)); evaluation_n = int(metadata.get("evaluation_n", 200))
    configs, search, evaluation = REPLAY.validate_trace_rectangle(
        traces, metadata, search_n=search_n, evaluation_n=evaluation_n)
    config_index = {name: i for i, name in enumerate(configs)}
    search.sort(key=lambda row: (config_index[str(row["config_id"])], int(row["question_id"])))
    rewards = [[REPLAY.selector_reward(row, args.selector_reward)
                for row in search[i * search_n:(i + 1) * search_n]] for i in range(len(configs))]
    costs = [[float(row["cost_usd"]) for row in search[i * search_n:(i + 1) * search_n]]
             for i in range(len(configs))]
    attempts = [[len(row["attempts"]) for row in search[i * search_n:(i + 1) * search_n]]
                for i in range(len(configs))]
    evaluation_by_config = {name: [] for name in configs}
    deployment_cost_by_config = {name: [] for name in configs}
    for row in evaluation:
        name = str(row["config_id"])
        evaluation_by_config[name].append(float(row["final_correct"]))
        deployment_cost_by_config[name].append(float(row["cost_usd"]))
    exhaustive_cost = sum(sum(row) for row in costs)
    seeds = args.seed or metadata.get("seeds", [6113, 6114, 6115, 6116, 6117, 6118, 6119, 6120])
    settings = [0.01, 0.025, 0.05, 0.1, 0.2, 0.3, 0.5]
    args.output_dir.mkdir(parents=True, exist_ok=True)
    identity = {"trace_sha256": REPLAY._digest(args.trace_dir / "traces.json"),
                "metadata_sha256": REPLAY._digest(args.trace_dir / "metadata.json"),
                "selector_reward": args.selector_reward,
                "runner_sha256": REPLAY._digest(Path(__file__))}
    manifest = args.output_dir / "replay-identity.json"
    checkpoint = args.output_dir / "selector-checkpoint.jsonl"
    with REPLAY.output_directory_lock(args.output_dir):
        if manifest.exists():
            if not args.resume:
                raise SystemExit("output already initialized; use --resume")
            old = json.loads(manifest.read_text())
            if old != identity:
                raise SystemExit("trace, reward, or runner changed; use a new output directory")
        else:
            if checkpoint.exists():
                raise SystemExit("checkpoint without identity manifest")
            manifest.write_text(json.dumps(identity, indent=2) + "\n")
        completed = REPLAY.load_completed_runs(checkpoint)
        runs = []
        row_slots = row_slots_from_config_ids(configs)
        for fraction in settings:
            for seed in seeds:
                setting = {"algorithm": "sgfr", "parameter_name": "budget_fraction",
                           "parameter_value": fraction, "budget_basis": "cell_fraction", "seed": int(seed)}
                key = REPLAY._run_key(setting)
                if key in completed:
                    result = dict(completed[key])
                else:
                    started = time.perf_counter()
                    result = run_sgfr(rewards, costs, configs, attempts=attempts,
                                      row_slots=row_slots, budget_fraction=fraction, seed=int(seed))
                    result.update(setting)
                    result["selection_time_seconds"] = time.perf_counter() - started
                    REPLAY.append_completed_run(checkpoint, result)
                    completed[key] = result
                selected = result.get("selected_config_id")
                if selected is not None:
                    result["heldout_accuracy"] = sum(evaluation_by_config[selected]) / evaluation_n
                    result["heldout_mean_cost"] = sum(deployment_cost_by_config[selected]) / evaluation_n
                runs.append(result)
        oracle = max(configs, key=lambda name: (sum(rewards[config_index[name]]) / search_n,
                                                 -sum(costs[config_index[name]]), name))
        paths = write_report(
            runs, exhaustive_search_cost=exhaustive_cost, output_dir=args.output_dir,
            exhaustive_accuracy=sum(evaluation_by_config[oracle]) / evaluation_n,
            metadata={"trace_dir": str(args.trace_dir), "search_n": search_n,
                      "evaluation_n": evaluation_n, "configs": len(configs),
                      "settings": len(settings), "seeds": list(seeds),
                      "checkpoint_completed_runs": len(runs),
                      "checkpoint_expected_standard_runs": len(settings) * len(seeds),
                      "replay_complete": len(runs) == len(settings) * len(seeds),
                      "selector_reward": args.selector_reward,
                      "exhaustive_reference_config": oracle,
                      "exhaustive_reference_heldout_mean_cost": sum(deployment_cost_by_config[oracle]) / evaluation_n,
                      "replay_identity": identity,
                      "algorithm_note": "SGFR heuristic; gate diagnostics are not confidence bounds"},
        )
    print(json.dumps({"output": paths, "selector_runs": len(runs),
                      "selector_reward": args.selector_reward,
                      "exhaustive_reference_config": oracle}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
