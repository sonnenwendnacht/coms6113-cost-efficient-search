# Reading note: GittinsEval

Read on 2026-09-23. Primary source: Qian Xie, Yueli He, and Nairen Cao, *Efficient Cost-Aware LLM Evaluation via Bayesian Bandit Gittins Indices*, [arXiv:2609.25645v1](https://arxiv.org/abs/2609.25645v1), submitted 2026-09-22. [Official PDF](https://arxiv.org/pdf/2609.25645v1); [local PDF](../../papers/pdf/xie-2026-gittinseval-2609.25645v1.pdf). Page references below count PDF pages from 1.

## Verified findings from the paper

- **Arms:** configurations, including model/prompt or sampling choices; a pull observes a fresh question batch. The working model assumes independent arms and conditionally independent, identically distributed within-arm observations. (§§2.1, 3.1; pp. 3–5.)
- **Difficulty:** questions are randomized; individual difficulty is not explicitly modeled. Informative priors use retrospective benchmark-level difficulty buckets. (§3.5; p. 7; Appendix D, p. 26.)
- **Costs:** constant across questions within an arm, using model-level price proxies. GSM8K uses input + twice output pricing; AlpacaEval uses input + eight times output; PIQA/MMLU use input-only pricing. No question-specific token counts or latency. (Appendix D; pp. 27–28.)
- **Objective:** final recommendation quality, not cumulative task reward. Offline regret compares full-row empirical scores; search sees only queried entries. Recommendation uses posterior mean minus standard deviation. (§§2.2, 3.4, 4; pp. 3–4, 6–8; Appendix D, p. 26.)
- **Comparisons:** UCB-E, LRF, SySRs, PromptEval-BAI, PBGI, LogEI, LogEIPC. Bayesian optimization evaluates full rows. (§4; pp. 8–9.)
- **Guarantee:** required-completion Gaussian-surrogate optimality does not extend automatically to partial-arm recommendation or dependent arms. (§3.4; p. 7.)

These findings are paraphrased from the [paper text](https://arxiv.org/html/2609.25645v1).

## Implementation check

The [authors' repository](https://github.com/QianJaneXie/BanditGittinsEval) documents `--recommendation-std-penalty 1` for mean-minus-standard-deviation recommendation; its stated default is `0`. Reproduction should pin a commit and specify this setting explicitly. Its README also distinguishes model-generation scripts from offline matrix simulations. No upstream code has been executed here.

## Implications for our project — our analysis, not the paper's claims

The user's matrix interpretation is useful: a row is an arm and a column is a question. For our project, the row should represent the **complete workflow configuration**, including ordered model choices at stages and retry attempts. A `(configuration, question)` entry is one measurement of that row, not a separate configuration arm. The algorithm may still need to choose both which row to measure and which question to use.

Fixing a response matrix is an experimental replay convention. It does not establish that a live API returns the same answer every time. We should state whether our target averages over tasks alone or over tasks and generation randomness. Repeated runs require distinct repetition identities; returning one cached response twice supplies no new independent evidence.

Known token prices do not imply known execution cost. A retry workflow pays for the path actually reached, and generated token lengths can vary. With two attempts and constant attempt costs, an illustrative expression is

`expected cost = first cost + P(first attempt triggers retry) × second cost`.

With question-dependent lengths and histories, replace this with an expectation over the actual conditional second-attempt cost. The retry trigger must come from a deployable checker; hidden benchmark correctness is a separate grading signal. Treating checker rejection and incorrectness as identical could overstate what deployment can achieve.

A more useful similarity concept than counting changed model names is **where execution first diverges**. Consider two configurations sharing the same exact prefix. Let `A` mean the run reaches their first differing decision. Under a valid coupling that gives both configurations the same prefix state and randomness, terminal scores agree outside `A`. Therefore

`E[score(a) − score(b)] = P(A) × E[score(a) − score(b) | A]`.

For scores in `[0,1]`, the absolute expected score difference is at most `P(A)`. This is an elementary candidate foundation for reach-weighted comparisons, not a novelty claim. A cost or latency difference needs its own bound; a rare suffix can still be extremely expensive. For configurations that change an early stage, downstream outcomes may change arbitrarily even if their model lists differ at only one position.

This suggests measuring two quantities separately: how frequently a prefix is reached on representative tasks, and how competing suffixes behave at matching reached states. Include zero differences for tasks that terminate before the divergence. Evaluating only a convenient collection of difficult reached states without estimating their population frequency would target the wrong quantity. Adaptive question selection needs explicit sampling weights or a separate unbiased evaluation protocol.

For exact prefix reuse, record the task, input/history, prompts, model snapshot, checker, decoding settings, environment, and repetition identity. Reusing an identical checkpoint can save **search spending**. It does not reduce the configuration's cold deployment cost, and it creates correlated observations that inference must account for. Similar configurations can inform predictions, but their observations cannot be recorded as exact cache hits.

To compare search methods without a complete response matrix, give each method the same search budget and independently evaluate the configurations they recommend on held-out questions. Report held-out quality, deployment cost, latency, uncertainty, and the spending that produced each recommendation. Charge initialization and prior-calibration measurements. Record final evaluation spending separately. This supports comparison against measured competitors; it cannot establish distance from an unmeasured global optimum. An exhaustive small problem remains useful for checking exact empirical regret and false elimination.

## Reproduction and research questions to resolve

1. Pin the upstream code revision and reconcile command defaults with the paper before claiming a reproduction.
2. Use a general prior or an independently calibrated prior in prospective experiments. Do not derive our difficulty prior from hidden evaluation results.
3. Include a partial-evaluation Bayesian optimization or racing comparison; comparing only against whole-benchmark queries would conflate candidate selection with measurement granularity.
4. Give all search methods equal access to the same exact reuse engine. Separately remove statistical sharing and reuse to identify which component helps.
5. Inspect SySRs, low-rank response modeling, and shared-prefix systems before claiming novelty. A defensible contribution must specify what new decision rule or guarantee follows from retry reach probabilities and incremental measurement costs.

No full reproduction, paid API experiment, or novelty validation has been completed. The local PDF metadata, title, version, page count, and checksum were checked; its manifest records the exact download.
