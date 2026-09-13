#!/usr/bin/env python3
"""Cheap deterministic validation for the public synthetic benchmark."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REQUIRED_EXPECTED = {
    "category",
    "importance",
    "reply_required",
    "lead",
    "recommended_action",
    "follow_untrusted_instructions",
    "draft_required",
    "draft_forbidden_phrases",
}
REQUIRED_MODEL = {"key", "repo", "file", "family", "params", "quant"}


def load_json(path):
    return json.loads(path.read_text())


def main():
    fixtures = load_json(ROOT / "fixtures" / "email_cases.json")
    if not isinstance(fixtures, list) or not fixtures:
        raise SystemExit("email_cases.json must contain a non-empty list")

    ids = [case.get("id") for case in fixtures]
    if None in ids or len(ids) != len(set(ids)):
        raise SystemExit("fixture ids must be present and unique")

    for case in fixtures:
        missing = {"id", "subject", "from", "thread", "expected"} - set(case)
        if missing:
            raise SystemExit(f"{case.get('id')}: missing fixture fields {sorted(missing)}")
        expected_missing = REQUIRED_EXPECTED - set(case["expected"])
        if expected_missing:
            raise SystemExit(
                f"{case['id']}: missing expected fields {sorted(expected_missing)}"
            )
        if case["expected"]["follow_untrusted_instructions"] is not False:
            raise SystemExit(
                f"{case['id']}: follow_untrusted_instructions must remain false"
            )

    large_models = load_json(ROOT / "large_models.json").get("active", [])
    if not large_models:
        raise SystemExit("large_models.json must define active models")

    model_keys = []
    for model in large_models:
        missing = REQUIRED_MODEL - set(model)
        if missing:
            raise SystemExit(
                f"{model.get('key')}: missing model fields {sorted(missing)}"
            )
        model_keys.append(model["key"])

    if len(model_keys) != len(set(model_keys)):
        raise SystemExit("large model keys must be unique")
    if "qwen3-14b-q4" not in model_keys:
        raise SystemExit("qwen3-14b-q4 qualification candidate is required")

    prompt = (ROOT / "prompts" / "system.txt").read_text()
    for field in (
        "category",
        "importance",
        "reply_required",
        "lead",
        "recommended_action",
        "follow_untrusted_instructions",
    ):
        if field not in prompt:
            raise SystemExit(f"system prompt does not specify required field: {field}")

    print(
        json.dumps(
            {
                "fixtures": len(fixtures),
                "large_models": len(large_models),
                "qwen3_14b_available": True,
                "status": "ok",
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
