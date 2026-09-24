# Working together

`main` is the shared, working version. Put each task on its own branch, open a pull request, and have another person review it before merging. The initial setup commits are the exception. GitHub requires one approving review, passing `offline-checks`, an up-to-date branch, and resolved review conversations. Stale approvals are dismissed after changes. Force pushes and branch deletion are blocked. The repository owner retains an administrator override for setup and recovery; ordinary team work follows the same review process.

## One task, one branch, one owner

1. Claim an issue (or an entry in `docs/TASKS.md`) and name the owner and files being changed.
2. Start from the latest `main`:

   ```bash
   git switch main
   git pull --ff-only
   git switch -c research/your-name-short-topic
   ```

3. Use `research/`, `feat/`, `fix/`, or `docs/` as a branch prefix. Make focused commits.
4. Run `python3 -m unittest discover -s tests -v` and the checks relevant to your change.
5. Push your branch, open a pull request, and explain the change, evidence, and limitations. Link the issue. Squash merge after review; delete the merged branch.

Do not force-push `main`, overwrite another person's work, or commit credentials, full benchmark dumps, raw model responses, caches, or unreviewed generated results. Review `git diff --cached` before committing.

## Codex and Claude Code

Both follow [AGENTS.md](AGENTS.md); [CLAUDE.md](CLAUDE.md) points to the same instructions. Humans own research decisions and final claims. Record material assistant contributions in pull requests and experiment records.

Use separate working directories when multiple assistants work concurrently:

```bash
git worktree add ../coms6113-codex -b feat/codex-topic main
git worktree add ../coms6113-claude -b feat/claude-topic main
```

They can share the repository history, but should not edit the same working directory or task branch at the same time. Do not change another assistant's checkout underneath it.

## Research records

- Label every statement as a cited finding, a hypothesis, a decision, or a measured result as appropriate.
- A run record includes the commit, settings, dataset version and split hash, model snapshots, prompt/checker versions, seed, pricing snapshot, spending, and artifact location.
- Preserve failed and negative runs. Do not select only favorable seeds or budgets.
- Changes to the objective, splits, retry meaning, or cost definition belong in a dated decision record before a confirmatory run.
- The repository is public at the owner's request. The group has not selected a software license; do not add one or change visibility as an incidental edit.

## Repository owner

GitHub owner: `sonnenwendnacht`. Add confirmed teammate accounts with write access; invite mentors only when requested. Do not use a placeholder CODEOWNERS file that implies unconfirmed people have agreed to review.
