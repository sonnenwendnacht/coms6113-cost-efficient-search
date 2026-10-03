# Replay protocol audit for Algorithm 2 (2026-09-29)

This is a read-only audit of the existing Experiment 1 replay code. No
generation, selector replay, or model/API evaluation was launched.

## What the current replay gets right

The generator records a complete rectangle in a deterministic order:
questions first, then all 729 ordered solver rows. Its metadata separates the
first 200 search questions from the 200 held-out questions. The replay
validator checks the exact `(config_id, question_id)` key set, rejects
duplicates and missing cells, and keeps the two partitions disjoint
(`scripts/replay_experiment1_nine_model.py:55-97`). This is a useful integrity
check for the completed trace.

The selector sweep receives only a search reward/cost matrix and does not
receive the held-out matrix (`scripts/replay_experiment1_nine_model.py:152-166`,
`src/retry_search/selection_sweep.py:760-836`). The ordinary selectors read a
cell through `_pick_cell`, which records it in a per-run `seen` set and charges
its realized cost once (`src/retry_search/selection_sweep.py:100-119`). Each
algorithm/parameter/seed starts with fresh state. Therefore the current
post-hoc comparison can be described as a leak-free *counterfactual replay*
provided the selector implementations continue to obey the pull-only access
discipline.

## What it does not yet represent

**The reported search bill is counterfactual.** The local generator has already
paid for the entire 400-question by 729-row rectangle before any selector is
run. The report recomputes the sum of cells that a selector would have pulled;
that number is useful for an offline allocation comparison, but it is not an
API charge avoided by the already completed trace. A live claim requires a
selector-facing execution service that requests cells online and records the
physical ledger. The paper should call the current quantity replay-equivalent
search cost and reserve actual savings claims for a live or simulated online
run with the same ledger.

**The two budget semantics are mixed.** The ordinary sweep interprets
`fraction` as a number-of-cells target. The structured methods are given a
realized-cost target (`replay_experiment1_nine_model.py:167-184`), but their
next action is admitted using observed cost only and a final pair can overshoot.
There is no maximum-charge reservation. These are not equal-dollar method
comparisons. Algorithm 2 should either use a common hard admission rule,
`spent + reserved + max_new_action_charge <= B`, or label every result as a
soft-cap result and report overshoot. The bound derived in note 32 is needed
for a strict cap.

This is not a reason to invent a budgeted bandit baseline from scratch. Li and
Cheung's [Best Arm Identification with Resource Constraints](https://proceedings.mlr.press/v238/li24c.html)
already gives a resource-constrained pure-exploration formulation and a
successive-halving-with-resource-rationing baseline. It should be included as
the appropriate cost-heterogeneous comparison once the row action and charge
semantics are aligned. Our possible extension is the complete retry-row,
same-question shared-evidence ledger, not the existence of a dollar cap.

**Question schedules are not registered outputs.** Each selector creates a
seeded permutation internally; pair methods create additional pair-specific
permutations when a pair is first visited. The seed makes a particular run
reproducible in the current code, but the schedules are not saved as part of
the result and different methods do not share one declared screening fold.
For a paired hub comparison, save a manifest containing the exact question
permutation for each seed, the hub block, candidate blocks, confirmation fold,
and tie-breaking rule. A candidate must not choose a question after seeing its
outcome. If different schedules are retained, they must be treated as
cross-fitted streams rather than silently pooled as one independent sample.

**There is no shared hub bank.** CACR and SCCR can reuse an exact observed
cell when it overlaps a later incumbent/challenger comparison, but their
incumbent changes and the pair state is keyed by that directed pair. The
random anchor in the graph residual baseline is not a predeclared hub whose
measurements are amortized across all challengers. Nothing in the current
runner charges one hub once and then exposes its observations to a registered
set of candidate races. Algorithm 2 must make the hub a first-class paid
resource: select it without target outcomes, record its cells once, let every
candidate compare on the same hub questions, and budget a fresh direct or
second-hub confirmation.

**The full matrix is still physically available to the process.** Current
selectors follow the intended pull-only convention, but a Python matrix is
not an information boundary. A future selector can accidentally index an
unpulled value. For a definitive experiment, expose a ledger-backed oracle
whose `pull(row, question)` method is the only way to obtain a reward or
charge; keep an audit log of every request, reuse, reservation, and rejection.
The full trace can remain the fixture backend, but it must not be passed as a
plain public matrix to the algorithm under test.

**Some existing selectors return a surrogate row.** The similarity and graph
residual selectors can choose a row from a posterior/path estimate even when
that row has no direct cells in `seen`. The replay script then attaches its
held-out accuracy immediately, with no fresh search confirmation. This is
valid only if the result is explicitly labelled a surrogate recommendation.
The headline Algorithm 2 protocol must either require a directly observed
incumbent or buy and charge a fresh direct confirmation before the audit
evaluation. Add a `selected_row_directly_observed` field and separate
`confirmation_spend` from the search bill.

The current racing radii are also heuristic. In particular, the pairwise
radius accepts confidence-related arguments but does not implement a
time-uniform confidence level. The structured prototypes should therefore be
called allocation heuristics until the registered finite-population or
anytime-valid interval is implemented; a parameter name must not imply a
confidence guarantee.

## Fair replay contract for the next protocol

For each method/parameter/seed, register before selection:

1. the search question population and one or more fixed permutations;
2. the initial knowledge set (normally empty, or the explicitly paid hub
   cells only);
3. the row/cell oracle and its realized-cost ledger;
4. the hard-cap reservation rule or a declared soft-cap rule;
5. the stopping, tie-breaking, confirmation, and audit attachment rules.

Run methods in isolated ledgers. If one physical trace is used as a simulator,
reset every method to its registered initial knowledge; a later method cannot
inherit a previous method's free observations. For the hub method, reuse is
within that method's ledger and is counted once. For baselines, give each
method the same opportunity to reuse exact observations allowed by its own
declared protocol.

The primary table should then report: realized search spend, reserved spend,
overshoot (zero under a valid hard cap), number of paid complete cells, number
of reused hub cells, selected-row held-out quality, and confirmation failures.
The current Table-7-style report is a useful presentation layer, but its cost
savings column must be renamed or qualified until this online ledger contract
is implemented.

## Consequence for the contribution claim

This audit does not create a new bandit method. It identifies the experimental
condition needed to test the narrower claim: a shared, answer-key-blind hub
can amortize complete retry-row measurements across many candidate rows under
realized, path-dependent charges. Without the ledger and the hub-vs-baseline
initial-knowledge contract, a positive replay result could be an artifact of
post-hoc matrix access, unequal cap semantics, or free cache inheritance.
