from __future__ import annotations

import argparse
import json
from dataclasses import replace
from pathlib import Path

from agent.companion.contracts import CompanionState


def main() -> int:
    parser = argparse.ArgumentParser(description="Reconcile a companion task result")
    parser.add_argument("--state", default="agent/state/current.json")
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--result", choices=["done", "failed", "blocked"], required=True)
    parser.add_argument("--note", default="")
    parser.add_argument("--out", default="agent/state/current.json")
    args = parser.parse_args()

    state = CompanionState.load(Path(args.state))
    matches = [task for task in state.tasks if task.id == args.task_id]
    if len(matches) != 1:
        raise SystemExit(f"unknown task id: {args.task_id}")

    task = matches[0]
    status = args.result
    # Failed tasks with attempts remaining are returned to the queue so a
    # later bounded cycle can retry them. Exhausted tasks stay failed.
    if status == "failed" and task.attempts < task.max_attempts:
        status = "ready"

    updated = replace(task, status=status, notes=args.note or task.notes)
    state = state.with_task(updated)
    state.active_task = None
    state.last_result = f"{args.task_id}:{args.result}"
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    state.write(Path(args.out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
