"""Cost-synchronized successive rejects for complete retry rows.

This is a transparent research baseline for Algorithm 2.  It evaluates every
active complete row on the same question block, then removes one empirical
loser.  A cost budget uses realized cell charges and may overshoot because a
future retry path is not known before the cell runs.  The stopping radius is a
heuristic diagnostic; this module is not a confidence-certified implementation.

No workflow prefix, suffix, model output, or verifier state is reused.  The
only sharing is that active rows are evaluated on the same question IDs.
"""

from __future__ import annotations

import math
import random
from collections.abc import Sequence
from typing import Any

from .selection_sweep import _matrix_shape


def _heuristic_radius(values: Sequence[float], total_questions: int) -> float:
    """Return a diagnostic radius, not a simultaneous confidence bound."""

    if not values:
        return 1.0
    if len(values) >= total_questions:
        return 0.0
    mean = sum(values) / len(values)
    variance = sum((value - mean) ** 2 for value in values) / max(1, len(values) - 1)
    return min(1.0, math.sqrt(max(0.02, variance) / len(values)) + 0.5 / math.sqrt(len(values)))


def run_cost_sysrs(
    rewards: Any,
    costs: Any,
    config_ids: Sequence[str],
    *,
    cell_budget: int | None = None,
    cost_budget: float | None = None,
    seed: int = 0,
    initial_block: int = 1,
    margin: float = 0.0,
) -> dict[str, Any]:
    """Run synchronized successive rejects on a complete row/question matrix.

    Exactly one of ``cell_budget`` or ``cost_budget`` is required.  The
    question order is fixed before any outcome is observed.  With a cost
    budget, block sizes use only already observed row charge averages; the
    actual ledger remains authoritative and can overshoot the target.
    """

    k, n = _matrix_shape(rewards, "rewards")
    if _matrix_shape(costs, "costs") != (k, n):
        raise ValueError("rewards and costs must have the same shape")
    if len(config_ids) != k or len(set(str(item) for item in config_ids)) != k:
        raise ValueError("config_ids must be unique and match the matrix")
    if (cell_budget is None) == (cost_budget is None):
        raise ValueError("provide exactly one of cell_budget or cost_budget")
    if cell_budget is not None and cell_budget < 1:
        raise ValueError("cell_budget must be positive")
    if cost_budget is not None and (not math.isfinite(cost_budget) or cost_budget <= 0.0):
        raise ValueError("cost_budget must be positive")
    if initial_block < 1:
        raise ValueError("initial_block must be positive")
    if not math.isfinite(margin) or not 0.0 <= margin < 1.0:
        raise ValueError("margin must be in [0, 1)")

    rng = random.Random(seed)
    question_order = rng.sample(range(n), n)
    active = list(range(k))
    seen: set[tuple[int, int]] = set()
    observed: dict[int, list[tuple[int, float, float]]] = {}
    last_complete_observed: dict[int, list[tuple[int, float, float]]] = {}
    total_cost = 0.0
    cursor = 0
    phases = 0
    complete_phases = 0
    incomplete_phase = False
    eliminated: list[int] = []
    phase_records: list[dict[str, Any]] = []

    def reached() -> bool:
        return (cell_budget is not None and len(seen) >= cell_budget) or (
            cost_budget is not None and total_cost >= cost_budget
        )

    def pull(row: int, question: int) -> bool:
        nonlocal total_cost
        cell = (row, question)
        if cell in seen:
            return False
        if cell_budget is not None and len(seen) >= cell_budget:
            return False
        reward = float(rewards[row][question])
        cost = float(costs[row][question])
        if not math.isfinite(reward) or not 0.0 <= reward <= 1.0:
            raise ValueError("pulled rewards must be finite and in [0, 1]")
        if not math.isfinite(cost) or cost < 0.0:
            raise ValueError("pulled costs must be finite and nonnegative")
        seen.add(cell)
        observed.setdefault(row, []).append((question, reward, cost))
        total_cost += cost
        return True

    def row_values(
        row: int,
        source: dict[int, list[tuple[int, float, float]]] | None = None,
    ) -> list[float]:
        values = observed if source is None else source
        return [reward for _, reward, _ in values.get(row, ())]

    def row_cost_estimate(row: int) -> float:
        values = [cost for _, _, cost in observed.get(row, ())]
        if values:
            return sum(values) / len(values)
        all_values = [cost for entries in observed.values() for _, _, cost in entries]
        return sum(all_values) / len(all_values) if all_values else 1.0

    def row_score(row: int) -> tuple[float, float, int]:
        values = row_values(row)
        mean = sum(values) / len(values) if values else 0.0
        radius = _heuristic_radius(values, n)
        # The radius is used only to make the final diagnostic choice
        # deterministic; elimination itself follows the SySRs empirical loser.
        return mean + radius, mean, -row

    def choose_block_size() -> int:
        remaining_questions = n - cursor
        if remaining_questions <= 0:
            return 0
        # The first block is deliberately small.  Later blocks may grow as
        # active rows shrink, as in successive rejects.
        suggested = max(
            initial_block,
            min(remaining_questions, initial_block * (2 ** max(0, phases - 1))),
        )
        if cell_budget is not None:
            remaining_cells = cell_budget - len(seen)
            return max(0, min(suggested, remaining_cells // max(1, len(active))))
        remaining_dollars = max(0.0, float(cost_budget) - total_cost)
        phase_cost = sum(row_cost_estimate(row) for row in active)
        if phase_cost <= 0.0:
            return suggested
        affordable = int(remaining_dollars // phase_cost)
        # One question is allowed in realized-cost mode so the ledger records
        # a possible overshoot rather than pretending the charge was known.
        return max(1, min(suggested, remaining_questions, affordable))

    while len(active) > 1 and cursor < n and not reached():
        phases += 1
        block_size = choose_block_size()
        if block_size <= 0:
            break
        block = question_order[cursor:cursor + block_size]
        phase_record: dict[str, Any] = {
            "phase": phases,
            "active_rows": [str(config_ids[row]) for row in active],
            "question_indices": list(block),
            "planned_cells": len(block) * len(active),
            "completed_cells": 0,
            "realized_cost": 0.0,
            "complete": False,
        }
        phase_complete = True
        for question_index, question in enumerate(block):
            for row_index, row in enumerate(active):
                if not pull(row, question):
                    phase_complete = False
                    break
                phase_record["completed_cells"] += 1
                phase_record["realized_cost"] += float(costs[row][question])
                last_cell_in_block = question_index == len(block) - 1 and row_index == len(active) - 1
                if reached() and cost_budget is not None and not last_cell_in_block:
                    # A realized cost can cross the target in the middle of a
                    # synchronized block. Do not eliminate from an incomplete
                    # block; return its spend and overshoot honestly.
                    phase_complete = False
                    break
            if not phase_complete:
                break
        if not phase_complete:
            phase_records.append(phase_record)
            incomplete_phase = True
            break
        cursor += block_size
        complete_phases += 1
        phase_record["complete"] = True
        last_complete_observed = {
            row: list(observed.get(row, ())) for row in active
        }
        loser = min(active, key=lambda row: (row_score(row)[1], row))
        best = max(active, key=lambda row: (row_score(row)[1], -row))
        if row_score(best)[1] - row_score(loser)[1] < margin and cursor >= n:
            # At a complete question bank, retain the empirical best rather
            # than forcing an arbitrary elimination at a tied margin.
            active = [best]
            phase_record["eliminated_row"] = None
            phase_records.append(phase_record)
            break
        active.remove(loser)
        eliminated.append(loser)
        phase_record["eliminated_row"] = str(config_ids[loser])
        phase_records.append(phase_record)

    if incomplete_phase:
        stop_reason = "incomplete_phase"
    elif len(active) <= 1:
        stop_reason = "one_row_remaining"
    elif cursor >= n:
        stop_reason = "question_bank_exhausted"
    elif reached():
        stop_reason = "budget_exhausted"
    else:
        stop_reason = "no_affordable_complete_block"

    selection_status = "selected_after_complete_phase"
    selection_source = observed
    candidates = active if complete_phases else []
    if not complete_phases:
        selection_status = "no_complete_common_sample"
    if incomplete_phase:
        # Ignore extra cells from the partial block. A previous complete phase
        # gives a common sample; with no such phase there is no evidence from
        # which to recommend a row.
        selection_source = last_complete_observed
        candidates = [row for row in active if row in last_complete_observed]
        if not candidates:
            selection_status = "no_complete_common_sample"
    if candidates:
        def selection_score(row: int) -> tuple[float, float, int]:
            values = row_values(row, selection_source)
            mean = sum(values) / len(values) if values else 0.0
            radius = _heuristic_radius(values, n)
            return mean + radius, mean, -row

        selected: int | None = max(candidates, key=selection_score)
        selected_values = row_values(selected, selection_source)
        if incomplete_phase:
            selection_status = "provisional_common_prefix"
    else:
        selected = None
        selected_values = []
    return {
        "selected_config_id": str(config_ids[selected]) if selected is not None else None,
        "selected_config_index": selected,
        "search_evaluations": len(seen),
        "search_cost": total_cost,
        "selected_observed_accuracy": (
            sum(selected_values) / len(selected_values) if selected_values else None
        ),
        "active_rows": [str(config_ids[row]) for row in active],
        "eliminated_rows": [str(config_ids[row]) for row in eliminated],
        "phases": phases,
        "complete_phases": complete_phases,
        "phase_records": phase_records,
        "incomplete_phase": incomplete_phase,
        "stop_reason": stop_reason,
        "selection_status": selection_status,
        "selection_basis": "cost_synchronized_successive_rejects",
        "budget_basis": "cell_budget" if cell_budget is not None else "realized_cost_budget",
        "confidence_kind": "heuristic_radius",
        "overshoot": max(0.0, total_cost - float(cost_budget)) if cost_budget is not None else 0.0,
    }


__all__ = ["run_cost_sysrs"]
