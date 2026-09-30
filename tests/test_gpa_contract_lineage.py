import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from maestro.governed_activation import GovernedPolicyActivation


def candidate():
    return SimpleNamespace(
        candidate_id="OGA-LINEAGE-1",
        task_family="DIRECT",
        status="PROMOTION_READY",
        proposed_change={"authority_change": False},
    )


def propose(engine, **overrides):
    values = {
        "policy_kind": "MODEL_SELECTION",
        "policy_ref": "POL-CANDIDATE",
        "baseline_ref": "POL-BASELINE",
        "rollback_ref": "POL-BASELINE",
        "canary_fraction": 0.10,
        "metadata": {"source": "test"},
    }
    values.update(overrides)

    return engine.propose(
        candidate(),
        **values,
    )


class GPAContractLineageTests(unittest.TestCase):

    def test_identical_reproposal_is_idempotent(self):
        engine = GovernedPolicyActivation()

        first = propose(engine)
        second = propose(engine)

        self.assertEqual(first.contract_id, second.contract_id)
        self.assertEqual(len(engine.ledger.events()), 1)
        self.assertEqual(
            len(engine.ledger.by_candidate("OGA-LINEAGE-1")),
            1,
        )

    def test_same_candidate_cannot_change_policy_ref(self):
        engine = GovernedPolicyActivation()
        first = propose(engine)

        with self.assertRaises(PermissionError):
            propose(
                engine,
                policy_ref="POL-CONFLICTING",
            )

        rows = engine.ledger.by_candidate("OGA-LINEAGE-1")
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0].contract_id, first.contract_id)

    def test_same_candidate_cannot_change_contract_parameters(self):
        engine = GovernedPolicyActivation()
        propose(engine)

        with self.assertRaises(PermissionError):
            propose(
                engine,
                canary_fraction=0.25,
            )

        with self.assertRaises(PermissionError):
            propose(
                engine,
                metadata={"source": "tampered"},
            )

    def test_lineage_conflict_is_rejected_after_restart(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "activation.jsonl"

            first_engine = GovernedPolicyActivation(path)
            first = propose(first_engine)

            restarted = GovernedPolicyActivation(path)

            same = propose(restarted)
            self.assertEqual(same.contract_id, first.contract_id)

            with self.assertRaises(PermissionError):
                propose(
                    restarted,
                    rollback_ref="POL-OTHER-BASELINE",
                )

            self.assertEqual(
                len(
                    restarted.ledger.by_candidate(
                        "OGA-LINEAGE-1"
                    )
                ),
                1,
            )


if __name__ == "__main__":
    unittest.main()
