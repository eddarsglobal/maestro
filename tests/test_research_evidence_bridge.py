import unittest

from maestro.enums import (
    CouncilId,
    EvidenceKind,
)
from maestro.research import (
    ContentDigest,
    ExternalArtifact,
    ResearchClaim,
    ResearchEvidenceBridge,
    ResearchSource,
    SourceProvenance,
    TrustState,
)


NOW = "2026-10-03T12:00:00+00:00"


class ResearchEvidenceBridgeTests(
    unittest.TestCase
):
    def artifact(
        self,
        uri="https://example.com/source",
        body=b"external content",
    ):
        source = ResearchSource(
            uri,
            label="External source",
        )

        provenance = SourceProvenance(
            source_id=source.source_id,
            retrieved_at=NOW,
            digest=ContentDigest.from_bytes(
                body
            ),
            author="Example Author",
            license="Example License",
            version="1.0",
        )

        return ExternalArtifact(
            source=source,
            provenance=provenance,
            artifact_kind="DOCUMENT",
            media_type="text/plain",
        )

    def claim(self, *artifacts):
        return ResearchClaim(
            statement="External factual claim",
            artifact_ids=tuple(
                artifact.artifact_id
                for artifact in artifacts
            ),
            created_at=NOW,
        )

    def test_maps_claim_to_rx_web_source(self):
        artifact = self.artifact()
        claim = self.claim(
            artifact
        )

        evidence = (
            ResearchEvidenceBridge
            .to_evidence(
                task_id="TASK-ABCDEF012345",
                claim=claim,
                artifacts=[artifact],
            )
        )

        self.assertEqual(
            evidence.task_id,
            "TASK-ABCDEF012345",
        )
        self.assertEqual(
            evidence.council,
            CouncilId.RX,
        )
        self.assertEqual(
            evidence.kind,
            EvidenceKind.WEB_SOURCE,
        )
        self.assertEqual(
            evidence.claim,
            claim.statement,
        )
        self.assertEqual(
            evidence.source_ref,
            claim.claim_id,
        )

    def test_preserves_provenance_and_digest(self):
        artifact = self.artifact()
        claim = self.claim(
            artifact
        )

        evidence = (
            ResearchEvidenceBridge
            .to_evidence(
                task_id="TASK-ABCDEF012345",
                claim=claim,
                artifacts=[artifact],
            )
        )

        row = evidence.payload[
            "artifacts"
        ][0]

        self.assertEqual(
            row["source"]["uri"],
            artifact.source.uri,
        )

        self.assertEqual(
            row["provenance"]["digest"][
                "hex_digest"
            ],
            artifact.provenance.digest.hex_digest,
        )

    def test_missing_artifact_fails_closed(self):
        first = self.artifact(
            "https://example.com/one"
        )
        second = self.artifact(
            "https://example.com/two"
        )

        claim = self.claim(
            first,
            second,
        )

        with self.assertRaises(
            ValueError
        ):
            ResearchEvidenceBridge.to_evidence(
                task_id="TASK-ABCDEF012345",
                claim=claim,
                artifacts=[first],
            )

    def test_extra_artifact_fails_closed(self):
        first = self.artifact(
            "https://example.com/one"
        )
        second = self.artifact(
            "https://example.com/two"
        )

        claim = self.claim(
            first
        )

        with self.assertRaises(
            ValueError
        ):
            ResearchEvidenceBridge.to_evidence(
                task_id="TASK-ABCDEF012345",
                claim=claim,
                artifacts=[
                    first,
                    second,
                ],
            )

    def test_duplicate_supplied_artifact_fails(self):
        artifact = self.artifact()
        claim = self.claim(
            artifact
        )

        with self.assertRaises(
            ValueError
        ):
            ResearchEvidenceBridge.to_evidence(
                task_id="TASK-ABCDEF012345",
                claim=claim,
                artifacts=[
                    artifact,
                    artifact,
                ],
            )

    def test_invalid_task_id_fails(self):
        artifact = self.artifact()
        claim = self.claim(
            artifact
        )

        secret = (
            "customer@example.com"
            "?token=RX03E2_BRIDGE_SECRET"
        )

        for task_id in (
            "",
            "   ",
            "TASK-\x00BAD",
            "TASK-short",
            "task-ABCDEF012345",
            "TASK-ABCDEF01234",
            "TASK-ABCDEF0123456",
            " TASK-ABCDEF012345",
            "TASK-ABCDEF012345 ",
            secret,
            (
                "TASK-"
                + chr(0xD800)
            ),
        ):
            with self.subTest(
                task_id=repr(task_id)
            ):
                with self.assertRaises(
                    ValueError
                ) as context:
                    (
                        ResearchEvidenceBridge
                        .to_evidence(
                            task_id=task_id,
                            claim=claim,
                            artifacts=[
                                artifact
                            ],
                        )
                    )

                self.assertNotIn(
                    "RX03E2_BRIDGE_SECRET",
                    str(
                        context.exception
                    ),
                )

    def test_bridge_never_claims_verification(self):
        artifact = self.artifact()
        claim = self.claim(
            artifact
        )

        evidence = (
            ResearchEvidenceBridge
            .to_evidence(
                task_id="TASK-ABCDEF012345",
                claim=claim,
                artifacts=[artifact],
            )
        )

        verification = (
            evidence.payload[
                "verification"
            ]
        )

        self.assertEqual(
            verification["status"],
            "UNVERIFIED_EXTERNAL",
        )
        self.assertEqual(
            verification[
                "required_authority"
            ],
            "AY",
        )
        self.assertFalse(
            verification[
                "system_truth_asserted"
            ]
        )

        self.assertEqual(
            claim.trust_state,
            TrustState.UNTRUSTED,
        )


if __name__ == "__main__":
    unittest.main()
