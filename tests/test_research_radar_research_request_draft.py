from __future__ import annotations

import ast
import copy
import unittest

from pathlib import Path
from types import MappingProxyType

from maestro.research import (
    ContentDigest,
    ExternalArtifact,
    GovernedRadarDecisionEnvelope,
    GovernedRadarEvidenceFollowUp,
    GovernedRadarEvaluationPipeline,
    GovernedRadarFollowUpCandidateBuilder,
    GovernedRadarPortfolio,
    GovernedRadarResearchRequestDraftBuilder,
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


class RadarResearchRequestDraftTests(
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
                f"adel016-{suffix}"
            ),
            label=(
                f"ADEL0.16 {suffix}"
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

    def candidates(
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

        followup = (
            GovernedRadarEvidenceFollowUp
            .build(
                response
            )
        )

        return (
            GovernedRadarFollowUpCandidateBuilder
            .build(
                followup
            )
        )

    def test_empty_candidates_produce_empty_drafts(
        self,
    ):
        result = (
            GovernedRadarResearchRequestDraftBuilder
            .build(
                self.candidates(
                    count=0
                )
            )
        )

        self.assertEqual(
            result.size,
            0,
        )

    def test_candidate_produces_draft(
        self,
    ):
        result = (
            GovernedRadarResearchRequestDraftBuilder
            .build(
                self.candidates()
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
            GovernedRadarResearchRequestDraftBuilder
            .build(
                self.candidates()
            )
        )

        self.assertEqual(
            result.entries[0].capability,
            ResearchCapability.SEARCH,
        )

    def test_arguments_contain_query_only(
        self,
    ):
        candidates = self.candidates()

        result = (
            GovernedRadarResearchRequestDraftBuilder
            .build(
                candidates
            )
        )

        row = result.entries[0]

        self.assertEqual(
            set(row.arguments),
            {"query"},
        )
        self.assertEqual(
            row.arguments["query"],
            candidates.entries[0].query,
        )

    def test_arguments_are_immutable(
        self,
    ):
        result = (
            GovernedRadarResearchRequestDraftBuilder
            .build(
                self.candidates()
            )
        )

        self.assertIsInstance(
            result.entries[0].arguments,
            MappingProxyType,
        )

        with self.assertRaises(
            TypeError
        ):
            result.entries[0].arguments[
                "query"
            ] = "mutated"

    def test_preferred_local_preserved(
        self,
    ):
        candidates = self.candidates()

        result = (
            GovernedRadarResearchRequestDraftBuilder
            .build(
                candidates
            )
        )

        self.assertEqual(
            result.entries[0].preferred_local,
            candidates.entries[0]
            .preferred_local,
        )

    def test_no_forbidden_provider_selected(
        self,
    ):
        result = (
            GovernedRadarResearchRequestDraftBuilder
            .build(
                self.candidates()
            )
        )

        self.assertEqual(
            result.entries[0]
            .forbidden_provider_ids,
            (),
        )

    def test_target_preserved(
        self,
    ):
        result = (
            GovernedRadarResearchRequestDraftBuilder
            .build(
                self.candidates(
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

    def test_order_preserved(
        self,
    ):
        candidates = self.candidates(
            count=3
        )

        result = (
            GovernedRadarResearchRequestDraftBuilder
            .build(
                candidates
            )
        )

        self.assertEqual(
            result.evidence_ids,
            candidates.evidence_ids,
        )

    def test_payload_preserved(
        self,
    ):
        candidates = self.candidates()

        result = (
            GovernedRadarResearchRequestDraftBuilder
            .build(
                candidates
            )
        )

        before = candidates.entries[0]
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
            GovernedRadarResearchRequestDraftBuilder
            .build(
                self.candidates()
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

    def test_no_task_identity_is_bound(
        self,
    ):
        result = (
            GovernedRadarResearchRequestDraftBuilder
            .build(
                self.candidates()
            )
        )

        self.assertFalse(
            result.entries[0]
            .task_id_bound
        )

    def test_no_research_request_created(
        self,
    ):
        result = (
            GovernedRadarResearchRequestDraftBuilder
            .build(
                self.candidates()
            )
        )

        self.assertFalse(
            result.entries[0]
            .research_request_created
        )

    def test_no_provider_or_routing_selected(
        self,
    ):
        row = (
            GovernedRadarResearchRequestDraftBuilder
            .build(
                self.candidates()
            )
            .entries[0]
        )

        self.assertFalse(
            row.provider_selected
        )
        self.assertFalse(
            row.routing_decision_created
        )

    def test_no_runtime_side_effects_requested(
        self,
    ):
        row = (
            GovernedRadarResearchRequestDraftBuilder
            .build(
                self.candidates()
            )
            .entries[0]
        )

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

    def test_no_authority_asserted(
        self,
    ):
        row = (
            GovernedRadarResearchRequestDraftBuilder
            .build(
                self.candidates()
            )
            .entries[0]
        )

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
        candidates = self.candidates(
            count=2
        )

        first = (
            GovernedRadarResearchRequestDraftBuilder
            .build(
                candidates
            )
        )

        second = (
            GovernedRadarResearchRequestDraftBuilder
            .build(
                candidates
            )
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
            "radar_research_request_draft.py"
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
