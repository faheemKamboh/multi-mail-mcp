from __future__ import annotations

import argparse
import json
import os
from dataclasses import replace
from pathlib import Path

from agent.companion.contracts import CompanionState


def choose_task(state: CompanionState):
    ready = list(state.ready_tasks())
    return ready[0] if ready else None


def main() -> int:
    parser = argparse.ArgumentParser(description="Run one bounded development-companion cycle")
    parser.add_argument("--state", default="agent/state/current.json")
    parser.add_argument("--out", default="agent/state/companion-output.json")
    parser.add_argument("--max-tasks", type=int, default=1)
    args = parser.parse_args()

    if args.max_tasks < 1 or args.max_tasks > 5:
        raise SystemExit("--max-tasks must be between 1 and 5")

    state_path = Path(args.state)
    state = CompanionState.load(state_path)
    selected = []
    working = state

    for _ in range(args.max_tasks):
        task = choose_task(working)
        if task is None:
            break
        selected.append(task)
        running = replace(task, status="running", attempts=task.attempts + 1)
        working = working.with_task(running)
        working.active_task = task.id
        # One workflow cycle only reserves work. Execution happens in an
        # isolated downstream worker job using the trusted manifest path.
        break

    working.cycle += 1
    if not selected:
        working.active_task = None
        working.last_result = "idle"

    output = {
        "cycle": working.cycle,
        "selected": [
            {
                "id": task.id,
                "title": task.title,
                "task_manifest": task.task_manifest,
            }
            for task in selected
        ],
        "state": working.to_dict(),
    }

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(output, indent=2, sort_keys=True) + "\n")

    gha_output = os.environ.get("GITHUB_OUTPUT")
    if gha_output:
        with open(gha_output, "a", encoding="utf-8") as handle:
            handle.write(f"selected_count={len(selected)}\n")
            handle.write(
                "task_manifest=" + (selected[0].task_manifest if selected else "") + "\n"
            )
            handle.write("task_id=" + (selected[0].id if selected else "") + "\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
