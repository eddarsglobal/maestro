import tempfile
import unittest

from maestro import MaestroKernel
from maestro.enums import CouncilId, MissionState
from maestro.orchestration.dag import DagNode
from maestro.orchestration.retry_ledger import RetryAttempt


class KernelV02Tests(unittest.TestCase):
    def test_kernel_has_18_councils(self):
        self.assertEqual(MaestroKernel().council_count, 18)

    def test_checkpoint_resume_through_kernel(self):
        kernel = MaestroKernel()
        mission = kernel.create_mission("x")
        kernel.add_dag_node(mission, DagNode("it", CouncilId.IT, "IMPLEMENT"))
        kernel.move(mission, MissionState.ANALYSIS)
        kernel.record_retry(
            mission,
            RetryAttempt(mission.task_id, CouncilId.IT, "AC-01", "Failure", "Strategy"),
        )

        with tempfile.TemporaryDirectory() as td:
            kernel.save_checkpoint(mission, td)
            kernel2 = MaestroKernel()
            resumed = kernel2.resume_checkpoint(mission.task_id, td)
            self.assertEqual(resumed.state, MissionState.ANALYSIS)
            self.assertIn("it", kernel2.dag(resumed).nodes)
            self.assertEqual(len(kernel2.retry_ledgers[mission.task_id].attempts), 1)


if __name__ == "__main__":
    unittest.main()
