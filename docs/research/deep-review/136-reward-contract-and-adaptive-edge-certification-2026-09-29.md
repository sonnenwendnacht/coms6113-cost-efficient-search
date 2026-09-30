# 136: Reward contract and adaptive-edge certification (2026-09-29)

The CG-RTE proof target needs two corrections before implementation.

## Separate the selector reward from the audit label

The local trace contains an answer-key-blind verifier result and a later gold
`final_correct` label. A selector can use the verifier result during deployment
but cannot use the answer key. Define two separate modes:

* **Deployment-faithful mode:** (Y) is a verifier-visible proxy such as
  PASS/RETRY. The confidence intervals and graph eliminations target the
  proxy's finite-bank mean. Held-out answer-key accuracy is a separate audit
  outcome; no proxy-to-gold correctness theorem follows automatically.
* **Gold-visible diagnostic mode:** (Y) is answer-key correctness after the
  cell finishes. This can diagnose an allocation method on a fixed trace, but
  it is an offline oracle replay and cannot support a deployed-search claim.

The row recommendation is a function of exactly one declared (Y) contract.
Mixing verifier rewards during search with gold rewards in the proof would
invalidate the interpretation of the confidence intervals.

## Certify adaptively opened edges on fresh data

An edge can look stable because its calibration residuals happened to be small.
If that same block is then used to certify an elimination interval, adaptive
edge admission creates selection optimism. The safe protocol is:

1. allocate a calibration block solely to estimate the residual and decide
   whether the edge is eligible;
2. if it passes, open a fresh pre-shuffled certification block with a
   preallocated simultaneous confidence share; and
3. use only certification observations for graph-based elimination.

An alternative is to pre-register every possible edge stream and union-bound
all edge/prefix intervals, including edges that later fail the gate. A
stability test is a useful diagnostic but does not by itself prove that the
residual distribution is stationary.

The global confidence event must cover all direct node streams, all eligible
edge streams, all block prefixes, and any data-selected minimum-width path.
Once that event is established, choosing the narrowest valid path from past
data is safe; without it, “best path” selection is another unaccounted
multiple-comparisons step.

Cached cells also need sampling-design eligibility. A cell observed in an
outcome-adaptive earlier block should not be retroactively counted as part of
an edge's fixed residual stream merely because its bytes match. Reuse only
pre-registered block cells; otherwise collect a fresh certification block.

Finally, an endpoint executed inside an edge is already a direct complete cell.
The protocol's “fresh direct confirmation” is an additional independent block,
not a claim that an edge residual magically observes an unpulled endpoint.
Anchor selection by observed cost is suitable for a soft realized-spend run;
hard-cap anchor selection needs simultaneous cost bounds or a predeclared rule.

No implementation or experiment is claimed by this note.
