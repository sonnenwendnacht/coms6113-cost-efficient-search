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
import os
import sys
import time
from collections import OrderedDict
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


def model_registry() -> tuple[dict[str, str], dict[str, float]]:
    data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    model_root_raw = os.environ.get("COMS6113_MODEL_ROOT")
    model_root = Path(model_root_raw).expanduser() if model_root_raw else None
    paths = {}
    for item in data["model_pool"]:
        raw_path = item["path"]
        if raw_path.startswith("${COMS6113_MODEL_ROOT}/"):
            if model_root is None:
                raise SystemExit(
                    "set COMS6113_MODEL_ROOT to the Hugging Face hub directory "
                    "containing the pinned model snapshots"
                )
            raw_path = str(model_root / raw_path.split("/", 1)[1])
        paths[item["id"]] = os.path.expandvars(raw_path)
    coefficients = {
        item["id"]: float(item["coefficient_usd_per_input_token"])
        for item in data["model_pool"]
    }
    return paths, coefficients


def ordered_rows(ids: list[str]) -> list[tuple[str, str, str]]:
    return [(a, b, c) for a in ids for b in ids for c in ids]


def expanded_solver_prompt(
    row: dict[str, Any], previous: str | None = None, feedback: str | None = None
) -> str:
    """Use a short, uniform output contract for the expanded local pool.

    The pilot's explanatory prompt causes small checkpoints to spend their
    whole output budget on prose.  Keeping the contract short makes a missing
    ``FINAL`` marker a measurable parse failure rather than an artifact of a
    long prompt.  Retry context is still included because it is part of the
    deployment input and therefore part of the cost ledger.
    """
    prompt = (
        "Solve this multiple-choice math problem. Work out the answer silently. "
        "Reply with exactly one line in the form FINAL: a, FINAL: b, FINAL: c, "
        "FINAL: d, or FINAL: e. Do not explain.\n\n"
        f"Problem: {row['Problem']}\nOptions: {row['options']}"
    )
    if previous:
        prompt += (
            "\n\nRetry the problem. The previous attempt was:\n"
            + previous[-1200:]
            + "\n\nVerifier feedback:\n"
            + (feedback or "RETRY")[-400:]
            + "\nReturn exactly one FINAL line."
        )
    return prompt


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
        self.is_qwen3 = "qwen3" in (name + path).lower()
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
            template_kwargs = {
                "tokenize": True,
                "add_generation_prompt": True,
                "return_tensors": "pt",
            }
            # Qwen3 otherwise spends its short deterministic generation budget
            # in a visible <think> block.  Older tokenizer templates do not
            # accept this keyword, so retry without it when unsupported.
            if self.is_qwen3:
                template_kwargs["enable_thinking"] = False
            try:
                inputs = self.tokenizer.apply_chat_template(messages, **template_kwargs)
            except TypeError:
                template_kwargs.pop("enable_thinking", None)
                inputs = self.tokenizer.apply_chat_template(messages, **template_kwargs)
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
    def __init__(self, paths: dict[str, str], verifier_name: str, verifier_path: str,
                 max_resident: int = 3):
        self.paths = paths
        self.runners: OrderedDict[str, LocalModel] = OrderedDict()
        self.verifier_name = verifier_name
        self.verifier_path = verifier_path
        self.max_resident = max(2, int(max_resident))

    def call(self, name: str, prompt: str, max_new_tokens: int):
        if name in self.runners:
            self.runners.move_to_end(name)
        else:
            if len(self.runners) >= self.max_resident:
                old_name, old_runner = self.runners.popitem(last=False)
                print(f"unloading {old_name}", file=sys.stderr, flush=True)
                old_runner.close()
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
    max_new_tokens: int,
) -> dict[str, Any]:
    calls: list[dict[str, Any]] = []
    attempts: list[dict[str, Any]] = []
    previous: str | None = None
    feedback: str | None = None
    accepted_attempt = None
    final_text = ""
    for attempt, solver_name in enumerate(config, start=1):
        prompt = expanded_solver_prompt(row, previous, feedback)
        text, input_tokens, output_tokens, latency = pool.call(solver_name, prompt, max_new_tokens)
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


def _write_status(path: Path, *, run_id: str, status: str, completed: int, total: int) -> None:
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps({
        "run_id": run_id,
        "status": status,
        "completed": completed,
        "total": total,
        "fraction_complete": completed / total if total else 1.0,
        "updated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }, indent=2), encoding="utf-8")
    temporary.replace(path)


def _load_checkpoint(path: Path, questions: list[tuple[int, dict[str, Any]]],
                     configs: list[tuple[str, str, str]]) -> list[dict[str, Any]]:
    """Check the exact generation order and recover only a torn final write.

    A complete but invalid record is an error. A final line without a newline
    is uncommitted, even if its JSON happens to parse, and will be regenerated.
    """
    traces = []
    if not path.exists():
        return traces
    last_complete = 0
    with path.open('rb') as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.endswith(b'\n'):
                break
            try:
                trace = json.loads(line)
            except (json.JSONDecodeError, UnicodeDecodeError) as exc:
                raise SystemExit(f'invalid checkpoint line {line_number} in {path}') from exc
            index = len(traces)
            if index >= len(questions) * len(configs):
                raise SystemExit('checkpoint contains more records than the configured run')
            qid = questions[index // len(configs)][0]
            cid = configuration_id(configs[index % len(configs)])
            if not isinstance(trace, dict) or trace.get('question_id') != qid or trace.get('config_id') != cid:
                raise SystemExit(f'checkpoint order/identity mismatch at line {line_number}')
            traces.append(trace)
            last_complete += len(line)
    if path.stat().st_size != last_complete:
        with path.open('r+b') as handle:
            handle.truncate(last_complete)
        print('discarded uncommitted final checkpoint line; its workflow will be rerun',
              file=sys.stderr, flush=True)
    return traces


def generate(args: argparse.Namespace) -> int:
    ids = model_ids()
    configured_paths, configured_coefficients = model_registry()
    solver_paths = configured_paths
    if args.model_path:
        solver_paths.update(parse_key_values(args.model_path, ids, "--model-path"))
    verifier_path = args.verifier_path or solver_paths.get(args.verifier_model, "")
    coefficients = configured_coefficients
    if args.coefficient:
        coefficients.update({name: float(value) for name, value in (item.split("=", 1) for item in args.coefficient)})
    missing_coefficients = [name for name in ids + [args.verifier_model] if name not in coefficients]
    if missing_coefficients:
        raise SystemExit(f"provide --coefficient NAME=USD_PER_INPUT_TOKEN for {missing_coefficients}")
    dataset = Path(args.dataset)
    audit_dataset = Path(args.audit_dataset)
    search = stable_sample(json.loads(dataset.read_text(encoding="utf-8")), 200, args.seed)
    evaluation = stable_sample(json.loads(audit_dataset.read_text(encoding="utf-8")), 200, args.seed + 1)
    if len(search) != 200 or len(evaluation) != 200:
        raise SystemExit('both source datasets must contain at least 200 questions')
    questions = [(i, row) for i, row in enumerate(search)] + [(200 + i, row) for i, row in enumerate(evaluation)]
    configs = ordered_rows(ids)
    run_id = args.run_id or time.strftime("exp1-nine-model-%Y%m%d-%H%M%S")
    if args.resume and not args.run_id:
        raise SystemExit("--resume requires --run-id so the existing checkpoint is unambiguous")
    if args.checkpoint_every <= 0:
        raise SystemExit("--checkpoint-every must be a positive integer")
    run_dir = ROOT / "results/runs" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    metadata = {"experiment": "exp1_retry_aware_nine_model_rows", "run_id": run_id,
                "config_path": str(CONFIG_PATH), "config_sha256": sha256_file(CONFIG_PATH),
                "dataset_sha256": sha256_file(dataset), "audit_dataset_sha256": sha256_file(audit_dataset),
                "search_n": 200, "evaluation_n": 200, "rows": len(configs),
                "solver_models": ids, "verifier_model": args.verifier_model,
                "verifier_path": verifier_path,
                "runner_sha256": sha256_file(Path(__file__)),
                "model_paths": solver_paths, "coefficients_usd_per_input_token": coefficients,
                "seed": args.seed, "output_tokens_charged": False, "cache_discount": False,
                "answer_key_access": "evaluator only after workflow",
                "solver_prompt": "concise_final_line_v1",
                "solver_max_new_tokens": args.max_new_tokens,
                "verifier_max_new_tokens": 64,
                "max_resident_models": args.max_resident}
    metadata_path = run_dir / "metadata.json"
    if args.resume:
        if not metadata_path.exists():
            raise SystemExit('--resume requires an existing metadata.json')
        existing = json.loads(metadata_path.read_text(encoding="utf-8"))
        changed = [key for key, value in metadata.items()
                   if key != 'max_resident_models' and existing.get(key) != value]
        if changed:
            raise SystemExit(f'resume settings differ from the recorded run: {changed}')
    else:
        if any((run_dir / name).exists() for name in ('metadata.json', 'traces.jsonl', 'traces.json')):
            raise SystemExit('run already exists; use --resume or choose a new --run-id')
        metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    missing_paths = [name for name in ids if not Path(solver_paths[name]).exists()]
    if not verifier_path or not Path(verifier_path).exists():
        missing_paths.append(args.verifier_model + " (verifier)")
    if missing_paths:
        raise SystemExit(f"missing local model paths: {missing_paths}")
    total = len(questions) * len(configs)
    jsonl_path = run_dir / "traces.jsonl"
    traces = _load_checkpoint(jsonl_path, questions, configs) if args.resume else []
    start = len(traces)
    persisted = start
    _write_status(run_dir / "status.json", run_id=run_id, status="running", completed=start, total=total)
    pool = LocalPool(solver_paths, args.verifier_model, verifier_path, args.max_resident)
    try:
        with jsonl_path.open("a", encoding="utf-8") as checkpoint:
            for index in range(start, total):
                qid, row = questions[index // len(configs)]
                done = index + 1
                # The inner configuration is recovered by a deterministic position.
                config = configs[index % len(configs)]
                trace = run_workflow(row, config, pool, qid, coefficients, args.verifier_model,
                                     args.max_new_tokens)
                traces.append(trace)
                checkpoint.write(json.dumps(trace, separators=(",", ":")) + "\n")
                checkpoint.flush()
                persisted = done
                if done == 1 or done % args.checkpoint_every == 0 or done == total:
                    os.fsync(checkpoint.fileno())
                    _write_status(run_dir / "status.json", run_id=run_id, status="running",
                                  completed=done, total=total)
                    print(f"completed {done}/{total}", file=sys.stderr, flush=True)
    except BaseException:
        _write_status(run_dir / 'status.json', run_id=run_id, status='interrupted',
                      completed=persisted, total=total)
        raise
    finally:
        pool.close()
    (run_dir / "traces.json").write_text(json.dumps(traces), encoding="utf-8")
    _write_status(run_dir / "status.json", run_id=run_id, status="completed", completed=total, total=total)
    print(json.dumps({"run_id": run_id, "trace_count": len(traces), "run_dir": str(run_dir)}))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--generate", action="store_true", help="run all 729 rows on both 200-question splits")
    ap.add_argument("--dataset", default=str(ROOT / "data/raw/mathqa/train.json"))
    ap.add_argument("--audit-dataset", default=str(ROOT / "data/raw/mathqa/dev.json"))
    ap.add_argument("--run-id")
    ap.add_argument("--seed", type=int, default=6113)
    ap.add_argument("--model-path", action="append", default=[], metavar="NAME=PATH",
                    help="optional override; otherwise use pinned paths in the config")
    ap.add_argument("--verifier-model", default=DEFAULT_VERIFIER)
    ap.add_argument("--verifier-path", required=False, default="",
                    help="optional override; otherwise use the verifier's pinned solver path")
    ap.add_argument("--coefficient", action="append", default=[], metavar="NAME=USD_PER_INPUT_TOKEN")
    ap.add_argument("--max-resident", type=int, default=3,
                    help="maximum local models kept in memory at once (default: 3)")
    ap.add_argument("--max-new-tokens", type=int, default=256,
                    help="solver generation cap (default: 256; output is not charged)")
    ap.add_argument("--checkpoint-every", type=int, default=1000,
                    help="sync to disk and update status every N workflows; JSONL is flushed per workflow")
    ap.add_argument("--resume", action="store_true",
                    help="resume traces.jsonl for the supplied --run-id")
    args = ap.parse_args()
    if not args.generate:
        ap.error("generation is explicit; use --generate after supplying nine model paths and coefficients")
    return generate(args)


if __name__ == "__main__":
    raise SystemExit(main())
