# Hidden-verifier retry and routing boundary

Two additional papers make the information boundary sharper.

Ray and Goyal's [VeriHarness study](https://arxiv.org/html/2607.14167) uses a
code-controlled model → external validator → feedback loop. The validator
controls acceptance, budgets, and traces; hidden HumanEval tests are used only
after the visible repair loop. Their experiment asks which failure feedback
helps repair under a call cap. This establishes that answer-key-blind retry
control, durable traces, and hidden post-hoc correctness are sensible
engineering boundaries, not a new contribution by themselves. It does not
search over model assignments or select one row across questions.

Chen's [Resample or Reroute?](https://arxiv.org/html/2607.08665) is closer to
the outer decision. It studies whether, after a weak verifier stop, a system
should resample or reroute, and explicitly separates recoverable stopping debt,
support for identifying the better action, and held-out value. The paper's
fail-closed lesson applies directly: an evaluator-only pointwise maximum or a
historical replay cannot license an outcome-blind deployable selector without
action support and held-out testing.

The difference from our proposed row search is the target and action object.
Chen's action is a next per-query resample/reroute after a declared stop; our
action is a complete solver/verifier/retry assignment selected before future
questions. A row's later retry slot may not exist after a PASS, and when it
does exist its prompt contains earlier output and verifier feedback. Therefore
the row is not decomposable into independently sampleable “attributes” or
stationary model pulls. Its observable is a coupled trajectory
`(final_correct, reached_calls, realized_charge)`.

## Protocol consequence

The Algorithm 2 paper should include a support gate before interpreting a
learned similarity transfer: every candidate transfer must have direct paired
observations on a registered question fold, and every headline recommendation
must have held-out direct confirmation. If the candidate has no observations on
questions where its retry path differs, the correct result is “not identified,”
not a favorable surrogate score. This is compatible with a finite-population
paired estimator, but it rules out silently treating the full brute-force
trace as if it were a deployable selector's information stream.

The practical claim is consequently conditional: HAPR/CAPR may reduce search
spend when same-question differences are predictable and the hub cache
amortizes across candidates, but it must fail closed when path support,
residual calibration, or confirmation budget is insufficient.
