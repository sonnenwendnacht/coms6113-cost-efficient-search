# Verifier blind spots and independent audit

[Cheap Verifiers, Large Blind Spots](https://arxiv.org/html/2609.01345)
shows that a cheap verifier can make a cascade appear reliable while its
answer-key-based error is much larger. It measures false-accept blind spots
with a withheld gold oracle and reports a nontrivial cost tradeoff when a
stronger verifier is used.

This changes what the experiment must report. A verifier PASS rate is not the
primary quality outcome. For every selected row, report held-out gold
correctness, verifier-pass rate, false-accept and false-reject rates when the
gold audit is available, and the realized path charge. The answer key may be
used only after the deployment-style execution to form `Q`; it must not enter
the verifier prompt, the hub residual, or stopping decisions. The independent
audit split is therefore a validity requirement, not just another accuracy
sample.

The paper studies verifier/cascade reliability rather than finite-row search.
It is a required execution-side baseline and a reason to reject any HAPR
variant that chooses a row from verifier agreement alone.
