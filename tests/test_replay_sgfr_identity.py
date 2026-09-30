import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
_SPEC = importlib.util.spec_from_file_location(
    "replay_sgfr_trace_for_identity_test", ROOT / "scripts" / "replay_sgfr_trace.py"
)
_MODULE = importlib.util.module_from_spec(_SPEC)
assert _SPEC.loader is not None
_SPEC.loader.exec_module(_MODULE)


class ReplaySgfrIdentityTests(unittest.TestCase):
    def test_resume_identity_changes_when_sgfr_source_changes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            trace = root / "trace"
            trace.mkdir()
            (trace / "traces.json").write_text("[]\n")
            (trace / "metadata.json").write_text("{}\n")
            source = root / "slot_gated_factorial_racing.py"
            source.write_text("version = 1\n")
            old_identity = _MODULE.replay_identity(trace, "final_correct", sgfr_source=source)
            source.write_text("version = 2\n")
            new_identity = _MODULE.replay_identity(trace, "final_correct", sgfr_source=source)
            self.assertNotEqual(old_identity["sgfr_source_sha256"],
                                new_identity["sgfr_source_sha256"])
            self.assertNotEqual(old_identity, new_identity)
            with self.assertRaises(SystemExit):
                _MODULE.validate_replay_identity(old_identity, new_identity)


if __name__ == "__main__":
    unittest.main()
