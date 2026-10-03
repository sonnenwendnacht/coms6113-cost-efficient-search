#!/usr/bin/env python3
"""Measure correctness-vector similarity between Experiment 1 rows.

For every pair of the 729 complete rows, this script computes:

* phi/Pearson correlation between their 200 binary correctness values;
* question-level agreement, the fraction of equal correctness bits.

Pairs are grouped by the exact retry slots they share.  Search and audit
questions are analyzed separately.  The result is descriptive finite-bank
analysis, not an independence-based significance test.
"""

from __future__ import annotations

import argparse
import csv
from collections import OrderedDict
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


SLOTS = ("original", "retry_1", "retry_2")
MASK_ORDER = (0, 1, 2, 4, 3, 5, 6)
MASK_LABEL = {
    0: "none",
    1: "retry_2 only",
    2: "retry_1 only",
    4: "original only",
    3: "retry_1 + retry_2",
    5: "original + retry_2",
    6: "original + retry_1",
}


def read_matrix(path: Path, prefix: str) -> tuple[list[str], list[tuple[str, str, str]], np.ndarray]:
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != 729:
        raise ValueError(f"expected 729 rows, found {len(rows)}")
    names = [row["config_id"] for row in rows]
    triples = [tuple(name.split("/")) for name in names]
    if any(len(triple) != 3 for triple in triples):
        raise ValueError("every config_id must contain three slash-separated model names")
    columns = [f"{prefix}_q{i:03d}" for i in range(200)]
    matrix = np.array([[int(row[column]) for column in columns] for row in rows], dtype=np.float64)
    if not np.isin(matrix, [0, 1]).all():
        raise ValueError("correctness matrix is not binary")
    return names, triples, matrix


def pair_statistics(matrix: np.ndarray, triples: list[tuple[str, str, str]]) -> list[dict[str, object]]:
    n_rows, n_questions = matrix.shape
    if n_rows != 729 or n_questions != 200:
        raise ValueError(f"expected 729 x 200 matrix, found {matrix.shape}")

    i, j = np.triu_indices(n_rows, k=1)
    means = matrix.mean(axis=1)
    std = matrix.std(axis=1, ddof=1)
    if np.any(std == 0):
        raise ValueError("a row has zero variance; phi correlation would be undefined")
    standardized = (matrix - means[:, None]) / std[:, None]
    correlations = (standardized @ standardized.T) / (n_questions - 1)
    phi = correlations[i, j]
    agreement = 1.0 - np.not_equal(matrix[i], matrix[j]).mean(axis=1)

    equal = np.array(
        [[triples[a][slot] == triples[b][slot] for slot in range(3)] for a, b in zip(i, j)],
        dtype=bool,
    )
    masks = equal[:, 0] * 4 + equal[:, 1] * 2 + equal[:, 2]
    shared_count = equal.sum(axis=1)

    groups: OrderedDict[tuple[str, str], np.ndarray] = OrderedDict()
    for mask in MASK_ORDER:
        groups[("exact_shared_slots", str(mask))] = masks == mask
    for slot, slot_name in enumerate(SLOTS):
        groups[("slot_same", slot_name)] = equal[:, slot]
        groups[("slot_different", slot_name)] = ~equal[:, slot]
    for count in (0, 1, 2):
        groups[("shared_slot_count", str(count))] = shared_count == count

    output: list[dict[str, object]] = []
    for group_type, group_name in groups:
        selected = groups[(group_type, group_name)]
        corr_values = phi[selected]
        agreement_values = agreement[selected]
        if len(corr_values) == 0:
            continue
        if group_type == "exact_shared_slots":
            label = MASK_LABEL[int(group_name)]
        elif group_type in {"slot_same", "slot_different"}:
            label = f"{group_name} {group_type.replace('_', ' ')}"
        else:
            label = f"{group_name} shared slots"
        output.append(
            {
                "group_type": group_type,
                "group": group_name,
                "label": label,
                "pair_count": int(len(corr_values)),
                "mean_phi": float(corr_values.mean()),
                "median_phi": float(np.median(corr_values)),
                "std_phi": float(corr_values.std(ddof=1)) if len(corr_values) > 1 else 0.0,
                "mean_agreement": float(agreement_values.mean()),
                "median_agreement": float(np.median(agreement_values)),
            }
        )
    return output


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = list(rows[0])
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def stats(rows: list[dict[str, object]], split: str, group_type: str, group: str) -> dict[str, object]:
    for row in rows:
        if row["split"] == split and row["group_type"] == group_type and row["group"] == group:
            return row
    raise KeyError((split, group_type, group))


def write_report(path: Path, rows: list[dict[str, object]]) -> None:
    exact = [row for row in rows if row["group_type"] == "exact_shared_slots"]
    lines = [
        "# Experiment 1 row-similarity analysis",
        "",
        "This descriptive analysis uses the binary final-workflow correctness vectors "
        "from `experiment1-nine-model-correctness.csv`. For every pair of the 729 "
        "complete rows, phi/Pearson correlation measures whether the two rows tend "
        "to be correct on the same questions. Agreement is the fraction of questions "
        "on which their correctness bits are equal. Search and audit splits are kept "
        "separate. Pair observations are dependent, so these are finite-bank "
        "descriptive summaries rather than independent-sample significance tests.",
        "",
        "## Exact shared-slot groups",
        "",
        "| Split | Shared slots exactly | Pairs | Mean correlation | Mean agreement |",
        "|---|---|---:|---:|---:|",
    ]
    for row in exact:
        lines.append(
            f"| {row['split']} | {row['label']} | {row['pair_count']:,} | "
            f"{float(row['mean_phi']):.3f} | {float(row['mean_agreement']):.3f} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "* Sharing the **original solver** is the dominant similarity signal. "
            "Pairs sharing only that slot have correlation about 0.933 on search "
            "and 0.921 on audit, with about 99.4% and 99.1% agreement.",
            "* Sharing **retry 1 only** or **retry 2 only** has almost no structural "
            "effect: correlation is about 0.064/0.047 and agreement about 0.669/0.670, "
            "essentially the same as pairs sharing no slots.",
            "* The aggregate count of shared slots is misleading unless the slot is "
            "identified. Its apparent positive effect is almost entirely caused by "
            "the original solver slot.",
            "* This supports an original-slot-aware search prior, but it does not "
            "show that retry choices can be safely inferred. The natural stopping "
            "policy rarely reaches retries, so Experiment 2 needs a forced-retry "
            "calibration stratum.",
            "",
            "The correlation is between final correctness vectors, not between model "
            "names or costs. It reflects shared question difficulty and the deployed "
            "verifier's stopping behavior as well as model similarity.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def plot(path: Path, rows: list[dict[str, object]]) -> None:
    exact = [row for row in rows if row["group_type"] == "exact_shared_slots"]
    labels = [row["label"] for row in exact if row["split"] == "search"]
    search = [float(row["mean_phi"]) for row in exact if row["split"] == "search"]
    audit = [float(row["mean_phi"]) for row in exact if row["split"] == "audit"]
    search_agree = [float(row["mean_agreement"]) for row in exact if row["split"] == "search"]
    audit_agree = [float(row["mean_agreement"]) for row in exact if row["split"] == "audit"]
    x = np.arange(len(labels))
    width = 0.36
    fig, axes = plt.subplots(1, 2, figsize=(14, 5.5), sharex=True)
    for ax, left, right, title, ylabel in [
        (axes[0], search, audit, "Correctness correlation", "Mean phi correlation"),
        (axes[1], search_agree, audit_agree, "Question-level agreement", "Mean fraction equal"),
    ]:
        ax.bar(x - width / 2, left, width, label="Search", color="#3568a8")
        ax.bar(x + width / 2, right, width, label="Audit", color="#c45a36")
        ax.set_title(title)
        ax.set_ylabel(ylabel)
        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation=32, ha="right")
        ax.grid(axis="y", alpha=0.25)
        ax.legend(frameon=False)
    axes[0].axhline(0, color="#222", linewidth=0.8)
    axes[0].set_ylim(-0.05, 1.05)
    axes[1].set_ylim(0.6, 1.02)
    fig.suptitle("Experiment 1: what row similarity is actually present?", fontsize=15)
    fig.text(
        0.5,
        0.01,
        "Groups are exact shared-slot patterns; rows are complete (original, retry 1, retry 2) configurations.",
        ha="center",
        fontsize=9,
    )
    fig.tight_layout(rect=(0, 0.05, 1, 0.94))
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=220, bbox_inches="tight")
    plt.close(fig)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=Path("results/experiment1-nine-model-correctness.csv"))
    parser.add_argument("--csv", type=Path, default=Path("results/experiment1-similarity-analysis.csv"))
    parser.add_argument("--report", type=Path, default=Path("results/experiment1-similarity-analysis.md"))
    parser.add_argument("--plot", type=Path, default=Path("results/experiment1-similarity-analysis.png"))
    args = parser.parse_args()

    _, triples, search_matrix = read_matrix(args.input, "search")
    _, _, audit_matrix = read_matrix(args.input, "audit")
    output: list[dict[str, object]] = []
    for split, matrix in (("search", search_matrix), ("audit", audit_matrix)):
        for row in pair_statistics(matrix, triples):
            row = {"split": split, **row}
            output.append(row)
    write_csv(args.csv, output)
    write_report(args.report, output)
    plot(args.plot, output)
    print(f"wrote {args.csv}, {args.report}, and {args.plot}")
    for split in ("search", "audit"):
        row = stats(output, split, "exact_shared_slots", "4")
        retry1 = stats(output, split, "exact_shared_slots", "2")
        retry2 = stats(output, split, "exact_shared_slots", "1")
        print(
            f"{split}: original-only r={float(row['mean_phi']):.3f}, "
            f"retry1-only r={float(retry1['mean_phi']):.3f}, "
            f"retry2-only r={float(retry2['mean_phi']):.3f}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
