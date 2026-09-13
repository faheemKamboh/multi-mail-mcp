#!/usr/bin/env python3
"""Apply an untrusted worker proposal under a trusted task contract and run fixed tests."""

from __future__ import annotations

import argparse
import json
import subprocess
import time
from pathlib import Path

from contracts import REPO_ROOT, load_task, validate_proposal

TEST_TIMEOUT_SECONDS = 180


def run(command: list[str]) -> dict:
    started = time.perf_counter()
    completed = subprocess.run(
        command,
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        timeout=TEST_TIMEOUT_SECONDS,
        check=False,
    )
    return {
        "argv": command,
        "returncode": completed.returncode,
        "elapsed_ms": round((time.perf_counter() - started) * 1000),
        "stdout": completed.stdout[-8000:],
        "stderr": completed.stderr[-8000:],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", required=True)
    parser.add_argument("--worker-record", required=True)
    parser.add_argument("--report", required=True)
    parser.add_argument("--patch", required=True)
    args = parser.parse_args()

    _, task = load_task(args.task)
    worker = json.loads(Path(args.worker_record).read_text())
    if worker.get("task_id") != task["id"]:
        raise SystemExit("worker record task id does not match trusted task")
    if not worker.get("valid") or not isinstance(worker.get("proposal"), dict):
        raise SystemExit("worker record does not contain a valid proposal")

    changes = validate_proposal(task, worker["proposal"])
    before = {}
    for change in changes:
        target = REPO_ROOT / change["path"]
        before[change["path"]] = target.read_text() if target.is_file() else None
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(change["content"])

    # Intent-to-add makes new text files visible in a normal git diff without
    # staging their content. The checkout is ephemeral in the workflow.
    subprocess.run(
        ["git", "add", "-N", "--", *[change["path"] for change in changes]],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    diff = subprocess.run(
        ["git", "diff", "--no-ext-diff", "--", *[change["path"] for change in changes]],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=True,
    ).stdout
    if not diff.strip():
        raise SystemExit("proposal produced no repository diff")

    results = []
    all_passed = True
    for command in task["test_commands"]:
        try:
            result = run(command)
        except subprocess.TimeoutExpired as exc:
            result = {
                "argv": command,
                "returncode": None,
                "elapsed_ms": TEST_TIMEOUT_SECONDS * 1000,
                "stdout": (exc.stdout or "")[-8000:] if isinstance(exc.stdout, str) else "",
                "stderr": (exc.stderr or "")[-8000:] if isinstance(exc.stderr, str) else "",
                "timeout": True,
            }
        results.append(result)
        if result.get("returncode") != 0:
            all_passed = False
            break

    report = {
        "task_id": task["id"],
        "changed_files": [change["path"] for change in changes],
        "tests_passed": all_passed,
        "tests": results,
        "worker_summary": worker["proposal"].get("summary"),
        "worker_risks": worker["proposal"].get("risks", []),
    }
    Path(args.report).parent.mkdir(parents=True, exist_ok=True)
    Path(args.report).write_text(json.dumps(report, indent=2))
    Path(args.patch).parent.mkdir(parents=True, exist_ok=True)
    Path(args.patch).write_text(diff)
    print(json.dumps(report, indent=2))

    if not all_passed:
        raise SystemExit("proposal failed trusted deterministic tests")


if __name__ == "__main__":
    main()
