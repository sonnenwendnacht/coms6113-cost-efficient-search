"""Prototype cost-weighted pairwise local racing.

This module is deliberately separate from the existing selector sweep while
the method is being audited.  It uses complete row/question cells only: no
prefix, suffix, model output, verifier state, or unpulled cost is reused.
The method is a heuristic research baseline, not a confidence-certified
best-arm implementation.
"""

from __future__ import annotations

import math
import random
from collections.abc import Sequence
from typing import Any

from .selection_sweep import _hamming_neighbors, _matrix_shape


def _radius(samples: Sequence[float], delta: float, max_races: int, n_questions: int) -> float:
    """Practical paired-race radius; not a fixed-confidence certificate.

    The finite-population Hoeffding radius is too conservative for a search
    heuristic at the small budgets in Experiment 1.  We retain the parameter
    names so a later branch can swap in a proved confidence sequence.  This
    empirical radius is reported as heuristic evidence only.
    """

    m = len(samples)
    if not m:
        return 2.0
    if m >= n_questions:
        return 0.0
    mean = sum(samples) / m
    variance = sum((value - mean) ** 2 for value in samples) / max(1, m - 1)
    return min(2.0, math.sqrt(max(0.02, variance) / m) + 0.5 / math.sqrt(m))


def run_cw_plr(
    rewards: Any,
    costs: Any,
    config_ids: Sequence[str],
    *,
    cell_budget: int | None = None,
    cost_budget: float | None = None,
    seed: int = 0,
    restart_floor: float = 0.15,
    initial_block: int = 2,
    margin: float = 0.0,
    confidence_delta: float = 0.05,
    row_slots: Sequence[Sequence[int]] | None = None,
) -> dict[str, Any]:
    """Run a budgeted pairwise local-racing selector on a search matrix.

    The selector receives only cells it pulls.  A pair race creates an
    independent, pre-shuffled question permutation and consumes its prefix;
    previously observed exact cells may be reused when they occur in that
    prefix.  Give either a cell budget or a realized-cost budget. A pair may
    overshoot a cost budget because its endpoint costs are unknown until the
    calls return; the overshoot is recorded in ``search_cost``.
    """

    k, n = _matrix_shape(rewards, "rewards")
    if _matrix_shape(costs, "costs") != (k, n):
        raise ValueError("rewards and costs must have the same shape")
    if len(config_ids) != k or len(set(str(x) for x in config_ids)) != k:
        raise ValueError("config_ids must be unique and match the matrix")
    if row_slots is not None:
        if len(row_slots) != k or any(len(slot) == 0 for slot in row_slots):
            raise ValueError("row_slots must have one nonempty slot tuple per row")
        slots = [tuple(int(value) for value in slot) for slot in row_slots]
        if len(set(slots)) != k:
            raise ValueError("row_slots must be unique")
        width = len(slots[0])
        if any(len(slot) != width for slot in slots):
            raise ValueError("row_slots must have consistent widths")
    else:
        slots = None
    if (cell_budget is None) == (cost_budget is None):
        raise ValueError("provide exactly one of cell_budget or cost_budget")
    if cell_budget is not None and cell_budget < 1:
        raise ValueError("cell_budget must be positive")
    if cost_budget is not None and (not math.isfinite(cost_budget) or cost_budget <= 0.0):
        raise ValueError("cost_budget must be positive")
    if not 0.0 <= restart_floor <= 1.0:
        raise ValueError("restart_floor must be in [0, 1]")
    if initial_block < 1 or not 0.0 <= margin < 1.0:
        raise ValueError("invalid initial_block or margin")

    rng = random.Random(seed)
    seen: set[tuple[int, int]] = set()
    observed: dict[tuple[int, int], tuple[float, float]] = {}
    pair_stats: dict[tuple[int, int], list[float]] = {}
    pair_costs: dict[tuple[int, int], list[float]] = {}
    total_cost = 0.0
    max_races = max(1, (cell_budget if cell_budget is not None else k * n) // 2)

    def budget_reached() -> bool:
        return (
            (cell_budget is not None and len(seen) >= cell_budget)
            or (cost_budget is not None and total_cost >= cost_budget)
        )

    def pull(arm: int, question: int) -> bool:
        nonlocal total_cost
        cell = (arm, question)
        if cell in seen:
            return False
        reward = float(rewards[arm][question])
        cost = float(costs[arm][question])
        if not math.isfinite(reward) or not math.isfinite(cost) or cost < 0.0:
            raise ValueError("pulled cells must have finite reward and nonnegative cost")
        seen.add(cell)
        observed[cell] = (reward, cost)
        total_cost += cost
        return True

    def predicted_cost(arm: int) -> float:
        values = [cost for (row, _), (_, cost) in observed.items() if row == arm]
        if values:
            return sum(values) / len(values)
        all_values = [cost for _, cost in observed.values()]
        return sum(all_values) / len(all_values) if all_values else 1.0

    def candidate_neighbors(arm: int) -> list[int]:
        if slots is None:
            return [row for row in _hamming_neighbors(arm, k) if row != arm]
        target = slots[arm]
        return [
            row for row, slot in enumerate(slots)
            if row != arm and sum(left != right for left, right in zip(target, slot)) == 1
        ]

    def race(incumbent: int, challenger: int) -> tuple[str, float, float, int]:
        """Run one paired race; return decision, mean, radius, sample count."""

        permutation = list(range(n))
        rng.shuffle(permutation)
        samples: list[float] = []
        costs_for_pair: list[float] = []
        next_check = max(1, initial_block)
        for question in permutation:
            missing = int((incumbent, question) not in seen) + int(
                (challenger, question) not in seen
            )
            if cell_budget is not None and len(seen) + missing > cell_budget:
                break
            if budget_reached():
                break
            pull(incumbent, question)
            pull(challenger, question)
            if (incumbent, question) not in observed or (challenger, question) not in observed:
                continue
            difference = observed[(challenger, question)][0] - observed[(incumbent, question)][0]
            pair_cost = observed[(incumbent, question)][1] + observed[(challenger, question)][1]
            samples.append(difference)
            costs_for_pair.append(pair_cost)
            if len(samples) < next_check:
                continue
            mean = sum(samples) / len(samples)
            radius = _radius(samples, confidence_delta, max_races, n)
            if mean + radius < margin:
                pair_stats[(incumbent, challenger)] = samples[:]
                pair_costs[(incumbent, challenger)] = costs_for_pair[:]
                return "reject", mean, radius, len(samples)
            if mean - radius > margin:
                pair_stats[(incumbent, challenger)] = samples[:]
                pair_costs[(incumbent, challenger)] = costs_for_pair[:]
                return "accept", mean, radius, len(samples)
            next_check = min(n, max(next_check + 1, next_check * 2))
        if samples:
            mean = sum(samples) / len(samples)
            radius = _radius(samples, confidence_delta, max_races, n)
        else:
            mean, radius = 0.0, 2.0
        pair_stats[(incumbent, challenger)] = samples[:]
        pair_costs[(incumbent, challenger)] = costs_for_pair[:]
        return ("accept" if mean > margin else "reject"), mean, radius, len(samples)

    # Spend a small, fixed scout reserve before local search.  Starting from
    # one arbitrary row makes a neighbor heuristic look worse than random
    # search on multimodal landscapes.  Scouts use the same questions but are
    # still paid complete row evaluations; no prefix is reused.
    scout_rows = list(range(k))
    rng.shuffle(scout_rows)
    scout_rows = scout_rows[: min(k, max(3, int(math.sqrt(k))))]
    scout_questions = list(range(n))
    rng.shuffle(scout_questions)
    for row in scout_rows:
        for question in scout_questions[: min(n, initial_block)]:
            if budget_reached():
                break
            pull(row, question)
    incumbent = max(
        (row for row in scout_rows if any(seen_row == row for seen_row, _ in seen)),
        key=lambda row: (
            sum(observed[(row, q)][0] for q in scout_questions if (row, q) in observed)
            / max(1, sum((row, q) in observed for q in scout_questions)),
            -row,
        ),
    )
    races = 0
    accepted = 0
    while not budget_reached() and races < max_races:
        neighbors = candidate_neighbors(incumbent)
        explore = rng.random() < max(restart_floor, 0.35 * (1.0 - races / max_races))
        candidates = list(range(k)) if explore else neighbors
        candidates = [row for row in candidates if row != incumbent]
        if not candidates:
            break

        def proposal_score(row: int) -> tuple[float, float, int]:
            history = pair_stats.get((incumbent, row))
            if not history:
                return (float("inf"), -predicted_cost(row), -row)
            mean = sum(history) / len(history)
            radius = _radius(history, confidence_delta, max_races, n)
            advantage = mean + radius
            pair_cost = sum(pair_costs[(incumbent, row)]) / max(1, len(pair_costs[(incumbent, row)]))
            return (advantage / max(1e-9, pair_cost), -pair_cost, -row)

        challenger = max(candidates, key=proposal_score)
        decision, _, _, count = race(incumbent, challenger)
        races += 1
        if decision == "accept" and count:
            incumbent = challenger
            accepted += 1

    # The selector returns the current incumbent.  Held-out confirmation is a
    # separate caller operation and must not inspect the audit matrix here.
    row_cells = [cell for cell in observed if cell[0] == incumbent]
    direct_mean = (
        sum(observed[cell][0] for cell in row_cells) / len(row_cells) if row_cells else None
    )
    return {
        "selected_config_id": str(config_ids[incumbent]),
        "selected_config_index": incumbent,
        "search_evaluations": len(seen),
        "search_cost": total_cost,
        "selected_observed_accuracy": direct_mean,
        "races": races,
        "accepted_moves": accepted,
        "selection_basis": "cost_weighted_pairwise_local_racing",
        "pair_stats": {f"{a}:{b}": len(values) for (a, b), values in pair_stats.items()},
    }


__all__ = ["run_cw_plr"]
