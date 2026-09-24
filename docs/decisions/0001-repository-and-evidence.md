# 0001: Repository and evidence conventions

Date: 2026-09-23. Status: setup defaults; research choices remain proposals.

- Use a private repository under `sonnenwendnacht`, named `coms6113-cost-efficient-search`, with `main` as the shared branch.
- Keep source code, settings, citations, protocols, and small reviewed summaries in Git. Keep original meeting screenshots, downloaded PDFs, raw responses, and generated runs local; provide a versioned PDF download manifest.
- Use the same assistant instructions for Codex and Claude Code and separate worktrees for concurrent tasks.
- Separate search, audit/reference construction, and deployment costs in all research reporting. Do not describe synthetic checks as empirical findings.
- Start with a dependency-free Python accounting scaffold. Model APIs, benchmark selection, budget, and the proposed search algorithm are not implemented or fixed by this setup.

Pending group decisions: benchmark and deployable retry checker; model snapshots and authorized spending budget; primary constrained objective; public licensing; paper venue and author/contribution process.
