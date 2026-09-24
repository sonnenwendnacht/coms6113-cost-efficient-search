# Instructions for all coding assistants

This is a collaborative Columbia COMS 6113 research project. Read `README.md`, `docs/STATUS.md`, and the relevant research note before working. `CONTRIBUTING.md` defines collaboration conventions.

- Work on one claimed task and a separate branch/worktree. Preserve user changes. Coordinate file ownership if agents share a checkout.
- Distinguish source findings, hypotheses, synthetic demonstrations, and measured results. Never invent a citation, run, significance claim, or novelty claim.
- Do not expose held-out answers or unrevealed replay cells to the search policy.
- Record all paid attempts, including failed attempts and checker/tool calls. Cache reuse changes search spending, not the cold deployment cost of a configuration.
- Exact reuse requires matching task, execution state/history, model/version, prompt, checker, decoding settings, environment and repetition identity. A neighboring configuration is not an exact cache hit.
- An unvisited retry is missing/not reached, not a failed response. A cached result is not a fresh independent observation.
- Check source papers before attributing assumptions or results. Use primary links and precise sections where possible.
- The initial package uses Python's standard library. Add dependencies only for a concrete need and pin an appropriate environment for experiments.
- Run meaningful checks for changes to spending, stopping, data splits, or reuse. Do not spend model/API money as an incidental smoke test.
- Update project status and the relevant task after substantive work. Report exactly what ran and what remains unverified.

The current code is a small deterministic accounting scaffold, not an implementation or reproduction of AgentOpt, VineLM, GittinsEval, or the proposed method.
