import json
import tempfile
import unittest
from pathlib import Path

from maestro.adaptive import (
    AdaptiveController,
    AdaptivePolicy,
    PersistentAdaptivePolicyManager,
    PolicyKind,
    PolicyStatus,
    PromotionEvidence,
)


def evidence(candidate_id, replay=0.95, baseline=0.80):
    return PromotionEvidence(
        replay_score=replay,
        baseline_score=baseline,
        regression_count=0,
        shadow_success_rate=1.0,
        evaluation_samples=12,
        academy_recommended=True,
        learning_candidate_id=candidate_id,
    )


def policy(version, subject, candidate_id):
    return AdaptivePolicy(
        kind=PolicyKind.MODEL_SELECTION,
        version=version,
        description=f"policy {version}",
        parameters={
            "subject_id": subject,
            "source_candidate_id": candidate_id,
        },
    )


class PersistentAdaptivePolicyManagerTests(unittest.TestCase):

    def test_shadow_policy_survives_restart(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "adaptive_state.json"

            manager = PersistentAdaptivePolicyManager(path)
            controller = AdaptiveController(manager)

            candidate = policy(1, "candidate", "OGA-C1")
            controller.stage_candidate(candidate)

            restarted = PersistentAdaptivePolicyManager(path)
            restored = restarted.policy(candidate.policy_id)

            self.assertEqual(
                restored.status,
                PolicyStatus.SHADOW,
            )
            self.assertEqual(
                restored.parameters["subject_id"],
                "candidate",
            )
            self.assertIsNone(
                restarted.active(PolicyKind.MODEL_SELECTION)
            )

    def test_activation_pointer_and_history_survive_restart(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "adaptive_state.json"

            manager = PersistentAdaptivePolicyManager(path)

            baseline = policy(1, "baseline", "BASELINE")
            manager.bootstrap_active(baseline)

            candidate = policy(2, "candidate", "OGA-C2")
            AdaptiveController(manager).stage_candidate(candidate)

            manager.activate(
                candidate.policy_id,
                evidence=evidence("OGA-C2"),
                ay_validated=True,
                ex_authorized=True,
            )

            restarted = PersistentAdaptivePolicyManager(path)

            active = restarted.active(
                PolicyKind.MODEL_SELECTION
            )
            self.assertIsNotNone(active)
            self.assertEqual(
                active.policy_id,
                candidate.policy_id,
            )
            self.assertEqual(
                restarted.policy(baseline.policy_id).status,
                PolicyStatus.RETIRED,
            )

            history = restarted.history()
            self.assertEqual(
                [row.action for row in history],
                ["BOOTSTRAP", "ACTIVATE"],
            )
            self.assertEqual(
                history[-1].previous_policy_id,
                baseline.policy_id,
            )

    def test_rollback_survives_restart(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "adaptive_state.json"

            manager = PersistentAdaptivePolicyManager(path)

            baseline = policy(1, "baseline", "BASELINE")
            manager.bootstrap_active(baseline)

            candidate = policy(2, "candidate", "OGA-C3")
            AdaptiveController(manager).stage_candidate(candidate)

            manager.activate(
                candidate.policy_id,
                evidence=evidence("OGA-C3"),
                ay_validated=True,
                ex_authorized=True,
            )

            manager.rollback(
                PolicyKind.MODEL_SELECTION,
                ex_authorized=True,
                ay_acknowledged=True,
                reason="runtime degradation",
            )

            restarted = PersistentAdaptivePolicyManager(path)

            active = restarted.active(
                PolicyKind.MODEL_SELECTION
            )
            self.assertIsNotNone(active)
            self.assertEqual(
                active.policy_id,
                baseline.policy_id,
            )
            self.assertEqual(
                restarted.policy(candidate.policy_id).status,
                PolicyStatus.RETIRED,
            )
            self.assertEqual(
                restarted.history()[-1].action,
                "ROLLBACK",
            )

    def test_invalid_active_pointer_is_rejected_on_restart(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "adaptive_state.json"

            manager = PersistentAdaptivePolicyManager(path)
            baseline = policy(1, "baseline", "BASELINE")
            manager.bootstrap_active(baseline)

            payload = json.loads(
                path.read_text(encoding="utf-8")
            )
            payload["active"]["MODEL_SELECTION"] = "POL-MISSING"
            path.write_text(
                json.dumps(payload),
                encoding="utf-8",
            )

            with self.assertRaises(ValueError):
                PersistentAdaptivePolicyManager(path)


if __name__ == "__main__":
    unittest.main()
