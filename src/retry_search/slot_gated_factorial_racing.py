"""Empirical Slot-Gated Factorial Racing (SGFR) research prototype.

A pull is one *complete workflow* on one question.  No execution prefix or
model output is shared.  Separate quality, retry-reach, and charge diagnostics
from paid one-slot pairs alter the allocation, never impute a reward.  Quiet
slots remain accessible through a direct exploration reserve.  The final
recommendation uses a fresh, reserved question block.

The fold bounds below are heuristic uncertainty scores, not certified
confidence intervals. This minimal version has no additive outcome model and
makes no cross-context interaction or fixed-confidence guarantee. The current
implementation is a bookkeeping-corrected exploratory racer; it is not the
cross-fitted residual-transfer design in deep-review note 147 and must not be
used as confirmatory evidence for a similarity saving.
"""
from __future__ import annotations

import math
import random
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

from .selection_sweep import _arm_digits, _matrix_shape


def _mean(values: Sequence[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def _radius(values: Sequence[float], scale: float) -> float:
    if not values:
        return 1.0
    mean = _mean(values)
    variance = sum((value - mean) ** 2 for value in values) / max(1, len(values) - 1)
    return min(1.0, scale * (math.sqrt(variance / len(values)) + 1.0 / len(values)))


def _gate(values: Sequence[float], tolerance: float, scale: float) -> dict[str, Any]:
    """Both alternating calibration folds must be small to mark a slot quiet."""
    folds = (values[::2], values[1::2])
    if min(map(len, folds)) < 2:
        return {"state": "unresolved", "mean": _mean(values), "lower": 0.0, "upper": 1.0,
                "samples": len(values)}
    lower = min(max(0.0, _mean(fold) - _radius(fold, scale)) for fold in folds)
    upper = max(min(1.0, _mean(fold) + _radius(fold, scale)) for fold in folds)
    state = "quiet" if upper <= tolerance else "active" if lower > tolerance else "unresolved"
    return {"state": state, "mean": _mean(values), "lower": lower, "upper": upper,
            "samples": len(values)}


@dataclass(frozen=True)
class _Cell:
    quality: float
    charge: float
    attempts: int | None


def run_sgfr(
    rewards: Any,
    costs: Any,
    config_ids: Sequence[str],
    *,
    attempts: Any | None = None,
    row_slots: Sequence[Sequence[int]] | None = None,
    budget_fraction: float | None = None,
    cell_budget: int | None = None,
    cost_budget: float | None = None,
    seed: int = 0,
    calibration_block: int = 8,
    calibration_fraction: float = 0.25,
    confirmation_fraction: float = 0.20,
    reserve_fraction: float = 0.15,
    quality_tolerance: float = 0.02,
    reach_tolerance: float = 0.05,
    charge_tolerance: float = 0.05,
    uncertainty_scale: float = 0.25,
) -> dict[str, Any]:
    """Race complete configurations under a cell or realized-charge budget.

    All inputs are SEARCH matrices.  Only shapes are inspected before pulls.
    ``attempts[row][question]`` is the number of attempts reached in the paid
    workflow, between one and the number of slots.  Missing attempts disable
    the reach gate, leaving it unresolved rather than declaring low reach.

    Supply exactly one budget.  A fraction means ceil(fraction*K*N) cells.
    Costs are not known in advance: in dollar mode the last *single* complete
    workflow can overshoot the cap.  This overshoot is explicitly reported.
    Gates only affect acquisition; they do not permanently eliminate a slot.
    Finalists are compared on reserved questions never used for calibration or
    racing.  A missing complete confirmation round yields no recommendation.
    At a full cell budget, exhaustive direct evaluation takes precedence.
    """
    k, n = _matrix_shape(rewards, "rewards")
    if _matrix_shape(costs, "costs") != (k, n):
        raise ValueError("rewards and costs must have the same shape")
    if attempts is not None and _matrix_shape(attempts, "attempts") != (k, n):
        raise ValueError("attempts must match rewards")
    if len(config_ids) != k or len(set(map(str, config_ids))) != k:
        raise ValueError("config_ids must be unique and match rows")
    if row_slots is None:
        slots = [_arm_digits(row, k) for row in range(k)]
        if any(value is None for value in slots):
            raise ValueError("non-cube row counts require explicit row_slots")
    else:
        slots = [tuple(value) for value in row_slots]
    if len(slots) != k or not slots[0] or len(set(slots)) != k:
        raise ValueError("row_slots must contain one unique nonempty tuple per row")
    dimensions = len(slots[0])
    if any(len(value) != dimensions for value in slots):
        raise ValueError("row_slots must have equal lengths")
    if sum(value is not None for value in (budget_fraction, cell_budget, cost_budget)) != 1:
        raise ValueError("provide exactly one budget")
    if budget_fraction is not None:
        if not math.isfinite(budget_fraction) or not 0 < budget_fraction <= 1:
            raise ValueError("budget_fraction must be in (0, 1]")
        cell_budget = max(1, math.ceil(k * n * budget_fraction))
    if cell_budget is not None:
        if isinstance(cell_budget, bool) or not isinstance(cell_budget, int) or cell_budget < 1:
            raise ValueError("cell_budget must be a positive integer")
        cell_budget = min(cell_budget, k * n)
        if cell_budget < n:
            raise ValueError("cell_budget must fit one complete row")
    if cost_budget is not None and (not math.isfinite(cost_budget) or cost_budget <= 0):
        raise ValueError("cost_budget must be finite and positive")
    if isinstance(calibration_block, bool) or not isinstance(calibration_block, int) or calibration_block < 1:
        raise ValueError("calibration_block must be a positive integer")
    for name, value in (("calibration_fraction", calibration_fraction),
                        ("confirmation_fraction", confirmation_fraction),
                        ("reserve_fraction", reserve_fraction)):
        if not math.isfinite(value) or not 0 < value < 1:
            raise ValueError(f"{name} must be in (0, 1)")
    if calibration_fraction + confirmation_fraction >= 1:
        raise ValueError("calibration and confirmation fractions must leave racing budget")
    for value in (quality_tolerance, reach_tolerance, charge_tolerance):
        if not math.isfinite(value) or not 0 <= value < 1:
            raise ValueError("gate tolerances must be in [0, 1)")
    if not math.isfinite(uncertainty_scale) or uncertainty_scale <= 0:
        raise ValueError("uncertainty_scale must be finite and positive")

    rng = random.Random(seed)
    questions = rng.sample(range(n), n)
    confirm_n = min(n, max(1, math.ceil(n * confirmation_fraction)))
    confirm_questions = questions[-confirm_n:]
    search_questions = questions[:-confirm_n]
    cells: dict[tuple[int, int], _Cell] = {}
    quality_by_row: dict[int, list[float]] = {}
    complete_rows: set[int] = set()
    charge_by_row: dict[int, list[float]] = {}
    charge_total = 0.0
    calibration_cells = 0
    direct_reserve_cells = 0
    confirmation_cells = 0
    paired_questions = 0
    pair_records: list[dict[str, Any]] = []
    racing_pair_count = 0
    gate_values = [{"quality": [], "reach": [], "charge": []} for _ in range(dimensions)]

    def spent() -> float:
        return float(len(cells)) if cell_budget is not None else charge_total

    budget = float(cell_budget if cell_budget is not None else cost_budget)
    explore_limit = math.floor(budget * (1 - confirmation_fraction)) if cell_budget is not None else budget * (1 - confirmation_fraction)
    calibration_limit = math.floor(budget * calibration_fraction) if cell_budget is not None else budget * calibration_fraction

    def pull(row: int, question: int, limit: float) -> bool:
        nonlocal charge_total
        key = row, question
        if key in cells:
            return True
        if spent() >= limit:
            return False
        quality = float(rewards[row][question])
        charge = float(costs[row][question])
        if not math.isfinite(quality) or not 0 <= quality <= 1:
            raise ValueError("paid quality must be in [0, 1]")
        if not math.isfinite(charge) or charge < 0:
            raise ValueError("paid charge must be finite and nonnegative")
        reached = attempts[row][question] if attempts is not None else None
        if reached is not None and (
            isinstance(reached, bool) or int(reached) != reached or not 1 <= reached <= dimensions
        ):
            raise ValueError("paid attempts must be an integer from 1 to number of slots")
        cells[key] = _Cell(quality, charge, int(reached) if reached is not None else None)
        quality_by_row.setdefault(row, []).append(quality)
        charge_by_row.setdefault(row, []).append(charge)
        charge_total += charge
        return True

    def direct_key(row: int) -> tuple[float, float, str, int]:
        return (-_mean(quality_by_row[row]), _mean(charge_by_row[row]), str(config_ids[row]), row)

    def result(selected: int | None, stop: str, diagnostics: list[dict[str, Any]]) -> dict[str, Any]:
        return {
            "selected_config_id": str(config_ids[selected]) if selected is not None else None,
            "selected_config_index": selected,
            "selected_observed_accuracy": _mean(quality_by_row[selected]) if selected is not None else None,
            "search_evaluations": len(cells), "search_cost": charge_total,
            "selection_basis": "slot_gated_factorial_racing", "stop_reason": stop,
            "budget_basis": "cell_fraction" if budget_fraction is not None else "cells" if cell_budget is not None else "realized_cost",
            "cost_budget_overshoot": max(0.0, charge_total - cost_budget) if cost_budget is not None else 0.0,
            "calibration_evaluations": calibration_cells,
            "direct_reserve_evaluations": direct_reserve_cells,
            "confirmation_evaluations": confirmation_cells,
            "paired_questions": paired_questions, "slot_gates": diagnostics,
            "complete_rows": len(complete_rows),
            "reach_gate_enabled": attempts is not None,
            # ``calibration_pair_count`` is retained for compatibility with
            # the exploratory artifact; the explicit race count makes it
            # possible to verify that post-calibration acquisition occurred.
            "calibration_pair_count": len(pair_records),
            "racing_pair_count": racing_pair_count,
        }

    if cell_budget == k * n:
        for question in questions:
            for row in range(k):
                pull(row, question, budget)
        complete_rows.update(range(k))
        return result(min(quality_by_row, key=direct_key), "full_matrix_direct_reference", [])

    # Predeclare calibration edge order. Neither construction reads an
    # outcome or a charge. Rows are always completed before a pair is gated.
    edges_by_slot: list[list[tuple[int, int]]] = [[] for _ in range(dimensions)]
    for left in range(k):
        for right in range(left + 1, k):
            differences = [slot for slot in range(dimensions)
                           if slots[left][slot] != slots[right][slot]]
            if len(differences) == 1:
                edges_by_slot[differences[0]].append((left, right))
    for edges in edges_by_slot:
        rng.shuffle(edges)
    # Keep the first calibration rounds round-robin across slots.  A global
    # shuffle can spend the entire small calibration block on one coordinate,
    # leaving the other gates permanently unresolved.  Randomise the slot
    # order once, then take one edge from each available slot per round.
    slot_order = list(range(dimensions))
    rng.shuffle(slot_order)
    calibration_pairs = []
    for index in range(max(map(len, edges_by_slot), default=0)):
        for slot in slot_order:
            if index < len(edges_by_slot[slot]):
                calibration_pairs.append((slot, edges_by_slot[slot][index]))

    def row_complete(row: int, qset: Sequence[int], limit: float) -> bool:
        missing = [q for q in qset if (row, q) not in cells]
        # Cell-budget mode never starts a row that cannot be completed. Cost
        # mode deliberately allows the final row to overshoot the cap because
        # future response-dependent charges are not known before pulling it.
        if cell_budget is not None and len(cells) + len(missing) > int(limit):
            return False
        if cost_budget is not None and charge_total >= float(limit):
            return False
        for q in missing:
            if not pull(row, q, int(limit) if cell_budget is not None else float("inf")):
                return False
        # A row is considered observed only after every requested question has
        # been paid. Partial rows are never used as a calibration or finalist.
        if all((row, q) in cells for q in qset):
            complete_rows.add(row)
            return True
        return False

    def pair_values(left: int, right: int) -> tuple[list[float], list[float], list[float]]:
        quality = []
        reach = []
        charge = []
        for q in search_questions:
            a, b = cells[(left, q)], cells[(right, q)]
            quality.append(abs(b.quality - a.quality))
            if a.attempts is not None and b.attempts is not None:
                reach.append(abs(float(b.attempts > 1) - float(a.attempts > 1)))
            scale = max(1e-12, abs(a.charge) + abs(b.charge))
            charge.append(abs(b.charge - a.charge) / scale)
        return quality, reach, charge

    def gates_for(slot: int) -> dict[str, Any]:
        values = gate_values[slot]
        quality_gate = _gate(values["quality"], float(quality_tolerance), float(uncertainty_scale))
        charge_gate = _gate(values["charge"], float(charge_tolerance), float(uncertainty_scale))
        if attempts is None:
            reach_gate = {"state": "disabled", "mean": None, "lower": None,
                          "upper": None, "samples": 0}
            all_gates = quality_gate["state"] == "quiet" and charge_gate["state"] == "quiet"
        else:
            reach_gate = _gate(values["reach"], float(reach_tolerance), float(uncertainty_scale))
            all_gates = all(value["state"] == "quiet"
                            for value in (quality_gate, reach_gate, charge_gate))
        return {"slot": slot, "quality": quality_gate, "reach": reach_gate,
                "charge": charge_gate, "all_gates": bool(all_gates)}

    # Calibration spends only complete rows. A pair contributes absolute
    # same-question differences to exactly one changed slot.
    for slot, (left, right) in calibration_pairs:
        if len(pair_records) >= calibration_block:
            break
        before = len(cells)
        if not row_complete(left, search_questions, calibration_limit):
            continue
        if not row_complete(right, search_questions, calibration_limit):
            continue
        quality, reach_values, charge = pair_values(left, right)
        gate_values[slot]["quality"].extend(quality)
        gate_values[slot]["reach"].extend(reach_values)
        gate_values[slot]["charge"].extend(charge)
        paired_questions += len(quality)
        calibration_cells += len(cells) - before
        pair_records.append({"slot": slot, "rows": [left, right],
                             "gates": gates_for(slot), "questions": len(quality)})
        if (cell_budget is not None and len(cells) >= calibration_limit) or (
            cost_budget is not None and charge_total >= float(calibration_limit)
        ):
            break

    # Reserve a random direct sample of rows so a bad anchor or a quiet gate
    # cannot trap the search in one corner of the factorial grid.
    # The reserve is a second, cumulative slice after calibration.  Using only
    # budget*reserve_fraction here makes the reserve target smaller than the
    # already-spent calibration target in the common case.
    reserve_target = (int(budget * (calibration_fraction + reserve_fraction))
                      if cell_budget is not None
                      else float(budget) * (calibration_fraction + reserve_fraction))
    reserve_rows = list(range(k))
    rng.shuffle(reserve_rows)
    for row in reserve_rows:
        if row in complete_rows:
            # Calibration rows are already complete, and count as direct rows.
            continue
        before = len(cells)
        if not row_complete(row, search_questions, reserve_target):
            break
        direct_reserve_cells += len(cells) - before
        if (cell_budget is not None and len(cells) >= reserve_target) or (
            cost_budget is not None and charge_total >= reserve_target
        ):
            break

    # Race a random sequence of one-slot edges.  Once all three gates for a
    # slot are quiet, use the signed paired residual as a local estimate. A
    # failed or unresolved gate always uses the candidate's direct mean.
    observed_pairs = {(tuple(record["rows"])[0], tuple(record["rows"])[1])
                      for record in pair_records}
    candidates = [(slot, edge) for slot, edges in enumerate(edges_by_slot)
                  for edge in edges if edge not in observed_pairs]
    rng.shuffle(candidates)
    incumbent: int | None = None
    rows_with_data = sorted(complete_rows, key=direct_key)
    if rows_with_data:
        incumbent = rows_with_data[0]
    for slot, (left, right) in candidates:
        if left in complete_rows and right in complete_rows:
            continue
        # Stay inside the post-calibration exploration budget. Each row is a
        # whole block; a cell budget that cannot fit it leaves this race open.
        exploration_limit = explore_limit
        before = len(cells)
        if not row_complete(left, search_questions, exploration_limit):
            continue
        if not row_complete(right, search_questions, exploration_limit):
            continue
        if len(cells) == before:
            continue
        quality, reach_values, charge = pair_values(left, right)
        gate_values[slot]["quality"].extend(quality)
        gate_values[slot]["reach"].extend(reach_values)
        gate_values[slot]["charge"].extend(charge)
        paired_questions += len(quality)
        pair_records.append({"slot": slot, "rows": [left, right],
                             "gates": gates_for(slot), "questions": len(quality)})
        racing_pair_count += 1
        if incumbent is None:
            incumbent = left
        gates = gates_for(slot)
        for candidate in (left, right):
            if incumbent == candidate:
                continue
            candidate_mean = _mean(quality_by_row[candidate])
            if gates["all_gates"]:
                anchor_mean = _mean(quality_by_row[incumbent])
                # Preserve the sign: pair_values stores absolute values for
                # gates, but the recommendation uses direct observed values.
                residual = _mean([cells[(candidate, q)].quality - cells[(incumbent, q)].quality
                                 for q in search_questions])
                estimate = anchor_mean + residual
            else:
                estimate = candidate_mean
            incumbent_mean = _mean(quality_by_row[incumbent])
            incumbent_charge = _mean(charge_by_row[incumbent])
            candidate_charge = _mean(charge_by_row[candidate])
            score = estimate - 0.01 * math.log(max(candidate_charge, 1e-12) /
                                               max(incumbent_charge, 1e-12))
            if score > incumbent_mean:
                incumbent = candidate
        if (cell_budget is not None and len(cells) >= explore_limit) or (
            cost_budget is not None and charge_total >= explore_limit
        ):
            break

    # Fresh confirmation compares the two best directly observed rows only on
    # questions excluded from all calibration/racing blocks. If it cannot pay a
    # complete confirmation block, the result is explicitly no-recommendation.
    if len(complete_rows) < 2:
        diagnostics = [gates_for(slot) for slot in range(dimensions)]
        return result(None, "insufficient_complete_rows", diagnostics)
    finalists = sorted(complete_rows, key=direct_key)[:2]
    confirmation_limit = budget
    confirmation_ready = True
    for row in finalists:
        before = len(cells)
        if not row_complete(row, confirm_questions, confirmation_limit):
            confirmation_ready = False
            break
        confirmation_cells += len(cells) - before
    if not confirmation_ready:
        diagnostics = [gates_for(slot) for slot in range(dimensions)]
        return result(None, "confirmation_budget_unavailable", diagnostics)
    final_means = {row: _mean([cells[(row, q)].quality for q in confirm_questions]) for row in finalists}
    selected = max(finalists, key=lambda row: (final_means[row], -_mean(charge_by_row[row]), -row))
    diagnostics = [gates_for(slot) for slot in range(dimensions)]
    output = result(selected, "confirmation_complete", diagnostics)
    output["confirmation_config_ids"] = [str(config_ids[row]) for row in finalists]
    output["confirmation_accuracy"] = {str(config_ids[row]): final_means[row] for row in finalists}
    output["calibration_pairs"] = pair_records
    output["calibration_pair_count"] = len(pair_records)
    return output


__all__ = ["run_sgfr"]
