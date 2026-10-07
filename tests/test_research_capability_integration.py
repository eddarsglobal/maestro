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
    CapabilityIntegrationEvaluator,
    CapabilityIntegrationInvariantError,
    ContentDigest,
    ExternalArtifact,
    RadarFactors,
    ResearchClaim,
    ResearchEvidenceBridge,
    ResearchSource,
    SourceProvenance,
    TechnologyRadarInvariantError,
)


class CapabilityIntegrationTests(
    unittest.TestCase
):
    def evidence(
        self,
        statement=(
            "Local GPU inference adds semantic "
            "reasoning and research capability"
        ),
    ):
        now = datetime.now(
            timezone.utc
        ).isoformat()

        source = ResearchSource(
            "https://example.com/"
            "adel04-source",
            label="ADEL0.4 source",
        )

        provenance = SourceProvenance(
            source_id=source.source_id,
            retrieved_at=now,
            digest=ContentDigest.from_bytes(
                statement.encode("utf-8")
            ),
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

    def factors(
        self,
    ):
        return RadarFactors(
            novelty=0.90,
            source_quality=0.80,
            relevance_to_maestro=0.85,
            expected_capability_gain=0.10,
            reproducibility=0.70,
            integration_cost=0.90,
            security_risk=0.20,
        )

    def test_matching_new_capabilities_produce_full_gain(
        self,
    ):
        result = (
            CapabilityIntegrationEvaluator
            .evaluate(
                self.evidence(),
                capability_terms=[
                    "GPU",
                    "semantic",
                    "reasoning",
                ],
            )
        )

        self.assertEqual(
            result.expected_capability_gain,
            1.0,
        )

    def test_missing_capability_context_is_unknown(
        self,
    ):
        result = (
            CapabilityIntegrationEvaluator
            .evaluate(
                self.evidence(),
            )
        )

        self.assertIsNone(
            result.expected_capability_gain
        )

        self.assertFalse(
            result.capability_gain_known
        )

    def test_existing_capability_is_not_counted_as_gain(
        self,
    ):
        result = (
            CapabilityIntegrationEvaluator
            .evaluate(
                self.evidence(),
                capability_terms=[
                    "GPU",
                    "semantic",
                ],
                existing_capabilities=[
                    "GPU",
                    "semantic",
                ],
            )
        )

        self.assertEqual(
            result.expected_capability_gain,
            0.0,
        )

        self.assertEqual(
            result.novel_capability_terms,
            (),
        )

    def test_partial_capability_match_produces_partial_gain(
        self,
    ):
        result = (
            CapabilityIntegrationEvaluator
            .evaluate(
                self.evidence(),
                capability_terms=[
                    "GPU",
                    "semantic",
                    "reasoning",
                    "vision",
                ],
            )
        )

        self.assertGreater(
            result.expected_capability_gain,
            0.0,
        )

        self.assertLess(
            result.expected_capability_gain,
            1.0,
        )

    def test_full_integration_support_has_zero_cost(
        self,
    ):
        result = (
            CapabilityIntegrationEvaluator
            .evaluate(
                self.evidence(),
                integration_requirements=[
                    "python",
                    "gpu",
                ],
                available_integration_support=[
                    "python",
                    "gpu",
                ],
            )
        )

        self.assertEqual(
            result.integration_cost,
            0.0,
        )

    def test_no_integration_support_has_maximum_cost(
        self,
    ):
        result = (
            CapabilityIntegrationEvaluator
            .evaluate(
                self.evidence(),
                integration_requirements=[
                    "python",
                    "gpu",
                ],
                available_integration_support=[],
            )
        )

        self.assertEqual(
            result.integration_cost,
            1.0,
        )

    def test_partial_support_produces_partial_cost(
        self,
    ):
        result = (
            CapabilityIntegrationEvaluator
            .evaluate(
                self.evidence(),
                integration_requirements=[
                    "python",
                    "gpu",
                    "runtime",
                    "driver",
                ],
                available_integration_support=[
                    "python",
                    "runtime",
                ],
            )
        )

        self.assertEqual(
            result.integration_cost,
            0.5,
        )

    def test_missing_integration_requirements_is_unknown(
        self,
    ):
        result = (
            CapabilityIntegrationEvaluator
            .evaluate(
                self.evidence(),
            )
        )

        self.assertIsNone(
            result.integration_cost
        )

        self.assertFalse(
            result.integration_cost_known
        )

    def test_evaluation_is_deterministic(
        self,
    ):
        evidence = self.evidence()

        kwargs = {
            "capability_terms": [
                "GPU",
                "reasoning",
                "vision",
            ],
            "existing_capabilities": [
                "GPU",
            ],
            "integration_requirements": [
                "python",
                "driver",
            ],
            "available_integration_support": [
                "python",
            ],
        }

        first = (
            CapabilityIntegrationEvaluator
            .evaluate(
                evidence,
                **kwargs,
            )
        )

        second = (
            CapabilityIntegrationEvaluator
            .evaluate(
                evidence,
                **kwargs,
            )
        )

        self.assertEqual(
            first,
            second,
        )

    def test_scores_remain_bounded(
        self,
    ):
        result = (
            CapabilityIntegrationEvaluator
            .evaluate(
                self.evidence(),
                capability_terms=[
                    "GPU",
                    "reasoning",
                    "vision",
                ],
                integration_requirements=[
                    "python",
                    "driver",
                ],
                available_integration_support=[
                    "python",
                ],
            )
        )

        self.assertIsNotNone(
            result.expected_capability_gain
        )

        self.assertGreaterEqual(
            result.expected_capability_gain,
            0.0,
        )

        self.assertLessEqual(
            result.expected_capability_gain,
            1.0,
        )

        self.assertIsNotNone(
            result.integration_cost
        )

        self.assertGreaterEqual(
            result.integration_cost,
            0.0,
        )

        self.assertLessEqual(
            result.integration_cost,
            1.0,
        )

    def test_unverified_boundary_is_preserved(
        self,
    ):
        result = (
            CapabilityIntegrationEvaluator
            .evaluate(
                self.evidence(),
                capability_terms=[
                    "GPU"
                ],
                integration_requirements=[
                    "python"
                ],
                available_integration_support=[
                    "python"
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

    def test_evaluation_does_not_mutate_evidence(
        self,
    ):
        evidence = self.evidence()

        original = copy.deepcopy(
            evidence
        )

        CapabilityIntegrationEvaluator.evaluate(
            evidence,
            capability_terms=[
                "GPU"
            ],
            integration_requirements=[
                "python"
            ],
            available_integration_support=[
                "python"
            ],
        )

        self.assertEqual(
            evidence,
            original,
        )

    def test_apply_replaces_only_capability_and_cost_factors(
        self,
    ):
        result = (
            CapabilityIntegrationEvaluator
            .evaluate(
                self.evidence(),
                capability_terms=[
                    "GPU",
                    "reasoning",
                ],
                integration_requirements=[
                    "python",
                    "driver",
                ],
                available_integration_support=[
                    "python",
                ],
            )
        )

        before = self.factors()

        after = result.apply_to_factors(
            before
        )

        self.assertEqual(
            after.expected_capability_gain,
            result.expected_capability_gain,
        )

        self.assertEqual(
            after.integration_cost,
            result.integration_cost,
        )

        self.assertEqual(
            after.novelty,
            before.novelty,
        )

        self.assertEqual(
            after.source_quality,
            before.source_quality,
        )

        self.assertEqual(
            after.relevance_to_maestro,
            before.relevance_to_maestro,
        )

        self.assertEqual(
            after.reproducibility,
            before.reproducibility,
        )

        self.assertEqual(
            after.security_risk,
            before.security_risk,
        )

    def test_unknown_values_cannot_be_silently_applied(
        self,
    ):
        result = (
            CapabilityIntegrationEvaluator
            .evaluate(
                self.evidence()
            )
        )

        with self.assertRaises(
            CapabilityIntegrationInvariantError
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
                CapabilityIntegrationEvaluator
                .evaluate(
                    evidence
                )
            )

    def test_maximum_gain_and_minimum_cost_do_not_assert_truth(
        self,
    ):
        result = (
            CapabilityIntegrationEvaluator
            .evaluate(
                self.evidence(),
                capability_terms=[
                    "GPU",
                    "semantic",
                    "reasoning",
                    "research",
                    "capability",
                ],
                integration_requirements=[
                    "python",
                    "runtime",
                ],
                available_integration_support=[
                    "python",
                    "runtime",
                ],
            )
        )

        self.assertEqual(
            result.expected_capability_gain,
            1.0,
        )

        self.assertEqual(
            result.integration_cost,
            0.0,
        )

        self.assertFalse(
            result.system_truth_asserted
        )

        self.assertEqual(
            result.verification_status,
            "UNVERIFIED_EXTERNAL",
        )

    def test_module_has_no_network_learning_or_activation_imports(
        self,
    ):
        path = Path(
            "src/maestro/research/"
            "capability_integration.py"
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
