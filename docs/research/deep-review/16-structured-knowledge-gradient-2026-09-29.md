# Structured correlated knowledge gradient for complete retry rows

Research note prepared 2026-09-29. This is one candidate Algorithm 2 design,
not an experiment, theorem, novelty claim, or recommendation to spend on a
live provider. I did not read response traces or held-out answers and did not
make model calls. The repository's search unit is a paid cell `(row, question)`;
every cell below means a complete row execution on one question. There is no
prefix, checkpoint, or partial-workflow action in this design.

## Target and structural prior

There are three categorical choices with nine levels each, so the complete row
set is

```text
C = {1,...,9}^3,       |C| = 9^3 = 729.
```

For row `c` and search question `q`, a completed run returns

```text
Q(c,q) in [0,1]       offline final correctness after the completed path
K(c,q) >= 0           realized input-token charge of every reached call
```

The answer-key-blind checker signal `A(c,q,j)` controls whether attempt `j+1`
is reached; it never sees the answer key. In the current offline replay, `Q`
is scored after the complete path and can be returned to the selector as the
benchmark measurement. That is a benchmark-evaluation protocol, not a claim
that a deployed checker can observe correctness. A live deployment version
would replace `Q` with a registered quality observation and must state that
target separately. The held-out audit questions and their keys remain hidden
until the search recommendation is frozen.

The latent finite-population row mean is `mu_c = E_q[Q(c,q)]`. (For a fixed
benchmark, `E_q` is the registered question average.) Use treatment/reference
coding for the row features:

```text
phi(c) = [1,
          1{c_j=k} for j=1,2,3 and k=1,...,8,
          1{c_j=k,c_l=h} for (j,l) in {(1,2),(1,3),(2,3)}
                              and k,h=1,...,8].
```

There are `1 + 3*8 = 25` additive features and `3*8*8 = 192` pairwise
features, hence `p = 217`. Put a Gaussian structural prior and an explicit
unstructured row residual on all 729 means:

```text
theta ~ N(m_theta, V_theta)
u       ~ N(0, tau_Y^2 I_729)
mu_c    = phi(c)^T theta + u_c.
```

With design matrix `Phi` (729 by 217), the initial row-mean belief is

```text
m_0 = Phi m_theta,
S_0 = Phi V_theta Phi^T + tau_Y^2 I_729.
```

Thus a measured row can update structurally related rows through `Phi V_theta
Phi^T`, while `tau_Y^2` prevents a perfect, unjustified transfer. Setting the
residual very large approaches an unstructured independent-arm baseline;
setting it to zero is a strong structural assumption and should not be the
default.

This is a model for latent row means, not a claim that Hamming neighbors share
an execution prefix. A one-slot neighbor can have a very different downstream
prompt or retry path. Any transfer is therefore a Bayesian prediction whose
residual must be checked, never an exact cache hit.

## Separate row-mean covariance from same-question covariance

The covariance in `S` is prior/posterior uncertainty about the *unknown row
means*. It is different from correlation in the measurement noise when two
rows are run on the same question. A useful Gaussian working likelihood is

```text
Q(c,q) = mu_c + d_q + e(c,q),
```

where `d_q` is a question-difficulty term shared by rows on that question and
`e` is row-specific noise. For a fresh single-row cell use noise variance
`r_c = Var(d_q)+Var(e(c,q))`. For a same-question pair `(a,b)`, use

```text
R_ab = [[r_a, rho_q sqrt(r_a r_b)],
        [rho_q sqrt(r_a r_b), r_b]].
```

The cross-row `rho_q` must be estimated from paid paired cells (or set to a
conservative value); Hamming distance alone is not evidence for it. Positive
`rho_q` can make a paired difference precise, while an anti-correlated pair
can be worse than two independent questions. This distinction follows the
correlated-normal knowledge-gradient model of Frazier, Powell, and Dayanik
(2009), which uses a multivariate-normal belief over alternatives and
independent measurement errors, and the covariance-adaptive best-arm model of
Saad, Blanchard, and Verzelen (2023), which obtains multiple arm outcomes on a
common sampling unit. The proposed row prior and retry costs are our
application-specific hypotheses, not results of those papers.

Primary sources:

* Frazier, Powell, and Dayanik, *The Knowledge-Gradient Policy for Correlated
  Normal Beliefs*, INFORMS Journal on Computing 21(4), 599--613 (2009),
  [paper PDF](https://optimallearning.princeton.edu/Papers/Frazier%20Powell%20Dayanik%20CorrelatedKnowledgeGradientJOC.pdf).
  Their model and Eq. (1) use a multivariate-normal prior over alternative
  means; Eqs. (3)--(4) give the rank-one posterior-mean update used below.
* Russo, *Simple Bayesian Algorithms for Best Arm Identification*, COLT 2016,
  [PMLR page](https://proceedings.mlr.press/v49/russo16.html). Top-Two
  Probability sampling chooses the two designs with largest posterior
  probability of being optimal and allocates effort between them; its stated
  objective is best-arm identification rather than cumulative reward.
* Saad, Blanchard, and Verzelen, *A Best-Arm Identification Algorithm for
  Correlated Bandits*, NeurIPS 2023,
  [paper](https://arxiv.org/abs/2306.02630). Their common-unit arm-vector
  observations establish covariance-adaptive comparisons, but do not model
  retry cascades or random token charges.

## Exact one-cell correlated-Gaussian KG

Suppose the current posterior is `mu | H_t ~ N(m,S)` and we consider paying
for a fresh cell of row `c`, with Gaussian measurement variance `r_c`. Let
`e_c` be the 729-vector selecting row `c`. Before seeing its value,

```text
a_c = S e_c / sqrt(S_cc + r_c),       Z ~ N(0,1),
m_next(Z) = m + a_c Z.
```

The covariance after the observation is deterministic:

```text
S_next = S - S e_c e_c^T S / (S_cc + r_c).
```

The one-step correlated knowledge gradient is therefore exactly

```text
KG(c) = E_Z[max_j {m_j + a_c,j Z}] - max_j m_j.                 (1)
```

This is not a diagonal-arm heuristic: every nonzero element of `S[:,c]`
updates a structurally related row. Equation (1) is a one-dimensional normal
integral. It can be evaluated without Monte Carlo by taking the upper
envelope of the 729 lines `m_j + a_c,j z`. If the envelope has line `j_l` on
`[t_l,t_{l+1}]`, then its contribution is

```text
m_jl [Phi(t_{l+1})-Phi(t_l)]
 + a_c,jl [varphi(t_l)-varphi(t_{l+1})],
```

with the usual limiting values at plus or minus infinity. Summing these terms
and subtracting `max(m)` gives (1). The line-envelope calculation is exact for
the Gaussian surrogate; a bounded/Bernoulli confidence statement requires a
separate concentration method.

After observing a completed cell value `y`, the actual update is

```text
kappa = S e_c / (S_cc + r_c)
m <- m + kappa (y - m_c)
S <- S - kappa (e_c^T S).                                      (2)
```

Equation (2) is the usual correlated-normal update. It updates unvisited row
means, but it does not mark those rows as measured or provide their missing
cell correctness.

## Pair action and exact pair-difference update

When the leader and a challenger are close, run *both complete rows* on the
same fresh question block. Let `a` and `b` be the row indices,

```text
H = [e_a^T; e_b^T],       G = H S H^T + R_ab.
```

For a pair observation `y=(Q(a,q),Q(b,q))`,

```text
m_next = m + S H^T G^{-1}(y - Hm),
S_next = S - S H^T G^{-1} H S.                                  (3)
```

This full update should be retained because both completed cell outcomes are
direct evidence and can inform all 729 means. Its exact two-dimensional KG is

```text
KG(a,b) = E_{Z~N(0,I_2)}[ max_j {m_j + A_j,: Z} ] - max_j m_j,
A = S H^T L^{-T},  LL^T=G.                                     (4)
```

Equation (4) is an exact definition under the model; a deterministic
two-dimensional normal quadrature can evaluate it. A policy may instead use
the following scalar comparison update for a cheaper top-two score. Put
`h=e_a-e_b`, observe the paired difference `z=Q(a,q)-Q(b,q)`, and let

```text
v_D = h^T S h,
w_D = [1,-1] R_ab [1,-1]^T.
```

Then

```text
m_next = m + S h (z - h^T m)/(v_D + w_D),
S_next = S - S h h^T S/(v_D + w_D).                              (5)
```

The posterior variance of the latent gap `mu_a-mu_b` is
`v_D w_D/(v_D+w_D)`. A positive same-question covariance lowers `w_D`; an
anti-correlated pair raises it. The scalar update is appropriate for deciding
which of the two rows wins, while (3) is the correct update when the pair can
change beliefs about other rows.

## Explicit realized-cost model

The charge is not a fixed price per row: retries, early acceptance, and output
length make `K(c,q)` random. Use the same feature map (or a preregistered
cost-specific one) in a log-cost model:

```text
L(c,q) = log(1 + K(c,q)) = psi(c)^T beta + u_c^K + eta(c,q),
beta ~ N(b_0,W_0),       u_c^K ~ N(0,tau_K^2),
eta(c,q) ~ N(0,s_K^2).
```

To allow row quality and row cost to be related by retry behavior, the row
residuals may have a joint prior

```text
(u_c, u_c^K) ~ N(0, [[tau_Y^2, rho_u tau_Y tau_K],
                    [rho_u tau_Y tau_K, tau_K^2]]).
```

This optional cross-covariance is estimated only from completed search cells;
it is not inferred from an API price coefficient. Given the posterior for
`L_c`, use

```text
k_hat(c) = exp(m_L,c + 0.5 s_L,c^2) - 1
k_U(c)   = exp(m_L,c + z_(1-alpha) s_L,c) - 1                  (6)
```

as the predicted mean and a conservative scheduling quantile. For a pair,
`k_U(a,b)` is a high bound on the sum (or a registered worst-case envelope),
not the charge of one row. The primary fixed-budget selector scores

```text
score(action) = KG(action) / k_U(action),                       (7)
```

only as a myopic allocation heuristic. It is not a global cost-optimality
claim. A hard dollar cap must admit a complete block only when its worst-case
charge envelope fits; otherwise call the cap a soft cap and report realized
overshoot. If a deployment-cost constraint is itself an objective, maintain a
separate cost interval and register that constrained objective before search.

## One coherent selector: SC-KG with a top-two challenger

The following procedure uses structure to decide where to measure, and
same-question pairing to resolve a close leader/challenger contest. It never
uses a predicted value as an exact observation.

```text
Input: all 729 rows; fixed search-question permutation and complete blocks;
       structural prior (m,S); quality-noise model; cost prior; search budget B.

while the next complete block fits the registered budget:
    For every candidate row c:
        compute direct KG(c) from (1)
        compute k_U(c) from (6)
        direct_score[c] = KG(c) / k_U(c)

    Draw posterior mean vectors from N(m,S) (allocation only).
    leader       = row with largest posterior probability of being optimal
    challenger   = second row by that posterior probability
    Compute pair KG(leader, challenger) from (4), or the conservative
        pair-gap score from (5), using same-question R_ab.
    pair_score = pair_KG / k_U(leader, challenger)

    With a fixed epsilon_global reserve, choose the best-scoring direct row,
        the top-two pair, or a row outside the current top posterior region.
    Select the next questions from the precommitted permutation. A pair uses
        exactly the same questions for both complete rows.
    Execute every selected (row, question) cell to completion. In an offline
        benchmark replay reveal Q only after the workflow; in a live setting
        reveal the registered deployment-quality signal. Record A and K too.
    Apply (2) for direct cells or (3) for pairs; update the cost model with K.
    At fixed block checkpoints, inspect held-in search residual diagnostics.
        Inflate tau_Y / disable structural transfer if the registered gate
        fails; never shrink uncertainty because the fit looks convenient.

At the search deadline, choose argmax posterior mean among finalists. A
conservative deployment policy directly confirms finalists on a fresh search
block before freezing the row; this confirmation is a policy choice, not a
universal Bayesian requirement. Only after freezing the row, run the hidden
held-out audit and report its quality and cold deployment cost separately.
```

The top-two step is an adaptation of Russo's posterior-probability idea to an
action that buys two complete cells on one question. It is not the same theorem
as Top-Two Probability sampling, because the two outcomes are paired and the
row means have a structured correlated prior. The pair action is particularly
useful when `KG(leader,challenger)` is large relative to the direct scores and
`v_D` is small enough that a shared question can settle the contest. A fixed
global reserve is necessary because a local top-two policy can miss a distant
row with a rare but important interaction.

## Misspecification and validity boundary

The Gaussian KG is an allocation rule under a working model. The following
failure modes must be explicit.

* **Nonlinear workflow interactions.** The 217 features omit three-way effects,
  prompt-induced changes, and verifier thresholds. The residual `u_c` is not a
  proof that the misspecification is bounded uniformly over all 729 rows. A
  residual radius estimated from a few visited rows can be badly optimistic.
  Use held-in cross-fitting, inflate the residual, retain global exploration,
  and report a direct unstructured fallback when diagnostics fail.
* **Binary outcomes.** Correctness is bounded and often Bernoulli, whereas a
  normal likelihood permits values outside `[0,1]`. KG then supplies a useful
  ranking heuristic, not a fixed-confidence certificate. Final elimination or
  audit intervals should use bounded Bernoulli/finite-population methods with a
  declared block schedule.
* **Unknown same-question covariance.** Estimating `rho_q` after selecting a
  favorable pair can make (3)--(5) overconfident. Pair calibration must use
  outcome-independent blocks, or a confidence sequence/error allocation over
  the registered pair family. If the covariance estimate is unreliable, set
  `R_ab` to the conservative independent-noise value and retain direct
  intervals.
* **Random, outcome-dependent charge.** The log-cost model can miss heavy
  tails, and retry cost can correlate with correctness. Equation (7) is then
  only scheduling guidance. Use a high quantile or worst-case per-cell limit,
  never treat an unvisited retry as a zero-cost failure, and record every
  realized charge including failed calls.
* **Adaptive stopping.** Repeatedly checking ordinary sample variances or KG
  values does not create anytime-valid confidence. Freeze block boundaries,
  use an allocated confidence sequence, or label the result heuristic.

The most important caveat is the unvisited row. The prior can assign an
unvisited row a posterior mean and can make its cell worth buying; this is
legitimate model-based transfer. It does not mean its correctness was observed
or that a neighboring row is an exact substitute. If the surrogate is wrong,
the row residual and global reserve are the only safeguards. Requiring a direct
confirmation block before deployment is a conservative recommendation rule;
the Bayesian fixed-budget objective may instead select an unvisited row when
its posterior expected value is highest, provided that choice is reported as
model-dependent.

## Baselines and a falsifiable comparison

The primary baseline should be the same one-cell Bayesian KG with `S` forced
diagonal (independent row means), the same cost model, question blocks, and
realized-dollar accounting. This isolates the value of structural transfer.
Add a synchronized top-two direct baseline that runs the leader and
challenger on the same questions but does not use `Phi V_theta Phi^T`; this
isolates paired outcome covariance. Uniform complete-row allocation and a
cost-aware random-row baseline are sanity controls. Every method receives the
same search questions, checker, cache/reuse rules, and budget; held-out audit
questions remain hidden until all recommendations are frozen.

The claim to test is narrow: under equal realized profiling spend, the
structured posterior plus valid global reserve selects a better complete row
than the diagonal KG and paired-only controls on some workflows where the
additive/pairwise residual is small. A null result, or a result that disappears
under permuted slot labels, anti-correlated questions, or three-way
interaction controls, would reject the structural advantage. No result is
established by this note.
