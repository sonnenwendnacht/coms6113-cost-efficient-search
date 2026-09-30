import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts/replay_experiment1_nine_model.py"
SPEC = importlib.util.spec_from_file_location("checkpoint_replay", SCRIPT)
REPLAY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(REPLAY)


class SelectorCheckpointTests(unittest.TestCase):
    def test_resume_retains_complete_result_and_discards_only_torn_write(self):
        record = {"algorithm": "random", "parameter_name": "fraction",
                  "parameter_value": 0.1, "seed": 6113,
                  "selected_config_id": "a/b/c", "search_cost": 1.0}
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "checkpoint.jsonl"
            REPLAY.append_completed_run(path, record)
            committed = path.read_bytes()
            with path.open("ab") as handle:
                handle.write(b'{"algorithm": "unfinished"')
            loaded = REPLAY.load_completed_runs(path)
            self.assertEqual(list(loaded.values()), [record])
            self.assertEqual(path.read_bytes(), committed)

    def test_duplicate_complete_results_fail_closed(self):
        record = {"algorithm": "random", "parameter_name": "fraction",
                  "parameter_value": 0.1, "seed": 6113}
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "checkpoint.jsonl"
            path.write_text((json.dumps(record) + "\n") * 2)
            with self.assertRaisesRegex(ValueError, "duplicate checkpoint"):
                REPLAY.load_completed_runs(path)

    def test_complete_invalid_json_is_not_silently_discarded(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "checkpoint.jsonl"
            path.write_text('{"broken":\n')
            with self.assertRaises(json.JSONDecodeError):
                REPLAY.load_completed_runs(path)


if __name__ == "__main__":
    unittest.main()
