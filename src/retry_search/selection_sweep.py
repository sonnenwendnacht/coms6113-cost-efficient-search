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
    *(dict(algorithm="similarity_annealed_ucb", parameter_name="fraction", parameter_value=x)
      for x in (0.01, 0.025, 0.05, 0.1, 0.2, 0.3, 0.5)),
    *(dict(algorithm="graph_residual_racing", parameter_name="fraction", parameter_value=x)
      for x in (0.01, 0.025, 0.05, 0.1, 0.2, 0.3, 0.5)),
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


def _arm_digits(arm: int, k: int) -> tuple[int, int, int] | None:
    """Decode a cube-indexed row into its three model-choice slots."""

    side = round(k ** (1.0 / 3.0))
    if side ** 3 != k or side < 2:
        return None
    return ((arm // (side * side)) % side, (arm // side) % side, arm % side)


def _changed_slot(a: int, b: int, k: int) -> int | None:
    first, second = _arm_digits(a, k), _arm_digits(b, k)
    if first is None or second is None:
        return None
    changed = [i for i, (x, y) in enumerate(zip(first, second)) if x != y]
    return changed[0] if len(changed) == 1 else None


def _similarity_weights(
    samples_by_question: Mapping[int, Mapping[int, tuple[float, float]]], k: int
) -> tuple[float, float, float]:
    """Increase distance for slots whose one-step changes disagree empirically."""

    disagreement = [0.0, 0.0, 0.0]
    counts = [0, 0, 0]
    for samples in samples_by_question.values():
        for arm, (reward, _) in samples.items():
            for neighbor in _hamming_neighbors(arm, k):
                if neighbor <= arm or neighbor not in samples:
                    continue
                slot = _changed_slot(arm, neighbor, k)
                if slot is None:
                    continue
                disagreement[slot] += abs(reward - samples[neighbor][0])
                counts[slot] += 1
    return tuple(
        min(3.0, max(0.5, 0.5 + 2.0 * (disagreement[i] / counts[i]))) if counts[i] else 1.0
        for i in range(3)
    )


def _weighted_prediction(
    arm: int,
    question: int,
    samples_by_question: Mapping[int, Mapping[int, tuple[float, float]]],
    k: int,
    bandwidth: float,
    slot_weights: Sequence[float],
    global_mean: float,
) -> tuple[float, float, float]:
    """Return a same-question kernel mean, uncertainty, and effective sample size."""

    samples = samples_by_question.get(question, {})
    if not samples:
        return global_mean, 1.0, 0.0
    target = _arm_digits(arm, k)
    weighted: list[tuple[float, float]] = []
    for other, (reward, _) in samples.items():
        other_digits = _arm_digits(other, k)
        if target is None or other_digits is None:
            distance = 0.0 if other == arm else 1.0
        else:
            distance = sum(
                weight for left, right, weight in zip(target, other_digits, slot_weights)
                if left != right
            )
        weight = math.exp(-distance / max(1e-6, bandwidth))
        weighted.append((weight, reward))
    total_weight = sum(weight for weight, _ in weighted)
    if total_weight <= 0.0:
        return global_mean, 1.0, 0.0
    mean = sum(weight * reward for weight, reward in weighted) / total_weight
    effective_n = total_weight * total_weight / sum(weight * weight for weight, _ in weighted)
    disagreement = sum(weight * abs(reward - mean) for weight, reward in weighted) / total_weight
    uncertainty = min(1.0, math.sqrt(0.25 / (effective_n + 1.0)) + 0.5 * disagreement)
    return mean, uncertainty, effective_n


def _similarity_annealed_ucb(
    fraction: Any, k: int, n: int, rng: random.Random, rewards: Any, costs: Any,
    observed: dict[int, list[tuple[float, float]]], seen: set[tuple[int, int]],
) -> tuple[str, int]:
    """Use an adaptive Hamming graph as side information for cost-aware UCB.

    This is a configuration-level method: rows are similar when their ordered
    model-choice tuples differ in few slots.  It shares only observed
    same-question rewards through the graph.  It does not reuse prefixes,
    suffixes, checkpoints, or model outputs from another workflow.
    """

    bandwidth = 1.0
    target = _cell_count(fraction, k, n)
    q_order = list(range(n))
    rng.shuffle(q_order)
    samples_by_question: dict[int, dict[int, tuple[float, float]]] = {}
    slot_weights = (1.0, 1.0, 1.0)
    global_mean = 0.5
    global_cost = 1.0

    def refresh_statistics() -> None:
        nonlocal slot_weights, global_mean, global_cost
        rewards_seen = [reward for entries in observed.values() for reward, _ in entries]
        costs_seen = [cost for entries in observed.values() for _, cost in entries]
        if rewards_seen:
            global_mean = sum(rewards_seen) / len(rewards_seen)
        if costs_seen:
            global_cost = max(1e-12, sum(costs_seen) / len(costs_seen))
        slot_weights = _similarity_weights(samples_by_question, k)

    def candidate_arms(question: int) -> list[int]:
        samples = samples_by_question.get(question, {})
        candidates = set(samples)
        for arm in samples:
            candidates.update(_hamming_neighbors(arm, k))
        # Keep a small global exploration reserve so disconnected graph
        # regions are eventually visited even when the current elite is wrong.
        reserve = list(range(k))
        rng.shuffle(reserve)
        for arm in reserve[: min(k, max(8, int(math.sqrt(k))))]:
            candidates.add(arm)
        return [arm for arm in candidates if (arm, question) not in seen]

    for step in range(target):
        if step == 0 or step % max(4, min(32, n)) == 0:
            refresh_statistics()
        question = q_order[step % n]
        candidates = candidate_arms(question)
        if not candidates:
            # A graph frontier can be exhausted for one question; advance to
            # any question with an unseen cell before declaring completion.
            for fallback in q_order:
                candidates = candidate_arms(fallback)
                if candidates:
                    question = fallback
                    break
        if not candidates:
            break
        scored: list[tuple[int, float]] = []
        for arm in candidates:
            mean, uncertainty, _ = _weighted_prediction(
                arm, question, samples_by_question, k, bandwidth, slot_weights, global_mean
            )
            cost_est = (
                sum(cost for _, cost in observed[arm]) / len(observed[arm])
                if arm in observed else global_cost
            )
            beta = 0.7 + 0.2 * math.sqrt(math.log(step + 2.0))
            ucb = min(1.5, mean + beta * uncertainty)
            # Cost is known only after a cell is pulled.  This estimate uses
            # observed calls for the row and never reads an unpulled cost.
            score = ucb - 0.08 * math.log(max(cost_est, 1e-12) / global_cost)
            scored.append((arm, score))
        best_score = max(score for _, score in scored)
        temperature = max(0.01, 0.16 * (1.0 - step / max(1, target - 1)))
        weights = [math.exp(min(50.0, (score - best_score) / temperature)) for _, score in scored]
        arm = rng.choices([arm for arm, _ in scored], weights=weights, k=1)[0]
        cost = _pick_cell(arm, question, rewards, costs, observed, seen)
        samples_by_question.setdefault(question, {})[arm] = (observed[arm][-1][0], cost)

    refresh_statistics()
    recommendations: list[tuple[float, float, str, int]] = []
    for arm in range(k):
        predicted = [
            _weighted_prediction(arm, question, samples_by_question, k, bandwidth, slot_weights, global_mean)[0]
            for question in range(n)
        ]
        mean = sum(predicted) / len(predicted) if predicted else global_mean
        cost_est = (
            sum(cost for _, cost in observed[arm]) / len(observed[arm])
            if arm in observed else global_cost
        )
        recommendations.append((-mean, cost_est, str(arm), arm))
    selected = min(recommendations)[-1]
    return "annealed_similarity_completed", selected


def _edge_list(k: int) -> list[tuple[int, int]]:
    """Return undirected one-slot edges of the complete-row Hamming graph."""

    return [(arm, neighbor) for arm in range(k) for neighbor in _hamming_neighbors(arm, k)
            if arm < neighbor]


def _graph_residual_racing(
    fraction: Any, k: int, n: int, rng: random.Random, rewards: Any, costs: Any,
    observed: dict[int, list[tuple[float, float]]], seen: set[tuple[int, int]],
) -> tuple[str, int | None]:
    """Race complete rows using same-question residuals on a Hamming graph.

    A row's score can be estimated from an anchor row plus edge differences
    ``Y[v,q] - Y[u,q]`` measured on the same questions.  Every edge gets its
    own random question permutation, fixed before outcomes are observed.  The
    method is deliberately conservative: it never calls a neighboring row an
    exact cache hit, and at a full budget it falls back to the direct matrix
    means so the exhaustive reference remains exact.

    This is an empirical allocation rule rather than a confidence-certified
    best-arm algorithm.  The paired residual is the proposed structure; the
    radius/cost score only decides which unresolved comparison to buy next.
    """

    target = _cell_count(fraction, k, n)
    q_order = list(range(n))
    rng.shuffle(q_order)
    if target >= k * n:
        for question in q_order:
            for arm in range(k):
                _pick_cell(arm, question, rewards, costs, observed, seen)
        return "full_matrix_direct_reference", None

    cell_reward: dict[tuple[int, int], float] = {}
    cell_cost: dict[tuple[int, int], float] = {}
    row_rewards: dict[int, list[float]] = {}
    row_costs: dict[int, list[float]] = {}

    def pull(arm: int, question: int) -> bool:
        if (arm, question) in seen:
            return False
        cost = _pick_cell(arm, question, rewards, costs, observed, seen)
        reward = float(rewards[arm][question])
        cell_reward[(arm, question)] = reward
        cell_cost[(arm, question)] = cost
        row_rewards.setdefault(arm, []).append(reward)
        row_costs.setdefault(arm, []).append(cost)
        return True

    # The anchor is selected before seeing any outcome.  Spending about half
    # the budget on it makes each later residual much cheaper: on a shared
    # question the anchor cell is already present, so only the candidate cell
    # needs to be purchased.
    anchor = rng.randrange(k)
    anchor_count = min(n, max(1, target // 2))
    for question in q_order[:anchor_count]:
        if len(seen) >= target:
            break
        pull(anchor, question)

    edges = _edge_list(k)
    edge_by_arm: dict[int, list[tuple[int, int]]] = {}
    for edge in edges:
        edge_by_arm.setdefault(edge[0], []).append(edge)
        edge_by_arm.setdefault(edge[1], []).append(edge)
    edge_order: dict[tuple[int, int], list[int]] = {}
    edge_used: dict[tuple[int, int], set[int]] = {}
    edge_samples: dict[tuple[int, int], list[tuple[float, float]]] = {}

    def orient(edge: tuple[int, int], left: int, right: int) -> float:
        delta = edge_samples[edge]
        sign = 1.0 if edge == (left, right) else -1.0
        return sign * (sum(value for value, _ in delta) / len(delta))

    def edge_radius(edge: tuple[int, int]) -> float:
        samples = edge_samples.get(edge, [])
        if not samples:
            return 1.0
        values = [value for value, _ in samples]
        mean = sum(values) / len(values)
        variance = sum((value - mean) ** 2 for value in values) / max(1, len(values) - 1)
        return min(2.0, math.sqrt(variance / len(values)) + 1.0 / math.sqrt(len(values)))

    def row_estimates() -> tuple[dict[int, float], dict[int, float], set[int]]:
        adjacency: dict[int, list[tuple[int, tuple[int, int]]]] = {}
        for edge in edge_samples:
            left, right = edge
            adjacency.setdefault(left, []).append((right, edge))
            adjacency.setdefault(right, []).append((left, edge))
        estimates: dict[int, float] = {}
        radii: dict[int, float] = {}
        reachable = {anchor}
        anchor_values = row_rewards.get(anchor, [])
        if anchor_values:
            estimates[anchor] = sum(anchor_values) / len(anchor_values)
            radii[anchor] = 0.5 / math.sqrt(len(anchor_values))
        # Dijkstra on uncertainty gives a reproducible low-error path to each
        # row.  Path differences telescope in expectation for uniform questions.
        frontier: list[tuple[float, int]] = [(radii.get(anchor, 1.0), anchor)]
        while frontier:
            frontier.sort()
            radius, arm = frontier.pop(0)
            if arm not in estimates:
                continue
            reachable.add(arm)
            for neighbor, edge in adjacency.get(arm, []):
                candidate_radius = radius + edge_radius(edge)
                candidate_mean = estimates[arm] + orient(edge, arm, neighbor)
                if neighbor not in radii or candidate_radius < radii[neighbor]:
                    radii[neighbor] = candidate_radius
                    estimates[neighbor] = candidate_mean
                    frontier.append((candidate_radius, neighbor))
        # Direct observations are safer than a long extrapolated path.
        for arm, values in row_rewards.items():
            if values:
                direct_radius = 0.5 / math.sqrt(len(values))
                if arm not in radii or direct_radius < radii[arm]:
                    estimates[arm] = sum(values) / len(values)
                    radii[arm] = direct_radius
                    reachable.add(arm)
        return estimates, radii, reachable

    def predicted_pair_cost(edge: tuple[int, int]) -> float:
        values = row_costs.get(edge[0], []) + row_costs.get(edge[1], [])
        if not values:
            values = [cost for entries in observed.values() for _, cost in entries]
        return max(1e-9, 2.0 * (sum(values) / len(values) if values else 1.0))

    def pull_edge(edge: tuple[int, int]) -> bool:
        if edge not in edge_order:
            order = list(range(n))
            rng.shuffle(order)
            # Prefer questions where one endpoint has already been measured;
            # this turns a comparison into a one-new-cell residual whenever
            # the anchor (or a previously measured row) is reusable.
            left, right = edge
            order.sort(key=lambda question: (
                not ((left, question) in cell_reward or (right, question) in cell_reward),
                rng.random(),
            ))
        else:
            order = edge_order[edge]
        edge_order[edge] = order
        used = edge_used.setdefault(edge, set())
        left, right = edge
        for question in order:
            if question in used:
                continue
            if len(seen) >= target:
                return False
            before = len(seen)
            pull(left, question)
            if len(seen) >= target and (right, question) not in seen:
                return False
            pull(right, question)
            if (left, question) in cell_reward and (right, question) in cell_reward:
                used.add(question)
                residual = cell_reward[(right, question)] - cell_reward[(left, question)]
                pair_cost = cell_cost[(left, question)] + cell_cost[(right, question)]
                edge_samples.setdefault(edge, []).append((residual, pair_cost))
                return len(seen) > before
        return False

    # Initialize each edge's order on first use, then spend on the comparison
    # with the largest residual uncertainty per observed pair cost.  A small
    # random reserve prevents a bad first anchor from trapping all exploration.
    while len(seen) < target:
        estimates, radii, reachable = row_estimates()
        elite = max(estimates, key=lambda arm: (estimates[arm], -arm)) if estimates else anchor
        focus_arms = sorted(
            reachable,
            key=lambda arm: (estimates.get(arm, 0.5) - radii.get(arm, 1.0), -arm),
            reverse=True,
        )[: min(8, len(reachable))]
        candidates_set: set[tuple[int, int]] = set()
        for arm in focus_arms:
            candidates_set.update(edge_by_arm.get(arm, ()))
        # Keep a bounded global reserve so local graph mistakes do not make
        # the selector inspect all 8,748 edges on every pull.
        reserve_size = min(len(edges), max(16, int(4 * math.sqrt(k))))
        candidates_set.update(rng.sample(edges, reserve_size))
        candidates = list(candidates_set)
        if not candidates:
            candidates = list(edges)
        scored: list[tuple[float, tuple[int, int]]] = []
        for edge in candidates:
            score = edge_radius(edge) / predicted_pair_cost(edge)
            if elite in edge:
                score *= 1.25
            if not edge_samples.get(edge):
                score += 0.05
            score += rng.random() * 1e-6
            scored.append((score, edge))
        _, edge = max(scored, key=lambda item: item[0])
        if not pull_edge(edge):
            # If a previously used question made a pair impossible, try a
            # fresh edge; only a final odd cell may be consumed directly.
            alternatives = [item[1] for item in scored if item[1] != edge]
            if alternatives:
                if not pull_edge(alternatives[0]):
                    break
            else:
                break
    if len(seen) < target:
        for question in q_order:
            for arm in range(k):
                if len(seen) >= target:
                    break
                pull(arm, question)

    estimates, _, _ = row_estimates()
    if not estimates:
        return "paired_residual_completed", anchor
    return "paired_residual_completed", max(estimates, key=lambda arm: (estimates[arm], -arm))


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
            selection_hint: int | None = None
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
            elif algorithm in {"similarity_annealed_ucb", "graph_similarity_ucb"}:
                stop_reason, selection_hint = _similarity_annealed_ucb(
                    parameter_value, k, n, rng, rewards, costs, observed, seen
                )
            elif algorithm in {"graph_residual_racing", "gr_cabai"}:
                stop_reason, selection_hint = _graph_residual_racing(
                    parameter_value, k, n, rng, rewards, costs, observed, seen
                )
            else:
                raise ValueError(f"unknown selector algorithm: {algorithm}")
            selected = selection_hint if selection_hint is not None else _best_observed(observed, config_ids)
            values = observed.get(selected, [])
            selected_observed_accuracy = _safe_mean([reward for reward, _ in values])
            if not values:
                selected_observed_accuracy = None
            outputs.append({
                "algorithm": algorithm,
                "parameter_name": parameter_name,
                "parameter_value": parameter_value,
                "seed": seed,
                "selected_config_id": str(config_ids[selected]),
                "selected_config_index": selected,
                "search_evaluations": len(seen),
                "search_cost": sum(cost for entries in observed.values() for _, cost in entries),
                "selected_observed_accuracy": selected_observed_accuracy,
                "selection_basis": (
                    "paired_residual_graph" if algorithm in {"graph_residual_racing", "gr_cabai"}
                    else "similarity_posterior" if selection_hint is not None else "observed_cells"
                ),
                "selection_time_seconds": time.perf_counter() - started,
                "stop_reason": stop_reason,
                "settings": setting,
            })
    return outputs


__all__ = ["DEFAULT_SETTINGS", "default_settings", "run_sweep"]
