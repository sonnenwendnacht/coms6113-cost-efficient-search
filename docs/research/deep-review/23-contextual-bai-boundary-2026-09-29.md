# Contextual BAI boundary for question sampling (2026-09-29)

Research-only source audit; no experiments, traces, replays, or model calls.

Kato and Ariu, *The Role of Contextual Information in Best Arm Identification*,
JMLR 27 (2026): [paper](https://www.jmlr.org/beta/papers/v27/22-0358.html), study
fixed-confidence BAI when each round reveals a context before an arm is chosen.
The reward depends on that context, but the target is the arm with the best mean
after averaging over the context distribution. They derive contextual lower bounds
and a context-aware Track-and-Stop allocation that asymptotically matches them.

In our problem, a MathQA question is naturally a context and
`Q(row, question)` is context-dependent. This creates two distinct targets:

* the best row on the fixed 200-question search set; or
* the row with the best expected quality over a task distribution.

An adaptive procedure that chooses which rows to run on each question should not
silently move between these targets. For the task-distribution target, question
sampling and row allocation form a contextual-BAI problem. For the fixed-set
target, the search is finite-population estimation and needs a corresponding
sampling/permutation argument. In both cases, same-question row pairs are batch
observations with shared context, so the covariance benefit is a side-observation
extension rather than ordinary independent-arm BAI.

Algorithm 2 documentation should state the target explicitly, reserve the hidden
audit set for final evaluation, and avoid claiming that a confidence interval on
the sampled search questions is automatically a confidence guarantee over unseen
questions.

