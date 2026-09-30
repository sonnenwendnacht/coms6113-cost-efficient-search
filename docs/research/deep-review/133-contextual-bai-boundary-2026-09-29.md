# 133: Contextual BAI boundary (2026-09-29)

Kato and Ariu's 2026 [The Role of Contextual Information in Best Arm
Identification](https://www.jmlr.org/beta/papers/v27/22-0358.html) studies
best-arm identification when a context is observed before choosing an arm and
the reward depends on that context. Its target is the best arm's mean after
averaging over the context distribution, and its context-aware Track-and-Stop
allocation has matching lower-bound analysis.

This prevents us from presenting question difficulty alone as a new source of
structure. A MathQA question can be treated as a finite context, and a full
configuration row as an arm. The important differences are narrower:

* the search trace has a registered finite question bank rather than an
  unknown context stream;
* several complete rows are run on the same question, creating paired
  residuals instead of receiving one arm's contextual reward per round;
* the final verifier decision controls whether later retry attempts occur, so
  realized cost is a response-dependent cell outcome; and
* the deployment objective is a row recommendation under profiling spend,
  followed by evaluation on a separate held-out question set.

The fair baseline set should therefore include a context-aware allocation
method where feasible, alongside direct paired elimination and PROBE-style
residual calibration. The proposed graph method must not select questions
because they appear easy after observing outcomes; it can use predeclared
question metadata or a fixed permutation, and it must report the finite-bank
target explicitly. Any extension that merely feeds question features into UCB
is contextual BAI prior art rather than the project's central novelty.

No implementation or experiment is claimed by this note.
