from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from agent.companion.contracts import CompanionState, CompanionTask


def slug(task_id: str) -> str:
    return re.sub(r"[^a-z0-9-]+", "-", task_id.lower()).strip("-")[:48]


def pr_state(task_id: str, pull_requests: list[dict]) -> str | None:
    prefix = f"agent/{slug(task_id)}-"
    matches = [pr for pr in pull_requests if str(pr.get("headRefName", "")).startswith(prefix)]
    if not matches:
        return None
    if any(pr.get("mergedAt") for pr in matches):
        return "merged"
    if any(pr.get("state") == "OPEN" for pr in matches):
        return "open"
    return "closed"


def failed_attempts(task_manifest: str, runs: list[dict]) -> int:
    expected_title = f"agent-task {task_manifest}"
    return sum(
        1
        for run in runs
        if run.get("displayTitle") == expected_title
        and run.get("status") == "completed"
        and run.get("conclusion") != "success"
    )


def pending_tasks(state: CompanionState) -> list[CompanionTask]:
    """Return queue candidates before GitHub-derived dependency resolution.

    Checked-in state is intentionally durable and may remain ``ready`` after a
    task is completed by merging its generated PR. Dependency completion is
    therefore resolved from both checked-in state and merged PR history in
    ``select_next_task`` rather than inside ``CompanionState.ready_tasks``.
    """
    return sorted(
        (
            task
            for task in state.tasks
            if task.status == "ready" and task.attempts < task.max_attempts
        ),
        key=lambda task: (task.priority, task.id),
    )


def select_next_task(
    state: CompanionState,
    pull_requests: list[dict],
    runs: list[dict],
) -> tuple[CompanionTask | None, int]:
    merged = state.completed_ids() | {
        task.id
        for task in state.tasks
        if pr_state(task.id, pull_requests) == "merged"
    }

    for task in pending_tasks(state):
        # A merged PR completes the task and an open PR means work is already
        # awaiting maintainer review. A closed, unmerged PR is retryable; the
        # bounded workflow-run history below remains the source of attempt count.
        if pr_state(task.id, pull_requests) in {"merged", "open"}:
            continue
        failures = task.attempts + failed_attempts(task.task_manifest, runs)
        if failures >= task.max_attempts:
            continue
        if not set(task.depends_on).issubset(merged):
            continue
        return task, failures

    return None, 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--state", default="agent/state/current.json")
    parser.add_argument("--prs", required=True)
    parser.add_argument("--runs")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    state = CompanionState.load(Path(args.state))
    prs = json.loads(Path(args.prs).read_text())
    runs = json.loads(Path(args.runs).read_text()) if args.runs else []
    selected, selected_failures = select_next_task(state, prs, runs)

    result = {
        "selected": selected is not None,
        "task_id": selected.id if selected else "",
        "task_manifest": selected.task_manifest if selected else "",
        "failed_attempts": selected_failures if selected else 0,
    }
    Path(args.out).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
