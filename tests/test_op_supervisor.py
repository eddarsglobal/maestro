import unittest

from maestro import MaestroKernel
from maestro.enums import CouncilId
from maestro.os.op_supervisor import LiveOPSupervisor, OPSignal


class OPSupervisorTests(unittest.TestCase):
    def test_third_same_failure_recommends_breakout(self):
        kernel = MaestroKernel()
        mission = kernel.create_mission("x")
        op = LiveOPSupervisor(kernel)

        decision = None
        for _ in range(3):
            decision = op.observe_failure(
                mission,
                worker=CouncilId.IT,
                criterion_id="AC-1",
                failure_mode="same",
                strategy="same",
            )
        self.assertEqual(decision.signal, OPSignal.BREAKOUT_RECOMMENDED)


if __name__ == "__main__":
    unittest.main()
