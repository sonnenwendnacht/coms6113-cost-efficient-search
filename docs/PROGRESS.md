# Resumable checkpoint

Updated: 2026-09-29 19:00 ET.

## Research branch

- Algorithm branch: `research/algorithm2-sequential-comparison`.
- Main experiment branch: `research/experiment1-nine-models`.
- The algorithm branch contains CW-PLR, CACR, and the gated SCCR prototype,
  synthetic iid/smooth/permuted controls, the pilot trace-locality diagnostic,
  and the expanded related-work boundary. The latest pushed algorithm commit
  is checked by the repository's offline CI. Research note 33 audits the
  replay contract: the current full trace supports leak-free counterfactual
  selector comparison, but not a live shared-hub ledger or strict equal-dollar
  caps.
- Run `python -m unittest discover -s tests -q` for the current offline test
  suite (38 tests).

## Long local trace

- Run ID: `exp1-nine-local-20260927-proper`.
- Status observed at this checkpoint: `84,100 / 291,600` cells (`28.84%`),
  still running in PID `8763`.
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

## Research-only audit checkpoint

- No new generation, selector replay, tests, or model/API calls were launched
  during the 2026-09-29 review window.
- The next implementation gate is an isolated ledger-backed oracle with a
  registered question-stream manifest, explicit initial cache, reservation
  accounting, and separate search/confirmation/audit charges. Until that
  exists, replay costs must be described as counterfactual search costs.
