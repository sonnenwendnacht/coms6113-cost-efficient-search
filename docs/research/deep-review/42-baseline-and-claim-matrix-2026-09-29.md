# Baseline and claim matrix

The literature review suggests a comparison matrix that separates the outer
selection problem from inner retry control. Every method must receive the same
registered search questions, the same legal answer-key-blind signals, the same
hard or explicitly soft dollar rule, and the same untouched audit questions.

| Label | What it selects | What one paid action observes | Why it is needed |
| --- | --- | --- | --- |
| Uniform/random | Complete rows | Direct `(Q,K,R)` cells | Simple search floor and coverage control |
| Independent cost-aware BAI | Complete rows | Direct row cells; no pairing | Compares against CoPSI/CoHV-UCB/PBGI-style allocation |
| Paired racing | Leader–candidate complete-row pairs | Same-question `Delta` cells; leader is repaid as required | Isolates common-random-number variance reduction |
| Cached-incumbent control | Current leader reused across candidates | Same paired cells with the leader cache | Prevents an artificial advantage from assuming every baseline reruns the leader |
| Two-hub control | Two predeclared hubs | Hub-paired differences and direct checks | Tests whether any gain is anchor-specific |
| HAPR/CAPR | Complete rows with a hub ledger | Cached hub plus candidate trajectory, reservations, and CS state | Proposed shared-row mechanism |
| Fixed-candidate verifier allocation | Verifier attributes only | Separate verifier observations | BMA-GAI-style scope control; not a row selector |
| Inner generate–rank–verify | Per-question generation/verification counts | Candidate scores and verifier labels | ADAP-style deployment comparator; not an outer row selector |

The headline claim should be licensed only if HAPR/CAPR beats the
cached-incumbent paired control at matched *realized search spend*, while its
selected row is directly confirmed and its held-out audit quality is at least
as good within the registered tolerance. Beating a fresh-rerun leader is only a
diagnostic because a real sequential selector can cache its incumbent.

## Required reporting columns

For each algorithm–parameter pair and each replicate, report:

* search spend paid before recommendation;
* reserved amount and any hard-cap rejection or soft-cap overshoot;
* number of complete row cells and direct observations of the selected row;
* hub cells, pair cells, and confirmation cells separately;
* selected-row search accuracy and untouched audit accuracy;
* cold deployment cost of the selected row on the audit questions;
* whether the selected row was directly observed before recommendation; and
* a confidence interval or finite-population confidence sequence for the
  selection comparison.

Do not put audit outcomes into the selector state. Do not call the exhaustive
trace-generation bill a selector's money saved. Report it as a separate
oracle-data acquisition cost, because the current replay is an offline
counterfactual benchmark rather than a live ledger.

## Claim levels

1. **Engineering claim:** the ledger records legal observations and enforces
   reservations without leaking answer keys.
2. **Statistical claim:** paired intervals preserve the declared finite-set
   target under the registered sampling and stopping rule.
3. **Efficiency claim:** shared hub cells reduce realized search spend versus
   the matched cached-incumbent control at the same audit quality.
4. **Scientific scope:** the result applies to the tested complete retry rows,
   question distribution, verifier, and cost model. It is not a general
   theorem about all agents, similarity graphs, or model routing.

If level 2 or direct confirmation fails, report only the engineering or
descriptive result. If level 3 fails, the contribution is not an efficient
search method even if the paired estimates are statistically valid.
