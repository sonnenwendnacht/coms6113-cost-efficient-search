import unittest

from retry_search.selection_sweep import run_sweep


class SelectionSweepTests(unittest.TestCase):
    def setUp(self):
        # Eight configurations with deliberately different rewards/costs.
        self.rewards = [[(i + q) % 3 / 2 for q in range(6)] for i in range(8)]
        self.costs = [[1.0 + (i % 3) * 0.1 for _ in range(6)] for i in range(8)]
        self.ids = [f"row-{i}" for i in range(8)]

    def test_each_setting_is_reported_and_search_has_no_duplicates(self):
        settings = [
            {"algorithm": "random", "parameter_name": "fraction", "parameter_value": 0.25},
            {"algorithm": "matrix_ucb_e", "parameter_name": "fraction", "parameter_value": 0.2},
            {"algorithm": "arm_elimination", "parameter_name": "confidence_multiplier", "parameter_value": 1.0},
        ]
        rows = run_sweep(self.rewards, self.costs, self.ids, settings=settings, seeds=[3, 4])
        self.assertEqual(len(rows), 6)
        self.assertEqual({r["seed"] for r in rows}, {3, 4})
        for row in rows:
            self.assertGreater(row["search_evaluations"], 0)
            self.assertGreater(row["search_cost"], 0)
            self.assertIn(row["selected_config_id"], self.ids)

    def test_heldout_values_are_not_an_argument(self):
        with self.assertRaises(TypeError):
            run_sweep(self.rewards, self.costs, self.ids, heldout=self.rewards)

    def test_invalid_matrix_is_rejected(self):
        with self.assertRaises(ValueError):
            run_sweep([[1.0]], [[1.0, 2.0]], ["row"])


if __name__ == "__main__":
    unittest.main()
