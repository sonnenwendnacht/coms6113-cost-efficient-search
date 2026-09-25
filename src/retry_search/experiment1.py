"""Experiment 1: retry-aware search over 27 ordered solver rows.

The module deliberately separates the expensive workflow traces from the
search policy.  A trace cell is one complete deployment on one MathQA
question and contains every solver/checker call reached by that row.  Search
policies can therefore be replayed without making another model call.
"""

from __future__ import annotations

import hashlib
import json
import math
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


SOLVER_MODELS = (
    "qwen2.5-1.5b",
    "qwen2.5-3b",
    "qwen2.5-7b",
)
VERIFIER_MODEL = "qwen2.5-1.5b"
# These are deliberately simulated USD/input-token coefficients for the local
# proxy run.  They are versioned inputs, not claims about provider pricing.
DEFAULT_COEFFICIENTS_USD_PER_TOKEN = {
    "qwen2.5-1.5b": 1.0e-7,
    "qwen2.5-3b": 3.0e-7,
    "qwen2.5-7b": 5.0e-7,
}


def configurations(models: Sequence[str] = SOLVER_MODELS) -> list[tuple[str, str, str]]:
    """Return all ordered triples, allowing a model to repeat across retries."""

    return [(a, b, c) for a in models for b in models for c in models]


def configuration_id(config: Sequence[str]) -> str:
    return "/".join(config)


def stable_sample(rows: Sequence[Mapping[str, Any]], n: int, seed: int) -> list[dict[str, Any]]:
    """Select a reproducible split without using answer labels in the prompts."""

    keyed = []
    for i, row in enumerate(rows):
        key = hashlib.sha256(f"{seed}:{i}:{row['Problem']}".encode()).hexdigest()
        keyed.append((key, i, dict(row)))
    keyed.sort()
    return [row for _, _, row in keyed[:n]]


def split_mathqa(
    path: str | Path, search_n: int = 20, audit_n: int = 10, seed: int = 6113
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    rows = json.loads(Path(path).read_text(encoding="utf-8"))
    selected = stable_sample(rows, search_n + audit_n, seed)
    return selected[:search_n], selected[search_n:]


def question_prompt(row: Mapping[str, Any]) -> str:
    return (
        "Solve this multiple-choice math problem. Explain the calculation briefly and "
        "finish with exactly one line of the form FINAL: a, FINAL: b, FINAL: c, "
        "FINAL: d, or FINAL: e.\n\n"
        f"Problem: {row['Problem']}\nOptions: {row['options']}"
    )


def solver_prompt(
    row: Mapping[str, Any], previous: str | None = None, feedback: str | None = None
) -> str:
    prompt = question_prompt(row)
    if previous:
        prompt += (
            "\n\nThis is a retry. The previous attempt was:\n"
            + previous[-2400:]
            + "\n\nThe deployment checker gave this feedback:\n"
            + (feedback or "RETRY")[-800:]
            + "\nReconsider the calculation and produce a new answer."
        )
    return prompt


def verifier_prompt(row: Mapping[str, Any], candidate: str) -> str:
    return (
        "You are a deployment-time verifier for a math solver. You do not have the "
        "answer key and must not assume one. Check the candidate's reasoning against "
        "the problem and options. Return exactly one line, VERDICT: PASS if the "
        "candidate is convincing, otherwise VERDICT: RETRY. You may give one short "
        "reason after that line.\n\n"
        f"Problem: {row['Problem']}\nOptions: {row['options']}\n"
        f"Candidate response:\n{candidate[-3000:]}"
    )


def parse_answer(text: str) -> str | None:
    import re

    matches = re.findall(r"\bFINAL\s*:\s*([A-Ea-e])\b", text)
    if matches:
        return matches[-1].lower()
    # A fallback is useful when a small local model omits the requested marker.
    matches = re.findall(r"(?:answer|choice)\s*(?:is|:)\s*([A-Ea-e])\b", text, re.I)
    return matches[-1].lower() if matches else None


def parse_verdict(text: str) -> bool:
    import re

    matches = re.findall(r"VERDICT\s*:\s*(PASS|RETRY)", text, re.I)
    return bool(matches and matches[-1].upper() == "PASS")


def primary_cost(calls: Iterable[Mapping[str, Any]]) -> float:
    return sum(float(c["coefficient_usd_per_token"]) * int(c["input_tokens"]) for c in calls)


@dataclass(frozen=True)
class Cell:
    question_id: int
    config_id: str
    reward: int
    cost_usd: float
    input_tokens: int
    attempts: int
    accepted_attempt: int | None


def cell_from_json(obj: Mapping[str, Any]) -> Cell:
    return Cell(
        question_id=int(obj["question_id"]),
        config_id=str(obj["config_id"]),
        reward=int(obj["final_correct"]),
        cost_usd=float(obj["cost_usd"]),
        input_tokens=int(obj["input_tokens"]),
        attempts=(len(obj["attempts"]) if isinstance(obj["attempts"], list) else int(obj["attempts"])),
        accepted_attempt=obj.get("accepted_attempt"),
    )


class Policy:
    name = "policy"

    def choose(self, arms: list[str], counts: Mapping[str, int], means: Mapping[str, float], costs: Mapping[str, float], t: int, rng: random.Random) -> str:
        raise NotImplementedError


class RandomPolicy(Policy):
    name = "random"

    def choose(self, arms, counts, means, costs, t, rng):
        return rng.choice(arms)


class UniformPolicy(Policy):
    name = "uniform"

    def choose(self, arms, counts, means, costs, t, rng):
        return min(arms, key=lambda a: (counts[a], a))


class UCBPolicy(Policy):
    name = "ucb1"

    def choose(self, arms, counts, means, costs, t, rng):
        unseen = [a for a in arms if counts[a] == 0]
        if unseen:
            return unseen[0]
        return max(arms, key=lambda a: (means[a] + math.sqrt(2.0 * math.log(max(2, t)) / counts[a]), -costs[a], a))


class CostUCBPolicy(UCBPolicy):
    name = "cost_ucb"

    def choose(self, arms, counts, means, costs, t, rng):
        unseen = [a for a in arms if counts[a] == 0]
        if unseen:
            return min(unseen, key=lambda a: (costs[a], a))
        return max(
            arms,
            key=lambda a: (
                (means[a] + math.sqrt(2.0 * math.log(max(2, t)) / counts[a]))
                / max(costs[a], 1e-12),
                -costs[a],
                a,
            ),
        )


class ArmEliminationPolicy(Policy):
    """AgentOpt-style confidence elimination adapted to dollar stopping."""

    name = "arm_elimination"

    def choose(self, arms, counts, means, costs, t, rng):
        unseen = [a for a in arms if counts[a] == 0]
        if unseen:
            return unseen[0]
        radius = {a: math.sqrt(2.0 * math.log(max(2, t)) / counts[a]) for a in arms}
        best_lower = max(means[a] - radius[a] for a in arms)
        active = [a for a in arms if means[a] + radius[a] >= best_lower]
        return min(active, key=lambda a: (counts[a], -means[a], a))


class KernelBayesUCBPolicy(Policy):
    """Small dependency-free categorical GP-UCB-like baseline.

    The kernel treats two rows as similar when they differ in fewer retry
    slots. It is intentionally a baseline, not a claim to reproduce a
    particular Bayesian optimizer implementation.
    """

    name = "kernel_bayes_ucb"

    @staticmethod
    def _distance(a: str, b: str) -> int:
        xa, xb = a.split("/"), b.split("/")
        return sum(x != y for x, y in zip(xa, xb))

    def choose(self, arms, counts, means, costs, t, rng):
        unseen = [a for a in arms if counts[a] == 0]
        if not means:
            return arms[0]
        observed = [a for a in arms if counts[a] > 0]
        if unseen and len(observed) < 2:
            return unseen[0]
        n = len(observed)
        length = 1.0
        noise = 0.15
        k = [[math.exp(-self._distance(a, b) / length) + (noise if i == j else 0.0)
              for j, b in enumerate(observed)] for i, a in enumerate(observed)]
        y = [means[a] for a in observed]
        alpha = _solve_linear(k, y)
        best_arm, best_value = None, -float("inf")
        for arm in arms:
            cov = [math.exp(-self._distance(arm, b) / length) for b in observed]
            mean = sum(c * x for c, x in zip(cov, alpha))
            var = max(0.01, 1.0 - sum(c * x for c, x in zip(cov, _solve_linear(k, cov))))
            value = mean + 1.5 * math.sqrt(var)
            if value > best_value or (value == best_value and arm < (best_arm or arm)):
                best_arm, best_value = arm, value
        return best_arm or arms[0]


def _solve_linear(a: list[list[float]], b: list[float]) -> list[float]:
    """Gaussian elimination for the tiny (<=27) GP system."""

    n = len(b)
    aug = [row[:] + [float(bi)] for row, bi in zip(a, b)]
    for col in range(n):
        pivot = max(range(col, n), key=lambda i: abs(aug[i][col]))
        if abs(aug[pivot][col]) < 1e-12:
            aug[pivot][col] = 1e-12
        aug[col], aug[pivot] = aug[pivot], aug[col]
        p = aug[col][col]
        aug[col] = [x / p for x in aug[col]]
        for i in range(n):
            if i == col:
                continue
            factor = aug[i][col]
            aug[i] = [x - factor * y for x, y in zip(aug[i], aug[col])]
    return [aug[i][-1] for i in range(n)]


def replay_policy(
    cells: Mapping[tuple[str, int], Cell],
    search_question_ids: Sequence[int],
    audit_cells: Mapping[tuple[str, int], Cell],
    policy: Policy,
    budget_usd: float,
    seed: int,
) -> dict[str, Any]:
    arms = sorted({arm for arm, _ in cells})
    rng = random.Random(seed)
    counts = {a: 0 for a in arms}
    sums = {a: 0.0 for a in arms}
    costs = {a: 0.0 for a in arms}
    steps: list[dict[str, Any]] = []
    while True:
        t = len(steps) + 1
        arm = policy.choose(arms, counts, {a: (sums[a] / counts[a] if counts[a] else 0.0) for a in arms}, {a: (costs[a] / counts[a] if counts[a] else 1.0) for a in arms}, t, rng)
        q_index = counts[arm]
        if q_index >= len(search_question_ids):
            available = [a for a in arms if counts[a] < len(search_question_ids)]
            if not available:
                break
            arm = min(available, key=lambda a: (counts[a], a))
            q_index = counts[arm]
        qid = int(search_question_ids[q_index])
        cell = cells[(arm, qid)]
        if sum(x["cost_usd"] for x in steps) + cell.cost_usd > budget_usd:
            break
        counts[arm] += 1
        sums[arm] += cell.reward
        costs[arm] += cell.cost_usd
        cumulative = sum(x["cost_usd"] for x in steps) + cell.cost_usd
        steps.append({"step": t, "config_id": arm, "question_id": qid, "reward": cell.reward, "cost_usd": cell.cost_usd, "cumulative_cost_usd": cumulative})
    selected = max(arms, key=lambda a: ((sums[a] / counts[a]) if counts[a] else -1.0, -costs[a], a))
    audit = [audit_cells[(selected, q)] for q in sorted({q for arm, q in audit_cells if arm == selected})]
    # The comprehension above intentionally uses only the selected row; the
    # search policy never sees the audit cells.
    audit_accuracy = sum(c.reward for c in audit) / len(audit) if audit else None
    return {
        "policy": policy.name,
        "seed": seed,
        "budget_usd": budget_usd,
        "search_spend_usd": sum(x["cost_usd"] for x in steps),
        "steps": steps,
        "selected_config_id": selected,
        "selected_search_accuracy": (sums[selected] / counts[selected]) if counts[selected] else None,
        "audit_accuracy": audit_accuracy,
        "audit_n": len(audit),
    }


def oracle(cells: Mapping[tuple[str, int], Cell], question_ids: Sequence[int]) -> dict[str, Any]:
    arms = sorted({a for a, _ in cells})
    scores = {
        a: sum(cells[(a, q)].reward for q in question_ids) / len(question_ids)
        for a in arms
    }
    selected = max(arms, key=lambda a: (scores[a], -sum(cells[(a, q)].cost_usd for q in question_ids), a))
    return {"config_id": selected, "accuracy": scores[selected], "n": len(question_ids)}
