from pathlib import Path
import tempfile

from maestro import MaestroKernel
from maestro.enums import CouncilId, EvidenceKind, MissionState
from maestro.models import Evidence
from maestro.orchestration.dag import DagNode
from maestro.orchestration.retry_ledger import RetryAttempt


kernel = MaestroKernel()
mission = kernel.create_mission(
    "Build a secure upload capability",
    scope="Product definition + implementation + security audit",
    requested_output="Auditable implementation",
)
mission.acceptance_criteria = [
    "AC-01 Product behavior is explicit",
    "AC-02 Upload implementation works",
    "AC-03 Security controls are validated",
]

kernel.add_dag_node(mission, DagNode("pm", CouncilId.PM, "DEFINE_PRODUCT", ["AC-01"]))
kernel.add_dag_node(
    mission,
    DagNode("it", CouncilId.IT, "IMPLEMENT", ["AC-02"], depends_on={"pm"}),
)
kernel.add_dag_node(
    mission,
    DagNode("sc", CouncilId.SC, "AUDIT_SECURITY", ["AC-03"], depends_on={"it"}),
)

print("READY:", [node.node_id for node in kernel.ready_dag_nodes(mission)])

kernel.start_dag_node(mission, "pm")
kernel.succeed_dag_node(mission, "pm", {"product_scope": "Upload PDF only, max 20 MB"})

print("READY:", [node.node_id for node in kernel.ready_dag_nodes(mission)])

context = kernel.compile_context(mission, "it")
print("IT CONTEXT:", context.to_dict())

kernel.start_dag_node(mission, "it")
kernel.add_evidence(
    Evidence(
        task_id=mission.task_id,
        council=CouncilId.IT,
        kind=EvidenceKind.TEST_RESULT,
        claim="Upload tests executed",
        payload={"passed": 12, "failed": 0},
    )
)
kernel.succeed_dag_node(mission, "it", {"artifact": "upload_endpoint.py"})

print("READY:", [node.node_id for node in kernel.ready_dag_nodes(mission)])

# Demonstrate OP's same-loop detection.
for _ in range(3):
    assessment = kernel.record_retry(
        mission,
        RetryAttempt(
            mission.task_id,
            CouncilId.IT,
            "AC-03",
            "Authorization still bypassed",
            "Patch the same controller condition",
        ),
    )
print("BREAKOUT RECOMMENDED:", assessment.breakout_recommended)

with tempfile.TemporaryDirectory() as td:
    checkpoint = kernel.save_checkpoint(mission, td)
    print("CHECKPOINT:", checkpoint)
