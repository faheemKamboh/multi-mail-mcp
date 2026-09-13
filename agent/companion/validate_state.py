from __future__ import annotations

import argparse
import json
from pathlib import Path

from agent.companion.contracts import CompanionState

REQUIRED = {"id", "title", "objective", "acceptance_criteria", "context_files", "editable_files", "test_commands"}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--state", default="agent/state/current.json")
    parser.add_argument("--repo", default=".")
    args = parser.parse_args()
    repo = Path(args.repo)
    state = CompanionState.load(Path(args.state))
    for queued in state.tasks:
        path = repo / queued.task_manifest
        if not path.is_file():
            raise ValueError(f"missing task manifest: {queued.task_manifest}")
        data = json.loads(path.read_text())
        missing = REQUIRED - set(data)
        if missing:
            raise ValueError(f"missing fields: {sorted(missing)}")
        if data["id"] != queued.id:
            raise ValueError("queue id must match manifest id")
        if not data["acceptance_criteria"] or not data["editable_files"] or not data["test_commands"]:
            raise ValueError("task manifest has an empty required collection")
        for filename in data["context_files"] + data["editable_files"]:
            if not (repo / filename).is_file():
                raise ValueError(f"missing referenced file: {filename}")
    print(f"validated {len(state.tasks)} companion task(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
