#!/usr/bin/env python3
"""Publish an independently approved, re-verified proposal as a draft pull request."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
from pathlib import Path

from contracts import REPO_ROOT, load_task


def checked(argv: list[str], *, env: dict | None = None) -> str:
    completed = subprocess.run(
        argv,
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        env=env,
        check=False,
    )
    if completed.returncode != 0:
        raise SystemExit(
            f"command failed ({completed.returncode}): {' '.join(argv)}\n"
            f"stdout:\n{completed.stdout[-4000:]}\n"
            f"stderr:\n{completed.stderr[-4000:]}"
        )
    return completed.stdout.strip()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", required=True)
    parser.add_argument("--verification", required=True)
    parser.add_argument("--review", required=True)
    parser.add_argument("--base", default="main")
    args = parser.parse_args()

    _, task = load_task(args.task)
    verification = json.loads(Path(args.verification).read_text())
    review_record = json.loads(Path(args.review).read_text())

    if verification.get("task_id") != task["id"] or not verification.get("tests_passed"):
        raise SystemExit("publish requires matching, passing deterministic verification")
    if review_record.get("task_id") != task["id"]:
        raise SystemExit("review record does not match trusted task")
    if not review_record.get("valid") or review_record.get("verdict") != "pass":
        raise SystemExit("publish requires a valid independent reviewer pass")

    changed = verification.get("changed_files")
    if not isinstance(changed, list) or not changed:
        raise SystemExit("verification report has no changed files")
    allowed = set(task["editable_files"])
    if any(path not in allowed for path in changed):
        raise SystemExit("verification report contains a path outside the task allowlist")

    run_id = os.environ.get("GITHUB_RUN_ID", "local")
    slug = re.sub(r"[^a-z0-9-]+", "-", task["id"].lower()).strip("-")[:48]
    branch = f"agent/{slug}-{run_id}"

    checked(["git", "config", "user.name", "github-actions[bot]"])
    checked(["git", "config", "user.email", "41898282+github-actions[bot]@users.noreply.github.com"])
    checked(["git", "checkout", "-b", branch])
    checked(["git", "add", "--", *changed])

    staged = checked(["git", "diff", "--cached", "--name-only"]).splitlines()
    if set(staged) != set(changed):
        raise SystemExit(f"staged file set mismatch: staged={staged}, expected={changed}")

    checked(["git", "commit", "-m", f"agent: {task['title']}"])
    checked(["git", "push", "--set-upstream", "origin", branch])

    server = os.environ.get("GITHUB_SERVER_URL", "https://github.com")
    repository = os.environ.get("GITHUB_REPOSITORY", "")
    run_url = f"{server}/{repository}/actions/runs/{run_id}" if repository else ""
    review = review_record.get("review") or {}
    body = "\n".join(
        [
            "Automated bounded task proposal.",
            "",
            f"Task: `{task['id']}` — {task['title']}",
            f"Deterministic tests: passed",
            f"Independent reviewer: pass",
            f"Reviewer reason: {review.get('reason', '')}",
            f"Workflow evidence: {run_url}" if run_url else "",
            "",
            "This PR is intentionally created as a draft. Autonomous merge is disabled during qualification.",
        ]
    ).strip()

    env = os.environ.copy()
    token = env.get("GH_TOKEN") or env.get("GITHUB_TOKEN")
    if not token:
        raise SystemExit("GH_TOKEN/GITHUB_TOKEN is required only for the publish job")
    env["GH_TOKEN"] = token
    pr_url = checked(
        [
            "gh",
            "pr",
            "create",
            "--draft",
            "--base",
            args.base,
            "--head",
            branch,
            "--title",
            f"agent: {task['title']}",
            "--body",
            body,
        ],
        env=env,
    )
    print(json.dumps({"branch": branch, "pull_request": pr_url}, indent=2))


if __name__ == "__main__":
    main()
