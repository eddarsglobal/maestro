import tempfile
import unittest

from maestro.autonomous.mission_store import MissionStore
from maestro.models import Mission


class MissionStoreTests(unittest.TestCase):
    def test_roundtrip(self):
        with tempfile.TemporaryDirectory() as td:
            store = MissionStore(td)
            m = Mission("persist me")
            store.save(m)
            loaded = store.load(m.task_id)
            self.assertEqual(loaded.task_id, m.task_id)
            self.assertEqual(loaded.objective, "persist me")


if __name__ == "__main__":
    unittest.main()
