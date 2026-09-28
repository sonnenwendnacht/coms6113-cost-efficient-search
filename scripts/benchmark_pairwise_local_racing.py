#!/usr/bin/env python3
"""Synthetic, held-out check for the CW-PLR research candidate.

This benchmark is deliberately separate from MathQA and makes no claim about
the real experiment.  Search and audit questions are generated independently.
All selectors receive the same cell budget and the report includes realized
cost, rather than comparing incompatible fraction parameters.
"""

from __future__ import annotations

import argparse
import json
import random
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from retry_search.pairwise_local_racing import run_cw_plr  # noqa: E402
from retry_search.cost_aware_correlated_racing import run_cacr  # noqa: E402


def make_matrix(side: int, questions: int, offset: int) -> tuple[list[list[float]], list[list[float]]]:
    rewards: list[list[float]] = []
    costs: list[list[float]] = []
    for arm in range(side**3):
        digits = ((arm // (side * side)) % side, (arm // side) % side, arm % side)
        distance = sum(abs(value - (side - 1)) for value in digits)
        mean = max(0.05, 0.9 - 0.12 * distance)
        row_rewards = []
        row_costs = []
        for question in range(questions):
            hash_value = (question * 37 + arm * 19 + offset * 101) % 1000
            row_rewards.append(float(hash_value < mean * 1000))
            row_costs.append(1.0 + 0.15 * sum(digits) + 0.01 * ((question + arm) % 5))
        rewards.append(row_rewards)
        costs.append(row_costs)
    return rewards, costs


def random_cell_selector(rewards, costs, budget: int, seed: int) -> dict:
    rng = random.Random(seed)
    k, n = len(rewards), len(rewards[0])
    cells = [(arm, question) for arm in range(k) for question in range(n)]
    rng.shuffle(cells)
    pulled = cells[:budget]
    by_row: dict[int, list[float]] = {}
    spend = 0.0
    for arm, question in pulled:
        by_row.setdefault(arm, []).append(rewards[arm][question])
        spend += costs[arm][question]
    selected = max(by_row, key=lambda row: (sum(by_row[row]) / len(by_row[row]), -row))
    return {"selected_config_index": selected, "search_evaluations": len(pulled), "search_cost": spend}


def random_cost_selector(rewards, costs, cap: float, seed: int) -> dict:
    rng = random.Random(seed)
    k, n = len(rewards), len(rewards[0])
    cells = [(arm, question) for arm in range(k) for question in range(n)]
    rng.shuffle(cells)
    pulled = []
    spend = 0.0
    for arm, question in cells:
        if spend >= cap:
            break
        pulled.append((arm, question))
        spend += costs[arm][question]
    by_row: dict[int, list[float]] = {}
    for arm, question in pulled:
        by_row.setdefault(arm, []).append(rewards[arm][question])
    selected = max(by_row, key=lambda row: (sum(by_row[row]) / len(by_row[row]), -row))
    return {"selected_config_index": selected, "search_evaluations": len(pulled), "search_cost": spend}


def evaluate(result: dict, audit_rewards, audit_costs) -> dict:
    arm = result["selected_config_index"]
    result = dict(result)
    result["audit_accuracy"] = statistics.mean(audit_rewards[arm])
    result["audit_cold_cost"] = statistics.mean(audit_costs[arm])
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--side", type=int, default=3)
    parser.add_argument("--search-questions", type=int, default=50)
    parser.add_argument("--audit-questions", type=int, default=200)
    parser.add_argument("--seeds", type=int, default=20)
    parser.add_argument("--fraction", type=float, default=0.1)
    parser.add_argument("--cost-cap", type=float, default=None)
    args = parser.parse_args()
    k = args.side**3
    if args.cost_cap is not None and args.cost_cap <= 0:
        parser.error("--cost-cap must be positive")
    budget = None if args.cost_cap is not None else max(2, int(args.fraction * k * args.search_questions))
    search_rewards, search_costs = make_matrix(args.side, args.search_questions, 0)
    audit_rewards, audit_costs = make_matrix(args.side, args.audit_questions, 1)
    ids = [str(i) for i in range(k)]
    records: list[dict] = []
    for seed in range(args.seeds):
        random_result = (
            random_cost_selector(search_rewards, search_costs, args.cost_cap, seed)
            if args.cost_cap is not None
            else random_cell_selector(search_rewards, search_costs, budget, seed)
        )
        records.append(evaluate({"algorithm": "random_cells", **random_result}, audit_rewards, audit_costs))
        plr_kwargs = {"cost_budget": args.cost_cap} if args.cost_cap is not None else {"cell_budget": budget}
        plr = run_cw_plr(search_rewards, search_costs, ids, seed=seed, **plr_kwargs)
        records.append(evaluate({"algorithm": "cw_plr", **plr}, audit_rewards, audit_costs))
        cacr = run_cacr(search_rewards, search_costs, ids, seed=seed, **plr_kwargs)
        records.append(evaluate({"algorithm": "cacr", **cacr}, audit_rewards, audit_costs))
    summary = {}
    for algorithm in ("random_cells", "cw_plr", "cacr"):
        rows = [row for row in records if row["algorithm"] == algorithm]
        summary[algorithm] = {
            "mean_audit_accuracy": statistics.mean(row["audit_accuracy"] for row in rows),
            "audit_optimal_rate": sum(row["selected_config_index"] == k - 1 for row in rows) / len(rows),
            "mean_search_evaluations": statistics.mean(row["search_evaluations"] for row in rows),
            "mean_search_cost": statistics.mean(row["search_cost"] for row in rows),
            "mean_audit_cold_cost": statistics.mean(row["audit_cold_cost"] for row in rows),
        }
    print(json.dumps({"synthetic": True, "settings": vars(args), "budget_cells": budget, "cost_cap": args.cost_cap, "summary": summary}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
