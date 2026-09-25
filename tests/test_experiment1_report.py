import tempfile
import unittest
from pathlib import Path

from retry_search.experiment1_report import aggregate_runs, render_markdown, write_csv


class Experiment1ReportTests(unittest.TestCase):
    def test_aggregates_seed_results_and_savings(self):
        runs = [
            {"algorithm": "random", "parameter_name": "fraction", "parameter_value": 0.1,
             "heldout_accuracy": 0.4, "search_evaluations": 4, "search_cost": 2.0},
            {"algorithm": "random", "parameter_name": "fraction", "parameter_value": 0.1,
             "heldout_accuracy": 0.6, "search_evaluations": 6, "search_cost": 4.0},
        ]
        rows = aggregate_runs(runs, exhaustive_search_cost=8.0)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["repeats"], 2)
        self.assertAlmostEqual(rows[0]["mean_accuracy"], 0.5)
        self.assertAlmostEqual(rows[0]["mean_evaluations"], 5.0)
        self.assertAlmostEqual(rows[0]["cost_savings"], 0.625)
        self.assertIn("Mean Acc.", render_markdown(rows))

    def test_csv_is_written(self):
        runs = [{"algorithm": "u", "parameter_name": "fraction", "parameter_value": 1,
                 "heldout_accuracy": 0.5, "search_evaluations": 1, "search_cost": 1.0}]
        rows = aggregate_runs(runs, exhaustive_search_cost=1.0)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "table.csv"
            write_csv(rows, path)
            self.assertTrue(path.exists())
            self.assertIn("mean_accuracy", path.read_text())


if __name__ == "__main__":
    unittest.main()
