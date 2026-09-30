import unittest
from datetime import timedelta

from maestro.os.leases import LeaseManager, LeaseState, utc_now


class LeaseTests(unittest.TestCase):
    def test_heartbeat_and_release(self):
        m = LeaseManager()
        lease = m.acquire("W1", "worker", lease_seconds=30)
        m.heartbeat("W1", "worker")
        m.release("W1", "worker")
        self.assertEqual(lease.state, LeaseState.RELEASED)

    def test_stale_lease_expires(self):
        m = LeaseManager()
        lease = m.acquire("W1", "worker", lease_seconds=1)
        lease.heartbeat_at = utc_now() - timedelta(seconds=5)
        expired = m.expire_stale()
        self.assertEqual(len(expired), 1)
        self.assertEqual(lease.state, LeaseState.EXPIRED)


if __name__ == "__main__":
    unittest.main()
