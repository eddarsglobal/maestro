import tempfile
import unittest

from maestro.autonomous.runtime import AutonomousRuntime
from maestro.autonomous.workers import WorkerSpec
from maestro.autonomous.executor import ExecutionResult
from maestro.enums import CouncilId
from maestro.orchestration.dag import DagNode


class FakeIT:
    council = CouncilId.IT
    def execute(self, request):
        return ExecutionResult(request.task_id, request.council, True, {"artifact": "ok.py"})


class AutonomousRuntimeTests(unittest.TestCase):
    def test_end_to_end_one_work_item(self):
        with tempfile.TemporaryDirectory() as td:
            rt = AutonomousRuntime(td)
            rt.executor.register(FakeIT())
            rt.register_worker(WorkerSpec("W1", {"IT"}))

            m = rt.create_mission("build")
            rt.kernel.add_dag_node(m, DagNode("it", CouncilId.IT, "IMPLEMENT"))
            work_ids = rt.enqueue_dag_ready(m)
            self.assertEqual(len(work_ids), 1)

            result = rt.run_one("W1")
            self.assertTrue(result.success)
            self.assertTrue(rt.kernel.dag(m).nodes["it"].output["artifact"] == "ok.py")
            self.assertEqual(len(rt.events.for_task(m.task_id)), 2)


if __name__ == "__main__":
    unittest.main()
