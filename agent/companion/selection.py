from __future__ import annotations

from agent.companion.contracts import CompanionState, CompanionTask


def next_ready_task(state: CompanionState) -> CompanionTask | None:
    ready = list(state.ready_tasks())
    return ready[0] if ready else None
