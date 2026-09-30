import unittest

from maestro.autonomous.workers import WorkerRegistry, WorkerSpec


class WorkerTests(unittest.TestCase):
    def test_available_for_council(self):
        r = WorkerRegistry()
        r.register(WorkerSpec("W1", {"IT", "SC"}))
        r.register(WorkerSpec("W2", {"CM"}))
        self.assertEqual([w.worker_id for w in r.available_for("SC")], ["W1"])


if __name__ == "__main__":
    unittest.main()
