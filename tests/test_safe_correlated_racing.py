import unittest

from retry_search.safe_correlated_racing import run_sccr


class SafeCorrelatedRacingTests(unittest.TestCase):
    def setUp(self):
        # The first and second rows share question difficulty, so their paired
        # differences are nearly constant.  The third row is an iid control.
        base = [0.0, 1.0, 0.0, 1.0, 1.0, 0.0, 1.0, 0.0]
        self.rewards = [
            base,
            [min(1.0, value + 0.1) for value in base],
            [float((i * 3 + 1) % 2) for i in range(len(base))],
        ]
        self.costs = [[1.0 + 0.05 * row for _ in base] for row in range(3)]
        self.ids = ["a", "b", "c"]

    def test_returns_observed_row_and_diagnostics(self):
        result = run_sccr(self.rewards, self.costs, self.ids, cell_budget=14, seed=3)
        self.assertIn(result["selected_config_index"], range(3))
        self.assertGreater(result["search_evaluations"], 0)
        self.assertLessEqual(result["search_evaluations"], 14)
        self.assertIn(result["selection_basis"], {"safe_cost_aware_correlated_racing"})
        self.assertIn("safe_edges", result)
        self.assertIn("unsafe_edges", result)

    def test_cost_cap_and_explicit_slots(self):
        slots = [(0, 0, 0), (0, 0, 1), (1, 1, 1)]
        result = run_sccr(
            self.rewards,
            self.costs,
            self.ids,
            cost_budget=4.0,
            seed=2,
            row_slots=slots,
        )
        # A final pair can overshoot a realized cost cap, but it must not stop
        # before making any observation.
        self.assertGreater(result["search_evaluations"], 0)
        self.assertGreater(result["search_cost"], 0.0)
        self.assertEqual(result["selected_config_id"], self.ids[result["selected_config_index"]])

    def test_rejects_invalid_gate_parameters(self):
        with self.assertRaises(ValueError):
            run_sccr(self.rewards, self.costs, self.ids, cell_budget=4, calibration_block=1)
        with self.assertRaises(ValueError):
            run_sccr(self.rewards, self.costs, self.ids, cell_budget=4, min_reduction=1.0)
        with self.assertRaises(ValueError):
            run_sccr(self.rewards, self.costs, self.ids, cell_budget=4, variance_margin=float("nan"))
        with self.assertRaises(ValueError):
            run_sccr(self.rewards, self.costs, self.ids, cell_budget=4, margin=float("nan"))

    def test_gate_can_reject_anti_correlated_pair(self):
        # Opposite answers on the same question make the paired residual noisier
        # than two independent row estimates.  The selector must retain the
        # direct fallback rather than treating this edge as safe.
        rewards = [
            [0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0],
            [1.0, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 0.0],
            self.rewards[2],
        ]
        result = run_sccr(rewards, self.costs, self.ids, cell_budget=14, seed=0)
        self.assertGreater(result["unsafe_edges"], 0)
        self.assertGreater(result["gated_fallbacks"], 0)

    def test_full_calibration_still_uses_direct_decision(self):
        result = run_sccr(
            [[0.0, 0.0, 0.0, 0.0], [1.0, 1.0, 1.0, 1.0]],
            [[1.0] * 4, [1.0] * 4],
            ["low", "high"],
            cell_budget=8,
            seed=0,
            initial_block=1,
            calibration_block=4,
        )
        self.assertEqual(result["selected_config_id"], "high")
        self.assertEqual(result["search_evaluations"], 8)


if __name__ == "__main__":
    unittest.main()
