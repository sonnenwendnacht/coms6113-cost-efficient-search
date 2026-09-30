# 137: Combinatorial configuration prior art (2026-09-29)

The 9x9x9 row space is a product action space, so factorization alone is not
an Algorithm 2 contribution. [AC-Band](https://ojs.aaai.org/index.php/AAAI/article/view/26456)
already applies combinatorial bandits to algorithm configuration, and
combinatorial pure-exploration work covers structured action sets with full or
partial feedback ([Du, Kuroki, and Chen](https://ojs.aaai.org/index.php/AAAI/article/view/16892);
[Gabillon et al.](https://proceedings.mlr.press/v51/gabillon16.html)). Graph
Cartesian-product Bayesian optimization also models categorical configuration
spaces ([COMBO](https://proceedings.neurips.cc/paper/2019/hash/2cb6b10338a7fc4117a80da24b582060-Abstract.html)).

For this project, a factor model such as

\[
\mu_{a,b,c}=\beta_0+\beta_1(a)+\beta_2(b)+\beta_3(c)
\]

is only a diagnostic. Retry feedback can create strong interactions between
slots: the second solver sees the first solver's text and verifier feedback,
and the third sees the earlier path. Additive or low-order interaction
assumptions must therefore be cross-validated on held-out question blocks and
must fail closed when residuals are large.

The defensible distinction is narrower than “structured search”: a complete
row is the unit of deployment, the same question can be run under several
rows for paired residuals, and each cell's realized cost includes the
verifier-controlled retry path. A future comparison should include AC-Band or
a combinatorial pure-exploration baseline, a graph/GP baseline, and direct
paired elimination. Any gain must survive a shuffled-coordinate control and
the same realized-dollar ledger.

No implementation or experiment is claimed by this note.
