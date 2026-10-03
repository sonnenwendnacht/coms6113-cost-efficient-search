import csv
import json
import math
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from retry_search.experiment1_report import aggregate_runs, render_markdown, write_csv, write_report


class Experiment1ReportTests(unittest.TestCase):
    @staticmethod
    def run_record(**updates):
        record = {
            "algorithm": "random", "parameter_name": "fraction", "parameter_value": 0.1,
            "budget_basis": "row_fraction", "seed": 4, "selected_config_id": "a/b/c",
            "heldout_accuracy": 0.5, "search_evaluations": 4, "search_cost": 2.0,
            "selection_time_seconds": 0.2, "heldout_mean_cost": 0.3,
        }
        record.update(updates)
        return record

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

    def test_preserves_budget_bases_instead_of_merging_distinct_settings(self):
        runs = [self.run_record(), self.run_record(budget_basis="cell_fraction")]
        rows = aggregate_runs(runs, exhaustive_search_cost=8)
        self.assertEqual(len(rows), 2)
        self.assertEqual({row["budget_basis"] for row in rows}, {"row_fraction", "cell_fraction"})
        table = render_markdown(rows)
        self.assertIn("row_fraction", table)
        self.assertIn("cell_fraction", table)

    def test_sample_sd_runtime_and_deployment_cost_are_separate(self):
        runs = [self.run_record(), self.run_record(
            seed=5, selected_config_id="c/b/a", heldout_accuracy=0.7,
            search_cost=6, search_evaluations=8, selection_time_seconds=0.6,
            heldout_mean_cost=0.5,
        )]
        row = aggregate_runs(runs, exhaustive_search_cost=10)[0]
        self.assertAlmostEqual(row["std_accuracy"], math.sqrt(0.02))
        self.assertAlmostEqual(row["std_evaluations"], math.sqrt(8))
        self.assertAlmostEqual(row["std_search_cost"], math.sqrt(8))
        self.assertAlmostEqual(row["mean_selection_time_seconds"], 0.4)
        self.assertAlmostEqual(row["mean_heldout_cost"], 0.4)
        self.assertAlmostEqual(row["cost_savings"], 0.6)
        self.assertEqual(row["selection_time_count"], 2)
        self.assertEqual(row["heldout_cost_count"], 2)

    def test_no_recommendation_retains_spending_and_exposes_denominator(self):
        runs = [self.run_record(), self.run_record(
            seed=5, selected_config_id=None, heldout_accuracy=None,
            heldout_mean_cost=None, search_cost=1, search_evaluations=2,
        )]
        row = aggregate_runs(runs, exhaustive_search_cost=8)[0]
        self.assertEqual(row["repeats"], 2)
        self.assertEqual(row["recommendation_count"], 1)
        self.assertEqual(row["no_recommendation_count"], 1)
        self.assertEqual(row["no_recommendation_rate"], 0.5)
        self.assertEqual(row["mean_accuracy"], 0.5)
        self.assertEqual(row["mean_search_cost"], 1.5)
        self.assertEqual(row["mean_evaluations"], 3)
        empty_row = aggregate_runs(runs[1:], exhaustive_search_cost=8)[0]
        self.assertIsNone(empty_row["mean_accuracy"])
        self.assertIsNone(empty_row["std_accuracy"])
        self.assertIn("1/1", render_markdown([empty_row]))
        missing_label = dict(runs[1])
        del missing_label["heldout_accuracy"]
        self.assertIsNone(aggregate_runs([missing_label], exhaustive_search_cost=8)[0]["mean_accuracy"])

    def test_rejects_accuracy_without_recommendation_and_nonfinite_cost(self):
        for record in (self.run_record(selected_config_id=None), self.run_record(search_cost=float("nan"))):
            with self.subTest(record=record), self.assertRaises(ValueError):
                aggregate_runs([record], exhaustive_search_cost=8)

    def test_csv_is_written(self):
        runs = [{"algorithm": "u", "parameter_name": "fraction", "parameter_value": 1,
                 "heldout_accuracy": 0.5, "search_evaluations": 1, "search_cost": 1.0}]
        rows = aggregate_runs(runs, exhaustive_search_cost=1.0)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "table.csv"
            write_csv(rows, path)
            self.assertTrue(path.exists())
            self.assertIn("mean_accuracy", path.read_text())

    def test_report_reference_counts_search_cells_and_preserves_full_run(self):
        runs = [self.run_record()]
        metadata = {
            "search_n": 200, "evaluation_n": 200, "configs": 729,
            "selector_reward": "final_correct", "exhaustive_reference_config": "z/z/z",
            "exhaustive_reference_heldout_mean_cost": 0.7,
        }
        # Exercise report serialization without importing any GUI dependency.
        with tempfile.TemporaryDirectory() as tmp, patch("retry_search.experiment1_report.render_plot") as plot:
            paths = write_report(runs, 16, tmp, metadata=metadata, exhaustive_accuracy=0.75)
            payload = json.loads(Path(paths["json"]).read_text())
            reference = payload["rows"][0]
            self.assertTrue(reference["is_reference"])
            self.assertEqual(reference["mean_evaluations"], 145800)
            self.assertEqual(reference["mean_accuracy"], 0.75)
            self.assertEqual(reference["mean_search_cost"], 16)
            self.assertEqual(reference["cost_savings"], 0)
            self.assertEqual(reference["mean_heldout_cost"], 0.7)
            self.assertEqual(reference["selected_config_id"], "z/z/z")
            per_run = json.loads(Path(paths["runs_json"]).read_text())
            self.assertEqual(per_run["runs"], runs)
            self.assertEqual(per_run["metadata"], metadata)
            self.assertEqual(payload["scenario"], "Gold-labeled offline profiling")
            self.assertNotIn("oracle", " ".join(payload["notes"]).lower())
            self.assertIn("not a confidence interval", payload["standard_deviation_basis"])
            with Path(paths["csv"]).open(newline="") as handle:
                csv_rows = list(csv.DictReader(handle))
            self.assertEqual(csv_rows[0]["mean_evaluations"], "145800")
            self.assertEqual(csv_rows[1]["budget_basis"], "row_fraction")
            self.assertEqual(plot.call_count, 3)
            self.assertEqual({call.args[1].suffix for call in plot.call_args_list}, {".png", ".pdf", ".svg"})

    def test_label_free_report_identifies_proxy_objective(self):
        with tempfile.TemporaryDirectory() as tmp, patch("retry_search.experiment1_report.render_plot"):
            paths = write_report([self.run_record()], 8, tmp, metadata={"selector_reward": "verifier_pass"})
            text = Path(paths["markdown"]).read_text()
            self.assertIn("Verifier-proxy search", text)
            self.assertIn("separate label-free search scenario", text)
            self.assertIn("does not imply optimizing gold correctness", text)

    def test_reference_does_not_guess_evaluation_count_without_metadata(self):
        with tempfile.TemporaryDirectory() as tmp, patch("retry_search.experiment1_report.render_plot"):
            paths = write_report([self.run_record()], 8, tmp)
            reference = json.loads(Path(paths["json"]).read_text())["rows"][0]
            self.assertIsNone(reference["mean_evaluations"])
            self.assertIsNone(reference["mean_accuracy"])


if __name__ == "__main__":
    unittest.main()
