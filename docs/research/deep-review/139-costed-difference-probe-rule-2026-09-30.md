# 139: Costed difference-probe rule (2026-09-30)

For an implementable allocation rule, maintain an unresolved comparison set

\[
\mathcal{D}_t=\{(u,v): U_{v,t}-L_{u,t}>\epsilon\},
\]

where the intervals refer to the declared selector reward contract. A possible
probe (a) is either a direct complete cell ((v,q)) or a paired endpoint
probe ((u,v,q)). Its incremental charge is the sum of endpoint charges not
already present in the eligible cache. It may shrink several comparison
intervals at once because the returned cell is shared by every difference that
contains that endpoint.

Under a validated covariance model, let (W_t(d)) be the current width of
difference (d), and let (W_{t+a}(d)) be the width after the probe's
information update. A RAGE-style heuristic score is

\[
\operatorname{score}_t(a)=
\frac{\max_{d\in\mathcal D_t}W_t(d)-
      \max_{d\in\mathcal D_t}W_{t+a}(d)}
     {\widehat{\operatorname{new\_charge}}_t(a)}.
\]

Choose the highest score while reserving a fixed fraction of the budget for
direct/random probes. For a hard cap, replace the denominator with a
deterministic upper charge and reserve it before launching the complete block.
For a soft realized-spend run, record the realized denominator and any
overshoot; the score is then an allocation heuristic, not a cap guarantee.

The covariance update must not be used merely because two rows were run on the
same question. If a simultaneous paired-confidence bound is unavailable, use
the conservative sum of endpoint/residual radii and mark the covariance score
as unavailable. The direct fallback remains legal. Any data-selected probe
and minimum-width comparison is covered by the global confidence allocation
from note 136.

This rule is a direct adaptation of transductive target-difference allocation,
not a new information-theoretic algorithm. The project-specific question is
whether unique-cell charging and cached anchor reuse make it materially better
than direct paired racing when retry charges are response-dependent. Required
measurements are unique cells purchased, realized dollars, false eliminations,
and held-out row quality; interval width alone is insufficient.

No implementation or experiment is claimed by this note.
