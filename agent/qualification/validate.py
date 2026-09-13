#!/usr/bin/env python3
"""Cheap deterministic validation for coding worker/reviewer qualification assets."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def load(path):
    return json.loads(path.read_text())


def main():
    tasks = load(ROOT / "agent" / "qualification" / "tasks.json")
    if not isinstance(tasks, list) or not tasks:
        raise SystemExit("tasks.json must contain a non-empty list")

    ids = []
    for task in tasks:
        required = {
            "id",
            "title",
            "instruction",
            "context_files",
            "editable_files",
            "test_command",
            "workdir",
        }
        missing = required - set(task)
        if missing:
            raise SystemExit(f"task missing fields: {sorted(missing)}")
        ids.append(task["id"])
        if not task["editable_files"]:
            raise SystemExit(f"{task['id']}: editable_files cannot be empty")
        if not task["test_command"]:
            raise SystemExit(f"{task['id']}: test_command cannot be empty")
        for rel in task["context_files"] + task["editable_files"]:
            path = ROOT / rel
            if not path.is_file():
                raise SystemExit(f"{task['id']}: missing referenced file {rel}")
        workdir = ROOT / task["workdir"]
        if not workdir.is_dir():
            raise SystemExit(f"{task['id']}: missing workdir {task['workdir']}")
        for rel in task["editable_files"]:
            try:
                (ROOT / rel).relative_to(workdir)
            except ValueError as exc:
                raise SystemExit(
                    f"{task['id']}: editable file must stay inside workdir: {rel}"
                ) from exc

    if len(ids) != len(set(ids)):
        raise SystemExit("coding task ids must be unique")

    reviews = load(ROOT / "agent" / "qualification" / "review_cases.json")
    if not isinstance(reviews, list) or not reviews:
        raise SystemExit("review_cases.json must contain a non-empty list")

    review_ids = []
    verdicts = set()
    for case in reviews:
        required = {
            "id",
            "task",
            "diff",
            "tests",
            "expected_verdict",
            "required_finding_terms",
        }
        missing = required - set(case)
        if missing:
            raise SystemExit(f"review case missing fields: {sorted(missing)}")
        review_ids.append(case["id"])
        verdict = case["expected_verdict"]
        if verdict not in {"pass", "changes_required"}:
            raise SystemExit(f"{case['id']}: invalid expected_verdict {verdict}")
        verdicts.add(verdict)
        if verdict == "changes_required" and not case["required_finding_terms"]:
            raise SystemExit(
                f"{case['id']}: rejection cases need finding terms for measurable review"
            )

    if len(review_ids) != len(set(review_ids)):
        raise SystemExit("review case ids must be unique")
    if verdicts != {"pass", "changes_required"}:
        raise SystemExit("review suite must contain both passing and rejecting cases")

    print(
        json.dumps(
            {
                "coding_tasks": len(tasks),
                "review_cases": len(reviews),
                "status": "ok",
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
