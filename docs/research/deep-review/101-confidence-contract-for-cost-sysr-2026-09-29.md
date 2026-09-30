# Confidence contract for Cost-SySR

Cost-SySR is only statistically meaningful if its synchronized blocks preserve
the question-sampling design. The following contract separates what is valid
from what is merely a useful heuristic.

## Current trace target

The local runner calls `generate(..., do_sample=False)` for every solver and
verifier. Within this run, a question/row cell is therefore intended to be a
deterministic response and cost; the randomization is the search-question split,
its fixed shuffle, and the selector. The primary estimand is the finite-bank
mean over the registered search questions. It is not automatically an iid
estimate of performance on future MathQA questions. The untouched evaluation
bank is a separate held-out estimand.

This distinction matters for confidence claims: a valid finite-bank confidence
statement can support selection among the registered questions, while a future-
task claim needs another sampling model and another uncertainty term.

## Conditions for adaptive elimination

Let `Q_t` be the next question in one global random permutation and let
`D_ab(t)=Y(a,Q_t)-Y(b,Q_t)` for two active complete rows. A synchronized phase
must satisfy all of the following:

- every active row is evaluated on every question in the phase;
- the next block is chosen before seeing its outcomes and uniformly from the
  remaining search questions (or uses a pre-registered permutation prefix);
- no row is admitted late without either catching up on all earlier blocks or
  receiving an independent fresh stream;
- a budget boundary never stops halfway through a synchronized block;
- the stopping/elimination rule uses an anytime confidence sequence or a
  pre-sized phase union bound, not a fixed-`n` interval repeatedly checked at
  random times.

With these conditions, the pair residual has target mean
`mu_a - mu_b` for the finite search bank. A simple fixed-phase implementation
can allocate an error share `alpha_{k,a,b}` to every phase and active pair and
use a bounded finite-population interval. An anytime implementation must use a
valid without-replacement/martingale confidence sequence and a union allocation
across all registered pair streams. The current heuristic radius in the
prototype is not such a proof.

If the selector chooses a fresh question only after observing an earlier row's
cost or verifier result, the observed cells are outcome-dependent. They cannot
be treated as a representative sample of the row, and an unobserved retry is
not a failure. This is the main way a seemingly sensible cost-aware race can
become biased.

## Cost does not replace quality uncertainty

A cost observation can influence which complete block is affordable, but the
quality interval and the cost ledger remain separate. Under realized-spend mode,
finish the full block and report its actual charge, including overshoot. Under a
safe hard cap, reserve deterministic upper bounds for every new complete cell
before launch. In either mode, do not use the average cost as though it were a
known resource amount: verifier reach can couple `K(c,q)` to `Y(c,q)` and to
question difficulty.

Eliminate row `b` only when a simultaneous lower/upper comparison proves that
some active row `a` is better, for example `LCB(mu_a-mu_b)>0`; choosing `a` as
the empirical leader is safe only when all relevant pair intervals are covered.
At budget exhaustion without such a comparison, return the best directly
measured row and label the result exploratory rather than claiming
`delta`-correct identification.

## Practical recommendation

Use a global synchronized block design as the clean baseline. Add cost-aware
phase sizing only after verifying that its question order is outcome-independent
and that the confidence procedure remains valid at adaptive boundaries. Compare
against the same selector with a permuted row-neighborhood proposal, and report
finite-bank selection accuracy, held-out accuracy, actual profiling spend,
phase utilization, and cold deployment cost separately. This gives similarity a
measurable role without reusing workflow prefixes or silently changing the
estimand.
