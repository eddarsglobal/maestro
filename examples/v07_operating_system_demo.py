import asyncio
import tempfile

from maestro import MaestroKernel
from maestro.autonomous.executor import CouncilExecutor, ExecutionRequest, ExecutionResult
from maestro.enums import CouncilId
from maestro.os.async_runtime import AsyncCouncilRunner
from maestro.os.council_lifecycle import CouncilLifecycleManager
from maestro.os.leases import LeaseManager
from maestro.os.op_supervisor import LiveOPSupervisor
from maestro.os.skill_dag import SkillDagCompiler
from maestro.adaptive.skills import SkillCandidate


class ITAdapter:
    council = CouncilId.IT
    def execute(self, request):
        return ExecutionResult(request.task_id, request.council, True, {"action": request.action})


async def main():
    executor = CouncilExecutor()
    executor.register(ITAdapter())
    runner = AsyncCouncilRunner(executor, max_concurrency=2)

    requests = [
        ExecutionRequest("TASK-A", CouncilId.IT, "IMPLEMENT-A", {}),
        ExecutionRequest("TASK-B", CouncilId.IT, "IMPLEMENT-B", {}),
    ]
    results = await runner.run_many(requests)
    print("ASYNC RESULTS:", [x.result.output for x in results])

    leases = LeaseManager()
    lease = leases.acquire("WORK-1", "worker-it", lease_seconds=30)
    leases.heartbeat("WORK-1", "worker-it")
    print("LEASE ACTIVE:", lease.state.value)

    lifecycle = CouncilLifecycleManager()
    lifecycle.activate("IT")
    lifecycle.release_worker("IT")
    lifecycle.cool("IT")
    print("IT TEMP:", lifecycle.snapshot()["IT"]["temperature"])

    kernel = MaestroKernel()
    mission = kernel.create_mission("repair recurring auth failure")
    op = LiveOPSupervisor(kernel)
    signal = None
    for _ in range(3):
        signal = op.observe_failure(
            mission,
            worker=CouncilId.IT,
            criterion_id="AC-AUTH",
            failure_mode="authorization still bypassed",
            strategy="patch same condition",
        )
    print("OP SIGNAL:", signal.signal.value)

    skill = SkillCandidate(
        "PAYMENT_SKILL", "PAYMENT",
        ["PM", "IT", "SC"],
        ["DEFINE", "IMPLEMENT", "AUDIT"],
        ["integration_test"],
        ["EXP-1", "EXP-2", "EXP-3"],
    )
    dag = SkillDagCompiler().compile(skill)
    print("SKILL DAG:", dag.topological_order())

asyncio.run(main())
