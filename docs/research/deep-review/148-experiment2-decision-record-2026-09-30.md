# Experiment 2 decision record: what to implement next

Updated: 2026-09-30 17:58 ET

This record freezes the next CPU-independent decision. It does not authorize a GPU or API run.

## The research question

Given a finite set of complete ordered retry rows, can a selector reduce **profiling spend** by transferring question-level evidence between one-slot-neighbor rows, while choosing the same or a better row than direct paired racing at the same realized spend?

The unit of recommendation remains a complete row. A row is never declared best from a partially observed suffix. A model response or verifier output is not reused between rows; the only permitted transfer is a prediction learned on one question block and tested on a different block.

## Frozen estimands

For a selected row `r` on an untouched final audit, report:

* `final_correct`: answer-key correctness, attached only after selection;
* `verifier_pass`: the deployment-time, answer-key-blind signal used by the selector;
* `realized_charge`: solver and verifier input-token charges, including failed attempts and all reached retry slots;
* `retry_reach[s]`: the fraction of workflows that reach slot `s`;
* `search_spend`: the actual profiling charge, including confirmation;
* `cold_deployment_cost`: the mean charge to execute the frozen row on the final audit.

The primary comparison is paired final-audit correctness at matched realized search spend. Search spend and cold deployment cost are separate axes. A lower profiling bill cannot compensate for a worse final row unless the pre-registered utility says so.

## Candidate methods and fair controls

| Family | Role in the comparison | What must be held fixed |
| --- | --- | --- |
| Random / uniform | low-information reference | same question order, seed list, and spend ledger |
| Matrix UCB-E / categorical BO | independent configuration search | no structural transfer |
| Arm elimination / hill climbing | classic adaptive references | same reserve and confirmation rules |
| SySRs | synchronized same-question correlation baseline | same paired question blocks and confirmation reserve |
| Direct paired racing | strongest no-transfer control | every challenger race cell is directly paid |
| CRPR | proposed cross-fitted transfer | calibration residuals may only score a disjoint race block; finalists are directly confirmed |
| Identity / shuffled controls | falsification tests | remove useful row-slot or question correspondence while preserving costs |

The result that would support CRPR is a lower number of paid challenger cells and lower search spend than direct paired racing, with a non-inferior final-audit correctness interval and no under-reporting of realized charge. If the interval or the cost ledger fails, the useful paper result is a negative one: direct paired racing is safer.

## CRPR protocol, without prefix reuse

1. Split questions before looking at outcomes into calibration, race, confirmation, and final-audit blocks. Stratify each block by difficulty and keep the split fixed for every method.
2. Use complete-row pairs that differ in exactly one model slot. Pay both endpoints on calibration questions. For each pair and difficulty/reach stratum, store the signed quality difference, reach difference for each retry slot, and charge difference.
3. Pay the incumbent on race questions. Predict the challenger-minus-incumbent difference from calibration residuals. The prediction interval must include calibration uncertainty and the observed race-incumbent uncertainty; a plug-in mean alone is not a gate.
4. Pay the challenger when its upper confidence bound can beat the incumbent lower bound, when the interval overlaps the decision boundary, or when a pre-registered direct-exploration reserve selects it. Otherwise mark it as provisionally screened, never as the winner.
5. Keep separate gates for quality, retry reach, and charge. A quality gate cannot hide a rare expensive continuation. Reserve the worst-case charge before opening a challenger cell, and charge the whole cell even when the verifier stops early.
6. Directly evaluate every finalist on confirmation questions. Freeze the winner and run the final audit once. No final-audit statistic may tune a budget, threshold, seed, or method parameter.

The first implementation should use a stratum mean residual and a bounded confidence sequence, not a learned neural surrogate. Because many pairs, strata, slots, and checkpoints may be screened adaptively, predeclare the finite edge set and spend one global error budget across all quality, reach, and charge gates (for example, a Bonferroni boundary or a simultaneous bootstrap/confidence-sequence construction). Record the maximum number of looks. A no-transfer version with the same reserve is mandatory: if cross-fitting does not beat it at equal realized dollars, stop adding structure. Disable residual transfer when a predeclared calibration-versus-race drift check fails.

## Sample-size and reporting rule

Two hundred final questions are adequate for a pilot but not a precise superiority claim: around 38.5% accuracy, a simple 95% binomial interval has a half-width near 6.9 percentage points. For a paired comparison, if the discordant-pair rate is `d`, a rough normal approximation for a two-sided 5% test with 80% power and target gap `delta` is

`n ≈ (1.96 + 0.84)^2 * d / delta^2`.

At `d = 0.20`, this is about 620 questions for a 5-point gap and about 1,720 for a 3-point gap. Use the observed discordance and a pre-registered target to choose a later confirmatory audit; do not treat eight allocation seeds as independent replications.

## Decision gate before any expensive run

Implement the ledger and disjoint-block splitter first, then run only deterministic unit tests and a tiny invented-data sanity check. Start a full local run only after the following are machine-checkable: no audit reads before freeze, no unconfirmed row is selected, exact realized-cost accounting, resume identity binding, and separate natural/forced-retry labels. GPU/API access is not needed to settle those properties.
