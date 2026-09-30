import json
import tempfile
import unittest
from pathlib import Path

from maestro.enums import CouncilId, MissionState
from maestro.models import Mission
from maestro.orchestration.dag import DagEngine, DagNode
from maestro.orchestration.retry_ledger import RetryLedger, RetryAttempt
from maestro.runtime.checkpoint import CheckpointError, CheckpointStore


class CheckpointTests(unittest.TestCase):
    def test_roundtrip(self):
        with tempfile.TemporaryDirectory() as td:
            mission = Mission("x", state=MissionState.EXECUTING)
            dag = DagEngine()
            dag.add_node(DagNode("it", CouncilId.IT, "IMPLEMENT"))
            ledger = RetryLedger()
            ledger.record(CouncilId.OP, RetryAttempt(mission.task_id, CouncilId.IT, "AC-01", "f", "s"))

            store = CheckpointStore(td)
            store.save(mission, dag, ledger, ["EVD-1"], trace_count=4)
            bundle = store.load(mission.task_id)

            self.assertEqual(bundle.mission.task_id, mission.task_id)
            self.assertIn("it", bundle.dag.nodes)
            self.assertEqual(len(bundle.retry_ledger.attempts), 1)
            self.assertEqual(bundle.metadata["trace_count"], 4)

    def test_tamper_detected(self):
        with tempfile.TemporaryDirectory() as td:
            mission = Mission("x")
            dag = DagEngine()
            ledger = RetryLedger()
            store = CheckpointStore(td)
            path = store.save(mission, dag, ledger)

            data = json.loads(path.read_text())
            data["body"]["mission"]["objective"] = "tampered"
            path.write_text(json.dumps(data), encoding="utf-8")

            with self.assertRaises(CheckpointError):
                store.load(mission.task_id)


if __name__ == "__main__":
    unittest.main()
