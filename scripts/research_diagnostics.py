"""Exact calculations on invented finite populations, not LLM experiments.

Run with --output PATH to save JSON. Uses only the Python standard library.
The examples test assumptions and accounting; no search-method superiority is
measured. Fractions avoid rounding in the identities being checked.
"""

import argparse
from fractions import Fraction as F
from itertools import combinations, product
import json
from pathlib import Path


def mean(values):
    return sum(values, F(0)) / len(values)


def variance(values):
    center = mean(values)
    return mean([(x - center) ** 2 for x in values])


def calculate():
    # Two policies share their prefix. The checker stops on 90 tasks, but ten
    # of those accepted answers are wrong. Only ten tasks reach the differing slot.
    common = [1] * 80 + [0] * 10
    suffix_a = [1] * 2 + [0] * 8
    suffix_b = [1] * 8 + [0] * 2
    ya, yb = common + suffix_a, common + suffix_b
    differences = [b - a for a, b in zip(ya, yb)]
    conditional = [b - a for a, b in zip(suffix_a, suffix_b)]
    reach = F(len(suffix_a), len(ya))
    gap = mean(differences)
    assert gap == reach * mean(conditional) == F(6, 100)
    assert abs(gap) <= reach
    assert mean([d * d for d in differences]) <= reach

    # All possible binary completions of this reached set have scores inside
    # one common interval. This is exact for this finite toy population.
    group_lower, group_upper = F(80, 100), F(90, 100)
    completion_means = [F(sum(common) + sum(tail), 100)
                        for tail in product([0, 1], repeat=10)]
    assert min(completion_means) == group_lower
    assert max(completion_means) == group_upper
    incumbent = F(93, 100)
    assert all(x < incumbent for x in completion_means)

    prefix_price, a_price, b_price = F(2), F(5), F(7)
    shared_pair_price = prefix_price + reach * (a_price + b_price)
    separate_pair_price = 2 * prefix_price + reach * (a_price + b_price)
    paired_var = variance(differences)
    independent_var = variance(ya) + variance(yb)

    # Failure populations differ despite equally accurate initial models.
    # A retry solves 72/80 easy and 2/20 hard questions deterministically.
    retry_correct = set(range(72)) | {80, 81}
    fails_a = set(range(80, 100))
    fails_b = set(range(18)) | {72, 73}
    conditional_a = F(len(fails_a & retry_correct), len(fails_a))
    conditional_b = F(len(fails_b & retry_correct), len(fails_b))
    standalone_retry = F(len(retry_correct), 100)
    score_a = F(80, 100) + F(20, 100) * conditional_a
    score_b = F(80, 100) + F(20, 100) * conditional_b
    naive = F(80, 100) + F(20, 100) * standalone_retry
    assert (score_a, score_b, naive) == (F(82, 100), F(98, 100), F(948, 1000))

    # Uniform selection among reached cases has the right conditional mean.
    # Choosing two known-positive differences gives a biased population estimate.
    uniform_estimates = [reach * mean([conditional[i] for i in chosen])
                         for chosen in combinations(range(10), 2)]
    assert mean(uniform_estimates) == gap
    positives = [i for i, value in enumerate(conditional) if value > 0]
    selected = reach * mean([conditional[i] for i in positives[:2]])
    assert selected == F(10, 100) and selected != gap

    # Reveal two successful B suffixes and conservatively leave eight unknown.
    # Adaptive revelation does not invalidate these pointwise finite-row bounds.
    partial_lower, partial_upper = F(82, 100), F(90, 100)
    remaining_scores = [F(82 + sum(tail), 100)
                        for tail in product([0, 1], repeat=8)]
    assert all(partial_lower <= s <= partial_upper for s in remaining_scores)
    assert partial_lower <= mean(yb) <= partial_upper

    # Plain one-coordinate distance places no bound below 1 on a score gap.
    config_a = ("planner_A", "solver_fixed")
    config_b = ("planner_B", "solver_fixed")
    hamming = sum(a != b for a, b in zip(config_a, config_b))
    assert hamming == 1
    one_change_gap = mean([1] * 100) - mean([0] * 100)
    assert one_change_gap == 1

    # Fixed-n, independent normal-means illustration, not an adaptive BAI rule.
    budget = 90
    allocations = [(F(1, n1) + F(1, n2), n1, n2)
                   for n1 in range(1, budget)
                   for n2 in range(1, budget // 9 + 1)
                   if n1 + 9 * n2 <= budget]
    optimal_var, n1, n2 = min(allocations)
    assert n1 + 9 * n2 <= budget
    equal_count_var = F(2, 9)
    equal_dollar_var = F(1, 45) + F(1, 5)
    assert optimal_var < equal_count_var and optimal_var < equal_dollar_var

    return {
        "kind": "exact calculations on invented populations; not empirical LLM results",
        "random_trials": 0,
        "model_api_calls": 0,
        "shared_prefix": {
            "questions": 100, "reached_questions": 10,
            "checker_stops": 90, "correct_stopped_answers": 80,
            "score_a": mean(ya), "score_b": mean(yb),
            "conditional_score_difference_b_minus_a": mean(conditional),
            "overall_score_difference_b_minus_a": gap,
            "bound_on_absolute_score_difference": reach,
            "paired_difference_variance": paired_var,
            "independent_difference_variance": independent_var,
            "variance_ratio_independent_over_paired": independent_var / paired_var,
            "shared_pair_search_cost": shared_pair_price,
            "separate_pair_search_cost": separate_pair_price,
            "cold_deployment_cost_a": prefix_price + reach * a_price,
            "cold_deployment_cost_b": prefix_price + reach * b_price,
            "cost_unit": "invented unit, not USD",
        },
        "subtree_bounds": {
            "enumerated_completions": len(completion_means),
            "exact_finite_population_interval": [group_lower, group_upper],
            "known_incumbent_score": incumbent,
            "all_completions_quality_dominated": True,
            "caveat": "Dominance here assumes equal feasibility; real sample bounds need uncertainty.",
        },
        "failure_conditioning": {
            "standalone_retry_score": standalone_retry,
            "retry_score_after_a_failure": conditional_a,
            "retry_score_after_b_failure": conditional_b,
            "initial_score_both": F(80, 100),
            "actual_final_a": score_a, "actual_final_b": score_b,
            "naive_independence_estimate_both": naive,
        },
        "selected_suffix_bias": {
            "true_overall_difference": gap,
            "cherry_picked_two_positive_estimate": selected,
            "uniform_two_sample_design_expectation": mean(uniform_estimates),
            "enumerated_uniform_subsets": len(uniform_estimates),
        },
        "partial_revelation": {
            "exact_finite_row_interval": [partial_lower, partial_upper],
            "true_score_b": mean(yb),
            "enumerated_remaining_completions": len(remaining_scores),
            "caveat": "The interval is conservative, not an imputed point estimate.",
        },
        "hamming_counterexample": {
            "differing_slots": hamming, "possible_score_gap": one_change_gap,
        },
        "rare_expensive_suffix": {
            "reach_probability": F(1, 100),
            "quality_gap_upper_bound": F(1, 100),
            "extra_conditional_cost": 1000,
            "extra_expected_cost": F(1, 100) * 1000,
            "cost_unit": "invented unit, not USD",
        },
        "zero_reaches_uncertainty": {
            "iid_parent_samples": 100, "observed_reaches": 0,
            "fixed_sample_one_sided_confidence": 0.95,
            "exact_binomial_upper_reach_bound": 1 - 0.05 ** (1 / 100),
            "caveat": "Single fixed-n bound, not simultaneous or valid for arbitrary optional stopping.",
        },
        "two_mean_allocation": {
            "variances": [1, 1], "costs": [1, 9], "budget": budget,
            "optimal_integer_sample_counts": [n1, n2],
            "optimal_estimated_difference_variance": optimal_var,
            "equal_count_difference_variance": equal_count_var,
            "equal_dollar_difference_variance": equal_dollar_var,
            "continuous_optimum_sample_ratio_n1_over_n2": 3,
            "caveat": "Fixed two-mean estimation example, not a theorem for full adaptive search.",
        },
    }


def encode(value):
    if isinstance(value, F):
        return float(value)
    raise TypeError(type(value).__name__)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = calculate()
    output = json.dumps(result, indent=2, default=encode) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output)
        print(f"Saved {len(result) - 3} exact illustrative diagnostics to {args.output}")
    else:
        print(output, end="")


if __name__ == "__main__":
    main()
