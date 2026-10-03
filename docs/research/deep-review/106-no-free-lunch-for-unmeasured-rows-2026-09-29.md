# No-free-lunch boundary for row similarity

Consider `K` complete retry rows, a finite search bank of `N` questions, and a
binary correctness matrix `Y(c,q)`. A selector may observe any paid subset of
cells and their realized charges. Suppose it recommends a row whose unobserved
cells are inferred only because the row is Hamming-close to observed rows.

## Indistinguishable-world argument

Let `O` be the cells observed by an adaptive selector, including its complete
quality/cost ledger. Construct two finite matrices `M` and `M'` that agree on
all cells in `O` and have identical observed costs. For an unobserved row `u`,
set its unrevealed correctness cells to zero in `M` and to one in `M'`; choose a
second row's unrevealed cells so that the best row differs between the two
worlds. The selector receives exactly the same transcript in both worlds, so it
must output the same row, and therefore errs in at least one world.

The construction still works if `u` differs from a measured row in one model
slot, if the observed rows have perfect same-question correlation, or if all
unobserved costs are assigned the same legal values. Hamming distance and
observed covariance alone do not rule out the two worlds.

This is why a distribution-free method must recommend a directly measured row,
or explicitly assume a smoothness/factorization/proxy model and account for its
bias. A graph proposal can improve which rows get paid; it cannot certify an
unpaid row by itself.

## What paired similarity does buy

For two rows that are both run on the same question, the residual
`D_ab(q)=Y(a,q)-Y(b,q)` has variance

```text
Var(D_ab) = Var(Y_a) + Var(Y_b) - 2 Cov(Y_a,Y_b).
```

A positive covariance can reduce the samples needed to decide their ordering.
That is a comparison-efficiency result for observed complete rows. It does not
supply values for an unobserved row. A hub/control-variate version has the same
limit: the anchor can reduce residual variance, but its mean and coefficient
must be estimated and its uncertainty is shared across candidates.

## How a structural theorem would change the result

A positive transfer guarantee needs an assumption such as

```text
|mu(c) - mu(c')| <= L * d(c,c')
```

or a validated factor/low-rank model with a stated prediction-error bound. The
constant `L` or the model error cannot be chosen from the held-out audit set. It
must be known, conservatively bounded from a calibration split, or treated as a
sensitivity parameter. The confidence interval for a proposed row then contains
both sampling uncertainty and structural bias; if that interval overlaps a
measured competitor, the algorithm must pay for a direct probe.

A verifier-gated retry path makes a casual smoothness assumption especially
risky: changing an early solver can alter whether later attempts execute, so a
one-slot change need not produce a small change in final correctness or cost.

## Algorithmic consequence

Algorithm 2 should use similarity in one of two limited ways:

1. **Proposal/measurement allocation:** rank complete rows or paired edges by
   measured residual information per dollar, while retaining a global scout and
   directly confirming the recommendation; or
2. **Model-based transfer:** expose a structural bound and add its uncertainty
   to every inferred row interval, with a fail-closed direct-measurement fallback.

The first route needs no unverified smoothness theorem and is the recommended
initial claim. The second may save more calls but is a separate hypothesis that
must be compared with structured BAI and falsified under permuted or adversarial
row landscapes.
