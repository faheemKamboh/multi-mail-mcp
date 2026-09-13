from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from agent.companion.contracts import CompanionState


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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--state", default="agent/state/current.json")
    parser.add_argument("--prs", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    state = CompanionState.load(Path(args.state))
    prs = json.loads(Path(args.prs).read_text())
    merged = state.completed_ids() | {
        task.id for task in state.tasks if pr_state(task.id, prs) == "merged"
    }

    selected = None
    for task in state.ready_tasks():
        if pr_state(task.id, prs) is not None:
            continue
        if not set(task.depends_on).issubset(merged):
            continue
        selected = task
        break

    result = {
        "selected": selected is not None,
        "task_id": selected.id if selected else "",
        "task_manifest": selected.task_manifest if selected else "",
    }
    Path(args.out).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
