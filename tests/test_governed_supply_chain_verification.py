from __future__ import annotations

import ast
import hashlib
import unittest

from dataclasses import replace
from pathlib import Path

from maestro.governance.governed_supply_chain_verification import (
    ArtifactKind,
    ArtifactManifest,
    ArtifactProvenanceClaim,
    ArtifactVerificationState,
    GovernedArtifactVerification,
    GovernedSupplyChainInvariantError,
    GovernedSupplyChainVerifier,
    IntegrityState,
    ProvenanceState,
    SignatureState,
    SignatureVerificationEvidence,
)


DOC = Path(
    "docs/GOVERNED_SUPPLY_CHAIN_VERIFICATION_CONSTITUTION.md"
)

SOURCE = Path(
    "src/maestro/governance/"
    "governed_supply_chain_verification.py"
)


def payload() -> bytes:
    return b"maestro-supply-chain-artifact"


def digest() -> str:
    return hashlib.sha256(
        payload()
    ).hexdigest()


def manifest(
    *,
    signed: bool = False,
) -> ArtifactManifest:
    kwargs = {}

    if signed:
        kwargs = {
            "signer_id": "publisher-key-1",
            "signature_algorithm": (
                "GENERIC-SIGNATURE-V1"
            ),
        }

    return ArtifactManifest(
        artifact_id="adapter.demo",
        artifact_kind=ArtifactKind.ADAPTER,
        artifact_version="1.0.0",
        origin_id="publisher.demo",
        source_ref=(
            "artifact://adapter.demo/1.0.0"
        ),
        digest_algorithm="sha256",
        expected_digest=digest(),
        **kwargs,
    )


def provenance(
    *,
    origin_id: str = "publisher.demo",
) -> ArtifactProvenanceClaim:
    return ArtifactProvenanceClaim(
        artifact_id="adapter.demo",
        artifact_version="1.0.0",
        origin_id=origin_id,
        source_ref=(
            "artifact://adapter.demo/1.0.0"
        ),
        digest_algorithm="sha256",
        digest=digest(),
    )


def signature(
    *,
    signer_id: str = "publisher-key-1",
    verified: bool | None = True,
) -> SignatureVerificationEvidence:
    return SignatureVerificationEvidence(
        evidence_id="SIGE-test",
        artifact_id="adapter.demo",
        artifact_digest=digest(),
        signer_id=signer_id,
        signature_algorithm=(
            "GENERIC-SIGNATURE-V1"
        ),
        signature_present=True,
        cryptographically_verified=verified,
        verifier_ref="verifier://independent",
    )


class GovernedSupplyChainVerificationTests(
    unittest.TestCase
):
    def test_01_constitution_contains_ten_laws(self):
        text = DOC.read_text(
            encoding="utf-8"
        )

        for number in range(1, 11):
            self.assertIn(
                f"SCV-{number:02d}",
                text,
            )

        for law in (
            "DISCOVERED != VERIFIED",
            "HASH MATCH != TRUST",
            (
                "SIGNATURE PRESENT != "
                "SIGNATURE VALID"
            ),
            (
                "SUPPLY-CHAIN VERIFIED "
                "!= TRUSTED"
            ),
            (
                "VERIFIED ARTIFACT "
                "!= EXECUTED"
            ),
            (
                "SUPPLY-CHAIN VERIFICATION "
                "!= OBSERVABILITY SYSTEM"
            ),
        ):
            self.assertIn(
                law,
                text,
            )

    def test_02_unsigned_digest_match_is_incomplete_not_trusted(self):
        result = GovernedSupplyChainVerifier.verify(
            manifest(),
            artifact_bytes=payload(),
            provenance=provenance(),
        )

        self.assertIs(
            result.integrity_state,
            IntegrityState.VERIFIED,
        )

        self.assertIs(
            result.signature_state,
            SignatureState.ABSENT,
        )

        self.assertIs(
            result.provenance_state,
            ProvenanceState.UNKNOWN,
        )

        self.assertIs(
            result.verification_state,
            ArtifactVerificationState.INCOMPLETE,
        )

        self.assertFalse(result.trusted)
        self.assertFalse(
            result.installation_authorized
        )
        self.assertFalse(result.activated)
        self.assertFalse(result.executed)

    def test_03_valid_signature_verifies_but_grants_no_authority(self):
        result = GovernedSupplyChainVerifier.verify(
            manifest(signed=True),
            artifact_bytes=payload(),
            provenance=provenance(),
            signature_evidence=signature(),
        )

        self.assertIs(
            result.integrity_state,
            IntegrityState.VERIFIED,
        )

        self.assertIs(
            result.signature_state,
            SignatureState.VALID,
        )

        self.assertIs(
            result.provenance_state,
            ProvenanceState.VERIFIED,
        )

        self.assertIs(
            result.verification_state,
            ArtifactVerificationState.VERIFIED,
        )

        for field_name in (
            "trusted",
            "installation_authorized",
            "installed",
            "activation_authorized",
            "activated",
            "execution_authorized",
            "executed",
            "core_mutation_requested",
            "observability_system_created",
            "system_truth_asserted",
        ):
            self.assertFalse(
                getattr(
                    result,
                    field_name,
                )
            )

    def test_04_digest_mismatch_fails_closed(self):
        result = GovernedSupplyChainVerifier.verify(
            manifest(),
            artifact_bytes=b"tampered",
            provenance=provenance(),
        )

        self.assertIs(
            result.integrity_state,
            IntegrityState.FAILED,
        )

        self.assertIs(
            result.verification_state,
            ArtifactVerificationState.FAILED,
        )

        self.assertFalse(result.trusted)
        self.assertFalse(
            result.execution_authorized
        )

    def test_05_signature_presence_is_not_signature_validity(self):
        result = GovernedSupplyChainVerifier.verify(
            manifest(signed=True),
            artifact_bytes=payload(),
            provenance=provenance(),
            signature_evidence=signature(
                verified=None
            ),
        )

        self.assertIs(
            result.signature_state,
            SignatureState.UNKNOWN,
        )

        self.assertIs(
            result.provenance_state,
            ProvenanceState.UNKNOWN,
        )

        self.assertIs(
            result.verification_state,
            ArtifactVerificationState.INCOMPLETE,
        )

    def test_06_provenance_and_signature_binding_mismatch_fail_closed(self):
        bad_provenance = (
            GovernedSupplyChainVerifier.verify(
                manifest(signed=True),
                artifact_bytes=payload(),
                provenance=provenance(
                    origin_id="foreign.origin"
                ),
                signature_evidence=signature(),
            )
        )

        self.assertIs(
            bad_provenance.provenance_state,
            ProvenanceState.FAILED,
        )

        self.assertIs(
            bad_provenance.verification_state,
            ArtifactVerificationState.FAILED,
        )

        bad_signature = (
            GovernedSupplyChainVerifier.verify(
                manifest(signed=True),
                artifact_bytes=payload(),
                provenance=provenance(),
                signature_evidence=signature(
                    signer_id="foreign-key"
                ),
            )
        )

        self.assertIs(
            bad_signature.signature_state,
            SignatureState.INVALID,
        )

        self.assertIs(
            bad_signature.verification_state,
            ArtifactVerificationState.FAILED,
        )

    def test_07_direct_provenance_spoof_fails_closed(self):
        cases = (
            (
                SignatureState.ABSENT,
                None,
            ),
            (
                SignatureState.UNKNOWN,
                "SIGE-unknown",
            ),
        )

        for signature_state, evidence_id in cases:
            with self.subTest(
                signature_state=signature_state,
            ):
                with self.assertRaises(
                    GovernedSupplyChainInvariantError
                ):
                    GovernedArtifactVerification(
                        verification_id="SCV-spoof",
                        artifact_id="adapter.demo",
                        artifact_kind=(
                            ArtifactKind.ADAPTER
                        ),
                        artifact_version="1.0.0",
                        origin_id="publisher.demo",
                        source_ref=(
                            "artifact://adapter.demo/"
                            "1.0.0"
                        ),
                        expected_digest=digest(),
                        observed_digest=digest(),
                        integrity_state=(
                            IntegrityState.VERIFIED
                        ),
                        signature_state=(
                            signature_state
                        ),
                        provenance_state=(
                            ProvenanceState.VERIFIED
                        ),
                        verification_state=(
                            ArtifactVerificationState
                            .VERIFIED
                        ),
                        signature_evidence_id=(
                            evidence_id
                        ),
                    )

        with self.assertRaises(
            GovernedSupplyChainInvariantError
        ):
            GovernedArtifactVerification(
                verification_id="SCV-inconsistent",
                artifact_id="adapter.demo",
                artifact_kind=(
                    ArtifactKind.ADAPTER
                ),
                artifact_version="1.0.0",
                origin_id="publisher.demo",
                source_ref=(
                    "artifact://adapter.demo/1.0.0"
                ),
                expected_digest=digest(),
                observed_digest=digest(),
                integrity_state=(
                    IntegrityState.VERIFIED
                ),
                signature_state=(
                    SignatureState.VALID
                ),
                provenance_state=(
                    ProvenanceState.UNKNOWN
                ),
                verification_state=(
                    ArtifactVerificationState
                    .INCOMPLETE
                ),
                signature_evidence_id="SIGE-valid",
            )

    def test_08_verification_is_deterministic(self):
        first = GovernedSupplyChainVerifier.verify(
            manifest(signed=True),
            artifact_bytes=payload(),
            provenance=provenance(),
            signature_evidence=signature(),
        )

        second = GovernedSupplyChainVerifier.verify(
            manifest(signed=True),
            artifact_bytes=payload(),
            provenance=provenance(),
            signature_evidence=signature(),
        )

        self.assertEqual(
            first.verification_id,
            second.verification_id,
        )

        self.assertEqual(
            first.to_dict(),
            second.to_dict(),
        )

    def test_09_authority_escalation_fails_closed(self):
        result = GovernedSupplyChainVerifier.verify(
            manifest(signed=True),
            artifact_bytes=payload(),
            provenance=provenance(),
            signature_evidence=signature(),
        )

        fields = (
            "trusted",
            "installation_authorized",
            "installed",
            "activation_authorized",
            "activated",
            "execution_authorized",
            "executed",
            "core_mutation_requested",
            "observability_system_created",
            "system_truth_asserted",
        )

        for field_name in fields:
            with self.subTest(
                field=field_name
            ):
                with self.assertRaises(
                    GovernedSupplyChainInvariantError
                ):
                    replace(
                        result,
                        **{field_name: True},
                    )

    def test_10_module_is_passive_and_bmf023_separate(self):
        text = SOURCE.read_text(
            encoding="utf-8"
        )

        tree = ast.parse(text)

        imports = set()
        calls = set()

        for node in ast.walk(tree):
            if isinstance(
                node,
                ast.Import,
            ):
                imports.update(
                    alias.name
                    for alias in node.names
                )

            elif isinstance(
                node,
                ast.ImportFrom,
            ):
                if node.module:
                    imports.add(
                        node.module
                    )

            elif isinstance(
                node,
                ast.Call,
            ):
                if isinstance(
                    node.func,
                    ast.Name,
                ):
                    calls.add(
                        node.func.id
                    )

                elif isinstance(
                    node.func,
                    ast.Attribute,
                ):
                    calls.add(
                        node.func.attr
                    )

        forbidden_import_roots = (
            "subprocess",
            "socket",
            "requests",
            "httpx",
            "aiohttp",
            "urllib",
        )

        bad_imports = {
            name
            for name in imports
            if any(
                name == root
                or name.startswith(
                    root + "."
                )
                for root
                in forbidden_import_roots
            )
        }

        forbidden_calls = {
            "download",
            "register",
            "install",
            "activate",
            "authorize",
            "execute",
            "dispatch",
            "migrate",
            "apply",
            "promote",
        }

        self.assertEqual(
            bad_imports,
            set(),
        )

        self.assertEqual(
            calls & forbidden_calls,
            set(),
        )

        for forbidden_symbol in (
            "DynamicAdapterRegistry",
            "PlatformExecutionHandoff",
            "CouncilCapsuleRegistry",
            "ObservabilitySystem",
            "TelemetrySystem",
        ):
            self.assertNotIn(
                forbidden_symbol,
                text,
            )


if __name__ == "__main__":
    unittest.main()
