#!/usr/bin/env python3
import argparse
import json
import os
import time
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-key", required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()

    models = json.loads(Path("benchmark/models.json").read_text())
    entry = next((m for m in models["active"] if m["key"] == args.model_key), None)
    if not entry:
        raise SystemExit(f"Unknown model key: {args.model_key}")

    model_id = entry["model_id"]
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    fixtures = json.loads(Path("benchmark/fixtures/email_cases.json").read_text())
    system_prompt = Path("benchmark/prompts/system.txt").read_text()

    torch.set_num_threads(max(1, min(4, os.cpu_count() or 1)))

    load_started = time.perf_counter()
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        torch_dtype="auto",
        low_cpu_mem_usage=True,
    )
    model.eval()
    load_seconds = time.perf_counter() - load_started

    timings = []
    for case in fixtures:
        user_text = (
            "Analyze this synthetic email/thread.\n\n"
            f"From: {case['from']}\n"
            f"Subject: {case['subject']}\n\n"
            f"Thread:\n{case['thread']}"
        )
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_text},
        ]

        try:
            prompt = tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True,
                enable_thinking=False,
            )
        except TypeError:
            prompt = tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True,
            )

        inputs = tokenizer(prompt, return_tensors="pt")
        started = time.perf_counter()
        with torch.inference_mode():
            generated = model.generate(
                **inputs,
                max_new_tokens=220,
                do_sample=False,
                pad_token_id=tokenizer.eos_token_id,
            )
        elapsed_ms = round((time.perf_counter() - started) * 1000)
        response_tokens = generated[0][inputs["input_ids"].shape[1] :]
        text = tokenizer.decode(response_tokens, skip_special_tokens=True).strip()

        (output_dir / f"{case['id']}.txt").write_text(text)
        (output_dir / f"{case['id']}.response.json").write_text(
            json.dumps({"model": model_id, "text": text}, indent=2)
        )
        timings.append((case["id"], elapsed_ms))

    (output_dir / "timings-ms.csv").write_text(
        "".join(f"{case_id},{elapsed_ms}\n" for case_id, elapsed_ms in timings)
    )
    (output_dir / "runtime.json").write_text(
        json.dumps(
            {
                "model_key": args.model_key,
                "model_id": model_id,
                "model_load_seconds": round(load_seconds, 3),
                "torch_version": torch.__version__,
                "cpu_threads": torch.get_num_threads(),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
