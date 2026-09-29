# Gold-visibility protocol correction

The project must distinguish two information boundaries that were conflated in
some earlier notes.

* **Runtime boundary:** the solver/verifier workflow cannot use the MathQA
  answer key. The fixed verifier sees the question, options, candidate, and
  retry context only; its PASS/RETRY decision controls whether another call
  is reached.
* **Benchmark profiling boundary:** after a complete paid cell finishes, the
  evaluator may compare its final answer with the answer key and expose
  `final_correct` to the selector. This is how the current replay and the
  mentor's response-matrix setting update their search scores. The selector
  still cannot read unpulled cells or the held-out evaluation split.

The distinction matters for the paper. HAPR's primary experiment should be
the benchmark-profiling setting, with `Q(c,q)` revealed only after paying for
that complete row/question cell and held-out questions withheld until the
recommendation. A second deployment-adaptive variant can forbid post-run gold
scores, but then it must target verifier utility or assume calibrated
verdict-to-correctness error; it cannot claim a gold-accuracy guarantee from
arbitrary PASS/RETRY signals.

This correction aligns the proposed comparison with GittinsEval and the
existing `run_sweep` replay, while preserving the answer-key-blind verifier
requirement. It also removes an accidental novelty claim: hidden gold labels
are not the contribution. The contribution remains complete-row structure,
verifier-gated reach, realized path charge, and observed same-question row
dependence under limited profiling.
