import tempfile
import unittest

from maestro.adaptive.models import AdaptivePolicy, PolicyKind
from maestro.adaptive.store import AdaptivePolicyStore
from maestro.storage.object_store import BinaryObjectStore


class AdaptivePolicyStoreTests(unittest.TestCase):
    def test_policy_is_persisted_binary(self):
        with tempfile.TemporaryDirectory() as td:
            store = AdaptivePolicyStore(BinaryObjectStore(td))
            policy = AdaptivePolicy(PolicyKind.ROUTING, 1, "x", {"rules": {"A": ["IT"]}})
            ref = store.put(policy)
            raw = store.raw(policy.policy_id)
            self.assertEqual(raw["policy_id"], policy.policy_id)
            self.assertEqual(raw["kind"], "ROUTING")


if __name__ == "__main__":
    unittest.main()
