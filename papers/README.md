# Reading catalog

Start with GittinsEval, AgentOpt, and VineLM, then SySRs and BanditEval. Hyperband, random search, and BOHB connect the project to hyperparameter search. Context readings come from the shared-document screenshots and are downloaded for reference; they have not all been reviewed in depth.

```bash
python3 scripts/download_papers.py
python3 scripts/download_papers.py --verify-local
```

Papers listed in the document screenshots use those titles as filenames, with colons replaced by hyphens for Windows compatibility. The manifest preserves each official publication title, document title, version, source URL, and checksum. PDFs are local in `papers/pdf/` and excluded from Git. A fresh clone gets the catalog and downloader; run it to obtain the same readings. The original publisher/author terms still apply.

| Reading | Priority | Pinned version | Local PDF |
| --- | --- | --- | --- |
| [Efficient Cost-Aware LLM Evaluation via Bayesian Bandit Gittins Indices](https://arxiv.org/abs/2609.25645v1) | required | arXiv:2609.25645v1 (2026-09-22) | [PDF](<pdf/Efficient Cost-Aware LLM Evaluation via Bayesian Bandit Gittins Indices.pdf>) |
| [AgentOpt v0.1 Technical Report: Client-Side Optimization for LLM-Based Agent](https://arxiv.org/abs/2604.06296v2) | required | 2604.06296v2 | [PDF](<pdf/AgentOpt v0.1 Technical Report - Client-Side Optimization for LLM-Based Agent.pdf>) |
| [VineLM: Trie-Based Fine-Grained Control for Agentic Workflows](https://arxiv.org/abs/2605.23914v1) | required | 2605.23914v1 | [PDF](<pdf/VineLM - Trie-Based Fine-Grained Control for Agentic Workflows.pdf>) |
| [Cutting LLM Evaluation Costs with SySRs: A Bandit Algorithm that Provably Exploits Model Similarity](https://arxiv.org/abs/2606.07726v1) | background | 2606.07726v1 | [PDF](<pdf/Cutting LLM Evaluation Costs with SySRs - A Bandit Algorithm that Provably Exploits Model Similarity.pdf>) |
| [Bandit Eval - On Speeding Up Language Model Evaluation](https://arxiv.org/abs/2407.06172v3) | background | 2407.06172v3 | [PDF](<pdf/Bandit Eval - On Speeding Up Language Model Evaluation.pdf>) |
| [Prompt Eval - Efficient Multi-Prompt Evaluation of LLMs](https://arxiv.org/abs/2405.17202v3) | background | 2405.17202v3 | [PDF](<pdf/Prompt Eval - Efficient Multi-Prompt Evaluation of LLMs.pdf>) |
| [Hyperband: A Novel Bandit-Based Approach to Hyperparameter Optimization](https://www.jmlr.org/papers/v18/16-558.html) | background | JMLR 18(185), 2018 | [PDF](<pdf/hyperband-jmlr-2018.pdf>) |
| [Random Search for Hyper-Parameter Optimization](https://www.jmlr.org/papers/v13/bergstra12a.html) | background | JMLR 13(10), 2012 | [PDF](<pdf/random-search-jmlr-2012.pdf>) |
| [BOHB: Robust and Efficient Hyperparameter Optimization at Scale](https://proceedings.mlr.press/v80/falkner18a.html) | background | PMLR 80, 2018 | [PDF](<pdf/bohb-icml-2018.pdf>) |
| [SCOPE - Selective Conformal Optimized Pairwise LLM Judging](https://arxiv.org/abs/2602.13110v4) | context | 2602.13110v4 | [PDF](<pdf/SCOPE - Selective Conformal Optimized Pairwise LLM Judging.pdf>) |
| [Beyond Prompts: Measuring and Optimizing LLM Tool-Agent Harnesses](https://arxiv.org/abs/2609.05736v2) | context | 2609.05736v2 | [PDF](<pdf/Beyond Prompts - Measuring and Optimizing LLM Tool-Agent Harnesses.pdf>) |
| [An Empirical Study of Harness Design for Coding Agents](https://arxiv.org/abs/2609.20804v1) | context | 2609.20804v1 | [PDF](<pdf/An Empirical Study of Harness Design for Coding Agents.pdf>) |
| [Harness Engineering: Anatomy, Architecture, and Evolution of Coding Agents — A Source-Code Study of Eleven Systems](https://arxiv.org/abs/2609.00006v1) | context | 2609.00006v1 | [PDF](<pdf/Harness Engineering - Anatomy, Architecture, and Evolution of Coding Agents — A Source-Code Study of Eleven Systems.pdf>) |
| [Routerbench: A benchmark for multi-llm routing system](https://arxiv.org/abs/2403.12031v2) | context | 2403.12031v2 | [PDF](<pdf/Routerbench - A benchmark for multi-llm routing system.pdf>) |

Detailed notes: [GittinsEval](../docs/research/gittinseval-reading.md), [related work](../docs/research/related-work.md). Machine-readable citations are in [references.bib](references.bib).
