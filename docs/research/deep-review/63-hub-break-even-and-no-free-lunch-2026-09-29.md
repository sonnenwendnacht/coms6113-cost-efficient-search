# Hub break-even and the no-free-lunch condition

The shared hub only helps if its paired residual is more informative per paid
candidate cell than an honest cached-incumbent comparison. Let `h` be the
incumbent hub and `c` a challenger on the same registered question. A simple
paired estimator has variance

```text
Var[D_Q(c,q)] = Var[Q_c] + Var[Q_h] - 2 Cov[Q_c,Q_h].
```

An independent comparison to a well-known hub mean has variance approximately
`Var[Q_c]` per candidate question. Pairing is then useful only when
`Var[Q_h] < 2 Cov[Q_c,Q_h]`; with comparable variances this requires a
correlation above one half. If the hub's mean is still uncertain, the proper
comparison includes its confidence width and may favor direct incumbent
refresh instead.

For `J` challengers, the search ledger must compare

```text
hub_cost + sum_j n_pair(j) * candidate_charge(j)
```

against the cached-incumbent baseline receiving the same initial hub cells,
question permutation, reservations, and direct confirmation. A baseline that
reruns the incumbent for every challenger is not a valid cost comparison; a
baseline that already has the same cache may erase the hub's call-saving
advantage. The remaining possible gain is lower uncertainty, better
allocation, or fewer finalist confirmations.

The same condition applies to cost residuals, but path-dependent reach can
make `Cov[K_c,K_h]` negative. HAPR should estimate covariance on a calibration
block and disable residual transfer when the one-sided variance-reduction
condition is not supported. A row-coordinate distance or embedding can choose
the hub candidate, but it cannot substitute for this observed break-even
check.

This is a falsification rule, not a theorem of universal superiority. Report
cases with weak or reversed covariance, where HAPR falls back to independent
cost-aware racing, alongside cases where the paired hub reduces profiling
spend at matched held-out quality.
