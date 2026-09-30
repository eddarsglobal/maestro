import tempfile
import unittest

from maestro import MaestroKernel
from maestro.os.checkpoint_manager import AutomaticCheckpointManager, CheckpointPolicy


class AutoCheckpointTests(unittest.TestCase):
    def test_event_threshold(self):
        with tempfile.TemporaryDirectory() as td:
            kernel = MaestroKernel()
            mission = kernel.create_mission("x")
            mgr = AutomaticCheckpointManager(
                kernel, td, CheckpointPolicy(every_events=2, on_states=frozenset())
            )
            self.assertIsNone(mgr.maybe_checkpoint(mission, 1))
            self.assertIsNotNone(mgr.maybe_checkpoint(mission, 2))


if __name__ == "__main__":
    unittest.main()
