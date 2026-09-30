from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from maestro.constitution import (
    authorize_tx_commit,
    bootstrap_constitution,
    can_close,
    commit_tx_state,
    register_verdict,
)
from maestro.councils.registry import COUNCILS
from maestro.enums import CouncilId, MissionState
from maestro.evidence.store import EvidenceStore
from maestro.governance.action_firewall import ActionFirewall
from maestro.models import Evidence, Mission, RoutingRequest, Verdict
from maestro.orchestration.dag import DagEngine, DagNode
from maestro.orchestration.dispatcher import Dispatcher
from maestro.orchestration.retry_ledger import RetryLedger, RetryAttempt, RetryAssessment
from maestro.runtime.checkpoint import CheckpointStore
from maestro.runtime.context_compiler import ContextCompiler, CouncilContext
from maestro.state_machine import transition
from maestro.telemetry.tracer import Tracer
from maestro.tools.registry import ToolRegistry


@dataclass
class MaestroKernel:
    dispatcher: Dispatcher = field(default_factory=Dispatcher)
    evidence: EvidenceStore = field(default_factory=EvidenceStore)
    tracer: Tracer = field(default_factory=Tracer)
    firewall: ActionFirewall = field(default_factory=ActionFirewall)
    missions: dict[str, Mission] = field(default_factory=dict)
    dags: dict[str, DagEngine] = field(default_factory=dict)
    retry_ledgers: dict[str, RetryLedger] = field(default_factory=dict)

    def __post_init__(self) -> None:
        bootstrap_constitution()
        self.tools = ToolRegistry(self.firewall)
        self.context_compiler = ContextCompiler()

    @property
    def council_count(self) -> int:
        return len(COUNCILS)

    def create_mission(self, objective: str, scope: str = "", requested_output: str = "") -> Mission:
        mission = Mission(objective=objective, scope=scope, requested_output=requested_output)
        self.missions[mission.task_id] = mission
        self.dags[mission.task_id] = DagEngine()
        self.retry_ledgers[mission.task_id] = RetryLedger()
        self.tracer.emit(mission.task_id, "MISSION_CREATED", "MAESTRO", objective=objective)
        return mission

    def move(self, mission: Mission, new_state: MissionState) -> None:
        old = mission.state
        transition(mission, CouncilId.EX, new_state)
        self.tracer.emit(
            mission.task_id,
            "STATE_TRANSITION",
            CouncilId.EX.value,
            old_state=old.value,
            new_state=new_state.value,
        )

    def route(self, request: RoutingRequest) -> None:
        records = self.dispatcher.dispatch(request, actor=CouncilId.EX)
        self.tracer.emit(
            request.task_id,
            "ROUTED",
            CouncilId.EX.value,
            requested_by=request.requested_by.value,
            targets=[x.target.value for x in records],
            action=request.action,
        )

    def dag(self, mission: Mission) -> DagEngine:
        return self.dags[mission.task_id]

    def add_dag_node(self, mission: Mission, node: DagNode) -> None:
        self.dag(mission).add_node(node)
        self.tracer.emit(
            mission.task_id, "DAG_NODE_ADDED", CouncilId.EX.value,
            node_id=node.node_id, council=node.council.value, action=node.action,
        )

    def ready_dag_nodes(self, mission: Mission) -> list[DagNode]:
        return self.dag(mission).ready_nodes()

    def start_dag_node(self, mission: Mission, node_id: str) -> DagNode:
        node = self.dag(mission).start(node_id, actor=CouncilId.EX)
        self.tracer.emit(
            mission.task_id, "DAG_NODE_STARTED", CouncilId.EX.value,
            node_id=node_id, council=node.council.value,
        )
        return node

    def succeed_dag_node(self, mission: Mission, node_id: str, output: dict | None = None) -> None:
        self.dag(mission).succeed(node_id, output)
        self.tracer.emit(
            mission.task_id, "DAG_NODE_SUCCEEDED", self.dag(mission).nodes[node_id].council.value,
            node_id=node_id,
        )

    def fail_dag_node(self, mission: Mission, node_id: str, error: str) -> None:
        self.dag(mission).fail(node_id, error)
        self.tracer.emit(
            mission.task_id, "DAG_NODE_FAILED", self.dag(mission).nodes[node_id].council.value,
            node_id=node_id, error=error,
        )

    def compile_context(self, mission: Mission, node_id: str, **metadata) -> CouncilContext:
        node = self.dag(mission).nodes[node_id]
        context = self.context_compiler.compile(
            mission,
            node,
            self.dag(mission),
            self.evidence.for_task(mission.task_id),
            metadata,
        )
        self.tracer.emit(
            mission.task_id, "COUNCIL_CONTEXT_COMPILED", CouncilId.EX.value,
            node_id=node_id, council=node.council.value, truncated=context.truncated,
        )
        return context

    def add_evidence(self, evidence: Evidence) -> str:
        evidence_id = self.evidence.add(evidence)
        self.tracer.emit(
            evidence.task_id,
            "EVIDENCE_ADDED",
            evidence.council.value,
            evidence_id=evidence_id,
            kind=evidence.kind.value,
            claim=evidence.claim,
        )
        return evidence_id

    def submit_verdict(self, mission: Mission, verdict: Verdict) -> None:
        register_verdict(mission, verdict)
        self.tracer.emit(
            mission.task_id,
            "VERDICT_RECORDED",
            verdict.council.value,
            verdict=verdict.value.value,
            scope=verdict.scope.value,
        )

    def record_retry(self, mission: Mission, attempt: RetryAttempt) -> RetryAssessment:
        assessment = self.retry_ledgers[mission.task_id].record(CouncilId.OP, attempt)
        self.tracer.emit(
            mission.task_id,
            "OP_RETRY_RECORDED",
            CouncilId.OP.value,
            worker=attempt.worker.value,
            criterion=attempt.criterion_id,
            risk=assessment.risk.value,
            breakout_recommended=assessment.breakout_recommended,
        )
        return assessment

    def save_checkpoint(self, mission: Mission, directory: str | Path) -> Path:
        store = CheckpointStore(directory)
        path = store.save(
            mission,
            self.dag(mission),
            self.retry_ledgers[mission.task_id],
            evidence_ids=[x.evidence_id for x in self.evidence.for_task(mission.task_id)],
            trace_count=len([x for x in self.tracer.events if x.task_id == mission.task_id]),
        )
        self.tracer.emit(
            mission.task_id, "CHECKPOINT_SAVED", CouncilId.EX.value, path=str(path)
        )
        return path

    def resume_checkpoint(self, task_id: str, directory: str | Path) -> Mission:
        bundle = CheckpointStore(directory).load(task_id)
        mission = bundle.mission
        self.missions[task_id] = mission
        self.dags[task_id] = bundle.dag
        self.retry_ledgers[task_id] = bundle.retry_ledger
        self.tracer.emit(task_id, "CHECKPOINT_RESUMED", CouncilId.EX.value)
        return mission

    def authorize_durable_commit(self, mission: Mission) -> None:
        authorize_tx_commit(mission, CouncilId.EX)
        self.tracer.emit(mission.task_id, "TX_COMMIT_AUTHORIZED", CouncilId.EX.value)

    def commit_durable_state(self, mission: Mission) -> None:
        commit_tx_state(mission, CouncilId.TX)
        self.tracer.emit(mission.task_id, "TX_STATE_COMMITTED", CouncilId.TX.value)

    def close(self, mission: Mission, durable_change_required: bool) -> None:
        if not can_close(mission, durable_change_required):
            raise RuntimeError("Mission cannot close: required validation/commit gates are incomplete.")
        self.move(mission, MissionState.TASK_COMPLETE)
        self.tracer.emit(mission.task_id, "MISSION_CLOSED", "MAESTRO")
