# Current update (2026-09-30)

- The complete local nine-model trace is `exp1-nine-local-20260927-proper`: 729 rows, 200 search questions, and 200 disjoint audit questions (291,600 cells). It is a fixed local proxy trace, not an API result.
- Gold-labeled selector replay is under `results/runs/exp1-nine-local-20260930/full-gold/`; verifier-proxy replay is under `.../proxy-similarity/`. The gold graph-residual high-budget settings are partial and clearly marked in the research note.
- The first SGFR curves are withdrawn as evidence: source audit found an empty racing phase and same-block residuals that reduce to direct candidate means. The old files remain preserved as exploratory row-sampling artifacts. The corrected next candidate is CRPR, specified in [deep-review note 147](research/deep-review/147-corrected-cross-fitted-racing-design-2026-09-30.md), but it has not been implemented or run.
- The latest offline suite has 72 passing tests. Replay identities now bind the trace, reward, runner, SGFR source, seed list, and budget grid, so a changed implementation cannot silently resume an old checkpoint. No API calls or purchases were made.
- Current interpretation and limits: [deep-review note 143](research/deep-review/143-exp1-results-and-algorithm2-next-step-2026-09-30.md), [prior-art boundary note 144](research/deep-review/144-sgfr-prior-art-and-falsification-2026-09-30.md), [withdrawal/design note 146](research/deep-review/146-withdraw-sgfr-curve-and-freeze-e2-2026-09-30.md), [CRPR note 147](research/deep-review/147-corrected-cross-fitted-racing-design-2026-09-30.md), and [Experiment 2 protocol](../experiments/experiment2-sgfr.md).

# Project status

Updated: 2026-09-28. This file distinguishes setup from research progress.

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
- Completed the first local Experiment 1 pilot on MathQA: 27 ordered solver rows (three Qwen tiers, three attempts including two retries), a fixed answer-key-blind verifier, 20 search questions, 10 independent audit questions, 810 workflow traces, and six equal-realized-cost replay policies. The reviewed summary is [experiment1-local-20260924.json](../results/experiment1-local-20260924.json); raw traces remain ignored under `results/runs/`.
- Every solver and verifier call in that pilot was charged as `coefficient_model * input_tokens`; output tokens, latency, and cache discounts were excluded. The coefficients are local proxy values, and no provider/API run was performed because no endpoint credentials were configured.
- Added a candidate Algorithm 2, [adaptive similarity-annealed UCB](research/algorithm2-similarity-search.md). It treats complete ordered retry rows as nodes in a Hamming graph, transfers only same-question observations, learns which retry slots are safe to compare, and uses a cooling exploration policy. A 20-seed synthetic smooth-landscape check favored it over the included random and kernel-BO baselines; this is a sanity check, not MathQA evidence.
- Added a corrected [graph-residual cost-aware racing candidate](research/algorithm2-graph-residual.md). It measures neighboring complete rows on shared questions and estimates row differences through paired residuals. On the same synthetic landscape it reached mean latent reward `0.654` at a 10% cell fraction, below the exploratory kernel prototype's `0.862`; this negative result is preserved as a warning that the anchor and residual allocation need further work.
- Audited the closest similarity prior, SySRs, and recorded the stronger Algorithm 2 research direction in [QPG-TS](research/qpg-track-and-stop.md): a cost-weighted, graph-constrained successive-rejection design for complete retry rows with realized cascade costs. Same-question pairing and similarity alone are explicitly excluded as novelty claims; the proposed extension remains a hypothesis until it is compared with SySRs and direct-cost baselines.
- A follow-up audit found that graph paths have no automatic variance advantage over a direct paired endpoint comparison, and that ParamILS/FocusedILS already combine one-change local moves with same-instance racing. The current research direction is therefore a narrower **Cost-Weighted Pairwise Local Racing** candidate, with a synchronized cost-aware SySRs procedure as the safer baseline. The graph-path prototype remains a negative allocation ablation.
- Added a gated **Safe Cost-aware Correlated Racing (SCCR)** prototype. It calibrates each proposed edge on a fixed question block, uses paired uncertainty only when an empirical variance-reduction margin passes, and falls back to direct row uncertainty with global restarts otherwise. Its synthetic iid control is noise-level, while its smooth score is below ungated CACR; this is a safety ablation, not a superiority result.
- Added resumable JSONL checkpoints to the nine-model local runner. The earlier `exp1-nine-local-20260927` attempt ended after partial model work without a usable trace; it is not reported as a completed experiment. Future runs can resume with `--resume --run-id ...`.

## GitHub

Public repository: <https://github.com/sonnenwendnacht/coms6113-cost-efficient-search>. Visibility was changed at the owner's explicit request during setup.

Owner authentication verified as `sonnenwendnacht`; SSH is configured. Squash merging and automatic deletion of merged branches are enabled. Alternate merge styles and the wiki are disabled to keep the workflow consistent.

The initial commit `9fe292c` was uploaded to `main`; [GitHub's automatic checks passed](https://github.com/sonnenwendnacht/coms6113-cost-efficient-search/actions/runs/35943843084). The detailed assessment and subsequent reading catalog changes are on `research/structure-aware-search` for review; they are not an approved group research decision.

**Branch protection is enabled on `main`.** GitHub requires one approving review, passing `offline-checks`, an up-to-date branch, and resolved review conversations. Stale approvals are dismissed, linear history is required, and force pushes/deletion are disabled. The owner retains administrator override for setup and recovery. Protection became available after the requested switch to public visibility; no account upgrade was needed.

Teammate usernames have not been supplied, so no collaborator invitations have been sent.

## Not yet implemented or established

- No provider/API calls or publication-level empirical findings. The local proxy pilot is an engineering result, not evidence of provider pricing or statistical superiority.
- No completed reproduction of GittinsEval, AgentOpt, VineLM, or another baseline.
- No production budget manager or latency objective. Algorithm 2 is an experimental candidate only; its full nine-model MathQA comparison and ablations remain to be run. Experiment 1's local runner and replay policies are still a baseline/pilot implementation.
- No claim of novelty, superiority, or publication readiness. The first pilot must test whether the proposed structural advantage survives strong baselines and fair cost accounting.
- Full live shared-document access was not obtained; the screenshots are a partial view.

## Next decisions

Confirm teammate access, choose exact API model versions and a spending limit, inspect the pilot's weak verifier, and agree on the next held-out test run. See [TASKS.md](TASKS.md), the [assessment](research/deep-review/README.md), and [Experiment 1](../experiments/experiment1.md).
