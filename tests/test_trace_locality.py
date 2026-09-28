import json
import tempfile
import unittest
from pathlib import Path

from scripts.diagnose_trace_locality import diagnose


class TraceLocalityTests(unittest.TestCase):
    def test_groups_pairs_by_explicit_model_slots(self):
        with tempfile.TemporaryDirectory() as directory:
            run_dir = Path(directory)
            traces = []
            for config_id, values in {
                "a/b": [1, 1, 0],
                "a/c": [1, 0, 0],
                "c/c": [0, 0, 0],
            }.items():
                for question_id, final_correct in enumerate(values):
                    traces.append(
                        {
                            "config_id": config_id,
                            "question_id": question_id,
                            "final_correct": final_correct,
                        }
                    )
            (run_dir / "traces.json").write_text(json.dumps(traces))
            result = diagnose(run_dir)
            self.assertEqual(result["rows"], 3)
            self.assertIn("1", result["by_hamming_distance"])
            self.assertIn("2", result["by_hamming_distance"])


if __name__ == "__main__":
    unittest.main()
