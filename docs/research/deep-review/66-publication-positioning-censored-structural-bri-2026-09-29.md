# Publication positioning: censored structural best-row identification

For a paper title and abstract, the method can be described as **Censored
Structural Best-Row Identification (CS-BRI)**, with HAPR as the concrete
hub-anchored racing implementation. The name makes the actual intersection
visible:

1. the arm is a Cartesian complete retry row;
2. later stages are censored by verifier outcomes and are not missing at
   random;
3. each pull has a random realized solver/verifier charge; and
4. final quality is hidden during profiling and certified on a held-out audit.

The algorithm synchronizes question blocks across complete rows, estimates
coordinate/path-stratum utility differences, allocates by uncertainty reduced
per conservative charge, and falls back to independent cost-aware racing when
the observed paired covariance is weak. A final direct block is mandatory.

This positioning does not claim that row similarity, UCB/BO, adaptive
stopping, or response-matrix imputation is new. SySRs, PULSE, GittinsEval,
cost-aware configuration bandits, and recent routing/cascade systems already
cover those ingredients. The proposed claim is their combination under the
declared retry-row observation contract, with a theorem conditional on a
low-dimensional structural model and an explicit failure fallback.

Because gold labels are withheld during profiling, a theorem also needs an
explicit verifier assumption. Either calibrate the deployment-visible
verdict/path signal on a separate labeled set, with a stated false-accept and
false-reject bound, or define the profiling target in terms of verifier utility
and make held-out gold accuracy purely empirical. Without such a condition,
no method can guarantee a gold-optimal row from arbitrary verifier outputs;
optimizing PASS rate would not be the same as optimizing accuracy.
