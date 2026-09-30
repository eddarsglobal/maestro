import tempfile

from maestro.autonomous import AutonomousRuntime, WorkerSpec
from maestro.autonomous.executor import ExecutionResult
from maestro.enums import CouncilId
from maestro.orchestration.dag import DagNode


class PMAdapter:
    council = CouncilId.PM
    def execute(self, request):
        return ExecutionResult(
            request.task_id,
            request.council,
            True,
            {"scope": "Upload PDF, max 20 MB"},
        )


class ITAdapter:
    council = CouncilId.IT
    def execute(self, request):
        return ExecutionResult(
            request.task_id,
            request.council,
            True,
            {"artifact": "upload_endpoint.py", "tests": 12},
        )


with tempfile.TemporaryDirectory() as td:
    rt = AutonomousRuntime(td)

    rt.executor.register(PMAdapter())
    rt.executor.register(ITAdapter())

    rt.register_worker(WorkerSpec("worker-product", {"PM"}))
    rt.register_worker(WorkerSpec("worker-code", {"IT"}))

    mission = rt.create_mission(
        "Build secure upload",
        scope="product + implementation",
        requested_output="auditable implementation",
    )
    mission.acceptance_criteria = [
        "AC-01 product scope explicit",
        "AC-02 implementation works",
    ]

    rt.kernel.add_dag_node(mission, DagNode("pm", CouncilId.PM, "DEFINE", ["AC-01"]))
    rt.kernel.add_dag_node(
        mission,
        DagNode("it", CouncilId.IT, "IMPLEMENT", ["AC-02"], depends_on={"pm"}),
    )

    print("QUEUE 1:", rt.enqueue_dag_ready(mission))
    print("PM RESULT:", rt.run_one("worker-product").output)

    print("QUEUE 2:", rt.enqueue_dag_ready(mission))
    print("IT RESULT:", rt.run_one("worker-code").output)

    print("DAG COMPLETE:", rt.kernel.dag(mission).complete())
    print("EVENTS:", len(rt.events.for_task(mission.task_id)))

    recovered = rt.recovery.recover(mission.task_id)
    print("RECOVERED:", recovered.mission.task_id == mission.task_id)
