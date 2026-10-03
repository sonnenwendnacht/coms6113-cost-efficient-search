# Structural BAI theorem target

The cleanest way to state what similarity could buy is as a conditional
structure assumption, not an intuition. Let `K=|M|^3` be the complete rows and
let

```text
theta_r = ( -E[C_r], E[Y_r] )
```

denote the deployment cost and final gold correctness of row `r`. Without a
relation among rows, any method that leaves a row essentially unobserved has a
no-free-lunch instance pair: both instances agree on every purchased row but
assign different best means to the hidden row.

One possible structured model is

```text
theta_r = Theta phi(r) + epsilon_r,     ||epsilon_r|| <= rho,
```

where `phi(r)` contains shared model-coordinate and explicitly registered
interaction features, `d=dim(phi)` is much smaller than `K`, and paired
question noise is sub-Gaussian. A robust cost-aware linear pure-exploration
algorithm can then use a confidence radius of the form

```text
sqrt(phi(r)^T V^{-1} phi(r)) + rho
```

for quality and cost, with a paired-difference variance term when a paid hub
exists. Under the assumed model, the structural sample burden can scale with
`d` (and the residual term `rho`) rather than treating all `K` rows as
independent. This is only a theorem target: it is false when the residual or
interaction error is large, and it does not follow from one-edit Hamming
distance by itself.

Retry reach makes the model harder. Later-stage outcomes are missing-not-at-
random because a verifier failure is required to reach them. Features or
weights must include survival/path indicators, or the analysis must restrict
itself to complete final row outcomes and avoid imputing later slots. Shared
question difficulty can lower paired-difference variance, but covariance must
be estimated and monitored on a calibration block.

The falsifiable experiment is therefore: report effective dimension `d`,
residual scale `rho`, paired-difference variance, and coverage; compare the
structural model with identity features and an independent-arm Gittins/UCB
fallback; and include a permuted/adversarial row assignment where structural
transfer should fail. If the feature model cannot beat identity at matched
spend, the project should report a well-engineered independent-arm baseline
rather than claim similarity gains.

This boundary is essential because [SySRs](https://arxiv.org/html/2606.07726)
already uses synchronized same-question subsets, paired comparisons, response
similarity, and low-rank reconstruction for single-model evaluation. The
complete-row extension must therefore expose the new path variables and cost
semantics rather than rename the same matrix method.
