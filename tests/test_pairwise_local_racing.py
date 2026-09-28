import unittest

from retry_search.pairwise_local_racing import run_cw_plr


class PairwiseLocalRacingTests(unittest.TestCase):
    def setUp(self):
        self.rewards = [[float((row + q) % 3 == 0) for q in range(8)] for row in range(8)]
        self.costs = [[1.0 + 0.1 * row for _ in range(8)] for row in range(8)]
        self.ids = [f"row-{row}" for row in range(8)]

    def test_cost_budget_records_realized_overshoot(self):
        result = run_cw_plr(self.rewards, self.costs, self.ids, cost_budget=20.0, seed=2)
        self.assertIn(result["selected_config_id"], self.ids)
        self.assertGreaterEqual(result["search_cost"], 20.0)
        self.assertGreater(result["search_evaluations"], 0)

    def test_exactly_one_budget_is_required(self):
        with self.assertRaises(ValueError):
            run_cw_plr(self.rewards, self.costs, self.ids, seed=0)
        with self.assertRaises(ValueError):
            run_cw_plr(self.rewards, self.costs, self.ids, cell_budget=4, cost_budget=4, seed=0)


if __name__ == "__main__":
    unittest.main()
