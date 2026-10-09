from __future__ import annotations

import ast
import unittest

from pathlib import Path
from unittest.mock import patch

from maestro.enums import (
    CouncilId,
    SideEffectLevel,
)

from maestro.research import (
    ContentDigest,
    ExternalArtifact,
    GovernedRadarDecisionEnvelope,
    GovernedRadarEvidenceFollowUp,
    GovernedRadarEvaluationPipeline,
    GovernedRadarFollowUpCandidateBuilder,
    GovernedRadarFollowUpCycleGate,
    GovernedRadarFollowUpCycleGovernor,
    GovernedRadarPortfolio,
    GovernedRadarReevaluationDecisionMaker,
    GovernedRadarReevaluationPortfolioReintegrator,
    GovernedRadarReevaluationReviewPacketMaterializer,
    GovernedRadarReevaluationStarter,
    GovernedRadarResearchDraftAdmissionGate,
    GovernedRadarResearchEvidenceReintegrator,
    GovernedRadarResearchExactExecutor,
    GovernedRadarResearchProviderReturnAdmission,
    GovernedRadarResearchRequestDraftBuilder,
    GovernedRadarResearchRequestMaterializer,
    GovernedRadarResearchRouter,
    GovernedRadarResearchTaskBinder,
    GovernedRadarResearchToolValidator,
    GovernedRadarReviewHandoff,
    GovernedRadarReviewPacket,
    GovernedRadarReviewResponse,
    GovernedResearchRuntime,
    RadarDecisionPolicy,
    RadarDisposition,
    RadarFollowUpCycleContext,
    RadarFollowUpCycleDisposition,
    RadarFollowUpCyclePolicy,
    RadarPortfolioEntry,
    RadarResearchDraftAdmissionStatus,
    RadarResearchProviderReturnPacket,
    RadarReviewResponseValue,
    RadarReviewTarget,
    ResearchCapability,
    ResearchClaim,
    ResearchEvidenceBridge,
    ResearchProviderDescriptor,
    ResearchProviderRegistry,
    ResearchSource,
    SourceProvenance,
    TechnologyRadar,
)

from maestro.tools.registry import (
    ToolRegistry,
    ToolSpec,
)


class RadarReevaluationReviewPacketTests(
    unittest.TestCase
):
    NOW = "2026-10-09T06:00:00+00:00"

    TASK_A = "TASK-A1B2C3D4E5F6"
    TASK_B = "TASK-B1C2D3E4F5A6"
    TASK_C = "TASK-C1D2E3F4A5B6"

    def provider(
        self,
    ):
        return ResearchProviderDescriptor(
            provider_id="alpha",
            capabilities=frozenset(
                {
                    ResearchCapability.SEARCH,
                }
            ),
            tool_names={
                ResearchCapability.SEARCH: (
                    "alpha.search"
                ),
            },
            local=True,
            quality_score=0.9,
            cost_score=0.1,
            latency_score=0.1,
        )

    def runtime(
        self,
    ):
        providers = ResearchProviderRegistry()

        providers.register(
            self.provider()
        )

        counter = {
            "value": 0,
        }

        def handler(
            **kwargs,
        ):
            counter["value"] += 1

            statement = (
                "External source reports "
                "new MAESTRO research "
                f"observation {counter['value']}."
            )

            source = ResearchSource(
                (
                    "https://example.com/"
                    f"adel028-{counter['value']}"
                ),
                label="ADEL0.28 source",
            )

            provenance = SourceProvenance(
                source_id=source.source_id,
                retrieved_at=self.NOW,
                digest=ContentDigest.from_bytes(
                    statement.encode(
                        "utf-8"
                    )
                ),
                author="External Provider",
                version="1",
            )

            return (
                RadarResearchProviderReturnPacket(
                    provider_id="alpha",
                    tool_name="alpha.search",
                    source=source,
                    provenance=provenance,
                    claim_statement=statement,
                    artifact_kind="DOCUMENT",
                    media_type="text/plain",
                )
            )

        tools = ToolRegistry()

        tools.register(
            ToolSpec(
                name="alpha.search",
                description="ADEL0.28 search",
                capabilities=(
                    "research.search",
                    "research.provider:alpha",
                ),
                allowed_councils=frozenset(
                    {CouncilId.RX}
                ),
                side_effect_level=(
                    SideEffectLevel.A0_READ_ONLY
                ),
                requires_policy_approval=False,
                requires_human_approval=False,
            ),
            handler,
        )

        return GovernedResearchRuntime(
            providers,
            tools,
        )

    def original_evidence(
        self,
        suffix,
    ):
        statement = (
            "GPU reasoning improves "
            f"MAESTRO research {suffix}"
        )

        source = ResearchSource(
            (
                "https://example.com/"
                f"adel028-origin-{suffix}"
            ),
            label=f"ADEL0.28 {suffix}",
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
            ResearchEvidenceBridge.to_evidence(
                task_id=self.TASK_A,
                claim=claim,
                artifacts=[artifact],
            )
        )

    def initial_context(
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
                    "network",
                    "execution",
                ],
                mitigations=[
                    "network"
                ],
            )
        )

    def materialization(
        self,
        count=1,
    ):
        portfolio = (
            GovernedRadarPortfolio()
            .evaluate(
                tuple(
                    RadarPortfolioEntry(
                        evidence=(
                            self.original_evidence(
                                str(index)
                            )
                        ),
                        context=(
                            self.initial_context()
                        ),
                    )
                    for index in range(count)
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
                    entry.evidence_id: (
                        RadarReviewTarget
                        .HUMAN_REVIEW
                    )
                    for entry
                    in packet.entries
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

        candidates = (
            GovernedRadarFollowUpCandidateBuilder
            .build(
                followup
            )
        )

        drafts = (
            GovernedRadarResearchRequestDraftBuilder
            .build(
                candidates
            )
        )

        admission = (
            GovernedRadarResearchDraftAdmissionGate
            .evaluate(
                drafts
            )
        )

        task_values = (
            self.TASK_A,
            self.TASK_B,
            self.TASK_C,
        )

        task_ids = {
            entry.evidence_id: (
                task_values[index]
            )
            for index, entry
            in enumerate(
                admission.entries
            )
            if (
                entry.status
                is RadarResearchDraftAdmissionStatus
                .ADMISSIBLE
            )
        }

        binding = (
            GovernedRadarResearchTaskBinder
            .bind(
                admission,
                task_ids=task_ids,
            )
        )

        return (
            GovernedRadarResearchRequestMaterializer
            .materialize(
                binding
            )
        )

    def portfolio_reintegration(
        self,
        count=1,
        *,
        completed_cycles=0,
    ):
        runtime = self.runtime()

        routing = (
            GovernedRadarResearchRouter
            .route(
                self.materialization(
                    count
                ),
                runtime=runtime,
            )
        )

        handoff = (
            GovernedRadarResearchToolValidator
            .validate(
                routing,
                runtime=runtime,
            )
        )

        execution = (
            GovernedRadarResearchExactExecutor
            .execute(
                handoff,
                runtime=runtime,
            )
        )

        admission = (
            GovernedRadarResearchProviderReturnAdmission
            .admit(
                execution
            )
        )

        reintegration = (
            GovernedRadarResearchEvidenceReintegrator
            .reintegrate(
                admission
            )
        )

        gate = (
            GovernedRadarFollowUpCycleGate
            .decide(
                reintegration,
                decisions={
                    evidence_id: (
                        RadarFollowUpCycleDisposition
                        .ELIGIBLE_FOR_REEVALUATION
                    )
                    for evidence_id
                    in reintegration.evidence_ids
                },
            )
        )

        cycle_governance = (
            GovernedRadarFollowUpCycleGovernor
            .govern(
                gate,
                contexts={
                    evidence_id: (
                        RadarFollowUpCycleContext(
                            completed_cycles=(
                                completed_cycles
                            ),
                            known_claims=(
                                "unrelated legacy",
                            ),
                        )
                    )
                    for evidence_id
                    in gate.eligible_evidence_ids
                },
                policy=(
                    RadarFollowUpCyclePolicy(
                        max_cycles=3,
                        minimum_novelty=0.05,
                    )
                ),
            )
        )

        contexts = {
            evidence_id: (
                GovernedRadarEvaluationPipeline
                .context(
                    known_claims=(
                        "unrelated legacy",
                    ),
                    relevance_terms=[
                        "MAESTRO",
                        "research",
                    ],
                    capability_terms=[
                        "External",
                        "research",
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
                        "network",
                        "execution",
                    ],
                    mitigations=[
                        "network"
                    ],
                )
            )
            for evidence_id
            in cycle_governance.admitted_evidence_ids
        }

        start = (
            GovernedRadarReevaluationStarter
            .start(
                cycle_governance,
                contexts=contexts,
            )
        )

        return (
            GovernedRadarReevaluationPortfolioReintegrator
            .reintegrate(
                start
            )
        )

    def decision(
        self,
        count=1,
        *,
        policy,
        completed_cycles=0,
    ):
        source = self.portfolio_reintegration(
            count,
            completed_cycles=completed_cycles,
        )

        return (
            GovernedRadarReevaluationDecisionMaker
            .decide(
                source,
                policy=policy,
            )
        )

    def review_policy(
        self,
    ):
        return RadarDecisionPolicy(
            investigate_min_priority=0.0,
            review_min_priority=0.0,
        )

    def observe_policy(
        self,
    ):
        return RadarDecisionPolicy(
            investigate_min_priority=1.0,
            review_min_priority=1.0,
        )

    def investigate_policy(
        self,
    ):
        source = self.portfolio_reintegration()

        score = (
            source.entries[0]
            .priority_score
        )

        self.assertLess(
            score,
            1.0,
        )

        return RadarDecisionPolicy(
            investigate_min_priority=score,
            review_min_priority=(
                score
                + ((1.0 - score) / 2.0)
            ),
        )

    def test_empty_source_creates_no_packet(
        self,
    ):
        source = self.decision(
            0,
            policy=self.review_policy(),
        )

        result = (
            GovernedRadarReevaluationReviewPacketMaterializer
            .materialize(
                source
            )
        )

        self.assertIsNone(
            result.packet
        )

        self.assertFalse(
            result.review_packet_created
        )

        self.assertEqual(
            result.size,
            0,
        )

    def test_observe_is_excluded(
        self,
    ):
        source = self.decision(
            policy=self.observe_policy(),
        )

        self.assertIs(
            source.entries[0].disposition,
            RadarDisposition.OBSERVE,
        )

        result = (
            GovernedRadarReevaluationReviewPacketMaterializer
            .materialize(
                source
            )
        )

        self.assertIsNone(
            result.packet
        )

        self.assertEqual(
            result.size,
            0,
        )

    def test_investigate_is_excluded(
        self,
    ):
        policy = self.investigate_policy()

        source = self.decision(
            policy=policy,
        )

        self.assertIs(
            source.entries[0].disposition,
            RadarDisposition.INVESTIGATE,
        )

        result = (
            GovernedRadarReevaluationReviewPacketMaterializer
            .materialize(
                source
            )
        )

        self.assertIsNone(
            result.packet
        )

        self.assertEqual(
            result.size,
            0,
        )

    def test_review_creates_packet(
        self,
    ):
        source = self.decision(
            policy=self.review_policy(),
        )

        result = (
            GovernedRadarReevaluationReviewPacketMaterializer
            .materialize(
                source
            )
        )

        self.assertTrue(
            result.review_packet_created
        )

        self.assertIsNotNone(
            result.packet
        )

        self.assertEqual(
            result.size,
            1,
        )

    def test_packet_contains_exact_review_ids(
        self,
    ):
        source = self.decision(
            3,
            policy=self.review_policy(),
        )

        result = (
            GovernedRadarReevaluationReviewPacketMaterializer
            .materialize(
                source
            )
        )

        self.assertEqual(
            result.evidence_ids,
            source.review_recommended_evidence_ids,
        )

        self.assertEqual(
            result.packet.evidence_ids,
            source.review_recommended_evidence_ids,
        )

    def test_packet_local_ranks_are_contiguous(
        self,
    ):
        result = (
            GovernedRadarReevaluationReviewPacketMaterializer
            .materialize(
                self.decision(
                    3,
                    policy=self.review_policy(),
                )
            )
        )

        self.assertEqual(
            result.packet_ranks,
            (
                1,
                2,
                3,
            ),
        )

    def test_source_ranks_are_preserved(
        self,
    ):
        source = self.decision(
            3,
            policy=self.review_policy(),
        )

        result = (
            GovernedRadarReevaluationReviewPacketMaterializer
            .materialize(
                source
            )
        )

        self.assertEqual(
            result.source_ranks,
            tuple(
                entry.rank
                for entry in source.entries
                if entry.review_recommended
            ),
        )

    def test_source_ref_and_claim_are_preserved(
        self,
    ):
        source = self.decision(
            policy=self.review_policy(),
        )

        result = (
            GovernedRadarReevaluationReviewPacketMaterializer
            .materialize(
                source
            )
        )

        before = (
            source.entries[0]
            .source_entry
            .ranked_observation
        )

        after = result.packet.entries[0]

        self.assertEqual(
            after.source_ref,
            before.source_ref,
        )

        self.assertEqual(
            after.claim,
            before.claim,
        )

    def test_factor_snapshot_is_preserved(
        self,
    ):
        source = self.decision(
            policy=self.review_policy(),
        )

        result = (
            GovernedRadarReevaluationReviewPacketMaterializer
            .materialize(
                source
            )
        )

        before = (
            source.entries[0]
            .source_entry
            .ranked_observation
            .factors
        )

        after = (
            result.packet.entries[0]
            .factors
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

        self.assertEqual(
            after.security_risk,
            before.security_risk,
        )

    def test_policy_identity_is_preserved(
        self,
    ):
        policy = self.review_policy()

        source = self.decision(
            2,
            policy=policy,
        )

        result = (
            GovernedRadarReevaluationReviewPacketMaterializer
            .materialize(
                source
            )
        )

        self.assertIs(
            source.policy,
            policy,
        )

        self.assertIs(
            result.packet.policy,
            policy,
        )

        for row in result.entries:
            self.assertIs(
                row.policy,
                policy,
            )

    def test_generic_adel011_builder_is_not_called(
        self,
    ):
        source = self.decision(
            2,
            policy=self.review_policy(),
        )

        with patch.object(
            GovernedRadarReviewPacket,
            "build",
            side_effect=AssertionError(
                "GENERIC ADEL0.11 BUILDER CALLED"
            ),
        ):
            result = (
                GovernedRadarReevaluationReviewPacketMaterializer
                .materialize(
                    source
                )
            )

        self.assertEqual(
            result.size,
            2,
        )

    def test_no_second_evaluation_ranking_or_decision(
        self,
    ):
        source = self.decision(
            2,
            policy=self.review_policy(),
        )

        with (
            patch.object(
                GovernedRadarEvaluationPipeline,
                "evaluate",
                side_effect=AssertionError(
                    "SECOND EVALUATION"
                ),
            ),
            patch.object(
                TechnologyRadar,
                "rank",
                side_effect=AssertionError(
                    "SECOND RANKING"
                ),
            ),
            patch.object(
                GovernedRadarDecisionEnvelope,
                "evaluate",
                side_effect=AssertionError(
                    "SECOND DECISION"
                ),
            ),
        ):
            result = (
                GovernedRadarReevaluationReviewPacketMaterializer
                .materialize(
                    source
                )
            )

        self.assertEqual(
            result.size,
            2,
        )

        self.assertFalse(
            result.second_radar_evaluation
        )

        self.assertFalse(
            result.second_ranking_created
        )

        self.assertFalse(
            result.second_decision_created
        )

    def test_no_handoff_response_or_human_approval(
        self,
    ):
        result = (
            GovernedRadarReevaluationReviewPacketMaterializer
            .materialize(
                self.decision(
                    policy=self.review_policy(),
                )
            )
        )

        self.assertFalse(
            result.review_handoff_created
        )

        self.assertFalse(
            result.review_response_created
        )

        self.assertFalse(
            result.human_approval_asserted
        )

        for row in result.entries:
            self.assertFalse(
                row.review_handoff_created
            )

            self.assertFalse(
                row.review_response_created
            )

            self.assertFalse(
                row.human_approval_asserted
            )

    def test_no_followup_research_network_or_persistence(
        self,
    ):
        result = (
            GovernedRadarReevaluationReviewPacketMaterializer
            .materialize(
                self.decision(
                    policy=self.review_policy(),
                )
            )
        )

        self.assertFalse(
            result.followup_created
        )

        self.assertFalse(
            result.new_research_request_created
        )

        self.assertFalse(
            result.network_requested
        )

        self.assertFalse(
            result.tool_execution_requested
        )

        self.assertFalse(
            result.persistence_requested
        )

        self.assertFalse(
            result.mission_transition_requested
        )

    def test_unverified_truth_and_authority_boundaries(
        self,
    ):
        result = (
            GovernedRadarReevaluationReviewPacketMaterializer
            .materialize(
                self.decision(
                    policy=self.review_policy(),
                )
            )
        )

        for row in result.entries:
            self.assertEqual(
                row.verification_status,
                "UNVERIFIED_EXTERNAL",
            )

            self.assertEqual(
                row.packet_entry
                .verification_status,
                "UNVERIFIED_EXTERNAL",
            )

            self.assertFalse(
                row.system_truth_asserted
            )

        self.assertFalse(
            result.system_truth_asserted
        )

        self.assertFalse(
            result.ay_validation_asserted
        )

        self.assertFalse(
            result.ex_authorization_asserted
        )

        self.assertFalse(
            result.learning_asserted
        )

        self.assertFalse(
            result.promotion_asserted
        )

        self.assertFalse(
            result.activation_asserted
        )

        self.assertFalse(
            result.execution_asserted
        )

    def test_wrong_source_fails_closed(
        self,
    ):
        with self.assertRaises(
            TypeError
        ):
            (
                GovernedRadarReevaluationReviewPacketMaterializer
                .materialize(
                    object()
                )
            )

    def test_deterministic_and_source_unchanged(
        self,
    ):
        source = self.decision(
            3,
            policy=self.review_policy(),
        )

        original_entries = source.entries
        original_envelope = source.envelope
        original_ids = source.evidence_ids
        original_dispositions = (
            source.dispositions
        )

        first = (
            GovernedRadarReevaluationReviewPacketMaterializer
            .materialize(
                source
            )
        )

        second = (
            GovernedRadarReevaluationReviewPacketMaterializer
            .materialize(
                source
            )
        )

        self.assertEqual(
            first,
            second,
        )

        self.assertIs(
            source.entries,
            original_entries,
        )

        self.assertIs(
            source.envelope,
            original_envelope,
        )

        self.assertEqual(
            source.evidence_ids,
            original_ids,
        )

        self.assertEqual(
            source.dispositions,
            original_dispositions,
        )

    def test_static_boundary_is_exact(
        self,
    ):
        path = Path(
            "src/maestro/research/"
            "radar_research_reevaluation_review_packet.py"
        )

        tree = ast.parse(
            path.read_text(
                encoding="utf-8"
            )
        )

        calls = set()
        imported_names = set()
        imported_modules = set()

        for node in ast.walk(tree):
            if isinstance(
                node,
                ast.Call,
            ):
                try:
                    calls.add(
                        ast.unparse(
                            node.func
                        )
                    )
                except Exception:
                    pass

            if isinstance(
                node,
                ast.ImportFrom,
            ):
                imported_modules.add(
                    node.module or ""
                )

                for alias in node.names:
                    imported_names.add(
                        alias.name
                    )

        self.assertIn(
            "RadarFactorSnapshot.from_factors",
            calls,
        )

        self.assertIn(
            "RadarReviewEntry",
            calls,
        )

        self.assertIn(
            "RadarReviewPacket",
            calls,
        )

        self.assertNotIn(
            "GovernedRadarReviewPacket",
            imported_names,
        )

        forbidden_calls = {
            "GovernedRadarReviewPacket.build",
            "GovernedRadarEvaluationPipeline.evaluate",
            "GovernedRadarPortfolio.evaluate",
            "TechnologyRadar.rank",
            "GovernedRadarDecisionEnvelope.evaluate",
            "GovernedRadarReviewHandoff.build",
            "GovernedRadarReviewResponse.build",
            "GovernedRadarEvidenceFollowUp.build",
            "GovernedRadarResearchRequestDraftBuilder.build",
            "ResearchEvidenceStore.record",
            "runtime.route",
            "runtime.execute",
            "runtime.execute_exact",
            "runtime.tools.invoke",
        }

        self.assertTrue(
            calls.isdisjoint(
                forbidden_calls
            )
        )

        forbidden_modules = (
            "radar_review_handoff",
            "radar_review_response",
            "radar_evidence_followup",
            "radar_research_request_draft",
            "durable_store",
            "runtime",
        )

        for imported in imported_modules:
            for fragment in forbidden_modules:
                self.assertNotIn(
                    fragment,
                    imported,
                )


if __name__ == "__main__":
    unittest.main()
