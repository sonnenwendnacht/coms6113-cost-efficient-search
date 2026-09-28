# Related work and the contribution we still need to establish

Reviewed 2026-09-23. These are research notes, not claims that the proposed method is novel or effective. The downloaded versions are pinned in the paper manifest; PDFs remain local in `papers/pdf/`. The mentor's cost-aware evaluation paper has a separate [reading note](gittinseval-reading.md).

The project fits configuration search and experimental design: the system being configured happens to contain LLM calls, retries, and tools. That framing is useful, but already appears explicitly in AgentOpt. The publication opportunity must be more specific than “apply bandits to agents” or “similar configurations can share information.”

The later [deep review](deep-review/README.md) includes pinned implementation evidence, expanded theory connections, and a narrower proposed contribution. This page is the initial literature map.

## Closest papers

| Paper and verified version | What it already provides | Consequence for this project |
| --- | --- | --- |
| [AgentOpt v0.1 Technical Report: Client-Side Optimization for LLM-Based Agent](https://arxiv.org/abs/2604.06296v2), Hua et al., 2026 | End-to-end model-combination search; Matrix UCB-E, low-rank factorization, elimination, hill climbing, and Bayesian optimization. Section 4.4 caches identical HTTP requests across combinations. Section 5.2's hill climbing changes one role assignment at a time. | One-coordinate neighborhoods, correlated score prediction, and identical-call reuse are already baseline capabilities. Compare against them rather than claiming these ingredients as new. |
| [VineLM: Trie-Based Fine-Grained Control for Agentic Workflows](https://arxiv.org/abs/2605.23914v1), Pagonas et al., 2026 | An execution trie supports different models across invocations, checkpointed prefixes, sparse cascade profiling, and online replanning. Section 4.2 corrects failure-conditioned observation bias through cascade decomposition; Appendix A smooths sparse deep conditional rates. | Shared prefixes and correction for early stopping are direct prior work. A new profiler needs a demonstrable advantage over VineLM's sampling and estimation, not just a new trie implementation. |
| [On Speeding Up Language Model Evaluation](https://arxiv.org/abs/2407.06172v3), Zhou et al., ICLR 2025; code: [BanditEval](https://github.com/kilian-group/banditeval) | UCB-E allocates evaluations among methods; UCB-E-LRF predicts missing entries in the method-by-example matrix and directs measurements toward uncertain cells. | “Choose the next configuration and question” and low-rank matrix completion are established approaches. Compare under actual execution costs; equal numbers of observed matrix cells need not mean equal spending. |
| [Cutting LLM Evaluation Costs with SySRs: A Bandit Algorithm that Provably Exploits Model Similarity](https://arxiv.org/abs/2606.07726v1), Lyu et al., ICML 2026; code: [SySRs](https://github.com/zifanlyu/llm-bandits-sysrs) | Synchronized Successive Rejects compares surviving models on common question batches. Paired comparisons exploit correlated outcomes, with guarantees improving as models become more similar. | Similarity itself is not an adequate novelty claim. A same-question paired baseline is essential even when our configuration structure is richer than a flat model list. |
| [Efficient multi-prompt evaluation of LLMs](https://arxiv.org/abs/2405.17202v3), Maia Polo et al., NeurIPS 2024; code: [PromptEval](https://github.com/felipemaiapolo/prompteval) | Estimates a distribution of prompt performances from a sparse prompt-by-question matrix using shared statistical structure, including item-difficulty models and balanced sampling. | Question difficulty is not a new confounder. Borrowing information across rows and columns is established; our estimator should explain why workflow structure adds information beyond those models. |
| [Using Common Random Numbers and Control Variates in Multiple-Comparison Procedures](https://pubsonline.informs.org/doi/pdf/10.1287/opre.39.4.583), Yang and Nelson, Operations Research 1991 | Constructs simultaneous intervals for differences between simulated alternatives and uses common random numbers to reduce comparison variance. | Same-question paired residuals are established simulation-optimization practice. Our gap, if any, must come from retry-specific realized costs and full-row workflow semantics, not pairing alone. |

AgentOpt's downloaded v2 still has the technical-report title above; it reports ten search methods. Do not merge claims from another title or an older abstract without checking the exact version.

## Foundations for fair baselines

- [Random Search for Hyper-Parameter Optimization](https://www.jmlr.org/papers/v13/bergstra12a.html), Bergstra and Bengio, JMLR 2012, establishes random search as a serious optimization baseline. For this project, specify both how configurations are drawn and how their questions are allocated; “random search” alone leaves the spending policy ambiguous.
- [Hyperband: A Novel Bandit-Based Approach to Hyperparameter Optimization](https://www.jmlr.org/papers/v18/16-558.html), Li et al., JMLR 2018, allocates resources to randomly drawn configurations and stops poor candidates early. Here the resource could be benchmark questions, but unequal per-question costs and prefix reuse require explicit accounting rather than a silent substitution.
- [BOHB: Robust and Efficient Hyperparameter Optimization at Scale](https://proceedings.mlr.press/v80/falkner18a.html), Falkner et al., ICML 2018, combines model-guided proposal with Hyperband-style allocation. It reinforces that proposing promising configurations and allocating evaluation effort are separate choices that should be ablated.

## Distinguish three meanings of similarity

1. **Exact execution reuse.** Two configurations with the same executed prefix on the same question can start from one saved state if the prompt, model version, decoding settings, tools, and environment match. This saves actual calls. It does not create another independent observation of the prefix. Reusing a recorded outcome is exact for a frozen replay experiment; treating it as a new independent stochastic run would be incorrect.
2. **Paired statistical comparison.** Run candidate configurations on the same sampled questions. Shared question difficulty can reduce the variance of their score difference. Pairing does not imply that unexecuted outputs are known.
3. **Predicted similarity.** A model change at one position, an embedding, a low-rank model, or a graph neighborhood predicts that other outcomes may be similar. This is an assumption to test. An early change can alter every downstream prompt and reverse the final ranking; a late change after a shared saved state offers a much stronger structural connection.

These distinctions are our synthesis of the papers above. Keep saved observations, logically implied outcomes, and statistical predictions separate in the implementation and logs. An early successful stop can determine a longer policy's result only when that longer policy shares the same stop rule and would preserve that result. Additional refinement alone does not guarantee monotone accuracy.

## A defensible candidate contribution

Our proposed direction is **adaptive selection of the next useful continuation under a monetary profiling budget**, using already observed prefixes and failure-conditioned evidence. The acquisition decision should consider how much it can change the choice of the final configuration, how many candidates it informs, and how much new execution it actually requires. This is a research hypothesis, not a verified gap in all existing literature.

To make that direction stronger than a collection of existing ingredients:

- Specify the estimator and sampling rule jointly. Adaptive selection of failures, questions, or branches can bias simple averages. Define the target question distribution and provide valid uncertainty estimates under the chosen sampling procedure.
- Use observed shared-prefix structure to predict marginal execution cost. Separate the known price per token from unknown output lengths, failure rates, and continuation lengths.
- Test whether structured continuation selection adds value beyond ordinary paired evaluation, low-rank prediction, and a generic configuration surrogate. Include adversarial cases where one-model changes destroy similarity.
- Give every search method the same legal checkpoint/cache access. Report a separate ablation with reuse disabled so savings from execution reuse and savings from better measurement choices can be distinguished.
- Compare selected configurations on untouched questions at matched actual profiling dollars. Without a complete response matrix, claim improvement over the tested baselines with uncertainty, not distance to a global optimum. Use small exhaustive spaces only where an optimum or exact frontier is actually known.

Before a paper novelty statement, extend the review to correlated/structured best-arm identification, costly side observations, adaptive experimental design, and algorithm configuration with instance-dependent evaluation costs. This first pass establishes serious overlap; it does not establish that the remaining direction is unpublished.

## Reading order

Read the mentor's cost-aware paper first, then AgentOpt Sections 4.4–5 and VineLM Sections 3.5–4.2 plus Appendix A. Follow with SySRs and BanditEval to choose the strongest allocation baselines. Read PromptEval for question-difficulty modeling, then the three hyperparameter-search papers for the broader framing.

## Additional structured and cost-aware prior art

- [Ranking and Selection: A New Sequential Bayesian Procedure for Use with Common Random Numbers](https://arxiv.org/abs/1410.6782), Gorder and Kolonko, allocates simulation effort using posterior covariance when alternatives share common scenarios. A cost-aware paired race must be compared with covariance-aware ranking and selection; paired blocks alone are not new.
- [Best-Arm Identification in Correlated Multi-Armed Bandits](https://arxiv.org/abs/2109.04941), Gupta, Joshi, and Yagan, uses correlation information between arms to reduce fixed-confidence best-arm samples. Similarity needs an explicit conditional model or a diagnostic; an observed Hamming pattern is not a proof that an unpulled row can be inferred.
- [Balancing Performance and Costs in Best Arm Identification](https://arxiv.org/abs/2505.20583), Harding and Kandasamy, treats learning cost and the penalty for recommending a suboptimal arm in one risk objective. We should report profiling cost and held-out row quality separately before introducing any scalarized cost--accuracy objective.
- [Best Arm Identification with Resource Constraints](https://proceedings.mlr.press/v238/li24c.html), Li and Cheung, allows arm-dependent random resource consumption while identifying the best mean-reward arm. It is a closer cost-accounting baseline than dividing accuracy by a nominal price.
- [Best Arm Identification in Spectral Bandits](https://www.ijcai.org/proceedings/2020/307), Kocak and Garivier, studies fixed-confidence identification when arm means obey graph-smoothness constraints. A Hamming graph therefore has a direct structured-BAI precedent; our work cannot claim graph-guided search as new without a retry-cost-specific result.
- [Best Arm Identification in Generalized Linear Bandits via Hybrid Feedback](https://arxiv.org/abs/2605.05745), Zeng et al., combines absolute and pairwise observations and extends Track-and-Stop to heterogeneous acquisition costs. Pairwise-versus-direct cost allocation is therefore already a close baseline; any gap must use the full outcome-dependent retry cascade rather than a free dueling query.
- [Best-Arm Identification with Generative Proxy](https://arxiv.org/abs/2607.06879), Ma et al., uses a correlated cheap proxy and controls residual variance when the correlation is unknown. Any row-as-proxy or control-variate extension should be compared with this framework.
- [Best-Arm Identification with Generative Proxy](https://arxiv.org/abs/2607.06879), Ma et al., uses a correlated cheap proxy and controls residual variance when the correlation is unknown. Any row-as-proxy or control-variate extension should be compared with this framework.
