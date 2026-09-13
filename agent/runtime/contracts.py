#!/usr/bin/env python3
"""Validation helpers for trusted task manifests and untrusted model proposals."""

from __future__ import annotations

import json
from pathlib import Path, PurePosixPath

REPO_ROOT = Path(__file__).resolve().parents[2]
TASK_ROOT = PurePosixPath("agent/tasks")
PROTECTED_PREFIXES = (
    PurePosixPath(".git"),
    PurePosixPath(".github"),
    PurePosixPath("agent/runtime"),
    PurePosixPath("agent/qualification"),
)
MAX_EDIT_FILES = 12
MAX_FILE_BYTES = 250_000


def _relative_repo_path(value: str) -> PurePosixPath:
    path = PurePosixPath(value)
    if path.is_absolute() or not path.parts or ".." in path.parts or "." in path.parts:
        raise ValueError(f"unsafe repository path: {value!r}")
    return path


def _under(path: PurePosixPath, prefix: PurePosixPath) -> bool:
    return path == prefix or prefix in path.parents


def load_task(task_file: str | Path) -> tuple[Path, dict]:
    raw = PurePosixPath(str(task_file))
    if raw.is_absolute() or ".." in raw.parts:
        raise ValueError("task file must be a repository-relative path")
    if not _under(raw, TASK_ROOT):
        raise ValueError("task file must live under agent/tasks/")

    absolute = REPO_ROOT / Path(*raw.parts)
    task = json.loads(absolute.read_text())
    validate_task(task)
    return absolute, task


def validate_task(task: dict) -> None:
    required = {
        "id",
        "title",
        "objective",
        "context_files",
        "editable_files",
        "test_commands",
    }
    missing = required - set(task)
    if missing:
        raise ValueError(f"task missing fields: {sorted(missing)}")

    if not isinstance(task["id"], str) or not task["id"].strip():
        raise ValueError("task id must be non-empty text")
    if not isinstance(task["title"], str) or not task["title"].strip():
        raise ValueError("task title must be non-empty text")
    if not isinstance(task["objective"], str) or not task["objective"].strip():
        raise ValueError("task objective must be non-empty text")

    context_files = task["context_files"]
    editable_files = task["editable_files"]
    test_commands = task["test_commands"]
    if not isinstance(context_files, list):
        raise ValueError("context_files must be a list")
    if not isinstance(editable_files, list) or not editable_files:
        raise ValueError("editable_files must be a non-empty list")
    if len(editable_files) > MAX_EDIT_FILES:
        raise ValueError(f"too many editable files (max {MAX_EDIT_FILES})")
    if len(editable_files) != len(set(editable_files)):
        raise ValueError("editable_files must be unique")

    allow_protected = bool(task.get("allow_protected_paths", False))
    for value in context_files:
        path = _relative_repo_path(value)
        if not (REPO_ROOT / Path(*path.parts)).is_file():
            raise ValueError(f"missing context file: {value}")

    for value in editable_files:
        path = _relative_repo_path(value)
        if not allow_protected and any(_under(path, prefix) for prefix in PROTECTED_PREFIXES):
            raise ValueError(f"protected path is not editable: {value}")

    if not isinstance(test_commands, list) or not test_commands:
        raise ValueError("test_commands must be a non-empty list")
    for command in test_commands:
        if not isinstance(command, list) or not command:
            raise ValueError("each test command must be a non-empty argv list")
        if not all(isinstance(arg, str) and arg for arg in command):
            raise ValueError("test command arguments must be non-empty strings")


def validate_proposal(task: dict, proposal: dict) -> list[dict]:
    if not isinstance(proposal, dict):
        raise ValueError("proposal must be an object")
    changes = proposal.get("changes")
    if not isinstance(changes, list) or not changes:
        raise ValueError("proposal must contain non-empty changes")
    if len(changes) > MAX_EDIT_FILES:
        raise ValueError(f"proposal changes too many files (max {MAX_EDIT_FILES})")

    allowed = set(task["editable_files"])
    seen: set[str] = set()
    normalized = []
    for change in changes:
        if not isinstance(change, dict):
            raise ValueError("each change must be an object")
        path = change.get("path")
        content = change.get("content")
        if path not in allowed:
            raise ValueError(f"model attempted non-allowed path: {path!r}")
        if path in seen:
            raise ValueError(f"duplicate change path: {path}")
        _relative_repo_path(path)
        if not isinstance(content, str):
            raise ValueError(f"content must be text for {path}")
        if len(content.encode("utf-8")) > MAX_FILE_BYTES:
            raise ValueError(f"replacement exceeds {MAX_FILE_BYTES} bytes: {path}")
        seen.add(path)
        normalized.append({"path": path, "content": content})

    return normalized


def extract_json_object(text: str) -> dict:
    start, end = text.find("{"), text.rfind("}")
    if start < 0 or end < start:
        raise ValueError("response contains no JSON object")
    value = json.loads(text[start : end + 1])
    if not isinstance(value, dict):
        raise ValueError("response JSON must be an object")
    return value
