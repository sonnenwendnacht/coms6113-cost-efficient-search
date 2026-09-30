# GittinsEval: source and implementation audit

Reviewed 2026-09-23. This is a source audit and our mathematical analysis, **not a benchmark reproduction**. The complete local paper text, including appendices, was read; numerical results were not digitized or independently reproduced. No model APIs were called.

Primary paper: Qian Xie, Yueli He, and Nairen Cao, [*Efficient Cost-Aware LLM Evaluation via Bayesian Bandit Gittins Indices*, arXiv:2609.25645v1](https://arxiv.org/abs/2609.25645v1). Page numbers below count PDF pages, starting at 1. Local PDF is pinned in `papers/manifest.json`.

Primary implementation: [BanditGittinsEval at `a4992e22a48e781327efd5411fb7d0921ad5ab61`](https://github.com/QianJaneXie/BanditGittinsEval/tree/a4992e22a48e781327efd5411fb7d0921ad5ab61), commit dated 2026-09-22. All code findings below refer to this revision. The read-only audit checkout is under ignored `.cache/deep-mentor/upstream/`.

## Main assessment

The user's row/column interpretation is useful. A row represents a whole candidate configuration; a question contributes a measurement of that candidate. The research task is choosing a good final configuration with little measurement spending. Maximizing the rewards collected while searching would be a different objective.

The most useful transfer is the separation between **allocation**, **recommendation**, **stopping**, and **accounting**. The main obstacle to directly reusing the theorem is that shared workflow execution changes the information and cost of multiple candidate configurations together. A scalar index for an independently advancing row does not automatically remain optimal.

Two consequential reproduction issues emerged beyond the earlier reading note: the pinned public runners use per-cell planning while acting in batches, and their supplied AlpacaEval inputs contain 153 arms whereas the manuscript specifies 152. Both need reconciliation before we label a run a reproduction. These are verifiable discrepancies, not evidence about which code generated the published figures.

## 1. What is the target?

The paper distinguishes a population target `theta_k` from a finite benchmark target `F_k = mean_j Z[k,j]`. Its required-completion Gaussian-surrogate theorem concerns independent arms, predetermined local transition/noise/cost schedules, and terminal selection of a completed arm. Numerical roots, continuation after stopping, and optional-completion recommendations are outside that guarantee. Its empirical regret uses complete row means, not unknown population means. The reported recommendation subtracts one posterior standard deviation; this is a stabilization choice, not a confidence guarantee. Informative difficulty priors are retrospectively assigned using aggregate benchmark information. [Paper §§2–3.5, pp. 3–8; Appendix B, pp. 17–19](https://arxiv.org/html/2609.25645v1).

Our consequence: completing every question in a finite benchmark removes uncertainty about that realized row, **not** uncertainty about performance on new questions or new generations. We must choose the target before copying an estimator. An offline replay study and a held-out deployment study answer different questions.

The pinned simulator constructs a hidden full matrix and an initially missing observation matrix. Only queried cells are copied into the latter; the full row means are used externally to score regret. This is a valid way to simulate costly information acquisition from already available data. It does not require the search policy itself to know the full matrix. [`simulate_simple_regret.py`, lines 67–70, 95–110, 136–148](https://github.com/QianJaneXie/BanditGittinsEval/blob/a4992e22a48e781327efd5411fb7d0921ad5ab61/scripts/simulate_simple_regret.py#L67).

Without a full matrix, we can estimate differences between methods' held-out recommendations. We cannot report `max_k F_k - F_recommended` unless the maximum is available from a genuinely exhaustive reference or a justified bound. Search spending can still be measured exactly from a call ledger; the missing optimum affects the quality metric, not whether spending is observable.

## 2. Arm and question semantics

The paper's experimental arms are richer than model names: GSM8K/PIQA include model, temperature, decoding length, and prompt choices; MMLU uses model/template pairs. See Appendix C.1, pp. 19–20. The pinned GSM8K pricing metadata contains 122 configurations; PIQA contains 103; MMLU contains 1,500. These are candidate counts, not counts of independent model families. [Configuration metadata](https://github.com/QianJaneXie/BanditGittinsEval/tree/a4992e22a48e781327efd5411fb7d0921ad5ab61/data_analysis/pricing).

The Gittins action selects one row, then samples up to `B` distinct missing columns uniformly with `torch.randperm`. It never deliberately targets a difficult question, never pulls a known cell again, and does not force different rows to receive matching questions. The last batch is shortened when the row has fewer than `B` cells left. [`gittins_policy.py`, lines 464–487](https://github.com/QianJaneXie/BanditGittinsEval/blob/a4992e22a48e781327efd5411fb7d0921ad5ab61/src/gittins_policy.py#L464).

Our interpretation:

- A fresh draw from a population and a uniformly sampled unrevealed finite-matrix entry are different sampling descriptions. Conditional independence is a working generative assumption; it is not established merely by randomizing the order of fixed questions.
- A common question can correlate different configurations' scores. The independent-arm surrogate does not model that information. Arm identities need not be changed to `(configuration, question)` to exploit it; an allocation rule can choose a configuration **and** a question while still targeting configuration-level performance.
- Deterministic replay means an existing cell has one stored value. It does not mean a live model has a deterministic response. The source uses several independently generated GSM8K/PIQA matrices; variation across response-generation seeds and variation across search seeds must be kept distinct.
- For our project, each arm should initially identify a complete workflow policy: stage/retry model choices, checker, prompt rules, termination behavior, and relevant generation settings. Its realized execution is a path through that policy.

## 3. The Gaussian bookkeeping, rederived

These equations are our algebraic explanation of the pinned implementations [`simple_regret_recommend.py`, lines 28–46 and 81–114](https://github.com/QianJaneXie/BanditGittinsEval/blob/a4992e22a48e781327efd5411fb7d0921ad5ab61/src/simple_regret_recommend.py#L28) and [`gittins_shrinking_posterior.py`, lines 116–184](https://github.com/QianJaneXie/BanditGittinsEval/blob/a4992e22a48e781327efd5411fb7d0921ad5ab61/src/gittins_shrinking_posterior.py#L116). They agree with the paper's Appendix B.

Let an arm have `N` available cells, `n` observed cells with sum `S`, prior `theta ~ Normal(mu0,v0)`, and working per-cell noise variance `s²`. The latent posterior is

\[
v_n=(v_0^{-1}+n/s^2)^{-1},\qquad
\mu_n=v_n(\mu_0/v_0+S/s^2).
\]

For `m=N-n` unrevealed cells, conditioning on the observed values gives

\[
M_n=\mathbb E[F\mid D]=(S+m\mu_n)/N,
\qquad
V_n=\operatorname{Var}(F\mid D)=(m^2v_n+ms^2)/N^2.
\]

The two variance terms have different meanings: uncertainty in the common latent mean, and remaining cell noise. Dropping the second term understates uncertainty. At `n=N`, `M_N=S/N` and `V_N=0`; the latent posterior generally retains shrinkage and positive variance.

This is not simply multiplying a sample-mean variance by a classical finite-population correction. It is posterior prediction of the missing part of the row under a particular generative model.

Rearranging the posterior identity gives

\[
M_n=a\mu_n+(1-a)\mu_0,
\qquad a=1+\frac{s^2}{Nv_0}.
\]

For a next batch of actual size `b`, conjugate updating yields

\[
v_{n+b}=(v_n^{-1}+b/s^2)^{-1},\qquad
\operatorname{Var}(M_{n+b}-M_n\mid D)
=a^2\frac{v_n^2}{v_n+s^2/b}.
\]

Because `a>1` is common when arms share prior/noise/horizon, finite and latent posterior means rank arms identically on the same observations. Their index policies need not coincide: the transition variance has changed while monetary costs have not. The variance of the next posterior update is also distinct from the total remaining target variance used in recommendation.

The runners default to `s²=1/4`, equivalently batch-mean variance `1/(4B)`. This is a conservative variance bound for bounded independent scores, not a proof that their average is Gaussian. A Gaussian prior also assigns probability outside `[0,1]`; it is a computational surrogate rather than an exactly bounded accuracy model. For small batches, non-Gaussian behavior can matter even though the variance bound remains valid. [`run_simple_regret_wandb.py`, lines 261–267](https://github.com/QianJaneXie/BanditGittinsEval/blob/a4992e22a48e781327efd5411fb7d0921ad5ab61/scripts/run_simple_regret_wandb.py#L261).

**Executed diagnostic:** imported only the upstream posterior-moment functions on an invented 3-by-4 tensor. With `mu0=.5`, `v0=.04`, `s²=.25`, a completed all-success row has finite mean `1`, variance `0`, but latent mean approximately `.695122`, variance `.0243902`. The assertion passed. The local JSON record is `.cache/deep-mentor/moment-check.json`. This is a source-level mathematical sanity check, not an algorithm performance result.

## 4. Cost: precisely what is known in advance?

The checked pricing JSONs store **USD per one million input tokens, with a fixed output/input ratio folded in**, not measured dollars per benchmark question. The simulator sums these numerical proxies once per revealed cell. An unknown common input length cancels in percentage-of-exhaustive-cost plots. Question-specific lengths would not generally cancel.

For example, at proxy `0.90`, an assumed 100-input-token question with the stipulated output ratio would cost `0.90 * 100 / 1,000,000 = $0.00009`. The source experiment does not measure that question's length. Calling the simulator's accumulated proxy values literal paid dollars would therefore be inaccurate. [Pricing JSONs](https://github.com/QianJaneXie/BanditGittinsEval/tree/a4992e22a48e781327efd5411fb7d0921ad5ab61/data_analysis/pricing).

The exact GSM8K/PIQA source values are:

| Base model | Input rate | Output rate | GSM8K proxy `input + 2*output` | PIQA proxy `input` |
| --- | ---: | ---: | ---: | ---: |
| CodeLlama | 0.30 | 0.30 | 0.90 | 0.30 |
| Gemma-7B | 0.20 | 0.20 | 0.60 | 0.20 |
| GPT-2 | 0.10 | 0.10 | 0.30 | 0.10 |
| GPT-2 Large | 0.10 | 0.10 | 0.30 | 0.10 |
| LLaMA2-7B | 0.20 | 0.20 | 0.60 | 0.20 |
| Llemma-7B | 0.80 | 1.20 | 3.20 | 0.80 |
| Mistral-7B | 0.05 | 0.20 | 0.45 | 0.05 |
| Phi-2 | 0.05 | 0.10 | 0.25 | 0.05 |
| StarCoder2-7B | 0.20 | 0.20 | 0.60 | 0.20 |
| Tulu | 0.20 | 0.20 | 0.60 | 0.20 |
| Tulu2 | 0.20 | 0.20 | 0.60 | 0.20 |

Source: [`banditeval_model_cost.json`](https://github.com/QianJaneXie/BanditGittinsEval/blob/a4992e22a48e781327efd5411fb7d0921ad5ab61/data_analysis/pricing/banditeval_model_cost.json), cross-checked against the per-configuration JSONs and paper Table 2, p. 28. These are the study's historical assumptions, not a current pricing recommendation.

MMLU repeats each input-only proxy across 100 prompt arms:

| Model | Proxy | Model | Proxy |
| --- | ---: | --- | ---: |
| CodeLlama-34B-Instruct | .776 | Llama-3-70B-Instruct | .51 |
| Falcon-180B | 1.25 | Llama-3-8B | .05 |
| Falcon-40B | .84 | Llama-3-8B-Instruct | .03 |
| FLAN-T5-XL | .60 | Merlinite-7B | .60 |
| FLAN-T5-XXL | 1.80 | Mistral-7B-Instruct-v0.2 | .14 |
| FLAN-UL2 | 5.00 | Mistral-7B-v0.1 | .11 |
| Gemma-7B | .20 | Mixtral-8x7B-Instruct-v0.1 | .54 |
| Gemma-7B-IT | .07 | | |

Source: [`mmlu_prompt_eval_configurations_input_price.json`](https://github.com/QianJaneXie/BanditGittinsEval/blob/a4992e22a48e781327efd5411fb7d0921ad5ab61/data_analysis/pricing/mmlu_prompt_eval_configurations_input_price.json), matching paper Table 3, p. 28. Thus changing prompt or maximum generation length does not automatically change the arm's cost in this proxy model.

AlpacaEval uses `input + 8*output`; its pinned 153-arm file ranges from `.9` to `615`. For example, Claude 3 Opus has `15 + 8*75 = 615`. This proxy prices candidate inference, without separately metering a judge, tool, checker, or cache operation in the simulator. [Alpaca pricing file](https://github.com/QianJaneXie/BanditGittinsEval/blob/a4992e22a48e781327efd5411fb7d0921ad5ab61/data_analysis/pricing/alpaca_153_models_no_rounding_debias_price_1to8.json).

Our distinction for retries: provider rates can be known while the quantity purchased is unknown. For a reached attempt with random token length, the dollar cost depends on the task, history, output, checker behavior, and earlier failures. A cost predictor can guide selection, but the experiment must debit actual completed calls, failed attempts, and auxiliary services. Cache savings alter **new search spending**; they do not turn a full configuration's cold deployment cost into zero.

The parameter `lambda` converts cost units to accuracy utility in the planning problem. The public default is `1e-4`; the sweep includes `1e-5`, `1e-4`, and `1e-3`. It is not the deployment cost penalty unless we deliberately define it that way. We must calibrate it using development data or report a prespecified sensitivity grid rather than tune it on the final comparison. [Sweep configuration](https://github.com/QianJaneXie/BanditGittinsEval/blob/a4992e22a48e781327efd5411fb7d0921ad5ab61/scripts/config/GSM8KSimpleRegretSweep.yml).

## 5. Difficulty and prospective priors

The public prior resolver maps a dataset/task label to shared values; it does not use per-question difficulty in posterior updating. General: `N(.5,.04)`; GSM8K/Alpaca: `N(.2,.01)`; PIQA/MMLU-hard: `N(.4,.02)`; MMLU-medium: `N(.6,.02)`; MMLU-easy: `N(.75,.01)`. Missing MMLU metadata falls back to the general prior. [`run_simple_regret_wandb.py`, constants and lines 152–189](https://github.com/QianJaneXie/BanditGittinsEval/blob/a4992e22a48e781327efd5411fb7d0921ad5ab61/scripts/run_simple_regret_wandb.py#L152). The [bucket document](https://github.com/QianJaneXie/BanditGittinsEval/blob/a4992e22a48e781327efd5411fb7d0921ad5ab61/docs/mmlu_prior_buckets.md) records accuracy thresholds `.5` and `.7`.

Our assessment: a common prior supplies no direct ranking of arms, yet choosing its bucket using the complete benchmark supplies information unavailable before prospective evaluation. It is explicitly retrospective in the paper; it should not be presented as a cost-free no-oracle procedure in our live setting. Use a general prior, independently available related-task evidence, or an explicitly charged calibration sample. Keep the calibration tasks separate from final evaluation. Report sensitivity to misspecified priors because all our workflow configurations may have a systematically different quality distribution from single-model configurations.

## 6. Why the theorem and the working procedure differ

For our own explanation, write an arm's state as `(M,n)` and its remaining planning horizon as `H`. With outside reward `alpha`, the required-completion recursion is

\[
V_H(M;\alpha)=\max(M,\alpha),\qquad
V_n(M;\alpha)=\max\{\alpha,-c_n+\mathbb E[V_{n+1}(M';\alpha)]\}.
\]

Before completion, abandoning the arm takes the outside reward. Recommending the arm itself before completion is not an option in this recursion. The index is the outside reward at which further investigation becomes unattractive. Thus adding an anytime recommendation is an extra decision rule, not a consequence that can silently be read into the theorem.

Likewise, maximizing posterior mean is Bayes-optimal for posterior expected simple regret under a trusted joint model: conditional on the observed history, the expected best-arm value is the same additive term for every recommendation. Subtracting a standard deviation changes that objective. It can stabilize recommendations under misspecification but does not provide a frequentist error level or guarantee better mean regret.

In a workflow with shared prefixes, one observation can reveal an outcome relevant to many configurations, and the marginal cost of a continuation depends on previously stored checkpoints. Then “only the selected arm changes, at its predetermined local cost” generally fails. Independence cannot be restored merely by naming each workflow a different arm. We may still use a Gittins-inspired score as a heuristic baseline, with an explicit disclaimer about its assumptions and without importing optimality.

## 7. Concrete discrepancies to resolve before reproduction

| Issue | Evidence at the pinned revision | Consequence |
| --- | --- | --- |
| Per-cell planning, batch actions | `simulate_simple_regret.py:400–445` and `run_simple_regret_wandb.py:261–328` build `N+1` per-cell roots and set `use_batch_mean_gittins_dp=False`. | The public default plans with intermediate stopping opportunities inside each actual batch. Paper Algorithm 1 uses one transition per batch. |
| Switching the batch flag is insufficient | `gittins_policy.py:112–126` creates identical costs for every remaining batch, including a shorter final batch. | A correct paper-aligned implementation needs costs proportional to each actual batch size; clarify caller units. |
| Recommendation default | `simulate_simple_regret.py:243–249` defaults standard-deviation penalty to `0`; sweep runner does likewise. | Set `--recommendation-std-penalty 1` explicitly for the manuscript's LCB rule. Sweep YAMLs do not supply it. |
| Alpaca candidate set | Bundled sweep `.npy` is `(153,805)`; row 80 is constant `.5`, named `gpt4_1106_preview` in pricing. BO inputs also have 153 rows. | Manuscript Appendix C.1 specifies 152 after excluding this reference. Apply a consistent mask to matrix, metadata, BO inputs, and costs for that protocol. |
| Budget edge | Simulator charges a full batch, then checks the budget (`simulate_simple_regret.py:104–110,148`). BO checks affordability before evaluation (`run_bo_baseline.py:460–466,509–513`). | Equal nominal budgets need not mean equal actual spending. Use last recommendation available at or below the reporting budget. |

Pinned code links: [standalone simulator](https://github.com/QianJaneXie/BanditGittinsEval/blob/a4992e22a48e781327efd5411fb7d0921ad5ab61/scripts/simulate_simple_regret.py#L400), [sweep runner](https://github.com/QianJaneXie/BanditGittinsEval/blob/a4992e22a48e781327efd5411fb7d0921ad5ab61/scripts/run_simple_regret_wandb.py#L261), [alternate batch mode](https://github.com/QianJaneXie/BanditGittinsEval/blob/a4992e22a48e781327efd5411fb7d0921ad5ab61/src/gittins_policy.py#L112), [BO runner](https://github.com/QianJaneXie/BanditGittinsEval/blob/a4992e22a48e781327efd5411fb7d0921ad5ab61/scripts/run_bo_baseline.py#L460), [Alpaca sweep inputs](https://github.com/QianJaneXie/BanditGittinsEval/blob/a4992e22a48e781327efd5411fb7d0921ad5ab61/scripts/config/AlpacaSimpleRegretSweep.yml).

Our mathematical interpretation of the first discrepancy: for the same Gaussian process and per-cell costs, the per-cell controller can imitate a fixed batch controller, but it can also abandon the arm between cells. Its allowed actions contain the batch controller's actions. The single-arm continuation value can therefore be larger. Correct batch posterior updates alone do not make the two planning policies equivalent. The measured effect on the source paper's experiments is **unknown**.

The matrix dimensions and reference-row identity above were directly checked with NumPy, not inferred from filenames. The README notes 152-arm PromptEval reproduction scripts under ignored `outputs/`; those scripts are absent from a fresh clone. That does not establish how the manuscript's principal runs were produced. Obtain an artifact-to-figure map or author confirmation before assigning blame or claiming a result is reproduced.

## 8. Baseline interpretation and comparison design

The paper compares UCB-E, LRF, SySRs, PE-OneHot PromptEval-BAI, and full-configuration BO variants PBGI, LogEI, and LogEIPC. In particular, BO buys a whole row per decision; beating it does not establish superiority over a BO procedure that can choose partial evaluation effort. [Paper §4 and Appendix D, pp. 8–10, 26–27](https://arxiv.org/html/2609.25645v1).

The BO runner fits a categorical mixed Gaussian process. Default random initialization is `min(dominant_dimension, round(.05*K))` at the nominal `.10` budget: 6/5/8/75 configurations for GSM8K/PIQA/Alpaca/MMLU. Initializations purchase full rows. Its affordability check stops when the chosen candidate is too expensive; it does not search for the next affordable candidate. [`run_bo_baseline.py`, lines 59–100, 411, 460–514](https://github.com/QianJaneXie/BanditGittinsEval/blob/a4992e22a48e781327efd5411fb7d0921ad5ab61/scripts/run_bo_baseline.py#L59).

Our comparison should therefore include both a faithful historical baseline and stronger budget-aware alternatives. For our central similarity claim, random search alone is insufficient: a structure-aware method should also compete with racing/halving, a partial-evaluation surrogate, and a shared-reuse baseline receiving the same checkpoint infrastructure.

Further reporting choices matter. Use recommendation step functions at fixed **actually spent** budgets, keep initialization visible, and report how many runs have reached each budget. A straight line between two observations can show performance improvement before the method has paid for the observation that enables it. Use paired search seeds where useful, but compute task-level uncertainty from independent evaluation tasks rather than treating repeated search runs on one fixed matrix as new benchmark populations. Runtime measured with array lookups is controller overhead, not API latency.

## 9. What can be transplanted to retries?

| Reuse directly as an idea | Requires new modeling or an explicitly labeled heuristic |
| --- | --- |
| Separate acquisition, recommendation, stopping, and spending | A stopping guarantee when partial workflows can be recommended |
| Treat a complete configuration as a candidate | A joint model for shared prefix and suffix observations |
| Charge all observations and show budget-quality curves | History-dependent marginal costs and reach probabilities |
| Reveal only queried replay information | Task selection biased toward reached or difficult states |
| Use small exhaustive instances to measure empirical regret | Generalization from those instances to new tasks/generation seeds |
| Keep priors and algorithm settings recorded | Prospective prior calibration with its spending included |

For two configurations sharing an exact execution prefix, let `A` be reaching the first differing decision under a valid coupling of prefix randomness. For a bounded terminal score, their paired difference `D` is zero on paths terminating before `A`; hence `E[D]=P(A)E[D|A]` and `|E[D]|<=P(A)`. This elementary identity is a possible design tool, not a novelty claim. It suggests separating **how often a suffix matters** from **how different its alternatives are**, rather than treating all one-model edits as equally similar.

Its practical limitation is crucial: evaluating suffixes only on stored failed cases estimates a conditional quantity. We still need an unbiased or otherwise justified estimate of their population frequency, and all upstream calls used to discover those states must be charged. A one-model change near the root can radically alter downstream states; edit distance alone supplies no accuracy guarantee. A rare branch can also have enormous cost, so the score bound does not automatically bound dollar or latency differences.

## Corrections and open questions

The earlier `gittinseval-reading.md` is directionally sound but incomplete. “A fresh question batch” should specify uniformly selected unrevealed columns without replacement. “Costs known in advance” refers to fixed proxy weights, not measured question costs. The finite-target adjustment affects allocation and stopping as well as recommendation. The earlier note did not identify the planning/action granularity or Alpaca candidate-set discrepancies. A fixed replay cell is not evidence of live-response determinism.

Before any reproduction claim, resolve: which source revision and commands produced each figure; whether batch or cell roots were used; how the 152-arm Alpaca artifacts were built; and whether published traces explicitly used recommendation penalty one. For our project, also decide whether we target population quality or a finite test set, how prior calibration is paid for, and how unknown retry costs and joint observations enter allocation.

Verification performed: full paper-text reading; browser verification of primary sources; pinned source inspection; pricing metadata and array-shape checks; one posterior-moment diagnostic. Not performed: upstream policy sweeps, figure reproduction, statistical replication, live inference, or empirical validation of the proposed retry-search method.
