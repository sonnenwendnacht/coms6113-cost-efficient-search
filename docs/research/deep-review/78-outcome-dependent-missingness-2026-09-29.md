# Outcome-dependent missingness in retry rows

## Source

Mahrooghi et al., *Multi-armed Bandits with Missing Outcomes*, UAI 2025, PMLR 286:2844–2875: [paper](https://proceedings.mlr.press/v286/mahrooghi25a.html).

The paper shows that ignoring missing outcomes, or treating them as random missingness, can bias reward estimates and can produce linear regret. It gives separate methods for missing-at-random and missing-not-at-random mechanisms.

## Consequence for retries

Later retry results are absent precisely when the earlier verifier accepted, rejected, timed out, or failed. Those missing entries are therefore outcome-dependent. We must not encode “no third attempt” as a zero-quality third attempt, average only the reached continuations, or treat the continuation matrix as randomly missing.

There are two safe choices:

1. Define the online target as the observable verifier-controlled utility and model the observation mechanism explicitly; or
2. Define final answer correctness on the complete row and use directly paid complete-row observations plus a disjoint gold audit. Any selective audit or reached-only estimator needs known/positive inclusion probabilities, inverse-propensity correction, or a conservative interval.

The proposed reach-stratified estimator is valid only for a declared sampling design. If it cannot estimate the reach probability or support is absent, it must return an uncertainty interval and fall back to CW-PTT. This is a direct reason to keep the structural component fail-closed.
