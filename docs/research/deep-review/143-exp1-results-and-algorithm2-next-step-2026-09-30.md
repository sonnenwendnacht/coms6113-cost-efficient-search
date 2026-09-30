# Experiment 1 results and the next algorithm

Updated: 2026-09-30 14:36 ET

This note records what the completed fixed trace can support. It does not claim that the current heuristic is a publishable improvement.

## Trace and target

The run is `exp1-nine-local-20260927-proper`. It contains 729 retry rows (three slots, nine local models per slot) evaluated on 200 search questions and 200 disjoint audit questions: 291,600 row-question cells. A cell returns the answer-key-based `final_correct` label and the answer-key-blind verifier outcome. The model coefficient times input tokens is the cost; output tokens, cache effects, and latency are excluded. The reported dollar amounts are local proxy dollars, not invoices.

The execution trace is heavily first-attempt dominated: 284,553 workflows stop after the original attempt, 6,012 use one retry, and 1,035 use both retries. The verifier accepted 291,398/291,600 workflows. Among accepted workflows, the false-pass rate is about 77.33%. Consequently, this trace is useful for a fixed-trace selector benchmark, but it is not a strong test of retry-aware search.

The answer-key reference row selected by exhaustive search is `qwen2.5-7b/tinyllama-1.1b/tinyllama-1.1b`. It reaches 38.0% on the 200-question search split and 38.5% on the held-out 200-question audit split. Exhaustive search costs $8.20715 in the search proxy ledger and evaluates 145,800 search cells. The corresponding held-out deployment-path proxy cost is about $0.00010 for one selected row over the audit split; it is not the profiling cost.

## Gold-labeled profiling replay

The report is at:

- `results/runs/exp1-nine-local-20260930/full-gold/selector-table.md`
- `results/runs/exp1-nine-local-20260930/full-gold/selector-table.csv`
- `results/runs/exp1-nine-local-20260930/full-gold/accuracy-search-cost.png`

Search labels in this table are `final_correct` labels from already-paid profiling cells. This is valid for an offline labeled selector benchmark. The verifier still does not see the answer key; the audit split remains held out until a row has been selected.

Selected results:

| Selector setting | Held-out accuracy | Search evaluations | Search proxy cost | Saving vs exhaustive |
|---|---:|---:|---:|---:|
| Brute-force reference | 38.50% | 145,800 | $8.20715 | 0.0% |
| Random, 0.01 | 37.69% | 1,600 | $0.09062 | 98.9% |
| Bayesian optimization, 0.01 | 36.88% | 1,600 | $0.09749 | 98.8% |
| Similarity-annealed UCB, 0.01 | 34.50% | 1,458 | $0.07292 | 99.1% |
| Similarity-annealed UCB, 0.10 | 37.69% | 14,581 | $0.68036 | 91.7% |
| Similarity-annealed UCB, 0.20 | 38.50% | 29,161 | $1.39199 | 83.0% |
| Hill climbing, one restart | 38.50% | 8,200 | $0.56942 | 93.1% |
| Arm elimination, 0.25 confidence multiplier | 38.50% | 102,864.6 | $5.67330 | 30.9% |

These figures show that cost-aware search can recover the exhaustive winner at lower profiling spend on this fixed trace. They do not show that similarity is better: at the same low budgets, similarity is below random (34.50% versus 37.69% at 0.01; 36.12% versus 37.69% at 0.025; 36.06% versus 37.69% at 0.05). The current similarity acquisition catches up at larger budgets because the first solver dominates the row.

The full-gold replay is incomplete for `graph_residual_racing`: all seeds are present through fractions 0.01, 0.025, and 0.05, and only two seeds are present at 0.10. Fractions 0.20, 0.30, and 0.50 are not available. Those rows must not be compared as if they were complete eight-seed settings.

## Verifier-proxy replay

The deployment-faithful replay uses `verifier_pass` for search selection and attaches `final_correct` only after selection. Its checkpoint is at `results/runs/exp1-nine-local-20260930/proxy-similarity/selector-checkpoint.jsonl`, and the completed report is `results/runs/exp1-nine-local-20260930/proxy-similarity/selector-table.md` with plot `accuracy-search-cost.png`. All seven fractions from 0.01 through 0.50 have eight seeds. The exhaustive verifier-proxy reference selects `qwen2.5-0.5b/tinyllama-1.1b/tinyllama-1.1b` and reaches 18.5% gold audit accuracy. Do not compare this proxy curve directly with the gold-labeled curve as if they optimize the same objective.

The completed proxy replay exposes the central confound: verifier pass is near one for nearly every selected row, while held-out answer-key accuracy is roughly 18.5–21.9% for the tested low and medium fractions. A verifier-only selector therefore cannot be presented as an accuracy selector without a calibration assumption or a paid gold-labeled confirmation stage.

## Structural diagnosis

The trace diagnostic is `results/experiment1-nine-model-diagnostics-20260930.json`; the structural summary is `results/runs/exp1-nine-local-20260927-proper/analysis-20260930/structure.json`.

There are only 39 distinct search reward vectors among 729 rows. Main effects explain 0.9972 of row-mean variance, and the first solver alone explains about 0.9967. Changing the original solver gives 66.90% reward agreement across paired cells; changing retry 1 gives 99.40%; changing retry 2 gives 99.93%. This is evidence that similarity over retry coordinates is not informative on this trace because those coordinates are rarely reached, not evidence that graph methods are generally ineffective.

## Next experiment and Algorithm 2 hypothesis

The next experiment should force the information that Experiment 1 lacks. Register a finite search bank and disjoint audit bank with explicit difficulty strata. Add a forced-retry or verifier-calibration stratum so later slots are observed with positive probability. Keep an ordinary deployment stratum with endogenous early stopping. Shuffle row labels, permute question assignments, and randomize cost coefficients as negative controls.

The candidate Algorithm 2 is **slot-gated factorial racing (SGFR)**:

1. Pay a small complete-row calibration block across all first-slot models, with the same questions for paired comparisons.
2. Estimate, separately, quality, retry reach, and realized charge for each row and each question stratum.
3. Open retry-slot comparisons only when the estimated reach and potential quality gain clear a pre-registered gate; otherwise spend the next dollar on first-slot uncertainty.
4. Allocate paired questions by residual uncertainty divided by expected realized complete-row charge.
5. Require direct complete-row confirmation of the recommended row on fresh questions before reporting it as the winner.

A dependency-free research prototype is now implemented as `src/retry_search/slot_gated_factorial_racing.py` with tests in `tests/test_slot_gated_factorial_racing.py`. It is intentionally a heuristic: its gate diagnostics are not confidence intervals and it has no fixed-confidence guarantee. This is a testable hypothesis, not yet a novelty claim. Neighbor similarity, Hamming graphs, paired comparisons, adaptive racing, cost-normalized acquisition, and factorized configuration search all have prior art. The defensible intersection is the combination of a complete retry row, question-indexed paired outcomes, verifier-censored retry reach, response-dependent realized charge, and a finite search bank under a matched cached-incumbent ledger.

The required baselines are random, uniform allocation, Matrix UCB-E, Bayesian optimization, arm elimination, hill climbing, Cost-SySR or another similarity baseline, and a cost-aware stopping baseline. Report search spend, held-out accuracy, realized path cost, verifier pass rate, retry reach, and false-pass/false-reject rates separately. Do not use a pointwise full-matrix oracle as a deployment claim.

## First SGFR replay (exploratory)

The checkpointed replay script is `scripts/replay_sgfr_trace.py`. It ran all seven budget fractions and eight seeds on both selector rewards:

- Gold-labeled profiling: `results/runs/exp1-nine-local-20260930/sgfr-gold/selector-table.md`.
- Verifier-proxy profiling: `results/runs/exp1-nine-local-20260930/sgfr-proxy/selector-table.md`.

On gold labels, SGFR reached the 38.5% exhaustive-audit accuracy at fraction 0.20 with mean search cost $0.25185, a 96.9% saving in this local proxy ledger. At fraction 0.05 it reached 35.25% for $0.11178. This is a promising fixed-trace observation, not a significance claim: the same trace is first-slot dominated and the SGFR budget fractions are caps, so actual paid cells are lower than the cap after confirmation.

On the verifier proxy, SGFR reached 20.31% at fraction 0.01, 20.56% at 0.10, and 18.50% at 0.30 and 0.50; the exhaustive verifier-proxy reference is 18.50%. The proxy and gold curves are therefore different objectives, and the gold-labeled result cannot be presented as deployment-faithful. A real next experiment must add a calibrated verifier or a positive-probability gold confirmation block before making an accuracy claim.
