# Formulation, valid inference, and a minimal search procedure

Prepared 2026-09-23. **Status: proposed formulation and original elementary derivations, not a new-theorem claim, implementation, or measured research result.** This note sharpens the [initial research plan](../research-plan.md). Quantities below are defined for a fixed benchmark distribution, workflow, checker, and model versions. Claims about those quantities require those assumptions; they are not claims that real model behavior has already been verified.

## 1. The recommendation and the next experiment are different objects

Let `X` be a finite, registered set of complete configurations. A configuration specifies models at each stage and allowed attempt, retry limits, prompts, and a deployment-available stopping/checking rule. Initially hold everything except the model assignments fixed. A configuration is the **recommendation arm**: the item we ultimately deploy.

For a random question `Q ~ P` and deployment randomness `Z`, define:

```text
Y_x = final score in [0,1]
C_x = cold deployment expense of all executed operations
L_x = deployment elapsed time under a stated execution policy
mu_x = E[Y_x],  c_x = E[C_x],  ell_x = E[L_x].
```

The simplest primary target is an approximately best feasible configuration:

```text
F = {x: c_x <= c_cap and ell_x <= ell_cap}
find x_hat in F with mu_x_hat >= max_{x in F} mu_x - epsilon.
```

This is an expectation constraint, not a promise that every request meets the cap. Tail latency needs a separate target, such as `P(L_x > deadline) <= alpha`; its Bernoulli exceedance indicator can be estimated directly. A mean-latency bound cannot certify a percentile. If `F` is empty, the correct answer is that no feasible configuration was identified, with any distinction between certified infeasibility and insufficient evidence retained.

At search round `t`, the **measurement action** can instead be:

- Run one configuration on a new randomly selected question.
- Run a common prefix once, then compare two complete continuations on that same question.
- Run only a common prefix to bound every configuration extending it.
- Randomly select a reached checkpoint from a properly sampled parent pool and finish specified continuations.

The action includes the question-selection rule, replicate identity, and continuation choices. A model/question pair is an experimental location; treating every such pair as an independent recommendation arm would change the objective to finding the best *cell*, rather than the best row average.

Let `H_(t-1)` contain all revealed observations, cache state, and spending. The newly incurred charge `K_t` has a distribution depending on both the chosen action `a_t` and `H_(t-1)`. Its prediction is

```text
kappa(a,H) = E[K_t | a_t=a, H_(t-1)=H].
```

It is generally neither known exactly nor constant for an arm: output length, question difficulty, retries, checkpoint availability, and price rules all matter. A known input length or provider price table does not make the total action price deterministic. Search chooses a sequence of measurements to support a final decision; this is pure exploration/experimental design. It does not require training a reinforcement-learning controller for deployment.

The distinction between measurement and recommendation sets already exists in transductive experimental design. [Fiez et al. (2019), abstract and problem setup](https://arxiv.org/abs/1906.08399) use separate measurement and recommendation vectors. Their linear observation model is an assumption, however; a model-choice vector alone does not establish linear workflow quality.

## 2. Exactly what shared-prefix structure guarantees

Consider two configurations `a,b` with identical execution rules until their first possible divergence. On each representative question, draw their common prefix **once from its correct deployment distribution**. Reuse that state for both continuations. Let `R` indicate that execution reaches the divergence point, and let `p = P(R=1)`.

Requirements include identical prompts/history, model snapshot and decoding settings, tools/environment, checker, and prefix randomness. A stochastic prefix may be coupled across continuations if its marginal distribution is correct for each. Continuations need their correct conditional distributions; they need not be independent of each other. A cached state selected because of an interesting outcome is not automatically a representative prefix draw.

If `R=0`, both configurations have the same final outcome. If `R=1`, write their conditional score difference as `d`. Therefore, with `Delta = mu_a - mu_b`:

```text
D = Y_a - Y_b = R d
Delta = p * delta,                    delta = E[d | R=1]
|Delta| <= p
Var(D) = p * sigma_d^2 + p(1-p) * delta^2 <= p,
                                    sigma_d^2 = Var(d | R=1).
```

These follow from conditioning, `|d| <= 1`, and the law of total variance. They are not a novelty claim. For `p=0`, `D=0` identically and the conditional quantities need not be defined.

Matched questions can reduce variance because

```text
Var(Y_a - Y_b) = Var(Y_a) + Var(Y_b) - 2 Cov(Y_a,Y_b).
```

Positive covariance helps; pairing is not guaranteed to help when covariance is negative. Exact physical prefix reuse saves computation even when the statistical advantage is small. Those are separate effects to ablate.

For costs, write the cold executions as

```text
C_a = C_pre + R C_a_suffix
C_b = C_pre + R C_b_suffix.
```

Here `C_pre` includes the actual common execution through termination or the divergence checkpoint. If suffix costs are nonnegative with certified caps `U_a,U_b`, then

```text
c_a - c_b = p * E[C_a_suffix - C_b_suffix | R=1]
|c_a - c_b| <= p * max(U_a,U_b).
```

The corresponding physical cost of a cold paired experiment is

```text
K_pair = C_pre + R(C_a_suffix + C_b_suffix) + C_eval,
```

where `C_eval` is evaluation-only expense, such as a paid scorer not used at deployment. Thus cold pairing saves one common-prefix execution relative to two separate cold runs. A preexisting valid cache can reduce new search charges further, but each deployment estimate must still reconstruct its full cold path. Evaluation-only scoring must not accidentally be included in deployment cost.

For serial latency, the same decomposition holds if the shared prefix has the same elapsed time and each suffix duration is defined under the intended deployment load. Resuming two branches concurrently on a congested server does not automatically produce valid measurements of their separate deployment latencies. With parallel workflows, define end-to-end completion/critical-path time explicitly; summing API durations is generally wrong.

For a registered utility `U_x = Y_x - lambda C_x - eta L_x`, with nonnegative fixed weights and suffix bounds, one valid conservative bound is

```text
|E[U_a-U_b]| <= p * [1 + lambda max(U_Ca,U_Cb)
                       + eta max(U_La,U_Lb)].
```

A small reach probability alone does not justify pruning on cost, latency, or subgroup quality. For example, reach probability `0.001` and a `$1,000` extra suffix have mean cost impact `$1`. Also, an event rare overall may comprise an entire important subgroup. Such a subgroup requires its own target and denominator.

## 3. A stronger use of structure: bound an entire subtree without finishing it

Let `G` be a registered family of complete configurations sharing an execution prefix up to a cut. Choose this family before seeing the current question/prefix outcomes. Run the common prefix on representative parent samples. Let `R=1` mean the cut was reached; if execution instead terminated, score its final answer as `Y_stop` using the normal evaluation rule. Define

```text
A = (1-R) Y_stop             [take A=0 when R=1]
B = A + R.
```

For **every fixed descendant configuration** `x in G`, on the correct coupling:

```text
A <= Y_x <= B
E[A] <= mu_x <= E[B]
E[B] - E[A] = p.
```

This does not assume that an accepted answer is correct: `Y_stop` is its actual evaluation score. No unreached continuation is assigned a failure label. The `[0,1]` uncertainty of unfinished cases is deliberately retained.

If `U_C(G)` caps every allowed suffix's deployment charge, then

```text
C_pre <= C_x <= C_pre + R U_C(G),   for every x in G.
```

Analogous latency bounds require the execution conditions above. Estimate lower and upper expectations from the **whole parent pool**. For quality, if bounds on `E[A]` and `E[B]` are `[L_A,U_A]` and `[L_B,U_B]`, every descendant satisfies `mu_x in [L_A,U_B]`. All descendants inherit the same group-level certificate. There is no extra union bound over descendants for this deterministic implication; uncertainty still needs to cover every prefix statistic used.

Example, solely illustrative: if the known population values were `P(R=1)=0.20` and `E[A]=0.72`, no completion in this family could exceed quality `0.92`. An independently certified feasible incumbent above `0.92` would remove the whole family without suffix evaluations. In data, replace all those values with valid one-sided confidence bounds.

More parent samples reduce statistical uncertainty around this interval. They do **not** remove its structural width `p`. Once that width prevents a decision, the algorithm must evaluate continuations or refine the cut. This gives a concrete choice between paying for more prefixes and paying to resolve unfinished outcomes.

This is an instance of partial-information bounding, closely related to multi-fidelity best-arm identification. [Poiani et al. (2022), Section 2](https://proceedings.neurips.cc/paper_files/paper/2022/file/71c31ebf577ffdad5f4a74156daad518-Paper-Conference.pdf) assume known fidelity-bias bounds and fixed fidelity prices; here reach measurements produce a shared bound and checkpoint availability affects price. Those differences are reasons to study the mapping carefully, not proof of a new contribution. Simply ending retries early and treating the resulting quality as unbiased for the complete configuration is invalid.

## 4. Why counting changed model choices is insufficient

The proposed intuition is useful as a way to propose comparisons, but it does not prove a relationship between mean scores.

1. **A one-slot change can change everything.** Suppose one initial planner always generates a correct plan and another always generates a wrong plan; all later stages merely implement it. Neighboring assignments can have qualities `1` and `0`.
2. **A distant configuration can be identical.** Change every retry slot after a checker that always terminates. All outputs and deployment paths remain unchanged.
3. **Local improvement can miss interactions.** Four two-slot configurations can have scores `mu_00=.7, mu_10=.6, mu_01=.6, mu_11=1`. One-coordinate ascent starting at `00` stops at a suboptimal point.
4. **A cheap rare branch can still determine the winner.** Two configurations may differ by only `0.001` overall, with all of the difference inside a branch reached with probability `0.001`. If the required tolerance is `0.01`, resolving this is unnecessary for quality; if the tolerance is `0.0001`, it may be essential.

A learned kernel/additive model can guide allocation, but a calibrated predictor or explicit model-misspecification bound is needed before its predictions justify irreversible elimination. Graph structure and model names do not supply such a bound by themselves. [Gupta, Joshi, and Yağan (2021/2023), model definition](https://arxiv.org/abs/2109.04941) formalize correlated-arm information through supplied conditional-reward bounds; mere observed resemblance is a weaker premise.

## 5. Representative paired samples remain valid under adaptive allocation

For the first implementation, register a finite set of candidate pairs. Before drawing a new question, select which pair to compare using past information only. Draw a fresh question from `P` and a fresh prefix replicate; finish both continuations if reached. Record **zero difference when the differing part is not reached**.

For each pair `e`, its `n` observations then have the target mean `Delta_e`. With a fixed sample count, their average estimates the unconditional difference. Across pairs, observations may be correlated; independence across pairs is not needed for a union bound. Each registered stream must still obey its own sampling conditions.

Adaptive choice of how often to sample an edge does not justify ordinary fixed-sample intervals at an arbitrary stopping time. Nor does conditional unbiasedness of the next increment imply that the sample mean at a data-dependent stopping time is unbiased. [Shin, Ramdas, and Rinaldo (2020)](https://proceedings.mlr.press/v119/shin20a.html) discuss bias from adaptive collection and conditioning. Use simultaneous time-uniform intervals for decisions, and untouched fixed-design audits for final performance reporting.

Important exclusions from this simple argument:

- Choosing a pair after inspecting the current question or its failure state changes its sampling distribution.
- Adding only convenient cached cells to a row average changes the selection rule.
- Sharing one stochastic prefix across ten continuations does not create ten independent prefix samples.
- If completion is selectively abandoned after seeing an expensive or unfavorable partial outcome, complete-case averages need not estimate the original target.
- Repeated draws on the same question are not fresh draws from the question population. Model repetitions and question sampling are different variance components.

Side observations are still valuable, but they must be used with their actual observation design. The common-prefix bounds in Section 3 are one safe use of incomplete data. Do not append only the stopped cases as if they were a representative sample for every unselected descendant.

### Frozen finite matrix versus population sampling

A deterministic matrix with `N` questions defines `mu_x^N = sum_q Y_xq/N`, not population `mu_x`. Different question difficulties are fixed differences between columns; uniform random sampling averages over them. A nonuniform target needs stated weights.

A clean replay design registers, for each measurement stream, a uniformly random question permutation independent of the matrix and exposes its next unused position whenever the stream is chosen. Fixed-length prefixes are uniform samples without replacement. A valid bound for all prefix lengths remains valid at adaptively selected sample counts, even when scheduling uses other streams. The revealed order must not be rearranged using outcomes. [Bardenet and Maillard (2015)](https://arxiv.org/abs/1309.4029) provide finite-population concentration results; basic Hoeffding bounds also remain conservative under uniform sampling without replacement. At all `N` questions, the finite-matrix mean is known exactly.

Keep the stream identity when one configuration participates in several pairs. Pooling overlapping question sets from different pair permutations and pretending they are one without-replacement sample is invalid. One simple option is to retain pair-specific absolute-metric intervals and intersect valid bounds; the latent-row construction below is another.

For population claims, questions must come from the stated population, or inference must account for how the benchmark was sampled. An arbitrarily assembled benchmark does not acquire population coverage merely through a random permutation. Rerunning a deterministic cached cell produces no new population information. Repeated independently randomized indices can mathematically be sampling-with-replacement observations of a fixed matrix, but this is randomization over a finite list, not new evidence about model stochasticity or unseen questions.

If question selection is adaptive/nonuniform, the raw sample mean is generally wrong. Known positive selection probabilities can support importance-weighted estimators, at a variance cost. Arbitrary question selection is not part of the minimal algorithm.

## 6. Two-phase sampling of reached checkpoints

There is a legitimate way to spend suffix money primarily on reached cases. It must retain how those cases arose.

First generate `N` representative parent prefixes. For parent `i`, observe `R_i` and preserve the prefix state. For reached parents, let `d_i` be the paired suffix difference that would be observed under the experiment's defined continuation randomness. Randomly include the suffix pair with known probability `pi_i > 0`, using a coin independent of its unrevealed outcome conditional on available information. Write inclusion as `S_i`.

The inverse-probability estimator is

```text
Delta_hat = (1/N) sum_i R_i S_i d_i / pi_i.
```

At fixed `N`, conditional on a fixed pool of potential differences and independent inclusion coins, it is unbiased for the pool's unconditional average. Its selection variance is

```text
Var(Delta_hat | pool) = (1/N^2) sum_i R_i d_i^2 (1-pi_i)/pi_i.
```

For independent representative parents and a fixed within-parent sampling rule, the unconditional variance is

```text
Var(Delta_hat) = [ E(R d^2/pi) - Delta^2 ] / N.
```

The formula separates the gain in suffix spending from the increase in estimation noise. Fixed probabilities and independent selection are the conditions for these particular variance formulas. Adaptive sampling across parents can retain appropriate martingale expectations with predictable probabilities, but the displayed independent-sampling variance expression and ordinary fixed-sample intervals should not be carried over without proof. An estimated inclusion probability is not automatically a known one. Positivity, or a separate structural bound for excluded cases, is required.

An alternative is to choose `k` reached checkpoints uniformly without replacement from the `M = sum_i R_i` reached parents. For `M>0` and `1 <= k <= M`,

```text
Delta_hat = (M/N) * mean(d over the k chosen reached checkpoints)
Var(Delta_hat | pool)
  = (M/N)^2 * (1-k/M) * s_reached^2/k,
```

where `s_reached^2` is the finite reached-pool variance with denominator `M-1`; a one-element fully sampled pool has variance zero. If `M=0`, the estimate of the *pool mean* is zero, but population uncertainty about reach remains. Choose `k` before observing the sampled differences; outcome-dependent stopping changes the analysis. This estimator makes the missing denominator explicit: reporting only the reached-case mean estimates `delta`, whereas the target difference is `p delta`.

It also shows why reusing failures from a different preceding model is invalid without additional correction: those failures have a different conditional distribution and often different execution states. The same benchmark question does not make those states interchangeable.

For a design intuition, minimizing `E(R d^2/pi)` at a fixed expected suffix budget gives, by a pointwise Lagrange multiplier calculation,

```text
pi(h) = clip(sqrt(E[d^2 | h,R=1] / (lambda k_suffix(h))),
             pi_min, 1)
```

on reached prefix state `h`, for positive expected suffix cost and a fixed positive sampling floor `pi_min`. If an eligible existing checkpoint's continuation has zero new charge, choose inclusion probability one rather than divide by zero; this reveals no new independent root. This is an oracle allocation identity, not an implementable optimum: conditional second moments and costs must be learned, pilot expense charged, and positivity preserved. It says to consider both variability and price, rather than simply preferring apparently promising failures. It is a later extension; begin with all reached suffix pairs or uniform two-phase samples.

## 7. A conservative confidence rule that survives repeated inspection

Here is a transparent initial rule, preferable to an unproved Gaussian interval. Register `J` bounded statistic streams: configuration metrics, pair differences, reach indicators, and common-prefix lower/upper variables. Statistic `j` has observations in an interval of known width `w_j`. For independent representative observations within each stream, at its own sample count `n >= 1`, use

```text
r_j(n) = w_j sqrt{ log[pi^2 J n^2 / (3 delta_conf)] / (2n) }.
```

Hoeffding's two-sided bound makes the failure probability at `(j,n)` at most

```text
6 delta_conf / (pi^2 J n^2).
```

Summing over every stream and every `n` gives total failure probability at most `delta_conf`. Thus, simultaneously over all sample counts, `[mean_j(n)-r_j(n), mean_j(n)+r_j(n)]` covers every target mean with probability at least `1-delta_conf`. Intersect with the known variable range and with previous valid intervals. `n=0` retains the full known range. Stopping and stream selection based on revealed data do not invalidate this event. No independence between streams is used.

For quality means, `w=1`; for quality differences in `[-1,1]`, `w=2`. Normalize bounded cost/latency or use their actual range widths. Apply the same time-union idea to a justified finite-population bound in replay. For dynamically introduced streams, either freeze them after a development phase and collect fresh certification data, or allocate a summable error budget at registration and use valid future samples. Choosing a hypothesis from data and then treating those same data as pre-registered evidence requires more care.

A useful structural intersection is

```text
pair confidence interval intersected with [-U_p, U_p],
```

where `U_p` is a simultaneous upper confidence bound on the pair's reach probability. Zero observed reaches does not imply `p=0`. The cost version uses `[-U_p U_b, U_p U_a]`.

This Hoeffding rule is deliberately conservative and does not exploit low paired variance. For an actual performance claim about variance reduction, use and verify a variance-adaptive time-uniform construction, such as those developed by [Howard et al. (2021)](https://arxiv.org/abs/1810.08240), or explicitly analyze conditional/reach-factor intervals. The existence of a small true variance does not by itself make a Hoeffding-based implementation efficient. The confidence construction here establishes decision validity under its assumptions, not a cost-optimality result.

### An alternative safe baseline: retain intervals for every unfinished cell

Adaptive selection of which continuation to finish does not inevitably require inverse-probability weighting. There is a conservative alternative that preserves unknown outcomes as intervals instead of estimating them from a selected subset.

Fix all `K` candidate configurations before certification. Register an ordered sequence of independent representative root questions/replicates. Conceptually, root `i` has a full potential-outcome vector `(Y_xi: x in X)`, although almost all entries may never be evaluated. The vector can share prefix randomness across configurations; each configuration must have its correct marginal deployment distribution, and different root vectors must be independent. No assumption of independence between configurations is needed. Replicates of one fixed question are not independent population questions and require a different sampling/cluster analysis.

At any reveal time `t`, maintain pointwise bounds

```text
lo_xi(t) <= Y_xi <= hi_xi(t).
```

An entirely unknown score has bounds `[0,1]`. A completed execution has `[Y_xi,Y_xi]`. If a shared prefix terminates, all compatible descendants receive that same exact score for this root. Reached but unfinished suffixes retain `[0,1]`, unless a tighter logically valid bound is available. Revealing continuations can depend arbitrarily on already observed questions, costs, or outcomes; it never changes the conceptual target values or excludes inconvenient roots from the denominator.

For the first `n` registered roots, the latent full row average obeys

```text
mean_i lo_xi(t) <= mean_i Y_xi <= mean_i hi_xi(t).
```

Apply the simultaneous Hoeffding construction to **the latent full rows**, over all `(x,n)`, rather than to adaptively selected completed cells or changing interval endpoints. With radius `r_x(n)` for the latent row,

```text
mu_x in [ mean_i lo_xi(t) - r_x(n),
          mean_i hi_xi(t) + r_x(n) ]
```

holds simultaneously for all candidates, root-prefix lengths, and reveal times, on that one high-probability event. The proof is just the two displayed pointwise inequalities and the latent-row concentration event. The endpoints themselves need not be independent or unbiased. Adaptive completion changes how informative the interval becomes, not whether it is valid. Keep every one of the first `n` roots in every row denominator, including completely unstarted configurations.

For a fixed deterministic benchmark containing all `N` target questions, use all `N` in the denominator and omit the concentration radius when targeting its exact finite-benchmark mean. Then these are deterministic **identification intervals**, valid under any reveal order. If using only a random subset of that benchmark, finite-population sampling uncertainty still remains. For a population claim, benchmark-sampling uncertainty must still be addressed.

The same argument applies to cost and latency if each latent full value has a correct pointwise lower/upper bound and a finite range. Costs already incurred on a compatible prefix lower-bound a descendant's cold cost; remaining invocation caps provide an upper bound. Incompatible execution paths provide no such partial trace for that descendant. Measuring latency requires the deployment semantics discussed earlier.

This is a useful first correctness baseline for arbitrary adaptive continuation completion. It is conservative: a large unobserved fraction keeps bounds wide, and its basic Hoeffding radius does not exploit paired variance. A trie can compress identical intervals shared by many descendants. More efficient estimators may improve on it, but must earn their additional assumptions. The independent-stream procedure above, corrected two-phase sampling, and these latent-row bounds are distinct valid designs; do not mix their sample counts or confidence formulas without specifying why the resulting bound still holds.

## 8. Feasibility, elimination, and what can be certified

Let `[L_mu(x),U_mu(x)]`, `[L_c(x),U_c(x)]`, and `[L_ell(x),U_ell(x)]` be simultaneous intervals, including all justified structural intersections.

```text
definitely feasible: U_c(x) <= c_cap and U_ell(x) <= ell_cap
possibly feasible:  L_c(x) <= c_cap and L_ell(x) <= ell_cap
definitely infeasible: L_c(x) > c_cap or L_ell(x) > ell_cap.
```

Among definitely feasible configurations, retain a witness `b` with largest quality lower bound `L_mu(b)`. A possibly feasible candidate cannot beat this witness by more than `epsilon` if

```text
U_mu(x) <= L_mu(b) + epsilon.
```

The same test can remove a whole group by substituting the group's quality upper bound. A group can be declared infeasible if its common-prefix cost/latency lower bound already exceeds a cap. Keep the feasible witness and its certificate. Do not chain several `epsilon` comparisons and silently accumulate a larger tolerance; use the best retained feasible lower-bound witness directly.

A valid stopping certificate is: `b` is definitely feasible, and every possibly feasible candidate/group has quality upper bound at most `L_mu(b)+epsilon`. On the simultaneous event, `b` is feasible and within `epsilon` of the best feasible item in the registered candidate set. This is a short implication of the intervals, not a guarantee that a particular acquisition rule will reach the certificate quickly.

Even without the full response matrix, the quantity

```text
max(0, max_{x possibly feasible} U_mu(x) - L_mu(b))
```

is a conservative upper bound on `b`'s quality shortfall from the best truly feasible registered candidate, provided `b` is certified feasible and every candidate is covered. This is an uncertainty certificate, not the measured exact regret. An unvisited family must keep its broad upper bound unless valid structural information narrows it. A searched subset alone cannot certify an optimum over excluded configurations.

Near an exact feasibility boundary, certification can remain unresolved indefinitely without margin assumptions. A dollar cap may arrive first. Then return a clearly labeled recommendation and its remaining uncertainty; do not call it a fixed-confidence success. Hard fixed budget and unconditional fixed-confidence termination are different objectives.

For a frontier objective, define tolerances in actual units. A retained set `S` is an additive `(epsilon_q,epsilon_c,epsilon_l)` cover if for every candidate `x` there is `s in S` with

```text
mu_s >= mu_x - epsilon_q
c_s <= c_x + epsilon_c
ell_s <= ell_x + epsilon_l.
```

Use simultaneous intervals and direct retained witnesses to certify those inequalities. This definition is a coverage objective, not a claim that every retained point lies on the exact Pareto frontier. Discarding points because of uncalibrated predicted dominance does not certify coverage. Start with one constrained recommendation; validating a whole frontier is a larger experiment.

### Pairwise comparison graphs do not supply missing absolute information

If the only retained information is mean differences on graph edges, those equations identify configuration means only up to an additive constant in each connected component. With `K` vertices and `g` connected components, the edge-incidence matrix has rank `K-g`.

A connected graph can support rankings from exact differences, but cannot by itself certify absolute cost/quality constraints. Disconnected components cannot even be ranked against each other without anchors or bridge comparisons. Full paired runs already contain absolute outcomes; retain them and their sampling provenance. A differences-only implementation must deliberately add absolute measurements. Summing valid edge intervals along paths is possible; interval widths grow and covariances must not be ignored in a sharper combined estimator.

## 9. Rare branches: importance and measurement difficulty move together

The reach identity does not say that deeper comparisons are always better buys. With conditional gap `delta`, the overall gap is `Delta=p delta`. Ignoring logarithms, a variance-sensitive fixed-pair heuristic gives

```text
parent samples to resolve the sign ~ Var(D)/Delta^2
  = [sigma_d^2 + (1-p)delta^2] / (p delta^2).
```

When the conditional problem remains nontrivial, parent sampling becomes harder as `p` falls. One informative reached checkpoint costs approximately `E[C_pre]/p` in parent generation, plus continuation expense, if starting cold and collecting independent representative prefixes. A bank of previously paid reached states can make suffix comparisons cheap now; their acquisition cost cannot disappear from the overall experiment.

The displayed variance/gap expression is not a complete nonasymptotic sample bound: bounded-range terms, the confidence level, and at least some observations still matter, particularly when the variance vanishes.

At a fixed absolute quality tolerance, low reach may instead make further comparison unnecessary because `|Delta|<=p`. This is the tradeoff to exploit: determine when a family can be safely ignored and when a rare continuation is still decision-relevant. Small gaps, stringent deployment constraints, and subgroup objectives can force attention back to those rare states.

Conditioning can reduce variance from the random number of reached cases, but reach uncertainty remains. For illustration, if an independent estimate `p_hat` from `N` Bernoulli parents and an independent conditional-mean estimate `delta_hat` from `m` representative reached cases are available, then

```text
Var(p_hat delta_hat)
  = p^2 sigma_d^2/m
    + delta^2 p(1-p)/N
    + p(1-p) sigma_d^2/(Nm).
```

This is an original product-variance calculation under the specified independence design, not the formula for arbitrary cached two-phase samples. It shows why multiplying a highly precise conditional estimate by a poorly measured reach rate does not solve the unconditional problem.

## 10. Hard budget semantics and the smallest executable proposal

Before an action, reserve a certified maximum bill for the whole action based on token/output caps, all attempts, tools, and paid checkers. Permit it only if

```text
spent + already_reserved + maximum_new_action_charge <= search_budget.
```

After completion, reconcile the actual charge and release unused reserve. Expected cost can guide allocation but cannot guarantee a hard cap. If no finite billing bound is available, label the budget expected/probabilistic, or impose enforceable limits. A configuration evaluated with token/time caps is that capped configuration; do not extrapolate its quality to an uncapped deployment. Infrastructure aborts and search interruption need explicit outcome/missingness rules. Picking only calls predicted cheap on their current question can bias the question distribution.

If a root is registered before a question-dependent reservation rejects its continuation, keep that root's unfinished interval in the latent-row denominator. For the representative completed-stream design, use an acceptance/reservation rule independent of the new root's question/outcome, or analyze the resulting selection explicitly. Deleting expensive roots and averaging only completed ones is not a budget-control fix.

The proposed first algorithm has a deliberately small scope:

1. Register a modest configuration set, a tree of genuinely shared prefixes, permitted pair comparisons, metric caps/tolerances, confidence budget, and a randomized question design. Include global comparisons or anchors across all components.
2. Charge a small initialization that gives every relevant component absolute measurements. Maintain a physical invocation ledger and separate complete cold-path metrics.
3. Maintain valid configuration, pair, reach, and subtree bounds. Preserve parent denominators and replicate identity. Use either the stated representative-stream designs or the latent-row completion intervals for adaptive revealing, with any combination explicitly justified. Defer learned cross-configuration transfer.
4. Retain the best certified feasible witness. Prune only via the rules in Section 8; unresolved feasibility remains unresolved.
5. Choose among new parent prefixes, complete paired runs, and uniformly sampled reached continuations. Use a declared heuristic for expected decision-bound reduction per new dollar, with a fixed global-exploration schedule. Estimate prices only from permitted observations. Freeze/tune the heuristic on development data, then compare it with uniform and independent-arm allocation under the same cache engine.
6. Enforce reservations. Stop at the registered budget or a valid certificate. Report whether certification actually occurred. Audit frozen recommendations independently, irrespective of whether search intervals are narrow.

The valid bounds can be implemented before a sophisticated acquisition rule. The heuristic in step 5 is the research component; no bound here proves it more efficient than alternatives. A rigorous efficiency theorem would need a precise action model and assumptions covering state-dependent costs, shared observations, and stopping; it cannot be inherited from an independent-arm theorem by changing its cost variable.

## 11. Prior-work connections that constrain a publication claim

These are specific conceptual mappings, not completed reproductions.

| Primary source | Already-existing idea | What still needs care here |
| --- | --- | --- |
| [Huang et al., Structured Best Arm Identification, ALT 2017](https://proceedings.mlr.press/v76/huang17a.html) | Best recommendation values can be functions of noisy micro-observables. | Which workflow quantities truly compose, without independence or linearity being invented? |
| [Fiez et al., Transductive Linear Bandits, NeurIPS 2019](https://arxiv.org/abs/1906.08399) | Measure one object to identify another; allocation should resolve relevant differences. | Workflow outcomes are not automatically linear in model-assignment features. |
| [Gupta, Linked Bandits, 2018](https://arxiv.org/abs/1811.07476) | One sequential interaction reveals arms only until the first success; reach rates affect information. | Workflow retries can alter state and distributions, and dollars are not interaction counts. |
| [Gupta, Joshi, Yağan, Correlated BAI](https://arxiv.org/abs/2109.04941) | Formal side information can reduce required direct sampling. | Empirical Hamming resemblance does not supply the required conditional bounds. |
| [Poiani et al., Multi-Fidelity BAI, NeurIPS 2022](https://proceedings.neurips.cc/paper_files/paper/2022/file/71c31ebf577ffdad5f4a74156daad518-Paper-Conference.pdf) | Cheap biased measurements can eliminate candidates when bias is bounded. | Partial workflow observations give shared bounds; reach and new action prices must be learned/accounted for. |
| [Poiani et al., Optimal Multi-Fidelity BAI, NeurIPS 2024](https://arxiv.org/abs/2406.03033) | Fidelity selection itself has cost-complexity lower bounds and adaptive methods. | Establish whether our special partial-observation model adds anything beyond an adaptation. |
| [Li and Cheung, Resource-Constrained BAI, AISTATS 2024](https://proceedings.mlr.press/v238/li24c.html) | Identification can have deterministic or stochastic resource consumption. | A shared checkpoint is both retained information and an asset affecting future marginal costs. |

Together with AgentOpt, VineLM, SySRs, and GittinsEval, this means that **similarity, cost awareness, pairing, early stopping, and caching separately are not credible novelty claims**. A plausible narrower contribution is a well-specified, validated allocation procedure over prefix-bound and continuation measurements, showing when their joint information/cost structure reduces total search expense. A negative result against a strong multi-fidelity/paired baseline is a meaningful outcome.

## 12. Tests that can falsify the direction before a large paid study

Use exact finite synthetic enumerations for correctness, then budgeted real pilots for usefulness. Synthetic demonstrations verify reasoning; they do not establish real-world superiority.

- **Reach identity and group bounds:** enumerate all questions/paths and check every descendant against its common-prefix interval. Include accepted but incorrect answers.
- **Selection bias:** compare uniform parent sampling, reached-only naive averages, and corrected two-phase estimates. Vary difficulty and the preceding model; show that importing the wrong failure pool fails.
- **Cache/accounting equality:** enable the same cache for every search baseline. If the purported algorithm gain disappears, report an execution benefit rather than an allocation benefit.
- **Statistical advantage:** compare paired variance and uncertainty per dollar with independent questions. Include anticorrelated pairs and expensive shared prefixes.
- **Rare continuations:** hold conditional gaps fixed while varying reach, then hold absolute gaps/tolerances fixed where feasible. These answer different questions. Include rare expensive suffixes and rare important subgroups.
- **Early interactions:** include the four-configuration local-search trap. If global exploration cannot escape at realistic budgets, the method's scope must be narrower.
- **Inference stress:** repeatedly inspect/stochastically stop intervals across many synthetic repetitions; check erroneous elimination/certification against the registered error target. These tests cannot prove the theorem, but can find implementation violations.
- **Constraint boundaries:** include arms just above/below cost and latency caps. Track uncertified outcomes separately from correct certificates and from actual feasibility violations.
- **Incomplete matrix evaluation:** compare held-out recommendations at identical search-dollar checkpoints, with charged pilot/tuning data and independent audits. Without a hidden exhaustive reference, claim performance relative to those competitors, not a gap to the unknown global optimum.

The most useful immediate pilot question is precise: **Does a prefix observation bound enough candidate configurations tightly enough to avoid meaningful suffix expense, after giving every baseline identical reuse and question access?** If not, adding a complicated allocation layer is unlikely to be the best research investment.
