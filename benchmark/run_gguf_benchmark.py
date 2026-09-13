#!/usr/bin/env python3
import argparse
import json
import os
import time
from pathlib import Path

from llama_cpp import Llama


def model_value(entry, primary, legacy):
    value = entry.get(primary, entry.get(legacy))
    if value is None:
        raise KeyError(f"Model entry is missing '{primary}'")
    return value


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--model-key", required=True)
    p.add_argument("--output-dir", required=True)
    p.add_argument("--max-cases", type=int, default=0, help="0 means all fixtures")
    a = p.parse_args()

    models = json.loads(Path("benchmark/large_models.json").read_text())
    entry = next((m for m in models["active"] if m["key"] == a.model_key), None)
    if not entry:
        raise SystemExit(f"Unknown model key: {a.model_key}")

    repo_id = model_value(entry, "repo", "repo_id")
    filename = model_value(entry, "file", "filename")
    parameters = model_value(entry, "params", "parameters")
    quantization = model_value(entry, "quant", "quantization")

    out = Path(a.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    fixtures = json.loads(Path("benchmark/fixtures/email_cases.json").read_text())
    if a.max_cases > 0:
        fixtures = fixtures[: a.max_cases]
    system_prompt = Path("benchmark/prompts/system.txt").read_text()

    load_started = time.perf_counter()
    llm = Llama.from_pretrained(
        repo_id=repo_id,
        filename=filename,
        n_ctx=2048,
        n_threads=max(1, min(4, os.cpu_count() or 1)),
        n_batch=128,
        seed=42,
        verbose=False,
    )
    load_seconds = time.perf_counter() - load_started

    timings = []
    for case in fixtures:
        user_text = (
            "/no_think\n"
            "Analyze this synthetic email/thread. Return only the required JSON object.\n\n"
            f"From: {case['from']}\n"
            f"Subject: {case['subject']}\n\n"
            f"Thread:\n{case['thread']}"
        )
        started = time.perf_counter()
        result = llm.create_chat_completion(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_text},
            ],
            temperature=0.7,
            top_p=0.8,
            top_k=20,
            min_p=0.0,
            seed=42,
            max_tokens=500,
        )
        elapsed_ms = round((time.perf_counter() - started) * 1000)
        text = (result["choices"][0]["message"]["content"] or "").strip()
        (out / f"{case['id']}.txt").write_text(text)
        (out / f"{case['id']}.response.json").write_text(
            json.dumps({"model": entry, "text": text}, indent=2)
        )
        timings.append((case["id"], elapsed_ms))

    (out / "timings-ms.csv").write_text(
        "".join(f"{case_id},{ms}\n" for case_id, ms in timings)
    )
    (out / "runtime.json").write_text(
        json.dumps(
            {
                "model_key": a.model_key,
                "repo_id": repo_id,
                "filename": filename,
                "parameters": parameters,
                "quantization": quantization,
                "cases_run": len(fixtures),
                "model_load_seconds": round(load_seconds, 3),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
