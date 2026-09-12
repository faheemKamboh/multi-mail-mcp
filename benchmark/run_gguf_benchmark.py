#!/usr/bin/env python3
import argparse, json, os, time
from pathlib import Path

from llama_cpp import Llama


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--model-key", required=True)
    p.add_argument("--output-dir", required=True)
    a = p.parse_args()

    models = json.loads(Path("benchmark/large_models.json").read_text())
    entry = next((m for m in models["active"] if m["key"] == a.model_key), None)
    if not entry:
        raise SystemExit(f"Unknown model key: {a.model_key}")

    out = Path(a.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    fixtures = json.loads(Path("benchmark/fixtures/email_cases.json").read_text())
    system_prompt = Path("benchmark/prompts/system.txt").read_text()

    load_started = time.perf_counter()
    llm = Llama.from_pretrained(
        repo_id=entry["repo_id"],
        filename=entry["filename"],
        n_ctx=2048,
        n_threads=max(1, min(4, os.cpu_count() or 1)),
        verbose=False,
    )
    load_seconds = time.perf_counter() - load_started

    timings = []
    for case in fixtures:
        user_text = (
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
            temperature=0,
            max_tokens=220,
        )
        elapsed_ms = round((time.perf_counter() - started) * 1000)
        text = (result["choices"][0]["message"]["content"] or "").strip()
        (out / f"{case['id']}.txt").write_text(text)
        (out / f"{case['id']}.response.json").write_text(json.dumps({"model": entry, "text": text}, indent=2))
        timings.append((case["id"], elapsed_ms))

    (out / "timings-ms.csv").write_text("".join(f"{case_id},{ms}\n" for case_id, ms in timings))
    (out / "runtime.json").write_text(json.dumps({
        "model_key": a.model_key,
        "repo_id": entry["repo_id"],
        "filename": entry["filename"],
        "parameters": entry["parameters"],
        "quantization": entry["quantization"],
        "model_load_seconds": round(load_seconds, 3),
    }, indent=2))


if __name__ == "__main__":
    main()
