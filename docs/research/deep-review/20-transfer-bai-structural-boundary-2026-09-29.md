# Transfer-BAI structural boundary (2026-09-29)

Research-only source audit; no experiments, traces, replays, or model calls.

## Source

Neopane, Ramdas, and Singh, *Best Arm Identification under Additive Transfer
Bandits*, arXiv:2112.04083 (2021):
[paper](https://arxiv.org/html/2112.04083).

## Relevant result

The paper defines source arms with unknown means `mu_i` and target arms whose
means are a known additive transfer function

`nu_a = sum_i f_{a,i}(mu_i)`.

It constructs time-uniform confidence sequences for source means and propagates
them through the transfer function to obtain target confidence sequences. An
LUCB-style rule samples the source coordinate that contributes most uncertainty
to the current target leader or challenger. The correctness theorem applies to
any adaptive sampling/stopping rule that uses valid source confidence sequences.

## Boundary for our row search

The result is a clean formal precedent for exploiting shared configuration
features. It does not justify the current 217-feature model as a theorem: the
model's relationship between slot treatments and final retry-workflow quality is
unknown, can be nonlinear, and may include verifier-triggered threshold effects.
An additive or linear row model can therefore be an allocation prior or a
registered baseline, but its posterior prediction must not replace direct row
evidence unless a residual confidence certificate is maintained.

If the project eventually assumes a known structural transfer map, the design
could replace posterior-only elimination with transfer confidence intervals and
sample the feature coordinate that controls leader/challenger uncertainty. Under
the current problem statement, a more honest design is to use the map for
ranking, retain an independent residual component, and require direct
time-uniform evidence for final elimination and recommendation.

