from __future__ import annotations

import argparse
import json
from pathlib import Path

from agent.companion.contracts import CompanionState


def validate_manifest_path(repo: Path, manifest_path: str) -> None:
    manifest = (repo / manifest_path).resolve()
    if repo.resolve() not in manifest.parents:
        raise ValueError(f"manifest escapes repository: {manifest_path}")
    if not manifest.is_file():
        raise ValueError(f"missing task manifest: {manifest_path}")
    data = json.loads(manifest.read_text())
    required = {"id", "title", "instructions", "editable_paths", "test_command"}
    missing = required - set(data)
    if missing:
        raise ValueError(f"manifest {manifest_path} missing fields: {sorted(missing)}")
    if not isinstance(data["editable_paths"], list) or not data["editable_paths"]:
        raise ValueError(f"manifest {manifest_path} must declare editable_paths")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate development companion state")
    parser.add_argument("--state", default="agent/state/current.json")
    parser.add_argument("--repo", default=".")
    args = parser.parse_args()

    repo = Path(args.repo).resolve()
    state = CompanionState.load(Path(args.state))
    for task in state.tasks:
        validate_manifest_path(repo, task.task_manifest)
    print(f"validated {len(state.tasks)} companion task(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
