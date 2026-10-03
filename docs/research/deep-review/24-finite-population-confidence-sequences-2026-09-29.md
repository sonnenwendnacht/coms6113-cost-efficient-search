# Finite MathQA population and confidence sequences (2026-09-29)

Research-only source audit; no experiments, traces, replays, or model calls.

Waudby-Smith and Ramdas, *Confidence sequences for sampling without
replacement*, NeurIPS 2020 / arXiv: [paper](https://arxiv.org/html/2006.04347),
give time-uniform Hoeffding and empirical-Bernstein confidence sequences when a
fixed finite population is revealed in a uniformly random order. The population
values are treated as deterministic; randomness comes only from the permutation.
The intervals remain valid at arbitrary data-dependent stopping times and become
exact when all units have been revealed.

This is a principled way to define the fixed-search-set target: each complete row
gets a precommitted random permutation of the 200 questions, and an adaptive
search may reveal a prefix of that stream. A paired comparison can use the same
permutation for two rows and a difference-valued confidence sequence. The result
does not justify adaptive selection of whichever questions look favorable after
observing outcomes. If question inclusion is chosen from prior outcomes, use
registered per-row streams, a valid predictable sampling design, or design-based
weights; otherwise the finite-population guarantee is lost.

This target must remain distinct from generalization to future questions. The
former is a finite-population mean; the latter requires a task-distribution model
and corresponding sampling assumptions.

