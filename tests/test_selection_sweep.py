import math
import random
import unittest
from unittest.mock import patch

import retry_search.selection_sweep as sweep

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

    def test_graph_residual_is_exact_at_full_fraction(self):
        # The structured estimator is optional side information.  It must not
        # change the exhaustive reference when every cell is paid for.
        rewards = [[1.0 if arm == 7 else 0.0 for _ in range(4)] for arm in range(8)]
        costs = [[1.0 for _ in range(4)] for _ in range(8)]
        rows = run_sweep(
            rewards,
            costs,
            [f"row-{i}" for i in range(8)],
            settings=[{"algorithm": "graph_residual_racing", "parameter_name": "fraction", "parameter_value": 1.0}],
            seeds=[0],
        )
        self.assertEqual(rows[0]["selected_config_id"], "row-7")
        self.assertEqual(rows[0]["search_evaluations"], 32)
        self.assertEqual(rows[0]["stop_reason"], "full_matrix_direct_reference")

    def test_graph_residual_uses_paired_cells_without_duplicates(self):
        rewards = [[float((arm + question) % 2) for question in range(5)] for arm in range(8)]
        costs = [[1.0 + 0.1 * arm for _ in range(5)] for arm in range(8)]
        rows = run_sweep(
            rewards,
            costs,
            [f"row-{i}" for i in range(8)],
            settings=[{"algorithm": "graph_residual_racing", "parameter_name": "fraction", "parameter_value": 0.5}],
            seeds=[2, 3],
        )
        self.assertEqual([row["search_evaluations"] for row in rows], [20, 20])
        self.assertTrue(all(row["selection_basis"] == "paired_residual_graph" for row in rows))


class ExactBayesianOptimizationTests(unittest.TestCase):
    @staticmethod
    def dense_score(k, observed, arm):
        """Original uncapped posterior, independently solved for each row."""
        arms = sorted(observed)
        kernel = [
            [math.exp(-sweep._hamming_distance(a, b, k)) + (0.12 if i == j else 0.0)
             for j, b in enumerate(arms)]
            for i, a in enumerate(arms)
        ]
        y = [sum(reward for reward, _ in observed[a]) / len(observed[a]) for a in arms]
        alpha = sweep._solve_linear(kernel, y)
        cov = [math.exp(-sweep._hamming_distance(arm, a, k)) for a in arms]
        solved = sweep._solve_linear(kernel, cov)
        mean = sum(c * value for c, value in zip(cov, alpha))
        variance = max(0.01, 1.0 - sum(c * value for c, value in zip(cov, solved)))
        return mean + 1.5 * math.sqrt(variance)

    @classmethod
    def dense_bo(cls, rewards, costs, fraction, seed):
        """Legacy row schedule and score tie break, with no inducing cap."""
        k, n = len(rewards), len(rewards[0])
        rng = random.Random(seed)
        questions = list(range(n))
        rng.shuffle(questions)
        candidates = list(range(k))
        rng.shuffle(candidates)
        observed, seen = {}, set()
        while len(observed) < sweep._row_count(fraction, k):
            if not observed:
                arm = candidates.pop()
            else:
                arm = max(candidates, key=lambda a: (cls.dense_score(k, observed, a), -a))
                candidates.remove(arm)
            sweep._pull_row(arm, questions, rewards, costs, observed, seen)
        return observed, seen

    def test_incremental_scores_equal_dense_with_more_than_32_observations(self):
        numpy = sweep._optional_numpy()
        for backend in (None, numpy) if numpy is not None else (None,):
            with self.subTest(backend="numpy" if backend is not None else "stdlib"):
                with patch.object(sweep, "_optional_numpy", return_value=backend):
                    posterior = sweep._CategoricalPosterior(64)
                rng = random.Random(739)
                order = rng.sample(range(64), 45)
                observed = {}
                for index, arm in enumerate(order):
                    reward = rng.random()
                    observed[arm] = [(reward, 1.0)]
                    posterior.update(arm, reward)
                    if index in (0, 7, 31, 44):
                        for candidate in (0, 7, 19, 31, 45, 63):
                            self.assertAlmostEqual(
                                posterior.score(candidate), self.dense_score(64, observed, candidate),
                                places=11,
                            )

    def test_uncapped_bo_matches_legacy_observations_and_spending(self):
        rng = random.Random(102)
        rewards = [[rng.random() for _ in range(7)] for _ in range(27)]
        costs = [[0.1 + rng.random() for _ in range(7)] for _ in range(27)]
        for seed in (3, 4, 6113):
            expected, expected_seen = self.dense_bo(rewards, costs, 0.75, seed)
            for backend in (None, sweep._optional_numpy()):
                with self.subTest(seed=seed, backend="numpy" if backend is not None else "stdlib"):
                    observed, seen = {}, set()
                    with patch.object(sweep, "_optional_numpy", return_value=backend):
                        result = sweep._bayesian_opt(
                            0.75, 27, 7, random.Random(seed), rewards, costs, observed, seen,
                        )
                    self.assertEqual(result, "fraction_rows_evaluated")
                    self.assertEqual(list(observed), list(expected))
                    self.assertEqual(seen, expected_seen)
                    self.assertEqual(observed, expected)

    def test_similarity_disagreement_cache_matches_full_scan(self):
        rng = random.Random(51)
        samples = {}
        for question in range(5):
            samples[question] = {}
            for arm in rng.sample(range(27), 9):
                samples[question][arm] = (rng.random(), 1.0)
        expected = sweep._similarity_weights(samples, 27)
        cached = sweep._SlotDisagreements(27)
        for question in range(5):
            revealed = {}
            for arm, value in samples[question].items():
                cached.add(arm, value[0], revealed)
                revealed[arm] = value
        expected_counts = [0, 0, 0]
        for question_samples in samples.values():
            for arm in question_samples:
                for neighbor in sweep._hamming_neighbor_tuple(arm, 27):
                    if neighbor > arm and neighbor in question_samples:
                        slot = sweep._changed_slot(arm, neighbor, 27)
                        if slot is not None:
                            expected_counts[slot] += 1
        self.assertEqual(cached.counts, expected_counts)
        for got, want in zip(cached.weights(), expected):
            self.assertAlmostEqual(got, want, places=12)

    def test_similarity_vector_batch_matches_scalar_prediction(self):
        rng = random.Random(52)
        samples = {3: {arm: (rng.random(), 1.0) for arm in rng.sample(range(27), 11)}}
        slot_weights = (0.7, 1.3, 2.0)
        batch = sweep._SimilarityPredictions(27).predict(
            [0, 1, 3, 8, 26], 3, samples, 1.0, slot_weights, 0.5,
        )
        for arm, got in zip([0, 1, 3, 8, 26], batch):
            want = sweep._weighted_prediction(arm, 3, samples, 27, 1.0, slot_weights, 0.5)
            for value, expected in zip(got, want):
                self.assertAlmostEqual(value, expected, places=12)

    def test_one_row_budget_needs_no_posterior(self):
        with patch.object(sweep, "_CategoricalPosterior", side_effect=AssertionError("unnecessary posterior")):
            observed, seen = {}, set()
            sweep._bayesian_opt(
                0.01, 2, 2, random.Random(0), [[0, 1], [1, 0]],
                [[1, 1], [2, 2]], observed, seen,
            )
        self.assertEqual(len(observed), 1)
        self.assertEqual(len(seen), 2)

    def test_exact_score_ties_keep_lower_index(self):
        with patch.object(sweep._CategoricalPosterior, "score", return_value=0.5):
            observed, seen = {}, set()
            sweep._bayesian_opt(
                1.0, 8, 1, random.Random(91), [[0.5]] * 8,
                [[1.0]] * 8, observed, seen,
            )
        self.assertEqual(list(observed)[1:], sorted(list(observed)[1:]))


if __name__ == "__main__":
    unittest.main()
