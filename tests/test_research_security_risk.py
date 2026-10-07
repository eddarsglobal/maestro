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
    SecurityRiskEvaluator,
    SecurityRiskInvariantError,
    SourceProvenance,
    TechnologyRadarInvariantError,
)


class SecurityRiskTests(
    unittest.TestCase
):
    def evidence(
        self,
    ):
        now = datetime.now(
            timezone.utc
        ).isoformat()

        source = ResearchSource(
            "https://example.com/"
            "adel06-source",
            label="ADEL0.6 source",
        )

        provenance = SourceProvenance(
            source_id=source.source_id,
            retrieved_at=now,
            digest=ContentDigest.from_bytes(
                b"ADEL0.6"
            ),
        )

        artifact = ExternalArtifact(
            source=source,
            provenance=provenance,
            artifact_kind="DOCUMENT",
            media_type="text/html",
        )

        claim = ResearchClaim(
            statement=(
                "External technology with "
                "security implications"
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
            source_quality=0.80,
            relevance_to_maestro=0.85,
            expected_capability_gain=0.75,
            reproducibility=0.70,
            integration_cost=0.20,
            security_risk=0.10,
        )

    def test_missing_risk_context_is_unknown(
        self,
    ):
        result = (
            SecurityRiskEvaluator
            .evaluate(
                self.evidence()
            )
        )

        self.assertIsNone(
            result.security_risk
        )

        self.assertFalse(
            result.security_risk_known
        )

    def test_unknown_risk_is_not_zero(
        self,
    ):
        unknown = (
            SecurityRiskEvaluator
            .evaluate(
                self.evidence()
            )
        )

        explicit_zero = (
            SecurityRiskEvaluator
            .evaluate(
                self.evidence(),
                risk_signals=[
                    "network"
                ],
                mitigations=[
                    "network"
                ],
            )
        )

        self.assertIsNone(
            unknown.security_risk
        )

        self.assertEqual(
            explicit_zero.security_risk,
            0.0,
        )

    def test_unmitigated_signal_has_maximum_risk(
        self,
    ):
        result = (
            SecurityRiskEvaluator
            .evaluate(
                self.evidence(),
                risk_signals=[
                    "network"
                ],
            )
        )

        self.assertEqual(
            result.security_risk,
            1.0,
        )

    def test_fully_mitigated_signal_has_zero_risk(
        self,
    ):
        result = (
            SecurityRiskEvaluator
            .evaluate(
                self.evidence(),
                risk_signals=[
                    "network"
                ],
                mitigations=[
                    "network"
                ],
            )
        )

        self.assertEqual(
            result.security_risk,
            0.0,
        )

    def test_partial_mitigation_produces_partial_risk(
        self,
    ):
        result = (
            SecurityRiskEvaluator
            .evaluate(
                self.evidence(),
                risk_signals=[
                    "network",
                    "filesystem",
                    "execution",
                    "credentials",
                ],
                mitigations=[
                    "network",
                    "filesystem",
                ],
            )
        )

        self.assertEqual(
            result.security_risk,
            0.5,
        )

    def test_duplicate_signals_do_not_inflate_risk(
        self,
    ):
        result = (
            SecurityRiskEvaluator
            .evaluate(
                self.evidence(),
                risk_signals=[
                    "network",
                    "network",
                    "execution",
                ],
                mitigations=[
                    "network"
                ],
            )
        )

        self.assertEqual(
            result.security_risk,
            0.5,
        )

        self.assertEqual(
            result.risk_signals,
            (
                "execution",
                "network",
            ),
        )

    def test_irrelevant_mitigation_does_not_reduce_risk(
        self,
    ):
        result = (
            SecurityRiskEvaluator
            .evaluate(
                self.evidence(),
                risk_signals=[
                    "network",
                    "execution",
                ],
                mitigations=[
                    "unrelated"
                ],
            )
        )

        self.assertEqual(
            result.security_risk,
            1.0,
        )

    def test_evaluation_is_deterministic(
        self,
    ):
        evidence = self.evidence()

        kwargs = {
            "risk_signals": [
                "network",
                "filesystem",
                "execution",
            ],
            "mitigations": [
                "network"
            ],
        }

        first = (
            SecurityRiskEvaluator
            .evaluate(
                evidence,
                **kwargs,
            )
        )

        second = (
            SecurityRiskEvaluator
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
            SecurityRiskEvaluator
            .evaluate(
                self.evidence(),
                risk_signals=[
                    "network",
                    "filesystem",
                    "execution",
                ],
                mitigations=[
                    "network"
                ],
            )
        )

        self.assertGreaterEqual(
            result.security_risk,
            0.0,
        )

        self.assertLessEqual(
            result.security_risk,
            1.0,
        )

        self.assertGreaterEqual(
            result.residual_risk_ratio,
            0.0,
        )

        self.assertLessEqual(
            result.residual_risk_ratio,
            1.0,
        )

    def test_evidence_is_not_mutated(
        self,
    ):
        evidence = self.evidence()

        original = copy.deepcopy(
            evidence
        )

        SecurityRiskEvaluator.evaluate(
            evidence,
            risk_signals=[
                "network"
            ],
            mitigations=[
                "network"
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
            SecurityRiskEvaluator
            .evaluate(
                self.evidence(),
                risk_signals=[
                    "network"
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

    def test_zero_security_risk_is_not_truth(
        self,
    ):
        result = (
            SecurityRiskEvaluator
            .evaluate(
                self.evidence(),
                risk_signals=[
                    "network",
                    "execution",
                ],
                mitigations=[
                    "network",
                    "execution",
                ],
            )
        )

        self.assertEqual(
            result.security_risk,
            0.0,
        )

        self.assertFalse(
            result.system_truth_asserted
        )

    def test_maximum_security_risk_is_not_rejection_authority(
        self,
    ):
        result = (
            SecurityRiskEvaluator
            .evaluate(
                self.evidence(),
                risk_signals=[
                    "network",
                    "execution",
                ],
            )
        )

        self.assertEqual(
            result.security_risk,
            1.0,
        )

        self.assertEqual(
            result.verification_status,
            "UNVERIFIED_EXTERNAL",
        )

        self.assertFalse(
            result.system_truth_asserted
        )

    def test_apply_replaces_only_security_risk(
        self,
    ):
        result = (
            SecurityRiskEvaluator
            .evaluate(
                self.evidence(),
                risk_signals=[
                    "network",
                    "execution",
                ],
                mitigations=[
                    "network"
                ],
            )
        )

        before = self.factors()

        after = result.apply_to_factors(
            before
        )

        self.assertEqual(
            after.security_risk,
            result.security_risk,
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
            after.expected_capability_gain,
            before.expected_capability_gain,
        )

        self.assertEqual(
            after.reproducibility,
            before.reproducibility,
        )

        self.assertEqual(
            after.integration_cost,
            before.integration_cost,
        )

    def test_unknown_risk_cannot_be_silently_applied(
        self,
    ):
        result = (
            SecurityRiskEvaluator
            .evaluate(
                self.evidence()
            )
        )

        with self.assertRaises(
            SecurityRiskInvariantError
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
                SecurityRiskEvaluator
                .evaluate(
                    evidence
                )
            )

    def test_inputs_are_case_normalized(
        self,
    ):
        result = (
            SecurityRiskEvaluator
            .evaluate(
                self.evidence(),
                risk_signals=[
                    "NETWORK",
                    "Execution",
                ],
                mitigations=[
                    "network"
                ],
            )
        )

        self.assertEqual(
            result.risk_signals,
            (
                "execution",
                "network",
            ),
        )

        self.assertEqual(
            result.security_risk,
            0.5,
        )

    def test_module_has_no_network_learning_activation_or_authority_imports(
        self,
    ):
        path = Path(
            "src/maestro/research/"
            "security_risk.py"
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
