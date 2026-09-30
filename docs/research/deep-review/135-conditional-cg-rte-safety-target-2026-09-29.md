# 135: Conditional CG-RTE safety target (2026-09-29)

The useful theorem target is a safety statement, not an unconditional claim
of savings. Let (V) be a finite row set and let every question stream use
the same registered target distribution (uniform over a finite bank, or a
predeclared weighted design). For each row (v), let

\[
\mu_v = \mathbb{E}[Y_{v,Q}],
\]

where (Y_{v,Q}) is the terminal reward of a complete retry cell. For each
registered edge (e=(u,v)), define

\[
\Delta_e = \mathbb{E}[Y_{v,Q}-Y_{u,Q}].
\]

Then (mu_v=mu_u+Delta_e), and the signed edge sums telescope along any
path from an anchor (a) to (v).

Assume that, with probability at least (1-delta), all direct row estimates
and all registered edge residual estimates satisfy simultaneous anytime bounds

\[
|\widehat{\mu}_a-\mu_a|\le r_a(t),
\qquad
|\widehat{\Delta}_e-\Delta_e|\le s_e(t)
\]

for every time at which CG-RTE may inspect them. On this event, a path estimate

\[
\widehat{\mu}_v=\widehat{\mu}_a+
\sum_{e\in P(a,v)}\operatorname{sign}(e)\widehat{\Delta}_e
\]

has error at most

\[
r_a(t)+\sum_{e\in P(a,v)}s_e(t),
\]

or a smaller jointly valid covariance radius when cross-edge dependence is
explicitly handled. Therefore, if a candidate's upper bound is below the
incumbent's lower bound by more than epsilon, eliminating that candidate is
safe on the simultaneous event. A final row surviving all such eliminations is
epsilon-best over the registered finite bank, provided the recommendation is
made from a complete common sample or a direct confirmation block.

The proof needs four non-negotiable details:

1. Edge streams must target the same question distribution. An adaptive choice
   of cheap or easy questions changes (Delta_e); fixed random blocks or
   valid importance weights are required.
2. The confidence event must cover every edge that can be opened and every
   optional stopping time. Per-edge fixed-sample intervals are insufficient
   after adaptive path selection.
3. A partial block cannot be used for elimination. It may be retained in the
   ledger, but ranking must use a previous complete common sample.
4. The quality event says nothing about budget safety. A hard-dollar result
   additionally requires deterministic upper charges and atomic reservations
   before each complete block. A realized-cost result reports observed spend
   and overshoot only.

This target deliberately does not assert that CG-RTE costs fewer dollars than
direct racing. Any savings theorem would need an instance condition showing
that already-paid anchor measurements are reused across enough candidates, or
that residual widths reduce the required candidate cells enough to offset the
endpoint charges. That condition is empirical and workload-dependent.

No implementation or experiment is claimed by this note.
