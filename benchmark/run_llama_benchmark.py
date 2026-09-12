#!/usr/bin/env python3
import argparse
import json
import time
from pathlib import Path

import requests


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--model-key", required=True)
    p.add_argument("--output-dir", required=True)
    p.add_argument("--base-url", default="http://127.0.0.1:8080")
    args = p.parse_args()

    models = json.loads(Path("benchmark/large_models.json").read_text())
    model = next(m for m in models["active"] if m["key"] == args.model_key)
    fixtures = json.loads(Path("benchmark/fixtures/email_cases.json").read_text())
    system_prompt = Path("benchmark/prompts/system.txt").read_text()
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)

    timings = []
    for case in fixtures:
        user_text = (
            "Analyze this synthetic email/thread.\n\n"
            f"From: {case['from']}\n"
            f"Subject: {case['subject']}\n\n"
            f"Thread:\n{case['thread']}"
        )
        payload = {
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_text},
            ],
            "temperature": 0,
            "max_tokens": 220,
            "seed": 1,
        }
        if model["family"] == "qwen3":
            payload["chat_template_kwargs"] = {"enable_thinking": False}

        started = time.perf_counter()
        r = requests.post(
            f"{args.base_url}/v1/chat/completions",
            json=payload,
            timeout=900,
        )
        r.raise_for_status()
        data = r.json()
        elapsed_ms = round((time.perf_counter() - started) * 1000)
        text = data["choices"][0]["message"]["content"].strip()

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
                "repo": model["repo"],
                "file": model["file"],
                "family": model["family"],
                "params": model["params"],
                "quant": model["quant"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
