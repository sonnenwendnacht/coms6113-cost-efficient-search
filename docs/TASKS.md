# Initial work plan

No teammate has been assigned work without their agreement. Claim a task in an issue and record the branch before implementation.

| ID | Task | Completion evidence | Owner/status |
| --- | --- | --- | --- |
| T1 | Reproduce a small GittinsEval result | Exact upstream revision, settings, cost assumption, and reproduced plot | Unclaimed |
| T2 | Inspect AgentOpt/VineLM execution interfaces | Minimal documented checkpoint trace; verified reuse conditions | Unclaimed |
| T3 | Select one workflow and retry checker | Checker usable without gold answers; versioned task split | Group decision |
| T4 | Test the structure hypothesis | Paired outcomes by differing stage, reach frequency, difficulty; failures included | Unclaimed |
| T5 | Implement random and uniform allocation baselines | Equal-dollar runs with the same cache and recommendation rule | Codex; implemented in Experiment 1 replay; needs group review |
| T6 | Implement a structure-aware candidate method | Explicit uncertainty model, exploration floor, and no gold leakage | After T4 |
| T7 | Run small exhaustive reference | Search cannot access hidden cells; reference construction spending reported | Codex; 27-row local pilot complete; needs larger/held-out confirmation |
| T8 | Run sparse live comparison and audit | Preregistered budgets, multiple seeds, fresh paired held-out evaluation | Codex; local proxy pilot complete; API/test confirmation pending |
| R1 | Deep source/code audit and formal research assessment | [Assessment](research/deep-review/README.md), pinned code evidence, independently checked derivations, nine exact diagnostics, and pilot protocol | Codex; `research/structure-aware-search`; completed for team review; not an empirical result |
| R2 | Audit and simplify Algorithm 2 without prefix reuse | Check graph-path advantage, classical algorithm-configuration overlap, and paired local-search prototypes on preregistered synthetic matrices | Codex; `research/algorithm2-sequential-comparison`; CACR and gated SCCR prototypes, iid/permuted controls, and trace-locality diagnostic committed 2026-09-28; matched real-trace baseline still pending; active GPU run untouched |
| E1A | Analyze completed 729-row trace and publish reviewed tables/figures | Full rectangle validation, checkpointed selector seeds, separate search/audit accounting, verifier diagnostics and descriptive curves | Codex; `research/experiment1-nine-models`; active 2026-09-30; root owns replay and records, delegated worktrees own selector speedups, reporter and diagnostics |

Repository setup, primary reading downloads, a research proposal, and accounting smoke checks are handled in the initial setup. These tasks are research work to do next, not claimed completed experiments.
