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


class RadarReevaluationDecisionTests(
    unittest.TestCase
):
    NOW = "2026-10-08T06:00:00+00:00"

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
                    f"adel027-{counter['value']}"
                ),
                label="ADEL0.27 source",
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
                description="ADEL0.27 search",
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
                f"adel027-origin-{suffix}"
            ),
            label=f"ADEL0.27 {suffix}",
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

    def policy_review(
        self,
    ):
        return RadarDecisionPolicy(
            investigate_min_priority=0.0,
            review_min_priority=0.0,
        )

    def policy_observe(
        self,
    ):
        return RadarDecisionPolicy(
            investigate_min_priority=1.0,
            review_min_priority=1.0,
        )

    def policy_investigate(
        self,
        source,
    ):
        score = (
            source.entries[0]
            .priority_score
        )

        self.assertLess(
            score,
            1.0,
        )

        review_threshold = (
            score
            + ((1.0 - score) / 2.0)
        )

        return RadarDecisionPolicy(
            investigate_min_priority=score,
            review_min_priority=(
                review_threshold
            ),
        )

    def test_empty_portfolio_produces_empty_decision(
        self,
    ):
        source = self.portfolio_reintegration(
            0
        )

        result = (
            GovernedRadarReevaluationDecisionMaker
            .decide(
                source,
                policy=self.policy_review(),
            )
        )

        self.assertEqual(
            result.size,
            0,
        )

        self.assertEqual(
            result.envelope.size,
            0,
        )

    def test_decision_reuses_exact_adel026_portfolio(
        self,
    ):
        source = self.portfolio_reintegration(
            2
        )

        result = (
            GovernedRadarReevaluationDecisionMaker
            .decide(
                source,
                policy=self.policy_review(),
            )
        )

        self.assertIs(
            result.source,
            source,
        )

        self.assertIs(
            result.source.portfolio,
            source.portfolio,
        )

    def test_observe_recommendation(
        self,
    ):
        source = self.portfolio_reintegration()

        result = (
            GovernedRadarReevaluationDecisionMaker
            .decide(
                source,
                policy=self.policy_observe(),
            )
        )

        self.assertIs(
            result.entries[0].disposition,
            RadarDisposition.OBSERVE,
        )

        self.assertTrue(
            result.entries[0]
            .observe_recommended
        )

    def test_investigate_recommendation(
        self,
    ):
        source = self.portfolio_reintegration()

        policy = self.policy_investigate(
            source
        )

        result = (
            GovernedRadarReevaluationDecisionMaker
            .decide(
                source,
                policy=policy,
            )
        )

        self.assertIs(
            result.entries[0].disposition,
            RadarDisposition.INVESTIGATE,
        )

        self.assertTrue(
            result.entries[0]
            .investigate_recommended
        )

    def test_review_is_recommendation_only(
        self,
    ):
        source = self.portfolio_reintegration()

        result = (
            GovernedRadarReevaluationDecisionMaker
            .decide(
                source,
                policy=self.policy_review(),
            )
        )

        row = result.entries[0]

        self.assertIs(
            row.disposition,
            RadarDisposition.REVIEW,
        )

        self.assertTrue(
            row.review_recommended
        )

        self.assertFalse(
            row.review_packet_created
        )

        self.assertFalse(
            row.review_handoff_created
        )

        self.assertFalse(
            row.review_response_created
        )

    def test_decision_covers_exact_ranked_ids_in_order(
        self,
    ):
        source = self.portfolio_reintegration(
            3
        )

        result = (
            GovernedRadarReevaluationDecisionMaker
            .decide(
                source,
                policy=self.policy_review(),
            )
        )

        self.assertEqual(
            result.evidence_ids,
            source.ranked_evidence_ids,
        )

        self.assertEqual(
            result.envelope.evidence_ids,
            source.ranked_evidence_ids,
        )

    def test_ranks_are_preserved(
        self,
    ):
        source = self.portfolio_reintegration(
            3
        )

        result = (
            GovernedRadarReevaluationDecisionMaker
            .decide(
                source,
                policy=self.policy_review(),
            )
        )

        self.assertEqual(
            tuple(
                row.rank
                for row in result.entries
            ),
            source.portfolio_ranks,
        )

    def test_priority_scores_are_preserved(
        self,
    ):
        source = self.portfolio_reintegration(
            3
        )

        result = (
            GovernedRadarReevaluationDecisionMaker
            .decide(
                source,
                policy=self.policy_review(),
            )
        )

        self.assertEqual(
            tuple(
                row.priority_score
                for row in result.entries
            ),
            tuple(
                row.priority_score
                for row in source.entries
            ),
        )

    def test_source_entry_and_policy_identity_preserved(
        self,
    ):
        source = self.portfolio_reintegration(
            2
        )

        policy = self.policy_review()

        result = (
            GovernedRadarReevaluationDecisionMaker
            .decide(
                source,
                policy=policy,
            )
        )

        self.assertIs(
            result.policy,
            policy,
        )

        for before, after in zip(
            source.entries,
            result.entries,
            strict=True,
        ):
            self.assertIs(
                after.source_entry,
                before,
            )

            self.assertIs(
                after.policy,
                policy,
            )

    def test_cycle_and_lineage_preserved(
        self,
    ):
        source = self.portfolio_reintegration(
            2,
            completed_cycles=1,
        )

        result = (
            GovernedRadarReevaluationDecisionMaker
            .decide(
                source,
                policy=self.policy_review(),
            )
        )

        for before, after in zip(
            source.entries,
            result.entries,
            strict=True,
        ):
            self.assertEqual(
                after.cycle_number,
                2,
            )

            self.assertEqual(
                after.origin_evidence_id,
                before.origin_evidence_id,
            )

            self.assertEqual(
                after.task_id,
                before.task_id,
            )

    def test_no_second_evaluation_or_second_ranking(
        self,
    ):
        source = self.portfolio_reintegration(
            2
        )

        with (
            patch.object(
                GovernedRadarEvaluationPipeline,
                "evaluate",
                side_effect=AssertionError(
                    "SECOND RADAR EVALUATION"
                ),
            ),
            patch.object(
                TechnologyRadar,
                "rank",
                side_effect=AssertionError(
                    "SECOND RANKING"
                ),
            ),
        ):
            result = (
                GovernedRadarReevaluationDecisionMaker
                .decide(
                    source,
                    policy=self.policy_review(),
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

    def test_no_review_followup_or_research_created(
        self,
    ):
        result = (
            GovernedRadarReevaluationDecisionMaker
            .decide(
                self.portfolio_reintegration(),
                policy=self.policy_review(),
            )
        )

        self.assertFalse(
            result.review_packet_created
        )

        self.assertFalse(
            result.review_handoff_created
        )

        self.assertFalse(
            result.review_response_created
        )

        self.assertFalse(
            result.followup_created
        )

        self.assertFalse(
            result.new_research_request_created
        )

    def test_no_network_execution_persistence_or_mission(
        self,
    ):
        result = (
            GovernedRadarReevaluationDecisionMaker
            .decide(
                self.portfolio_reintegration(),
                policy=self.policy_review(),
            )
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

        self.assertFalse(
            result.execution_asserted
        )

    def test_unverified_truth_and_authority_boundaries(
        self,
    ):
        result = (
            GovernedRadarReevaluationDecisionMaker
            .decide(
                self.portfolio_reintegration(),
                policy=self.policy_review(),
            )
        )

        for row in result.entries:
            self.assertEqual(
                row.verification_status,
                "UNVERIFIED_EXTERNAL",
            )

            self.assertEqual(
                row.decision_entry
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

    def test_wrong_source_fails_closed(
        self,
    ):
        with self.assertRaises(
            TypeError
        ):
            (
                GovernedRadarReevaluationDecisionMaker
                .decide(
                    object(),
                    policy=self.policy_review(),
                )
            )

    def test_wrong_policy_fails_closed(
        self,
    ):
        with self.assertRaises(
            TypeError
        ):
            (
                GovernedRadarReevaluationDecisionMaker
                .decide(
                    self.portfolio_reintegration(),
                    policy=object(),
                )
            )

    def test_deterministic_and_source_unchanged(
        self,
    ):
        source = self.portfolio_reintegration(
            3
        )

        policy = self.policy_review()

        original_entries = source.entries
        original_portfolio = source.portfolio
        original_ids = source.ranked_evidence_ids
        original_ranks = source.portfolio_ranks

        first = (
            GovernedRadarReevaluationDecisionMaker
            .decide(
                source,
                policy=policy,
            )
        )

        second = (
            GovernedRadarReevaluationDecisionMaker
            .decide(
                source,
                policy=policy,
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
            source.portfolio,
            original_portfolio,
        )

        self.assertEqual(
            source.ranked_evidence_ids,
            original_ids,
        )

        self.assertEqual(
            source.portfolio_ranks,
            original_ranks,
        )

    def test_static_boundary_is_exact(
        self,
    ):
        path = Path(
            "src/maestro/research/"
            "radar_research_reevaluation_decision.py"
        )

        tree = ast.parse(
            path.read_text(
                encoding="utf-8"
            )
        )

        calls = set()
        imports = set()

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
                imports.add(
                    node.module or ""
                )

        self.assertIn(
            "GovernedRadarDecisionEnvelope.evaluate",
            calls,
        )

        forbidden_calls = {
            "GovernedRadarEvaluationPipeline.evaluate",
            "GovernedRadarPortfolio.evaluate",
            "TechnologyRadar.rank",
            "GovernedRadarReviewPacket.build",
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

        forbidden_import_fragments = (
            "radar_evaluation_pipeline",
            "radar_portfolio",
            "technology_radar",
            "radar_review_packet",
            "radar_review_handoff",
            "radar_review_response",
            "radar_evidence_followup",
            "radar_research_request_draft",
            "durable_store",
            "runtime",
        )

        for imported in imports:
            for fragment in (
                forbidden_import_fragments
            ):
                self.assertNotIn(
                    fragment,
                    imported,
                )


if __name__ == "__main__":
    unittest.main()
