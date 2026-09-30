from __future__ import annotations

from pathlib import Path

from maestro.autonomous.runtime import AutonomousRuntime
from maestro.autonomous.workers import WorkerSpec
from maestro.autonomous.executor import ExecutionResult

from .event_sourcing import EventSourcedMissionStore
from .leases import LeaseManager
from .checkpoint_manager import AutomaticCheckpointManager
from .op_supervisor import LiveOPSupervisor
from .academy_feedback import OnlineAcademyFeedback
from .council_lifecycle import CouncilLifecycleManager


class MaestroOperatingSystem:
    """
    v0.7 composition root.

    This remains a microkernel: subsystems are separate and replaceable.
    """

    def __init__(self, runtime_dir: str | Path):
        self.runtime_dir = Path(runtime_dir)
        self.runtime = AutonomousRuntime(self.runtime_dir / "runtime")

        self.event_sourcing = EventSourcedMissionStore(self.runtime.events)
        self.leases = LeaseManager()
        self.checkpoints = AutomaticCheckpointManager(
            self.runtime.kernel,
            self.runtime_dir / "checkpoints",
        )
        self.op = LiveOPSupervisor(self.runtime.kernel)
        self.academy_feedback = OnlineAcademyFeedback()
        self.council_lifecycle = CouncilLifecycleManager()

    def register_worker(self, worker: WorkerSpec) -> None:
        self.runtime.register_worker(worker)

    def run_one(self, worker_id: str) -> ExecutionResult | None:
        worker = self.runtime.workers.get(worker_id)
        item = self.runtime.scheduler.lease_next(worker_id, worker.allowed_councils)
        if item is None:
            return None

        lease = self.leases.acquire(item.work_id, worker_id, lease_seconds=30)
        self.council_lifecycle.activate(item.council)

        # Runtime.run_one expects to lease itself, so execute the equivalent path
        # by temporarily restoring queue state is avoided here. For v0.7 the OS
        # delegates to runtime only when using its own scheduler loop; this method
        # is used for lifecycle/lease tests and explicit OS-managed work.
        # Mark the item back as QUEUED then let runtime consume it.
        from maestro.autonomous.scheduler import WorkStatus
        item.status = WorkStatus.QUEUED
        item.leased_by = None
        self.runtime.scheduler._heap.append((item.priority, -1, item.work_id))
        import heapq
        heapq.heapify(self.runtime.scheduler._heap)

        try:
            result = self.runtime.run_one(worker_id)
            return result
        finally:
            try:
                self.leases.release(item.work_id, worker_id)
            except Exception:
                pass
            self.council_lifecycle.release_worker(item.council)
