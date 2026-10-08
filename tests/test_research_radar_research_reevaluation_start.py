from __future__ import annotations

import ast
import unittest

from pathlib import Path

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
    RadarEvaluationContext,
    RadarFollowUpCycleContext,
    RadarFollowUpCycleDisposition,
    RadarFollowUpCycleGovernanceDisposition,
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
)

from maestro.tools.registry import (
    ToolRegistry,
    ToolSpec,
)


class RadarReevaluationStartTests(
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
                    f"adel025-{counter['value']}"
                ),
                label="ADEL0.25 source",
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
                description="ADEL0.25 search",
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
                f"adel025-origin-{suffix}"
            ),
            label=f"ADEL0.25 {suffix}",
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

    def governance(
        self,
        count=1,
        *,
        stop_first=False,
        completed_cycles=0,
    ):
        reintegration = self.reintegration(
            count
        )

        decisions = {
            evidence_id: (
                RadarFollowUpCycleDisposition
                .ELIGIBLE_FOR_REEVALUATION
            )
            for evidence_id
            in reintegration.evidence_ids
        }

        if (
            stop_first
            and reintegration.evidence_ids
        ):
            decisions[
                reintegration.evidence_ids[0]
            ] = (
                RadarFollowUpCycleDisposition
                .STOP_CYCLE
            )

        gate = (
            GovernedRadarFollowUpCycleGate
            .decide(
                reintegration,
                decisions=decisions,
            )
        )

        contexts = {
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
        }

        return (
            GovernedRadarFollowUpCycleGovernor
            .govern(
                gate,
                contexts=contexts,
                policy=(
                    RadarFollowUpCyclePolicy(
                        max_cycles=3,
                        minimum_novelty=0.05,
                    )
                ),
            )
        )

    def reevaluation_context(
        self,
        *,
        known_claims=(
            "unrelated legacy",
        ),
    ):
        return (
            GovernedRadarEvaluationPipeline
            .context(
                known_claims=known_claims,
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

    def contexts(
        self,
        governance,
    ):
        return {
            evidence_id: (
                self.reevaluation_context()
            )
            for evidence_id
            in governance.admitted_evidence_ids
        }

    def test_empty_governance_starts_nothing(
        self,
    ):
        governance = self.governance(0)

        result = (
            GovernedRadarReevaluationStarter
            .start(
                governance,
                contexts={},
            )
        )

        self.assertEqual(
            result.size,
            0,
        )

    def test_one_authorized_entry_starts_once(
        self,
    ):
        governance = self.governance()

        result = (
            GovernedRadarReevaluationStarter
            .start(
                governance,
                contexts=self.contexts(
                    governance
                ),
            )
        )

        self.assertEqual(
            result.size,
            1,
        )

        row = result.entries[0]

        self.assertTrue(
            row.reevaluation_authorized
        )

        self.assertTrue(
            row.cycle_started
        )

        self.assertTrue(
            row.radar_evaluated
        )

    def test_cycle_number_is_completed_plus_one(
        self,
    ):
        governance = self.governance(
            completed_cycles=1
        )

        result = (
            GovernedRadarReevaluationStarter
            .start(
                governance,
                contexts=self.contexts(
                    governance
                ),
            )
        )

        self.assertEqual(
            result.entries[0]
            .cycle_number,
            2,
        )

    def test_missing_context_fails_closed(
        self,
    ):
        governance = self.governance()

        with self.assertRaisesRegex(
            ValueError,
            "missing=",
        ):
            (
                GovernedRadarReevaluationStarter
                .start(
                    governance,
                    contexts={},
                )
            )

    def test_extra_context_fails_closed(
        self,
    ):
        governance = self.governance(
            1,
            stop_first=True,
        )

        with self.assertRaisesRegex(
            ValueError,
            "extra=",
        ):
            (
                GovernedRadarReevaluationStarter
                .start(
                    governance,
                    contexts={
                        governance
                        .evidence_ids[0]:
                        self.reevaluation_context()
                    },
                )
            )

    def test_wrong_input_fails_closed(
        self,
    ):
        with self.assertRaises(
            TypeError
        ):
            (
                GovernedRadarReevaluationStarter
                .start(
                    object(),
                    contexts={},
                )
            )

        governance = self.governance()

        with self.assertRaises(
            TypeError
        ):
            (
                GovernedRadarReevaluationStarter
                .start(
                    governance,
                    contexts=object(),
                )
            )

    def test_wrong_context_type_fails_closed(
        self,
    ):
        governance = self.governance()

        with self.assertRaises(
            TypeError
        ):
            (
                GovernedRadarReevaluationStarter
                .start(
                    governance,
                    contexts={
                        governance
                        .admitted_evidence_ids[0]:
                        object()
                    },
                )
            )

    def test_known_claims_context_drift_fails_closed(
        self,
    ):
        governance = self.governance()

        evidence_id = (
            governance
            .admitted_evidence_ids[0]
        )

        with self.assertRaisesRegex(
            ValueError,
            "known_claims",
        ):
            (
                GovernedRadarReevaluationStarter
                .start(
                    governance,
                    contexts={
                        evidence_id: (
                            self
                            .reevaluation_context(
                                known_claims=(
                                    "different history",
                                )
                            )
                        )
                    },
                )
            )

    def test_evidence_identity_and_lineage_preserved(
        self,
    ):
        governance = self.governance()

        row = (
            GovernedRadarReevaluationStarter
            .start(
                governance,
                contexts=self.contexts(
                    governance
                ),
            )
            .entries[0]
        )

        self.assertIs(
            row.evidence,
            row.source_entry.evidence,
        )

        self.assertEqual(
            row.evaluation.evidence_id,
            row.evidence_id,
        )

        self.assertEqual(
            row.evaluation
            .observation
            .task_id,
            row.task_id,
        )

        self.assertEqual(
            row.evaluation
            .observation
            .source_ref,
            row.evidence.source_ref,
        )

        self.assertEqual(
            row.evaluation
            .observation
            .claim,
            row.evidence.claim,
        )

    def test_novelty_matches_cycle_governance(
        self,
    ):
        governance = self.governance()

        row = (
            GovernedRadarReevaluationStarter
            .start(
                governance,
                contexts=self.contexts(
                    governance
                ),
            )
            .entries[0]
        )

        self.assertEqual(
            row.evaluation
            .novelty_relevance
            .novelty,
            row.source_entry.novelty,
        )

    def test_evaluation_produces_all_seven_factors(
        self,
    ):
        governance = self.governance()

        row = (
            GovernedRadarReevaluationStarter
            .start(
                governance,
                contexts=self.contexts(
                    governance
                ),
            )
            .entries[0]
        )

        factors = row.evaluation.factors

        values = (
            factors.novelty,
            factors.source_quality,
            factors.relevance_to_maestro,
            factors.expected_capability_gain,
            factors.reproducibility,
            factors.integration_cost,
            factors.security_risk,
        )

        self.assertEqual(
            len(values),
            7,
        )

        for value in values:
            self.assertGreaterEqual(
                value,
                0.0,
            )
            self.assertLessEqual(
                value,
                1.0,
            )

    def test_unverified_boundary_preserved(
        self,
    ):
        governance = self.governance()

        row = (
            GovernedRadarReevaluationStarter
            .start(
                governance,
                contexts=self.contexts(
                    governance
                ),
            )
            .entries[0]
        )

        self.assertEqual(
            row.verification_status,
            "UNVERIFIED_EXTERNAL",
        )

        self.assertEqual(
            row.evaluation
            .observation
            .verification_status,
            "UNVERIFIED_EXTERNAL",
        )

        self.assertFalse(
            row.system_truth_asserted
        )

        self.assertFalse(
            row.evaluation
            .observation
            .system_truth_asserted
        )

    def test_stopped_governance_entries_are_not_evaluated(
        self,
    ):
        governance = self.governance(
            2,
            stop_first=True,
        )

        result = (
            GovernedRadarReevaluationStarter
            .start(
                governance,
                contexts=self.contexts(
                    governance
                ),
            )
        )

        self.assertEqual(
            result.evidence_ids,
            governance.admitted_evidence_ids,
        )

        self.assertEqual(
            result.size,
            1,
        )

        self.assertNotIn(
            governance.stopped_evidence_ids[0],
            result.evidence_ids,
        )

    def test_multiple_admitted_preserve_order(
        self,
    ):
        governance = self.governance(3)

        result = (
            GovernedRadarReevaluationStarter
            .start(
                governance,
                contexts=self.contexts(
                    governance
                ),
            )
        )

        self.assertEqual(
            result.evidence_ids,
            governance.admitted_evidence_ids,
        )

        self.assertEqual(
            result.size,
            3,
        )

    def test_no_portfolio_decision_review_or_followup(
        self,
    ):
        governance = self.governance()

        row = (
            GovernedRadarReevaluationStarter
            .start(
                governance,
                contexts=self.contexts(
                    governance
                ),
            )
            .entries[0]
        )

        self.assertFalse(
            row.portfolio_created
        )

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
        governance = self.governance()

        row = (
            GovernedRadarReevaluationStarter
            .start(
                governance,
                contexts=self.contexts(
                    governance
                ),
            )
            .entries[0]
        )

        self.assertFalse(
            row.new_research_request_created
        )

        self.assertFalse(
            row.network_requested
        )

        self.assertFalse(
            row.tool_execution_requested
        )

        self.assertFalse(
            row.persistence_requested
        )

        self.assertFalse(
            row.mission_transition_requested
        )

        self.assertFalse(
            row.execution_asserted
        )

    def test_no_truth_ay_ex_learning_promotion_activation(
        self,
    ):
        governance = self.governance()

        row = (
            GovernedRadarReevaluationStarter
            .start(
                governance,
                contexts=self.contexts(
                    governance
                ),
            )
            .entries[0]
        )

        self.assertFalse(
            row.system_truth_asserted
        )

        self.assertFalse(
            row.ay_validation_asserted
        )

        self.assertFalse(
            row.ex_authorization_asserted
        )

        self.assertFalse(
            row.learning_asserted
        )

        self.assertFalse(
            row.promotion_asserted
        )

        self.assertFalse(
            row.activation_asserted
        )

    def test_deterministic_and_static_boundary(
        self,
    ):
        governance = self.governance()

        contexts = self.contexts(
            governance
        )

        first = (
            GovernedRadarReevaluationStarter
            .start(
                governance,
                contexts=contexts,
            )
        )

        second = (
            GovernedRadarReevaluationStarter
            .start(
                governance,
                contexts=contexts,
            )
        )

        self.assertEqual(
            first,
            second,
        )

        path = Path(
            "src/maestro/research/"
            "radar_research_reevaluation_start.py"
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
            "pipeline.evaluate",
            calls,
        )

        forbidden_calls = {
            "GovernedRadarPortfolio.evaluate",
            "TechnologyRadar.rank",
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
            "radar_portfolio",
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
