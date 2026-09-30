# 121: Cost-SySRs to EGCR hybrid (2026-09-29)

The literature audit suggests one coherent Algorithm 2 candidate instead of a
collection of unrelated heuristics.

## Two phases

### Phase A: cost-synchronized successive rejects

Start with all registered rows active. At each phase, draw one fixed block of
questions and execute every active row on that block. This preserves the
same-question covariance that SySRs exploits. Eliminate the row with the worst
supported quality bound, charging every complete cell.

Unlike ordinary SySRs, choose the block size from a reserved-dollar forecast:

\[
B_k \approx |Q_k|\sum_{x\in A_k}\widehat c_x,
\]

where `A_k` is the active set and `\widehat c_x` is learned only from already
paid cells. For a hard cap, replace the forecast with a deterministic upper
charge. If no upper charge exists, use the realized ledger and record
overshoot. The phase must be abandoned or shortened before launching a block
whose reservation cannot fit the remaining hard cap.

### Phase B: edge-gated complete-row racing

When the active set is small or its rows have sharply different charges, stop
paying every active row on every question. Use the EGCR protocol from note 113:

1. choose incumbent/challenger pairs using only a pilot-frozen edge gate;
2. run both complete rows on the next fixed question block;
3. apply a cross-fitted paired confidence test;
4. choose the next pair by reduction in decision uncertainty per reserved dollar;
5. stop only with direct evidence for the surviving row and audit it on fresh
   questions.

The switch criterion must be predeclared or cross-fitted. Examples are an
active-set size threshold, a measured charge-imbalance threshold, or a
predicted cost of the next synchronized phase exceeding the predicted cost of
pairwise races. Choosing the switch after looking at held-out outcomes would
invalidate the comparison.

## Why this combination is plausible

Phase A protects against a bad local graph start and supplies comparable
question-aligned evidence. Phase B avoids paying expensive retry rows on every
remaining question once only a few plausible rows remain. The graph does not
provide free row observations; it only orders paid pairwise comparisons.

The candidate is a cost/path extension of established synchronized BAI, not a
new synchronization principle. Its empirical claim would be:

> Under unequal, realized retry charges, the gated switch can identify the
> best complete row at lower profiling dollars than Cost-SySRs and direct
> cost-aware paired racing, at matched held-out quality.

## Failure modes to register before testing

- If costs are nearly equal, Phase B adds overhead and should not win.
- If Hamming neighbors are not response-similar, the gate should reject them
  and fall back to direct races.
- If the best row lies in a disconnected graph region, Phase A or a global
  exploration reserve must discover it before local races dominate.
- If retry reach is strongly outcome-dependent, a mean charge forecast can
  underreserve; use a hard upper bound or report only realized spend.
- If the verifier proxy and final correctness disagree, all profiling
  elimination claims need an independent gold audit.
- If the switch rule itself is tuned on the same search fold, it needs a
  separate development fold or multiplicity correction.

This hybrid is the current most defensible Algorithm 2 design, but it remains
conditional until an equal-realized-dollar evaluation and the listed controls
show a benefit.
