# 122: Reward-visibility contract (2026-09-29)

## The leakage risk

The trace records both an answer-key-blind verifier decision and a later gold
`final_correct` label. A real deployment selector can observe the verifier
decision, but it cannot observe the answer key. Feeding `final_correct` into a
selector is therefore an offline gold-visible oracle replay. It is useful for
diagnosing the best possible allocation on a fixed matrix, but it cannot be
presented as the deployed search procedure.

The distinction matters more for retry rows than for a one-shot model: a false
verifier pass changes whether later attempts are reached, and the resulting
cost and outcome are part of the row's behavior.

## Source-level repair

The replay script now accepts:

```text
--selector-reward final_correct   # explicit offline gold oracle (default for compatibility)
--selector-reward verifier_pass   # deployment-visible proxy
```

The latter derives a cell reward from the recorded answer-key-blind verifier
passes and keeps held-out `final_correct` evaluation separate. The report
metadata records the chosen reward contract so a table cannot silently mix
the two modes.

## Required reporting

For a deployment-faithful claim, run the selector on `verifier_pass`, freeze
its recommendation, then report on the same independent audit questions:

- gold held-out accuracy;
- verifier-pass rate and false-pass/false-retry rates;
- profiling dollars and overshoot;
- cold deployment cost and latency.

For a gold-visible diagnostic, label it as such and do not claim it models the
online search process. If the verifier proxy is weak, the result is evidence
about proxy optimization only; it does not identify the gold-best row.

No replay was run while adding this mode. The existing long trace and its
source data remain untouched.
