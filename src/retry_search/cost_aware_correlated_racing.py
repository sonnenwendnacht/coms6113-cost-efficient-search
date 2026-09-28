"""Prototype of Cost-Aware Correlated Racing (CACR).

CACR is an allocation ablation for Algorithm 2.  It uses same-question
comparisons, Hamming neighbors as proposals, and a conservative forecast of
the next complete-workflow cost.  It never predicts an unpulled cell and it
does not add residuals along a graph path.  The stopping radius is heuristic;
this module is not a fixed-confidence best-arm implementation.
"""

from __future__ import annotations

import math
import random
from collections.abc import Sequence
from typing import Any

from .selection_sweep import _hamming_neighbors, _matrix_shape


def _radius(values: Sequence[float], n_questions: int) -> float:
    if not values:
        return 2.0
    if len(values) >= n_questions:
        return 0.0
    mean = sum(values) / len(values)
    variance = sum((value - mean) ** 2 for value in values) / max(1, len(values) - 1)
    return min(2.0, math.sqrt(max(0.02, variance) / len(values)) + 0.5 / math.sqrt(len(values)))


def run_cacr(
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
    row_slots: Sequence[Sequence[int]] | None = None,
) -> dict[str, Any]:
    """Run the CACR research prototype on a complete row/question matrix.

    A question is a shared random scenario for the two compared rows.  Cells
    already observed are reused as exact values, while each cell is charged at
    most once.  For a cost budget, the final pair can overshoot because its
    realized cascade costs are unknown before the calls return.
    """

    k, n = _matrix_shape(rewards, "rewards")
    if _matrix_shape(costs, "costs") != (k, n):
        raise ValueError("rewards and costs must have the same shape")
    if len(config_ids) != k or len(set(str(item) for item in config_ids)) != k:
        raise ValueError("config_ids must be unique and match the matrix")
    if row_slots is not None:
        if len(row_slots) != k or any(len(slot) == 0 for slot in row_slots):
            raise ValueError("row_slots must have one nonempty slot tuple per row")
        normalized_slots = [tuple(int(value) for value in slot) for slot in row_slots]
        if len(set(normalized_slots)) != k:
            raise ValueError("row_slots must be unique")
    else:
        normalized_slots = None
    if (cell_budget is None) == (cost_budget is None):
        raise ValueError("provide exactly one of cell_budget or cost_budget")
    if cell_budget is not None and cell_budget < 1:
        raise ValueError("cell_budget must be positive")
    if cost_budget is not None and (not math.isfinite(cost_budget) or cost_budget <= 0):
        raise ValueError("cost_budget must be positive")
    if initial_block < 1 or not 0 <= restart_floor <= 1 or not 0 <= margin < 1:
        raise ValueError("invalid racing parameters")

    rng = random.Random(seed)
    seen: set[tuple[int, int]] = set()
    observed: dict[tuple[int, int], tuple[float, float]] = {}
    total_cost = 0.0
    pair_values: dict[tuple[int, int], list[float]] = {}
    pair_questions: dict[tuple[int, int], set[int]] = {}
    pair_permutations: dict[tuple[int, int], list[int]] = {}
    pair_cursors: dict[tuple[int, int], int] = {}
    closed: set[tuple[int, int]] = set()
    rounds = 0
    accepted = 0

    def reached() -> bool:
        return (cell_budget is not None and len(seen) >= cell_budget) or (
            cost_budget is not None and total_cost >= cost_budget
        )

    def pull(row: int, question: int) -> None:
        nonlocal total_cost
        cell = (row, question)
        if cell in seen:
            return
        reward = float(rewards[row][question])
        cost = float(costs[row][question])
        if not math.isfinite(reward) or not math.isfinite(cost) or cost < 0:
            raise ValueError("pulled cells must have finite reward and nonnegative cost")
        seen.add(cell)
        observed[cell] = reward, cost
        total_cost += cost

    def row_values(row: int) -> list[float]:
        return [reward for (seen_row, _), (reward, _) in observed.items() if seen_row == row]

    def row_costs(row: int) -> list[float]:
        return [cost for (seen_row, _), (_, cost) in observed.items() if seen_row == row]

    def row_estimate(row: int) -> tuple[float, float]:
        values = row_values(row)
        if not values:
            return 0.5, 1.0
        return sum(values) / len(values), _radius(values, n)

    def predicted_row_cost(row: int) -> float:
        values = row_costs(row)
        if not values:
            all_values = [cost for _, cost in observed.values()]
            return sum(all_values) / len(all_values) if all_values else 1.0
        mean = sum(values) / len(values)
        if len(values) == 1:
            return mean * 1.25
        variance = sum((value - mean) ** 2 for value in values) / (len(values) - 1)
        return max(1e-9, mean + 1.96 * math.sqrt(variance / len(values)))

    def neighbors(row: int) -> list[int]:
        if normalized_slots is None:
            return [candidate for candidate in _hamming_neighbors(row, k) if candidate != row]
        target = normalized_slots[row]
        return [
            candidate
            for candidate, slot in enumerate(normalized_slots)
            if candidate != row and len(slot) == len(target) and sum(a != b for a, b in zip(slot, target)) == 1
        ]

    def block_choice(pair: tuple[int, int]) -> int:
        history = pair_values.get(pair, [])
        remaining = max(1, n - len(history))
        current = _radius(history, n)
        pair_cost = predicted_row_cost(pair[0]) + predicted_row_cost(pair[1])
        best: tuple[float, int] | None = None
        for candidate in (1, 2, 4, 8, 16, 32):
            block = min(candidate, remaining)
            after = _radius(history + [0.5] * block, n)
            gain = max(0.0, current - after)
            # A small fixed term prevents always choosing one-cell blocks when
            # the uncertainty curve is nearly flat.
            score = (gain + 0.01 * current) / max(1e-9, block * pair_cost)
            if best is None or score > best[0]:
                best = score, block
        return best[1] if best else 1

    def race_block(incumbent: int, challenger: int, block: int) -> tuple[str, int]:
        pair = (incumbent, challenger)
        values = pair_values.setdefault(pair, [])
        known_questions = pair_questions.setdefault(pair, set())
        permutation = pair_permutations.setdefault(pair, rng.sample(range(n), n))
        cursor = pair_cursors.setdefault(pair, 0)
        processed = 0
        while cursor < n and processed < block and not reached():
            question = permutation[cursor]
            missing = int((incumbent, question) not in seen) + int((challenger, question) not in seen)
            if cell_budget is not None and len(seen) + missing > cell_budget:
                break
            pull(incumbent, question)
            pull(challenger, question)
            if question not in known_questions:
                values.append(observed[(challenger, question)][0] - observed[(incumbent, question)][0])
                known_questions.add(question)
            processed += 1
            cursor += 1
        pair_cursors[pair] = cursor

        if not values:
            return "reject", processed
        mean = sum(values) / len(values)
        radius = _radius(values, n)
        if mean + radius < margin:
            closed.add(pair)
            return "reject", processed
        if mean - radius > margin:
            return "accept", processed
        if len(values) >= n:
            return ("accept" if mean > margin else "reject"), processed
        return "open", processed

    scout_rows = list(range(k))
    rng.shuffle(scout_rows)
    scout_rows = scout_rows[: min(k, max(3, int(math.sqrt(k))))]
    scout_questions = list(range(n))
    rng.shuffle(scout_questions)
    for row in scout_rows:
        for question in scout_questions[: min(n, initial_block)]:
            if reached():
                break
            pull(row, question)

    incumbent = max(scout_rows or [rng.randrange(k)], key=lambda row: row_estimate(row)[0] + row_estimate(row)[1])
    while not reached() and rounds < max(1, k * n):
        rounds += 1
        local_candidates = neighbors(incumbent)
        pool = list(range(k)) if rng.random() < max(restart_floor, 0.35 * (1 - rounds / max(1, k * n))) else local_candidates
        candidates = [row for row in pool if row != incumbent and (incumbent, row) not in closed]
        candidates = [row for row in candidates if len(pair_questions.get((incumbent, row), set())) < n]
        if not candidates:
            break

        inc_mean, inc_radius = row_estimate(incumbent)

        def proposal_score(row: int) -> float:
            pair = (incumbent, row)
            history = pair_values.get(pair, [])
            pair_mean = sum(history) / len(history) if history else row_estimate(row)[0] - inc_mean
            pair_radius = _radius(history, n) if history else row_estimate(row)[1] + inc_radius
            block = block_choice(pair)
            pair_cost = predicted_row_cost(incumbent) + predicted_row_cost(row)
            expected_gain = pair_radius - _radius(history + [0.5] * block, n)
            # Prefer candidates that might beat the incumbent, but spend on
            # uncertainty only when the expected reduction per cost is useful.
            return pair_mean + pair_radius + 0.05 * expected_gain / max(1e-9, block * pair_cost) - 0.01 * pair_cost

        challenger = max(candidates, key=proposal_score)
        block = block_choice((incumbent, challenger))
        decision, processed = race_block(incumbent, challenger, block)
        if not processed:
            closed.add((incumbent, challenger))
            continue
        if decision == "accept":
            incumbent = challenger
            accepted += 1
        elif decision == "reject":
            closed.add((incumbent, challenger))

    direct = row_values(incumbent)
    return {
        "selected_config_id": str(config_ids[incumbent]),
        "selected_config_index": incumbent,
        "search_evaluations": len(seen),
        "search_cost": total_cost,
        "selected_observed_accuracy": sum(direct) / len(direct) if direct else None,
        "races": rounds,
        "accepted_moves": accepted,
        "selection_basis": "cost_aware_correlated_racing",
        "observed_pairs": len(pair_values),
    }


__all__ = ["run_cacr"]
