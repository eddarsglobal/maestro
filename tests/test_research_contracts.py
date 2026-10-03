import unittest

from maestro.research import (
    ContentDigest,
    ExternalArtifact,
    ResearchClaim,
    ResearchSource,
    SourceProvenance,
    TrustState,
)


NOW = "2026-10-03T12:00:00+00:00"


class ResearchContractTests(unittest.TestCase):
    def source(self):
        return ResearchSource(
            "https://example.com/source",
            label="Example",
        )

    def provenance(self, source):
        return SourceProvenance(
            source_id=source.source_id,
            retrieved_at=NOW,
            digest=ContentDigest.from_bytes(
                b"external content"
            ),
            author="Example Author",
            license="Example License",
            version="1.0",
        )

    def artifact(self):
        source = self.source()

        return ExternalArtifact(
            source=source,
            provenance=self.provenance(source),
            artifact_kind="DOCUMENT",
            media_type="text/plain",
        )

    def test_content_digest_from_bytes(self):
        digest = ContentDigest.from_bytes(
            b"abc"
        )

        self.assertEqual(
            digest.algorithm,
            "sha256",
        )

        self.assertEqual(
            digest.hex_digest,
            (
                "ba7816bf8f01cfea414140de5dae2223"
                "b00361a396177a9cb410ff61f20015ad"
            ),
        )

        self.assertEqual(
            digest.to_dict()["algorithm"],
            "sha256",
        )

    def test_content_digest_rejects_non_sha256(self):
        with self.assertRaises(ValueError):
            ContentDigest(
                "0" * 64,
                algorithm="sha1",
            )

    def test_content_digest_rejects_invalid_hex(self):
        with self.assertRaises(ValueError):
            ContentDigest("not-a-digest")

    def test_source_requires_http_or_https(self):
        with self.assertRaises(ValueError):
            ResearchSource(
                "file:///tmp/source"
            )

        with self.assertRaises(ValueError):
            ResearchSource(
                "example.com/source"
            )

        source = ResearchSource(
            "https://example.com/source"
        )

        self.assertTrue(
            source.source_id.startswith(
                "SRC-"
            )
        )

    def test_source_rejects_nul(self):
        with self.assertRaises(ValueError):
            ResearchSource(
                "https://example.com/\x00source"
            )

    def test_provenance_requires_aware_timestamp(self):
        source = self.source()

        with self.assertRaises(ValueError):
            SourceProvenance(
                source_id=source.source_id,
                retrieved_at=(
                    "2026-10-03T12:00:00"
                ),
                digest=ContentDigest.from_bytes(
                    b"x"
                ),
            )

    def test_provenance_serializes_digest(self):
        source = self.source()
        provenance = self.provenance(
            source
        )

        data = provenance.to_dict()

        self.assertEqual(
            data["source_id"],
            source.source_id,
        )

        self.assertEqual(
            data["digest"]["algorithm"],
            "sha256",
        )

    def test_artifact_defaults_to_untrusted(self):
        artifact = self.artifact()

        self.assertEqual(
            artifact.trust_state,
            TrustState.UNTRUSTED,
        )

        self.assertEqual(
            artifact.to_dict()[
                "trust_state"
            ],
            "UNTRUSTED",
        )

    def test_artifact_rejects_provenance_mismatch(self):
        first = self.source()
        second = ResearchSource(
            "https://example.org/other"
        )

        provenance = self.provenance(
            first
        )

        with self.assertRaises(ValueError):
            ExternalArtifact(
                source=second,
                provenance=provenance,
                artifact_kind="DOCUMENT",
                media_type="text/plain",
            )

    def test_claim_requires_external_artifact(self):
        with self.assertRaises(ValueError):
            ResearchClaim(
                statement="A claim",
                artifact_ids=(),
                created_at=NOW,
            )

    def test_claim_rejects_duplicate_artifacts(self):
        artifact = self.artifact()

        with self.assertRaises(ValueError):
            ResearchClaim(
                statement="A claim",
                artifact_ids=(
                    artifact.artifact_id,
                    artifact.artifact_id,
                ),
                created_at=NOW,
            )

    def test_claim_defaults_to_untrusted(self):
        artifact = self.artifact()

        claim = ResearchClaim(
            statement="External claim",
            artifact_ids=(
                artifact.artifact_id,
            ),
            created_at=NOW,
        )

        self.assertEqual(
            claim.trust_state,
            TrustState.UNTRUSTED,
        )

        self.assertEqual(
            claim.to_dict()[
                "artifact_ids"
            ],
            [artifact.artifact_id],
        )

    def test_external_trust_has_no_verified_or_approved(self):
        values = {
            item.value
            for item in TrustState
        }

        self.assertNotIn(
            "VERIFIED",
            values,
        )

        self.assertNotIn(
            "APPROVED",
            values,
        )

    def test_source_label_rejects_nul(self):
        with self.assertRaises(ValueError):
            ResearchSource(
                "https://example.com/source",
                label="bad\x00label",
            )


if __name__ == "__main__":
    unittest.main()
