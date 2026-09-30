# COMS 6113 · Group 18

**Cost-Efficient Search for Agentic Workflows with Retries**

We study how to find a good combination of models for a multi-step workflow without spending more testing combinations than we can save by using the winner. A configuration specifies which model handles each stage and each allowed retry. The aim is a publishable research contribution; no method or result is established yet.

Repository: <https://github.com/sonnenwendnacht/coms6113-cost-efficient-search> (public).

## Start here

1. Read [the meeting record](docs/meetings/2026-09-23.md): what the supplied screenshots and mentor's whiteboard actually show.
2. Read [the detailed research assessment](docs/research/deep-review/README.md): source/code audits, checked derivations, precise novelty limits, and a falsifiable pilot.
3. Follow its links to the mentor-paper audit, workflow prior art, mathematical formulation, and experimental protocol. The [initial research plan](docs/research/research-plan.md) records the first proposal.
4. Follow [CONTRIBUTING.md](CONTRIBUTING.md) before changing code or running experiments.
5. Pick an unclaimed task in [the work plan](docs/TASKS.md).

## Get a working copy

```bash
git clone git@github.com:sonnenwendnacht/coms6113-cost-efficient-search.git
cd coms6113-cost-efficient-search
python3 -m unittest discover -s tests -v
python3 scripts/smoke_demo.py
python3 scripts/research_diagnostics.py
python3 scripts/download_papers.py
```

Python 3.11+ is the initial target. The starter code and checks use only the standard library. The demo and nine exact research diagnostics use invented data and make no API calls. They check assumptions, cost accounting and retry behavior; they are not empirical method-performance evidence.

## Where things go

| Location | Contents |
| --- | --- |
| `docs/research/` | Literature notes, hypotheses, evaluation plan |
| `docs/meetings/` | Dated meeting records with source and uncertainty |
| `docs/decisions/` | Agreed project choices and their rationale |
| `papers/` | Paper catalog, download script inputs, local PDFs |
| `configs/` | Versioned experiment settings |
| `src/retry_search/` | Shared implementation |
| `tests/` | Checks of behavior that affects research validity |
| `experiments/` | Protocols and run records |
| `results/` | Small reviewed summaries; generated runs stay local |
| `data/` | Dataset provenance and access instructions |

PDFs are downloaded into `papers/pdf/` but kept out of Git. Everyone gets the same versions using the manifest and checksum checks. The original screenshots remain untouched on the setup computer; their relevant content is recorded in the meeting note.

## Research guardrails

- Keep **search spending**, **independent evaluation spending**, and **deployment cost** separate.
- Shared execution history can sometimes be reused exactly. Similar-looking configurations only suggest similar outcomes; they do not prove them.
- Later retries see the cases that reached them, usually earlier failures. Their observed accuracy is not unconditional accuracy.
- Give comparison methods equal dollar budgets and equal access to reusable history.
- Keep final evaluation questions hidden from the search. Without an exhaustive reference, distinguish comparisons with measured competitors from a conservative whole-space certificate; neither is measured exact regret.
- A retry decision must use information available in actual deployment, not hidden benchmark answers.

See [project status](docs/STATUS.md) for what is implemented, verified, and still pending. No paid model evaluations have been run.
