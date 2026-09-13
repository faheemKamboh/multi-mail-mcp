from __future__ import annotations

from agent.companion.contracts import CompanionState, CompanionTask
from agent.companion.select_task import (
    failed_attempts,
    global_failure_breaker_blocked,
    pending_tasks,
    pr_state,
    run_is_resolved,
    select_next_task,
    slug,
)


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
    assert [item.id for item in pending_tasks(state)] == ["normalize-email", "classify-email"]

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
    merged_prs = [{
        "headRefName": "agent/normalize-email-123",
        "state": "CLOSED",
        "mergedAt": "2026-09-13T00:00:00Z",
    }]
    assert pr_state("normalize-email", merged_prs) == "merged"

    selected, failures = select_next_task(state, [], [])
    assert selected is not None and selected.id == "normalize-email"
    assert failures == 0

    selected, failures = select_next_task(state, merged_prs, [])
    assert selected is not None and selected.id == "classify-email"
    assert failures == 0

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

    breaker_state = CompanionState(tasks=[
        CompanionTask(
            id="runtime-smoke",
            title="Runtime smoke",
            task_manifest="agent/tasks/runtime-smoke.json",
            priority=10,
        ),
        CompanionTask(
            id="email-normalization",
            title="Normalize email",
            task_manifest="agent/tasks/email-normalization.json",
            priority=20,
            depends_on=("runtime-smoke",),
        ),
    ])
    breaker_runs = [
        {
            "displayTitle": "agent-task agent/tasks/email-normalization.json",
            "status": "completed",
            "conclusion": "failure",
        },
        {
            "displayTitle": "agent-task agent/tasks/runtime-smoke.json",
            "status": "completed",
            "conclusion": "failure",
        },
    ]
    assert global_failure_breaker_blocked(breaker_state, [], breaker_runs)

    resolved_prs = [
        {
            "headRefName": "agent/runtime-smoke-111",
            "state": "CLOSED",
            "mergedAt": "2026-09-13T00:00:00Z",
        },
        {
            "headRefName": "agent/email-normalization-222",
            "state": "CLOSED",
            "mergedAt": "2026-09-13T01:00:00Z",
        },
    ]
    assert run_is_resolved(breaker_state, resolved_prs, breaker_runs[0])
    assert run_is_resolved(breaker_state, resolved_prs, breaker_runs[1])
    assert not global_failure_breaker_blocked(breaker_state, resolved_prs, breaker_runs)

    unknown_failures = [
        {
            "displayTitle": "agent-task agent/tasks/unknown.json",
            "status": "completed",
            "conclusion": "failure",
        },
        breaker_runs[0],
    ]
    assert global_failure_breaker_blocked(breaker_state, [], unknown_failures)

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
