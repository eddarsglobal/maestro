import tempfile
import unittest
from pathlib import Path

from maestro.governed_activation import (
    ActivationContract,
    ActivationLedger,
    ActivationSnapshot,
    ActivationState,
    CanaryEvidence,
)


class GPADeepImmutabilityTests(unittest.TestCase):

    def contract(self):
        return ActivationContract(
            candidate_id="OGA-DEEP-IMMUTABLE",
            task_family="DIRECT",
            policy_kind="MODEL_SELECTION",
            policy_ref="POL-CANDIDATE",
            baseline_ref="POL-BASELINE",
            rollback_ref="POL-BASELINE",
            metadata={
                "nested": {
                    "route": ["r1", "r2"],
                    "limits": {"samples": 10},
                }
            },
        )

    def test_contract_metadata_is_deeply_immutable(self):
        contract = self.contract()
        original_id = contract.contract_id

        with self.assertRaises(TypeError):
            contract.metadata["nested"] = {}

        with self.assertRaises(TypeError):
            contract.metadata["nested"]["limits"]["samples"] = 99

        with self.assertRaises(AttributeError):
            contract.metadata["nested"]["route"].append("r3")

        self.assertEqual(contract.contract_id, original_id)
        contract.assert_integrity()

    def test_contract_roundtrip_preserves_id_and_plain_json_shape(self):
        contract = self.contract()
        payload = contract.to_dict()

        self.assertIsInstance(payload["metadata"], dict)
        self.assertIsInstance(payload["metadata"]["nested"], dict)
        self.assertIsInstance(
            payload["metadata"]["nested"]["route"],
            list,
        )

        restored = ActivationContract.from_dict(payload)

        self.assertEqual(restored.contract_id, contract.contract_id)
        self.assertEqual(restored.to_dict(), payload)
        restored.assert_integrity()

    def test_canary_metadata_is_deeply_immutable(self):
        evidence = CanaryEvidence(
            success_rate=1.0,
            regression_count=0,
            observed_samples=5,
            evidence_refs=("EVD-1",),
            latency_budget_pass=True,
            metadata={
                "nested": {
                    "latencies": [10, 11],
                }
            },
        )

        with self.assertRaises(TypeError):
            evidence.metadata["nested"]["latencies"] = []

        with self.assertRaises(AttributeError):
            evidence.metadata["nested"]["latencies"].append(12)

        payload = evidence.to_dict()

        self.assertEqual(
            payload["metadata"]["nested"]["latencies"],
            [10, 11],
        )

        restored = CanaryEvidence.from_dict(payload)
        self.assertEqual(restored.to_dict(), payload)

    def test_ledger_roundtrip_keeps_deep_immutability(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "activation.jsonl"

            snapshot = ActivationSnapshot(
                contract=self.contract(),
                state=ActivationState.PROPOSED,
                canary_evidence=CanaryEvidence(
                    success_rate=1.0,
                    regression_count=0,
                    observed_samples=5,
                    evidence_refs=("EVD-LEDGER",),
                    metadata={
                        "nested": {
                            "source": ["canary", "runtime"],
                        }
                    },
                ),
            )

            ledger = ActivationLedger(path)
            ledger.checkpoint(snapshot)

            restarted = ActivationLedger(path)
            loaded = restarted.latest(snapshot.contract_id)

            self.assertIsNotNone(loaded)
            loaded.contract.assert_integrity()

            with self.assertRaises(TypeError):
                loaded.contract.metadata["nested"]["limits"]["samples"] = 3

            with self.assertRaises(AttributeError):
                loaded.canary_evidence.metadata[
                    "nested"
                ]["source"].append("tampered")


if __name__ == "__main__":
    unittest.main()
