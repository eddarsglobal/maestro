from __future__ import annotations

import ast
import unittest

from pathlib import Path

from maestro.research import (
    CapabilityIntegrationEvaluation,
    NoveltyRelevanceEvaluation,
    RadarFactorComposer,
    RadarFactorComposition,
    RadarFactorCompositionInvariantError,
    SecurityRiskEvaluation,
    SourceQualityReproducibilityEvaluation,
)


class RadarFactorCompositionTests(
    unittest.TestCase
):
    def novelty_relevance(
        self,
        *,
        evidence_id="E-1",
        relevance=0.80,
    ):
        return NoveltyRelevanceEvaluation(
            evidence_id=evidence_id,
            novelty=0.90,
            relevance_to_maestro=relevance,
            exact_match=False,
            max_known_similarity=0.10,
            matched_relevance_terms=(
                "maestro",
            ),
        )

    def capability_integration(
        self,
        *,
        evidence_id="E-1",
        gain=0.75,
        cost=0.20,
    ):
        return CapabilityIntegrationEvaluation(
            evidence_id=evidence_id,
            expected_capability_gain=gain,
            integration_cost=cost,
            target_capability_terms=(
                "reasoning",
            ),
            novel_capability_terms=(
                "reasoning",
            ),
            matched_novel_capability_terms=(
                "reasoning",
            ),
            integration_requirements=(
                "python",
            ),
            unsupported_integration_requirements=(),
        )

    def source_quality_reproducibility(
        self,
        *,
        evidence_id="E-1",
        quality=0.85,
        reproducibility=0.70,
    ):
        return SourceQualityReproducibilityEvaluation(
            evidence_id=evidence_id,
            source_quality=quality,
            reproducibility=reproducibility,
            artifact_count=1,
            digest_coverage=1.0,
            metadata_coverage=0.50,
            independent_source_count=1,
            reproduction_requirement_count=2,
            reproduction_support_count=1,
            unsupported_reproduction_requirements=(
                "dataset",
            ),
        )

    def security_risk(
        self,
        *,
        evidence_id="E-1",
        risk=0.25,
    ):
        return SecurityRiskEvaluation(
            evidence_id=evidence_id,
            security_risk=risk,
            risk_signals=(
                "network",
                "execution",
            ),
            mitigated_risk_signals=(
                "network",
            ),
            unmitigated_risk_signals=(
                "execution",
            ),
            mitigation_count=1,
            residual_risk_ratio=risk,
        )

    def test_complete_composition_produces_all_seven_factors(
        self,
    ):
        factors = RadarFactorComposer.compose(
            novelty_relevance=(
                self.novelty_relevance()
            ),
            capability_integration=(
                self.capability_integration()
            ),
            source_quality_reproducibility=(
                self.source_quality_reproducibility()
            ),
            security_risk=(
                self.security_risk()
            ),
        )

        self.assertEqual(
            factors.novelty,
            0.90,
        )

        self.assertEqual(
            factors.source_quality,
            0.85,
        )

        self.assertEqual(
            factors.relevance_to_maestro,
            0.80,
        )

        self.assertEqual(
            factors.expected_capability_gain,
            0.75,
        )

        self.assertEqual(
            factors.reproducibility,
            0.70,
        )

        self.assertEqual(
            factors.integration_cost,
            0.20,
        )

        self.assertEqual(
            factors.security_risk,
            0.25,
        )

    def test_composition_is_deterministic(
        self,
    ):
        kwargs = {
            "novelty_relevance": (
                self.novelty_relevance()
            ),
            "capability_integration": (
                self.capability_integration()
            ),
            "source_quality_reproducibility": (
                self.source_quality_reproducibility()
            ),
            "security_risk": (
                self.security_risk()
            ),
        }

        first = RadarFactorComposer.compose(
            **kwargs
        )

        second = RadarFactorComposer.compose(
            **kwargs
        )

        self.assertEqual(
            first,
            second,
        )

    def test_composition_preserves_priority_formula(
        self,
    ):
        factors = RadarFactorComposer.compose(
            novelty_relevance=(
                self.novelty_relevance()
            ),
            capability_integration=(
                self.capability_integration()
            ),
            source_quality_reproducibility=(
                self.source_quality_reproducibility()
            ),
            security_risk=(
                self.security_risk()
            ),
        )

        expected = (
            0.90
            * 0.85
            * 0.80
            * 0.75
            * 0.70
            / (
                (1.0 + 0.20)
                * (1.0 + 0.25)
            )
        )

        self.assertAlmostEqual(
            factors.priority_score,
            expected,
        )

    def test_mismatched_evidence_ids_are_rejected(
        self,
    ):
        with self.assertRaises(
            RadarFactorCompositionInvariantError
        ):
            RadarFactorComposer.compose(
                novelty_relevance=(
                    self.novelty_relevance(
                        evidence_id="E-1"
                    )
                ),
                capability_integration=(
                    self.capability_integration(
                        evidence_id="E-2"
                    )
                ),
                source_quality_reproducibility=(
                    self.source_quality_reproducibility(
                        evidence_id="E-1"
                    )
                ),
                security_risk=(
                    self.security_risk(
                        evidence_id="E-1"
                    )
                ),
            )

    def test_unknown_relevance_prevents_composition(
        self,
    ):
        with self.assertRaises(
            RadarFactorCompositionInvariantError
        ):
            RadarFactorComposer.compose(
                novelty_relevance=(
                    self.novelty_relevance(
                        relevance=None
                    )
                ),
                capability_integration=(
                    self.capability_integration()
                ),
                source_quality_reproducibility=(
                    self.source_quality_reproducibility()
                ),
                security_risk=(
                    self.security_risk()
                ),
            )

    def test_unknown_capability_gain_prevents_composition(
        self,
    ):
        with self.assertRaises(
            RadarFactorCompositionInvariantError
        ):
            RadarFactorComposer.compose(
                novelty_relevance=(
                    self.novelty_relevance()
                ),
                capability_integration=(
                    self.capability_integration(
                        gain=None
                    )
                ),
                source_quality_reproducibility=(
                    self.source_quality_reproducibility()
                ),
                security_risk=(
                    self.security_risk()
                ),
            )

    def test_unknown_integration_cost_prevents_composition(
        self,
    ):
        with self.assertRaises(
            RadarFactorCompositionInvariantError
        ):
            RadarFactorComposer.compose(
                novelty_relevance=(
                    self.novelty_relevance()
                ),
                capability_integration=(
                    self.capability_integration(
                        cost=None
                    )
                ),
                source_quality_reproducibility=(
                    self.source_quality_reproducibility()
                ),
                security_risk=(
                    self.security_risk()
                ),
            )

    def test_unknown_source_quality_prevents_composition(
        self,
    ):
        with self.assertRaises(
            RadarFactorCompositionInvariantError
        ):
            RadarFactorComposer.compose(
                novelty_relevance=(
                    self.novelty_relevance()
                ),
                capability_integration=(
                    self.capability_integration()
                ),
                source_quality_reproducibility=(
                    self.source_quality_reproducibility(
                        quality=None
                    )
                ),
                security_risk=(
                    self.security_risk()
                ),
            )

    def test_unknown_reproducibility_prevents_composition(
        self,
    ):
        with self.assertRaises(
            RadarFactorCompositionInvariantError
        ):
            RadarFactorComposer.compose(
                novelty_relevance=(
                    self.novelty_relevance()
                ),
                capability_integration=(
                    self.capability_integration()
                ),
                source_quality_reproducibility=(
                    self.source_quality_reproducibility(
                        reproducibility=None
                    )
                ),
                security_risk=(
                    self.security_risk()
                ),
            )

    def test_unknown_security_risk_prevents_composition(
        self,
    ):
        with self.assertRaises(
            RadarFactorCompositionInvariantError
        ):
            RadarFactorComposer.compose(
                novelty_relevance=(
                    self.novelty_relevance()
                ),
                capability_integration=(
                    self.capability_integration()
                ),
                source_quality_reproducibility=(
                    self.source_quality_reproducibility()
                ),
                security_risk=(
                    self.security_risk(
                        risk=None
                    )
                ),
            )

    def test_composition_object_reports_complete(
        self,
    ):
        composition = RadarFactorComposition(
            novelty_relevance=(
                self.novelty_relevance()
            ),
            capability_integration=(
                self.capability_integration()
            ),
            source_quality_reproducibility=(
                self.source_quality_reproducibility()
            ),
            security_risk=(
                self.security_risk()
            ),
        )

        self.assertTrue(
            composition.complete
        )

        self.assertEqual(
            composition.evidence_id,
            "E-1",
        )

    def test_composition_object_reports_incomplete(
        self,
    ):
        composition = RadarFactorComposition(
            novelty_relevance=(
                self.novelty_relevance(
                    relevance=None
                )
            ),
            capability_integration=(
                self.capability_integration()
            ),
            source_quality_reproducibility=(
                self.source_quality_reproducibility()
            ),
            security_risk=(
                self.security_risk()
            ),
        )

        self.assertFalse(
            composition.complete
        )

    def test_wrong_novelty_relevance_type_is_rejected(
        self,
    ):
        with self.assertRaises(
            TypeError
        ):
            RadarFactorComposer.compose(
                novelty_relevance=object(),
                capability_integration=(
                    self.capability_integration()
                ),
                source_quality_reproducibility=(
                    self.source_quality_reproducibility()
                ),
                security_risk=(
                    self.security_risk()
                ),
            )

    def test_wrong_capability_integration_type_is_rejected(
        self,
    ):
        with self.assertRaises(
            TypeError
        ):
            RadarFactorComposer.compose(
                novelty_relevance=(
                    self.novelty_relevance()
                ),
                capability_integration=object(),
                source_quality_reproducibility=(
                    self.source_quality_reproducibility()
                ),
                security_risk=(
                    self.security_risk()
                ),
            )

    def test_wrong_source_quality_type_is_rejected(
        self,
    ):
        with self.assertRaises(
            TypeError
        ):
            RadarFactorComposer.compose(
                novelty_relevance=(
                    self.novelty_relevance()
                ),
                capability_integration=(
                    self.capability_integration()
                ),
                source_quality_reproducibility=object(),
                security_risk=(
                    self.security_risk()
                ),
            )

    def test_wrong_security_risk_type_is_rejected(
        self,
    ):
        with self.assertRaises(
            TypeError
        ):
            RadarFactorComposer.compose(
                novelty_relevance=(
                    self.novelty_relevance()
                ),
                capability_integration=(
                    self.capability_integration()
                ),
                source_quality_reproducibility=(
                    self.source_quality_reproducibility()
                ),
                security_risk=object(),
            )

    def test_composition_does_not_assert_truth_or_authority(
        self,
    ):
        composition = RadarFactorComposition(
            novelty_relevance=(
                self.novelty_relevance()
            ),
            capability_integration=(
                self.capability_integration()
            ),
            source_quality_reproducibility=(
                self.source_quality_reproducibility()
            ),
            security_risk=(
                self.security_risk()
            ),
        )

        factors = composition.to_factors()

        self.assertIsNotNone(
            factors
        )

        self.assertEqual(
            composition.novelty_relevance
            .verification_status,
            "UNVERIFIED_EXTERNAL",
        )

        self.assertFalse(
            composition.novelty_relevance
            .system_truth_asserted
        )

        self.assertFalse(
            composition.capability_integration
            .system_truth_asserted
        )

        self.assertFalse(
            composition.source_quality_reproducibility
            .system_truth_asserted
        )

        self.assertFalse(
            composition.security_risk
            .system_truth_asserted
        )

    def test_module_has_no_network_learning_activation_or_authority_imports(
        self,
    ):
        path = Path(
            "src/maestro/research/"
            "radar_factor_composition.py"
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
