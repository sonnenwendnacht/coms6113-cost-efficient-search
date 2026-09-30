# 112: Graph-similarity prior-art boundary (2026-09-29)

## New primary-paper check

`Graph Feedback Bandits with Similar Arms` (Qi, Fei, and Zhu, UAI 2024)
studies stochastic bandits in which a graph encodes similar arms and proposes
UCB variants that exploit that structure. Its similarity relation is about
nearby arm means, and its feedback model gives the learner graph-structured
information. `Near Optimal Best Arm Identification for Clustered Bandits`
(Yash, Ghosh, and Karamchandani, ICML 2025) likewise clusters related bandit
instances and uses successive elimination with probably-correct guarantees.
`Structured Best Arm Identification with Fixed Confidence` (Huang et al.,
ALT 2017) formalizes actions whose values are functions of shared noisy
micro-observations.

These papers rule out several easy claims for our project:

- “Use a similarity graph to transfer evidence” is established structured-BAI
  methodology.
- “Cluster rows and search one representative per cluster” is an established
  baseline family, not Algorithm 2's novelty.
- A Hamming graph over the nine-by-nine-by-nine row coordinates is only a
  candidate prior. It is not evidence that a row pull reveals anything about a
  neighbor.

## The exact difference that remains testable

In our setting, buying a complete `(configuration, question)` execution does
not automatically return a neighbor's result. The only legitimate reuse is
from cells that were actually paid for, usually by comparing two complete rows
on the same fixed question block. Retry reach, verifier outcomes, and charges
are part of that paid cell; later-attempt outcomes for an unexecuted row are
counterfactual and cannot be imputed from a graph edge.

Therefore the structured methods should be described as **graph-guided
challenger ordering with paid paired evidence**, not graph-feedback bandits.
The graph may decide which challenger to try next, but it cannot shrink a row's
confidence interval until that row has been observed. This distinction also
explains why a random-permutation graph control is mandatory: if the same
benefit survives after destroying the categorical adjacency, the proposed
similarity mechanism is not responsible.

## Consequences for Algorithm 2

The defensible algorithm contract is now:

1. Register complete row coordinates and a fixed question bank.
2. Use a pilot or cross-fitted fold to estimate paired residual variance for
   candidate edges; do not declare edges from Hamming distance alone.
3. Allocate a same-question block to an observed row/challenger pair, charging
   every complete execution and recording its realized charge.
4. Use the edge only to prioritize the next comparison. Elimination still
   requires a valid paired confidence bound, and a row cannot be recommended
   without direct evidence.
5. If residual similarity or cost amortization fails its pre-registered gate,
   fall back to direct cost-aware racing.

This is a useful implementation and evaluation rule, but not yet a theorem or
novelty claim. A publishable contribution would need to show that this paid,
complete-row setting creates a measurable equal-dollar advantage over graph,
clustered-BAI, cached-incumbent, and direct paired baselines while preserving
the independent held-out audit.

## Sources

- Qi, Fei, Zhu, “Graph Feedback Bandits with Similar Arms,” UAI 2024:
  https://proceedings.mlr.press/v244/qi24a.html
- Yash, Ghosh, Karamchandani, “Near Optimal Best Arm Identification for
  Clustered Bandits,” ICML 2025:
  https://proceedings.mlr.press/v267/yash25a.html
- Huang et al., “Structured Best Arm Identification with Fixed Confidence,”
  ALT 2017: https://proceedings.mlr.press/v76/huang17a.html
