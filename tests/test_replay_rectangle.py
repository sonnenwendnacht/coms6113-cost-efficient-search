import importlib.util
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts/replay_experiment1_nine_model.py"
SPEC = importlib.util.spec_from_file_location("replay_experiment1_nine_model", SCRIPT)
assert SPEC and SPEC.loader
REPLAY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(REPLAY)


class ReplayRectangleTests(unittest.TestCase):
    def rows(self):
        configs = ["small/medium/large", "large/medium/small"]
        return [
            {"config_id": config, "question_id": question,
             "final_correct": 0, "cost_usd": 1.0}
            for config in configs for question in range(4)
        ]

    def test_complete_rectangle_is_accepted_and_split_is_disjoint(self):
        configs, search, evaluation = REPLAY.validate_trace_rectangle(
            self.rows(), {"rows": 2}, search_n=2, evaluation_n=2
        )
        self.assertEqual(configs, ["large/medium/small", "small/medium/large"])
        self.assertEqual(len(search), 4)
        self.assertEqual(len(evaluation), 4)
        self.assertEqual({row["question_id"] for row in search}, {0, 1})
        self.assertEqual({row["question_id"] for row in evaluation}, {2, 3})

    def test_equal_length_duplicate_cell_is_rejected(self):
        rows = self.rows()
        rows[-1]["question_id"] = 2  # duplicate one config/question, missing q=3
        with self.assertRaisesRegex(ValueError, "duplicate trace cell"):
            REPLAY.validate_trace_rectangle(rows, {"rows": 2}, search_n=2, evaluation_n=2)

    def test_missing_cell_is_rejected_even_when_counts_match(self):
        rows = self.rows()
        rows[-1]["config_id"] = rows[3]["config_id"]  # duplicate row identity leaves another cell missing
        with self.assertRaisesRegex(ValueError, "duplicate trace cell"):
            REPLAY.validate_trace_rectangle(rows, {"rows": 2}, search_n=2, evaluation_n=2)

    def test_search_and_evaluation_cannot_leak_across_declared_split(self):
        rows = self.rows()
        # Replace a search question with an out-of-split id.  The full
        # rectangle check catches the missing search cell before replay.
        rows[0]["question_id"] = 4
        with self.assertRaises(ValueError):
            REPLAY.validate_trace_rectangle(rows, {"rows": 2}, search_n=2, evaluation_n=2)

    def test_metadata_row_count_is_checked(self):
        with self.assertRaisesRegex(ValueError, "metadata declares"):
            REPLAY.validate_trace_rectangle(self.rows(), {"rows": 3}, search_n=2, evaluation_n=2)

    def test_slash_config_ids_produce_explicit_slots(self):
        ids = ["qwen-1/qwen-2/qwen-3", "qwen-3/qwen-2/qwen-1", "qwen-1/qwen-2/qwen-1"]
        slots = REPLAY.row_slots_from_config_ids(ids)
        self.assertEqual(len(slots), len(ids))
        self.assertEqual(len(set(slots)), len(ids))
        # First and second rows differ in exactly two slots; first and third
        # differ in one.  The returned tuples retain that geometry.
        self.assertEqual(sum(a != b for a, b in zip(slots[0], slots[2])), 1)
        self.assertEqual(sum(a != b for a, b in zip(slots[0], slots[1])), 2)


if __name__ == "__main__":
    unittest.main()
