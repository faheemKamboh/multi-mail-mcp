import pytest

from agent.companion.contracts import CompanionState, CompanionTask


def test_dependencies_gate_ready_tasks():
    first = CompanionTask(id='first', title='first', task_manifest='agent/tasks/runtime-smoke.json', status='done', priority=20)
    second = CompanionTask(id='second', title='second', task_manifest='agent/tasks/runtime-smoke.json', depends_on=('first',), priority=10)
    state = CompanionState(tasks=[first, second])
    assert [task.id for task in state.ready_tasks()] == ['second']


def test_unknown_dependency_is_rejected():
    task = CompanionTask(id='x', title='x', task_manifest='agent/tasks/runtime-smoke.json', depends_on=('missing',))
    with pytest.raises(ValueError):
        CompanionState(tasks=[task]).validate()
