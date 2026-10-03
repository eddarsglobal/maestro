import sqlite3
import tempfile
import unittest
from concurrent.futures import (
    ThreadPoolExecutor,
)
from pathlib import Path

from maestro.enums import (
    CouncilId,
    EvidenceKind,
)
from maestro.research import (
    ContentDigest,
    ExternalArtifact,
    ResearchClaim,
    ResearchEvidenceBridge,
    ResearchEvidenceConflictError,
    ResearchEvidenceCorruptionError,
    ResearchEvidenceStore,
    ResearchSource,
    SourceProvenance,
)


NOW = "2026-10-03T12:00:00+00:00"


class ResearchEvidenceStoreTests(
    unittest.TestCase
):
    def artifact(
        self,
        uri="https://example.com/source",
    ):
        source = ResearchSource(
            uri,
            label="Example",
        )

        provenance = SourceProvenance(
            source_id=source.source_id,
            retrieved_at=NOW,
            digest=ContentDigest.from_bytes(
                b"external content"
            ),
            author="Author",
            license="License",
            version="1.0",
        )

        return ExternalArtifact(
            source=source,
            provenance=provenance,
            artifact_kind="DOCUMENT",
            media_type="text/plain",
        )

    def evidence(
        self,
        task_id="TASK-ABCDEF012345",
    ):
        artifact = self.artifact()

        claim = ResearchClaim(
            statement="External claim",
            artifact_ids=(
                artifact.artifact_id,
            ),
            created_at=NOW,
        )

        return (
            ResearchEvidenceBridge
            .to_evidence(
                task_id=task_id,
                claim=claim,
                artifacts=[artifact],
            )
        )

    def test_roundtrip_survives_restart(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "research.sqlite3"
            evidence = self.evidence()

            store = ResearchEvidenceStore(
                path
            )
            store.record(evidence)

            restarted = (
                ResearchEvidenceStore(
                    path
                )
            )

            loaded = restarted.get(
                evidence.evidence_id
            )

            self.assertEqual(
                loaded.to_dict(),
                evidence.to_dict(),
            )

    def test_duplicate_record_is_idempotent(self):
        with tempfile.TemporaryDirectory() as td:
            store = ResearchEvidenceStore(
                Path(td) / "research.sqlite3"
            )
            evidence = self.evidence()

            first = store.record(
                evidence
            )
            second = store.record(
                evidence
            )

            self.assertEqual(
                first,
                second,
            )
            self.assertEqual(
                store.count(),
                1,
            )

    def test_same_id_different_content_conflicts(self):
        with tempfile.TemporaryDirectory() as td:
            store = ResearchEvidenceStore(
                Path(td) / "research.sqlite3"
            )

            first = self.evidence()
            store.record(first)

            artifact = self.artifact(
                "https://example.org/other"
            )

            claim = ResearchClaim(
                statement="Different claim",
                artifact_ids=(
                    artifact.artifact_id,
                ),
                created_at=NOW,
                claim_id=first.source_ref,
            )

            second = (
                ResearchEvidenceBridge
                .to_evidence(
                    task_id=first.task_id,
                    claim=claim,
                    artifacts=[artifact],
                )
            )

            second.evidence_id = (
                first.evidence_id
            )

            with self.assertRaises(
                ResearchEvidenceConflictError
            ):
                store.record(second)

    def test_rejects_non_rx_evidence(self):
        with tempfile.TemporaryDirectory() as td:
            store = ResearchEvidenceStore(
                Path(td) / "research.sqlite3"
            )
            evidence = self.evidence()
            evidence.council = CouncilId.IT

            with self.assertRaises(
                ValueError
            ):
                store.record(evidence)

    def test_rejects_non_web_source(self):
        with tempfile.TemporaryDirectory() as td:
            store = ResearchEvidenceStore(
                Path(td) / "research.sqlite3"
            )
            evidence = self.evidence()
            evidence.kind = (
                EvidenceKind.OTHER
            )

            with self.assertRaises(
                ValueError
            ):
                store.record(evidence)

    def test_rejects_truth_assertion(self):
        with tempfile.TemporaryDirectory() as td:
            store = ResearchEvidenceStore(
                Path(td) / "research.sqlite3"
            )
            evidence = self.evidence()

            evidence.payload[
                "verification"
            ][
                "system_truth_asserted"
            ] = True

            with self.assertRaises(
                ValueError
            ):
                store.record(evidence)

    def test_rejects_source_ref_mismatch(self):
        with tempfile.TemporaryDirectory() as td:
            store = ResearchEvidenceStore(
                Path(td) / "research.sqlite3"
            )
            evidence = self.evidence()

            evidence.source_ref = (
                "CLM-AAAAAAAAAAAA"
            )

            with self.assertRaises(
                ValueError
            ):
                store.record(evidence)

    def test_rejects_claim_artifact_mismatch(self):
        with tempfile.TemporaryDirectory() as td:
            store = ResearchEvidenceStore(
                Path(td) / "research.sqlite3"
            )
            evidence = self.evidence()

            evidence.payload[
                "research_claim"
            ][
                "artifact_ids"
            ] = [
                "ART-AAAAAAAAAAAA"
            ]

            with self.assertRaises(
                ValueError
            ):
                store.record(evidence)

    def test_detects_persisted_json_tamper(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "research.sqlite3"

            store = ResearchEvidenceStore(
                path
            )
            evidence = self.evidence()

            store.record(evidence)

            with sqlite3.connect(path) as con:
                con.execute(
                    """
                    UPDATE research_evidence
                    SET canonical_json = ?
                    WHERE evidence_id = ?
                    """,
                    (
                        '{"tampered":true}',
                        evidence.evidence_id,
                    ),
                )
                con.commit()

            with self.assertRaises(
                ResearchEvidenceCorruptionError
            ):
                store.get(
                    evidence.evidence_id
                )

    def test_for_task_filters(self):
        with tempfile.TemporaryDirectory() as td:
            store = ResearchEvidenceStore(
                Path(td) / "research.sqlite3"
            )

            first = self.evidence(
                "TASK-111111111111"
            )
            second = self.evidence(
                "TASK-222222222222"
            )

            store.record(first)
            store.record(second)

            rows = store.for_task(
                "TASK-111111111111"
            )

            self.assertEqual(
                [
                    row.evidence_id
                    for row in rows
                ],
                [first.evidence_id],
            )

    def test_concurrent_idempotent_writers(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "research.sqlite3"

            ResearchEvidenceStore(
                path
            )

            evidence = self.evidence()

            def write_once():
                return (
                    ResearchEvidenceStore(
                        path
                    ).record(
                        evidence
                    )
                )

            with ThreadPoolExecutor(
                max_workers=4
            ) as pool:
                results = list(
                    pool.map(
                        lambda _: write_once(),
                        range(8),
                    )
                )

            self.assertEqual(
                set(results),
                {evidence.evidence_id},
            )

            self.assertEqual(
                ResearchEvidenceStore(
                    path
                ).count(),
                1,
            )

    def test_sqlite_profile_is_wal_full(self):
        with tempfile.TemporaryDirectory() as td:
            store = ResearchEvidenceStore(
                Path(td) / "research.sqlite3"
            )

            con = store._connect()

            try:
                journal_mode = (
                    con.execute(
                        "PRAGMA journal_mode"
                    )
                    .fetchone()[0]
                )

                synchronous = (
                    con.execute(
                        "PRAGMA synchronous"
                    )
                    .fetchone()[0]
                )
            finally:
                con.close()

            self.assertEqual(
                str(journal_mode).lower(),
                "wal",
            )

            self.assertEqual(
                int(synchronous),
                2,
            )

    def test_missing_id_raises_key_error(self):
        with tempfile.TemporaryDirectory() as td:
            store = ResearchEvidenceStore(
                Path(td) / "research.sqlite3"
            )

            with self.assertRaises(
                KeyError
            ):
                store.get(
                    "EVD-NOT-THERE"
                )

    def test_detects_created_at_index_tamper(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "research.sqlite3"

            store = ResearchEvidenceStore(
                path
            )
            evidence = self.evidence()

            store.record(evidence)

            with sqlite3.connect(path) as con:
                con.execute(
                    """
                    UPDATE research_evidence
                    SET created_at = ?
                    WHERE evidence_id = ?
                    """,
                    (
                        "2099-01-01T00:00:00+00:00",
                        evidence.evidence_id,
                    ),
                )
                con.commit()

            with self.assertRaises(
                ResearchEvidenceCorruptionError
            ):
                store.get(
                    evidence.evidence_id
                )

    def test_idempotent_record_detects_index_tamper(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "research.sqlite3"

            store = ResearchEvidenceStore(
                path
            )
            evidence = self.evidence()

            store.record(evidence)

            with sqlite3.connect(path) as con:
                con.execute(
                    """
                    UPDATE research_evidence
                    SET task_id = ?
                    WHERE evidence_id = ?
                    """,
                    (
                        "TASK-TAMPERED0000",
                        evidence.evidence_id,
                    ),
                )
                con.commit()

            with self.assertRaises(
                ResearchEvidenceCorruptionError
            ):
                store.record(evidence)


if __name__ == "__main__":
    unittest.main()
