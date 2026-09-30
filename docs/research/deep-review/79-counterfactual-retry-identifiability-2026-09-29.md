# Counterfactual retry identifiability

A complete row's final score is observable after its execution, even when an
individual later attempt is never invoked because the verifier stopped early.
The unexecuted attempt's hypothetical answer is not observed. Its labels are
missing because of the preceding verifier outcome, so they are not a row-level
reward matrix that can be averaged as if zeros or random missing values.

Without an absorbing/perfect checker, a continuation model with validated
support, or a randomized policy that sometimes forces the continuation, the
counterfactual question “what would retry 2 have done if the verifier had
continued?” is not identifiable from deployment logs. Algorithm 2 must estimate
complete-row final quality and realized path cost. It may use observed reach as
a covariate, but it must not infer an unexecuted retry's correctness from the
absence of a call.

This is also why a graph path is a measurement-prioritization device rather
than a license to fill an unpulled row. Direct complete-row confirmation is
required before recommendation.
