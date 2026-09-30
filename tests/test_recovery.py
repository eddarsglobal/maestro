import tempfile
import unittest
from pathlib import Path

from maestro.autonomous.event_store import EventStore, RuntimeEvent
from maestro.autonomous.mission_store import MissionStore
from maestro.autonomous.recovery import RecoveryManager
from maestro.models import Mission


class RecoveryTests(unittest.TestCase):
    def test_fallback_to_mission_store(self):
        with tempfile.TemporaryDirectory() as td:
            missions = MissionStore(Path(td) / "missions")
            events = EventStore(Path(td) / "events.jsonl")
            m = Mission("recover")
            missions.save(m)
            events.append(RuntimeEvent(m.task_id, "X", "EX", {}))
            result = RecoveryManager(missions, events).recover(m.task_id)
            self.assertFalse(result.recovered_from_checkpoint)
            self.assertEqual(result.event_count, 1)
            self.assertEqual(result.mission.task_id, m.task_id)


if __name__ == "__main__":
    unittest.main()
