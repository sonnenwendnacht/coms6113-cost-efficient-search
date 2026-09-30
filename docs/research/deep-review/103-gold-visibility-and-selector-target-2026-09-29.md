# Gold visibility and the selector's actual target

The retry workflow and the offline selector have different information boundaries.
The verifier prompt is constructed from the question and solver response; it does
not receive the MathQA answer key. After the workflow completes, the runner
compares the parsed final answer with the local `correct` field and records
`final_correct` in the trace. This distinction must be explicit in Algorithm 2.

## Two valid protocols

**Offline benchmark protocol.** A complete paid search cell reveals
`final_correct` to the selector only after the full workflow and cost ledger are
finished. The answer key is never available to the solver or verifier during
execution. In this protocol, paired confidence bounds target the true
finite-search-bank correctness mean, and the held-out audit bank remains hidden
until recommendation.

**Deployment-feedback protocol.** If the selector sees only the verifier's
accept/retry decision, its reward is verifier success, not answer-key
correctness. A confidence bound then certifies the best verifier-proxy row. It
cannot be relabeled as a gold-accuracy guarantee without a separate calibration
model, audits, or propensity-weighted gold observations.

The experiment report must name which protocol each selector uses. Mixing
verifier outcomes during search with gold correctness during evaluation produces
an ambiguous target and can make an apparently successful algorithm impossible
to reproduce.

## Consequences for similarity methods

A same-question residual is valid for whichever reward is actually observed:
`Y_gold(a,q)-Y_gold(b,q)` in the offline benchmark protocol, or
`Y_verifier(a,q)-Y_verifier(b,q)` in deployment feedback. Correlation in the
verifier proxy need not match correlation in gold correctness. Hamming-neighbor
variance diagnostics and Cost-SySR confidence allocation must therefore be run
on the selector-visible reward, while held-out gold accuracy is reported as a
separate deployment metric.

For the current local trace, `final_correct` is computed only after the complete
workflow, and the verifier remains key-blind. The safest paper wording is
“answer-key correctness is an offline profiling signal revealed after each paid
cell; the verifier is blind during deployment.” If a future API experiment
cannot expose gold labels after each search cell, switch all elimination and
confidence claims to the verifier proxy and reserve gold labels for held-out
audit.
