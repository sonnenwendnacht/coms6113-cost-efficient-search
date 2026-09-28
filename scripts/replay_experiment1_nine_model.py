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
from retry_search.pairwise_local_racing import run_cw_plr  # noqa: E402
from retry_search.cost_aware_correlated_racing import run_cacr  # noqa: E402
from retry_search.safe_correlated_racing import run_sccr  # noqa: E402


def _question_id(value: object, *, source: str) -> int:
    """Return a real integer question id, rejecting booleans and strings.

    JSON booleans are subclasses of ``int`` in Python.  Treating ``true`` as
    question 1 would make a malformed checkpoint look like a complete
    rectangle, so replay validates the on-disk type explicitly.
    """

    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{source}: question_id must be an integer")
    return value


def validate_trace_rectangle(
    traces: list[dict],
    metadata: dict,
    *,
    search_n: int,
    evaluation_n: int,
) -> tuple[list[str], list[dict], list[dict]]:
    """Validate the complete config/question rectangle before replay.

    A length check alone is unsafe: one duplicate cell can replace a missing
    cell while preserving the expected number of records.  This validator
    checks the full key set for both partitions, rejects unknown rows and
    question ids, and keeps search/evaluation questions disjoint.
    """

    if search_n <= 0 or evaluation_n <= 0:
        raise ValueError("search_n and evaluation_n must be positive")
    configs = sorted({str(row.get("config_id")) for row in traces if isinstance(row, dict)})
    if not configs or any(not isinstance(row, dict) for row in traces):
        raise ValueError("trace records must be nonempty JSON objects")
    declared_rows = metadata.get("rows")
    if declared_rows is not None:
        if isinstance(declared_rows, bool) or not isinstance(declared_rows, int) or declared_rows <= 0:
            raise ValueError("metadata.rows must be a positive integer")
        if declared_rows != len(configs):
            raise ValueError(
                f"metadata declares {declared_rows} rows but trace contains {len(configs)} config ids"
            )

    config_set = set(configs)
    total_questions = search_n + evaluation_n
    expected = {(config_id, question_id)
                for config_id in configs for question_id in range(total_questions)}
    seen: set[tuple[str, int]] = set()
    for index, row in enumerate(traces):
        config_id = row.get("config_id")
        if not isinstance(config_id, str) or config_id not in config_set:
            raise ValueError(f"trace record {index}: unknown config_id")
        question_id = _question_id(row.get("question_id"), source=f"trace record {index}")
        if not 0 <= question_id < total_questions:
            raise ValueError(f"trace record {index}: question_id outside declared split")
        key = (config_id, question_id)
        if key in seen:
            raise ValueError(f"duplicate trace cell: config_id={config_id!r}, question_id={question_id}")
        seen.add(key)
    missing = expected - seen
    unexpected = seen - expected
    if unexpected or missing or len(seen) != len(expected):
        raise ValueError(
            "trace does not contain exactly one cell for every config/question pair "
            f"(missing={sorted(missing)[:3]}, unexpected={sorted(unexpected)[:3]})"
        )

    search = [row for row in traces if _question_id(row["question_id"], source="search split") < search_n]
    evaluation = [row for row in traces if _question_id(row["question_id"], source="evaluation split") >= search_n]
    expected_search = len(configs) * search_n
    expected_evaluation = len(configs) * evaluation_n
    if len(search) != expected_search or len(evaluation) != expected_evaluation:
        raise ValueError("trace search/evaluation split is not a complete disjoint rectangle")
    return configs, search, evaluation


def row_slots_from_config_ids(config_ids: list[str]) -> list[tuple[int, ...]]:
    """Decode slash-separated complete rows into explicit Hamming slots.

    Structured selectors must receive these slots instead of relying on row
    list order.  The mapping is deterministic per slot position and preserves
    adjacency even when config ids are shuffled or lexicographically sorted.
    """

    parts = [config_id.split("/") for config_id in config_ids]
    if any(len(values) < 2 or any(not value for value in values) for values in parts):
        raise ValueError("structured replay requires slash-separated config ids")
    width = len(parts[0])
    if any(len(values) != width for values in parts):
        raise ValueError("all config ids must have the same number of slash-separated slots")
    levels = [{values[position] for values in parts} for position in range(width)]
    indexes = [{value: index for index, value in enumerate(sorted(values))}
               for values in levels]
    slots = [tuple(indexes[position][values[position]] for position in range(width))
             for values in parts]
    if len(set(slots)) != len(config_ids):
        raise ValueError("config ids map to duplicate row slots")
    return slots


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("trace_dir", type=Path, help="completed run directory under results/runs")
    ap.add_argument("--output-dir", type=Path, default=None)
    ap.add_argument("--seed", action="append", type=int, default=None)
    ap.add_argument("--include-structured", action="store_true",
                    help="also replay CW-PLR, CACR, and SCCR at realized-cost fractions")
    args = ap.parse_args()
    trace_dir = args.trace_dir
    traces = json.loads((trace_dir / "traces.json").read_text(encoding="utf-8"))
    if not traces:
        raise SystemExit("traces.json is empty")
    metadata = json.loads((trace_dir / "metadata.json").read_text(encoding="utf-8"))
    search_n = int(metadata.get("search_n", 200))
    evaluation_n = int(metadata.get("evaluation_n", 200))
    try:
        configs, search, evaluation = validate_trace_rectangle(
            traces, metadata, search_n=search_n, evaluation_n=evaluation_n
        )
    except ValueError as exc:
        raise SystemExit(f"invalid completed trace: {exc}") from exc
    if args.include_structured:
        try:
            row_slots = row_slots_from_config_ids(configs)
        except ValueError as exc:
            raise SystemExit(str(exc)) from exc
    else:
        row_slots = None
    config_index = {name: i for i, name in enumerate(configs)}
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
    exhaustive_cost = sum(sum(row) for row in costs)
    seeds = args.seed if args.seed is not None else metadata.get("seeds", [6113, 6114, 6115, 6116, 6117, 6118, 6119, 6120])
    selector_runs = run_sweep(rewards, costs, configs, settings=default_settings(), seeds=seeds)
    if args.include_structured:
        # These are explicit cost-budget settings, analogous to the budget
        # rows in AgentOpt's Table 7.  The methods see only search cells; the
        # held-out matrix is attached below after each recommendation.
        for fraction in (0.10, 0.20, 0.40, 0.60, 0.80, 1.00):
            budget = exhaustive_cost * fraction
            for seed in seeds:
                structured = (
                    ("cw_plr", run_cw_plr(rewards, costs, configs, cost_budget=budget, seed=int(seed))),
                    ("cacr", run_cacr(rewards, costs, configs, cost_budget=budget, seed=int(seed),
                                       row_slots=row_slots)),
                    ("sccr", run_sccr(rewards, costs, configs, cost_budget=budget, seed=int(seed),
                                       row_slots=row_slots)),
                )
                for algorithm, result in structured:
                    result.update({"algorithm": algorithm, "parameter_name": "cost_fraction",
                                   "parameter_value": fraction, "seed": int(seed)})
                    selector_runs.append(result)
    for run in selector_runs:
        selected = str(run["selected_config_id"])
        run["heldout_accuracy"] = sum(evaluation_by_config[selected]) / len(evaluation_by_config[selected])
        run["heldout_mean_cost"] = sum(evaluation_cost_by_config[selected]) / len(evaluation_cost_by_config[selected])
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
