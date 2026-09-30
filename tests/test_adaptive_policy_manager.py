import unittest

from maestro.adaptive.models import AdaptivePolicy, PolicyKind, PolicyStatus, PromotionEvidence
from maestro.adaptive.policy_manager import AdaptivePolicyManager, PolicyActivationDenied


class AdaptivePolicyManagerTests(unittest.TestCase):
    def _policy(self, version, parent=None):
        return AdaptivePolicy(
            kind=PolicyKind.ROUTING,
            version=version,
            parent_policy_id=parent,
            description=f"v{version}",
            parameters={"rules": {}},
        )

    def test_candidate_cannot_activate_without_shadow(self):
        manager = AdaptivePolicyManager()
        p = self._policy(1)
        manager.register(p)
        ev = PromotionEvidence(0.9, 0.8, 0, 0.95, 100, True)
        with self.assertRaises(PolicyActivationDenied):
            manager.activate(p.policy_id, evidence=ev, ay_validated=True, ex_authorized=True)

    def test_governed_activation_and_rollback(self):
        manager = AdaptivePolicyManager()
        p1 = self._policy(1)
        manager.bootstrap_active(p1)

        p2 = self._policy(2, parent=p1.policy_id)
        manager.register(p2)
        manager.set_shadow(p2.policy_id)
        ev = PromotionEvidence(0.95, 0.80, 0, 0.98, 100, True)

        manager.activate(
            p2.policy_id,
            evidence=ev,
            ay_validated=True,
            ex_authorized=True,
        )
        self.assertEqual(manager.active(PolicyKind.ROUTING).policy_id, p2.policy_id)

        manager.rollback(
            PolicyKind.ROUTING,
            ex_authorized=True,
            ay_acknowledged=True,
            reason="runtime regression",
        )
        self.assertEqual(manager.active(PolicyKind.ROUTING).policy_id, p1.policy_id)

    def test_regression_blocks_activation(self):
        manager = AdaptivePolicyManager()
        p = self._policy(1)
        manager.register(p)
        manager.set_shadow(p.policy_id)
        ev = PromotionEvidence(0.95, 0.80, 1, 0.98, 100, True)
        with self.assertRaises(PolicyActivationDenied):
            manager.activate(p.policy_id, evidence=ev, ay_validated=True, ex_authorized=True)


if __name__ == "__main__":
    unittest.main()
