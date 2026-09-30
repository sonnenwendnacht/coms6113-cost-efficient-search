# 117: Cost-aware BAI baseline and objective separation (2026-09-29)

## Primary-paper audit

Kanarios, Zhang, and Ying's **Cost Aware Best Arm Identification** (2024)
assigns each arm a reward distribution and a cost distribution. Its goal is to
identify the highest-reward arm while minimizing expected testing cost. The
paper derives cost-aware lower bounds and proposes CTAS and Chernoff-Overlap
allocations; in homogeneous-cost cases the low-complexity method reduces to a
racing procedure.

This rules out “divide uncertainty by arm cost” as a new idea. It is a required
baseline whenever our cost can be treated as an arm-level, pre-known or
stationary random charge.

## The retry-row distinction

Our cell is indexed by `(row, question)`, not only by row. The charge can vary
with question length, solver choice, verifier choice, retry reach, and whether
the verifier stops early. Thus there are three possible regimes, and the paper
must state which one Experiment 1 uses:

1. **Known deterministic cell price.** If the full charge is fixed before a
   call, use cost-aware BAI directly with the cell price and compare against
   CABAI-style allocation.
2. **Known upper bound, random realized charge.** If the charge is random but a
   deterministic per-cell upper bound is known, reserve that bound for a hard
   cap and use the realized charge for efficiency reporting.
3. **Only an estimated or outcome-linked charge.** Do not call the budget a
   hard cap. Use a realized-dollar ledger, report overshoot, and treat the cost
   model as part of the uncertainty contract.

The current structured replay uses realized cell costs and may overshoot its
fractional cap. That is an offline comparison protocol, not a CABAI guarantee.
The direct CABAI control should receive the same legal information: observed
costs for paid cells, fixed question blocks, and no held-out outcomes.

## Objective separation

CABAI's reward/cost objective is close to our search problem, but our reports
must keep three quantities distinct:

- profiling dollars spent to select a row;
- held-out quality of the selected row; and
- cold deployment charge of that row on a new question.

An algorithm can be cheaper to profile but select a row with a higher cold
deployment cost. A single “cost” column would hide that tradeoff. The primary
curve should therefore compare held-out quality at equal realized profiling
dollars, with deployment cost and latency reported separately.

## Source

Kanarios, Zhang, and Ying, “Cost Aware Best Arm Identification,” 2024:
https://arxiv.org/abs/2402.16710
