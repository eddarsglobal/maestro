from __future__ import annotations

from maestro.enums import CouncilId, MissionState, VerdictScope, VerdictValue
from maestro.models import Mission, RoutingRequest, Verdict
from maestro.councils.registry import validate_registry


class ConstitutionViolation(RuntimeError):
    pass


def bootstrap_constitution() -> None:
    validate_registry()


def validate_routing_request(request: RoutingRequest) -> None:
    if request.via is not CouncilId.EX:
        raise ConstitutionViolation("Every governed routing request must go through EX.")
    if not request.targets:
        raise ConstitutionViolation("Routing request must have at least one target.")


def validate_verdict(verdict: Verdict) -> None:
    if verdict.scope is VerdictScope.SYSTEM and verdict.council is not CouncilId.AY:
        raise ConstitutionViolation("Only AY may issue a SYSTEM verdict.")

    if verdict.council is CouncilId.AY and verdict.scope is not VerdictScope.SYSTEM:
        raise ConstitutionViolation("AY verdicts must use SYSTEM scope.")

    if verdict.council is not CouncilId.AY and verdict.scope is not VerdictScope.DOMAIN:
        raise ConstitutionViolation("Specialist Councils must use DOMAIN verdict scope.")


def register_verdict(mission: Mission, verdict: Verdict) -> None:
    if verdict.task_id != mission.task_id:
        raise ConstitutionViolation("Verdict task_id does not match mission.")

    validate_verdict(verdict)

    if verdict.scope is VerdictScope.SYSTEM:
        mission.system_verdict = verdict
    else:
        mission.domain_verdicts.append(verdict)

    mission.touch()


def authorize_tx_commit(mission: Mission, actor: CouncilId) -> None:
    if actor is not CouncilId.EX:
        raise ConstitutionViolation("Only EX may authorize TX durable commit.")

    if mission.system_verdict is None:
        raise ConstitutionViolation("TX commit cannot be authorized before AY SYSTEM verdict.")

    if mission.system_verdict.value is not VerdictValue.JUSTE:
        raise ConstitutionViolation("TX commit cannot be authorized unless AY SYSTEM verdict is JUSTE.")

    if mission.state is not MissionState.STATE_COMMIT_PENDING:
        raise ConstitutionViolation("Mission must be STATE_COMMIT_PENDING before TX commit authorization.")

    mission.tx_commit_authorized = True
    mission.touch()


def commit_tx_state(mission: Mission, actor: CouncilId) -> None:
    if actor is not CouncilId.TX:
        raise ConstitutionViolation("Only TX may commit durable project state.")

    if not mission.tx_commit_authorized:
        raise ConstitutionViolation("TX commit requires prior EX authorization.")

    if mission.system_verdict is None or mission.system_verdict.value is not VerdictValue.JUSTE:
        raise ConstitutionViolation("TX commit requires AY SYSTEM JUSTE.")

    mission.tx_committed = True
    mission.touch()


def can_close(mission: Mission, durable_change_required: bool) -> bool:
    if mission.system_verdict is None:
        return False
    if mission.system_verdict.value is not VerdictValue.JUSTE:
        return False
    if durable_change_required and not mission.tx_committed:
        return False
    return True
