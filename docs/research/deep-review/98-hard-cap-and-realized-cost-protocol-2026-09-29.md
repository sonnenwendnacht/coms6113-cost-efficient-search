# Hard-cap feasibility for retry-row profiling

The current selectors accept a `cost_budget` but may overshoot it: they start a
pair or block using an estimated next charge and only learn the exact input-token
ledger after the complete workflows finish. That is a valid fixed-realized-spend
heuristic, but it is not the “cumulative resource constraint holds with
certainty” objective in BAI with Resource Constraints.

## Two separate protocols

**Realized-spend protocol.** Let a paid cell return `(Y(c,q), K(c,q))`, where `K`
is the sum of all reached solver and verifier input-token charges. Stop after the
next complete cell would exceed the target, or report the actual overshoot. Match
selectors by a common realized-dollar grid in the report. This is the easiest
empirical protocol and should be the default for the existing Experiment 1
replay.

**Safe hard-cap protocol.** Before starting a cell, reserve a deterministic upper
bound `U(c,q)` on its complete-workflow charge. Only launch a new block if the sum
of the `U` values for all new cells is at most the remaining budget. Stop when no
complete cell fits. After execution, record the actual `K`; unused reservation is
released. If no finite valid `U` can be established, the method must not claim a
hard cap.

For this local runner, a candidate `U` can be derived from each model's fixed
maximum generation length and tokenizer limits: bound the input to every solver
prompt, including the maximum retained previous answer and verifier feedback, and
bound the verifier prompt that contains the maximum answer text. Multiply each
bound by the registered model coefficient and sum over all three attempts and
verifier calls. A bound based only on the mean observed charge is not safe.

## Consequences for Algorithm 2

The selector should expose the protocol in its result, for example
`budget_mode = realized | safe_hard_cap`, `requested_budget`, `actual_cost`,
`reserved_upper_bound`, `overshoot`, and `unused_budget`. A cost-aware allocation
rule can rank candidate blocks by expected uncertainty reduction per dollar, but
it may launch only blocks admissible under the selected protocol. A direct
cost-aware SH-RR or CABAI baseline receives the same reservation wrapper.

The hard-cap version creates a useful but limited result: it prevents a race from
spending the remaining budget on a large pair block, without adding any new
information source. The upper-bound construction can be pessimistic, so report
budget utilization and compare it with the realized-spend protocol. If the safe
wrapper changes which selector wins, that is a deployment-accounting result, not
proof that row similarity is useful.

## Statistical caution

`K(c,q)` is an outcome-linked resource observation because verifier reach changes
which calls occur. It must be analyzed jointly with `Y(c,q)` and never replaced
by a row's average charge when enforcing a hard cap. For a fixed-confidence
claim, confidence intervals for quality and cost feasibility are separate: a row
can have high accuracy but fail the cost constraint, or low cost but uncertain
accuracy. For a held-out deployment report, disclose both profiling spend and the
selected row's cold deployment cost.

This protocol does not make generic similarity novel. It supplies the missing
contract needed before comparing complete-row paired racing, resource-constrained
BAI, multi-fidelity controls, or random search at an equal and reproducible
budget.
