#!/usr/bin/env python3
import argparse
import json
import os
import time
from pathlib import Path

from huggingface_hub import hf_hub_download
from llama_cpp import Llama


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--model-key", required=True)
    p.add_argument("--output-dir", required=True)
    args = p.parse_args()

    models = json.loads(Path("benchmark/large_models.json").read_text())
    model_meta = next(m for m in models["active"] if m["key"] == args.model_key)
    fixtures = json.loads(Path("benchmark/fixtures/email_cases.json").read_text())
    system_prompt = Path("benchmark/prompts/system.txt").read_text()
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)

    started = time.perf_counter()
    model_path = hf_hub_download(
        repo_id=model_meta["repo"],
        filename=model_meta["file"],
        local_dir="/tmp/model",
    )
    download_seconds = time.perf_counter() - started

    load_started = time.perf_counter()
    llm = Llama(
        model_path=model_path,
        n_ctx=4096,
        n_threads=max(1, min(4, os.cpu_count() or 1)),
        verbose=False,
    )
    load_seconds = time.perf_counter() - load_started

    timings = []
    for case in fixtures:
        user_text = (
            "Analyze this synthetic email/thread.\n\n"
            f"From: {case['from']}\n"
            f"Subject: {case['subject']}\n\n"
            f"Thread:\n{case['thread']}"
        )
        if model_meta["family"] == "qwen3":
            user_text += "\n\n/no_think"

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_text},
        ]
        infer_started = time.perf_counter()
        response = llm.create_chat_completion(
            messages=messages,
            temperature=0,
            max_tokens=220,
            seed=1,
        )
        elapsed_ms = round((time.perf_counter() - infer_started) * 1000)
        text = response["choices"][0]["message"]["content"].strip()

        (out / f"{case['id']}.txt").write_text(text)
        (out / f"{case['id']}.response.json").write_text(
            json.dumps({"model": args.model_key, "text": text}, indent=2)
        )
        timings.append((case["id"], elapsed_ms))

    (out / "timings-ms.csv").write_text(
        "".join(f"{case_id},{elapsed_ms}\n" for case_id, elapsed_ms in timings)
    )
    (out / "runtime.json").write_text(
        json.dumps(
            {
                "model_key": args.model_key,
                "repo": model_meta["repo"],
                "file": model_meta["file"],
                "family": model_meta["family"],
                "params": model_meta["params"],
                "quant": model_meta["quant"],
                "download_seconds": round(download_seconds, 3),
                "model_load_seconds": round(load_seconds, 3),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
