from __future__ import annotations

import ast
import unittest

from datetime import (
    datetime,
    timezone,
)
from pathlib import Path

from maestro.research import (
    ContentDigest,
    ExternalArtifact,
    GovernedRadarDecisionEnvelope,
    GovernedRadarEvaluationPipeline,
    GovernedRadarPortfolio,
    RadarDecisionEnvelopeInvariantError,
    RadarDecisionPolicy,
    RadarDisposition,
    RadarPortfolioEntry,
    ResearchClaim,
    ResearchEvidenceBridge,
    ResearchSource,
    SourceProvenance,
)


class RadarDecisionEnvelopeTests(
    unittest.TestCase
):
    def evidence(
        self,
        *,
        statement: str,
        suffix: str,
    ):
        now = datetime.now(
            timezone.utc
        ).isoformat()

        source = ResearchSource(
            (
                "https://example.com/"
                f"adel010-{suffix}"
            ),
            label=(
                f"ADEL0.10 {suffix}"
            ),
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
        *,
        risk_signals=(
            "network",
            "execution",
        ),
        mitigations=(
            "network",
        ),
    ):
        return (
            GovernedRadarEvaluationPipeline
            .context(
                known_claims=[
                    "legacy baseline"
                ],
                relevance_terms=[
                    "MAESTRO",
                    "research",
                ],
                capability_terms=[
                    "GPU",
                    "reasoning",
                ],
                existing_capabilities=(),
                integration_requirements=[
                    "python"
                ],
                available_integration_support=[
                    "python"
                ],
                independent_sources=[
                    "source-a",
                    "source-b",
                ],
                reproduction_requirements=[
                    "code"
                ],
                reproduction_support=[
                    "code"
                ],
                risk_signals=risk_signals,
                mitigations=mitigations,
            )
        )

    def entry(
        self,
        *,
        suffix: str,
        context=None,
    ):
        return RadarPortfolioEntry(
            evidence=self.evidence(
                statement=(
                    "GPU reasoning improves "
                    "MAESTRO research"
                ),
                suffix=suffix,
            ),
            context=(
                context
                if context is not None
                else self.context()
            ),
        )

    def portfolio(
        self,
        count=1,
    ):
        entries = tuple(
            self.entry(
                suffix=str(index)
            )
            for index in range(count)
        )

        return (
            GovernedRadarPortfolio()
            .evaluate(entries)
        )

    def test_valid_policy(
        self,
    ):
        policy = RadarDecisionPolicy(
            investigate_min_priority=0.20,
            review_min_priority=0.50,
        )

        self.assertEqual(
            policy.investigate_min_priority,
            0.20,
        )

        self.assertEqual(
            policy.review_min_priority,
            0.50,
        )

    def test_negative_investigate_threshold_rejected(
        self,
    ):
        with self.assertRaises(
            RadarDecisionEnvelopeInvariantError
        ):
            RadarDecisionPolicy(
                investigate_min_priority=-0.1,
                review_min_priority=0.5,
            )

    def test_review_threshold_above_one_rejected(
        self,
    ):
        with self.assertRaises(
            RadarDecisionEnvelopeInvariantError
        ):
            RadarDecisionPolicy(
                investigate_min_priority=0.1,
                review_min_priority=1.1,
            )

    def test_investigate_above_review_rejected(
        self,
    ):
        with self.assertRaises(
            RadarDecisionEnvelopeInvariantError
        ):
            RadarDecisionPolicy(
                investigate_min_priority=0.8,
                review_min_priority=0.2,
            )

    def test_boolean_threshold_rejected(
        self,
    ):
        with self.assertRaises(
            TypeError
        ):
            RadarDecisionPolicy(
                investigate_min_priority=True,
                review_min_priority=0.5,
            )

    def test_empty_portfolio_produces_empty_envelope(
        self,
    ):
        portfolio = self.portfolio(
            count=0
        )

        result = (
            GovernedRadarDecisionEnvelope
            .evaluate(
                portfolio,
                policy=RadarDecisionPolicy(
                    investigate_min_priority=0.2,
                    review_min_priority=0.5,
                ),
            )
        )

        self.assertEqual(
            result.size,
            0,
        )

    def test_observe_disposition(
        self,
    ):
        portfolio = self.portfolio()

        result = (
            GovernedRadarDecisionEnvelope
            .evaluate(
                portfolio,
                policy=RadarDecisionPolicy(
                    investigate_min_priority=1.0,
                    review_min_priority=1.0,
                ),
            )
        )

        self.assertEqual(
            result.entries[0].disposition,
            RadarDisposition.OBSERVE,
        )

    def test_investigate_disposition(
        self,
    ):
        portfolio = self.portfolio()

        result = (
            GovernedRadarDecisionEnvelope
            .evaluate(
                portfolio,
                policy=RadarDecisionPolicy(
                    investigate_min_priority=0.0,
                    review_min_priority=1.0,
                ),
            )
        )

        self.assertEqual(
            result.entries[0].disposition,
            RadarDisposition.INVESTIGATE,
        )

    def test_review_disposition(
        self,
    ):
        portfolio = self.portfolio()

        result = (
            GovernedRadarDecisionEnvelope
            .evaluate(
                portfolio,
                policy=RadarDecisionPolicy(
                    investigate_min_priority=0.0,
                    review_min_priority=0.0,
                ),
            )
        )

        self.assertEqual(
            result.entries[0].disposition,
            RadarDisposition.REVIEW,
        )

    def test_investigate_boundary_is_inclusive(
        self,
    ):
        portfolio = self.portfolio()

        score = (
            portfolio.ranked_observations[0]
            .priority_score
        )

        result = (
            GovernedRadarDecisionEnvelope
            .evaluate(
                portfolio,
                policy=RadarDecisionPolicy(
                    investigate_min_priority=score,
                    review_min_priority=1.0,
                ),
            )
        )

        self.assertEqual(
            result.entries[0].disposition,
            RadarDisposition.INVESTIGATE,
        )

    def test_review_boundary_is_inclusive(
        self,
    ):
        portfolio = self.portfolio()

        score = (
            portfolio.ranked_observations[0]
            .priority_score
        )

        result = (
            GovernedRadarDecisionEnvelope
            .evaluate(
                portfolio,
                policy=RadarDecisionPolicy(
                    investigate_min_priority=0.0,
                    review_min_priority=score,
                ),
            )
        )

        self.assertEqual(
            result.entries[0].disposition,
            RadarDisposition.REVIEW,
        )

    def test_envelope_preserves_portfolio_order(
        self,
    ):
        portfolio = (
            GovernedRadarPortfolio()
            .evaluate(
                (
                    self.entry(
                        suffix="low",
                        context=self.context(
                            risk_signals=(
                                "network",
                            ),
                            mitigations=(),
                        ),
                    ),
                    self.entry(
                        suffix="high",
                        context=self.context(
                            risk_signals=(
                                "network",
                            ),
                            mitigations=(
                                "network",
                            ),
                        ),
                    ),
                )
            )
        )

        result = (
            GovernedRadarDecisionEnvelope
            .evaluate(
                portfolio,
                policy=RadarDecisionPolicy(
                    investigate_min_priority=0.0,
                    review_min_priority=1.0,
                ),
            )
        )

        expected = tuple(
            observation.evidence_id
            for observation
            in portfolio.ranked_observations
        )

        self.assertEqual(
            result.evidence_ids,
            expected,
        )

    def test_envelope_is_deterministic(
        self,
    ):
        portfolio = self.portfolio(
            count=2
        )

        policy = RadarDecisionPolicy(
            investigate_min_priority=0.1,
            review_min_priority=0.5,
        )

        first = (
            GovernedRadarDecisionEnvelope
            .evaluate(
                portfolio,
                policy=policy,
            )
        )

        second = (
            GovernedRadarDecisionEnvelope
            .evaluate(
                portfolio,
                policy=policy,
            )
        )

        self.assertEqual(
            first,
            second,
        )

    def test_envelope_preserves_evidence_ids(
        self,
    ):
        portfolio = self.portfolio(
            count=2
        )

        result = (
            GovernedRadarDecisionEnvelope
            .evaluate(
                portfolio,
                policy=RadarDecisionPolicy(
                    investigate_min_priority=0.0,
                    review_min_priority=1.0,
                ),
            )
        )

        self.assertEqual(
            set(result.evidence_ids),
            {
                observation.evidence_id
                for observation
                in portfolio.ranked_observations
            },
        )

    def test_envelope_preserves_unverified_boundary(
        self,
    ):
        result = (
            GovernedRadarDecisionEnvelope
            .evaluate(
                self.portfolio(),
                policy=RadarDecisionPolicy(
                    investigate_min_priority=0.0,
                    review_min_priority=1.0,
                ),
            )
        )

        for entry in result.entries:
            self.assertEqual(
                entry.verification_status,
                "UNVERIFIED_EXTERNAL",
            )

            self.assertFalse(
                entry.system_truth_asserted
            )

    def test_wrong_portfolio_type_rejected(
        self,
    ):
        with self.assertRaises(
            TypeError
        ):
            (
                GovernedRadarDecisionEnvelope
                .evaluate(
                    object(),
                    policy=RadarDecisionPolicy(
                        investigate_min_priority=0.1,
                        review_min_priority=0.5,
                    ),
                )
            )

    def test_wrong_policy_type_rejected(
        self,
    ):
        with self.assertRaises(
            TypeError
        ):
            (
                GovernedRadarDecisionEnvelope
                .evaluate(
                    self.portfolio(),
                    policy=object(),
                )
            )

    def test_module_has_no_activation_promotion_learning_or_network_imports(
        self,
    ):
        path = Path(
            "src/maestro/research/"
            "radar_decision_envelope.py"
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
            "maestro.governance",
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
