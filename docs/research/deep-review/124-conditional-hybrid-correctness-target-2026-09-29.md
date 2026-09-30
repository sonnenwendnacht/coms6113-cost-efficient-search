# 124: Conditional correctness target for the hybrid (2026-09-29)

This note states the strongest theorem target that the current design could
reasonably pursue. It is a conditional target, not a proved result.

## Target

Let `Q` be a fixed finite question bank and `X` the registered complete retry
rows. For a visible selector reward `Z` (either verifier proxy or a separately
defined stochastic score), define the finite-bank row value

\[
\mu_x = |Q|^{-1}\sum_{q\in Q} \mathbb E[Z_{xq}].
\]

For a paired edge `e=(a,b)`, define `D_e(q)=Z_{bq}-Z_{aq}`. The hybrid should
return an observed row `\hat x` such that, with probability at least
`1-\delta`,

\[
\mu_{\hat x} \ge \max_{x\in X}\mu_x - \varepsilon,
\]

or correctly report that the registered budget was exhausted before this
certificate was possible. A separate cost-feasibility interval can restrict
the maximum to rows whose deployment charge is within a declared cap.

## Assumptions a proof would need

1. **Registered finite bank.** The questions and row set are frozen before
   selection. Question blocks are sampled without replacement or in a fixed
   outcome-independent order.
2. **Complete-cell observations.** Every paid cell includes the full reached
   retry/verifier path. Unexecuted suffixes are not assigned a reward or cost.
3. **Cross-fitted gate.** The pilot fold alone chooses trusted edges and their
   thresholds. Racing and confirmation folds cannot alter the edge set.
4. **Simultaneous confidence.** Direct row intervals and paired-difference
   intervals are valid at all stopping times, with a union allocation over
   rows, edges, phases, and the cost-feasibility event.
5. **Observed-row recommendation.** A graph edge can prioritize a comparison
   but cannot certify a row that has no direct paid cells.
6. **Cost contract.** A strict cap requires a deterministic upper charge for
   every block before launch. If only realized charges are recorded, the
   result is an equal-realized-spend comparison and needs an anytime confidence
   rule for dollar-stopped sampling.
7. **Gold claim separation.** If `Z` is verifier pass, a gold-accuracy claim
   needs a stated calibration/shift assumption and an independent gold audit.
   If `Z` is `final_correct`, the result is explicitly an offline oracle
   replay.

## Conditional stopping argument

On the simultaneous-confidence event, Phase A can eliminate a row only when
its upper value bound is below the incumbent's lower bound (plus the chosen
`ε` margin). Phase B applies the same rule to trusted paired differences or
direct row intervals. Because every recommendation is directly observed, a
wrong graph edge can waste budget but cannot silently create an unobserved
winner. If all surviving rows are separated by these bounds, the returned row
is `ε`-best over the registered set.

The error probability would be bounded by the confidence allocation across the
pilot gate, racing, cost feasibility, and final confirmation. This argument
does not establish that EGCR saves dollars; it only makes a future savings
comparison scientifically interpretable.

## What remains empirical

The theorem target says nothing about the frequency of low-variance edges, the
best switch threshold, the realized-dollar advantage over Cost-SySRs, or
transfer to future questions. Those require matched controls, permutation
graphs, cost ledgers, and held-out audits. If the verifier proxy is biased or
the finite-bank structure shifts, the gold result can fail even when the proxy
certificate is correct.
