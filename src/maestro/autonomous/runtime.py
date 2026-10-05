from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from maestro import MaestroKernel
from maestro.enums import CouncilId
from maestro.models import Mission
from maestro.orchestration.dag import DagNode
from maestro.research.composition import (
    GovernedResearchComposition,
    compose_governed_web_research,
)
from maestro.research.web_fetch import (
    GovernedWebFetchBinding,
)

from .event_store import EventStore, RuntimeEvent
from .mission_store import MissionStore
from .scheduler import RuntimeScheduler, WorkItem
from .workers import WorkerRegistry, WorkerSpec, WorkerState
from .executor import CouncilExecutor, ExecutionRequest, ExecutionResult
from .recovery import RecoveryManager
from .shadow import LiveShadowEvaluator


class AutonomousRuntime:
    """
    Production-shaped orchestration runtime around the MAESTRO kernel.

    Important: autonomy operates *inside* constitutional limits.
    """

    def __init__(
        self,
        runtime_dir: str | Path,
        *,
        web_research_binding: (
            GovernedWebFetchBinding
            | None
        ) = None,
    ):
        if (
            web_research_binding is not None
            and not isinstance(
                web_research_binding,
                GovernedWebFetchBinding,
            )
        ):
            raise TypeError(
                "web_research_binding must be a "
                "GovernedWebFetchBinding or None."
            )

        self.runtime_dir = Path(runtime_dir)
        self.runtime_dir.mkdir(parents=True, exist_ok=True)

        self.kernel = MaestroKernel()

        self.research: (
            GovernedResearchComposition
            | None
        ) = None

        if web_research_binding is not None:
            self.research = (
                compose_governed_web_research(
                    tools=self.kernel.tools,
                    binding=(
                        web_research_binding
                    ),
                )
            )

        self.events = EventStore(self.runtime_dir / "events.jsonl")
        self.missions = MissionStore(self.runtime_dir / "missions")
        self.scheduler = RuntimeScheduler()
        self.workers = WorkerRegistry()
        self.executor = CouncilExecutor()
        self.shadow = LiveShadowEvaluator()
        self.recovery = RecoveryManager(self.missions, self.events)

    def create_mission(self, objective: str, scope: str = "", requested_output: str = "") -> Mission:
        mission = self.kernel.create_mission(objective, scope, requested_output)
        self.missions.save(mission)
        self.events.append(RuntimeEvent(mission.task_id, "MISSION_CREATED", "MAESTRO", {"objective": objective}))
        return mission

    def persist(self, mission: Mission, event_type: str, actor: str, payload: dict | None = None) -> None:
        self.missions.save(mission)
        self.events.append(RuntimeEvent(mission.task_id, event_type, actor, payload or {}))

    def enqueue_dag_ready(self, mission: Mission) -> list[str]:
        work_ids = []
        for node in self.kernel.ready_dag_nodes(mission):
            item = WorkItem(
                task_id=mission.task_id,
                council=node.council.value,
                action=node.action,
                payload={"node_id": node.node_id},
            )
            work_ids.append(self.scheduler.enqueue(item))
        return work_ids

    def register_worker(self, worker: WorkerSpec) -> None:
        self.workers.register(worker)

    def run_one(self, worker_id: str) -> ExecutionResult | None:
        worker = self.workers.get(worker_id)
        if worker.state is not WorkerState.IDLE:
            return None

        item = self.scheduler.lease_next(worker_id, worker.allowed_councils)
        if item is None:
            return None

        worker.state = WorkerState.BUSY
        try:
            council = CouncilId(item.council)
            mission = self.kernel.missions[item.task_id]
            node_id = item.payload["node_id"]

            self.kernel.start_dag_node(mission, node_id)
            context = self.kernel.compile_context(mission, node_id)

            result = self.executor.execute(
                ExecutionRequest(
                    task_id=mission.task_id,
                    council=council,
                    action=item.action,
                    context=context.to_dict(),
                )
            )

            if result.success:
                self.kernel.succeed_dag_node(mission, node_id, result.output)
                self.scheduler.complete(item.work_id)
                self.persist(mission, "WORK_SUCCEEDED", council.value, {"work_id": item.work_id, "node_id": node_id})
            else:
                self.kernel.fail_dag_node(mission, node_id, result.error or "unknown failure")
                self.scheduler.fail(item.work_id)
                self.persist(mission, "WORK_FAILED", council.value, {"work_id": item.work_id, "node_id": node_id, "error": result.error})

            return result
        finally:
            worker.state = WorkerState.IDLE
