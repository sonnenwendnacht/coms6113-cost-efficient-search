# Complete-row anchor control variate without prefix reuse

The most promising no-prefix similarity mechanism is a complete-row control
variate. Pick an anchor row `h` and run its full retry workflow on a registered
question block. For a leader `l` and challenger `x`, directly run both complete
rows on the same fresh questions and form

```text
D(q) = Y_x(q) - Y_l(q).
```

If the already-paid anchor score `Z(q)=Y_h(q)` is available on those questions,
fit a coefficient `beta` on a pilot split and estimate the pair difference with

```text
D_cv(q) = D(q) - beta * (Z(q) - mean(Z)).
```

The estimate remains unbiased when `mean(Z)` is fixed from an independent
split, a fully profiled finite bank, or cross-fitting. It uses only complete
row/question outcomes; no model output, checkpoint, prefix, or unexecuted
retry is reused. The anchor is a statistical hub, not an execution shortcut.

Count the anchor fairly. If it is the current leader and its cells are already
paid by the direct paired baseline, the control variate adds no extra workflow
cost. If it is a separate hub, its complete-row profiling and fresh anchor
cells are additional paid work. A few observed leader cells do not make its
mean known; use a pre-sized independent estimate or cross-fitting.

## Cost condition

Let `v_D` be the paired difference variance, `v_R` the residual variance after
the control variate, and `v_Z` the uncertainty of the anchor mean. With per-
question charges `c_D` and `c_Z`, a sub-Gaussian half-width calculation gives a
cost proportional to

```text
(sqrt(c_D * v_R) + |beta| * sqrt(c_Z * v_Z))^2.
```

Direct paired racing costs approximately `c_D * v_D` at the same confidence
width. The control variate can therefore save profiling money only when its
residual reduction and anchor cost satisfy this inequality. If the anchor mean
is already known, any nonzero covariance can help; if it must be estimated at a
comparable cost, the covariance must be strong enough to amortize that cost.

Conditionally, if question draws are uniform from the registered bank, `beta`
is fixed on an independent pilot, and the anchor mean is estimated from `m`
independent anchor questions, then

```text
E[D_cv] = E[D],
Var(mean(D_cv)) = v_R/n + beta^2 * v_Z/m,
```

where `v_R` is a residual per-question variance proxy and `v_Z` is a per-anchor-
question variance proxy. This is a control-variate identity, not a guarantee for an adaptively
chosen anchor. If the search stops on realized dollars, replace the fixed-sample
bound with an all-prefix confidence sequence.

For `K` pair races sharing one anchor mean, the anchor setup is amortized but
its uncertainty is shared. Under the same fixed-sample proxy, the cost to reach
variance target `t` is proportional to

```text
(sqrt(K * c_D * v_R) + |beta| * sqrt(c_Z * v_Z))^2 / t,
```

versus `K * c_D * v_D / t` for direct paired races. The anchor term is not
divided by `K` unless the design actually supplies independent anchor means;
simultaneous confidence accounting must retain the common uncertainty.

## Safe algorithmic use

1. Register the anchor and a pilot question split before outcomes are seen.
2. Estimate `beta` and its uncertainty only on the pilot; freeze it or
   cross-fit it for later blocks.
3. Use the control-variate residual to rank leader/challenger measurements per
   predicted dollar, but preserve a direct-racing/scout floor.
4. Use simultaneous confidence sequences for all adaptively opened pair streams
   and hub comparisons.
5. Recommend only a directly measured complete row, with independent final
   confirmation.

If the target is a quality-under-cost constraint rather than a predeclared
scalar utility, use separate control variates (or direct confidence intervals)
for quality and mean realized cost. A quality residual alone cannot certify
frontier feasibility; the final row must be directly checked on both quantities.

Required negative controls are zero-covariance rows, a costly anchor, a
permuted row-coordinate mapping, and a setting where direct paired racing is
already optimal. Same-question leader/challenger pairing already captures
their covariance; Hamming similarity alone provides no extra variance
reduction. If the residual or anchor uncertainty is not demonstrably smaller,
fall back to CW-PTT. This is a concrete hypothesis for Algorithm 2, not a
claim that row similarity alone provides free observations.
