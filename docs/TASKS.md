# Initial work plan

No teammate has been assigned work without their agreement. Claim a task in an issue and record the branch before implementation.

| ID | Task | Completion evidence | Owner/status |
| --- | --- | --- | --- |
| T1 | Reproduce a small GittinsEval result | Exact upstream revision, settings, cost assumption, and reproduced plot | Unclaimed |
| T2 | Inspect AgentOpt/VineLM execution interfaces | Minimal documented checkpoint trace; verified reuse conditions | Unclaimed |
| T3 | Select one workflow and retry checker | Checker usable without gold answers; versioned task split | Group decision |
| T4 | Test the structure hypothesis | Paired outcomes by differing stage, reach frequency, difficulty; failures included | Unclaimed |
| T5 | Implement random and uniform allocation baselines | Equal-dollar runs with the same cache and recommendation rule | Unclaimed |
| T6 | Implement a structure-aware candidate method | Explicit uncertainty model, exploration floor, and no gold leakage | After T4 |
| T7 | Run small exhaustive reference | Search cannot access hidden cells; reference construction spending reported | After T3/T5 |
| T8 | Run sparse live comparison and audit | Preregistered budgets, multiple seeds, fresh paired held-out evaluation | After pilot and budget choice |
| R1 | Deep source/code audit and formal research assessment | [Assessment](research/deep-review/README.md), pinned code evidence, independently checked derivations, nine exact diagnostics, and pilot protocol | Codex; `research/structure-aware-search`; completed for team review; not an empirical result |

Repository setup, primary reading downloads, a research proposal, and accounting smoke checks are handled in the initial setup. These tasks are research work to do next, not claimed completed experiments.
