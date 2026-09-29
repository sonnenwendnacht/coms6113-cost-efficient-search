# Complete-row arm formalization

The prior-art boundary is easiest to preserve with an explicit observation
object. Let `c` be a complete assignment of solver and verifier models to all
retry slots, and let `q` be one registered benchmark question. One deployment
execution returns

```text
X(c, q) = (Q(c, q), K(c, q), R(c, q))
```

where `Q` is final correctness measured after the run, `R` is the set of
solver/verifier calls that were actually reached, and

```text
K(c, q) = sum(model_price(call) * input_tokens(call) for call in R(c, q)).
```

The verifier sees no answer key. The observable search history contains the
candidate outputs, verifier verdicts, feedback, token counts, and charges; the
evaluator later attaches `Q` from the benchmark key. For a stochastic API,
`X(c,q)` is a coupled trajectory draw. For the pinned greedy local trace, it is
a finite-population cell value, but that does not turn an unobserved cell into
free evidence.

This notation exposes why retry rows cannot be treated as a collection of
independent attributes. If the first verifier returns PASS, the retry solver
call is absent. If it returns FAIL, the retry prompt contains the previous
answer and feedback. Therefore the distribution and charge of a retry slot
depend on the earlier trajectory. Sampling that slot in isolation changes the
deployment policy and does not identify `X(c,q)`.

The row-level target must be declared before search. The simplest target is

```text
c* = argmax_c E_q[Q(c, q)]
```

over a finite registered question set or a declared future-question
distribution. A cost-quality frontier or a constrained target is also valid,
but it must not be silently substituted after seeing the trace. Search spend,
selected-row deployment charge, and held-out audit quality are separate
quantities.

For a hub `h`, a paired screening observation is

```text
Delta(c, h, q) = Q(c, q) - Q(h, q),
```

and the hub cell may be reused only when it was already paid for on the same
registered `q`. This is a control-variate/common-random-number comparison,
not a side observation that reveals the candidate. The paired estimator can
certify a difference; it does not certify an unexecuted candidate row. Hence a
headline recommendation needs directly observed finalist evidence and a
fresh confirmation block, with those calls included in the search ledger.

## Theory target and failure mode

The minimal theorem target is conditional rather than universal: under a
registered finite-population question stream, bounded row charges, a
predeclared hub or cross-fitted hub, and simultaneous paired confidence
sequences, the ledger algorithm never eliminates a row whose mean is within
the declared tolerance except with probability `delta`. A second result can
bound the extra charge relative to direct paired racing when the hub residual
variance and amortization satisfy an explicit break-even condition.

If the hub is selected from the same correctness outcomes, if the residual
calibration is not cross-fitted, if charges are not reserved conservatively,
or if the candidate has no direct support on the fold where its retry path
differs, the theorem does not apply. The algorithm must then report “not
identified” or fall back to direct row pulls rather than presenting a
surrogate recommendation as certified.
