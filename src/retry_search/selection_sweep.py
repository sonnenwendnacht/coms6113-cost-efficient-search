"""Leak-free selector sweeps for the retry-aware Experiment 1 benchmark.

The search matrix supplied to :func:`run_sweep` has one row per ordered
configuration and one column per search question.  A policy receives a cell
only when it pulls that cell.  In particular, costs are never consulted to
choose the next pull and a policy never sees the held-out evaluation matrix.
This module intentionally uses only the Python standard library.

A result is one ``(algorithm, parameter, seed)`` run, in the reporting shape
used by AgentOpt's selector tables.  Search spending is the realized sum of
costs of paid cells; there is no shared dollar cap hidden inside the policies.
"""

from __future__ import annotations

import math
import random
import time
from collections.abc import Mapping, Sequence
from typing import Any


DEFAULT_SETTINGS: tuple[dict[str, Any], ...] = (
    *(dict(algorithm="random", parameter_name="fraction", parameter_value=x)
      for x in (0.01, 0.025, 0.05, 0.1, 0.2, 0.3, 0.5)),
    *(dict(algorithm="matrix_ucb_e", parameter_name="fraction", parameter_value=x)
      for x in (0.01, 0.025, 0.05, 0.1, 0.2, 0.3, 0.5)),
    *(dict(algorithm="uniform", parameter_name="fraction", parameter_value=x)
      for x in (0.01, 0.025, 0.05, 0.1, 0.2, 0.3, 0.5)),
    *(dict(algorithm="arm_elimination", parameter_name="confidence_multiplier", parameter_value=x)
      for x in (0.25, 0.5, 1.0, 2.0)),
    *(dict(algorithm="hill_climb", parameter_name="restarts", parameter_value=x)
      for x in (1, 2, 4, 8)),
    *(dict(algorithm="bayesian_opt", parameter_name="fraction", parameter_value=x)
      for x in (0.01, 0.025, 0.05, 0.1, 0.2)),
)


def default_settings() -> list[dict[str, Any]]:
    """Return a fresh list of the predeclared algorithm/parameter pairs."""

    return [dict(s) for s in DEFAULT_SETTINGS]


def _matrix_shape(matrix: Any, name: str) -> tuple[int, int]:
    """Validate only shape; individual cell values are read on pull."""

    try:
        k = len(matrix)
    except TypeError as exc:
        raise TypeError(f"{name} must be a two-dimensional sequence") from exc
    if k == 0:
        raise ValueError(f"{name} must contain at least one configuration")
    try:
        n = len(matrix[0])
    except (TypeError, IndexError) as exc:
        raise ValueError(f"{name} must contain rows of questions") from exc
    if n == 0:
        raise ValueError(f"{name} must contain at least one question")
    for i in range(k):
        try:
            row_n = len(matrix[i])
        except TypeError as exc:
            raise TypeError(f"{name}[{i}] is not a row") from exc
        if row_n != n:
            raise ValueError(f"{name} must be rectangular (row {i} has {row_n}, expected {n})")
    return k, n


def _fraction(value: Any) -> float:
    try:
        value = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError("fraction must be numeric") from exc
    if not 0.0 < value <= 1.0:
        raise ValueError("fraction must be in (0, 1]")
    return value


def _safe_mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else float("-inf")


def _best_observed(observed: Mapping[int, list[tuple[float, float]]], config_ids: Sequence[str]) -> int:
    """Choose a row using only its observed cells and deterministic tie breaks."""

    def key(arm: int) -> tuple[float, float, str, int]:
        values = observed[arm]
        mean = _safe_mean([x[0] for x in values])
        mean_cost = sum(x[1] for x in values) / len(values)
        return (-mean, mean_cost, str(config_ids[arm]), arm)

    return min(observed, key=key)


def _pick_cell(
    arm: int,
    question: int,
    rewards: Any,
    costs: Any,
    observed: dict[int, list[tuple[float, float]]],
    seen: set[tuple[int, int]],
) -> float:
    """Pull exactly one cell, recording its reward and realized cost."""

    if (arm, question) in seen:
        raise RuntimeError("selector attempted to pull a duplicate cell")
    # These are deliberately the only accesses to matrix values in this module.
    reward = float(rewards[arm][question])
    cost = float(costs[arm][question])
    if not math.isfinite(reward) or not math.isfinite(cost) or cost < 0.0:
        raise ValueError("pulled cells must have finite reward and nonnegative cost")
    seen.add((arm, question))
    observed.setdefault(arm, []).append((reward, cost))
    return cost


def _pull_row(
    arm: int,
    question_order: Sequence[int],
    rewards: Any,
    costs: Any,
    observed: dict[int, list[tuple[float, float]]],
    seen: set[tuple[int, int]],
) -> float:
    total = 0.0
    for question in question_order:
        total += _pick_cell(arm, question, rewards, costs, observed, seen)
    return total


def _row_count(fraction: Any, k: int) -> int:
    return max(1, min(k, int(math.ceil(_fraction(fraction) * k))))


def _cell_count(fraction: Any, k: int, n: int) -> int:
    return max(1, min(k * n, int(math.ceil(_fraction(fraction) * k * n))))


def _random_rows(
    fraction: Any, k: int, n: int, rng: random.Random, rewards: Any, costs: Any,
    observed: dict[int, list[tuple[float, float]]], seen: set[tuple[int, int]],
) -> str:
    arms = list(range(k))
    rng.shuffle(arms)
    question_order = list(range(n))
    rng.shuffle(question_order)
    for arm in arms[:_row_count(fraction, k)]:
        _pull_row(arm, question_order, rewards, costs, observed, seen)
    return "fraction_rows_evaluated"


def _uniform_cells(
    fraction: Any, k: int, n: int, q_order: Sequence[int], rewards: Any, costs: Any,
    observed: dict[int, list[tuple[float, float]]], seen: set[tuple[int, int]],
) -> str:
    budget = _cell_count(fraction, k, n)
    for offset in range(budget):
        arm = offset % k
        round_no = offset // k
        if round_no >= n:
            break
        _pick_cell(arm, q_order[round_no], rewards, costs, observed, seen)
    return "cell_fraction_reached"


def _matrix_ucb_e(
    fraction: Any, k: int, n: int, q_order: Sequence[int], rewards: Any, costs: Any,
    observed: dict[int, list[tuple[float, float]]], seen: set[tuple[int, int]],
) -> str:
    budget = _cell_count(fraction, k, n)
    next_q = [0] * k
    pulls = [0] * k
    means = [0.0] * k
    initial = min(k, budget)
    for arm in range(initial):
        _pick_cell(arm, q_order[next_q[arm]], rewards, costs, observed, seen)
        next_q[arm] += 1
        pulls[arm] = 1
        means[arm] = float(observed[arm][-1][0])
    used = initial
    while used < budget:
        candidates = [a for a in range(k) if next_q[a] < n]
        if not candidates:
            break
        t = max(2, used + 1)

        def score(arm: int) -> tuple[float, int]:
            if pulls[arm] == 0:
                return (float("inf"), -arm)
            return (means[arm] + math.sqrt(max(0.0, 2.0 * math.log(t) / pulls[arm])), -arm)

        arm = max(candidates, key=score)
        q = q_order[next_q[arm]]
        next_q[arm] += 1
        _pick_cell(arm, q, rewards, costs, observed, seen)
        pulls[arm] += 1
        means[arm] += (float(observed[arm][-1][0]) - means[arm]) / pulls[arm]
        used += 1
    return "cell_fraction_reached"


def _arm_elimination(
    multiplier: Any, k: int, n: int, q_order: Sequence[int], rewards: Any, costs: Any,
    observed: dict[int, list[tuple[float, float]]], seen: set[tuple[int, int]],
) -> str:
    try:
        multiplier = float(multiplier)
    except (TypeError, ValueError) as exc:
        raise ValueError("confidence_multiplier must be numeric") from exc
    if multiplier <= 0:
        raise ValueError("confidence_multiplier must be positive")
    active = list(range(k))
    next_q = [0] * k
    rounds = 0
    while len(active) > 1 and rounds < n:
        rounds += 1
        for arm in list(active):
            _pick_cell(arm, q_order[next_q[arm]], rewards, costs, observed, seen)
            next_q[arm] += 1
        t = max(2, sum(len(observed[a]) for a in active))
        means = {a: _safe_mean([x[0] for x in observed[a]]) for a in active}
        radius = {
            a: multiplier * math.sqrt(math.log(max(2.0, 2.0 * k * t)) / len(observed[a]))
            for a in active
        }
        best_lower = max(means[a] - radius[a] for a in active)
        survivors = [a for a in active if means[a] + radius[a] >= best_lower]
        active = survivors or [max(active, key=lambda a: (means[a], -a))]
    return "one_arm_remains" if len(active) == 1 else "all_questions_reached"


def _hamming_neighbors(arm: int, k: int) -> list[int]:
    """Neighbors for ordered triples of model indices when K is a cube."""

    side = round(k ** (1.0 / 3.0))
    if side ** 3 != k or side < 2:
        return [j for j in range(k) if j != arm]
    digits = [(arm // (side * side)) % side, (arm // side) % side, arm % side]
    out: list[int] = []
    for position in range(3):
        for value in range(side):
            if value == digits[position]:
                continue
            new = list(digits)
            new[position] = value
            out.append(new[0] * side * side + new[1] * side + new[2])
    return out


def _hill_climb(
    restarts: Any, k: int, n: int, rng: random.Random, rewards: Any, costs: Any,
    observed: dict[int, list[tuple[float, float]]], seen: set[tuple[int, int]],
) -> str:
    try:
        restarts = int(restarts)
    except (TypeError, ValueError) as exc:
        raise ValueError("restarts must be an integer") from exc
    if restarts < 1:
        raise ValueError("restarts must be positive")
    q_order = list(range(n))
    starts = list(range(k))
    rng.shuffle(starts)
    for start in starts[: min(restarts, k)]:
        current = start
        if current not in observed:
            _pull_row(current, q_order, rewards, costs, observed, seen)
        current_mean = _safe_mean([x[0] for x in observed[current]])
        while True:
            candidates = [a for a in _hamming_neighbors(current, k) if a not in observed]
            for candidate in candidates:
                _pull_row(candidate, q_order, rewards, costs, observed, seen)
            if not candidates:
                break
            candidate = max(candidates, key=lambda a: (_safe_mean([x[0] for x in observed[a]]), -a))
            candidate_mean = _safe_mean([x[0] for x in observed[candidate]])
            if candidate_mean <= current_mean:
                break
            current, current_mean = candidate, candidate_mean
    return "restarts_completed"


def _solve_linear(matrix: list[list[float]], vector: list[float]) -> list[float]:
    """Tiny pivoted Gaussian solve, used by the categorical GP baseline."""

    n = len(vector)
    if not n:
        return []
    a = [row[:] + [float(v)] for row, v in zip(matrix, vector)]
    for col in range(n):
        pivot = max(range(col, n), key=lambda r: abs(a[r][col]))
        if abs(a[pivot][col]) < 1e-10:
            a[pivot][col] = 1e-10
        a[col], a[pivot] = a[pivot], a[col]
        scale = a[col][col]
        a[col] = [x / scale for x in a[col]]
        for row in range(n):
            if row == col:
                continue
            factor = a[row][col]
            if factor:
                a[row] = [x - factor * y for x, y in zip(a[row], a[col])]
    return [a[i][-1] for i in range(n)]


def _hamming_distance(a: int, b: int, k: int) -> int:
    side = round(k ** (1.0 / 3.0))
    if side ** 3 != k:
        return 0 if a == b else 1
    da = ((a // (side * side)) % side, (a // side) % side, a % side)
    db = ((b // (side * side)) % side, (b // side) % side, b % side)
    return sum(x != y for x, y in zip(da, db))


def _bayesian_opt(
    fraction: Any, k: int, n: int, rng: random.Random, rewards: Any, costs: Any,
    observed: dict[int, list[tuple[float, float]]], seen: set[tuple[int, int]],
) -> str:
    target = _row_count(fraction, k)
    q_order = list(range(n))
    rng.shuffle(q_order)
    candidates = list(range(k))
    rng.shuffle(candidates)
    while len(observed) < target:
        if not observed:
            arm = candidates.pop()
        else:
            observed_arms = sorted(observed)
            y = [_safe_mean([x[0] for x in observed[a]]) for a in observed_arms]
            noise = 0.12
            kernel = [
                [math.exp(-_hamming_distance(a, b, k)) + (noise if i == j else 0.0)
                 for j, b in enumerate(observed_arms)]
                for i, a in enumerate(observed_arms)
            ]
            alpha = _solve_linear(kernel, y)
            best = None
            best_score = float("-inf")
            for arm in candidates:
                cov = [math.exp(-_hamming_distance(arm, b, k)) for b in observed_arms]
                mean = sum(c * a for c, a in zip(cov, alpha))
                solve_cov = _solve_linear(kernel, cov)
                variance = max(0.01, 1.0 - sum(c * z for c, z in zip(cov, solve_cov)))
                score = mean + 1.5 * math.sqrt(variance)
                if score > best_score or (score == best_score and arm < (best if best is not None else arm)):
                    best, best_score = arm, score
            if best is None:
                break
            arm = best
            candidates.remove(arm)
        _pull_row(arm, q_order, rewards, costs, observed, seen)
    return "fraction_rows_evaluated"


def _setting_copy(setting: Mapping[str, Any]) -> dict[str, Any]:
    return {str(k): v for k, v in setting.items()}


def run_sweep(
    rewards: Any,
    costs: Any,
    config_ids: Sequence[str],
    settings: Sequence[Mapping[str, Any]] | None = None,
    seeds: Sequence[int] = (0,),
) -> list[dict[str, Any]]:
    """Run every algorithm/parameter pair for every seed.

    ``rewards`` and ``costs`` are K x N search matrices.  Values are read only
    when a policy pulls their cell.  A held-out matrix is intentionally not an
    argument: callers must evaluate the selected row separately after a sweep.
    """

    k, n = _matrix_shape(rewards, "rewards")
    if _matrix_shape(costs, "costs") != (k, n):
        raise ValueError("rewards and costs must have the same shape")
    if len(config_ids) != k:
        raise ValueError("config_ids must have one ID per configuration")
    if len(set(str(x) for x in config_ids)) != k:
        raise ValueError("config_ids must be unique")
    settings = default_settings() if settings is None else list(settings)
    if not settings:
        raise ValueError("settings must not be empty")
    outputs: list[dict[str, Any]] = []
    for seed_value in seeds:
        seed = int(seed_value)
        for raw_setting in settings:
            setting = _setting_copy(raw_setting)
            algorithm = str(setting.get("algorithm", ""))
            if not algorithm:
                raise ValueError("each setting needs an algorithm")
            parameter_name = str(setting.get("parameter_name", "parameter"))
            parameter_value = setting.get("parameter_value", setting.get(parameter_name))
            if parameter_value is None:
                raise ValueError(f"setting for {algorithm} needs parameter_value")
            rng = random.Random(seed)
            q_order = list(range(n))
            rng.shuffle(q_order)
            observed: dict[int, list[tuple[float, float]]] = {}
            seen: set[tuple[int, int]] = set()
            started = time.perf_counter()
            if algorithm == "random":
                stop_reason = _random_rows(parameter_value, k, n, rng, rewards, costs, observed, seen)
            elif algorithm == "uniform":
                stop_reason = _uniform_cells(parameter_value, k, n, q_order, rewards, costs, observed, seen)
            elif algorithm in {"matrix_ucb_e", "matrix_ucb"}:
                stop_reason = _matrix_ucb_e(parameter_value, k, n, q_order, rewards, costs, observed, seen)
            elif algorithm in {"arm_elimination", "successive_elimination"}:
                stop_reason = _arm_elimination(parameter_value, k, n, q_order, rewards, costs, observed, seen)
            elif algorithm in {"hill_climb", "hill_climbing"}:
                stop_reason = _hill_climb(parameter_value, k, n, rng, rewards, costs, observed, seen)
            elif algorithm in {"bayesian_opt", "bayesian_optimization", "kernel_bayes_ucb"}:
                stop_reason = _bayesian_opt(parameter_value, k, n, rng, rewards, costs, observed, seen)
            else:
                raise ValueError(f"unknown selector algorithm: {algorithm}")
            selected = _best_observed(observed, config_ids)
            values = observed[selected]
            outputs.append({
                "algorithm": algorithm,
                "parameter_name": parameter_name,
                "parameter_value": parameter_value,
                "seed": seed,
                "selected_config_id": str(config_ids[selected]),
                "selected_config_index": selected,
                "search_evaluations": len(seen),
                "search_cost": sum(cost for entries in observed.values() for _, cost in entries),
                "selected_observed_accuracy": _safe_mean([reward for reward, _ in values]),
                "selection_time_seconds": time.perf_counter() - started,
                "stop_reason": stop_reason,
                "settings": setting,
            })
    return outputs


__all__ = ["DEFAULT_SETTINGS", "default_settings", "run_sweep"]
