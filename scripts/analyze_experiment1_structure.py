#!/usr/bin/env python3
"""Descriptive search-only structure diagnostic; never supplies a selector prior."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np


def analyze(run_dir: Path) -> dict:
    meta = json.loads((run_dir / "metadata.json").read_text())
    n = meta["search_n"]
    bank = {}
    trace_path = run_dir / "traces.jsonl"
    digest = hashlib.sha256()
    with trace_path.open("rb") as handle:
        for line in handle:
            digest.update(line)
            record = json.loads(line)
            q = record["question_id"]
            if q >= n:
                continue
            row = bank.setdefault(record["config_id"], {})
            if q in row:
                raise ValueError("duplicate search cell")
            row[q] = (record["final_correct"], record["cost_usd"])
    ids = sorted(bank)
    if len(ids) != meta["rows"] or any(set(row) != set(range(n)) for row in bank.values()):
        raise ValueError("incomplete search rectangle")
    y = np.array([[bank[r][q][0] for q in range(n)] for r in ids], dtype=float)
    c = np.array([[bank[r][q][1] for q in range(n)] for r in ids], dtype=float)
    slots = np.array([r.split("/") for r in ids])
    means, variances, prices = y.mean(axis=1), y.var(axis=1), c.mean(axis=1)
    cov = (y @ y.T) / n - means[:, None] * means[None, :]
    main_prediction = np.full(len(ids), means.mean())
    main_effects = {}
    for position in range(slots.shape[1]):
        levels = sorted(set(slots[:, position]))
        effects = {level: float(means[slots[:, position] == level].mean() - means.mean())
                   for level in levels}
        main_effects[str(position + 1)] = effects
        main_prediction += np.array([effects[level] for level in slots[:, position]])
    left, right = np.triu_indices(len(ids), 1)
    changed = slots[left] != slots[right]
    distance = changed.sum(axis=1)
    groups = {f"distance_{d}": distance == d for d in range(1, slots.shape[1] + 1)}
    groups.update({f"only_slot_{p + 1}": (distance == 1) & changed[:, p]
                   for p in range(slots.shape[1])})
    statistics = {}
    for label, mask in groups.items():
        a, b = left[mask], right[mask]
        residual_var = np.maximum(0., variances[a] + variances[b] - 2 * cov[a, b])
        gap = means[b] - means[a]
        disagreement = np.maximum(0., residual_var + gap ** 2)
        paired_coefficient = residual_var * (prices[a] + prices[b])
        independent_coefficient = (np.sqrt(variances[a] * prices[a])
                                   + np.sqrt(variances[b] * prices[b])) ** 2
        ratios = paired_coefficient / np.maximum(independent_coefficient, 1e-30)
        statistics[label] = {
            "pairs": int(len(a)),
            "mean_disagreement": float(disagreement.mean()),
            "mean_residual_variance": float(residual_var.mean()),
            "mean_absolute_accuracy_gap": float(np.abs(gap).mean()),
            "equal_reward_vector_fraction": float((disagreement < 1e-12).mean()),
            "mean_pair_cell_charge": float((prices[a] + prices[b]).mean()),
            "median_paired_to_independent_variance_cost_coefficient": float(np.median(ratios)),
        }
    total_var = float(means.var())
    return {
        "scope": "descriptive search-only full-reference diagnostic; not free selector knowledge",
        "trace_jsonl_sha256": digest.hexdigest(), "rows": len(ids), "search_questions": n,
        "numpy": np.__version__, "unique_search_reward_vectors": int(len(np.unique(y, axis=0))),
        "main_effects_explained_row_mean_variance": (
            1 - float(np.mean((means - main_prediction) ** 2)) / total_var if total_var else None),
        "first_slot_explained_row_mean_variance": (
            float(np.var([main_effects['1'][x] for x in slots[:, 0]])) / total_var if total_var else None),
        "by_pair_group": statistics,
        "caution": "Variance-cost coefficients omit confidence/range/calibration terms and are not predicted savings. "
                   "Many near-zero residuals can reflect unreached retry slots. No prefix reuse or model calls.",
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("run_dir", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = analyze(args.run_dir)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
