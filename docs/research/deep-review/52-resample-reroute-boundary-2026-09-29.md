# Resample-or-reroute boundary

[Resample or Reroute?](https://arxiv.org/html/2607.08665) is the closest
minimal-retry comparator found so far. It allocates a per-question budget
between resampling a committed model and rerouting to another model, uses an
imperfect verifier and marginal-correctness-per-cost rules, and reports
cost--quality curves from precomputed multi-draw correctness tensors with
early stopping and provider prices.

This paper rules out claims such as “we are the first to use a verifier to
allocate retry calls,” “we optimize resampling versus model switching under a
budget,” or “we report cost--quality curves for retrying LLMs.” Its action is
online and per question: it assumes the available draws and per-query model
outcomes can be replayed, then chooses a sequence for that question.

HAPR has a different outer target. Before deployment it recommends one fixed
complete row (model at each retry slot plus verifier) from a finite set using
sparse benchmark executions. The search sees only paid answer-key-blind cells,
records realized path-dependent input-token charge, and may use a hub only for
same-question paired residuals when both complete rows have actually run. RoR
should therefore be a required baseline or oracle-informed comparator, while
HAPR must not inherit its precomputed tensor as though it were live evidence.
