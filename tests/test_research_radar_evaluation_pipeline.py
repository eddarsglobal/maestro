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
    GovernedRadarEvaluationPipeline,
    RadarEvaluationContext,
    ResearchClaim,
    ResearchEvidenceBridge,
    ResearchSource,
    SourceProvenance,
    TechnologyRadarInvariantError,
)


class RadarEvaluationPipelineTests(
    unittest.TestCase
):
    def evidence(
        self,
        statement=(
            "GPU semantic reasoning runtime "
            "improves MAESTRO research"
        ),
    ):
        now = datetime.now(
            timezone.utc
        ).isoformat()

        source = ResearchSource(
            "https://example.com/"
            "adel08-source",
            label="ADEL0.8 source",
        )

        provenance = SourceProvenance(
            source_id=source.source_id,
            retrieved_at=now,
            digest=ContentDigest.from_bytes(
                statement.encode(
                    "utf-8"
                )
            ),
            author="Researcher",
            license="MIT",
            version="1.0",
        )

        artifact = ExternalArtifact(
            source=source,
            provenance=provenance,
            artifact_kind="DOCUMENT",
            media_type="text/html",
        )

        claim = ResearchClaim(
            statement=statement,
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

    def context(
        self,
    ):
        return (
            GovernedRadarEvaluationPipeline
            .context(
                known_claims=[
                    "Legacy CPU research"
                ],
                relevance_terms=[
                    "MAESTRO",
                    "research",
                ],
                capability_terms=[
                    "GPU",
                    "semantic",
                    "reasoning",
                ],
                existing_capabilities=[
                    "semantic",
                ],
                integration_requirements=[
                    "python",
                    "runtime",
                ],
                available_integration_support=[
                    "python",
                ],
                independent_sources=[
                    "source-a",
                    "source-b",
                ],
                reproduction_requirements=[
                    "code",
                    "steps",
                ],
                reproduction_support=[
                    "code",
                ],
                risk_signals=[
                    "network",
                    "execution",
                ],
                mitigations=[
                    "network",
                ],
            )
        )

    def test_pipeline_produces_observation(
        self,
    ):
        result = (
            GovernedRadarEvaluationPipeline()
            .evaluate(
                self.evidence(),
                context=self.context(),
            )
        )

        self.assertEqual(
            result.observation.evidence_id,
            result.evidence_id,
        )

    def test_pipeline_produces_all_seven_factors(
        self,
    ):
        result = (
            GovernedRadarEvaluationPipeline()
            .evaluate(
                self.evidence(),
                context=self.context(),
            )
        )

        factors = result.factors

        values = (
            factors.novelty,
            factors.source_quality,
            factors.relevance_to_maestro,
            factors.expected_capability_gain,
            factors.reproducibility,
            factors.integration_cost,
            factors.security_risk,
        )

        self.assertEqual(
            len(values),
            7,
        )

        for value in values:
            self.assertGreaterEqual(
                value,
                0.0,
            )

            self.assertLessEqual(
                value,
                1.0,
            )

    def test_pipeline_priority_matches_factors(
        self,
    ):
        result = (
            GovernedRadarEvaluationPipeline()
            .evaluate(
                self.evidence(),
                context=self.context(),
            )
        )

        self.assertEqual(
            result.observation.priority_score,
            result.factors.priority_score,
        )

    def test_pipeline_preserves_evidence_identity(
        self,
    ):
        evidence = self.evidence()

        result = (
            GovernedRadarEvaluationPipeline()
            .evaluate(
                evidence,
                context=self.context(),
            )
        )

        self.assertEqual(
            result.evidence_id,
            evidence.evidence_id,
        )

        self.assertEqual(
            result.observation.task_id,
            evidence.task_id,
        )

        self.assertEqual(
            result.observation.source_ref,
            evidence.source_ref,
        )

        self.assertEqual(
            result.observation.claim,
            evidence.claim,
        )

    def test_pipeline_is_deterministic(
        self,
    ):
        evidence = self.evidence()
        context = self.context()

        pipeline = (
            GovernedRadarEvaluationPipeline()
        )

        first = pipeline.evaluate(
            evidence,
            context=context,
        )

        second = pipeline.evaluate(
            evidence,
            context=context,
        )

        self.assertEqual(
            first,
            second,
        )

    def test_pipeline_does_not_mutate_evidence(
        self,
    ):
        evidence = self.evidence()
        original = copy.deepcopy(
            evidence
        )

        (
            GovernedRadarEvaluationPipeline()
            .evaluate(
                evidence,
                context=self.context(),
            )
        )

        self.assertEqual(
            evidence,
            original,
        )

    def test_pipeline_preserves_unverified_boundary(
        self,
    ):
        result = (
            GovernedRadarEvaluationPipeline()
            .evaluate(
                self.evidence(),
                context=self.context(),
            )
        )

        self.assertEqual(
            result.observation
            .verification_status,
            "UNVERIFIED_EXTERNAL",
        )

        self.assertFalse(
            result.observation
            .system_truth_asserted
        )

    def test_pipeline_does_not_assert_truth(
        self,
    ):
        result = (
            GovernedRadarEvaluationPipeline()
            .evaluate(
                self.evidence(),
                context=self.context(),
            )
        )

        self.assertFalse(
            result.novelty_relevance
            .system_truth_asserted
        )

        self.assertFalse(
            result.capability_integration
            .system_truth_asserted
        )

        self.assertFalse(
            result.source_quality_reproducibility
            .system_truth_asserted
        )

        self.assertFalse(
            result.security_risk
            .system_truth_asserted
        )

        self.assertFalse(
            result.observation
            .system_truth_asserted
        )

    def test_missing_relevance_fails_closed(
        self,
    ):
        context = (
            GovernedRadarEvaluationPipeline
            .context(
                capability_terms=[
                    "GPU"
                ],
                integration_requirements=[
                    "python"
                ],
                available_integration_support=[
                    "python"
                ],
                reproduction_requirements=[
                    "code"
                ],
                reproduction_support=[
                    "code"
                ],
                risk_signals=[
                    "network"
                ],
                mitigations=[
                    "network"
                ],
            )
        )

        with self.assertRaises(
            ValueError
        ):
            (
                GovernedRadarEvaluationPipeline()
                .evaluate(
                    self.evidence(),
                    context=context,
                )
            )

    def test_missing_capability_context_fails_closed(
        self,
    ):
        context = (
            GovernedRadarEvaluationPipeline
            .context(
                relevance_terms=[
                    "MAESTRO"
                ],
                integration_requirements=[
                    "python"
                ],
                available_integration_support=[
                    "python"
                ],
                reproduction_requirements=[
                    "code"
                ],
                reproduction_support=[
                    "code"
                ],
                risk_signals=[
                    "network"
                ],
                mitigations=[
                    "network"
                ],
            )
        )

        with self.assertRaises(
            ValueError
        ):
            (
                GovernedRadarEvaluationPipeline()
                .evaluate(
                    self.evidence(),
                    context=context,
                )
            )

    def test_missing_integration_context_fails_closed(
        self,
    ):
        context = (
            GovernedRadarEvaluationPipeline
            .context(
                relevance_terms=[
                    "MAESTRO"
                ],
                capability_terms=[
                    "GPU"
                ],
                reproduction_requirements=[
                    "code"
                ],
                reproduction_support=[
                    "code"
                ],
                risk_signals=[
                    "network"
                ],
                mitigations=[
                    "network"
                ],
            )
        )

        with self.assertRaises(
            ValueError
        ):
            (
                GovernedRadarEvaluationPipeline()
                .evaluate(
                    self.evidence(),
                    context=context,
                )
            )

    def test_missing_reproduction_context_fails_closed(
        self,
    ):
        context = (
            GovernedRadarEvaluationPipeline
            .context(
                relevance_terms=[
                    "MAESTRO"
                ],
                capability_terms=[
                    "GPU"
                ],
                integration_requirements=[
                    "python"
                ],
                available_integration_support=[
                    "python"
                ],
                risk_signals=[
                    "network"
                ],
                mitigations=[
                    "network"
                ],
            )
        )

        with self.assertRaises(
            ValueError
        ):
            (
                GovernedRadarEvaluationPipeline()
                .evaluate(
                    self.evidence(),
                    context=context,
                )
            )

    def test_missing_security_context_fails_closed(
        self,
    ):
        context = (
            GovernedRadarEvaluationPipeline
            .context(
                relevance_terms=[
                    "MAESTRO"
                ],
                capability_terms=[
                    "GPU"
                ],
                integration_requirements=[
                    "python"
                ],
                available_integration_support=[
                    "python"
                ],
                reproduction_requirements=[
                    "code"
                ],
                reproduction_support=[
                    "code"
                ],
            )
        )

        with self.assertRaises(
            ValueError
        ):
            (
                GovernedRadarEvaluationPipeline()
                .evaluate(
                    self.evidence(),
                    context=context,
                )
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
                GovernedRadarEvaluationPipeline()
                .evaluate(
                    evidence,
                    context=self.context(),
                )
            )

    def test_context_materializes_iterables(
        self,
    ):
        context = (
            GovernedRadarEvaluationPipeline
            .context(
                known_claims=(
                    value
                    for value in (
                        "one",
                        "two",
                    )
                ),
            )
        )

        self.assertEqual(
            context.known_claims,
            (
                "one",
                "two",
            ),
        )

    def test_context_rejects_string_as_iterable(
        self,
    ):
        with self.assertRaises(
            TypeError
        ):
            (
                GovernedRadarEvaluationPipeline
                .context(
                    known_claims="invalid"
                )
            )

    def test_wrong_context_type_is_rejected(
        self,
    ):
        with self.assertRaises(
            TypeError
        ):
            (
                GovernedRadarEvaluationPipeline()
                .evaluate(
                    self.evidence(),
                    context=object(),
                )
            )

    def test_module_has_no_network_learning_activation_or_authority_imports(
        self,
    ):
        path = Path(
            "src/maestro/research/"
            "radar_evaluation_pipeline.py"
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
            "maestro.strategic_adaptation",
            "maestro.outcome_governed_adaptation",
            "maestro.governed_activation",
            "maestro.tools",
            "maestro.autonomous",
            "maestro.sovereign",
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
