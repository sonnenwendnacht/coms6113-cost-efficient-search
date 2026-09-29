# Reach-aware paired estimation and selection bias

The retry trace creates a subtle statistical issue that a generic “similar
rows” rule does not solve. The verifier determines whether later attempts are
reached, so the charge and reach vector are outcome-dependent. A row that
usually passes at attempt one can have a very different cost distribution
from a row that often reaches attempt three. The same question can therefore
produce a useful paired quality contrast while producing a structurally
different cost trace.

For a registered question stream, record each complete execution as

```text
X(c,q) = (Q(c,q), K(c,q), R(c,q), V(c,q))
```

where `Q` is the post-run gold correctness, `K` is the realized input-token
charge, `R` is the attempt-reach vector, and `V` contains answer-key-blind
verdict/feedback metadata. The search policy may see `K`, `R`, and `V`, but
not the gold label used to form `Q`. For a hub `h` and candidate `c`, use

```text
D_Q(c,q) = Q(c,q) - Q(h,q)
D_K(c,q) = K(c,q) - K(h,q)
```

only on questions for which both complete rows were actually executed. A
reach-stratified report additionally gives the finite-population means of
`D_Q` within observed `(R(h,q), R(c,q))` strata. It does not impute a missing
continuation or treat a first-attempt PASS as a separately sampled retry arm.

Question selection must be nonanticipating. A fixed permutation and predeclared
blocks are the simplest design; selecting the next question after observing a
candidate's quality or reach can bias the paired residual. If adaptive block
opening is needed, use an anytime finite-population confidence sequence or a
fresh independent block for confirmation. A standard fixed-sample interval is
not enough after optional stopping.

For quality-under-cost selection, maintain simultaneous confidence bounds for
the pair `(mean D_Q, mean D_K)` and for the hub's absolute mean. Eliminate a
candidate only when its utility upper bound is below the incumbent lower bound,
or when its conservative cost lower bound violates the deployment cap. Use
similarity only to prioritize which complete row to open and how much paired
uncertainty it may reduce; never turn it into a label for an unexecuted row.
The final recommendation still needs a direct fresh block, followed by the
held-out evaluation split.

This design is a practical refinement of common-random-number ranking and
finite-population confidence sequences, not a new confidence-bound theorem.
Its empirical claim can only be that reach-aware paired complete-row racing
reduces paid profiling spend under matched cached-incumbent accounting on the
declared workload; it cannot claim unbiased row prediction in arbitrary
adaptive traces without the sampling conditions above.
