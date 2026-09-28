"""Gated Safe Cost-aware Correlated Racing (SCCR) prototype.

This module is an intentionally small research prototype, not a fixed-confidence
best-arm theorem.  It tests whether same-question pair comparisons are safe to
use before spending more cells on a local race.  The gate is empirical:
correlated racing is allowed only when a calibration block shows a conservative
reduction in paired-difference variance.  If the gate fails, the algorithm
falls back to direct row estimates and random/global proposals.

The selector never predicts an unobserved cell and always returns a row that
was directly evaluated.  A fixed per-pair question permutation is consumed as
a prefix; questions are not selected after seeing their outcomes.
"""

from __future__ import annotations

import math
import random
from collections.abc import Sequence
from typing import Any

from .cost_aware_correlated_racing import _radius
from .selection_sweep import _hamming_neighbors, _matrix_shape


def _variance(values: Sequence[float]) -> float:
    if len(values) < 2:
        return 0.0
    mean = sum(values) / len(values)
    return sum((value - mean) ** 2 for value in values) / (len(values) - 1)


def _validate(
    rewards: Any,
    costs: Any,
    config_ids: Sequence[str],
    *,
    cell_budget: int | None,
    cost_budget: float | None,
    restart_floor: float,
    initial_block: int,
    calibration_block: int,
    min_reduction: float,
    variance_margin: float,
) -> tuple[int, int, list[tuple[int, ...]] | None]:
    k, n = _matrix_shape(rewards, "rewards")
    if _matrix_shape(costs, "costs") != (k, n):
        raise ValueError("rewards and costs must have the same shape")
    if len(config_ids) != k or len(set(str(item) for item in config_ids)) != k:
        raise ValueError("config_ids must be unique and match the matrix")
    if (cell_budget is None) == (cost_budget is None):
        raise ValueError("provide exactly one of cell_budget or cost_budget")
    if cell_budget is not None and cell_budget < 1:
        raise ValueError("cell_budget must be positive")
    if cost_budget is not None and (not math.isfinite(cost_budget) or cost_budget <= 0):
        raise ValueError("cost_budget must be positive")
    if initial_block < 1 or calibration_block < 2:
        raise ValueError("initial_block must be positive and calibration_block at least 2")
    if not 0 <= restart_floor <= 1:
        raise ValueError("restart_floor must be in [0, 1]")
    if not math.isfinite(min_reduction) or not 0 <= min_reduction < 1:
        raise ValueError("invalid min_reduction")
    if not math.isfinite(variance_margin) or variance_margin < 0:
        raise ValueError("invalid gate parameters")
    return k, n, None


def run_sccr(
    rewards: Any,
    costs: Any,
    config_ids: Sequence[str],
    *,
    cell_budget: int | None = None,
    cost_budget: float | None = None,
    seed: int = 0,
    restart_floor: float = 0.15,
    initial_block: int = 2,
    calibration_block: int = 4,
    min_reduction: float = 0.10,
    variance_margin: float = 0.25,
    margin: float = 0.0,
    row_slots: Sequence[Sequence[int]] | None = None,
) -> dict[str, Any]:
    """Run SCCR under a cell or realized-cost budget.

    ``min_reduction`` is the required empirical paired-variance reduction.  The
    additive ``variance_margin`` is divided by ``sqrt(m)`` for a conservative
    small-sample buffer.  These are tuning parameters for an ablation, not a
    confidence guarantee.  Calibration cells are charged once and reused by
    the subsequent race.  Unsafe local pairs use direct row means/radii.
    """

    k, n, _ = _validate(
        rewards,
        costs,
        config_ids,
        cell_budget=cell_budget,
        cost_budget=cost_budget,
        restart_floor=restart_floor,
        initial_block=initial_block,
        calibration_block=calibration_block,
        min_reduction=min_reduction,
        variance_margin=variance_margin,
    )
    if not math.isfinite(margin) or not 0 <= margin < 1:
        raise ValueError("margin must be in [0, 1)")

    if row_slots is not None:
        if len(row_slots) != k or any(len(slot) == 0 for slot in row_slots):
            raise ValueError("row_slots must have one nonempty slot tuple per row")
        slots = [tuple(int(value) for value in slot) for slot in row_slots]
        if len(set(slots)) != k:
            raise ValueError("row_slots must be unique")
    else:
        slots = None

    rng = random.Random(seed)
    seen: set[tuple[int, int]] = set()
    observed: dict[tuple[int, int], tuple[float, float]] = {}
    total_cost = 0.0
    pair_values: dict[tuple[int, int], list[float]] = {}
    pair_questions: dict[tuple[int, int], set[int]] = {}
    pair_permutations: dict[tuple[int, int], list[int]] = {}
    pair_cursors: dict[tuple[int, int], int] = {}
    pair_safe: dict[tuple[int, int], bool] = {}
    closed: set[tuple[int, int]] = set()
    rounds = 0
    accepted = 0
    calibration_evaluations = 0
    gated_fallbacks = 0

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
        return max(1e-9, mean + 1.96 * math.sqrt(_variance(values) / len(values)))

    def neighbors(row: int) -> list[int]:
        if slots is None:
            return [candidate for candidate in _hamming_neighbors(row, k) if candidate != row]
        target = slots[row]
        return [
            candidate
            for candidate, slot in enumerate(slots)
            if candidate != row
            and len(slot) == len(target)
            and sum(a != b for a, b in zip(slot, target)) == 1
        ]

    def pair_key(incumbent: int, challenger: int) -> tuple[int, int]:
        return incumbent, challenger

    def permutation_for(pair: tuple[int, int]) -> list[int]:
        if pair not in pair_permutations:
            pair_permutations[pair] = rng.sample(range(n), n)
        return pair_permutations[pair]

    def take_pair_questions(pair: tuple[int, int], block: int) -> int:
        """Pull a fixed prefix for a pair, returning newly processed questions."""
        incumbent, challenger = pair
        values = pair_values.setdefault(pair, [])
        known_questions = pair_questions.setdefault(pair, set())
        permutation = permutation_for(pair)
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
        return processed

    def calibrate(pair: tuple[int, int]) -> bool | None:
        """Calibrate a pair once; None means budget ended before calibration."""
        nonlocal calibration_evaluations
        if pair in pair_safe:
            return pair_safe[pair]
        processed = take_pair_questions(pair, min(calibration_block, n))
        calibration_evaluations += processed
        if processed == 0 and not pair_questions.get(pair):
            return None
        values = pair_values[pair]
        if len(values) < 2:
            pair_safe[pair] = False
            return False
        inc, ch = pair
        inc_values = [observed[(inc, q)][0] for q in pair_questions[pair] if (inc, q) in observed]
        ch_values = [observed[(ch, q)][0] for q in pair_questions[pair] if (ch, q) in observed]
        paired_var = _variance(values)
        independent_var = _variance(inc_values) + _variance(ch_values)
        # The additive term is a deliberately simple small-sample uncertainty
        # buffer.  It prevents declaring safety from a noisy tiny block.
        if independent_var <= 1e-12:
            # A constant calibration block establishes no covariance benefit.
            pair_safe[pair] = False
            return False
        ratio = paired_var / independent_var
        conservative_ratio = ratio + variance_margin / math.sqrt(len(values))
        is_safe = conservative_ratio <= 1.0 - min_reduction
        pair_safe[pair] = is_safe
        return is_safe

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
            score = (gain + 0.01 * current) / max(1e-9, block * pair_cost)
            if best is None or score > best[0]:
                best = score, block
        return best[1] if best else 1

    def paired_decision(pair: tuple[int, int]) -> str:
        values = pair_values.get(pair, [])
        if not values:
            return "reject"
        mean = sum(values) / len(values)
        radius = _radius(values, n)
        if mean + radius < margin:
            return "reject"
        if mean - radius > margin:
            return "accept"
        if len(values) >= n:
            return "accept" if mean > margin else "reject"
        return "open"

    def direct_decision(incumbent: int, challenger: int) -> str:
        inc_mean, inc_radius = row_estimate(incumbent)
        ch_mean, ch_radius = row_estimate(challenger)
        delta = ch_mean - inc_mean
        radius = inc_radius + ch_radius
        if delta + radius < margin:
            return "reject"
        if delta - radius > margin:
            return "accept"
        # At a complete question budget, choose by directly observed mean.
        if len(row_values(challenger)) >= n and len(row_values(incumbent)) >= n:
            return "accept" if delta > margin else "reject"
        return "open"

    def race_pair(pair: tuple[int, int], safe: bool) -> tuple[str, int]:
        nonlocal gated_fallbacks
        incumbent, challenger = pair
        block = block_choice(pair)
        if not safe:
            gated_fallbacks += 1
        processed = take_pair_questions(pair, block)
        return (paired_decision(pair) if safe else direct_decision(incumbent, challenger)), processed

    # Small initial scout, as in CACR.  This is direct row evidence only.
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

    incumbent = max(
        (row for row in scout_rows if row_values(row)),
        key=lambda row: row_estimate(row)[0] + row_estimate(row)[1],
    )
    while not reached() and rounds < max(1, k * n):
        rounds += 1
        local_candidates = neighbors(incumbent)
        use_global = rng.random() < max(restart_floor, 0.35 * (1 - rounds / max(1, k * n)))
        pool = list(range(k)) if use_global else local_candidates
        candidates = [row for row in pool if row != incumbent and (incumbent, row) not in closed]
        candidates = [row for row in candidates if len(pair_questions.get(pair_key(incumbent, row), set())) < n]
        if not candidates:
            candidates = [
                row for row in range(k) if row != incumbent
                and (incumbent, row) not in closed
                and len(pair_questions.get((incumbent, row), set())) < n
            ]
        if not candidates:
            break

        inc_mean, inc_radius = row_estimate(incumbent)

        def proposal_score(row: int) -> float:
            pair = pair_key(incumbent, row)
            history = pair_values.get(pair, [])
            pair_mean = sum(history) / len(history) if history else row_estimate(row)[0] - inc_mean
            pair_radius = _radius(history, n) if history else row_estimate(row)[1] + inc_radius
            block = block_choice(pair)
            pair_cost = predicted_row_cost(incumbent) + predicted_row_cost(row)
            expected_gain = pair_radius - _radius(history + [0.5] * block, n)
            # Unsafe pairs are still available as direct fallbacks, but local
            # correlated proposals receive a small preference only after gate.
            gate_bonus = 0.02 if pair_safe.get(pair) is True else 0.0
            return pair_mean + pair_radius + gate_bonus + 0.05 * expected_gain / max(1e-9, block * pair_cost) - 0.01 * pair_cost

        challenger = max(candidates, key=proposal_score)
        pair = pair_key(incumbent, challenger)
        safe = calibrate(pair)
        if safe is None:
            break
        decision, processed = race_pair(pair, safe)
        if decision == "accept":
            incumbent = challenger
            accepted += 1
        elif decision == "reject" or not processed:
            closed.add(pair)

    direct = row_values(incumbent)
    safe_edges = sum(value is True for value in pair_safe.values())
    unsafe_edges = sum(value is False for value in pair_safe.values())
    return {
        "selected_config_id": str(config_ids[incumbent]),
        "selected_config_index": incumbent,
        "search_evaluations": len(seen),
        "search_cost": total_cost,
        "selected_observed_accuracy": sum(direct) / len(direct) if direct else None,
        "races": rounds,
        "accepted_moves": accepted,
        "selection_basis": "safe_cost_aware_correlated_racing",
        "observed_pairs": len(pair_values),
        "safe_edges": safe_edges,
        "unsafe_edges": unsafe_edges,
        "calibration_evaluations": calibration_evaluations,
        "gated_fallbacks": gated_fallbacks,
        "gate_parameters": {
            "calibration_block": calibration_block,
            "min_reduction": min_reduction,
            "variance_margin": variance_margin,
        },
    }


__all__ = ["run_sccr"]
