# Objective and frontier contract

The search budget and the deployment budget must not be conflated.

For each complete row `c`, report at least three quantities:

```text
profiling_spend(c, policy)       money paid while finding c
heldout_quality(c)               accuracy after the row is frozen
deployment_cost(c)               cold-run mean path charge on held-out tasks
```

The primary profiling objective should be fixed-budget best-row
identification: for every allowed search spend `B`, minimize the held-out
quality gap to the best registered row. This matches the Table-7-style
comparison and prevents a selector from choosing a cheap but poor row merely
because its deployment charge is low.

If the deployment goal is cost-constrained quality, register a separate cap
`D` and recommend the highest-quality row whose held-out deployment cost is
feasible. If the goal is a scalar tradeoff, register `lambda` before seeing
the audit split and optimize `Q - lambda*deployment_cost`; do not tune lambda
afterward. A single scalar utility is not a substitute for reporting the
quality--deployment-cost frontier.

Algorithm 2 may use a scalar utility internally to allocate paired evidence,
but it should maintain simultaneous uncertainty for quality and deployment
cost, and the final report should include the selected row, profiling spend,
held-out quality, held-out path cost, verifier-pass rate, and any constraint
violations. Search cost savings and deployment cost savings answer different
questions.

Every baseline receives the same registered profiling budget, question stream,
direct-confirmation rule, and held-out split. An exhaustive row oracle is used
only on a small declared space or as a post-hoc reference; it is not free
profiling evidence.
