# Reading catalog

Start with GittinsEval, AgentOpt, and VineLM, then SySRs and BanditEval. Hyperband, random search, and BOHB connect the project to hyperparameter search. Context readings come from the shared-document screenshots and are downloaded for reference; they have not all been reviewed in depth.

```bash
python3 scripts/download_papers.py
python3 scripts/download_papers.py --verify-local
```

The manifest pins each version, source URL, and checksum. PDFs are local in `papers/pdf/` and excluded from Git. A fresh clone gets the catalog and downloader; run it to obtain the same readings. The original publisher/author terms still apply.

| Reading | Priority | Pinned version | Local PDF |
| --- | --- | --- | --- |
| [Efficient Cost-Aware LLM Evaluation via Bayesian Bandit Gittins Indices](https://arxiv.org/abs/2609.25645v1) | required | arXiv:2609.25645v1 (2026-09-22) | [PDF](pdf/xie-2026-gittinseval-2609.25645v1.pdf) |
| [AgentOpt v0.1 Technical Report: Client-Side Optimization for LLM-Based Agent](https://arxiv.org/abs/2604.06296v2) | required | 2604.06296v2 | [PDF](pdf/agentopt-v0.1-2604.06296v2.pdf) |
| [VineLM: Trie-Based Fine-Grained Control for Agentic Workflows](https://arxiv.org/abs/2605.23914v1) | required | 2605.23914v1 | [PDF](pdf/vinelm-2605.23914v1.pdf) |
| [Cutting LLM Evaluation Costs with SySRs: A Bandit Algorithm that Provably Exploits Model Similarity](https://arxiv.org/abs/2606.07726v1) | background | 2606.07726v1 | [PDF](pdf/sysrs-2606.07726v1.pdf) |
| [On Speeding Up Language Model Evaluation](https://arxiv.org/abs/2407.06172v3) | background | 2407.06172v3 | [PDF](pdf/banditeval-2407.06172v3.pdf) |
| [Efficient multi-prompt evaluation of LLMs](https://arxiv.org/abs/2405.17202v3) | background | 2405.17202v3 | [PDF](pdf/prompteval-2405.17202v3.pdf) |
| [Hyperband: A Novel Bandit-Based Approach to Hyperparameter Optimization](https://www.jmlr.org/papers/v18/16-558.html) | background | JMLR 18(185), 2018 | [PDF](pdf/hyperband-jmlr-2018.pdf) |
| [Random Search for Hyper-Parameter Optimization](https://www.jmlr.org/papers/v13/bergstra12a.html) | background | JMLR 13(10), 2012 | [PDF](pdf/random-search-jmlr-2012.pdf) |
| [BOHB: Robust and Efficient Hyperparameter Optimization at Scale](https://proceedings.mlr.press/v80/falkner18a.html) | background | PMLR 80, 2018 | [PDF](pdf/bohb-icml-2018.pdf) |
| [SCOPE: Selective Conformal Optimized Pairwise LLM Judging](https://arxiv.org/abs/2602.13110v4) | context | 2602.13110v4 | [PDF](pdf/scope-2602.13110v4.pdf) |
| [Beyond Prompts: Measuring and Optimizing LLM Tool-Agent Harnesses](https://arxiv.org/abs/2609.05736v2) | context | 2609.05736v2 | [PDF](pdf/beyond-prompts-2609.05736v2.pdf) |
| [An Empirical Study of Harness Design for Coding Agents](https://arxiv.org/abs/2609.20804v1) | context | 2609.20804v1 | [PDF](pdf/harness-design-2609.20804v1.pdf) |
| [Harness Engineering: Anatomy, Architecture, and Evolution of Coding Agents -- A Source-Code Study of Eleven Systems](https://arxiv.org/abs/2609.00006v1) | context | 2609.00006v1 | [PDF](pdf/harness-engineering-2609.00006v1.pdf) |
| [RouterBench: A Benchmark for Multi-LLM Routing System](https://arxiv.org/abs/2403.12031v2) | context | 2403.12031v2 | [PDF](pdf/routerbench-2403.12031v2.pdf) |

Detailed notes: [GittinsEval](../docs/research/gittinseval-reading.md), [related work](../docs/research/related-work.md). Machine-readable citations are in [references.bib](references.bib).
