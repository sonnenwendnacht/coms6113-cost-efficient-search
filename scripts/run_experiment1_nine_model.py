#!/usr/bin/env python3
"""Generate the 9^3 retry trace and replay selector/parameter pairs.

This runner deliberately requires nine distinct solver checkpoints/endpoints.
It never aliases a smaller local model pool to nine names.  Generation is
optional and expensive; the selector sweep and Table-7 report operate on the
resulting trace without touching the held-out evaluation cells.
"""

from __future__ import annotations

import argparse
import gc
import hashlib
import json
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from retry_search.experiment1 import (  # noqa: E402
    configuration_id,
    parse_answer,
    parse_verdict,
    primary_cost,
    question_prompt,
    solver_prompt,
    verifier_prompt,
)


CONFIG_PATH = ROOT / "configs/experiment1-nine-model.json"
DEFAULT_VERIFIER = "qwen2.5-1.5b"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def model_ids() -> list[str]:
    data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    return [item["id"] for item in data["model_pool"]]


def ordered_rows(ids: list[str]) -> list[tuple[str, str, str]]:
    return [(a, b, c) for a in ids for b in ids for c in ids]


class LocalModel:
    """Small local adapter for Qwen-style and Ministral-style checkpoints."""

    def __init__(self, name: str, path: str):
        try:
            import torch
            from transformers import AutoModelForCausalLM, AutoTokenizer
        except ImportError as exc:  # pragma: no cover
            raise RuntimeError("Generation requires torch and transformers") from exc
        self.name = name
        self.path = path
        self.torch = torch
        self.is_mistral = "mistral" in (name + path).lower()
        if self.is_mistral:
            from transformers import AutoProcessor, Mistral3ForConditionalGeneration

            self.processor = AutoProcessor.from_pretrained(path, local_files_only=True)
            self.model = Mistral3ForConditionalGeneration.from_pretrained(
                path, local_files_only=True, device_map="auto", torch_dtype=torch.bfloat16
            )
            self.tokenizer = getattr(self.processor, "tokenizer", self.processor)
        else:
            self.tokenizer = AutoTokenizer.from_pretrained(path, local_files_only=True)
            if self.tokenizer.pad_token_id is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            self.model = AutoModelForCausalLM.from_pretrained(
                path, local_files_only=True, device_map="auto", torch_dtype=torch.bfloat16
            )
        self.model.eval()
        self.device = next(self.model.parameters()).device

    def generate(self, prompt: str, max_new_tokens: int) -> tuple[str, int, int, float]:
        started = time.perf_counter()
        if self.is_mistral:
            messages = [{"role": "user", "content": [{"type": "text", "text": prompt}]}]
            inputs = self.processor.apply_chat_template(
                messages, tokenize=True, return_dict=True, return_tensors="pt", add_generation_prompt=True
            )
        else:
            messages = [{"role": "user", "content": prompt}]
            inputs = self.tokenizer.apply_chat_template(
                messages, tokenize=True, add_generation_prompt=True, return_tensors="pt"
            )
            if not hasattr(inputs, "items"):
                inputs = {"input_ids": inputs, "attention_mask": (inputs != self.tokenizer.pad_token_id).long()}
            else:
                inputs = dict(inputs)
        input_len = int(inputs["input_ids"].shape[-1])
        inputs = {key: value.to(self.device) if hasattr(value, "to") else value for key, value in inputs.items()}
        with self.torch.inference_mode():
            output = self.model.generate(
                **inputs,
                do_sample=False,
                max_new_tokens=max_new_tokens,
                pad_token_id=getattr(self.tokenizer, "pad_token_id", None),
            )
        generated = output[:, input_len:]
        if self.is_mistral:
            text = self.processor.batch_decode(generated, skip_special_tokens=True)[0]
        else:
            text = self.tokenizer.decode(generated[0], skip_special_tokens=True)
        return text.strip(), input_len, int(generated.shape[-1]), time.perf_counter() - started

    def close(self) -> None:
        del self.model
        del self.tokenizer
        if hasattr(self, "processor"):
            del self.processor
        gc.collect()
        if self.torch.cuda.is_available():
            self.torch.cuda.empty_cache()


class LocalPool:
    def __init__(self, paths: dict[str, str], verifier_name: str, verifier_path: str):
        self.paths = paths
        self.runners: dict[str, LocalModel] = {}
        self.verifier_name = verifier_name
        self.verifier_path = verifier_path

    def call(self, name: str, prompt: str, max_new_tokens: int):
        if name not in self.runners:
            path = self.verifier_path if name == self.verifier_name else self.paths[name]
            print(f"loading {name}", file=sys.stderr, flush=True)
            self.runners[name] = LocalModel(name, path)
        return self.runners[name].generate(prompt, max_new_tokens)

    def close(self) -> None:
        for runner in self.runners.values():
            runner.close()
        self.runners.clear()


def run_workflow(
    row: dict[str, Any], config: tuple[str, str, str], pool: LocalPool,
    question_id: int, coefficients: dict[str, float], verifier_name: str,
) -> dict[str, Any]:
    calls: list[dict[str, Any]] = []
    attempts: list[dict[str, Any]] = []
    previous: str | None = None
    feedback: str | None = None
    accepted_attempt = None
    final_text = ""
    for attempt, solver_name in enumerate(config, start=1):
        prompt = solver_prompt(row, previous, feedback)
        text, input_tokens, output_tokens, latency = pool.call(solver_name, prompt, 256)
        calls.append({"role": "solver", "model": solver_name, "input_tokens": input_tokens,
                      "output_tokens": output_tokens, "coefficient_usd_per_token": coefficients[solver_name],
                      "latency_s": latency})
        candidate = parse_answer(text)
        vprompt = verifier_prompt(row, text)
        vtext, v_input, v_output, v_latency = pool.call(verifier_name, vprompt, 64)
        passed = parse_verdict(vtext)
        calls.append({"role": "verifier", "model": verifier_name, "input_tokens": v_input,
                      "output_tokens": v_output, "coefficient_usd_per_token": coefficients[verifier_name],
                      "latency_s": v_latency})
        attempts.append({"attempt": attempt, "solver_model": solver_name, "answer": candidate,
                         "verifier_pass": passed, "solver_output_tokens": output_tokens,
                         "verifier_output_tokens": v_output})
        final_text, previous, feedback = text, text, vtext
        if passed:
            accepted_attempt = attempt
            break
    final_answer = parse_answer(final_text)
    return {"question_id": question_id, "config_id": configuration_id(config), "attempts": attempts,
            "accepted_attempt": accepted_attempt, "final_answer": final_answer,
            "final_correct": int(final_answer == str(row["correct"]).lower()), "calls": calls,
            "input_tokens": sum(c["input_tokens"] for c in calls), "cost_usd": primary_cost(calls)}


def stable_sample(rows: list[dict[str, Any]], n: int, seed: int) -> list[dict[str, Any]]:
    keyed = [(hashlib.sha256(f"{seed}:{i}:{row['Problem']}".encode()).hexdigest(), row)
             for i, row in enumerate(rows)]
    keyed.sort(key=lambda item: item[0])
    return [row for _, row in keyed[:n]]


def parse_key_values(items: list[str], ids: list[str], label: str) -> dict[str, str]:
    values = {}
    for item in items:
        name, sep, value = item.partition("=")
        if not sep or name not in ids:
            raise SystemExit(f"{label} must use NAME=PATH with one of {ids}: {item}")
        values[name] = value
    missing = [name for name in ids if name not in values]
    if missing:
        raise SystemExit(f"nine distinct {label} values are required; missing {missing}")
    return values


def generate(args: argparse.Namespace) -> int:
    ids = model_ids()
    solver_paths = parse_key_values(args.model_path, ids, "--model-path")
    all_paths = dict(solver_paths)
    all_paths[args.verifier_model] = args.verifier_path
    coefficients = {name: float(value) for name, value in (item.split("=", 1) for item in args.coefficient)}
    missing_coefficients = [name for name in ids + [args.verifier_model] if name not in coefficients]
    if missing_coefficients:
        raise SystemExit(f"provide --coefficient NAME=USD_PER_INPUT_TOKEN for {missing_coefficients}")
    dataset = Path(args.dataset)
    audit_dataset = Path(args.audit_dataset)
    search = stable_sample(json.loads(dataset.read_text(encoding="utf-8")), 200, args.seed)
    evaluation = stable_sample(json.loads(audit_dataset.read_text(encoding="utf-8")), 200, args.seed + 1)
    questions = [(i, row) for i, row in enumerate(search)] + [(200 + i, row) for i, row in enumerate(evaluation)]
    configs = ordered_rows(ids)
    run_id = args.run_id or time.strftime("exp1-nine-model-%Y%m%d-%H%M%S")
    run_dir = ROOT / "results/runs" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    metadata = {"experiment": "exp1_retry_aware_nine_model_rows", "run_id": run_id,
                "config_path": str(CONFIG_PATH), "config_sha256": sha256_file(CONFIG_PATH),
                "dataset_sha256": sha256_file(dataset), "audit_dataset_sha256": sha256_file(audit_dataset),
                "search_n": 200, "evaluation_n": 200, "rows": len(configs),
                "solver_models": ids, "verifier_model": args.verifier_model,
                "model_paths": solver_paths, "coefficients_usd_per_input_token": coefficients,
                "seed": args.seed, "output_tokens_charged": False, "cache_discount": False,
                "answer_key_access": "evaluator only after workflow"}
    (run_dir / "metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    pool = LocalPool(solver_paths, args.verifier_model, args.verifier_path)
    traces: list[dict[str, Any]] = []
    try:
        total = len(questions) * len(configs)
        for done, (qid, row) in enumerate((item for item in questions for _ in configs), start=1):
            # The inner configuration is recovered by a deterministic position.
            config = configs[(done - 1) % len(configs)]
            traces.append(run_workflow(row, config, pool, qid, coefficients, args.verifier_model))
            if done == 1 or done % 100 == 0 or done == total:
                print(f"completed {done}/{total}", file=sys.stderr, flush=True)
    finally:
        pool.close()
    (run_dir / "traces.json").write_text(json.dumps(traces), encoding="utf-8")
    print(json.dumps({"run_id": run_id, "trace_count": len(traces), "run_dir": str(run_dir)}))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--generate", action="store_true", help="run all 729 rows on both 200-question splits")
    ap.add_argument("--dataset", default=str(ROOT / "data/raw/mathqa/train.json"))
    ap.add_argument("--audit-dataset", default=str(ROOT / "data/raw/mathqa/dev.json"))
    ap.add_argument("--run-id")
    ap.add_argument("--seed", type=int, default=6113)
    ap.add_argument("--model-path", action="append", default=[], metavar="NAME=PATH")
    ap.add_argument("--verifier-model", default=DEFAULT_VERIFIER)
    ap.add_argument("--verifier-path", required=False, default="")
    ap.add_argument("--coefficient", action="append", default=[], metavar="NAME=USD_PER_INPUT_TOKEN")
    args = ap.parse_args()
    if not args.generate:
        ap.error("generation is explicit; use --generate after supplying nine model paths and coefficients")
    if not args.verifier_path:
        ap.error("--verifier-path is required")
    return generate(args)


if __name__ == "__main__":
    raise SystemExit(main())
