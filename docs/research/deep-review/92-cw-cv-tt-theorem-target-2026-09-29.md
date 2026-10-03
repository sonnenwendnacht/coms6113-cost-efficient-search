# CW-CV-TT theorem target and missing proof

The strongest honest theory target is conditional, not yet a proved result.
For a registered finite row set, define one observation of row `r` on question
`q` as the complete deployment-defined trace

```text
X_r(q) = (Y_r(q), K_r(q), R_r(q)),
```

where `Y` is final answer-key correctness, `K` is realized path charge, and
`R` contains verifier/reach metadata. A possible theorem would assume:

- questions are uniform from a fixed bank, or sampling weights are known;
- every compared row is fully executed on the sampled question under the same
  retry/checker policy;
- pair and anchor choices are predictable from past observations;
- control coefficients are fixed on an independent pilot or cross-fitted;
- utilities and costs are bounded or have stated sub-Gaussian/tail controls;
- a simultaneous covariance/residual confidence set remains valid under the
  stopping rule; and
- deployment feasibility is certified with a separate cost interval.

Under those assumptions, a desired result would be a `delta`-correct
epsilon-best complete row, with an instance-dependent charge bound that
improves over direct CW-PTT only when the conservative control-variate gate
passes. The proof would combine a time-uniform residual confidence sequence,
the anchor-mean error, predictable cost accounting, and a union budget over
pair streams and anchors.

The current project has not proved this theorem. It is false or unidentifiable
without the assumptions: unexecuted retries cannot supply `Y`, selected
reached-only questions bias covariance, changing verifier policies break
stationarity, and random dollar stopping invalidates fixed-sample intervals.
Therefore CW-CV-TT remains an empirically testable gated adaptation until a
formal proof or a deliberately weaker observed-path guarantee is completed.
