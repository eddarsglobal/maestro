import tempfile
import unittest
from pathlib import Path

from maestro.autonomous.event_store import EventStore, RuntimeEvent
from maestro.os.event_sourcing import EventSourcedMissionStore


class EventSourcingTests(unittest.TestCase):
    def test_projection(self):
        with tempfile.TemporaryDirectory() as td:
            events = EventStore(Path(td) / "events.jsonl")
            events.append(RuntimeEvent("T1", "MISSION_CREATED", "MAESTRO", {"objective": "x"}))
            events.append(RuntimeEvent("T1", "WORK_SUCCEEDED", "IT", {}))
            events.append(RuntimeEvent("T1", "WORK_FAILED", "SC", {}))
            p = EventSourcedMissionStore(events).project("T1")
            self.assertEqual(p.event_count, 3)
            self.assertEqual(p.completed_work, 1)
            self.assertEqual(p.failed_work, 1)
            self.assertEqual(p.metadata["objective"], "x")


if __name__ == "__main__":
    unittest.main()
