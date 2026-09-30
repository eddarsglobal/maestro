import unittest

from maestro.enums import CouncilId, DagNodeState
from maestro.orchestration.dag import DagCycleError, DagEngine, DagNode


class DagTests(unittest.TestCase):
    def test_dependency_order_and_readiness(self):
        dag = DagEngine()
        dag.add_node(DagNode("pm", CouncilId.PM, "DEFINE"))
        dag.add_node(DagNode("it", CouncilId.IT, "IMPLEMENT", depends_on={"pm"}))
        dag.add_node(DagNode("sc", CouncilId.SC, "AUDIT", depends_on={"it"}))

        self.assertEqual([n.node_id for n in dag.ready_nodes()], ["pm"])
        dag.start("pm", CouncilId.EX)
        dag.succeed("pm", {"scope": "approved"})
        self.assertEqual([n.node_id for n in dag.ready_nodes()], ["it"])

    def test_only_ex_starts_nodes(self):
        dag = DagEngine()
        dag.add_node(DagNode("it", CouncilId.IT, "IMPLEMENT"))
        with self.assertRaises(PermissionError):
            dag.start("it", CouncilId.IT)

    def test_cycle_rejected(self):
        dag = DagEngine()
        dag.add_node(DagNode("a", CouncilId.IT, "A"))
        dag.add_node(DagNode("b", CouncilId.SC, "B"))
        dag.add_dependency("b", "a")
        with self.assertRaises(DagCycleError):
            dag.add_dependency("a", "b")

    def test_failure_blocks_descendant(self):
        dag = DagEngine()
        dag.add_node(DagNode("it", CouncilId.IT, "IMPLEMENT"))
        dag.add_node(DagNode("sc", CouncilId.SC, "AUDIT", depends_on={"it"}))
        dag.start("it", CouncilId.EX)
        dag.fail("it", "boom")
        dag.ready_nodes()
        self.assertEqual(dag.nodes["sc"].state, DagNodeState.BLOCKED)


if __name__ == "__main__":
    unittest.main()
