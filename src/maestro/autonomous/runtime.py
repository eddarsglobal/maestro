from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from datetime import datetime, timezone

from maestro.models import Evidence
from maestro.research.contracts import (
    ContentDigest,
    ExternalArtifact,
    ResearchClaim,
    ResearchSource,
    SourceProvenance,
)
from maestro.research.durable_store import (
    ResearchEvidenceStore,
)
from maestro.research.evidence_bridge import (
    ResearchEvidenceBridge,
)
from maestro.research.runtime import (
    ResearchRequest,
)
from maestro.research.transport import governed_http_cancellation
from maestro.research.web_fetch import (
    GOVERNED_WEB_FETCH_PROVIDER_ID,
    GovernedWebFetchResult,
)

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


class ResearchFetchCancelled(RuntimeError):
    """Cancellation observed before durable research evidence publication."""


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

        self.research_evidence: (
            ResearchEvidenceStore
            | None
        ) = None

        if web_research_binding is not None:
            self.activate_web_research(
                web_research_binding
            )

        self.events = EventStore(self.runtime_dir / "events.jsonl")
        self.missions = MissionStore(self.runtime_dir / "missions")
        self.scheduler = RuntimeScheduler()
        self.workers = WorkerRegistry()
        self.executor = CouncilExecutor()
        self.shadow = LiveShadowEvaluator()
        self.recovery = RecoveryManager(self.missions, self.events)

    def activate_web_research(
        self,
        binding: GovernedWebFetchBinding,
    ) -> None:
        """
        Explicitly activate governed Web Research
        after runtime construction.

        Default construction remains Web-OFF.
        The caller must supply the governed binding;
        this method never creates Web authority
        implicitly.
        """

        if not isinstance(
            binding,
            GovernedWebFetchBinding,
        ):
            raise TypeError(
                "binding must be a "
                "GovernedWebFetchBinding."
            )

        if (
            self.research is not None
            or self.research_evidence
            is not None
        ):
            raise RuntimeError(
                "Web research is already "
                "activated."
            )

        store = ResearchEvidenceStore(
            self.runtime_dir
            / "research_evidence.sqlite3"
        )

        composition = (
            compose_governed_web_research(
                tools=self.kernel.tools,
                binding=binding,
            )
        )

        self.research = composition
        self.research_evidence = store

        self._hydrate_research_evidence()

    def _hydrate_research_evidence(
        self,
    ) -> None:
        """
        Restore durable RX evidence into the
        Kernel's ordinary EvidenceStore.

        Hydration does not re-emit evidence events
        and performs no network access.
        """

        if self.research_evidence is None:
            return

        for evidence_id in (
            self.research_evidence.ids()
        ):
            evidence = (
                self.research_evidence.get(
                    evidence_id
                )
            )

            try:
                existing = (
                    self.kernel.evidence.get(
                        evidence_id
                    )
                )
            except KeyError:
                self.kernel.evidence.add(
                    evidence
                )
                continue

            if (
                existing.to_dict()
                != evidence.to_dict()
            ):
                raise RuntimeError(
                    "Durable research evidence "
                    "conflicts with Kernel evidence."
                )

    def research_fetch(
        self,
        mission: Mission,
        url: str,
        *,
        cancellation=None,
    ) -> Evidence:
        """
        Execute one governed RX Web fetch for an
        owned MAESTRO mission, convert the result
        to ordinary Evidence, persist the RX
        evidence, and expose the same Evidence to
        the Kernel.

        External content remains unverified.
        """

        if self.research is None:
            raise RuntimeError(
                "Web research is not activated."
            )

        if self.research_evidence is None:
            raise RuntimeError(
                "Durable research evidence "
                "is not activated."
            )

        if not isinstance(
            mission,
            Mission,
        ):
            raise TypeError(
                "mission must be a Mission."
            )

        if (
            self.kernel.missions.get(
                mission.task_id
            )
            is not mission
        ):
            raise ValueError(
                "mission must be owned by "
                "this runtime."
            )

        if cancellation is not None and cancellation.is_set():
            raise ResearchFetchCancelled("Research cancelled before external fetch")

        provider = (
            self.research.providers
            .descriptor(
                GOVERNED_WEB_FETCH_PROVIDER_ID
            )
        )

        capabilities = tuple(
            provider.capabilities
        )

        if len(capabilities) != 1:
            raise RuntimeError(
                "Governed Web provider must "
                "expose exactly one capability."
            )

        # ContextVar is scoped to this synchronous RX tool invocation only:
        # other missions, fallback providers and later tasks cannot inherit
        # the cancellation token after this block exits.
        try:
            with governed_http_cancellation(cancellation):
                result = self.research.runtime.execute(
                    ResearchRequest(
                        task_id=mission.task_id,
                        capability=capabilities[0],
                        arguments={"url": url},
                    )
                )
        except Exception as exc:
            if cancellation is not None and cancellation.is_set():
                raise ResearchFetchCancelled(
                    "Research cancelled during governed external transport"
                ) from exc
            raise

        # Do not materialize a response as durable evidence if cancellation
        # raced with completion of the governed network transport.
        if cancellation is not None and cancellation.is_set():
            raise ResearchFetchCancelled("Research cancelled during external fetch")

        if (
            result.provider_id
            != GOVERNED_WEB_FETCH_PROVIDER_ID
        ):
            raise RuntimeError(
                "Governed Web provider "
                "identity mismatch."
            )

        output = result.output

        if not isinstance(
            output,
            GovernedWebFetchResult,
        ):
            raise TypeError(
                "Governed Web FETCH returned "
                "an invalid result."
            )

        now = (
            datetime.now(
                timezone.utc
            )
            .isoformat()
        )

        source = ResearchSource(
            output.final_url,
            label="Governed Web source",
        )

        provenance = SourceProvenance(
            source_id=source.source_id,
            retrieved_at=now,
            digest=(
                ContentDigest.from_bytes(
                    output.body
                )
            ),
        )

        artifact = ExternalArtifact(
            source=source,
            provenance=provenance,
            artifact_kind="DOCUMENT",
            media_type=(
                output.content_type
                or "application/octet-stream"
            ),
        )

        claim = ResearchClaim(
            statement=(
                "RX observed a governed "
                "Web response."
            ),
            artifact_ids=(
                artifact.artifact_id,
            ),
            created_at=now,
        )

        evidence = (
            ResearchEvidenceBridge
            .to_evidence(
                task_id=mission.task_id,
                claim=claim,
                artifacts=[
                    artifact
                ],
            )
        )

        # Final cooperative checkpoint before durable evidence publication.
        # A simultaneous later cancellation may still be too late; the
        # Gateway also checks before mission TX authorization.
        if cancellation is not None and cancellation.is_set():
            raise ResearchFetchCancelled("Research cancelled before evidence publication")

        # Durable first: a process interruption
        # after this point remains recoverable
        # through hydration on restart.
        self.research_evidence.record(
            evidence
        )

        self.kernel.add_evidence(
            evidence
        )

        self.events.append(
            RuntimeEvent(
                mission.task_id,
                "RESEARCH_EVIDENCE_RECORDED",
                "RX",
                {
                    "evidence_id": (
                        evidence.evidence_id
                    ),
                    "source_ref": (
                        evidence.source_ref
                    ),
                    "status": output.status,
                    "body_sha256": (
                        output.body_sha256
                    ),
                    "body_size": (
                        output.body_size
                    ),
                },
            )
        )

        return evidence

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
