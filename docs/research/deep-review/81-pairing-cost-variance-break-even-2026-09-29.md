# Pairing cost–variance break-even

Similarity should be treated as a prediction of paired residual variance, not
as a free transfer of a row's accuracy. Let `U_a(q)` and `U_b(q)` be the
registered row utilities on the same question, with variances
`sigma_a^2`, `sigma_b^2` and covariance `cov_ab`. A paired block of `n`
questions has difference variance

```text
Var(mean(U_a-U_b)) = (sigma_a^2 + sigma_b^2 - 2*cov_ab) / n.
```

If the realized per-question charges are approximately `c_a` and `c_b`, the
paired variance per profiling dollar is proportional to

```text
(sigma_a^2 + sigma_b^2 - 2*cov_ab) * (c_a + c_b).
```

An independent-arm comparison with the same dollar budget can allocate
different numbers of questions to the two rows. Its optimal variance per
dollar is proportional to

```text
(sigma_a*sqrt(c_a) + sigma_b*sqrt(c_b))^2.
```

Therefore pairing is justified only when the first expression is smaller than
the second. With equal costs and equal variances, positive same-question
covariance helps; with a very cheap and a very expensive row, independent
allocation may still win even when the rows are similar. A similarity method
that always pairs or always follows Hamming distance is not cost-aware.

## Algorithmic use

Use scout blocks to estimate a conservative upper bound on paired residual
variance and a lower bound on the covariance benefit. Compare that bound with
the independent cost allocation before selecting a paired block. If the
inequality is not certified, fall back to direct independent or complete-row
Top-Two allocation. Structural features may rank which pair to inspect next,
but the recommendation and confidence interval still come from directly
observed complete rows.

This gives Algorithm 2 one falsifiable source of improvement: it should save
profiling dollars only in regimes where residual covariance or amortized
shared-question measurements crosses this break-even condition. Equal-cost
low-covariance and highly heterogeneous-cost cases are required negative
controls.
