# Inference corrections for complete-row search

Prepared 2026-09-29 during a research-only audit. This note corrects claims in
deep-review notes 08, 09, 10, 11, and 13. It reports no new run and does not
claim a theorem for the current prototypes. The corrections are intentionally
recorded here rather than silently rewriting the dated notes; the older notes
remain useful design history, but should not be quoted without these limits.

## The measured search quantity in the current replay

The workflow has two different per-attempt indicators:

```text
A(c,q,j) = checker decision (accept/pass versus retry) at attempt j
Q(c,q)   = final_correct after the completed path, scored with the answer key
K(c,q)   = input-token charge for the reached path
```

`A` controls whether the replay reaches another attempt. It is the deployable
checker signal and is kept answer-key blind. `Q` is the ground-truth outcome
used to measure a completed search cell after the workflow has run; it must not
be returned to the search policy while it chooses the next cell. `K` records
the reached calls. This is the behavior in [`replay.py`](../../../src/retry_search/replay.py)
and in the nine-model loader, which constructs search rewards from
`final_correct` ([`replay_experiment1_nine_model.py`](../../../scripts/replay_experiment1_nine_model.py)).

Thus the measured row target for the replay is

```text
mu(c) = E_q[Q(c,q)]
```

or the corresponding finite search-population mean. A note that defines `Y`
as the answer-key-blind checker outcome, or says that the answer key is used
only on the held-out audit, describes a different target. The selector remains
checker blind during search; offline scoring of search cells with `Q` is not
the selector seeing the answer key. Held-out audit questions must still remain
unseen until the recommendation is frozen.

This distinction is operationally important: checker success is not a valid
surrogate for answer correctness unless that surrogate relationship is a
registered assumption and measured separately. A retry that is accepted can be
wrong, and a rejected attempt can be correct. All selection curves in the
current replay therefore use `final_correct` as the measured reward, while
`accepted` explains path length and cost.

## Corrections to dated claims

### Cost feasibility has two opposite one-sided tests

Notes 08 and 13 use the right quality-elimination direction in places, but the
cost language is easy to reverse. Let simultaneous cost bounds be
`[L_K(c), U_K(c)]` and let the deployment cap be `b`.

```text
definitely feasible:       U_K(c) <= b
definitely infeasible:     L_K(c) >  b
unresolved at the cap:     L_K(c) <= b < U_K(c)
```

The second line is the safe *infeasibility* certificate: the lower confidence
bound already exceeds the cap. An upper bound exceeding the cap only says that
feasibility is not yet certified; it is not proof of violation. Conversely, a
policy that admits only certified-feasible rows should require `U_K <= b` and
leave the middle case unresolved. Therefore:

* [08, lines 181–186](08-similarity-theory-2026-09-29.md) should say that a
  row is rejected as infeasible only when `L_K(c) > b`; use `U_K(c) <= b` when
  the rule is conservative admission.
* [13, lines 77–80](13-correlated-resource-bai-theory-2026-09-29.md) should
  replace “reject a row when its upper cost bound violates the cap” with the
  same distinction. `U_K>b` is an unresolved certificate, not an observed
  violation.
* In [09, lines 99–102 and 124–142](09-hpo-alternatives-2026-09-29.md), an
  upper cost quantile is an acquisition/scheduling forecast. It is not a
  confidence bound and cannot by itself certify either feasibility or
  infeasibility.

For quality, the direction is different. If `b` is an incumbent and larger is
better, eliminate `c` for an additive tolerance `epsilon` only when

```text
U_mu(c) < L_mu(b) - epsilon.
```

This is why “UCB below incumbent LCB” is correct for quality, while “LCB above
cap” is correct for proving excessive cost. A row that is not certified
feasible must not be silently treated as infeasible.

### Fixed blocks do not, by themselves, cure optional stopping

The following statements are too strong:

* [08, lines 54–57 and 121–125](08-similarity-theory-2026-09-29.md) imply that
  checking a fixed-sample radius only between complete blocks is sufficient.
* [10, lines 105–109](10-similarity-gated-row-exploration-2026-09-29.md)
  presents decisions at `m, 2m, 4m, ...` as a safe default without an error
  allocation.
* [13, lines 92–100](13-correlated-resource-bai-theory-2026-09-29.md) says one
  may use a fixed radius and stop at preregistered block boundaries.

If the final block count is fixed independently of outcomes, a fixed-sample
interval is valid. If the procedure may stop at one of several block counts
after looking at outcomes, the stopping boundary is data dependent. Valid
options are a confidence sequence, an explicitly alpha-spent sequence of
fixed-look intervals, or a fixed final count selected without outcome data.
“Only stop between blocks” is a useful accounting rule, but it is not a
statistical correction.

For a finite benchmark, pre-draw a question permutation and use a simultaneous
without-replacement bound for every permitted prefix. If stream `s` has range
width `w_s` and prefix size `n`, a generic bound has the form

```text
P(for some permitted n: |mean_s(n) - mu_s| > r_s(n)) <= alpha_s,
```

where `r_s(n)` uses the finite-population correction and a summable allocation
`alpha_{s,n}` (or a published without-replacement confidence sequence). For
`Q`, `w=1`; for a paired difference `Q(c',q)-Q(c,q)`, `w=2`. At a full census
`n=N`, the finite benchmark mean is known exactly, regardless of a loose
concentration radius. For an external question distribution, a random
permutation of a fixed benchmark does not establish population validity; the
benchmark sampling design still has to be declared.

### Global versus pair-specific permutations

The notes overstate the claim that an adaptively opened pair must use a
disjoint cross-fitted block. A valid construction can precommit one independent
permutation for every registered direct or paired stream, allocate an error
budget to every stream and every prefix, and take the simultaneous event over
all streams before search begins. Choosing which stream to inspect next then
does not break that event. Exact cells reused from another stream remain
accounting reuse rather than independent samples, but the same cell need not be
discarded automatically.

There are two safe implementation choices:

1. Use a global permutation/block schedule and apply a simultaneous bound to
   all direct and paired streams. Track overlap and do not add reused cells as
   fresh independent observations.
2. Use disjoint or cross-fitted blocks when proving a simpler conditional
   argument, especially if an estimator pools cells from multiple streams.

What is invalid is generating a stream or selecting its included questions
after seeing their outcomes and then applying an ordinary random-sample
interval. A late row “catching up” can make coverage explicit, but catch-up by
itself does not make an outcome-selected subset independent.

### Variance gates and zero-variance edge cases

For a fixed pair, with `D=Q(c',q)-Q(c,q)`,

```text
Var(D) = Var(Q(c')) + Var(Q(c)) - 2 Cov(Q(c'),Q(c)).
```

Pairing has a variance advantage over two independent samples of equal size
only when `Var(D) < Var(Q(c'))+Var(Q(c))`; equivalently the covariance term is
positive enough. The sample gate in SCCR is an allocation heuristic unless its
finite-population, adaptive, time-uniform error is separately derived.

The “zero variance” case does not make the finite-sample cost zero. A sample
variance of zero can occur on a calibration stratum while unobserved questions
have nonzero differences. More generally, empirical-Bernstein radii retain a
range/logarithmic term, schematically

```text
r_n = O(sqrt(v_hat * log(1/alpha_n) / n)
        + w * log(1/alpha_n) / n),
```

so `v_hat=0` does not imply `r_n=0` before a census. The guide
`H(e)=k_e v_e / Delta_e^2` in [13, lines 48–58](13-correlated-resource-bai-theory-2026-09-29.md)
is only a leading, instance-dependent heuristic. A finite-sample complexity
must include range and confidence terms, a positive number of observations,
and the fact that `Delta=0` cannot be signed at any finite confidence level.
If an exact finite population has been fully enumerated, zero residual
variance is then a fact; it cannot be inferred from a zero sample variance
alone.

The numerical reversal example in [08, lines 203–214](08-similarity-theory-2026-09-29.md)
also has an arithmetic error. With four calibration values `(0,1,0,1)` and
the remaining 96 questions set to `A=1, B=0`, the full means are `0.98` and
`0.02`; the difference is `0.96`, not approximately `0.46`. The qualitative
lesson (a calibration stratum can reverse on the remainder) is unchanged.

### A dollar budget requires reservation, not a post-hoc check

“Admit a block under a known worst-case charge” in [11, lines 93–96](11-research-synthesis-2026-09-29.md)
and [13, lines 71–73](13-correlated-resource-bai-theory-2026-09-29.md) is
correct only if the envelope includes every reached call, output/context cap,
checker/tool charge, and any parallel branch. A hard-budget rule must reserve
before starting:

```text
spent + reserved + max_new_action_charge <= B.
```

If no defensible finite envelope exists, a realized-cost loop such as the one
shown in [09, lines 168–181](09-hpo-alternatives-2026-09-29.md) can overshoot
`B`; label that budget soft and report the overshoot. A cell/block budget can
be hard without a dollar envelope, but its dollar total remains a measured
random quantity. Outcome-dependent truncation of a question stream can also
change the question distribution, so it cannot be repaired by merely reporting
the final spend.

## Similarity, models, and unobserved rows

The repeated sentence that similarity “cannot estimate an unvisited row” needs
one qualification. Same-question pairing or a graph residual does not identify
an unmeasured row by itself. A structural model can produce a *prediction* for
an unseen row, and a theorem may turn that prediction into a bound under an
explicit model and misspecification radius. Such a prediction is not a measured
cell, an exact row mean, or an independent cache hit. The safe wording is:

> Similarity alone cannot identify an unvisited row. Model-based predictions may
> prioritize or bound it under registered assumptions, but the empirical
> recommendation and any model-free certificate require direct observations.

This applies to [08, lines 33–41](08-similarity-theory-2026-09-29.md), [10,
lines 30–34](10-similarity-gated-row-exploration-2026-09-29.md), [11, lines
45–55](11-research-synthesis-2026-09-29.md), and [13, lines 68–70](13-correlated-resource-bai-theory-2026-09-29.md).
The robust-surrogate language in [09, lines 94–122](09-hpo-alternatives-2026-09-29.md)
is appropriate when its assumptions are stated; its interval is not evidence
that the row was executed.

## Recommended editorial action

Do not patch the dated notes in this audit. Add this correction note and link
it from any future synthesis or protocol. Before a confirmatory run, update the
active protocol to (i) use `Q=final_correct` as the offline measured search
reward while keeping `A` checker blind, (ii) register a simultaneous
finite-population or anytime confidence construction, (iii) state the two
one-sided cost rules, and (iv) reserve a hard dollar envelope or explicitly
call the budget soft. Existing prototypes should continue to be described as
heuristics; these corrections do not convert them into delta-correct methods.
