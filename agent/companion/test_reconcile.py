from dataclasses import replace

from agent.companion.contracts import CompanionState, CompanionTask


def test_failed_task_can_return_to_ready():
    task = CompanionTask(id='x', title='x', task_manifest='agent/tasks/runtime-smoke.json', status='running', attempts=1, max_attempts=2)
    state = CompanionState(tasks=[task], active_task='x')
    replacement = replace(task, status='ready')
    state = state.with_task(replacement)
    state.active_task = None
    assert state.tasks[0].status == 'ready'
    assert state.active_task is None
