# Project status

Updated: 2026-09-23. This file distinguishes setup from research progress.

## Completed locally

- Read both supplied shared-document screenshots and the mentor's whiteboard photograph. Recorded provenance and uncertain handwriting; originals are unchanged.
- Established the project structure, collaboration guide, shared Codex/Claude instructions, task list, and experiment-record template.
- Downloaded 14 primary-source PDFs, including the three central readings, related evaluation work, hyperparameter-search foundations, and context papers from the screenshots. The catalog pins sources and checksums; context papers have not all been reviewed in depth.
- Added a deterministic, invented-data retry accounting scaffold. Seven tests cover failed-attempt costs, early stopping, exact-prefix reuse, cold deployment cost, incomplete runs, and checker/ground-truth separation.
- Research notes distinguish established prior work, proposed hypotheses, fair evaluation, and unresolved group choices.

## GitHub

Private repository: <https://github.com/sonnenwendnacht/coms6113-cost-efficient-search>.

Owner authentication verified as `sonnenwendnacht`; SSH is configured. Squash merging and automatic deletion of merged branches are enabled. Alternate merge styles and the wiki are disabled to keep the workflow consistent.

The initial commit `9fe292c` was uploaded to `main`; [GitHub's automatic checks passed](https://github.com/sonnenwendnacht/coms6113-cost-efficient-search/actions/runs/35943843084). Local tests, all 14 PDF checksums, manifest validation, and local document links also passed verification.

**Branch reviews are a team convention, not an enforced setting.** GitHub rejected the protection request with HTTP 403 because the current account plan does not support branch protection for this private repository. The repository remains private. Automatic checks run on pushes and pull requests but cannot block a merge without a supported protection rule. No account upgrade or visibility change was made.

Teammate usernames have not been supplied, so no collaborator invitations have been sent.

## Not yet implemented or established

- No live model calls, paid experiments, benchmark data, or empirical research findings.
- No completed reproduction of GittinsEval, AgentOpt, VineLM, or another baseline.
- No implementation of the proposed structure-aware search algorithm, real checkpoint engine, live budget manager, latency measurement, or full experiment runner.
- No claim of novelty, superiority, or publication readiness. The first pilot must test whether the proposed structural advantage survives strong baselines and fair cost accounting.
- Full live shared-document access was not obtained; the screenshots are a partial view.

## Next decisions

Confirm teammate access, select one benchmark/workflow and a deployable retry checker, choose exact model versions, set a spending limit, and agree on the primary quality/cost/latency objective. See [TASKS.md](TASKS.md) and the [research plan](research/research-plan.md).
