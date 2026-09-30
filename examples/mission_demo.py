from maestro import MaestroKernel
from maestro.enums import CouncilId, EvidenceKind, MissionState, VerdictScope, VerdictValue
from maestro.models import Evidence, RoutingRequest, Verdict


kernel = MaestroKernel()
mission = kernel.create_mission(
    "Implement a secure document upload endpoint",
    scope="API + storage + validation",
    requested_output="Audited implementation",
)

kernel.move(mission, MissionState.CONTEXT_LOADING)
kernel.move(mission, MissionState.ANALYSIS)
kernel.move(mission, MissionState.CONTRACT_PENDING)

mission.acceptance_criteria = [
    "AC-01 Upload valid document",
    "AC-02 Reject oversized input",
    "AC-03 Enforce authorization",
]
mission.strike_team = [CouncilId.IT, CouncilId.SC, CouncilId.OP, CouncilId.AY]

kernel.move(mission, MissionState.STRIKE_TEAM_CONVENED)

kernel.route(
    RoutingRequest(
        task_id=mission.task_id,
        requested_by=CouncilId.AY,
        targets=[CouncilId.IT, CouncilId.SC],
        action="EXECUTE_AND_AUDIT",
        reason="Acceptance contract requires implementation and security review.",
    )
)

kernel.move(mission, MissionState.DISPATCHED)
kernel.move(mission, MissionState.EXECUTING)

evidence_id = kernel.add_evidence(
    Evidence(
        task_id=mission.task_id,
        council=CouncilId.IT,
        kind=EvidenceKind.TEST_RESULT,
        claim="Upload integration tests pass",
        payload={"passed": 8, "failed": 0},
    )
)

kernel.move(mission, MissionState.PAUSED_FOR_AUDIT)
kernel.move(mission, MissionState.AUDITING)

kernel.submit_verdict(
    mission,
    Verdict(
        task_id=mission.task_id,
        council=CouncilId.SC,
        value=VerdictValue.JUSTE,
        scope=VerdictScope.DOMAIN,
        evidence_ids=[evidence_id],
    ),
)

kernel.submit_verdict(
    mission,
    Verdict(
        task_id=mission.task_id,
        council=CouncilId.AY,
        value=VerdictValue.JUSTE,
        scope=VerdictScope.SYSTEM,
        evidence_ids=[evidence_id],
    ),
)

kernel.move(mission, MissionState.READY_FOR_RELEASE)
kernel.move(mission, MissionState.STATE_COMMIT_PENDING)
kernel.authorize_durable_commit(mission)
kernel.commit_durable_state(mission)
kernel.close(mission, durable_change_required=True)

print(mission.to_dict())
