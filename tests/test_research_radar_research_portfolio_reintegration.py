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


class RadarReevaluationPortfolioReintegrationTests(
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
                    f"adel026-{counter['value']}"
                ),
                label="ADEL0.26 source",
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
                description="ADEL0.26 search",
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
                f"adel026-origin-{suffix}"
            ),
            label=f"ADEL0.26 {suffix}",
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
                    "network"
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

    def reintegration(
        self,
        count=1,
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

        return (
            GovernedRadarResearchEvidenceReintegrator
            .reintegrate(
                admission
            )
        )

    def reevaluation_start(
        self,
        count=1,
        *,
        completed_cycles=0,
    ):
        reintegration = self.reintegration(
            count
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

        governance = (
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
                        "network"
                    ],
                    mitigations=[
                        "network"
                    ],
                )
            )
            for evidence_id
            in governance.admitted_evidence_ids
        }

        return (
            GovernedRadarReevaluationStarter
            .start(
                governance,
                contexts=contexts,
            )
        )

    def test_empty_start_creates_empty_portfolio(
        self,
    ):
        start = self.reevaluation_start(
            0
        )

        result = (
            GovernedRadarReevaluationPortfolioReintegrator
            .reintegrate(
                start
            )
        )

        self.assertEqual(
            result.size,
            0,
        )

        self.assertEqual(
            result.portfolio.size,
            0,
        )

    def test_reuses_existing_evaluations_exactly(
        self,
    ):
        start = self.reevaluation_start(
            3
        )

        result = (
            GovernedRadarReevaluationPortfolioReintegrator
            .reintegrate(
                start
            )
        )

        self.assertEqual(
            len(
                result.portfolio.evaluations
            ),
            3,
        )

        for before, after in zip(
            start.evaluations,
            result.portfolio.evaluations,
            strict=True,
        ):
            self.assertIs(
                after,
                before,
            )

    def test_reuses_existing_observations_exactly(
        self,
    ):
        start = self.reevaluation_start(
            3
        )

        result = (
            GovernedRadarReevaluationPortfolioReintegrator
            .reintegrate(
                start
            )
        )

        source_observations = {
            entry.evidence_id:
            entry.evaluation.observation
            for entry in start.entries
        }

        for observation in (
            result.ranked_observations
        ):
            self.assertIs(
                observation,
                source_observations[
                    observation.evidence_id
                ],
            )

    def test_no_second_radar_evaluation(
        self,
    ):
        start = self.reevaluation_start(
            2
        )

        with patch.object(
            GovernedRadarEvaluationPipeline,
            "evaluate",
            side_effect=AssertionError(
                "SECOND RADAR EVALUATION"
            ),
        ):
            result = (
                GovernedRadarReevaluationPortfolioReintegrator
                .reintegrate(
                    start
                )
            )

        self.assertEqual(
            result.size,
            2,
        )

        self.assertFalse(
            result.second_radar_evaluation
        )

    def test_ranking_matches_technology_radar(
        self,
    ):
        start = self.reevaluation_start(
            3
        )

        expected = tuple(
            TechnologyRadar().rank(
                tuple(
                    entry.evaluation.observation
                    for entry in start.entries
                )
            )
        )

        result = (
            GovernedRadarReevaluationPortfolioReintegrator
            .reintegrate(
                start
            )
        )

        self.assertEqual(
            result.ranked_observations,
            expected,
        )

    def test_rank_numbers_are_one_based(
        self,
    ):
        result = (
            GovernedRadarReevaluationPortfolioReintegrator
            .reintegrate(
                self.reevaluation_start(
                    3
                )
            )
        )

        self.assertEqual(
            result.portfolio_ranks,
            (
                1,
                2,
                3,
            ),
        )

    def test_portfolio_ids_cover_exact_source_ids(
        self,
    ):
        start = self.reevaluation_start(
            3
        )

        result = (
            GovernedRadarReevaluationPortfolioReintegrator
            .reintegrate(
                start
            )
        )

        self.assertEqual(
            set(
                result.ranked_evidence_ids
            ),
            set(
                start.evidence_ids
            ),
        )

    def test_ranked_ids_are_unique(
        self,
    ):
        result = (
            GovernedRadarReevaluationPortfolioReintegrator
            .reintegrate(
                self.reevaluation_start(
                    3
                )
            )
        )

        self.assertEqual(
            len(
                result.ranked_evidence_ids
            ),
            len(
                set(
                    result.ranked_evidence_ids
                )
            ),
        )

    def test_lineage_preserved_per_ranked_entry(
        self,
    ):
        start = self.reevaluation_start(
            3
        )

        source = {
            entry.evidence_id: entry
            for entry in start.entries
        }

        result = (
            GovernedRadarReevaluationPortfolioReintegrator
            .reintegrate(
                start
            )
        )

        for row in result.entries:
            before = source[
                row.evidence_id
            ]

            self.assertIs(
                row.source_entry,
                before,
            )

            self.assertIs(
                row.evaluation,
                before.evaluation,
            )

            self.assertIs(
                row.ranked_observation,
                before.evaluation.observation,
            )

            self.assertEqual(
                row.task_id,
                before.task_id,
            )

            self.assertEqual(
                row.origin_evidence_id,
                before.origin_evidence_id,
            )

    def test_cycle_numbers_are_preserved(
        self,
    ):
        start = self.reevaluation_start(
            3,
            completed_cycles=1,
        )

        result = (
            GovernedRadarReevaluationPortfolioReintegrator
            .reintegrate(
                start
            )
        )

        source_cycles = {
            entry.evidence_id:
            entry.cycle_number
            for entry in start.entries
        }

        for row in result.entries:
            self.assertEqual(
                row.cycle_number,
                source_cycles[
                    row.evidence_id
                ],
            )

            self.assertEqual(
                row.cycle_number,
                2,
            )

    def test_unverified_boundary_preserved(
        self,
    ):
        result = (
            GovernedRadarReevaluationPortfolioReintegrator
            .reintegrate(
                self.reevaluation_start(
                    2
                )
            )
        )

        for row in result.entries:
            self.assertEqual(
                row.verification_status,
                "UNVERIFIED_EXTERNAL",
            )

            self.assertEqual(
                row.ranked_observation
                .verification_status,
                "UNVERIFIED_EXTERNAL",
            )

            self.assertFalse(
                row.system_truth_asserted
            )

            self.assertFalse(
                row.ranked_observation
                .system_truth_asserted
            )

    def test_no_decision_review_or_followup(
        self,
    ):
        result = (
            GovernedRadarReevaluationPortfolioReintegrator
            .reintegrate(
                self.reevaluation_start()
            )
        )

        self.assertFalse(
            result.decision_envelope_created
        )

        self.assertFalse(
            result.review_packet_created
        )

        self.assertFalse(
            result.followup_created
        )

        for row in result.entries:
            self.assertFalse(
                row.decision_envelope_created
            )

            self.assertFalse(
                row.review_packet_created
            )

            self.assertFalse(
                row.followup_created
            )

    def test_no_research_network_execution_or_persistence(
        self,
    ):
        result = (
            GovernedRadarReevaluationPortfolioReintegrator
            .reintegrate(
                self.reevaluation_start()
            )
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

        self.assertFalse(
            result.execution_asserted
        )

    def test_no_truth_authority_learning_promotion_activation(
        self,
    ):
        result = (
            GovernedRadarReevaluationPortfolioReintegrator
            .reintegrate(
                self.reevaluation_start()
            )
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

    def test_wrong_input_fails_closed(
        self,
    ):
        with self.assertRaises(
            TypeError
        ):
            (
                GovernedRadarReevaluationPortfolioReintegrator
                .reintegrate(
                    object()
                )
            )

    def test_deterministic(
        self,
    ):
        start = self.reevaluation_start(
            3
        )

        first = (
            GovernedRadarReevaluationPortfolioReintegrator
            .reintegrate(
                start
            )
        )

        second = (
            GovernedRadarReevaluationPortfolioReintegrator
            .reintegrate(
                start
            )
        )

        self.assertEqual(
            first,
            second,
        )

    def test_source_result_is_not_mutated(
        self,
    ):
        start = self.reevaluation_start(
            2
        )

        original_entries = start.entries
        original_evaluations = (
            start.evaluations
        )
        original_evidence_ids = (
            start.evidence_ids
        )
        original_cycle_numbers = (
            start.cycle_numbers
        )

        original_entry_ids = tuple(
            id(entry)
            for entry in start.entries
        )

        original_evaluation_ids = tuple(
            id(evaluation)
            for evaluation
            in start.evaluations
        )

        original_observation_ids = tuple(
            id(
                evaluation.observation
            )
            for evaluation
            in start.evaluations
        )

        (
            GovernedRadarReevaluationPortfolioReintegrator
            .reintegrate(
                start
            )
        )

        self.assertIs(
            start.entries,
            original_entries,
        )

        self.assertEqual(
            start.evaluations,
            original_evaluations,
        )

        self.assertEqual(
            start.evidence_ids,
            original_evidence_ids,
        )

        self.assertEqual(
            start.cycle_numbers,
            original_cycle_numbers,
        )

        self.assertEqual(
            tuple(
                id(entry)
                for entry
                in start.entries
            ),
            original_entry_ids,
        )

        self.assertEqual(
            tuple(
                id(evaluation)
                for evaluation
                in start.evaluations
            ),
            original_evaluation_ids,
        )

        self.assertEqual(
            tuple(
                id(
                    evaluation.observation
                )
                for evaluation
                in start.evaluations
            ),
            original_observation_ids,
        )

    def test_static_boundary_is_exact(
        self,
    ):
        path = Path(
            "src/maestro/research/"
            "radar_research_portfolio_reintegration.py"
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
            "radar.rank",
            calls,
        )

        forbidden_calls = {
            "GovernedRadarEvaluationPipeline",
            "GovernedRadarEvaluationPipeline.evaluate",
            "pipeline.evaluate",
            "GovernedRadarPortfolio",
            "GovernedRadarPortfolio.evaluate",
            "GovernedRadarDecisionEnvelope.evaluate",
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
            "radar_decision_envelope",
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
