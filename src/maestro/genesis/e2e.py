from __future__ import annotations

from dataclasses import dataclass

from maestro import MaestroKernel
from maestro.enums import (
    CouncilId,
    MissionState,
    VerdictScope,
    VerdictValue,
    EvidenceKind,
)
from maestro.models import Evidence, Verdict
from maestro.orchestration.dag import DagNode


@dataclass(slots=True)
class EndToEndResult:
    task_id: str
    dag_complete: bool
    ay_system_juste: bool
    tx_committed: bool
    mission_complete: bool
    evidence_count: int


class EndToEndMissionHarness:
    """
    Deterministic integration certification of the constitutional happy path.
    """

    def run(self) -> EndToEndResult:
        k = MaestroKernel()
        m = k.create_mission(
            "Production Genesis certification mission",
            scope="PM -> IT -> SC -> AY -> TX",
            requested_output="certified system state",
        )
        m.acceptance_criteria = [
            "AC-01 scope defined",
            "AC-02 implementation evidence exists",
            "AC-03 security reviewed",
        ]

        k.move(m, MissionState.CONTEXT_LOADING)
        k.move(m, MissionState.ANALYSIS)
        k.move(m, MissionState.CONTRACT_PENDING)
        m.strike_team = [CouncilId.PM, CouncilId.IT, CouncilId.SC, CouncilId.AY, CouncilId.TX]
        k.move(m, MissionState.STRIKE_TEAM_CONVENED)
        k.move(m, MissionState.DISPATCHED)
        k.move(m, MissionState.EXECUTING)

        k.add_dag_node(m, DagNode("pm", CouncilId.PM, "DEFINE", ["AC-01"]))
        k.add_dag_node(m, DagNode("it", CouncilId.IT, "IMPLEMENT", ["AC-02"], depends_on={"pm"}))
        k.add_dag_node(m, DagNode("sc", CouncilId.SC, "AUDIT", ["AC-03"], depends_on={"it"}))

        for node_id, output in [
            ("pm", {"scope": "approved"}),
            ("it", {"artifact": "certified.py"}),
            ("sc", {"security": "pass"}),
        ]:
            k.start_dag_node(m, node_id)
            k.succeed_dag_node(m, node_id, output)

        ev_ids = []
        for council, kind, claim in [
            (CouncilId.PM, EvidenceKind.OTHER, "Scope defined"),
            (CouncilId.IT, EvidenceKind.TEST_RESULT, "Implementation tests pass"),
            (CouncilId.SC, EvidenceKind.SECURITY_SCAN, "Security scan passes"),
        ]:
            ev_ids.append(
                k.add_evidence(
                    Evidence(
                        task_id=m.task_id,
                        council=council,
                        kind=kind,
                        claim=claim,
                        payload={"ok": True},
                    )
                )
            )

        k.move(m, MissionState.PAUSED_FOR_AUDIT)
        k.move(m, MissionState.AUDITING)

        k.submit_verdict(
            m,
            Verdict(
                task_id=m.task_id,
                council=CouncilId.SC,
                value=VerdictValue.JUSTE,
                scope=VerdictScope.DOMAIN,
                evidence_ids=[ev_ids[-1]],
            ),
        )
        k.submit_verdict(
            m,
            Verdict(
                task_id=m.task_id,
                council=CouncilId.AY,
                value=VerdictValue.JUSTE,
                scope=VerdictScope.SYSTEM,
                evidence_ids=ev_ids,
            ),
        )

        k.move(m, MissionState.READY_FOR_RELEASE)
        k.move(m, MissionState.STATE_COMMIT_PENDING)
        k.authorize_durable_commit(m)
        k.commit_durable_state(m)
        k.close(m, durable_change_required=True)

        return EndToEndResult(
            task_id=m.task_id,
            dag_complete=k.dag(m).complete(),
            ay_system_juste=bool(m.system_verdict and m.system_verdict.value is VerdictValue.JUSTE),
            tx_committed=m.tx_committed,
            mission_complete=m.state is MissionState.TASK_COMPLETE,
            evidence_count=len(k.evidence.for_task(m.task_id)),
        )
