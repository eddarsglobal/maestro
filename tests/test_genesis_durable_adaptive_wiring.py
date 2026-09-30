import tempfile
import unittest
from pathlib import Path

from maestro import ProductionGenesisSystem
from maestro.adaptive import (
    AdaptiveController,
    PersistentAdaptivePolicyManager,
)
from maestro.governed_activation import (
    RuntimeCommitOperation,
    RuntimeCommitRecord,
    RuntimeCommitState,
    StrictGovernedPolicyActivation,
)


class GenesisDurableAdaptiveWiringTests(unittest.TestCase):

    def test_genesis_wires_persistent_manager_and_controller(self):
        with tempfile.TemporaryDirectory() as td:
            system = ProductionGenesisSystem(td)

            self.assertIsInstance(
                system.adaptive_policy_manager,
                PersistentAdaptivePolicyManager,
            )
            self.assertIsInstance(
                system.adaptive_controller,
                AdaptiveController,
            )
            self.assertIs(
                system.adaptive_controller.manager,
                system.adaptive_policy_manager,
            )
            self.assertEqual(
                system.adaptive_policy_manager.path,
                Path(td) / "adaptive" / "control_plane.json",
            )
            self.assertIsInstance(
                system.governed_activation,
                StrictGovernedPolicyActivation,
            )

    def test_start_runs_recovery_before_ready(self):
        with tempfile.TemporaryDirectory() as td:
            system = ProductionGenesisSystem(td)
            result = system.start()

            self.assertEqual(result["status"], "READY")
            self.assertEqual(
                result["runtime_recovery"],
                {
                    "processed": 0,
                    "committed": 0,
                    "aborted": 0,
                    "blocked": 0,
                },
            )

    def test_persistent_blocked_transaction_prevents_ready(self):
        with tempfile.TemporaryDirectory() as td:
            system = ProductionGenesisSystem(td)

            row = RuntimeCommitRecord(
                contract_id="GPA-TEST-BLOCKED",
                operation=RuntimeCommitOperation.ACTIVATE,
                kind="MODEL_SELECTION",
                before_active_policy_id="POL-BEFORE",
                after_active_policy_id="POL-AFTER",
                gpa_before_state="CANARY_VERIFIED",
                gpa_after_state="ACTIVE",
            ).advanced(
                RuntimeCommitState.BLOCKED,
                reason="intentional test conflict",
            )

            system.governed_activation.runtime_commit_journal.append(row)

            with self.assertRaises(RuntimeError):
                system.start()

    def test_blocked_projection_survives_restart(self):
        with tempfile.TemporaryDirectory() as td:
            first = ProductionGenesisSystem(td)

            row = RuntimeCommitRecord(
                contract_id="GPA-TEST-BLOCKED-RESTART",
                operation=RuntimeCommitOperation.ROLLBACK,
                kind="MODEL_SELECTION",
                before_active_policy_id="POL-ACTIVE",
                after_active_policy_id="POL-BASELINE",
                gpa_before_state="ACTIVE",
                gpa_after_state="ROLLED_BACK",
            ).advanced(
                RuntimeCommitState.BLOCKED,
                reason="persistent contradiction",
            )

            first.governed_activation.runtime_commit_journal.append(row)

            restarted = ProductionGenesisSystem(td)

            blocked = (
                restarted.governed_activation
                .runtime_commit_journal
                .blocked()
            )

            self.assertEqual(len(blocked), 1)
            self.assertEqual(
                blocked[0].transaction_id,
                row.transaction_id,
            )

            with self.assertRaises(RuntimeError):
                restarted.start()


if __name__ == "__main__":
    unittest.main()
