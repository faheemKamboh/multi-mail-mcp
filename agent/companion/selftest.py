from __future__ import annotations

from agent.companion.contracts import CompanionState, CompanionTask
from agent.companion.select_task import failed_attempts, pr_state, slug


def run() -> None:
    assert slug("Normalize Email / Fixture") == "normalize-email-fixture"

    task = CompanionTask(
        id="normalize-email",
        title="Normalize email",
        task_manifest="agent/tasks/runtime-smoke.json",
        priority=10,
    )
    dependent = CompanionTask(
        id="classify-email",
        title="Classify email",
        task_manifest="agent/tasks/runtime-smoke.json",
        priority=20,
        depends_on=("normalize-email",),
    )
    state = CompanionState(tasks=[dependent, task])
    assert [item.id for item in state.ready_tasks()] == ["normalize-email"]

    assert pr_state("normalize-email", []) is None
    assert pr_state("normalize-email", [{
        "headRefName": "agent/normalize-email-123",
        "state": "OPEN",
        "mergedAt": None,
    }]) == "open"
    assert pr_state("normalize-email", [{
        "headRefName": "agent/normalize-email-123",
        "state": "CLOSED",
        "mergedAt": None,
    }]) == "closed"
    assert pr_state("normalize-email", [{
        "headRefName": "agent/normalize-email-123",
        "state": "CLOSED",
        "mergedAt": "2026-09-13T00:00:00Z",
    }]) == "merged"

    runs = [
        {
            "displayTitle": "agent-task agent/tasks/runtime-smoke.json",
            "status": "completed",
            "conclusion": "failure",
        },
        {
            "displayTitle": "agent-task agent/tasks/another-task.json",
            "status": "completed",
            "conclusion": "failure",
        },
        {
            "displayTitle": "agent-task agent/tasks/runtime-smoke.json",
            "status": "completed",
            "conclusion": "success",
        },
    ]
    assert failed_attempts("agent/tasks/runtime-smoke.json", runs) == 1

    try:
        CompanionState(tasks=[CompanionTask(
            id="bad",
            title="Bad dependency",
            task_manifest="agent/tasks/runtime-smoke.json",
            depends_on=("missing",),
        )]).validate()
    except ValueError:
        pass
    else:
        raise AssertionError("unknown dependencies must be rejected")


if __name__ == "__main__":
    run()
    print("companion self-test passed")
