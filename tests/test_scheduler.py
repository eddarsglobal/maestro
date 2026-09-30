import unittest

from maestro.autonomous.scheduler import RuntimeScheduler, WorkItem, WorkStatus


class SchedulerTests(unittest.TestCase):
    def test_leases_only_allowed_council(self):
        s = RuntimeScheduler()
        s.enqueue(WorkItem("T1", "SC", "AUDIT", priority=1))
        s.enqueue(WorkItem("T1", "IT", "CODE", priority=2))
        item = s.lease_next("W1", {"IT"})
        self.assertEqual(item.council, "IT")
        self.assertEqual(item.status, WorkStatus.LEASED)

    def test_fail_requeue(self):
        s = RuntimeScheduler()
        item = WorkItem("T1", "IT", "CODE")
        s.enqueue(item)
        s.lease_next("W1", {"IT"})
        s.fail(item.work_id)
        s.requeue_failed(item.work_id)
        self.assertEqual(s.snapshot()[item.work_id]["status"], "QUEUED")


if __name__ == "__main__":
    unittest.main()
