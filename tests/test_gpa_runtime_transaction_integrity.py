import json
import tempfile
import unittest
from pathlib import Path

from maestro.governed_activation import (
    RuntimeCommitJournal,
    RuntimeCommitOperation,
    RuntimeCommitRecord,
    RuntimeCommitState,
)


def record(transaction_id="RTX-INTEGRITY-1"):
    return RuntimeCommitRecord(
        contract_id="GPA-INTEGRITY-1",
        operation=RuntimeCommitOperation.ACTIVATE,
        kind="MODEL_SELECTION",
        before_active_policy_id="POL-BEFORE",
        after_active_policy_id="POL-AFTER",
        gpa_before_state="CANARY_VERIFIED",
        gpa_after_state="ACTIVE",
        governance={
            "nested": {
                "refs": ["EVD-1", "EVD-2"],
            }
        },
        transaction_id=transaction_id,
        created_at="2026-09-30T16:40:00+00:00",
    )


class RuntimeTransactionJournalIntegrityTests(unittest.TestCase):

    def test_record_event_id_is_deterministic_and_tamper_evident(self):
        first = record()
        second = record()

        self.assertEqual(first.event_id, second.event_id)
        first.assert_integrity()

        payload = first.to_dict()
        payload["after_active_policy_id"] = "POL-TAMPERED"

        with self.assertRaises(ValueError):
            RuntimeCommitRecord.from_dict(payload)

    def test_governance_payload_is_deeply_immutable(self):
        row = record()

        with self.assertRaises(TypeError):
            row.governance["nested"] = {}

        with self.assertRaises(TypeError):
            row.governance["nested"]["refs"] = []

        with self.assertRaises(AttributeError):
            row.governance["nested"]["refs"].append("EVD-3")

        payload = row.to_dict()
        self.assertEqual(
            payload["governance"]["nested"]["refs"],
            ["EVD-1", "EVD-2"],
        )

    def test_journal_events_are_hash_chained_and_survive_restart(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "runtime_transactions.jsonl"
            journal = RuntimeCommitJournal(path)

            prepared = journal.append(record())
            committed = journal.append(
                prepared.advanced(
                    RuntimeCommitState.MANAGER_COMMITTED
                )
            )
            final = journal.append(
                committed.advanced(
                    RuntimeCommitState.GPA_COMMITTED
                )
            )

            self.assertIsNone(prepared.previous_event_id)
            self.assertEqual(
                committed.previous_event_id,
                prepared.event_id,
            )
            self.assertEqual(
                final.previous_event_id,
                committed.event_id,
            )

            restarted = RuntimeCommitJournal(path)
            self.assertEqual(
                [row.event_id for row in restarted._events],
                [
                    prepared.event_id,
                    committed.event_id,
                    final.event_id,
                ],
            )

    def test_persisted_field_tampering_is_rejected_on_restart(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "runtime_transactions.jsonl"
            journal = RuntimeCommitJournal(path)

            first = journal.append(record())
            journal.append(
                first.advanced(
                    RuntimeCommitState.MANAGER_COMMITTED
                )
            )

            lines = path.read_text(
                encoding="utf-8"
            ).splitlines()

            payload = json.loads(lines[0])
            payload["before_active_policy_id"] = "POL-CORRUPTED"
            lines[0] = json.dumps(
                payload,
                sort_keys=True,
            )

            path.write_text(
                "\n".join(lines) + "\n",
                encoding="utf-8",
            )

            with self.assertRaises(ValueError):
                RuntimeCommitJournal(path)

    def test_event_deletion_breaks_chain(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "runtime_transactions.jsonl"
            journal = RuntimeCommitJournal(path)

            first = journal.append(record())
            second = journal.append(
                first.advanced(
                    RuntimeCommitState.MANAGER_COMMITTED
                )
            )
            journal.append(
                second.advanced(
                    RuntimeCommitState.GPA_COMMITTED
                )
            )

            lines = path.read_text(
                encoding="utf-8"
            ).splitlines()

            path.write_text(
                lines[0] + "\n" + lines[2] + "\n",
                encoding="utf-8",
            )

            with self.assertRaises(ValueError):
                RuntimeCommitJournal(path)


if __name__ == "__main__":
    unittest.main()
