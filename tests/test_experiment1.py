import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from retry_search.experiment1 import (
    ArmEliminationPolicy,
    KernelBayesUCBPolicy,
    SOLVER_MODELS,
    configurations,
    parse_answer,
    parse_verdict,
    primary_cost,
    question_prompt,
    verifier_prompt,
)


class Experiment1AccountingTests(unittest.TestCase):
    def test_ordered_rows_allow_repeated_retry_models(self):
        rows = configurations()
        self.assertEqual(len(rows), 27)
        self.assertIn((SOLVER_MODELS[0],) * 3, rows)
        self.assertIn((SOLVER_MODELS[2], SOLVER_MODELS[0], SOLVER_MODELS[1]), rows)

    def test_primary_cost_is_input_tokens_only(self):
        calls = [
            {"coefficient_usd_per_token": 1e-7, "input_tokens": 100, "output_tokens": 10000},
            {"coefficient_usd_per_token": 5e-7, "input_tokens": 200, "output_tokens": 1},
        ]
        self.assertAlmostEqual(primary_cost(calls), 1.1e-4)

    def test_verifier_prompt_is_blind_to_answer_key(self):
        row = {"Problem": "What is 2+2?", "options": "a ) 3, b ) 4", "correct": "b", "Rationale": "secret"}
        prompt = verifier_prompt(row, "FINAL: b")
        self.assertNotIn("secret", prompt)
        self.assertNotIn('"correct"', prompt)
        self.assertNotIn("correct: b", prompt.lower())
        self.assertNotIn("Rationale", prompt)

    def test_parsers_and_baseline_names(self):
        self.assertEqual(parse_answer("work\nFINAL: C"), "c")
        self.assertTrue(parse_verdict("VERDICT: PASS\nlooks good"))
        self.assertFalse(parse_verdict("VERDICT: RETRY"))
        self.assertEqual(ArmEliminationPolicy.name, "arm_elimination")
        self.assertEqual(KernelBayesUCBPolicy.name, "kernel_bayes_ucb")


if __name__ == "__main__":
    unittest.main()
