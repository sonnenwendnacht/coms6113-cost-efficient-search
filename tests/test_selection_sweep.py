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

    def test_similarity_selector_uses_hamming_side_information(self):
        # The best row is never required to be pulled: its one-slot neighbors
        # carry enough same-question signal for the posterior recommendation.
        rewards = [
            [1.0 if arm == 7 else (0.8 if bin(arm ^ 7).count("1") == 1 else 0.2) for _ in range(6)]
            for arm in range(8)
        ]
        costs = [[1.0 + 0.1 * arm for _ in range(6)] for arm in range(8)]
        rows = run_sweep(
            rewards,
            costs,
            [f"row-{i}" for i in range(8)],
            settings=[{"algorithm": "similarity_annealed_ucb", "parameter_name": "fraction", "parameter_value": 0.5}],
            seeds=[1],
        )
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["selected_config_id"], "row-7")
        self.assertEqual(rows[0]["selection_basis"], "similarity_posterior")
        self.assertEqual(rows[0]["search_evaluations"], 24)

    def test_similarity_selector_does_not_duplicate_cells(self):
        rewards = [[(arm + question) % 2 for question in range(4)] for arm in range(8)]
        costs = [[1.0 for _ in range(4)] for _ in range(8)]
        rows = run_sweep(
            rewards,
            costs,
            [f"row-{i}" for i in range(8)],
            settings=[{"algorithm": "similarity_annealed_ucb", "parameter_name": "fraction", "parameter_value": 0.75}],
            seeds=[4, 5],
        )
        self.assertEqual([row["search_evaluations"] for row in rows], [24, 24])


if __name__ == "__main__":
    unittest.main()
