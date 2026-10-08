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
    GovernedRadarPortfolio,
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
    RadarFollowUpCycleDisposition,
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


class RadarFollowUpCycleGateTests(
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

    def packet(
        self,
        suffix="returned",
    ):
        statement = (
            "External source reports "
            f"research observation {suffix}."
        )

        source = ResearchSource(
            (
                "https://example.com/"
                f"{suffix}"
            ),
            label="ADEL0.23 source",
        )

        provenance = SourceProvenance(
            source_id=source.source_id,
            retrieved_at=self.NOW,
            digest=ContentDigest.from_bytes(
                statement.encode("utf-8")
            ),
            author="External Provider",
            version="1",
        )

        return RadarResearchProviderReturnPacket(
            provider_id="alpha",
            tool_name="alpha.search",
            source=source,
            provenance=provenance,
            claim_statement=statement,
            artifact_kind="DOCUMENT",
            media_type="text/plain",
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

            return self.packet(
                f"returned-{counter['value']}"
            )

        tools = ToolRegistry()

        tools.register(
            ToolSpec(
                name="alpha.search",
                description="ADEL0.23 search",
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
                f"adel023-{suffix}"
            ),
            label=f"ADEL0.23 {suffix}",
        )

        provenance = SourceProvenance(
            source_id=source.source_id,
            retrieved_at=self.NOW,
            digest=ContentDigest.from_bytes(
                statement.encode("utf-8")
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

        return ResearchEvidenceBridge.to_evidence(
            task_id=self.TASK_A,
            claim=claim,
            artifacts=[artifact],
        )

    def context(
        self,
    ):
        return GovernedRadarEvaluationPipeline.context(
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
                        context=self.context(),
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

        review_handoff = (
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
                review_handoff,
                responses={
                    entry.evidence_id: (
                        RadarReviewResponseValue
                        .REQUEST_MORE_EVIDENCE
                    )
                    for entry
                    in review_handoff.entries
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

        admitted = (
            GovernedRadarResearchProviderReturnAdmission
            .admit(
                execution
            )
        )

        return (
            GovernedRadarResearchEvidenceReintegrator
            .reintegrate(
                admitted
            )
        )

    def decisions(
        self,
        reintegration,
        disposition,
    ):
        return {
            evidence_id: disposition
            for evidence_id
            in reintegration.evidence_ids
        }

    def test_empty_reintegration_with_empty_decisions(
        self,
    ):
        reintegration = self.reintegration(
            0
        )

        result = (
            GovernedRadarFollowUpCycleGate
            .decide(
                reintegration,
                decisions={},
            )
        )

        self.assertEqual(
            result.size,
            0,
        )

    def test_explicit_eligible_decision(
        self,
    ):
        reintegration = self.reintegration()

        result = (
            GovernedRadarFollowUpCycleGate
            .decide(
                reintegration,
                decisions=self.decisions(
                    reintegration,
                    RadarFollowUpCycleDisposition
                    .ELIGIBLE_FOR_REEVALUATION,
                ),
            )
        )

        row = result.entries[0]

        self.assertTrue(
            row.eligible_for_reevaluation
        )

        self.assertFalse(
            row.stop_cycle
        )

    def test_explicit_stop_decision(
        self,
    ):
        reintegration = self.reintegration()

        result = (
            GovernedRadarFollowUpCycleGate
            .decide(
                reintegration,
                decisions=self.decisions(
                    reintegration,
                    RadarFollowUpCycleDisposition
                    .STOP_CYCLE,
                ),
            )
        )

        row = result.entries[0]

        self.assertTrue(
            row.stop_cycle
        )

        self.assertFalse(
            row.eligible_for_reevaluation
        )

    def test_mixed_decisions_preserve_order(
        self,
    ):
        reintegration = self.reintegration(
            3
        )

        ids = reintegration.evidence_ids

        decisions = {
            ids[0]: (
                RadarFollowUpCycleDisposition
                .ELIGIBLE_FOR_REEVALUATION
            ),
            ids[1]: (
                RadarFollowUpCycleDisposition
                .STOP_CYCLE
            ),
            ids[2]: (
                RadarFollowUpCycleDisposition
                .ELIGIBLE_FOR_REEVALUATION
            ),
        }

        result = (
            GovernedRadarFollowUpCycleGate
            .decide(
                reintegration,
                decisions=decisions,
            )
        )

        self.assertEqual(
            result.evidence_ids,
            ids,
        )

        self.assertEqual(
            tuple(
                row.disposition
                for row in result.entries
            ),
            (
                decisions[ids[0]],
                decisions[ids[1]],
                decisions[ids[2]],
            ),
        )

    def test_missing_decision_fails_closed(
        self,
    ):
        reintegration = self.reintegration(
            2
        )

        with self.assertRaisesRegex(
            ValueError,
            "missing=",
        ):
            (
                GovernedRadarFollowUpCycleGate
                .decide(
                    reintegration,
                    decisions={
                        reintegration
                        .evidence_ids[0]:
                        (
                            RadarFollowUpCycleDisposition
                            .STOP_CYCLE
                        )
                    },
                )
            )

    def test_extra_decision_fails_closed(
        self,
    ):
        reintegration = self.reintegration()

        decisions = self.decisions(
            reintegration,
            RadarFollowUpCycleDisposition
            .STOP_CYCLE,
        )

        decisions[
            "EVD-AAAAAAAAAAAA"
        ] = (
            RadarFollowUpCycleDisposition
            .STOP_CYCLE
        )

        with self.assertRaisesRegex(
            ValueError,
            "extra=",
        ):
            (
                GovernedRadarFollowUpCycleGate
                .decide(
                    reintegration,
                    decisions=decisions,
                )
            )

    def test_invalid_decision_key_fails_closed(
        self,
    ):
        reintegration = self.reintegration()

        with self.assertRaises(
            ValueError
        ):
            (
                GovernedRadarFollowUpCycleGate
                .decide(
                    reintegration,
                    decisions={
                        "": (
                            RadarFollowUpCycleDisposition
                            .STOP_CYCLE
                        )
                    },
                )
            )

    def test_invalid_disposition_fails_closed(
        self,
    ):
        reintegration = self.reintegration()

        with self.assertRaises(
            TypeError
        ):
            (
                GovernedRadarFollowUpCycleGate
                .decide(
                    reintegration,
                    decisions={
                        reintegration
                        .evidence_ids[0]:
                        "ELIGIBLE_FOR_REEVALUATION"
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
                GovernedRadarFollowUpCycleGate
                .decide(
                    object(),
                    decisions={},
                )
            )

        reintegration = self.reintegration()

        with self.assertRaises(
            TypeError
        ):
            (
                GovernedRadarFollowUpCycleGate
                .decide(
                    reintegration,
                    decisions=object(),
                )
            )

    def test_source_entry_identity_preserved(
        self,
    ):
        reintegration = self.reintegration()

        result = (
            GovernedRadarFollowUpCycleGate
            .decide(
                reintegration,
                decisions=self.decisions(
                    reintegration,
                    RadarFollowUpCycleDisposition
                    .STOP_CYCLE,
                ),
            )
        )

        self.assertIs(
            result.entries[0]
            .source_entry,
            reintegration.entries[0],
        )

    def test_evidence_identity_and_lineage_preserved(
        self,
    ):
        reintegration = self.reintegration()

        result = (
            GovernedRadarFollowUpCycleGate
            .decide(
                reintegration,
                decisions=self.decisions(
                    reintegration,
                    RadarFollowUpCycleDisposition
                    .ELIGIBLE_FOR_REEVALUATION,
                ),
            )
        )

        before = reintegration.entries[0]
        after = result.entries[0]

        self.assertIs(
            after.evidence,
            before.evidence,
        )

        self.assertEqual(
            after.evidence_id,
            before.returned_evidence_id,
        )

        self.assertEqual(
            after.origin_evidence_id,
            before.origin_evidence_id,
        )

        self.assertEqual(
            after.task_id,
            before.task_id,
        )

        self.assertEqual(
            after.provider_id,
            before.provider_id,
        )

        self.assertEqual(
            after.tool_name,
            before.tool_name,
        )

    def test_eligible_and_stopped_id_sets(
        self,
    ):
        reintegration = self.reintegration(
            3
        )

        ids = reintegration.evidence_ids

        result = (
            GovernedRadarFollowUpCycleGate
            .decide(
                reintegration,
                decisions={
                    ids[0]: (
                        RadarFollowUpCycleDisposition
                        .ELIGIBLE_FOR_REEVALUATION
                    ),
                    ids[1]: (
                        RadarFollowUpCycleDisposition
                        .STOP_CYCLE
                    ),
                    ids[2]: (
                        RadarFollowUpCycleDisposition
                        .STOP_CYCLE
                    ),
                },
            )
        )

        self.assertEqual(
            result.eligible_evidence_ids,
            (ids[0],),
        )

        self.assertEqual(
            result.stopped_evidence_ids,
            (
                ids[1],
                ids[2],
            ),
        )

    def test_unverified_boundary_preserved(
        self,
    ):
        reintegration = self.reintegration()

        row = (
            GovernedRadarFollowUpCycleGate
            .decide(
                reintegration,
                decisions=self.decisions(
                    reintegration,
                    RadarFollowUpCycleDisposition
                    .ELIGIBLE_FOR_REEVALUATION,
                ),
            )
            .entries[0]
        )

        self.assertEqual(
            row.verification_status,
            "UNVERIFIED_EXTERNAL",
        )

        self.assertEqual(
            row.evidence.payload[
                "verification"
            ][
                "required_authority"
            ],
            CouncilId.AY.value,
        )

        self.assertFalse(
            row.system_truth_asserted
        )

    def test_no_radar_evaluation_or_cycle_start(
        self,
    ):
        reintegration = self.reintegration()

        row = (
            GovernedRadarFollowUpCycleGate
            .decide(
                reintegration,
                decisions=self.decisions(
                    reintegration,
                    RadarFollowUpCycleDisposition
                    .ELIGIBLE_FOR_REEVALUATION,
                ),
            )
            .entries[0]
        )

        self.assertTrue(
            row.eligible_for_reevaluation
        )

        self.assertFalse(
            row.cycle_started
        )

        self.assertFalse(
            row.radar_evaluated
        )

        self.assertFalse(
            row.reevaluation_authorized
        )

    def test_no_new_request_network_or_execution(
        self,
    ):
        reintegration = self.reintegration()

        row = (
            GovernedRadarFollowUpCycleGate
            .decide(
                reintegration,
                decisions=self.decisions(
                    reintegration,
                    RadarFollowUpCycleDisposition
                    .ELIGIBLE_FOR_REEVALUATION,
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
            row.execution_asserted
        )

    def test_no_persistence_or_mission_transition(
        self,
    ):
        reintegration = self.reintegration()

        row = (
            GovernedRadarFollowUpCycleGate
            .decide(
                reintegration,
                decisions=self.decisions(
                    reintegration,
                    RadarFollowUpCycleDisposition
                    .STOP_CYCLE,
                ),
            )
            .entries[0]
        )

        self.assertFalse(
            row.persistence_requested
        )

        self.assertFalse(
            row.mission_transition_requested
        )

    def test_no_truth_learning_or_authority(
        self,
    ):
        reintegration = self.reintegration()

        row = (
            GovernedRadarFollowUpCycleGate
            .decide(
                reintegration,
                decisions=self.decisions(
                    reintegration,
                    RadarFollowUpCycleDisposition
                    .ELIGIBLE_FOR_REEVALUATION,
                ),
            )
            .entries[0]
        )

        self.assertFalse(
            row.system_truth_asserted
        )

        self.assertFalse(
            row.learning_asserted
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

    def test_deterministic_and_static_boundary(
        self,
    ):
        reintegration = self.reintegration()

        decisions = self.decisions(
            reintegration,
            RadarFollowUpCycleDisposition
            .ELIGIBLE_FOR_REEVALUATION,
        )

        first = (
            GovernedRadarFollowUpCycleGate
            .decide(
                reintegration,
                decisions=decisions,
            )
        )

        second = (
            GovernedRadarFollowUpCycleGate
            .decide(
                reintegration,
                decisions=decisions,
            )
        )

        self.assertEqual(
            first,
            second,
        )

        path = Path(
            "src/maestro/research/"
            "radar_research_followup_cycle_gate.py"
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

        forbidden_calls = {
            "TechnologyRadar",
            "TechnologyRadar.assess",
            "GovernedRadarEvaluationPipeline.evaluate",
            "GovernedRadarPortfolio.evaluate",
            "ResearchEvidenceStore",
            "ResearchEvidenceStore.record",
            "GovernedResearchRuntime.route",
            "GovernedResearchRuntime.execute",
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
            "technology_radar",
            "radar_evaluation_pipeline",
            "radar_portfolio",
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
