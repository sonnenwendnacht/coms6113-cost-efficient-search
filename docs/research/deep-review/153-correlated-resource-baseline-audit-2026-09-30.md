# Correlated-resource baseline audit for Experiment 2

Updated: 2026-09-30 23:56 ET

Two additional primary baselines narrow the space further:

* **C-LUCB** models correlations between arms through conditional-reward upper bounds and uses them to reduce best-arm samples ([paper](https://arxiv.org/abs/2109.04941)). A row-neighbor model that claims to exploit similarity must explain what conditional bound it knows and how it is estimated.
* **SH-RR** performs sequential halving while rationing one or more resources, with a history-dependent elimination rule and a deterministic resource-consumption guarantee ([paper](https://proceedings.mlr.press/v238/li24c.html)). Its resource accounting is closer to our fixed-dollar cap than an ordinary UCB parameter.

Other priced-information work studies selection when comparison costs are random or known to the algorithm ([Angelov, Kunal, and McGregor](https://arxiv.org/abs/0710.0083)). It is not a retry workflow model, but it reinforces that “different pull costs” alone is not a novelty claim.

## Revised baseline set

The full 729-row study should include, subject to a faithful implementation:

1. random and uniform allocation;
2. Matrix UCB-E and categorical BO;
3. direct paired racing and SySRs-style synchronized racing;
4. CW-CRN-R&S, using covariance-aware allocation with missing observations;
5. a C-LUCB-style correlated-arm control when conditional bounds can be registered;
6. an SH-RR-style resource-rationed elimination control;
7. CRPR only as a cross-fitted transfer ablation.

The important comparison is not the name of the allocator. It is whether a retry-specific implementation handles all of these at once: complete ordered rows, question-indexed correlated outcomes, verifier-censored reach, response-dependent whole-cell charge, and a fixed dollar cap. If an established baseline handles the same ledger at lower cost, the paper should report that honestly.

