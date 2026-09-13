from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable
import json


VALID_STATUSES = {"ready", "running", "blocked", "done", "failed"}


@dataclass(frozen=True)
class CompanionTask:
    id: str
    title: str
    task_manifest: str
    status: str = "ready"
    priority: int = 100
    depends_on: tuple[str, ...] = ()
    attempts: int = 0
    max_attempts: int = 2
    notes: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CompanionTask":
        task = cls(
            id=str(data["id"]),
            title=str(data["title"]),
            task_manifest=str(data["task_manifest"]),
            status=str(data.get("status", "ready")),
            priority=int(data.get("priority", 100)),
            depends_on=tuple(str(x) for x in data.get("depends_on", [])),
            attempts=int(data.get("attempts", 0)),
            max_attempts=int(data.get("max_attempts", 2)),
            notes=str(data.get("notes", "")),
        )
        task.validate()
        return task

    def validate(self) -> None:
        if not self.id or not self.title or not self.task_manifest:
            raise ValueError("task id, title, and task_manifest are required")
        if self.status not in VALID_STATUSES:
            raise ValueError(f"invalid task status: {self.status}")
        if self.priority < 0:
            raise ValueError("priority must be non-negative")
        if self.attempts < 0 or self.max_attempts < 1:
            raise ValueError("invalid attempt counters")
        if self.id in self.depends_on:
            raise ValueError("task cannot depend on itself")

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "task_manifest": self.task_manifest,
            "status": self.status,
            "priority": self.priority,
            "depends_on": list(self.depends_on),
            "attempts": self.attempts,
            "max_attempts": self.max_attempts,
            "notes": self.notes,
        }


@dataclass
class CompanionState:
    version: int = 1
    cycle: int = 0
    active_task: str | None = None
    last_result: str | None = None
    tasks: list[CompanionTask] = field(default_factory=list)

    @classmethod
    def load(cls, path: Path) -> "CompanionState":
        raw = json.loads(path.read_text())
        state = cls(
            version=int(raw.get("version", 1)),
            cycle=int(raw.get("cycle", 0)),
            active_task=raw.get("active_task"),
            last_result=raw.get("last_result"),
            tasks=[CompanionTask.from_dict(item) for item in raw.get("tasks", [])],
        )
        state.validate()
        return state

    def validate(self) -> None:
        ids = [task.id for task in self.tasks]
        if len(ids) != len(set(ids)):
            raise ValueError("duplicate companion task id")
        known = set(ids)
        for task in self.tasks:
            unknown = set(task.depends_on) - known
            if unknown:
                raise ValueError(f"task {task.id} has unknown dependencies: {sorted(unknown)}")
        if self.active_task is not None and self.active_task not in known:
            raise ValueError("active_task must reference a known task")

    def completed_ids(self) -> set[str]:
        return {task.id for task in self.tasks if task.status == "done"}

    def ready_tasks(self) -> Iterable[CompanionTask]:
        completed = self.completed_ids()
        return sorted(
            (
                task
                for task in self.tasks
                if task.status == "ready"
                and task.attempts < task.max_attempts
                and set(task.depends_on).issubset(completed)
            ),
            key=lambda task: (task.priority, task.id),
        )

    def with_task(self, replacement: CompanionTask) -> "CompanionState":
        tasks = [replacement if task.id == replacement.id else task for task in self.tasks]
        updated = CompanionState(
            version=self.version,
            cycle=self.cycle,
            active_task=self.active_task,
            last_result=self.last_result,
            tasks=tasks,
        )
        updated.validate()
        return updated

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "cycle": self.cycle,
            "active_task": self.active_task,
            "last_result": self.last_result,
            "tasks": [task.to_dict() for task in self.tasks],
        }

    def write(self, path: Path) -> None:
        path.write_text(json.dumps(self.to_dict(), indent=2, sort_keys=True) + "\n")
