"""An invented example, not an empirical result. No network or model calls."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from retry_search.replay import Outcome, Replay


def main():
    runner = Replay(
        {
            ("q1", ("cheap",)): Outcome(False, False, 2),
            ("q1", ("cheap", "strong")): Outcome(True, True, 7),
            ("q1", ("cheap", "medium")): Outcome(True, True, 4),
        },
        context_id="synthetic-demo-v1-repetition-0",
        budget_units=20,
    )
    output = {"synthetic_only": True, "unit": "invented cost units", "runs": []}
    for models in [("cheap", "strong"), ("cheap", "medium")]:
        result = runner.evaluate("q1", models)
        output["runs"].append({
            "models": models,
            "completed": result.completed,
            "correct": result.final_correct,
            "new_search_spend": result.search_spend_units,
            "cold_execution_cost": result.cold_execution_cost_units,
            "reused_attempts": sum(a.reused for a in result.attempts),
        })
    output["total_search_spend"] = runner.spent_units
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
