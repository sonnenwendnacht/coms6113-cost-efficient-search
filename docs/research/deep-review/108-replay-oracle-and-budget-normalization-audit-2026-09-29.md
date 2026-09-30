# Replay oracle and budget-normalization audit

The nine-model replay is a post-hoc fixture, not yet an online API experiment.
That distinction affects both leakage claims and Table-7-style cost comparisons.

## What the replay currently does correctly

- `validate_trace_rectangle` checks that every row/question cell exists exactly
  once and separates the 200 search questions from the 200 evaluation questions.
- `run_sweep` records observations through `_pick_cell`; its policies use only
  pulled search cells for their decisions and never receive the evaluation
  matrix.
- The held-out row accuracy and cold cost are attached only after a selector
  returns a row.
- Structured selectors receive explicit slash-decoded row slots rather than
  inferring coordinates from a shuffled row index.

These checks support a leak-free **simulation** when the selector implementation
continues to access values only through the pull path.

## What is not an online budget contract

The replay constructs full `rewards` and `costs` arrays in memory. This is
convenient for deterministic replay, but an online implementation needs a cell
oracle that exposes only the requested complete cell. The full fixture must never
be treated as permission to inspect an unpulled reward or cost.

For structured methods, the replay sets each cap to
`fraction * exhaustive_search_cost`, where the denominator is computed from the
entire search matrix. An evaluator may use that denominator after the fact to
plot a normalized curve, but a live selector cannot know it without measuring
all cells. The algorithm itself must receive a declared dollar cap, a declared
cell cap, or an externally supplied normalization constant; it must not infer an
unseen exhaustive cost from the trace.

The standard `run_sweep` methods use cell fractions and ignore cost when choosing
pulls, then report their realized cost. Structured methods use realized-cost
fractions. Comparing their rows at the same fraction therefore does not mean
comparing equal search dollars. A fair report must either:

1. compare every method at a common realized-dollar grid, taking the latest
   recommendation whose completed ledger is below each grid point;
2. wrap every method in the same safe-reservation dollar budget; or
3. label the curves as separate cell-budget and cost-budget analyses.

A method may use the full matrix only in a post-hoc oracle/reference calculation,
never in its acquisition, stopping, or recommendation logic.

## Required online adapter

Before a real API or held-out claim, expose an oracle with
`pull(row, question) -> (quality_signal, realized_charge)` and a ledger with
reservation, stream, and question metadata. The replay can implement that oracle
with a fixture-backed wrapper. Add a fail-fast guard that raises if a selector
accesses a matrix entry outside `pull`; otherwise a deterministic fixture can
hide look-ahead bugs.

Keep the exhaustive reference separate from selector input. Its best row and
full cost are reporting quantities on the finite bank, not free evidence. This
adapter is compatible with the no-prefix requirement: only exact, already-paid
complete cells may be reused.
