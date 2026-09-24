import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from retry_search.replay import Outcome, Replay


class RetryAccountingTests(unittest.TestCase):
    def fixture(self, **kwargs):
        return Replay(
            {
                ("hard", ("cheap",)): Outcome(False, False, 2),
                ("hard", ("cheap", "strong")): Outcome(True, True, 7),
                ("hard", ("cheap", "medium")): Outcome(False, False, 4),
                ("hard", ("strong",)): Outcome(True, True, 5),
                ("easy", ("cheap",)): Outcome(True, True, 2),
                ("false_accept", ("cheap",)): Outcome(True, False, 2),
                ("false_reject", ("cheap",)): Outcome(False, True, 2),
                ("false_reject", ("cheap", "strong")): Outcome(True, True, 7),
            },
            context_id="invented-v1-repetition-0",
            **kwargs,
        )

    def test_failed_attempts_are_paid_and_success_stops(self):
        r = self.fixture(budget_units=20)
        hard = r.evaluate("hard", ("cheap", "strong"))
        self.assertTrue(hard.final_correct)
        self.assertEqual(hard.search_spend_units, 9)
        # No suffix fixture exists: early success must avoid reading it.
        easy = r.evaluate("easy", ("cheap", "strong"))
        self.assertEqual(len(easy.attempts), 1)
        self.assertEqual(r.spent_units, 11)

    def test_shared_prefix_saves_search_but_not_cold_deployment_cost(self):
        r = self.fixture(budget_units=20)
        r.evaluate("hard", ("cheap", "strong"))
        neighbor = r.evaluate("hard", ("cheap", "medium"))
        self.assertEqual(neighbor.search_spend_units, 4)
        self.assertEqual(neighbor.cold_execution_cost_units, 6)
        self.assertTrue(neighbor.attempts[0].reused)
        self.assertEqual(r.spent_units, 13)

    def test_suffix_is_not_reused_as_standalone_model(self):
        r = self.fixture(budget_units=20)
        r.evaluate("hard", ("cheap", "strong"))
        standalone = r.evaluate("hard", ("strong",))
        self.assertEqual(standalone.search_spend_units, 5)
        self.assertFalse(standalone.attempts[0].reused)

    def test_partial_run_is_not_mislabeled_failure_and_budget_not_exceeded(self):
        r = self.fixture(budget_units=8)
        result = r.evaluate("hard", ("cheap", "strong"))
        self.assertFalse(result.completed)
        self.assertIsNone(result.final_correct)
        self.assertEqual(r.spent_units, 2)
        self.assertEqual(len(result.attempts), 1)

    def test_repetition_and_no_cache_runs_pay_again(self):
        r = self.fixture(budget_units=20, reuse=False)
        r.evaluate("hard", ("cheap", "strong"))
        r.evaluate("hard", ("cheap", "strong"))
        self.assertEqual(r.spent_units, 18)
        # A new repetition/fixture instance starts cold.
        other = self.fixture(budget_units=20)
        self.assertEqual(other.evaluate("hard", ("cheap",)).search_spend_units, 2)

    def test_retry_checker_does_not_use_hidden_correctness(self):
        r = self.fixture(budget_units=20)
        accepted = r.evaluate("false_accept", ("cheap", "strong"))
        self.assertFalse(accepted.final_correct)
        self.assertEqual(len(accepted.attempts), 1)
        rejected = r.evaluate("false_reject", ("cheap", "strong"))
        self.assertEqual(len(rejected.attempts), 2)
        self.assertEqual(rejected.search_spend_units, 9)

    def test_invalid_costs_and_empty_configuration_rejected(self):
        for cost in [-1, 1.5, True]:
            with self.assertRaises(ValueError):
                Outcome(False, False, cost)
        with self.assertRaises(ValueError):
            self.fixture(budget_units=1).evaluate("hard", ())


if __name__ == "__main__":
    unittest.main()
