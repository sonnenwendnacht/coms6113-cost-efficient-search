# 130: Similarity needs an amortization condition (2026-09-29)

Complete-row accounting imposes a useful sanity check on Algorithm 2. To
measure a paired edge ((i,j)) on one question, the system must execute both
complete configurations and pay both retry cascades. Similarity is therefore
not free neighbor feedback. If a path (i\to h\to j) is measured on the same
question, the residuals telescope, while the path pays for the intermediate
row as well. If the edge blocks are independent, interval widths add along
the path and the path is generally no better than directly measuring the
endpoint at the same number of calls.

The potential savings mechanism is **amortization**. Suppose an anchor row
already has a sufficiently precise estimate because it was measured for other
candidate comparisons. A new candidate can then be sampled on a smaller
paired block, using a gated residual to transfer the anchor estimate. The
incremental cost is mostly the candidate's calls, while the anchor's previous
calls are shared across several candidates. A useful gate should therefore
compare:

* the width of the anchor interval plus the held-out residual interval;
* the width of a direct candidate interval at the same incremental dollar
  cost; and
* the number of future candidate rows over which the anchor measurement will
  be reused.

If the anchor was not already paid for, or if only one neighbor is tested, an
edge measurement may cost as much as direct sampling and should not be sold as
a saving. A path with extra intermediate rows is especially suspect. The
algorithm should keep a direct-sampling fallback and log the estimated versus
realized incremental cost for every propagated decision.

This makes the plausible contribution a transductive allocation policy rather
than a new graph estimator: discover when a paid anchor can be reused safely
across complete retry rows, and stop propagating when the amortization or
residual-variance gate fails. Required ablations include a no-reuse graph
control, a direct paired baseline, and a shuffled graph with the same edge
degrees. The primary result must show savings at equal held-out quality and
equal realized accounting, not merely narrower confidence intervals.

No implementation or experiment is claimed by this note.
