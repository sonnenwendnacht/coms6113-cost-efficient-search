# LLM surrogate-reward overlap

## Primary source

Ji, Pan, Zhu, and Lei, *Multi-Armed Bandits With Machine Learning-Generated
Surrogate Rewards*, arXiv:2506.16658v2: [paper](https://arxiv.org/html/2506.16658).

MLA-UCB already applies control-variate and prediction-powered inference ideas
to model selection. It uses cheap ML/LLM surrogate rewards, learns unknown
true–surrogate covariance online, and reports regret improvements. Its language
model case study uses open-source models as surrogates for proprietary model
selection. The method requires the surrogate and true reward to be jointly
observed on the same online unit, and its main theory uses iid bivariate
Gaussian rewards or a batched approximation.

## Consequence for our project

“Use a cheaper similar model as a proxy” is already a demonstrated idea. A
CW-CV-TT paper cannot claim this mechanism as new. Its possible difference is
that the proxy is an expensive, fully executed retry row and the target is a
fixed-confidence complete-row recommendation with verifier-gated, path-
dependent charges and hidden final correctness.

The required baseline set now includes MLA-UCB/PROBE-style surrogate methods
whenever a genuinely cheap surrogate is available. If all rows have similar
full execution cost, an anchor control variate may be less attractive than
direct covariance-adaptive pairing. Any claimed extension must account for
missing later attempts rather than pretend that a surrogate and final reward
are jointly observed when the verifier stopped before the attempt.
