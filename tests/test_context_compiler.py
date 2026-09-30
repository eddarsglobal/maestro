import unittest

from maestro.enums import CouncilId, EvidenceKind, DagNodeState
from maestro.models import Evidence, Mission
from maestro.orchestration.dag import DagEngine, DagNode
from maestro.runtime.context_compiler import ContextCompiler


class ContextCompilerTests(unittest.TestCase):
    def test_compiles_least_context(self):
        mission = Mission("Build secure API", scope="API")
        mission.acceptance_criteria = ["AC-01 works", "AC-02 secure"]

        dag = DagEngine()
        dag.add_node(DagNode("pm", CouncilId.PM, "DEFINE", state=DagNodeState.SUCCEEDED, output={"scope": "ok"}))
        dag.add_node(DagNode("it", CouncilId.IT, "IMPLEMENT", criteria_ids=["AC-01"], depends_on={"pm"}))

        evidence = [
            Evidence(mission.task_id, CouncilId.PM, EvidenceKind.OTHER, "Scope approved", {"ok": True}),
            Evidence(mission.task_id, CouncilId.MK, EvidenceKind.OTHER, "Unrelated market note", {"x": 1}),
        ]

        ctx = ContextCompiler().compile(mission, dag.nodes["it"], dag, evidence)
        self.assertEqual(ctx.council, CouncilId.IT)
        self.assertEqual(ctx.acceptance_criteria, ["AC-01 works"])
        self.assertIn("pm", ctx.dependency_outputs)
        self.assertEqual(len(ctx.evidence), 1)
        self.assertEqual(ctx.evidence[0]["council"], "PM")


if __name__ == "__main__":
    unittest.main()
