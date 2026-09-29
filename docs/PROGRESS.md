# Resumable checkpoint

Updated: 2026-09-29 19:00 ET (research-only window resumed; no experiments launched).

## Research branch

- Algorithm branch: `research/algorithm2-sequential-comparison`.
- Main experiment branch: `research/experiment1-nine-models`.
- The algorithm branch contains CW-PLR, CACR, and the gated SCCR prototype,
  synthetic iid/smooth/permuted controls, the pilot trace-locality diagnostic,
  and the expanded related-work boundary. The latest pushed algorithm commit
  is `44848d4`; source-audit commits after it add notes 19--39.
- Run `python -m unittest discover -s tests -q` for the current offline test
  suite (38 tests).

## Research-only window

- Through 2026-09-29 18:40 ET, no new experiments, replays, tests, or model/API
  calls were launched. The existing long trace was left untouched.
- Source-audited notes now cover the validity limits of paired similarity,
  cost/reward dependence, robust structured pure exploration, categorical BO
  prior art, and a concrete falsification plan. The synthesis is in
  `docs/research/deep-review/11-research-synthesis-2026-09-29.md`.
- The mentor-paper audit is in
  `docs/research/deep-review/12-mentor-gittinseval-audit-2026-09-29.md`; it
  records GittinsEval's Gaussian independent-arm assumptions and the exact
  retry-row differences that require a separate baseline or reduction.
- A candidate theory formulation for combining same-question covariance with
  outcome-dependent complete-row charges is in
  `docs/research/deep-review/13-correlated-resource-bai-theory-2026-09-29.md`.
- The constrained-BAI overlap audit is in
  `docs/research/deep-review/14-constrained-bai-audit-2026-09-29.md`; it rules
  out outcome-dependent cost alone as the novelty claim.
- Note 15 corrects cost-feasibility directions, optional-stopping claims, and
  the distinction between checker control and offline `final_correct` search
  reward. Note 16 gives one coherent structured correlated-KG candidate with
  217 categorical features, a residual, top-two pairing, and a cost model.
- Notes 17--32 audit covariance-adaptive stopping, cost-aware KG/Pandora,
  hierarchical and transfer BAI, generative proxies, spectral graph BAI,
  common-random-number ranking, contextual BAI, finite-population confidence
  sequences, offline-evidence bias, paired-racing and hub-anchor designs,
  verified retry-cost semantics, hub break-even/stream accounting, and a
  complete-row hub-anchored Algorithm 2 protocol, and hard-cap reservation
  bounds. They narrow the defensible claim to
  complete retry-row observations with same-question covariance and realized
  path cost; generic similarity, KG-per-cost, paired elimination, and silent
  switching between fixed-set and population targets are prior art or protocol
  errors.
- Note 33 audits the replay contract: the current full trace supports a
  leak-free counterfactual selector benchmark, but not a live shared-hub
  ledger, strict equal-dollar caps, registered question streams, or direct
  final confirmation for surrogate-row selectors.
- Note 34 specifies the next ledger-backed hub oracle: registered question
  streams, explicit initial cache, hard/soft reservation semantics, direct
  confirmation, and separate search versus audit fields.
- Note 35 requires a cached-incumbent baseline before claiming that a shared
  hub saves calls; fresh-comparator reuse is only a diagnostic.
- Note 36 audits three new 2026 papers on cost-aware multi-objective LLM
  configuration search, cost-aware LLM dueling, and budgeted multi-attribute
  verification. They narrow the claim to shared-question, complete-row,
  path-dependent retry charges.
- Note 37 audits contextual-dueling overlap. Contextual or graph structure,
  paired comparisons, and cost-aware allocation are established components;
  any claim must require the complete retry-row arm, answer-key-blind
  solver/verifier coupling, endogenous early stopping, and a matched
  cached-incumbent comparison.
- Note 38 audits structured BAI and feedback-graph overlap. A hub is a
  same-question covariate/control variate, not free side feedback about an
  unpulled candidate; direct candidate observations and final confirmation
  remain required.
- Note 39 audits adaptive generate-rank-verify. Within-question generation
  versus verification allocation is established; the remaining boundary is
  outer identification of one complete retry row with endogenous path charge
  and a shared-row ledger.
- The latest main-branch documentation checkpoints are `c4a9a60` and
  `f5fe2da`; the algorithm branch is included in PR #4.
- The current Algorithm 2 checkpoint is pushed on
  `research/algorithm2-sequential-comparison` and is included in PR #4.

## Long local trace

- Run ID: `exp1-nine-local-20260927-proper`.
- Status observed at 2026-09-29 22:39 UTC: `237,400 / 291,600` cells
  (`81.41%`), still running in PID `8763`.
- Status file: `results/runs/exp1-nine-local-20260927-proper/status.json`.
- The runner writes resumable JSONL checkpoints. If the machine is restarted,
  resume with the same command and add `--resume --run-id
  exp1-nine-local-20260927-proper`; do not start a second run with the same
  output directory.
- This run is not complete and has not produced a nine-model result. The
  small 27-row pilot remains descriptive only.

## Next research gate

When the nine-model trace completes, run every selector only on the search
questions, enforce equal realized profiling dollars, and evaluate the chosen
complete row on the untouched audit questions. Report search spend, held-out
accuracy, cold deployment cost, and uncertainty separately. Compare CACR/SCCR
with AgentOpt selectors, synchronized paired elimination, random/uniform
allocation, direct cost-aware allocation, and the hybrid-feedback baseline.

The replay command now accepts `--include-structured` to add CW-PLR, CACR,
and SCCR at explicit realized-cost fractions. It has been smoke-tested on the
completed 27-row pilot via a local fixture; the 729-row run remains pending.
Replay validates the full config/question rectangle and decodes explicit
slash-separated retry slots before any structured selector sees a cell.
