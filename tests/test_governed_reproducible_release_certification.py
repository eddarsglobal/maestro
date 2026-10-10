from __future__ import annotations

import ast
import hashlib
import unittest

from dataclasses import replace
from pathlib import Path

from maestro.governance.governed_reproducible_release_certification import (
    GateEvidenceState,
    GovernedPlatformCertification,
    GovernedReleaseCertificationResult,
    GovernedReleaseInvariantError,
    GovernedReproducibleReleaseCertification,
    PlatformCertificationState,
    PlatformGateEvidence,
    ReleaseCertificationState,
    ReproducibleReleaseManifest,
)


DOC = Path(
    "docs/"
    "GOVERNED_REPRODUCIBLE_RELEASE_CERTIFICATION_CONSTITUTION.md"
)

SOURCE = Path(
    "src/maestro/governance/"
    "governed_reproducible_release_certification.py"
)


def digest(
    value: str,
) -> str:
    return hashlib.sha256(
        value.encode("utf-8")
    ).hexdigest()


def manifest(
    platforms=(
        "PLATFORM-A",
        "PLATFORM-B",
    ),
    *,
    release_id="REL-001",
    core="core",
    constitution="constitution",
):
    return ReproducibleReleaseManifest(
        release_id=release_id,
        release_version="1.0",
        core_source_digest=digest(core),
        constitutional_fingerprint=digest(
            constitution
        ),
        supported_platform_ids=tuple(
            platforms
        ),
        build_recipe_id="RECIPE-001",
    )


def evidence(
    row: ReproducibleReleaseManifest,
    platform_id: str,
    *,
    build=GateEvidenceState.PASS,
    test=GateEvidenceState.PASS,
    artifact_digest=None,
    reproduced_artifact_digest=None,
    core_source_digest=None,
    constitutional_fingerprint=None,
):
    artifact = (
        artifact_digest
        if artifact_digest is not None
        else digest(
            "artifact-" + platform_id
        )
    )

    reproduced = (
        reproduced_artifact_digest
        if reproduced_artifact_digest
        is not None
        else artifact
    )

    return PlatformGateEvidence(
        platform_id=platform_id,
        build_state=build,
        test_state=test,
        artifact_id=(
            "ART-" + platform_id
        ),
        artifact_digest=artifact,
        reproduced_artifact_digest=(
            reproduced
        ),
        core_source_digest=(
            row.core_source_digest
            if core_source_digest is None
            else core_source_digest
        ),
        constitutional_fingerprint=(
            row.constitutional_fingerprint
            if constitutional_fingerprint
            is None
            else constitutional_fingerprint
        ),
        source_ref=(
            "evidence://" + platform_id
        ),
    )


def certify_platform(
    row: ReproducibleReleaseManifest,
    platform_id: str,
    **kwargs,
):
    return (
        GovernedReproducibleReleaseCertification
        .certify_platform(
            row,
            evidence(
                row,
                platform_id,
                **kwargs,
            ),
        )
    )


class GovernedReproducibleReleaseCertificationTests(
    unittest.TestCase
):
    def test_01_constitution_contains_ten_laws_and_core_invariants(self):
        text = DOC.read_text(
            encoding="utf-8"
        )

        for number in range(1, 11):
            self.assertIn(
                f"RRC-{number:02d}",
                text,
            )

        for invariant in (
            "BUILD SUCCESS != RELEASE CERTIFIED",
            "PLATFORM PASS != UNIVERSAL SUPPORT",
            "ONE PLATFORM PASS != ALL SUPPORTED PLATFORMS PASS",
            "REPRODUCIBLE != TRUSTED",
            "RELEASE EVIDENCE != RELEASE AUTHORIZATION",
            "RELEASE CERTIFIED != RELEASE AUTHORIZED",
            "CERTIFIED PLATFORM != CORE SEMANTIC VARIANT",
            "PACKAGING DIFFERENCE != CONSTITUTIONAL DIFFERENCE",
            "RELEASE GATE != CORE MUTATION",
            "UNKNOWN != PASS",
        ):
            self.assertIn(
                invariant,
                text,
            )

        self.assertIn(
            "FAILED takes state precedence over INCOMPLETE",
            text,
        )

        self.assertIn(
            "SUPPORTED SET COMPLETE + ALL PASS is required for PASS",
            text,
        )

    def test_02_complete_supported_platform_set_passes_without_authority(self):
        row = manifest(
            (
                "PLATFORM-C",
                "PLATFORM-A",
                "PLATFORM-B",
            )
        )

        certs = tuple(
            certify_platform(
                row,
                platform_id,
            )
            for platform_id
            in row.supported_platform_ids
        )

        result = (
            GovernedReproducibleReleaseCertification
            .certify_release(
                row,
                tuple(reversed(certs)),
            )
        )

        self.assertEqual(
            row.supported_platform_ids,
            (
                "PLATFORM-A",
                "PLATFORM-B",
                "PLATFORM-C",
            ),
        )

        self.assertIs(
            result.state,
            ReleaseCertificationState.PASS,
        )

        self.assertEqual(
            result.passed_platform_ids,
            row.supported_platform_ids,
        )

        self.assertEqual(
            result.missing_platform_ids,
            (),
        )

        self.assertFalse(
            result.trusted
        )
        self.assertFalse(
            result.release_authorized
        )
        self.assertFalse(
            result.publish_authorized
        )
        self.assertFalse(
            result.deploy_authorized
        )
        self.assertFalse(
            result.universal_support_asserted
        )

    def test_03_missing_platform_and_unknown_evidence_are_incomplete(self):
        row = manifest()

        cert = certify_platform(
            row,
            "PLATFORM-A",
            build=GateEvidenceState.UNKNOWN,
        )

        self.assertIs(
            cert.state,
            PlatformCertificationState.INCOMPLETE,
        )

        self.assertIn(
            "build gate unknown",
            cert.reasons,
        )

        result = (
            GovernedReproducibleReleaseCertification
            .certify_release(
                row,
                (cert,),
            )
        )

        self.assertIs(
            result.state,
            ReleaseCertificationState.INCOMPLETE,
        )

        self.assertEqual(
            result.missing_platform_ids,
            ("PLATFORM-B",),
        )

        self.assertFalse(
            result.release_authorized
        )

    def test_04_failure_precedence_preserves_all_observed_reasons(self):
        row = manifest(
            ("PLATFORM-A",)
        )

        raw = PlatformGateEvidence(
            platform_id="PLATFORM-A",
            build_state=(
                GateEvidenceState.FAIL
            ),
            test_state=(
                GateEvidenceState.UNKNOWN
            ),
            artifact_id="ART-A",
            artifact_digest=None,
            reproduced_artifact_digest=None,
            core_source_digest=(
                row.core_source_digest
            ),
            constitutional_fingerprint=(
                row.constitutional_fingerprint
            ),
            source_ref="evidence://a",
        )

        cert = (
            GovernedReproducibleReleaseCertification
            .certify_platform(
                row,
                raw,
            )
        )

        self.assertIs(
            cert.state,
            PlatformCertificationState.FAILED,
        )

        self.assertEqual(
            cert.reasons,
            (
                "build gate failed",
                "test gate unknown",
                "artifact digest missing",
                "reproduced artifact digest missing",
            ),
        )

        result = (
            GovernedReproducibleReleaseCertification
            .certify_release(
                row,
                (cert,),
            )
        )

        self.assertIs(
            result.state,
            ReleaseCertificationState.FAILED,
        )

    def test_05_reproducibility_and_core_identity_mismatches_fail(self):
        row = manifest(
            ("PLATFORM-A",)
        )

        mismatch = certify_platform(
            row,
            "PLATFORM-A",
            artifact_digest=digest(
                "artifact-one"
            ),
            reproduced_artifact_digest=digest(
                "artifact-two"
            ),
        )

        self.assertIs(
            mismatch.state,
            PlatformCertificationState.FAILED,
        )

        self.assertIn(
            "artifact reproducibility mismatch",
            mismatch.reasons,
        )

        source_mismatch = certify_platform(
            row,
            "PLATFORM-A",
            core_source_digest=digest(
                "different-core"
            ),
        )

        self.assertIs(
            source_mismatch.state,
            PlatformCertificationState.FAILED,
        )

        self.assertIn(
            "core source digest mismatch",
            source_mismatch.reasons,
        )

        constitution_mismatch = (
            certify_platform(
                row,
                "PLATFORM-A",
                constitutional_fingerprint=(
                    digest(
                        "different-constitution"
                    )
                ),
            )
        )

        self.assertIs(
            constitution_mismatch.state,
            PlatformCertificationState.FAILED,
        )

        self.assertIn(
            "constitutional fingerprint mismatch",
            constitution_mismatch.reasons,
        )

    def test_06_manifest_and_platform_lineage_fail_closed(self):
        with self.assertRaises(
            GovernedReleaseInvariantError
        ):
            ReproducibleReleaseManifest(
                release_id="REL-MISSING-CORE",
                release_version="1.0",
                core_source_digest=None,
                constitutional_fingerprint=(
                    digest("constitution")
                ),
                supported_platform_ids=(
                    "PLATFORM-A",
                ),
                build_recipe_id="RECIPE",
            )

        with self.assertRaises(
            GovernedReleaseInvariantError
        ):
            ReproducibleReleaseManifest(
                release_id="REL-DUP",
                release_version="1.0",
                core_source_digest=digest(
                    "core"
                ),
                constitutional_fingerprint=(
                    digest("constitution")
                ),
                supported_platform_ids=(
                    "PLATFORM-A",
                    "PLATFORM-A",
                ),
                build_recipe_id="RECIPE",
            )

        row = manifest(
            ("PLATFORM-A",)
        )

        undeclared = evidence(
            row,
            "PLATFORM-X",
        )

        with self.assertRaises(
            GovernedReleaseInvariantError
        ):
            GovernedReproducibleReleaseCertification.certify_platform(
                row,
                undeclared,
            )

        cert = certify_platform(
            row,
            "PLATFORM-A",
        )

        with self.assertRaises(
            GovernedReleaseInvariantError
        ):
            GovernedReproducibleReleaseCertification.certify_release(
                row,
                (
                    cert,
                    cert,
                ),
            )

        other = manifest(
            ("PLATFORM-A",),
            release_id="REL-OTHER",
            core="other-core",
        )

        with self.assertRaises(
            GovernedReleaseInvariantError
        ):
            GovernedReleaseCertificationResult(
                manifest=other,
                platform_certifications=(
                    cert,
                ),
            )

    def test_07_pass_requires_exactly_the_complete_supported_set(self):
        row = manifest(
            (
                "PLATFORM-A",
                "PLATFORM-B",
                "PLATFORM-C",
            )
        )

        partial_a = (
            GovernedReproducibleReleaseCertification
            .certify_release(
                row,
                (
                    certify_platform(
                        row,
                        "PLATFORM-A",
                    ),
                ),
            )
        )

        partial_b = (
            GovernedReproducibleReleaseCertification
            .certify_release(
                row,
                (
                    certify_platform(
                        row,
                        "PLATFORM-A",
                    ),
                    certify_platform(
                        row,
                        "PLATFORM-B",
                    ),
                ),
            )
        )

        complete = (
            GovernedReproducibleReleaseCertification
            .certify_release(
                row,
                (
                    certify_platform(
                        row,
                        "PLATFORM-C",
                    ),
                    certify_platform(
                        row,
                        "PLATFORM-A",
                    ),
                    certify_platform(
                        row,
                        "PLATFORM-B",
                    ),
                ),
            )
        )

        self.assertIs(
            partial_a.state,
            ReleaseCertificationState.INCOMPLETE,
        )

        self.assertIs(
            partial_b.state,
            ReleaseCertificationState.INCOMPLETE,
        )

        self.assertIs(
            complete.state,
            ReleaseCertificationState.PASS,
        )

        self.assertEqual(
            complete.missing_platform_ids,
            (),
        )

    def test_08_manifest_and_release_certification_are_deterministic(self):
        first = manifest(
            (
                "PLATFORM-B",
                "PLATFORM-A",
            ),
            release_id="REL-DET",
        )

        reordered = manifest(
            (
                "PLATFORM-A",
                "PLATFORM-B",
            ),
            release_id="REL-DET",
        )

        self.assertEqual(
            first.manifest_id,
            reordered.manifest_id,
        )

        certs = (
            certify_platform(
                first,
                "PLATFORM-A",
            ),
            certify_platform(
                first,
                "PLATFORM-B",
            ),
        )

        a = (
            GovernedReproducibleReleaseCertification
            .certify_release(
                first,
                certs,
            )
        )

        b = (
            GovernedReproducibleReleaseCertification
            .certify_release(
                first,
                tuple(reversed(certs)),
            )
        )

        self.assertEqual(
            a.certification_id,
            b.certification_id,
        )

        self.assertEqual(
            a.to_dict(),
            b.to_dict(),
        )

    def test_09_authority_escalation_fails_closed(self):
        row = manifest(
            ("PLATFORM-A",)
        )

        platform = certify_platform(
            row,
            "PLATFORM-A",
        )

        release = (
            GovernedReproducibleReleaseCertification
            .certify_release(
                row,
                (platform,),
            )
        )

        fields = (
            "trusted",
            "release_authorized",
            "publish_authorized",
            "deploy_authorized",
            "tag_mutation_authorized",
            "core_mutation_requested",
            "universal_support_asserted",
            "system_truth_asserted",
        )

        for target in (
            platform,
            release,
        ):
            for field_name in fields:
                with self.subTest(
                    target=type(
                        target
                    ).__name__,
                    field=field_name,
                ):
                    with self.assertRaises(
                        GovernedReleaseInvariantError
                    ):
                        replace(
                            target,
                            **{
                                field_name: True
                            },
                        )

    def test_10_module_is_passive_and_legacy_authorizer_is_not_dependency(self):
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
            "publish",
            "deploy",
            "push",
            "tag",
            "authorize",
            "activate",
            "install",
            "execute",
            "migrate",
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
            "ProductionReleaseGate",
            "ReleaseEvidence",
            "GenesisCertifier",
        ):
            self.assertNotIn(
                forbidden_symbol,
                text,
            )


if __name__ == "__main__":
    unittest.main()
