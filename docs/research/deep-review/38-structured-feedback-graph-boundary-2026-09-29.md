# Structured BAI and feedback-graph boundary

This note records another prior-art check before we describe shared-row
comparisons as a contribution. The relevant literature already has two ways
to exploit structure during best-arm identification:

* Azizi, Kveton, and Ghavamzadeh's [fixed-budget structured BAI paper](https://www.ijcai.org/proceedings/2022/388)
  fits a joint generalization model and successively eliminates arms. It
  analyzes linear and generalized-linear structure and uses G-optimal design.
* Huang et al.'s [structured BAI paper](https://proceedings.mlr.press/v76/huang17a.html)
  maps several noisy micro-observables to action values and gives LUCB-micro.
  The fact that a row has several model slots, retry attempts, or derived
  features is therefore not itself a new structured-BAI formulation.

Russo, Song, and Pacchiano's [feedback-graph pure-exploration paper](https://proceedings.mlr.press/v258/russo25a.html)
  is a related but different abstraction. A graph edge means that pulling one
  action directly reveals another action's feedback. In our proposed hub
  design, pulling a hub row does **not** reveal the candidate row's answer or
  correctness. It supplies a same-question covariate/control variate and a
  paired difference only after the candidate is also run. Calling that a
  feedback graph would overstate the information available.

The defensible statement is consequently narrower: complete retry rows are
structured arms, and the row structure motivates a prior or a comparison
schedule, but correctness certification still needs candidate observations.
The proposed HAPR/CAPR protocol adds a same-question paired estimator and a
reusable hub ledger; it must be compared against structured BAI, graph/side
observation, and cached-incumbent baselines. It cannot claim novelty for
structured elimination, graph feedback, linear features, or G-optimal
allocation alone.

## Consequences for the protocol

1. A hub observation can reduce the variance of a candidate-versus-hub
   difference but cannot be counted as a candidate correctness sample.
2. The candidate's verifier path remains answer-key blind, and its reached
   retries determine the realized charge. The hub and candidate are coupled
   through the question stream, not through a free side-observation edge.
3. Any surrogate prediction over unpulled rows is a screening device. A
   final recommendation requires a directly observed confirmation row, with
   that confirmation charged and reported.
4. If we later fit a graph, linear, or neural model over row features, the
   paper must report it as an established structured-BAI component and make
   the novelty claim about the retry-aware ledger, paired finite-population
   evidence, and endogenous generator/verifier stopping.

This boundary also prevents an invalid proof shortcut: a confidence interval
for the hub mean plus a model-based prediction interval is not a confidence
interval for a candidate row unless the residual calibration and sampling
filtration are specified. The safe certificate remains based on directly
observed paired differences (or an explicitly validated residual bound).
