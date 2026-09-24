# Project status

Updated: 2026-09-23. This file distinguishes setup from research progress.

## Completed locally

- Read both supplied shared-document screenshots and the mentor's whiteboard photograph. Recorded provenance and uncertain handwriting; originals are unchanged.
- Established the project structure, collaboration guide, shared Codex/Claude instructions, task list, and experiment-record template.
- Downloaded 22 primary-source PDFs, including the three central readings, related evaluation work, hyperparameter-search foundations, seven additional theory papers, and FlowCompile. The catalog pins sources and checksums. Document-listed papers retain the titles requested by the owner; reading depth is recorded separately from download status.
- Added a deterministic, invented-data retry accounting scaffold. Seven tests cover failed-attempt costs, early stopping, exact-prefix reuse, cold deployment cost, incomplete runs, and checker/ground-truth separation.
- Research notes distinguish established prior work, proposed hypotheses, fair evaluation, and unresolved group choices.
- Completed a [detailed research assessment](research/deep-review/README.md): full GittinsEval/AgentOpt/VineLM reading including appendices, selected SySRs and broader theory review, and three pinned public code audits. Recorded reproduction questions without claiming a completed reproduction or judging historical results from current code.
- Derived and independently assistant-reviewed reach-conditioned comparisons, partial-execution family bounds, valid adaptive-revelation intervals, two-phase estimators, feasibility rules, and a conservative whole-space regret certificate. These are analysis under explicit assumptions, not a new theorem/novelty claim.
- Ran nine exact diagnostics on invented populations, with a checked-in reproducible summary. Added a pilot protocol that compares allocation methods under equal actual spending and identical reuse access.
- Local verification passed: seven accounting tests, the smoke demo, all nine diagnostic calculations and artifact comparison, all 22 PDF checksums, manifest validation, local Markdown links, and Git whitespace checks. No paid calls were made.

## GitHub

Public repository: <https://github.com/sonnenwendnacht/coms6113-cost-efficient-search>. Visibility was changed at the owner's explicit request during setup.

Owner authentication verified as `sonnenwendnacht`; SSH is configured. Squash merging and automatic deletion of merged branches are enabled. Alternate merge styles and the wiki are disabled to keep the workflow consistent.

The initial commit `9fe292c` was uploaded to `main`; [GitHub's automatic checks passed](https://github.com/sonnenwendnacht/coms6113-cost-efficient-search/actions/runs/35943843084). The detailed assessment and subsequent reading catalog changes are on `research/structure-aware-search` for review; they are not an approved group research decision.

**Branch protection is enabled on `main`.** GitHub requires one approving review, passing `offline-checks`, an up-to-date branch, and resolved review conversations. Stale approvals are dismissed, linear history is required, and force pushes/deletion are disabled. The owner retains administrator override for setup and recovery. Protection became available after the requested switch to public visibility; no account upgrade was needed.

Teammate usernames have not been supplied, so no collaborator invitations have been sent.

## Not yet implemented or established

- No live model calls, paid experiments, benchmark data, or empirical research findings.
- No completed reproduction of GittinsEval, AgentOpt, VineLM, or another baseline.
- No implementation of the proposed structure-aware search algorithm, real checkpoint engine, live budget manager, latency measurement, or full experiment runner.
- No claim of novelty, superiority, or publication readiness. The first pilot must test whether the proposed structural advantage survives strong baselines and fair cost accounting.
- Full live shared-document access was not obtained; the screenshots are a partial view.

## Next decisions

Confirm teammate access, select one benchmark/workflow and a deployable retry checker, choose exact model versions, set a spending limit, and agree on the primary objective and practical quality tolerance. See [TASKS.md](TASKS.md), the [assessment](research/deep-review/README.md), and the [pilot protocol](research/deep-review/05-diagnostics-and-pilot.md).
