from pathlib import Path
import json

from agent.companion.contracts import CompanionState


def test_state_loads():
    state = CompanionState.load(Path('agent/state/current.json'))
    assert state.version == 1
    assert list(state.ready_tasks())
