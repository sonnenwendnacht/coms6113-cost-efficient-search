#!/usr/bin/env python3
"""Audit a completed retry trace without revealing held-out cells to selectors.

This standard-library script makes no model calls and never modifies its input.
It emits aggregate diagnostics only: no question text, answer keys, raw model
responses, or per-question outcomes. Optional dataset files enable correctness
checks for intermediate attempts, after SHA-256 provenance is verified.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import itertools
import json
import math
from pathlib import Path
from typing import Any


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def rate(numerator: float, denominator: int) -> float | None:
    return numerator / denominator if denominator else None


def valid_answer(answer: Any) -> bool:
    return isinstance(answer, str) and answer.lower() in ('a', 'b', 'c', 'd', 'e')


def gold_labels(path: Path, expected_sha256: str, count: int, seed: int) -> tuple[list[str], list[str]]:
    if file_sha256(path) != expected_sha256:
        raise ValueError(f'dataset checksum mismatch: {path}')
    source = json.loads(path.read_text(encoding='utf-8'))
    # This is the generator's stable_sample contract, reproduced explicitly.
    keyed = [(hashlib.sha256(f"{seed}:{i}:{row['Problem']}".encode()).hexdigest(), i, row)
             for i, row in enumerate(source)]
    keyed.sort(key=lambda item: (item[0], item[1]))
    if len(keyed) < count:
        raise ValueError('dataset contains fewer than the declared questions')
    labels = [str(row['correct']).lower() for _, _, row in keyed[:count]]
    if not all(valid_answer(answer) for answer in labels):
        raise ValueError('dataset has an invalid selected answer key')
    problem_hashes = [hashlib.sha256(row['Problem'].encode()).hexdigest() for _, _, row in keyed[:count]]
    return labels, problem_hashes


def validate(traces: list[dict[str, Any]], metadata: dict[str, Any]) -> list[str]:
    models = metadata['solver_models']
    configs = sorted('/'.join(parts) for parts in itertools.product(models, repeat=3))
    if len(set(models)) != len(models) or len(configs) != metadata['rows']:
        raise ValueError('metadata model pool and row count disagree')
    question_count = metadata['search_n'] + metadata['evaluation_n']
    expected = {(config, q) for config in configs for q in range(question_count)}
    seen = set()
    for row in traces:
        q = row['question_id']
        if isinstance(q, bool) or not isinstance(q, int):
            raise ValueError('question_id must be an integer')
        key = (row['config_id'], q)
        if key not in expected or key in seen:
            raise ValueError('unknown or duplicate config/question trace')
        seen.add(key)
        attempts, calls = row['attempts'], row['calls']
        if not isinstance(attempts, list) or not 1 <= len(attempts) <= 3:
            raise ValueError('each workflow must have one to three reached attempts')
        if len(calls) != 2 * len(attempts):
            raise ValueError('each reached attempt needs a solver and verifier call')
        if any(attempt['verifier_pass'] for attempt in attempts[:-1]):
            raise ValueError('workflow continued after verifier acceptance')
        if len(attempts) < 3 and not attempts[-1]['verifier_pass']:
            raise ValueError('workflow stopped early without verifier acceptance')
        if row['accepted_attempt'] != (len(attempts) if attempts[-1]['verifier_pass'] else None):
            raise ValueError('accepted_attempt disagrees with attempts')
        if row['final_answer'] != attempts[-1]['answer'] or row['final_correct'] not in (0, 1):
            raise ValueError('invalid final answer or correctness')
        for index, (attempt, model) in enumerate(zip(attempts, row['config_id'].split('/'))):
            solver, verifier = calls[2 * index:2 * index + 2]
            if attempt['attempt'] != index + 1 or attempt['solver_model'] != model:
                raise ValueError('reached attempt disagrees with configuration')
            if solver['role'] != 'solver' or solver['model'] != model:
                raise ValueError('solver call disagrees with attempt')
            if verifier['role'] != 'verifier' or verifier['model'] != metadata['verifier_model']:
                raise ValueError('invalid fixed verifier call')
        for call in calls:
            if call['coefficient_usd_per_token'] != metadata['coefficients_usd_per_input_token'][call['model']]:
                raise ValueError('call coefficient disagrees with metadata')
            if any(isinstance(call[key], bool) or not isinstance(call[key], int) or call[key] < 0
                   for key in ('input_tokens', 'output_tokens')):
                raise ValueError('token counts must be nonnegative integers')
        cost = math.fsum(c['coefficient_usd_per_token'] * c['input_tokens'] for c in calls)
        if not math.isclose(cost, row['cost_usd'], rel_tol=1e-12, abs_tol=1e-15):
            raise ValueError('primary cost ledger mismatch')
        if row['input_tokens'] != sum(c['input_tokens'] for c in calls):
            raise ValueError('input-token ledger mismatch')
    if seen != expected:
        raise ValueError(f'incomplete trace rectangle: missing {len(expected - seen)} cells')
    return configs


def confusion(pairs: list[tuple[bool, bool]]) -> dict[str, Any]:
    counts = Counter(('pass' if passed else 'retry') + ('_correct' if correct else '_incorrect')
                     for passed, correct in pairs)
    out = {key: counts[key] for key in ('pass_correct', 'pass_incorrect', 'retry_correct', 'retry_incorrect')}
    out['false_pass_fraction_among_passes'] = rate(out['pass_incorrect'], out['pass_correct'] + out['pass_incorrect'])
    out['false_retry_fraction_among_retries'] = rate(out['retry_correct'], out['retry_correct'] + out['retry_incorrect'])
    out['pass_rate_given_incorrect'] = rate(out['pass_incorrect'], out['pass_incorrect'] + out['retry_incorrect'])
    out['retry_rate_given_correct'] = rate(out['retry_correct'], out['pass_correct'] + out['retry_correct'])
    return out


def summarize(rows: list[dict[str, Any]], metadata: dict[str, Any], gold: dict[int, str] | None) -> dict[str, Any]:
    calls = [call for row in rows for call in row['calls']]
    attempts = [attempt for row in rows for attempt in row['attempts']]
    solver_calls = [c for c in calls if c['role'] == 'solver']
    verifier_calls = [c for c in calls if c['role'] == 'verifier']
    grouped = defaultdict(list)
    for row in rows:
        grouped[row['config_id']].append(row)
    vectors = [tuple(r['final_correct'] for r in sorted(values, key=lambda r: r['question_id']))
               for values in grouped.values()]
    pass_vectors = [tuple(bool(r['attempts'][-1]['verifier_pass']) for r in sorted(values, key=lambda r: r['question_id']))
                    for values in grouped.values()]
    total_cost = math.fsum(r['cost_usd'] for r in rows)
    final_parse_failures = sum(not valid_answer(r['final_answer']) for r in rows)
    out = {
        'cells': len(rows), 'configurations': len(grouped),
        'questions': len({r['question_id'] for r in rows}),
        'final_correct': sum(r['final_correct'] for r in rows),
        'final_accuracy': rate(sum(r['final_correct'] for r in rows), len(rows)),
        'final_parse_failures': final_parse_failures,
        'final_parse_failure_rate': rate(final_parse_failures, len(rows)),
        'accepted_unparseable_final_answers': sum(not valid_answer(r['final_answer']) and bool(r['attempts'][-1]['verifier_pass']) for r in rows),
        'attempt_parse_failures': sum(not valid_answer(a['answer']) for a in attempts),
        'attempt_count_histogram': dict(sorted(Counter(str(len(r['attempts'])) for r in rows).items())),
        'workflows_reaching_retry': sum(len(r['attempts']) > 1 for r in rows),
        'solver_calls': len(solver_calls), 'verifier_calls': len(verifier_calls),
        'solver_calls_at_output_cap': sum(c['output_tokens'] >= metadata['solver_max_new_tokens'] for c in solver_calls),
        'verifier_calls_at_output_cap': sum(c['output_tokens'] >= metadata['verifier_max_new_tokens'] for c in verifier_calls),
        'accepted_workflows': sum(bool(r['attempts'][-1]['verifier_pass']) for r in rows),
        'verifier_pass_calls': sum(bool(a['verifier_pass']) for a in attempts),
        'verifier_call_pass_rate': rate(sum(bool(a['verifier_pass']) for a in attempts), len(attempts)),
        'cost_usd_proxy': total_cost, 'mean_cold_workflow_cost_usd_proxy': rate(total_cost, len(rows)),
        'input_tokens': sum(c['input_tokens'] for c in calls),
        'output_tokens_uncharged': sum(c['output_tokens'] for c in calls),
        'unique_final_correct_reward_vectors': len(set(vectors)),
        'unique_verifier_pass_reward_vectors': len(set(pass_vectors)),
        'terminal_verifier_confusion': confusion([(bool(r['attempts'][-1]['verifier_pass']), bool(r['final_correct'])) for r in rows]),
    }
    if gold is not None:
        for row in rows:
            if row['final_correct'] != int(row['final_answer'] == gold[row['question_id']]):
                raise ValueError('recorded final correctness disagrees with verified dataset')
        out['all_attempts_verifier_confusion'] = confusion([
            (bool(a['verifier_pass']), a['answer'] == gold[r['question_id']])
            for r in rows for a in r['attempts']])
    return out


def analyze(trace_dir: Path, search_dataset: Path | None, evaluation_dataset: Path | None) -> dict[str, Any]:
    traces_path, metadata_path = trace_dir / 'traces.json', trace_dir / 'metadata.json'
    metadata = json.loads(metadata_path.read_text(encoding='utf-8'))
    traces = json.loads(traces_path.read_text(encoding='utf-8'))
    configs = validate(traces, metadata)
    sn, en = metadata['search_n'], metadata['evaluation_n']
    gold = None
    dataset_overlap = None
    if (search_dataset is None) != (evaluation_dataset is None):
        raise ValueError('provide both datasets or neither')
    if search_dataset is not None:
        labels, search_hashes = gold_labels(search_dataset, metadata['dataset_sha256'], sn, metadata['seed'])
        evaluation_labels, evaluation_hashes = gold_labels(evaluation_dataset, metadata['audit_dataset_sha256'], en, metadata['seed'] + 1)
        gold = dict(enumerate(labels + evaluation_labels))
        shared = set(search_hashes) & set(evaluation_hashes)
        dataset_overlap = {
            'comparison': 'exact Problem strings via SHA-256; no normalization',
            'search_seed': metadata['seed'], 'evaluation_seed': metadata['seed'] + 1,
            'search_unique_problems': len(set(search_hashes)),
            'evaluation_unique_problems': len(set(evaluation_hashes)),
            'search_duplicate_occurrences': sn - len(set(search_hashes)),
            'evaluation_duplicate_occurrences': en - len(set(evaluation_hashes)),
            'shared_unique_problems': len(shared),
            'search_questions_in_overlap': sum(value in shared for value in search_hashes),
            'evaluation_questions_in_overlap': sum(value in shared for value in evaluation_hashes),
        }
    splits = {'search': [r for r in traces if r['question_id'] < sn],
              'evaluation': [r for r in traces if r['question_id'] >= sn]}
    by_config = {name: defaultdict(list) for name in splits}
    for split, rows in splits.items():
        for row in rows:
            by_config[split][row['config_id']].append(row)
    def search_key(config: str) -> tuple[float, float, str]:
        rows = by_config['search'][config]
        return (sum(r['final_correct'] for r in rows) / sn, -math.fsum(r['cost_usd'] for r in rows), config)
    # Match replay's reference rule. Evaluation data does not enter this choice.
    selected = max(configs, key=search_key)
    first_model = {}
    for split, rows in splits.items():
        grouped = defaultdict(list)
        for row in rows:
            grouped[row['config_id'].split('/')[0]].append(row)
        first_model[split] = {model: summarize(values, metadata, gold) for model, values in sorted(grouped.items())}
    return {
        'schema_version': 1, 'run_id': metadata['run_id'],
        'source': {'traces_sha256': file_sha256(traces_path), 'metadata_sha256': file_sha256(metadata_path),
                   'script_sha256': file_sha256(Path(__file__)), 'dataset_sha256': metadata['dataset_sha256'],
                   'evaluation_dataset_sha256': metadata['audit_dataset_sha256']},
        'validation': {'complete_rectangle': True, 'cost_and_input_token_ledgers_match': True,
                       'fixed_verifier_and_retry_stopping_match': True, 'dataset_gold_verified': gold is not None},
        'splits': {name: summarize(rows, metadata, gold) for name, rows in splits.items()},
        'all': summarize(traces, metadata, gold), 'first_solver_model': first_model,
        'selected_dataset_problem_overlap': dataset_overlap,
        'search_selected_exhaustive_reference': {
            'config_id': selected, 'rule': 'max search accuracy; then lower total search cost; then lexicographically largest config id',
            'search_accuracy_tied_rows': sum(search_key(c)[0] == search_key(selected)[0] for c in configs),
            'search': summarize(by_config['search'][selected], metadata, gold),
            'evaluation': summarize(by_config['evaluation'][selected], metadata, gold)},
        'interpretation': [
            'Gold labels may be used for supervised offline search profiling; the workflow verifier must remain answer-key blind.',
            'The exhaustive reference is selected using search rows only, then measured on the independent evaluation split.',
            'First-model summaries pool all complete configurations with that first solver; these cells are not independent questions.',
            'Unique reward vectors describe this finite measured split, not equivalence on future questions.',
            'Terminal confusion compares the last verifier verdict with final parsed correctness; all-attempt confusion additionally requires verified datasets.',
            'Unparseable answers count as incorrect under the recorded exact-choice evaluator; output-cap hits are diagnostic, not automatically truncation proof.',
            'Cost is a local input-token proxy, not an API bill; only reached solver and verifier calls are charged.'],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('trace_dir', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--search-dataset', type=Path)
    parser.add_argument('--evaluation-dataset', type=Path)
    args = parser.parse_args()
    protected = [args.trace_dir / 'traces.json', args.trace_dir / 'metadata.json',
                 args.trace_dir / 'traces.jsonl', args.search_dataset, args.evaluation_dataset]
    if args.output.resolve() in {path.resolve() for path in protected if path is not None}:
        parser.error('output must not overwrite a trace, metadata, or source dataset')
    try:
        report = analyze(args.trace_dir, args.search_dataset, args.evaluation_dataset)
    except (KeyError, TypeError, ValueError) as exc:
        raise SystemExit(f'invalid trace or dataset: {exc}') from exc
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    print(json.dumps({'output': str(args.output), 'run_id': report['run_id'],
                      'cells': report['all']['cells'], 'reference_config': report['search_selected_exhaustive_reference']['config_id']}, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
