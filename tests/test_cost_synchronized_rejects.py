import unittest

from retry_search.cost_synchronized_rejects import run_cost_sysrs


class CostSynchronizedRejectsTests(unittest.TestCase):
    def setUp(self):
        self.rewards = [
            [0.0, 0.0, 1.0, 1.0, 0.0, 1.0],
            [1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
            [0.0, 1.0, 0.0, 1.0, 0.0, 1.0],
        ]
        self.costs = [
            [1.0] * 6,
            [1.2] * 6,
            [1.1] * 6,
        ]
        self.ids = ["a", "b", "c"]

    def test_full_cell_budget_returns_directly_observed_best_row(self):
        result = run_cost_sysrs(self.rewards, self.costs, self.ids, cell_budget=18, seed=2)
        self.assertEqual(result["selected_config_id"], "b")
        self.assertLessEqual(result["search_evaluations"], 18)
        self.assertGreater(result["search_evaluations"], 0)
        self.assertFalse(result["incomplete_phase"])

    def test_realized_cost_budget_reports_overshoot(self):
        result = run_cost_sysrs(self.rewards, self.costs, self.ids, cost_budget=2.0, seed=3)
        self.assertGreater(result["search_evaluations"], 0)
        self.assertGreaterEqual(result["overshoot"], 0.0)
        self.assertEqual(result["budget_basis"], "realized_cost_budget")

    def test_tiny_cost_budget_does_not_recommend_from_partial_block(self):
        result = run_cost_sysrs(self.rewards, self.costs, self.ids, cost_budget=0.5, seed=3)
        self.assertTrue(result["incomplete_phase"])
        self.assertIsNone(result["selected_config_id"])
        self.assertEqual(result["selection_status"], "no_complete_common_sample")

    def test_tiny_cell_budget_does_not_pick_unobserved_row(self):
        result = run_cost_sysrs(self.rewards, self.costs, self.ids, cell_budget=1, seed=3)
        self.assertEqual(result["complete_phases"], 0)
        self.assertIsNone(result["selected_config_id"])
        self.assertEqual(result["selection_status"], "no_complete_common_sample")

    def test_requires_one_budget(self):
        with self.assertRaises(ValueError):
            run_cost_sysrs(self.rewards, self.costs, self.ids)
        with self.assertRaises(ValueError):
            run_cost_sysrs(self.rewards, self.costs, self.ids, cell_budget=4, cost_budget=4.0)


if __name__ == "__main__":
    unittest.main()
