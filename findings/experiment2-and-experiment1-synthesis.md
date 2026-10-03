# Experiment 2 and Experiment 1 findings

Updated: October 2, 2026

This note is the running research summary that starts from the detailed
[Experiment 2 algorithm specification](experiment2-algorithm.pdf) and
incorporates the findings from the completed Experiment 1 trace, including
the binary correctness matrix, realized cost matrix, row-similarity analysis,
and the cost-accounting discussion.

The status is deliberately explicit: Experiment 1 is a completed local
proxy trace. Experiment 2 is a protocol and implementation plan. No valid
fresh Experiment 2 MathQA run has been completed, and no publication-level
superiority claim has been established.

## 1. The research problem

Each candidate is a complete ordered retry row:

```text
(model for original attempt, model for retry 1, model for retry 2)
```

With nine solver models there are `9 × 9 × 9 = 729` rows. A paid profiling
cell is one complete row on one question. The workflow runs under the real
stopping rule: the verifier may accept an answer after the first attempt, or
may trigger one or both retries.

The search algorithm must recommend one complete row. It may not recommend a
partially measured row, treat a retry suffix as a separate arm, copy a model
response between rows, or reuse a verifier state or workflow prefix.

The practical question is whether a selector can identify a strong row while
spending less profiling money than exhaustive evaluation of all 729 rows.

## 2. The current Experiment 2 algorithm

The current structural candidate is **cross-fitted reach-aware pair racing
(CRPR)**. It is an outer search selector, at the same level as Random Search,
UCB, Bayesian Optimization, and Hill Climbing. It does not replace the
solver or verifier.

The safer required comparison is **cost-weighted common-random-number ranking
and selection (CW-CRN-R&S)**, together with direct paired racing. CRPR is a
transfer ablation until it demonstrates a saving at matched realized spend.

### 2.1 What similarity means here

Two complete rows are neighbors when one ordered slot differs. For example:

```text
(A, B, B)  and  (A, C, B)
```

are one-slot neighbors. Similarity does not mean that the rows are
interchangeable. It only proposes a useful comparison: run both complete rows
on the same question and compare their outcomes.

For a pair of rows `a` and `b`, a same-question difference is:

```text
D(a,b,q) = outcome(b,q) - outcome(a,q)
```

Using the same question can cancel some question-difficulty variation. It is
not a free estimate of an unmeasured row. The anchor and challenger calls
still have to be paid, and every finalist must be measured directly.

### 2.2 Four question blocks

Before observing outcomes, split questions into four disjoint blocks:

1. **Calibration:** measure selected complete-row pairs and estimate their
   differences.
2. **Race:** measure incumbents directly and open challenger cells only under
   the registered rules.
3. **Confirmation:** directly compare the surviving finalists on fresh
   questions.
4. **Final audit:** evaluate one frozen row once, without exposing its labels
   during selection.

Question order, difficulty strata, row order, edge panel, dollar caps,
confidence level, non-inferiority margin, exploration reserve, and drift rule
must be frozen before outcomes are observed.

Natural early-stop questions and forced-retry questions must be labeled as
separate strata. They estimate different operating conditions.

### 2.3 Calibration and cross-fitted racing

For a complete incumbent and a one-slot challenger, run both complete rows on
the calibration block. Record three separate differences:

* quality or verifier outcome;
* whether each retry slot was reached;
* realized charge.

Estimate these differences within registered difficulty/reach strata. Then
apply the calibration estimate only to a separate race block. The first
implementation should use simple stratum means and conservative confidence
intervals rather than a neural surrogate.

On a race question:

1. run the incumbent directly;
2. build an interval for the challenger using the cross-fitted calibration
   residual and the observed incumbent uncertainty;
3. pay the complete challenger cell if it could still beat the incumbent, if
   the interval is unresolved, or if a direct-exploration reserve selects it;
4. otherwise mark it provisionally screened, never as the winner.

Transfer is turned off if the calibration-versus-race drift check fails. The
selector then falls back to direct paired racing.

Quality, retry reach, and charge each have their own gate. A small quality
difference cannot hide a rare but expensive continuation. Because many edges,
strata, and checkpoints may be inspected, one global error budget is needed;
per-edge nominal intervals are not enough.

### 2.4 Confirmation and final recommendation

Every finalist is directly evaluated on the fresh confirmation block. Only
then is one complete row frozen. The final audit is run once on the frozen
row, with answer-key correctness attached afterward.

No imputed or unconfirmed row can be reported as the winner. If the transfer
model is not credible, direct paired racing or the registered fallback
selector supplies the recommendation.

### 2.5 Pseudocode

```text
register rows, question blocks, strata, edge panel, costs, caps, and bounds
pay calibration cells for registered incumbent/challenger pairs
estimate quality, reach, and charge residuals by stratum

while profiling budget remains:
    choose an incumbent or a global-reserve row
    propose a one-slot neighbor or registered random challenger
    pay the incumbent on the next race question
    construct cross-fitted quality/reach/charge intervals

    if challenger can beat, is unresolved, or reserve requires it:
        reserve worst-case charge
        pay the complete challenger cell
        update direct and paired records
    else:
        mark challenger provisionally screened

    if drift or covariance gate fails:
        disable transfer and use direct paired racing

directly compare finalists on confirmation questions
freeze one complete row and run the untouched final audit
```

## 3. Required Experiment 2 comparison

The method must be compared with more than Random Search:

* Random and uniform allocation;
* Matrix UCB-E;
* categorical Bayesian Optimization;
* arm elimination and hill climbing;
* direct paired racing with no transfer;
* a synchronized common-question method such as Cost-SySR;
* CW-CRN-R&S with missing observations;
* C-LUCB-style correlated-arm control when its conditional bounds can be
  registered;
* SH-RR-style resource-rationed elimination;
* CRPR as the cross-fitted transfer arm.

Required falsification controls include shuffled row slots, question
permutations, unit costs, and permuted model-cost coefficients. All methods
must share question splits, seed rules, confirmation reserve, cached-incumbent
rules, and the realized-cost ledger.

### Stage A: mechanics gate

Use three preselected models and all ordered triples, giving 27 rows. Split
200 search questions into 60 calibration, 80 race, and 60 confirmation
questions, plus 200 untouched audit questions. Use a sparse nine-edge panel
covering every slot and model value.

Stage A is not evidence of superiority. It only verifies:

* no audit read before row freeze;
* no unconfirmed row selected;
* exact charge accounting for every complete cell;
* correct natural and forced-retry labels;
* valid checkpoint resume identity;
* transfer disabled after a failed drift check;
* whole-cell budget overshoot reported honestly.

### Stage B: research run

After Stage A passes, use the nine-model pool and 729 rows with a fresh
question bank and fresh final audit. Compare methods at matched realized
profiling dollars, not merely at the same fraction parameter.

At each registered spend point `b`, report:

```text
Delta accuracy = accuracy(CRPR) - accuracy(direct paired racing)
Delta spend    = spend(direct paired racing) - spend(CRPR)
```

The non-inferiority margin and minimum practical saving must be chosen before
the final audit is opened. The best-looking budget cannot be chosen after
seeing audit results.

## 4. What Experiment 1 actually contains

The completed local run contains 729 rows × 400 questions = 291,600 complete
workflow cells:

* questions `0–199`: search split;
* questions `200–399`: audit split;
* each cell has binary `final_correct` after the workflow's stopping rule;
* each cell has a realized proxy cost, token counts, calls, verifier outcomes,
  and reached attempts.

Tracked compact exports are:

* [binary correctness matrix](experiment1-nine-model-correctness.csv);
* [realized cost matrix](experiment1-nine-model-cost-usd.csv);
* [row-similarity statistics](experiment1-similarity-analysis.csv);
* [row-similarity report](experiment1-similarity-analysis.md);
* [row-similarity plot](experiment1-similarity-analysis.png).

The raw model responses and full trace remain ignored because they are large
generated artifacts. The compact matrices contain row names and only the
registered summary values.

## 5. What similarity is actually present

For every pair of rows, we computed Pearson correlation (the phi correlation
for binary correctness vectors) across the 200 questions and the fraction of
questions where the two correctness bits agree. There are 265,356 unordered
row pairs.

### Pairs that differ in exactly one slot

| Only changed slot | Search correlation | Audit correlation | Meaning |
|---|---:|---:|---|
| Original solver | 0.064 | 0.048 | Changing the first solver changes behavior substantially |
| Retry 1 | 0.933 | 0.922 | With the original fixed, retry 1 usually changes little |
| Retry 2 | 0.989 | 0.984 | With the original and retry 1 fixed, retry 2 changes even less |
| All three slots changed | 0.064 | 0.047 | Baseline for completely different rows |

### Rows sharing exactly one slot

| Shared slot only | Search correlation | Audit correlation | Agreement, search/audit |
|---|---:|---:|---:|
| Original solver | 0.933 | 0.921 | 99.4% / 99.1% |
| Retry 1 only | 0.064 | 0.048 | 66.9% / 67.0% |
| Retry 2 only | 0.064 | 0.047 | 66.9% / 67.0% |

The apparent benefit of “sharing one slot” is therefore misleading. It is
almost entirely the original solver slot. Sharing a retry model by itself
does not produce positive similarity in this natural-stopping trace.

This does not prove that retry choices are unimportant in a different
deployment policy. It shows that Experiment 1 rarely exposed those choices.

## 6. Cost accounting

For a row/question cell, the proxy cost is:

```text
cell cost = sum(model coefficient × input tokens for every reached call)
```

If a workflow reaches only the first two attempts, charge:

```text
original solver
+ verifier after attempt 1
+ retry-1 solver
+ verifier after attempt 2
```

Do not charge the third solver or verifier because they were never called. If
the first attempt is accepted, only the first solver and verifier are charged.
A call that runs and fails is still charged.

The fixed verifier is Qwen2.5-1.5B. Experiment 1 charges input tokens only;
output tokens, cache discounts, and latency are excluded. The model
coefficients are local proxy values, not provider invoices.

Known coefficients are not enough to predict a whole-cell charge because the
verifier determines which retries occur and the input length can change by
attempt. The selectors therefore use the realized charge after a cell is
paid. A row fraction or cell fraction is only an allocation rule; it does not
guarantee equal dollars. Profiling cost and cold deployment cost remain
separate metrics.

The exported cost matrix ranges from about `$0.0000194` to `$0.0005637` per
cell, with mean about `$0.0000573`. The full exhaustive search split costs
about `$8.20715` in this local proxy accounting. These are bookkeeping values,
not API bills.

## 7. The Experiment 1 plateau

The accuracy curves flatten quickly because 81 rows tie for the best search
score and all 81 also obtain 38.5% on the audit. Those rows share Qwen2.5-7B
as the original solver; their retry suffixes are observationally almost
equivalent under the natural stopping rule.

This is useful evidence that the first solver dominates this trace. It is also
a limitation: the experiment is a strong first-solver search but a weak test
of retry-aware search or retry-slot similarity.

Other relevant diagnostics are:

* only 7,047 of 291,600 workflows reached a retry, about 2.42%;
* retry-1 outcomes agree about 99.4% of the time;
* retry-2 outcomes agree about 99.93% of the time;
* final parse failure affects about 25.19% of cells;
* 77.33% of verifier-accepted workflows are incorrect in the all-attempts
  diagnostic.

The final point matters: verifier acceptance is not gold correctness. A
deployment-faithful selector cannot silently treat the verifier signal as the
answer key.

## 8. What was corrected during the research

The initial ideas evolved through several prototypes:

* similarity-annealed UCB treated complete rows as nodes in a Hamming graph;
* graph-residual racing tried to transfer paired differences through nearby
  rows;
* CW-PLR/CACR/SCCR explored pairwise local racing and cost gates on invented
  landscapes;
* SGFR was replayed, then withdrawn.

The SGFR replay is not evidence. Its racing candidate list was empty because
predeclared edges were mistaken for paid calibration pairs. Even without that
bug, its same-block residual identity reduced to the directly measured
candidate mean, so it did not create information about an unmeasured row.

The current design keeps similarity as a proposal and allocation signal,
uses disjoint calibration and race blocks, separates quality/reach/charge,
requires direct confirmation, and keeps direct racing as a fallback.

## 9. Claim boundary

The following are established ideas and must be treated as baselines or
components, not standalone novelty claims:

* common-question paired comparisons;
* local one-slot configuration moves;
* configuration racing and successive elimination;
* correlated-arm best-arm identification;
* resource-rationed search;
* heterogeneous pull costs.

The possible project-specific intersection is narrower:

> complete ordered retry rows + question-indexed comparisons across disjoint
> blocks + verifier-censored retry reach + response-dependent complete-row
> charge + direct finalist confirmation under a finite profiling budget.

CRPR earns a positive claim only if it saves a preregistered amount of
realized profiling cost or paid challenger cells while maintaining
non-inferior final-audit accuracy against direct paired racing and surviving
the permutation and unit-cost controls. Otherwise the correct result is that
direct complete-row racing is safer in this setting.

## 10. Current next step

Implement a separate protocol-aware Experiment 2 runner. Its immutable
manifest must bind the row bank, model snapshots, block/question IDs,
natural/forced retry mode, edge panel, methods and parameters, confidence
rules, non-inferiority margin, dollar caps, coefficients, prompt hashes, and
source checkpoint.

The runner must expose separate `profile`, `confirm`, and `audit` operations.
The audit operation must reject calls before a row is frozen and must never
give answer keys to the selector. Every paid complete cell must be recorded,
including early-stopped and failed calls. The first run should use invented
data and deterministic leakage/accounting tests before any GPU or API run.
