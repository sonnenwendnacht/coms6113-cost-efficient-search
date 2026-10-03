# 127: Resource-constrained BAI boundary (2026-09-29)

Li and Cheung's AISTATS 2024 paper, [Best Arm Identification with Resource
Constraints](https://proceedings.mlr.press/v238/li24c.html), is the closest
formal baseline for a cost-aware successive-elimination method. It defines a
best-arm problem in which each pull produces reward and consumes one or more
resources, and proposes Successive Halving with Resource Rationing (SH-RR).
The paper separates deterministic consumption from stochastic consumption and
requires the cumulative resource constraint to hold with certainty. Its
round-robin phase barriers are directly relevant to complete retry rows.

This changes how we should describe Cost-SySRs. A realized-dollar target is a
measurement protocol: the selector records actual charges and can overshoot
when a cell's retry cascade is not known before execution. It is not the same
as the paper's hard resource constraint. A strict dollar cap requires a known
per-cell upper bound that includes every possible retry, verifier/tool call,
failure charge, and prompt-size limit. Before launching a synchronized block,
the method must reserve the sum of those bounds for all active rows; otherwise
the cap cannot be certified.

The source prototype therefore remains an unverified heuristic. It now keeps a
per-phase ledger, records whether a block completed, and fails closed when a
budget cuts through the first block. A partial block may only use a previous
complete common sample for a provisional recommendation; with no such sample
it returns no recommendation. This is an implementation safety property, not a
new theorem.

For the eventual comparison, the fair options are:

1. **Soft realized-spend track:** predeclare question blocks, run a common
   synchronized block, charge every completed retry cascade, and compare
   selectors at common cumulative-dollar checkpoints. Report overshoot and
   partial-block status.
2. **Hard-cap track:** estimate or enforce a deterministic upper bound per
   complete cell, reserve the whole block atomically, and release unused
   reserve only after every active row reaches its terminal state. A timeout or
   provider failure still consumes a ledger cell with an explicit quality
   status; an unvisited retry is missing data rather than a zero reward.

The first track is suitable for the current trace because full retry reach and
prompt-dependent charges are observed only after execution. The second track
is the route to a future correctness claim, but it needs explicit token and
retry limits and has not been implemented or tested here.
