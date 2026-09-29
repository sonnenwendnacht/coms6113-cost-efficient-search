# Cost stopping and confidence sequences

Stopping when a realized-dollar budget is exhausted is informative stopping:
questions with long generations may consume the budget sooner, and realized
cost can correlate with correctness, reach, or difficulty. A fixed-sample
interval applied at the final number of completed questions is therefore not
enough for an adaptive cost-stopped run.

For each pre-shuffled question stream, use an all-prefix confidence sequence
(or a confidence sequence indexed by the charged cost with an explicit
martingale construction). Allocate error probability over every allowed
prefix and every structural stream. The stopping rule may then inspect the
current confidence bounds and cumulative charge without invalidating the
certificate. A fixed-`n` finite-population bound can still be reported for a
pre-registered, nonadaptive confirmation block, but it must not be described as
an anytime guarantee.

This is another reason to report both question count and actual search charge:
equal counts do not imply equal information or equal cost, and a cheaper
selector that stops earlier is only credible when its stopping-aware intervals
remain valid.
