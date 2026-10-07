from __future__ import annotations

import ast
import copy
import unittest

from pathlib import Path

from maestro.research import (
    ContentDigest,
    ExternalArtifact,
    GovernedRadarDecisionEnvelope,
    GovernedRadarEvidenceFollowUp,
    GovernedRadarEvaluationPipeline,
    GovernedRadarFollowUpCandidateBuilder,
    GovernedRadarPortfolio,
    GovernedRadarReviewHandoff,
    GovernedRadarReviewPacket,
    GovernedRadarReviewResponse,
    RadarDecisionPolicy,
    RadarPortfolioEntry,
    RadarReviewResponseValue,
    RadarReviewTarget,
    ResearchCapability,
    ResearchClaim,
    ResearchEvidenceBridge,
    ResearchSource,
    SourceProvenance,
)


class RadarFollowUpCandidateTests(
    unittest.TestCase
):
    NOW = "2026-01-01T00:00:00+00:00"

    def evidence(
        self,
        *,
        suffix: str,
    ):
        statement = (
            "GPU reasoning improves "
            "MAESTRO research"
        )

        source = ResearchSource(
            (
                "https://example.com/"
                f"adel015-{suffix}"
            ),
            label=(
                f"ADEL0.15 {suffix}"
            ),
        )

        provenance = SourceProvenance(
            source_id=source.source_id,
            retrieved_at=self.NOW,
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
            created_at=self.NOW,
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
                risk_signals=[
                    "network"
                ],
                mitigations=[
                    "network"
                ],
            )
        )

    def followup(
        self,
        *,
        count=1,
        target=(
            RadarReviewTarget
            .HUMAN_REVIEW
        ),
    ):
        portfolio = (
            GovernedRadarPortfolio()
            .evaluate(
                tuple(
                    RadarPortfolioEntry(
                        evidence=(
                            self.evidence(
                                suffix=str(index)
                            )
                        ),
                        context=self.context(),
                    )
                    for index
                    in range(count)
                )
            )
        )

        policy = RadarDecisionPolicy(
            investigate_min_priority=0.0,
            review_min_priority=0.0,
        )

        envelope = (
            GovernedRadarDecisionEnvelope
            .evaluate(
                portfolio,
                policy=policy,
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

        handoff = (
            GovernedRadarReviewHandoff
            .build(
                packet,
                assignments={
                    entry.evidence_id: target
                    for entry in packet.entries
                },
            )
        )

        response = (
            GovernedRadarReviewResponse
            .build(
                handoff,
                responses={
                    entry.evidence_id: (
                        RadarReviewResponseValue
                        .REQUEST_MORE_EVIDENCE
                    )
                    for entry
                    in handoff.entries
                },
            )
        )

        return (
            GovernedRadarEvidenceFollowUp
            .build(
                response
            )
        )

    def test_empty_followup_produces_empty_candidates(
        self,
    ):
        result = (
            GovernedRadarFollowUpCandidateBuilder
            .build(
                self.followup(
                    count=0
                )
            )
        )

        self.assertEqual(
            result.size,
            0,
        )

    def test_followup_produces_candidate(
        self,
    ):
        result = (
            GovernedRadarFollowUpCandidateBuilder
            .build(
                self.followup()
            )
        )

        self.assertEqual(
            result.size,
            1,
        )

    def test_capability_is_search(
        self,
    ):
        result = (
            GovernedRadarFollowUpCandidateBuilder
            .build(
                self.followup()
            )
        )

        self.assertEqual(
            result.entries[0].capability,
            ResearchCapability.SEARCH,
        )

    def test_query_contains_claim(
        self,
    ):
        followup = self.followup()

        result = (
            GovernedRadarFollowUpCandidateBuilder
            .build(
                followup
            )
        )

        self.assertIn(
            followup.needs[0].claim,
            result.entries[0].query,
        )

    def test_preferred_local_is_true(
        self,
    ):
        result = (
            GovernedRadarFollowUpCandidateBuilder
            .build(
                self.followup()
            )
        )

        self.assertTrue(
            result.entries[0]
            .preferred_local
        )

    def test_target_is_preserved(
        self,
    ):
        result = (
            GovernedRadarFollowUpCandidateBuilder
            .build(
                self.followup(
                    target=(
                        RadarReviewTarget
                        .AY_REVIEW
                    )
                )
            )
        )

        self.assertEqual(
            result.entries[0].target,
            RadarReviewTarget.AY_REVIEW,
        )

    def test_order_is_preserved(
        self,
    ):
        followup = self.followup(
            count=3
        )

        result = (
            GovernedRadarFollowUpCandidateBuilder
            .build(
                followup
            )
        )

        self.assertEqual(
            result.evidence_ids,
            followup.evidence_ids,
        )

    def test_payload_is_preserved(
        self,
    ):
        followup = self.followup()

        result = (
            GovernedRadarFollowUpCandidateBuilder
            .build(
                followup
            )
        )

        before = followup.needs[0]
        after = result.entries[0]

        self.assertEqual(
            after.rank,
            before.rank,
        )
        self.assertEqual(
            after.evidence_id,
            before.evidence_id,
        )
        self.assertEqual(
            after.source_ref,
            before.source_ref,
        )
        self.assertEqual(
            after.claim,
            before.claim,
        )
        self.assertEqual(
            after.priority_score,
            before.priority_score,
        )
        self.assertEqual(
            after.factors,
            before.factors,
        )
        self.assertEqual(
            after.rationale,
            before.rationale,
        )

    def test_unverified_boundary_preserved(
        self,
    ):
        result = (
            GovernedRadarFollowUpCandidateBuilder
            .build(
                self.followup()
            )
        )

        row = result.entries[0]

        self.assertEqual(
            row.verification_status,
            "UNVERIFIED_EXTERNAL",
        )
        self.assertFalse(
            row.system_truth_asserted
        )

    def test_no_research_request_created(
        self,
    ):
        result = (
            GovernedRadarFollowUpCandidateBuilder
            .build(
                self.followup()
            )
        )

        self.assertFalse(
            result.entries[0]
            .research_request_created
        )

    def test_no_provider_or_routing_selected(
        self,
    ):
        result = (
            GovernedRadarFollowUpCandidateBuilder
            .build(
                self.followup()
            )
        )

        row = result.entries[0]

        self.assertFalse(
            row.provider_selected
        )
        self.assertFalse(
            row.routing_decision_created
        )

    def test_no_runtime_side_effects_requested(
        self,
    ):
        result = (
            GovernedRadarFollowUpCandidateBuilder
            .build(
                self.followup()
            )
        )

        row = result.entries[0]

        self.assertFalse(
            row.network_requested
        )
        self.assertFalse(
            row.tool_execution_requested
        )
        self.assertFalse(
            row.mission_transition_requested
        )
        self.assertFalse(
            row.persistence_requested
        )

    def test_no_authority_is_asserted(
        self,
    ):
        result = (
            GovernedRadarFollowUpCandidateBuilder
            .build(
                self.followup()
            )
        )

        row = result.entries[0]

        self.assertFalse(
            row.authorization_asserted
        )
        self.assertFalse(
            row.promotion_asserted
        )
        self.assertFalse(
            row.activation_asserted
        )
        self.assertFalse(
            row.execution_asserted
        )

    def test_builder_is_deterministic(
        self,
    ):
        followup = self.followup(
            count=2
        )

        first = (
            GovernedRadarFollowUpCandidateBuilder
            .build(
                followup
            )
        )

        second = (
            GovernedRadarFollowUpCandidateBuilder
            .build(
                followup
            )
        )

        self.assertEqual(
            first,
            second,
        )

    def test_wrong_followup_type_rejected(
        self,
    ):
        with self.assertRaises(
            TypeError
        ):
            (
                GovernedRadarFollowUpCandidateBuilder
                .build(
                    object()
                )
            )

    def test_input_not_mutated(
        self,
    ):
        followup = self.followup()

        before = copy.deepcopy(
            followup
        )

        (
            GovernedRadarFollowUpCandidateBuilder
            .build(
                followup
            )
        )

        self.assertEqual(
            followup,
            before,
        )

    def test_query_is_deterministic(
        self,
    ):
        followup = self.followup()

        first = (
            GovernedRadarFollowUpCandidateBuilder
            .build(
                followup
            )
            .entries[0]
            .query
        )

        second = (
            GovernedRadarFollowUpCandidateBuilder
            .build(
                followup
            )
            .entries[0]
            .query
        )

        self.assertEqual(
            first,
            second,
        )

    def test_module_has_no_runtime_tool_network_or_governance_imports(
        self,
    ):
        path = Path(
            "src/maestro/research/"
            "radar_followup_candidate.py"
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
            "maestro.meta_cognition",
            "maestro.fabric",
            "maestro.tools",
            "maestro.autonomous",
            "maestro.sovereign",
            "maestro.state_machine",
            "maestro.runtime",
            "maestro.research.runtime",
            "maestro.research.runtime_contracts",
            "maestro.research.transport",
            "maestro.research.web_fetch",
            "maestro.research.composition",
            "maestro.research.provider_registry",
            "maestro.research.durable_store",
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
