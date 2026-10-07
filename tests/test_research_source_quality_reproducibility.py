from __future__ import annotations

import ast
import copy
import unittest

from datetime import (
    datetime,
    timezone,
)
from pathlib import Path

from maestro.enums import CouncilId
from maestro.research import (
    ContentDigest,
    ExternalArtifact,
    RadarFactors,
    ResearchClaim,
    ResearchEvidenceBridge,
    ResearchSource,
    SourceProvenance,
    SourceQualityReproducibilityEvaluator,
    SourceQualityReproducibilityInvariantError,
    TechnologyRadarInvariantError,
)


class SourceQualityReproducibilityTests(
    unittest.TestCase
):
    def evidence(
        self,
        *,
        author=None,
        license=None,
        version=None,
    ):
        now = datetime.now(
            timezone.utc
        ).isoformat()

        source = ResearchSource(
            "https://example.com/"
            "adel05-source",
            label="ADEL0.5 source",
        )

        provenance = SourceProvenance(
            source_id=source.source_id,
            retrieved_at=now,
            digest=ContentDigest.from_bytes(
                b"ADEL0.5"
            ),
            author=author,
            license=license,
            version=version,
        )

        artifact = ExternalArtifact(
            source=source,
            provenance=provenance,
            artifact_kind="DOCUMENT",
            media_type="text/html",
        )

        claim = ResearchClaim(
            statement=(
                "External reproducible "
                "technology observation"
            ),
            artifact_ids=(
                artifact.artifact_id,
            ),
            created_at=now,
        )

        return (
            ResearchEvidenceBridge
            .to_evidence(
                task_id=(
                    "TASK-A1B2C3D4E5F6"
                ),
                claim=claim,
                artifacts=[artifact],
            )
        )

    def factors(
        self,
    ):
        return RadarFactors(
            novelty=0.90,
            source_quality=0.10,
            relevance_to_maestro=0.85,
            expected_capability_gain=0.75,
            reproducibility=0.10,
            integration_cost=0.20,
            security_risk=0.15,
        )

    def test_digest_contributes_to_source_quality(
        self,
    ):
        result = (
            SourceQualityReproducibilityEvaluator
            .evaluate(
                self.evidence()
            )
        )

        self.assertEqual(
            result.digest_coverage,
            1.0,
        )

        self.assertGreater(
            result.source_quality,
            0.0,
        )

    def test_complete_metadata_increases_source_quality(
        self,
    ):
        sparse = (
            SourceQualityReproducibilityEvaluator
            .evaluate(
                self.evidence()
            )
        )

        rich = (
            SourceQualityReproducibilityEvaluator
            .evaluate(
                self.evidence(
                    author="Researcher",
                    license="MIT",
                    version="1.0",
                )
            )
        )

        self.assertGreater(
            rich.source_quality,
            sparse.source_quality,
        )

        self.assertEqual(
            rich.metadata_coverage,
            1.0,
        )

    def test_independent_sources_increase_source_quality(
        self,
    ):
        single = (
            SourceQualityReproducibilityEvaluator
            .evaluate(
                self.evidence(),
                independent_sources=[
                    "source-a"
                ],
            )
        )

        multiple = (
            SourceQualityReproducibilityEvaluator
            .evaluate(
                self.evidence(),
                independent_sources=[
                    "source-a",
                    "source-b",
                ],
            )
        )

        self.assertGreater(
            multiple.source_quality,
            single.source_quality,
        )

    def test_source_quality_is_not_truth(
        self,
    ):
        result = (
            SourceQualityReproducibilityEvaluator
            .evaluate(
                self.evidence(
                    author="Researcher",
                    license="MIT",
                    version="1.0",
                ),
                independent_sources=[
                    "source-a",
                    "source-b",
                ],
            )
        )

        self.assertEqual(
            result.source_quality,
            1.0,
        )

        self.assertFalse(
            result.system_truth_asserted
        )

    def test_full_reproduction_support_has_full_score(
        self,
    ):
        result = (
            SourceQualityReproducibilityEvaluator
            .evaluate(
                self.evidence(),
                reproduction_requirements=[
                    "code",
                    "dataset",
                    "steps",
                ],
                reproduction_support=[
                    "code",
                    "dataset",
                    "steps",
                ],
            )
        )

        self.assertEqual(
            result.reproducibility,
            1.0,
        )

    def test_no_reproduction_support_has_zero_score(
        self,
    ):
        result = (
            SourceQualityReproducibilityEvaluator
            .evaluate(
                self.evidence(),
                reproduction_requirements=[
                    "code",
                    "dataset",
                ],
                reproduction_support=[],
            )
        )

        self.assertEqual(
            result.reproducibility,
            0.0,
        )

    def test_partial_reproduction_support_has_partial_score(
        self,
    ):
        result = (
            SourceQualityReproducibilityEvaluator
            .evaluate(
                self.evidence(),
                reproduction_requirements=[
                    "code",
                    "dataset",
                    "steps",
                    "environment",
                ],
                reproduction_support=[
                    "code",
                    "steps",
                ],
            )
        )

        self.assertEqual(
            result.reproducibility,
            0.5,
        )

    def test_missing_reproduction_context_is_unknown(
        self,
    ):
        result = (
            SourceQualityReproducibilityEvaluator
            .evaluate(
                self.evidence()
            )
        )

        self.assertIsNone(
            result.reproducibility
        )

        self.assertFalse(
            result.reproducibility_known
        )

    def test_unknown_reproducibility_is_not_zero(
        self,
    ):
        unknown = (
            SourceQualityReproducibilityEvaluator
            .evaluate(
                self.evidence()
            )
        )

        explicit_zero = (
            SourceQualityReproducibilityEvaluator
            .evaluate(
                self.evidence(),
                reproduction_requirements=[
                    "code"
                ],
                reproduction_support=[],
            )
        )

        self.assertIsNone(
            unknown.reproducibility
        )

        self.assertEqual(
            explicit_zero.reproducibility,
            0.0,
        )

    def test_evaluation_is_deterministic(
        self,
    ):
        evidence = self.evidence(
            author="Researcher",
            version="1.0",
        )

        kwargs = {
            "independent_sources": [
                "alpha",
                "beta",
            ],
            "reproduction_requirements": [
                "code",
                "dataset",
            ],
            "reproduction_support": [
                "code",
            ],
        }

        first = (
            SourceQualityReproducibilityEvaluator
            .evaluate(
                evidence,
                **kwargs,
            )
        )

        second = (
            SourceQualityReproducibilityEvaluator
            .evaluate(
                evidence,
                **kwargs,
            )
        )

        self.assertEqual(
            first,
            second,
        )

    def test_scores_are_bounded(
        self,
    ):
        result = (
            SourceQualityReproducibilityEvaluator
            .evaluate(
                self.evidence(
                    author="Researcher",
                    license="MIT",
                    version="1.0",
                ),
                independent_sources=[
                    "a",
                    "b",
                    "c",
                ],
                reproduction_requirements=[
                    "code",
                    "dataset",
                ],
                reproduction_support=[
                    "code",
                ],
            )
        )

        self.assertGreaterEqual(
            result.source_quality,
            0.0,
        )

        self.assertLessEqual(
            result.source_quality,
            1.0,
        )

        self.assertGreaterEqual(
            result.reproducibility,
            0.0,
        )

        self.assertLessEqual(
            result.reproducibility,
            1.0,
        )

    def test_evidence_is_not_mutated(
        self,
    ):
        evidence = self.evidence()

        original = copy.deepcopy(
            evidence
        )

        SourceQualityReproducibilityEvaluator.evaluate(
            evidence,
            independent_sources=[
                "a",
                "b",
            ],
            reproduction_requirements=[
                "code"
            ],
            reproduction_support=[
                "code"
            ],
        )

        self.assertEqual(
            evidence,
            original,
        )

    def test_unverified_boundary_is_preserved(
        self,
    ):
        result = (
            SourceQualityReproducibilityEvaluator
            .evaluate(
                self.evidence(),
                reproduction_requirements=[
                    "code"
                ],
                reproduction_support=[
                    "code"
                ],
            )
        )

        self.assertEqual(
            result.verification_status,
            "UNVERIFIED_EXTERNAL",
        )

        self.assertFalse(
            result.system_truth_asserted
        )

    def test_apply_replaces_only_source_quality_and_reproducibility(
        self,
    ):
        result = (
            SourceQualityReproducibilityEvaluator
            .evaluate(
                self.evidence(
                    author="Researcher",
                    license="MIT",
                    version="1.0",
                ),
                reproduction_requirements=[
                    "code",
                    "dataset",
                ],
                reproduction_support=[
                    "code",
                ],
            )
        )

        before = self.factors()

        after = result.apply_to_factors(
            before
        )

        self.assertEqual(
            after.source_quality,
            result.source_quality,
        )

        self.assertEqual(
            after.reproducibility,
            result.reproducibility,
        )

        self.assertEqual(
            after.novelty,
            before.novelty,
        )

        self.assertEqual(
            after.relevance_to_maestro,
            before.relevance_to_maestro,
        )

        self.assertEqual(
            after.expected_capability_gain,
            before.expected_capability_gain,
        )

        self.assertEqual(
            after.integration_cost,
            before.integration_cost,
        )

        self.assertEqual(
            after.security_risk,
            before.security_risk,
        )

    def test_unknown_reproducibility_cannot_be_silently_applied(
        self,
    ):
        result = (
            SourceQualityReproducibilityEvaluator
            .evaluate(
                self.evidence()
            )
        )

        with self.assertRaises(
            SourceQualityReproducibilityInvariantError
        ):
            result.apply_to_factors(
                self.factors()
            )

    def test_non_rx_evidence_is_rejected(
        self,
    ):
        evidence = self.evidence()
        evidence.council = CouncilId.IT

        with self.assertRaises(
            TechnologyRadarInvariantError
        ):
            (
                SourceQualityReproducibilityEvaluator
                .evaluate(
                    evidence
                )
            )

    def test_high_quality_and_reproducibility_do_not_assert_truth(
        self,
    ):
        result = (
            SourceQualityReproducibilityEvaluator
            .evaluate(
                self.evidence(
                    author="Researcher",
                    license="MIT",
                    version="1.0",
                ),
                independent_sources=[
                    "a",
                    "b",
                ],
                reproduction_requirements=[
                    "code",
                    "dataset",
                ],
                reproduction_support=[
                    "code",
                    "dataset",
                ],
            )
        )

        self.assertEqual(
            result.source_quality,
            1.0,
        )

        self.assertEqual(
            result.reproducibility,
            1.0,
        )

        self.assertFalse(
            result.system_truth_asserted
        )

    def test_module_has_no_network_learning_or_activation_imports(
        self,
    ):
        path = Path(
            "src/maestro/research/"
            "source_quality_reproducibility.py"
        )

        tree = ast.parse(
            path.read_text(
                encoding="utf-8"
            )
        )

        imported = set()

        for node in ast.walk(tree):
            if isinstance(
                node,
                ast.Import,
            ):
                for alias in node.names:
                    imported.add(
                        alias.name
                    )

            elif isinstance(
                node,
                ast.ImportFrom,
            ):
                if node.module:
                    imported.add(
                        node.module
                    )

        forbidden = (
            "socket",
            "http",
            "urllib",
            "requests",
            "subprocess",
            "maestro.learning",
            "maestro.adaptive",
            (
                "maestro."
                "outcome_governed_adaptation"
            ),
            (
                "maestro."
                "governed_activation"
            ),
            "maestro.tools",
            "maestro.autonomous",
        )

        violations = sorted(
            name
            for name in imported
            if any(
                name == prefix
                or name.startswith(
                    prefix + "."
                )
                for prefix in forbidden
            )
        )

        self.assertEqual(
            violations,
            [],
        )


if __name__ == "__main__":
    unittest.main()
