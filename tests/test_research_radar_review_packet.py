from __future__ import annotations

import ast
import copy
import unittest

from dataclasses import replace
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
    GovernedRadarReviewPacket,
    RadarDecisionEnvelope,
    RadarDecisionEntry,
    RadarDecisionPolicy,
    RadarDisposition,
    RadarPortfolioEntry,
    RadarReviewPacketInvariantError,
    ResearchClaim,
    ResearchEvidenceBridge,
    ResearchSource,
    SourceProvenance,
)


class RadarReviewPacketTests(
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
                f"adel011-{suffix}"
            ),
            label=(
                f"ADEL0.11 {suffix}"
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

    def bundle(
        self,
        *,
        count=1,
        policy=None,
    ):
        entries = tuple(
            self.entry(
                suffix=str(index)
            )
            for index in range(count)
        )

        portfolio = (
            GovernedRadarPortfolio()
            .evaluate(entries)
        )

        selected_policy = (
            policy
            if policy is not None
            else RadarDecisionPolicy(
                investigate_min_priority=0.0,
                review_min_priority=1.0,
            )
        )

        envelope = (
            GovernedRadarDecisionEnvelope
            .evaluate(
                portfolio,
                policy=selected_policy,
            )
        )

        return (
            portfolio,
            selected_policy,
            envelope,
        )

    def test_empty_packet(
        self,
    ):
        portfolio, policy, envelope = (
            self.bundle(
                count=0
            )
        )

        packet = (
            GovernedRadarReviewPacket
            .build(
                portfolio,
                envelope,
                policy=policy,
            )
        )

        self.assertEqual(
            packet.size,
            0,
        )

    def test_single_entry_packet(
        self,
    ):
        portfolio, policy, envelope = (
            self.bundle()
        )

        packet = (
            GovernedRadarReviewPacket
            .build(
                portfolio,
                envelope,
                policy=policy,
            )
        )

        self.assertEqual(
            packet.size,
            1,
        )

    def test_packet_preserves_ranking_order(
        self,
    ):
        portfolio, policy, envelope = (
            self.bundle(
                count=2
            )
        )

        packet = (
            GovernedRadarReviewPacket
            .build(
                portfolio,
                envelope,
                policy=policy,
            )
        )

        self.assertEqual(
            packet.evidence_ids,
            envelope.evidence_ids,
        )

    def test_factor_snapshot_matches_observation(
        self,
    ):
        portfolio, policy, envelope = (
            self.bundle()
        )

        packet = (
            GovernedRadarReviewPacket
            .build(
                portfolio,
                envelope,
                policy=policy,
            )
        )

        factors = (
            portfolio
            .ranked_observations[0]
            .factors
        )

        snapshot = (
            packet.entries[0].factors
        )

        self.assertEqual(
            snapshot.novelty,
            factors.novelty,
        )

        self.assertEqual(
            snapshot.source_quality,
            factors.source_quality,
        )

        self.assertEqual(
            snapshot.relevance_to_maestro,
            factors.relevance_to_maestro,
        )

        self.assertEqual(
            snapshot.expected_capability_gain,
            factors.expected_capability_gain,
        )

        self.assertEqual(
            snapshot.reproducibility,
            factors.reproducibility,
        )

        self.assertEqual(
            snapshot.integration_cost,
            factors.integration_cost,
        )

        self.assertEqual(
            snapshot.security_risk,
            factors.security_risk,
        )

    def test_source_ref_and_claim_preserved(
        self,
    ):
        portfolio, policy, envelope = (
            self.bundle()
        )

        packet = (
            GovernedRadarReviewPacket
            .build(
                portfolio,
                envelope,
                policy=policy,
            )
        )

        observation = (
            portfolio
            .ranked_observations[0]
        )

        entry = packet.entries[0]

        self.assertEqual(
            entry.source_ref,
            observation.source_ref,
        )

        self.assertEqual(
            entry.claim,
            observation.claim,
        )

    def test_review_rationale(
        self,
    ):
        policy = RadarDecisionPolicy(
            investigate_min_priority=0.0,
            review_min_priority=0.0,
        )

        portfolio, policy, envelope = (
            self.bundle(
                policy=policy
            )
        )

        packet = (
            GovernedRadarReviewPacket
            .build(
                portfolio,
                envelope,
                policy=policy,
            )
        )

        self.assertEqual(
            packet.entries[0].disposition,
            RadarDisposition.REVIEW,
        )

        self.assertIn(
            "review threshold",
            packet.entries[0].rationale,
        )

    def test_investigate_rationale(
        self,
    ):
        policy = RadarDecisionPolicy(
            investigate_min_priority=0.0,
            review_min_priority=1.0,
        )

        portfolio, policy, envelope = (
            self.bundle(
                policy=policy
            )
        )

        packet = (
            GovernedRadarReviewPacket
            .build(
                portfolio,
                envelope,
                policy=policy,
            )
        )

        self.assertEqual(
            packet.entries[0].disposition,
            RadarDisposition.INVESTIGATE,
        )

        self.assertIn(
            "investigate threshold",
            packet.entries[0].rationale,
        )

    def test_observe_rationale(
        self,
    ):
        policy = RadarDecisionPolicy(
            investigate_min_priority=1.0,
            review_min_priority=1.0,
        )

        portfolio, policy, envelope = (
            self.bundle(
                policy=policy
            )
        )

        packet = (
            GovernedRadarReviewPacket
            .build(
                portfolio,
                envelope,
                policy=policy,
            )
        )

        self.assertEqual(
            packet.entries[0].disposition,
            RadarDisposition.OBSERVE,
        )

        self.assertIn(
            "below investigate threshold",
            packet.entries[0].rationale,
        )

    def test_packet_is_deterministic(
        self,
    ):
        portfolio, policy, envelope = (
            self.bundle(
                count=2
            )
        )

        first = (
            GovernedRadarReviewPacket
            .build(
                portfolio,
                envelope,
                policy=policy,
            )
        )

        second = (
            GovernedRadarReviewPacket
            .build(
                portfolio,
                envelope,
                policy=policy,
            )
        )

        self.assertEqual(
            first,
            second,
        )

    def test_unverified_boundary_preserved(
        self,
    ):
        portfolio, policy, envelope = (
            self.bundle()
        )

        packet = (
            GovernedRadarReviewPacket
            .build(
                portfolio,
                envelope,
                policy=policy,
            )
        )

        self.assertEqual(
            packet.entries[0]
            .verification_status,
            "UNVERIFIED_EXTERNAL",
        )

        self.assertFalse(
            packet.entries[0]
            .system_truth_asserted
        )

    def test_wrong_portfolio_type_rejected(
        self,
    ):
        _, policy, envelope = (
            self.bundle()
        )

        with self.assertRaises(
            TypeError
        ):
            (
                GovernedRadarReviewPacket
                .build(
                    object(),
                    envelope,
                    policy=policy,
                )
            )

    def test_wrong_envelope_type_rejected(
        self,
    ):
        portfolio, policy, _ = (
            self.bundle()
        )

        with self.assertRaises(
            TypeError
        ):
            (
                GovernedRadarReviewPacket
                .build(
                    portfolio,
                    object(),
                    policy=policy,
                )
            )

    def test_wrong_policy_type_rejected(
        self,
    ):
        portfolio, _, envelope = (
            self.bundle()
        )

        with self.assertRaises(
            TypeError
        ):
            (
                GovernedRadarReviewPacket
                .build(
                    portfolio,
                    envelope,
                    policy=object(),
                )
            )

    def test_mismatched_envelope_ids_fail_closed(
        self,
    ):
        portfolio, policy, envelope = (
            self.bundle(
                count=2
            )
        )

        reversed_envelope = (
            RadarDecisionEnvelope(
                entries=tuple(
                    replace(
                        entry,
                        rank=index,
                    )
                    for index, entry
                    in enumerate(
                        reversed(
                            envelope.entries
                        ),
                        start=1,
                    )
                )
            )
        )

        with self.assertRaises(
            RadarReviewPacketInvariantError
        ):
            (
                GovernedRadarReviewPacket
                .build(
                    portfolio,
                    reversed_envelope,
                    policy=policy,
                )
            )

    def test_mismatched_disposition_fails_closed(
        self,
    ):
        portfolio, policy, envelope = (
            self.bundle()
        )

        original = envelope.entries[0]

        changed = (
            RadarDisposition.REVIEW
            if original.disposition
            is not RadarDisposition.REVIEW
            else RadarDisposition.OBSERVE
        )

        altered = RadarDecisionEnvelope(
            entries=(
                replace(
                    original,
                    disposition=changed,
                ),
            )
        )

        with self.assertRaises(
            RadarReviewPacketInvariantError
        ):
            (
                GovernedRadarReviewPacket
                .build(
                    portfolio,
                    altered,
                    policy=policy,
                )
            )

    def test_mismatched_priority_fails_closed(
        self,
    ):
        portfolio, policy, envelope = (
            self.bundle()
        )

        original = envelope.entries[0]

        changed_score = (
            0.0
            if original.priority_score
            != 0.0
            else 1.0
        )

        altered = RadarDecisionEnvelope(
            entries=(
                RadarDecisionEntry(
                    rank=original.rank,
                    evidence_id=(
                        original.evidence_id
                    ),
                    priority_score=(
                        changed_score
                    ),
                    disposition=(
                        original.disposition
                    ),
                ),
            )
        )

        with self.assertRaises(
            RadarReviewPacketInvariantError
        ):
            (
                GovernedRadarReviewPacket
                .build(
                    portfolio,
                    altered,
                    policy=policy,
                )
            )

    def test_inputs_are_not_mutated(
        self,
    ):
        portfolio, policy, envelope = (
            self.bundle()
        )

        portfolio_before = copy.deepcopy(
            portfolio
        )
        envelope_before = copy.deepcopy(
            envelope
        )
        policy_before = copy.deepcopy(
            policy
        )

        (
            GovernedRadarReviewPacket
            .build(
                portfolio,
                envelope,
                policy=policy,
            )
        )

        self.assertEqual(
            portfolio,
            portfolio_before,
        )

        self.assertEqual(
            envelope,
            envelope_before,
        )

        self.assertEqual(
            policy,
            policy_before,
        )

    def test_module_has_no_network_learning_activation_or_authority_imports(
        self,
    ):
        path = Path(
            "src/maestro/research/"
            "radar_review_packet.py"
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
