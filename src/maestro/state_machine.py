from __future__ import annotations

from maestro.enums import CouncilId, MissionState
from maestro.models import Mission


class InvalidTransition(RuntimeError):
    pass


_ALLOWED: dict[MissionState, set[MissionState]] = {
    MissionState.RECEIVED: {MissionState.CONTEXT_LOADING, MissionState.ANALYSIS, MissionState.TASK_ABORTED},
    MissionState.CONTEXT_LOADING: {MissionState.ANALYSIS, MissionState.HUMAN_INPUT_REQUIRED, MissionState.TASK_ABORTED},
    MissionState.ANALYSIS: {MissionState.CONTRACT_PENDING, MissionState.HUMAN_INPUT_REQUIRED, MissionState.TASK_ABORTED},
    MissionState.CONTRACT_PENDING: {MissionState.STRIKE_TEAM_CONVENED, MissionState.HUMAN_INPUT_REQUIRED, MissionState.TASK_ABORTED},
    MissionState.STRIKE_TEAM_CONVENED: {MissionState.DISPATCHED, MissionState.TASK_ABORTED},
    MissionState.DISPATCHED: {MissionState.EXECUTING, MissionState.TASK_SUSPENDED, MissionState.TASK_ABORTED},
    MissionState.EXECUTING: {MissionState.PAUSED_FOR_AUDIT, MissionState.TASK_SUSPENDED, MissionState.TASK_ABORTED},
    MissionState.PAUSED_FOR_AUDIT: {MissionState.AUDITING, MissionState.TASK_ABORTED},
    MissionState.AUDITING: {
        MissionState.FAULT_RETURNED,
        MissionState.READY_FOR_RELEASE,
        MissionState.HUMAN_INPUT_REQUIRED,
        MissionState.EXTERNAL_COUNSEL_REQUIRED,
        MissionState.TASK_ABORTED,
    },
    MissionState.FAULT_RETURNED: {MissionState.RETRYING, MissionState.LOOP_BLOCKED, MissionState.TASK_ABORTED},
    MissionState.RETRYING: {MissionState.EXECUTING, MissionState.LOOP_BLOCKED, MissionState.TASK_ABORTED},
    MissionState.LOOP_BLOCKED: {MissionState.RX_ACTIVE, MissionState.HUMAN_INPUT_REQUIRED, MissionState.TASK_ABORTED},
    MissionState.RX_ACTIVE: {MissionState.RETRYING, MissionState.HUMAN_INPUT_REQUIRED, MissionState.TASK_ABORTED},
    MissionState.HUMAN_INPUT_REQUIRED: {
        MissionState.ANALYSIS, MissionState.CONTRACT_PENDING, MissionState.RETRYING,
        MissionState.TASK_SUSPENDED, MissionState.TASK_ABORTED,
    },
    MissionState.EXTERNAL_COUNSEL_REQUIRED: {
        MissionState.ANALYSIS, MissionState.CONTRACT_PENDING,
        MissionState.TASK_SUSPENDED, MissionState.TASK_ABORTED,
    },
    MissionState.READY_FOR_RELEASE: {MissionState.STATE_COMMIT_PENDING, MissionState.TASK_COMPLETE, MissionState.TASK_ABORTED},
    MissionState.STATE_COMMIT_PENDING: {MissionState.TASK_COMPLETE, MissionState.TASK_ABORTED},
    MissionState.TASK_SUSPENDED: {
        MissionState.CONTEXT_LOADING, MissionState.ANALYSIS, MissionState.RETRYING,
        MissionState.EXECUTING, MissionState.TASK_ABORTED,
    },
    MissionState.TASK_ABORTED: set(),
    MissionState.TASK_COMPLETE: set(),
}


def transition(mission: Mission, actor: CouncilId, new_state: MissionState) -> None:
    if actor is not CouncilId.EX:
        raise PermissionError("Only EX may change canonical mission lifecycle state.")

    allowed = _ALLOWED[mission.state]
    if new_state not in allowed:
        raise InvalidTransition(f"{mission.state.value} -> {new_state.value} is not allowed.")

    mission.state = new_state
    mission.touch()
