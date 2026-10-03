# Generation–verification allocation prior art

The prior-art audit found a close 2026 result that must be cited before we
claim that solver and verifier retries create a new cost-allocation problem.
Dughmi, Haghifam, and Kalayci's [Adaptive Generate-Rank-Verify (ADAP)](https://arxiv.org/html/2605.17609)
models inference for one prompt as active search. A generator produces
candidates, a cheap reward ranks them, and a costly verifier is applied until
a positive result is found. The paper explicitly charges generation and
verification separately, adapts their counts, and proves a constant-factor
bound under a monotone reward-to-verifier-success assumption.

This overlaps with the *within-question* decision in our workflow: whether a
later solver attempt or another verification should be paid for. It does not
solve the group project's selection problem. ADAP has one prompt at a time and
returns a verified answer; it does not choose one complete row of solver and
verifier assignments across a finite benchmark. It also does not reuse a
same-question observation from one row to compare another row, model retry
composition, or charge a complete row whose later calls are triggered by an
answer-key-blind verifier.

The distinction must be stated carefully. “Joint generation and verification
under a cost” is no longer a novelty claim. The narrower proposed problem is
**outer configuration identification under inner generate–verify cascades**:

* a row fixes the model at every solver and verifier slot;
* a row pull returns final correctness (scored only after the run), the
  answer-key-blind PASS/RETRY path, and its realized charge;
* the path determines whether later calls occur, so the row charge is
  endogenous rather than a fixed generation-plus-verification constant;
* a hub can be evaluated once on a question stream and reused as a paired
  covariate when screening other complete rows; and
* the selected row still needs direct confirmation on a held-out block.

ADAP should therefore be cited as an adjacent inner-loop baseline or as a
possible deployment policy inside one row, not as a direct substitute for
row-level search. A fair comparison must distinguish an algorithm that chooses
the retry policy from an algorithm that merely chooses how many candidates to
generate for an already chosen policy.

## Consequences for evaluation

1. Include a within-row generate–verify allocation baseline if the deployment
   system permits it; otherwise state that retry counts are fixed by the row.
2. Charge all solver and verifier calls made by a row, including any final
   confirmation. Do not compare HAPR/CAPR against an inner-loop method that
   stops before the same correctness target.
3. Keep the answer key outside the verifier and outside the search policy.
   The final correctness label is an evaluation outcome, not a deployment
   signal available to ADAP or HAPR during the run.
4. Report the outer search cost separately from per-question deployment cost.
   A policy that finds a good row cheaply can still be inferior in deployment
   if its chosen row has a larger realized charge.

The paper's own formulation is useful evidence for this boundary: it defines
cost-sensitive active search as choosing `Generate` or `Verify` actions for a
single prompt and proves its result under a score-conditioned success model.
Our row-level claim must add the benchmark-level selection and shared-row
ledger, and must be tested against the strongest valid inner-loop comparator.
