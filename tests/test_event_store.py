import tempfile
import unittest
from pathlib import Path

from maestro.autonomous.event_store import EventStore, RuntimeEvent


class EventStoreTests(unittest.TestCase):
    def test_append_and_filter(self):
        with tempfile.TemporaryDirectory() as td:
            store = EventStore(Path(td) / "events.jsonl")
            store.append(RuntimeEvent("T1", "A", "EX", {"x": 1}))
            store.append(RuntimeEvent("T2", "B", "AY", {}))
            store.append(RuntimeEvent("T1", "C", "IT", {}))
            self.assertEqual(len(store.all()), 3)
            self.assertEqual(len(store.for_task("T1")), 2)


if __name__ == "__main__":
    unittest.main()
