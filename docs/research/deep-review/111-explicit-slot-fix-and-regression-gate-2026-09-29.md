# 111: Explicit slot fix and regression gate (2026-09-29)

## What changed

Note 110 found that the replay passed explicit categorical slots to CACR and
SCCR but not to CW-PLR. CW-PLR therefore inferred Hamming neighbors from the
numeric row index. That inference is only valid when rows are enumerated in a
particular mixed-radix order; the replay sorts slash-separated configuration
IDs lexicographically, so a one-index step is not a reliable one-slot change.

The source-level correction is now in place:

1. `run_cw_plr` accepts an optional `row_slots` sequence.
2. When supplied, local candidates are rows at Hamming distance one in those
   explicit slots. The old numeric-order behavior remains available only when
   a caller omits the map, preserving compatibility while making the structured
   replay call explicit.
3. The replay decodes the slash-separated configuration IDs into deterministic
   categorical coordinates and passes the same map to CW-PLR, CACR, and SCCR.
4. Unit-test cases cover a valid explicit map and duplicate-slot rejection.

The map is a reproducibility repair, not an algorithmic gain. It prevents a
structured method from receiving a different graph than the one described in
the paper. It must be applied before comparing any Hamming-neighborhood claim.

## Verification boundary

This checkpoint performed only a syntax compilation and diff check. The unit
tests and the nine-model replay were deliberately not run during the
research-only window. The long Experiment 1 generator was not stopped,
restarted, or modified. A future test/replay must first verify the explicit
slot tests, then rerun the structured selectors with the common realized-dollar
ledger from notes 108--109.

The scientific claim remains conditional: explicit coordinates make the
baseline faithful, but do not show that similarity improves search. Any gain
still needs permutation/random-graph controls, a matched cached-incumbent
baseline, held-out audit questions, and equal realized profiling spend.
