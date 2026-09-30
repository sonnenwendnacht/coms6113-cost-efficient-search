# Per-question compute allocation boundary

Zhai et al.'s [Adaptive Test-Time Compute Allocation](https://arxiv.org/html/2604.14853v1)
formulates a different but important problem: map each incoming question to a
number of samples under an average compute budget. A Lagrangian oracle chooses
the per-question budget, and a classifier learns to imitate it from cheap
features. The paper evaluates MATH and GSM8K with 200 questions each and
several budget levels.

This is a strong baseline if deployment is allowed to choose a different retry
budget for each question. It does not identify one global complete
solver/verifier/retry row from profiling data, and its budget action is a
sample count for one model rather than a verifier-gated assignment of model
choices across retry slots. It also assumes an accuracy-versus-budget table
for each question, whereas our search policy must obtain legal answer-key-blind
signals and later calls can be absent after PASS.

The project must state which policy class it recommends:

* **Global-row target:** choose one complete row before deployment. This is
  the target for HAPR/CAPR and the existing 729-row experiment.
* **Per-question target:** choose a retry/model action after seeing each new
  question. This is closer to adaptive compute allocation and routing papers,
  and it requires a context model, a different deployment budget, and a
  different held-out evaluation.

Comparing a global-row selector against a per-question policy without labeling
the distinction would make the result uninterpretable. If the group later
wants both, the per-question policy should be an explicitly separate extension
or baseline, not silently folded into Algorithm 2.
