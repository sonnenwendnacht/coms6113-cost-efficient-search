import unittest

from retry_search.slot_gated_factorial_racing import run_sgfr


class SlotGatedFactorialRacingTests(unittest.TestCase):
    def setUp(self):
        self.rewards = [[float((row + q) % 5 == 0) for q in range(8)] for row in range(8)]
        # Row 7 is a stable high-quality row; rows 0 and 1 form a quiet pair.
        self.rewards[7] = [1.0] * 8
        self.costs = [[1.0 + .1 * row for _ in range(8)] for row in range(8)]
        self.attempts = [[1 + int((row + q) % 3 == 0) for q in range(8)] for row in range(8)]
        self.ids = [f"row-{row}" for row in range(8)]

    def test_full_budget_is_direct_and_exact(self):
        result = run_sgfr(self.rewards, self.costs, self.ids, attempts=self.attempts, cell_budget=64, seed=1)
        self.assertEqual(result["stop_reason"], "full_matrix_direct_reference")
        self.assertEqual(result["search_evaluations"], 64)
        self.assertEqual(result["selected_config_id"], "row-7")

    def test_deterministic_and_complete_rows(self):
        kwargs = dict(attempts=self.attempts, budget_fraction=.75, seed=42,
                      calibration_fraction=.5, reserve_fraction=.1)
        first = run_sgfr(self.rewards, self.costs, self.ids, **kwargs)
        second = run_sgfr(self.rewards, self.costs, self.ids, **kwargs)
        self.assertEqual(first, second)
        self.assertEqual(first["selection_basis"], "slot_gated_factorial_racing")
        self.assertGreater(first["calibration_pair_count"], 0)
        self.assertGreaterEqual(first["confirmation_evaluations"], 0)
        self.assertIn(first["selected_config_id"], self.ids)

    def test_missing_reach_channel_is_explicit(self):
        result = run_sgfr(self.rewards, self.costs, self.ids, cell_budget=48,
                          calibration_fraction=.5, reserve_fraction=.1, seed=0)
        self.assertFalse(result["reach_gate_enabled"])
        self.assertTrue(all(g["reach"]["state"] == "disabled" for g in result["slot_gates"]))

    def test_post_calibration_racing_phase_executes(self):
        result = run_sgfr(
            self.rewards, self.costs, self.ids, attempts=self.attempts,
            budget_fraction=.75, calibration_fraction=.25,
            reserve_fraction=.15, seed=42,
        )
        self.assertGreater(result["racing_pair_count"], 0)

    def test_calibration_round_robin_covers_each_slot_when_budget_allows(self):
        n = 80
        rewards = [[float((row + question) % 5 == 0) for question in range(n)]
                   for row in range(8)]
        costs = [[1.0] * n for _ in range(8)]
        attempts = [[1] * n for _ in range(8)]
        result = run_sgfr(
            rewards, costs, [f"row-{row}" for row in range(8)], attempts=attempts,
            budget_fraction=.95, calibration_fraction=.75,
            confirmation_fraction=.10, reserve_fraction=.01, seed=42,
        )
        observed_slots = {pair["slot"] for pair in result["calibration_pairs"][:3]}
        self.assertEqual(observed_slots, {0, 1, 2})

    def test_rejects_partial_complete_row_budget(self):
        with self.assertRaises(ValueError):
            run_sgfr(self.rewards, self.costs, self.ids, cell_budget=7)

    def test_non_cube_requires_slots(self):
        with self.assertRaises(ValueError):
            run_sgfr(self.rewards[:7], self.costs[:7], self.ids[:7], cell_budget=56)


if __name__ == "__main__":
    unittest.main()
