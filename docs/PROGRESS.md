# Resumable checkpoint

Updated: 2026-09-29 15:38 ET (research-only window complete).

## Research branch

- Algorithm branch: `research/algorithm2-sequential-comparison`.
- Main experiment branch: `research/experiment1-nine-models`.
- The algorithm branch contains CW-PLR, CACR, and the gated SCCR prototype,
  synthetic iid/smooth/permuted controls, the pilot trace-locality diagnostic,
  and the expanded related-work boundary. The latest pushed algorithm commit
  is checked by the repository's offline CI.
- Run `python -m unittest discover -s tests -q` for the current offline test
  suite (38 tests).

## Research-only window

- Through 2026-09-29 11:00 ET, no new experiments, replays, tests, or model/API
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
- The current Algorithm 2 checkpoint is pushed as commit `0d2d7d4` on
  `research/algorithm2-sequential-comparison` and is included in PR #4.

## Long local trace

- Run ID: `exp1-nine-local-20260927-proper`.
- Status observed at 2026-09-29 00:58 UTC: `110,700 / 291,600` cells
  (`37.96%`), still running in PID `8763`.
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
