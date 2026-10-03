# LLMSelector and the monotonicity boundary

Chen et al.'s [LLMSelector](https://arxiv.org/html/2502.14815) is direct prior
art for the original hyperparameter-search analogy. It treats a static
compound AI system as a fixed directed acyclic graph, assigns one model to
each module, and seeks a high-performing allocation without enumerating every
combination. Its method cycles through modules and chooses the model with the
best estimated module-wise performance; under intra- and inter-monotonicity it
gives a linear-in-module call bound and an optimality result for the stated
model.

This rules out claiming that model assignment across agent stages, one-slot
changes, or greedy coordinate search is novel. It also provides a useful
negative control. The paper's assumptions are not automatically valid for our
retry rows:

* a verifier PASS removes later retry slots, so changing an early solver can
  change which later model is ever invoked;
* a retry prompt contains the previous answer and verifier feedback, so the
  effect of a later model depends on the earlier model and trajectory;
* final correctness is not a monotone sum of independently measurable module
  scores; and
* the LLMSelector diagnoser is given the desired answer in its module-wise
  assessment, while our deployed verifier/search policy must not see the
  MathQA key.

Thus a coordinate method can be a baseline, but its monotonicity theorem does
not transfer to the answer-key-blind retry cascade. HAPR/CAPR should not claim
to improve because it “uses similarity” in the abstract. The narrower claim
would be that paired complete-row evidence can identify useful replacements
when module-wise monotonicity fails, provided the path support and confirmation
gates pass.

## Falsification test implied by this overlap

Construct a small paired example in which changing only the first solver
changes the verifier verdict and therefore changes whether the second solver
is reached. If the coordinate ranking predicts the same slot ordering in both
contexts, it is using an assumption the workflow does not satisfy. The
research record should report such violations rather than silently applying
LLMSelector's theorem to retry rows.
