# No-prefix paired Top-Two control

The reach identity is only useful when a comparison has a legitimate shared
prefix or a cheaper screening operation. Under the stricter no-prefix
constraint, the clean control is **Cost-Weighted Paired Top-Two (CW-PTT)**:

1. Reserve a fixed scout fraction and give every row a balanced block of
   uniformly shuffled questions.
2. Maintain a leader and a challenger using complete-row accuracy and cost
   confidence intervals.
3. On a fresh common question block, run both complete rows, compute the paired
   difference, and charge both realized path costs.
4. Spend the next block on the most uncertain leader/challenger comparison per
   expected dollar, while preserving a random challenger floor so rows cannot
   disappear permanently.
5. Stop when the leader's lower bound beats every challenger upper bound by the
   registered tolerance, or when the profiling budget is exhausted.

CW-PTT uses same-question covariance without assuming that a suffix would have
   produced the same answer. It is therefore a necessary baseline for a graph
   or reach-aware method. A structural method should beat it only when it shows
   a measured cost/variance/amortization advantage; similarity by Hamming
   distance alone is not enough.

The proposed Algorithm 2 can be presented as CW-PTT plus a certified structural
sidecar: use row coordinates and paired residual predictions only to prioritize
the next directly sampled comparison, retain the scout floor, and let only
directly observed complete rows enter the recommendation. If the structural
residual radius is too wide or the coupling assumptions fail, the sidecar
automatically collapses to CW-PTT. This gives one interpretable improvement
source and a meaningful ablation rather than a graph-only selector that can
recommend an unobserved row.
