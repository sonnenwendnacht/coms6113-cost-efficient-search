# Related theory: what our observation model must add

Prepared 2026-09-23. This is a comparison of problem formulations, not a claim that the cited proofs have been checked in full or that our proposed method is new. The seven added PDFs are pinned in [the manifest](../../../papers/manifest.json); source text was extracted into ignored `.cache/deep-root/`. The [workflow review](02-workflow-prior-art.md) covers AgentOpt, VineLM, SySRs, and the additionally downloaded FlowCompile.

The relevant question is narrower than whether previous work used an agent workflow. **Can the same search problem already be expressed by its measurement, cost, and recommendation rules?** Several familiar ingredients of our proposal already have substantial theory.

## Source findings and applicability

### Best Arm Identification with Resource Constraints

**Reading depth:** §2 model, introduction/related-work discussion, and the SH-RR algorithm description at a high level; proofs not audited. Li and Cheung allow unknown arm-specific joint distributions of reward and multiple resource consumptions. Consumption can be random, reward and consumption may correlate, and consumption is bounded. The goal is to identify the largest-mean-reward arm while respecting the cumulative resource budgets; this is different from choosing the greatest reward per dollar. [§2, PDF p.3](https://proceedings.mlr.press/v238/li24c/li24c.pdf).

**Implication for us:** variable token bills and unequal evaluation prices are not enough to distinguish our problem. A black-box workflow with stationary joint quality/cost observations can already be an arm here. What requires additional modeling is that a cached execution changes the next measurement's incremental cost, and one physical execution can inform several candidate configurations. A per-arm stationary consumption law does not directly encode that evolving shared state. The paper also separates constraints on search spending from constraints on the selected deployment arm. [Primary publication](https://proceedings.mlr.press/v238/li24c.html).

### Best Arm Identification in Linked Bandits

**Reading depth:** introduction and §2 setting/feedback interpretation, with selected sampling discussion; proofs not audited. Gupta's learner chooses an ordered subsequence of underlying Bernoulli arms. The environment reveals its prefix through the first success, or the full sequence if none succeeds. Rewards of the selected arms are independent. The target is the best **underlying arm**, and the principal resource is the number of sequence plays. [§2, PDF p.2](https://arxiv.org/pdf/1811.07476v2).

**Implication for us:** censored later observations and reach-dependent feedback are established ideas. But a repair model's quality can depend on preceding outputs and the question; it need not have one prefix-independent Bernoulli mean. We also want the best whole workflow under dollar and deployment constraints. These differences prevent directly relabeling repair models as linked-bandit arms and importing the theorem. A simplified independent success cascade would be a valuable bridge setting, with its unit-cost sequence-play model clearly distinguished from per-call API spending. [Pinned source](https://arxiv.org/abs/1811.07476v2).

### Structured Best Arm Identification with Fixed Confidence

**Reading depth:** abstract, §2 formal setup, and overview of LUCB-micro; proofs not audited. Huang et al. separate the quantities that can be sampled from the alternatives to recommend. Candidate payoffs are a **known mapping** of unknown means of smaller observable quantities. Their framework motivates adaptive measurement selection using structure; minimax trees are an important application. [§2, PDF pp.3–4](https://proceedings.mlr.press/v76/huang17a/huang17a.pdf).

**Implication for us:** “choose a component measurement rather than evaluate a complete candidate” is already a general abstraction. To use it, specify the map from observable conditional statistics to workflow value and show its required regularity. A graph of model assignments alone does not supply that map. Execution-dependent selection, cached costs, and imperfect stop signals must either be represented explicitly or remain outside the transferred guarantee. It is possible that a restricted workflow model reduces to this framework; establishing such a reduction is necessary before calling it a new bandit formulation. [Primary publication](https://proceedings.mlr.press/v76/huang17a.html).

### Sequential Experimental Design for Transductive Linear Bandits

**Reading depth:** introductory formulation, §2 model and lower-bound statement, algorithm overview; proofs not audited. Fiez et al. explicitly allow a measurement set `X` different from the recommendation set `Z`. Both consist of known feature vectors; measurements and recommendation values share an unknown linear parameter. Observations have independent, mean-zero, sub-Gaussian noise. Their allocation targets differences between candidate values. [§2, PDF p.3](https://proceedings.neurips.cc/paper/2019/file/8ba6c657b03fc7c8dd4dff8e45defcd2-Paper.pdf).

**Implication for us:** separating experiments from deployments and measuring informative pairwise directions are not new by themselves. A linear or additive model for workflow quality is an assumption requiring validation, especially when upstream outputs change later prompts. Feature encodings of model identities do not establish linearity. Exact prefix reuse may produce a useful observation design, but deriving its likelihood, covariance, and evolving acquisition cost remains necessary. A misspecified linear surrogate can guide exploration without providing a valid elimination certificate. [Primary publication](https://proceedings.neurips.cc/paper/2019/hash/8ba6c657b03fc7c8dd4dff8e45defcd2-Abstract.html).

### Multi-Fidelity Best-Arm Identification

**Reading depth:** §2 setting and selected lower-bound/algorithm discussion; proofs not audited. Poiani et al. allow cheaper, biased observations of each target arm, with known fidelity prices and known upper bounds on fidelity bias relative to the target mean. The algorithm chooses both the arm and the fidelity while identifying the best full-fidelity arm. [§2, PDF pp.2–3](https://proceedings.neurips.cc/paper_files/paper/2022/file/71c31ebf577ffdad5f4a74156daad518-Paper-Conference.pdf).

**Implication for us:** using fewer retries is not automatically a valid cheap evaluation of a longer workflow. It changes behavior, and a guaranteed fidelity relation requires a bias bound. Under a coupling where only reached extra invocations can change a bounded final score, their reach probability supplies a possible bound; estimating it introduces additional uncertainty. Fewer uniformly sampled questions ordinarily reduce precision rather than change the mean target, which is another distinct resource-allocation setting. Neither interpretation permits treating an unfinished run as an observed final failure. [Primary publication](https://proceedings.neurips.cc/paper_files/paper/2022/hash/71c31ebf577ffdad5f4a74156daad518-Abstract-Conference.html).

### LeapsAndBounds

**Reading depth:** introduction and §2 problem statement, with selected algorithm discussion; proofs not audited. Weisz et al. optimize solver configuration for runtime over random instances, charging the actual time spent discovering a good configuration. Runs can be capped: a timeout reveals a censored runtime, not the exact completion time. Their approximate-optimality definition includes a tail-probability allowance, addressing potentially heavy-tailed runtimes. [§2, PDF p.2](https://proceedings.mlr.press/v80/weisz18a/weisz18a.pdf).

**Implication for us:** the user's hyperparameter-search analogy has a strong theoretical precedent, including search expense and adaptive run truncation. Its runtime objective is not identical to finding accurate workflows under spending constraints, but the bookkeeping lesson transfers: stopping an expensive experiment changes what is observed. Saving money through truncation does not create a complete unbiased quality sample. Specify timeout semantics and the guarantee's target population before adapting the method. [Primary publication](https://proceedings.mlr.press/v80/weisz18a.html).

### Procrastinating with Confidence

**Reading depth:** introduction/contribution discussion and §2 model, with §3 algorithm overview; proofs not audited. Kleinberg et al.'s Structured Procrastination with Confidence adaptively allocates runtime among configurations and progressively caps runs. It is designed to provide improving recommendations as more search time becomes available. The model permits randomized algorithms through instance/seed pairs and does not require performance correlation between configurations. [§§1.2, 2–3, PDF pp.2–4](https://arxiv.org/pdf/1902.05454v3).

**Implication for us:** adaptively spending less on poor configurations, paying for search, and producing anytime recommendations are existing objectives. Our proposed shared execution may change the observation/cost structure, but replacing a solver with an agent does not establish that distinction. A strong comparison should preserve the same final-recommendation goal and account for all partial work. Correlation could improve an extension, but must enter an estimator or acquisition rule rather than appear only in motivation. [Pinned source](https://arxiv.org/abs/1902.05454v3).

## Our synthesis: the reduction questions to answer first

An adequate problem statement should specify five objects:

1. **Recommendation:** a complete fixed workflow assignment, or a runtime policy. These are different candidate classes.
2. **Measurement action:** an entire task run, a shared-prefix acquisition, or one/more continuations from an existing checkpoint.
3. **Feedback:** observed outputs, stop signals, final scores, and which other candidate outcomes become known exactly.
4. **Physical cost:** newly executed calls, tools, checking, and any state acquisition; separated from the selected workflow's cold deployment expense.
5. **Sampling law:** how representative questions, execution randomness, reached states, and adaptive selection create the observations.

The strongest possible structural benefit is not merely a smoother search space. A single paid operation can have several consequences: it can measure reach, create a reusable state, reveal a terminal outcome shared by several candidates, and reduce the future price of related measurements. Whether these consequences can be compressed into a known existing model is a research question. Their presence alone is not a proof of novelty.

A useful first theoretical exercise is a finite frozen-task setting with exact deterministic state reuse and a fixed finite candidate set. Define the marginal cost and information revealed by every allowable operation. Then ask whether ordinary synchronized elimination on the same engine already captures most of the benefit. Only afterward introduce stochastic outputs, adaptive question selection, imperfect judges, or an unbounded configuration space; each changes the assumptions needed for valid inference.

For a theory claim, identify an explicit assumption and a measurable advantage it enables. Examples include bounded reach-limited differences, a known exact value decomposition, or shared observations with a specified covariance structure. For an empirical claim, test the full procedure at equal physical budgets against methods granted identical computational reuse. A favorable result against a baseline forced to rerun shared work would establish the value of caching, not the novelty of an allocation rule.

## Remaining literature work

This reading pass establishes substantial overlap, not an exhaustive novelty clearance. It does not fully audit proofs, reproduce any baseline, or survey all work on feedback graphs, common-random-number simulation optimization, correlated-arm identification, and adaptive allocation with state-dependent experimental costs. The immediate priority is to determine which of those established models contains the precise restricted problem above, and which assumptions would fail for the actual workflow.
