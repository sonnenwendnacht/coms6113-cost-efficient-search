"""Small deterministic fixture runner for validating retry cost accounting.

This is not a live checkpoint engine. A fixture supplies outcomes for complete
attempt prefixes, so a model reached through different histories is distinct.
The caller gives each fixture/version/repetition a distinct context_id.
On exhausted retries this toy workflow emits the last answer, even if rejected
by the checker. A real workflow must choose and document return/abstain behavior.
"""

from dataclasses import dataclass
from typing import Mapping


@dataclass(frozen=True)
class Outcome:
    accepted: bool  # Decision made by the workflow's deployable checker.
    correct: bool  # Hidden grading result, never used to decide a retry.
    cost_units: int  # Includes this attempt's checker cost in the fixture.

    def __post_init__(self):
        if type(self.cost_units) is not int or self.cost_units < 0:
            raise ValueError("cost_units must be a nonnegative integer")


@dataclass(frozen=True)
class Attempt:
    prefix: tuple[str, ...]
    outcome: Outcome
    reused: bool
    paid_units: int


@dataclass(frozen=True)
class Evaluation:
    completed: bool
    final_correct: bool | None
    attempts: tuple[Attempt, ...]

    @property
    def search_spend_units(self):
        return sum(a.paid_units for a in self.attempts)

    @property
    def cold_execution_cost_units(self):
        """Full cost of the observed path, regardless of profiling reuse.

        For an incomplete evaluation this is only the partial-path cost.
        """
        return sum(a.outcome.cost_units for a in self.attempts)


class Replay:
    def __init__(
        self,
        outcomes: Mapping[tuple[str, tuple[str, ...]], Outcome],
        *,
        context_id: str,
        budget_units: int,
        reuse: bool = True,
    ):
        if not context_id:
            raise ValueError("A fixture/version/repetition identity is required")
        if type(budget_units) is not int or budget_units < 0:
            raise ValueError("budget_units must be a nonnegative integer")
        self._outcomes = dict(outcomes)
        self._context_id = context_id
        self._budget_units = budget_units
        self._reuse = reuse
        self._cache = {}
        self.spent_units = 0

    def evaluate(self, question: str, models: tuple[str, ...]) -> Evaluation:
        if not models or any(not isinstance(m, str) or not m for m in models):
            raise ValueError("Provide at least one nonempty model identifier")
        attempts = []
        for index in range(len(models)):
            prefix = tuple(models[: index + 1])
            key = (self._context_id, question, prefix)
            reused = self._reuse and key in self._cache
            if reused:
                outcome = self._cache[key]
                paid = 0
            else:
                # Only this requested cell is returned to the caller. Fixtures
                # are offline test data, not an API security boundary.
                outcome = self._outcomes[(question, prefix)]
                paid = outcome.cost_units
                if self.spent_units + paid > self._budget_units:
                    return Evaluation(False, None, tuple(attempts))
                self.spent_units += paid
                if self._reuse:
                    self._cache[key] = outcome
            attempts.append(Attempt(prefix, outcome, reused, paid))
            if outcome.accepted:
                break
        return Evaluation(True, attempts[-1].outcome.correct, tuple(attempts))
