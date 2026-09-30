# 113: Edge-gated complete-row racing (2026-09-29)

This note turns the prior-art boundary into a concrete Algorithm 2 candidate.
It is a protocol proposal, not a result.

## Observation model

Let `x` be one complete retry row and `q` a registered benchmark question.
A paid cell returns

\[
(Y_{xq}, C_{xq}),
\]

where `Y` is the final correctness outcome and `C` is the realized charge of
the entire solver/verifier/retry execution. A pull of `(x,q)` returns no free
observation about any other row. The target is the best registered row under a
declared finite-bank quality or deployment-cost constraint.

The row coordinates define a candidate graph `G0` (for example, one model
slot changed). `G0` is a measurement-order prior only. It is not a statistical
similarity guarantee.

## Proposed selector: EGCR

**Edge-Gated Complete-Row Racing (EGCR)** has five stages.

1. **Register and split.** Freeze row coordinates, a question permutation, a
   pilot fold, a racing fold, and an independent held-out audit. Freeze the
   deployment objective and a dollar ledger before observing outcomes.
2. **Pilot edge screen.** For a predeclared subset of candidate edges, buy
   complete cells for both endpoints on the same pilot questions. Estimate the
   paired residual variance and the endpoint charge distribution. Cross-fit the
   edge decision; do not use the racing fold to decide which edges are trusted.
3. **Gate.** Keep an edge as a similarity-guided comparison only if its paired
   residual interval is below the registered variance threshold and its
   reserved block charge is cheaper than the direct-racing alternative by the
   registered margin. Otherwise mark it ordinary graph order or reject it.
4. **Race.** Maintain direct confidence intervals for every observed row and
   paired intervals for trusted incumbent/challenger edges. Choose the next
   comparison by uncertainty reduction per *reserved* dollar, with a small
   predeclared global-exploration probability. A trusted edge can prioritize a
   challenger and reduce the variance of the comparison; it cannot certify an
   unobserved row.
5. **Stop and confirm.** Stop only when the incumbent beats every surviving
   observed competitor under simultaneous quality and feasibility bounds, or
   when the dollar budget is exhausted. Evaluate the selected complete row on
   the untouched audit questions. If no edge passes the gate, run the direct
   cost-aware baseline instead.

For a trusted edge `e=(a,b)` and a question block `B`, the paired stream is

\[
D_e(q)=Y_{bq}-Y_{aq},\qquad q\in B.
\]

The acquisition score may use the current confidence width of `D_e` divided
by a pre-call reservation for both endpoints, but the confidence rule must be
anytime-valid (or have a preallocated union bound). A realized-dollar replay
can report overshoot; a hard cap requires reserving a deterministic upper
charge before launching the block.

## Why this is the right amount of structure

EGCR does not pretend that Hamming neighbors are interchangeable. It uses
similarity only where the data show lower *paired residual variance* and where
the shared block amortizes its extra endpoint charges. The direct interval and
the independent audit protect against a graph prior that is wrong, a verifier
proxy that is biased, or an attractive local optimum in a multimodal row
landscape.

The closest established methods are graph-feedback UCB, clustered BAI,
structured BAI, and cost-aware best-arm allocation. The candidate gap is the
combination of: (i) complete retry rows, (ii) outcome-linked path charges, (iii)
no free neighbor feedback, and (iv) a finite held-out gold audit. The paper
must call this an empirical extension unless a theorem is proved under explicit
bounded-charge and cross-fitted residual assumptions.

## Required falsification controls

- **Permutation graph:** randomly permute row coordinates while preserving the
  same matrix; a gain that survives is not due to configuration similarity.
- **Cached-incumbent control:** give direct racing the same already-paid row
  cells and the same ledger.
- **Independent-arm control:** compare to cost-aware LUCB/SySRs without paired
  edges.
- **No-gate ablation:** always trust `G0`; this should lose when the structural
  prior is wrong.
- **Cold deployment audit:** report new-question quality and path cost
  separately from profiling spend.

Only an equal-realized-dollar improvement that survives these controls would
support a contribution claim. The candidate remains conditional until those
comparisons are performed.
