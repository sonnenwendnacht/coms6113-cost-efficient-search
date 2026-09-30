# Hub-anchor paired racing (2026-09-29)

Research-only design note; no experiments, traces, replays, or model calls.

## Idea

Use a cheap, broadly representative complete row `h` as a hub. Evaluate `h` once
on a precommitted question permutation and retain those cells. For each candidate
row `c`, evaluate `c` on the same questions and form paired differences

`D_c(q) = Q(c,q) - Q(h,q)`.

The first hub cell has already been paid for, so the incremental charge for adding
candidate `c` is its realized `K(c,q)`, rather than `K(h,q)+K(c,q)`. A single hub
stream can therefore provide common-question comparisons for many candidates,
which is attractive when one model configuration is much cheaper than the rows it
screens.

## Statistical requirements

Differences for two candidates share the same hub observations and are therefore
dependent. This does not require pretending they are independent: use a valid
finite-population confidence sequence for each registered difference and a
simultaneous error budget across all candidate streams. Do not sum the apparent
variance savings as though candidate differences were independent. A second hub or
fresh direct confirmation should be used to detect a hub that is unrepresentative
of the quality variation on the question set.

The hub is an anchor for relative comparisons, not a substitute for direct quality
evidence. Final recommendation should receive a direct fresh block (or an interval
that combines direct and paired evidence with overlap accounted for). The fixed
question permutation must be registered before outcomes are seen; selecting hub
questions after observing candidate outcomes would bias the finite-population
estimate.

## Prior-art boundary

Common random numbers and control variates already establish the general variance
reduction idea. The project-specific hypothesis is that a pre-paid cheap complete
retry row can serve as a reusable hub under heterogeneous, path-dependent row
charges. Any claimed gain should be compared against independent row racing,
ordinary synchronized pair racing that charges both rows, and a two-hub control.

