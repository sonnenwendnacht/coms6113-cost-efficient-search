#!/usr/bin/env python3
"""Run the local Experiment 1 trace and replay its search policies.

This script needs the optional local Transformers runtime.  It never sends a
MathQA answer key to a model: ``correct`` is read only after the workflow has
finished, by the evaluator in this file.  Generated traces are placed below
``results/runs`` (ignored by Git); a small reviewed summary is emitted by the
``--summary`` path.
"""

from __future__ import annotations

import argparse
import gc
import hashlib
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from retry_search.experiment1 import (  # noqa: E402
    DEFAULT_COEFFICIENTS_USD_PER_TOKEN,
    ArmEliminationPolicy,
    KernelBayesUCBPolicy,
    CostUCBPolicy,
    RandomPolicy,
    SOLVER_MODELS,
    UCBPolicy,
    UniformPolicy,
    VERIFIER_MODEL,
    cell_from_json,
    configurations,
    configuration_id,
    oracle,
    parse_answer,
    parse_verdict,
    primary_cost,
    replay_policy,
    solver_prompt,
    stable_sample,
    split_mathqa,
    verifier_prompt,
)


DEFAULT_MODEL_PATHS = {
    "qwen2.5-1.5b": "/home/gabi/zhengtong/data/models/models--Qwen--Qwen2.5-1.5B-Instruct/snapshots/989aa7980e4cf806f80c7fef2b1adb7bc71aa306",
    "qwen2.5-3b": "/home/gabi/zhengtong/data/models/models--Qwen--Qwen2.5-3B-Instruct",
    "qwen2.5-7b": "/home/gabi/zhengtong/data/models/models--Qwen--Qwen2.5-7B-Instruct/snapshots/a09a35458c702b33eeacc393d103063234e8bc28",
}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


class ModelRunner:
    def __init__(self, name: str, path: str):
        try:
            import torch
            from transformers import AutoModelForCausalLM, AutoTokenizer
        except ImportError as exc:  # pragma: no cover - optional live dependency
            raise RuntimeError("Use a Transformers runtime with torch installed") from exc
        self.name = name
        self.path = path
        self.torch = torch
        self.kind = "mistral" if name == "ministral-3-8b" else "qwen"
        if self.kind == "mistral":
            from transformers import AutoProcessor, Mistral3ForConditionalGeneration

            self.processor = AutoProcessor.from_pretrained(path, local_files_only=True)
            self.model = Mistral3ForConditionalGeneration.from_pretrained(
                path,
                local_files_only=True,
                device_map="auto",
                torch_dtype=torch.bfloat16,
            )
            self.tokenizer = getattr(self.processor, "tokenizer", self.processor)
        else:
            self.tokenizer = AutoTokenizer.from_pretrained(path, local_files_only=True)
            if self.tokenizer.pad_token_id is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            self.model = AutoModelForCausalLM.from_pretrained(
                path,
                local_files_only=True,
                device_map="auto",
                torch_dtype=torch.bfloat16,
            )
        self.model.eval()
        self.device = next(self.model.parameters()).device

    def generate(self, prompt: str, max_new_tokens: int) -> tuple[str, int, int, float]:
        t0 = time.perf_counter()
        if self.kind == "mistral":
            messages = [{"role": "user", "content": [{"type": "text", "text": prompt}]}]
            inputs = self.processor.apply_chat_template(
                messages, tokenize=True, return_dict=True, return_tensors="pt", add_generation_prompt=True
            )
            input_len = int(inputs["input_ids"].shape[-1])
        else:
            messages = [{"role": "user", "content": prompt}]
            inputs = self.tokenizer.apply_chat_template(
                messages, tokenize=True, add_generation_prompt=True, return_tensors="pt"
            )
            if hasattr(inputs, "items"):
                inputs = dict(inputs)
            else:
                inputs = {"input_ids": inputs, "attention_mask": (inputs != self.tokenizer.pad_token_id).long()}
            input_len = int(inputs["input_ids"].shape[-1])
        inputs = {k: v.to(self.device) if hasattr(v, "to") else v for k, v in inputs.items()}
        with self.torch.inference_mode():
            output = self.model.generate(
                **inputs,
                do_sample=False,
                max_new_tokens=max_new_tokens,
                pad_token_id=getattr(self.tokenizer, "pad_token_id", None),
            )
        generated = output[:, input_len:]
        if self.kind == "mistral":
            text = self.processor.batch_decode(generated, skip_special_tokens=True)[0]
        else:
            text = self.tokenizer.decode(generated[0], skip_special_tokens=True)
        return text.strip(), input_len, int(generated.shape[-1]), time.perf_counter() - t0

    def close(self) -> None:
        try:
            del self.model
            del self.tokenizer
            if hasattr(self, "processor"):
                del self.processor
        finally:
            gc.collect()
            if self.torch.cuda.is_available():
                self.torch.cuda.empty_cache()


class ModelPool:
    """Keep the fixed verifier and all three solver tiers resident.

    The three pinned Qwen snapshots fit in the 32 GB card (about 25.6 GB in
    the preflight), which avoids reloading a model between adjacent rows.
    """

    def __init__(self, paths: dict[str, str]):
        self.paths = paths
        self.verifier = ModelRunner(VERIFIER_MODEL, paths[VERIFIER_MODEL])
        self.runners: dict[str, ModelRunner] = {VERIFIER_MODEL: self.verifier}

    def solver_call(self, name: str, prompt: str, max_new_tokens: int):
        if name == VERIFIER_MODEL:
            return self.verifier.generate(prompt, max_new_tokens)
        if name not in self.runners:
            print(f"loading solver {name}", file=sys.stderr, flush=True)
            self.runners[name] = ModelRunner(name, self.paths[name])
        return self.runners[name].generate(prompt, max_new_tokens)

    def close(self):
        for name, runner in list(self.runners.items()):
            runner.close()
        self.runners.clear()


def run_workflow(row: dict[str, Any], config: tuple[str, str, str], pool: ModelPool, question_id: int, coeffs: dict[str, float]) -> dict[str, Any]:
    calls: list[dict[str, Any]] = []
    attempts: list[dict[str, Any]] = []
    previous = None
    feedback = None
    accepted_attempt = None
    final_text = ""
    for attempt, solver_name in enumerate(config, start=1):
        prompt = solver_prompt(row, previous, feedback)
        text, input_tokens, output_tokens, latency_s = pool.solver_call(solver_name, prompt, 160)
        calls.append({
            "role": "solver",
            "model": solver_name,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "coefficient_usd_per_token": coeffs[solver_name],
            "latency_s": latency_s,
        })
        candidate = parse_answer(text)
        vprompt = verifier_prompt(row, text)
        vtext, v_input, v_output, v_latency = pool.solver_call(VERIFIER_MODEL, vprompt, 64)
        passed = parse_verdict(vtext)
        calls.append({
            "role": "verifier",
            "model": VERIFIER_MODEL,
            "input_tokens": v_input,
            "output_tokens": v_output,
            "coefficient_usd_per_token": coeffs[VERIFIER_MODEL],
            "latency_s": v_latency,
        })
        attempts.append({
            "attempt": attempt,
            "solver_model": solver_name,
            "answer": candidate,
            "verifier_pass": passed,
            "solver_output_tokens": output_tokens,
            "verifier_output_tokens": v_output,
        })
        final_text, previous, feedback = text, text, vtext
        if passed:
            accepted_attempt = attempt
            break
    final_answer = parse_answer(final_text)
    return {
        "question_id": question_id,
        "config_id": configuration_id(config),
        "attempts": attempts,
        "accepted_attempt": accepted_attempt,
        "final_answer": final_answer,
        "final_correct": int(final_answer == str(row["correct"]).lower()),
        "calls": calls,
        "input_tokens": sum(c["input_tokens"] for c in calls),
        "cost_usd": primary_cost(calls),
    }


def metadata(paths: dict[str, str], dataset_path: Path, coeffs: dict[str, float]) -> dict[str, Any]:
    out = {"dataset": {"path": str(dataset_path), "sha256": sha256_file(dataset_path)}}
    out["models"] = {}
    for name, path_str in paths.items():
        p = Path(path_str)
        config = p / "config.json"
        out["models"][name] = {
            "path": str(p),
            "config_sha256": sha256_file(config) if config.exists() else None,
        }
    out["coefficients_usd_per_input_token"] = coeffs
    out["cost_definition"] = "sum(coefficient_usd_per_input_token[model] * input_tokens) for every solver and verifier call; output/cache/latency are excluded"
    return out


def replay_and_summarize(trace_rows: list[dict[str, Any]], search_n: int, audit_n: int, repeats: int = 8) -> dict[str, Any]:
    cells = {(r["config_id"], int(r["question_id"])): cell_from_json(r) for r in trace_rows}
    arms = sorted({r["config_id"] for r in trace_rows})
    search_ids = list(range(search_n))
    audit_ids = list(range(search_n, search_n + audit_n))
    search_cells = {(a, q): cells[(a, q)] for a in arms for q in search_ids}
    audit_cells = {(a, q): cells[(a, q)] for a in arms for q in audit_ids}
    exhaustive_cost = sum(c.cost_usd for c in search_cells.values())
    budgets = [exhaustive_cost * p for p in (0.25, 0.50, 0.75, 1.0)]
    policy_classes = [RandomPolicy, UniformPolicy, UCBPolicy, CostUCBPolicy, ArmEliminationPolicy, KernelBayesUCBPolicy]
    rows = []
    for cls in policy_classes:
        for budget in budgets:
            for seed in range(repeats):
                rows.append(replay_policy(search_cells, search_ids, audit_cells, cls(), budget, 6113 + seed))
    oracle_audit = oracle(audit_cells, audit_ids) if audit_ids else None
    grouped: dict[tuple[str, float], list[dict[str, Any]]] = {}
    for row in rows:
        grouped.setdefault((row["policy"], row["budget_usd"]), []).append(row)
    aggregates = []
    for (policy, budget), values in grouped.items():
        aggregates.append({
            "policy": policy,
            "budget_usd": budget,
            "mean_search_spend_usd": sum(x["search_spend_usd"] for x in values) / len(values),
            "mean_audit_accuracy": sum((x["audit_accuracy"] or 0.0) for x in values) / len(values),
            "mean_selected_search_accuracy": sum((x["selected_search_accuracy"] or 0.0) for x in values) / len(values),
            "repeats": len(values),
        })
    return {
        "search_n": search_n,
        "audit_n": audit_n,
        "exhaustive_search_cost_usd": exhaustive_cost,
        "budgets": budgets,
        "oracle_audit": oracle_audit,
        "aggregates": sorted(aggregates, key=lambda x: (x["budget_usd"], x["policy"])),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", default=str(ROOT / "data/raw/mathqa/train.json"), help="search split source")
    ap.add_argument("--audit-dataset", default=str(ROOT / "data/raw/mathqa/dev.json"), help="independent audit split source")
    ap.add_argument("--search-n", type=int, default=20)
    ap.add_argument("--audit-n", type=int, default=10)
    ap.add_argument("--seed", type=int, default=6113)
    ap.add_argument("--run-id", default=None)
    ap.add_argument("--model-path", action="append", metavar="NAME=PATH")
    ap.add_argument("--smoke", action="store_true", help="one question, for runtime checks")
    ap.add_argument("--smoke-all", action="store_true", help="one question and all 27 rows, for model checks")
    args = ap.parse_args()
    if args.smoke or args.smoke_all:
        args.search_n, args.audit_n = 1, 0
    paths = dict(DEFAULT_MODEL_PATHS)
    for item in args.model_path or []:
        name, value = item.split("=", 1)
        paths[name] = value
    for name in SOLVER_MODELS:
        if not Path(paths[name]).exists():
            raise SystemExit(f"missing local model snapshot for {name}: {paths[name]}")
    dataset_path = Path(args.dataset)
    audit_dataset_path = Path(args.audit_dataset)
    search_rows = stable_sample(json.loads(dataset_path.read_text(encoding="utf-8")), args.search_n, args.seed)
    audit_rows = stable_sample(json.loads(audit_dataset_path.read_text(encoding="utf-8")), args.audit_n, args.seed + 1)
    rows = [(i, row) for i, row in enumerate(search_rows)] + [(args.search_n + i, row) for i, row in enumerate(audit_rows)]
    configs = configurations(SOLVER_MODELS)
    if args.smoke:
        configs = configs[:1]
    run_id = args.run_id or time.strftime("exp1-local-%Y%m%d-%H%M%S")
    run_dir = ROOT / "results/runs" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    coeffs = dict(DEFAULT_COEFFICIENTS_USD_PER_TOKEN)
    run_metadata = metadata(paths, dataset_path, coeffs)
    run_metadata["audit_dataset"] = {"path": str(audit_dataset_path), "sha256": sha256_file(audit_dataset_path)}
    run_metadata["split"] = {
        "seed": args.seed,
        "search_n": args.search_n,
        "audit_n": args.audit_n,
        "search_question_sha256": [hashlib.sha256(row["Problem"].encode()).hexdigest() for row in search_rows],
        "audit_question_sha256": [hashlib.sha256(row["Problem"].encode()).hexdigest() for row in audit_rows],
    }
    (run_dir / "metadata.json").write_text(json.dumps(run_metadata, indent=2), encoding="utf-8")
    print(f"run={run_id} questions={len(rows)} rows={len(configs)}", file=sys.stderr, flush=True)
    pool = ModelPool(paths)
    traces: list[dict[str, Any]] = []
    try:
        total = len(rows) * len(configs)
        done = 0
        for qid, row in rows:
            for config in configs:
                traces.append(run_workflow(row, config, pool, qid, coeffs))
                done += 1
                if done == 1 or done % 5 == 0 or done == total:
                    print(f"completed {done}/{total}", file=sys.stderr, flush=True)
    finally:
        pool.close()
    (run_dir / "traces.json").write_text(json.dumps(traces, indent=2), encoding="utf-8")
    # The full replay needs all 27 rows.  A smoke run is only a model/runtime check.
    replay = None
    if len(configs) == 27:
        replay = replay_and_summarize(traces, args.search_n, args.audit_n)
        (run_dir / "replay.json").write_text(json.dumps(replay, indent=2), encoding="utf-8")
    status = {
        "run_id": run_id,
        "status": "completed" if replay is not None else "smoke_completed",
        "search_n": args.search_n,
        "audit_n": args.audit_n,
        "rows": len(configs),
        "trace_count": len(traces),
        "run_dir": str(run_dir),
        "replay": replay,
    }
    (run_dir / "status.json").write_text(json.dumps(status, indent=2), encoding="utf-8")
    print(json.dumps(status, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
