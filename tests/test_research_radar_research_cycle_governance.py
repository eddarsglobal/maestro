from __future__ import annotations

import ast
import unittest

from pathlib import Path

from maestro.enums import (
    CouncilId,
    SideEffectLevel,
)

from maestro.research import (
    MAX_RADAR_FOLLOWUP_CYCLES,
    ContentDigest,
    ExternalArtifact,
    GovernedRadarDecisionEnvelope,
    GovernedRadarEvidenceFollowUp,
    GovernedRadarEvaluationPipeline,
    GovernedRadarFollowUpCandidateBuilder,
    GovernedRadarFollowUpCycleGate,
    GovernedRadarFollowUpCycleGovernor,
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


class RadarFollowUpCycleGovernanceTests(
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
                    f"adel024-{counter['value']}"
                ),
                label="ADEL0.24 source",
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
                description="ADEL0.24 search",
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
                f"adel024-origin-{suffix}"
            ),
            label=f"ADEL0.24 {suffix}",
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

    def evaluation_context(
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
                            self.evaluation_context()
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

    def gate(
        self,
        count=1,
        *,
        stop_first=False,
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

        return (
            GovernedRadarFollowUpCycleGate
            .decide(
                reintegration,
                decisions=decisions,
            )
        )

    def context(
        self,
        *,
        completed_cycles=0,
        seen_evidence_ids=(),
        seen_content_digests=(),
        known_claims=(),
    ):
        return RadarFollowUpCycleContext(
            completed_cycles=(
                completed_cycles
            ),
            seen_evidence_ids=(
                seen_evidence_ids
            ),
            seen_content_digests=(
                seen_content_digests
            ),
            known_claims=known_claims,
        )

    def contexts(
        self,
        gate,
        *,
        completed_cycles=0,
        known_claims=(),
    ):
        return {
            evidence_id: self.context(
                completed_cycles=(
                    completed_cycles
                ),
                known_claims=known_claims,
            )
            for evidence_id
            in gate.eligible_evidence_ids
        }

    def policy(
        self,
        *,
        max_cycles=3,
        minimum_novelty=0.05,
    ):
        return RadarFollowUpCyclePolicy(
            max_cycles=max_cycles,
            minimum_novelty=(
                minimum_novelty
            ),
        )

    def test_policy_rejects_invalid_cycle_limits(
        self,
    ):
        for value in (
            0,
            MAX_RADAR_FOLLOWUP_CYCLES + 1,
            -1,
        ):
            with self.subTest(
                value=value
            ):
                with self.assertRaises(
                    ValueError
                ):
                    RadarFollowUpCyclePolicy(
                        max_cycles=value
                    )

        with self.assertRaises(
            TypeError
        ):
            RadarFollowUpCyclePolicy(
                max_cycles=True
            )

    def test_context_rejects_invalid_values(
        self,
    ):
        with self.assertRaises(
            ValueError
        ):
            self.context(
                completed_cycles=-1
            )

        with self.assertRaises(
            ValueError
        ):
            self.context(
                seen_content_digests=(
                    "not-a-sha256",
                )
            )

        with self.assertRaises(
            ValueError
        ):
            self.context(
                known_claims=("",)
            )

    def test_empty_gate_is_empty(
        self,
    ):
        gate = self.gate(0)

        result = (
            GovernedRadarFollowUpCycleGovernor
            .govern(
                gate,
                contexts={},
                policy=self.policy(),
            )
        )

        self.assertEqual(
            result.size,
            0,
        )

    def test_upstream_stop_requires_no_context(
        self,
    ):
        gate = self.gate(
            1,
            stop_first=True,
        )

        result = (
            GovernedRadarFollowUpCycleGovernor
            .govern(
                gate,
                contexts={},
                policy=self.policy(),
            )
        )

        row = result.entries[0]

        self.assertIs(
            row.disposition,
            RadarFollowUpCycleGovernanceDisposition
            .STOP_NOT_ELIGIBLE,
        )

        self.assertIsNone(
            row.context
        )

        self.assertFalse(
            row.reevaluation_authorized
        )

    def test_missing_context_fails_closed(
        self,
    ):
        gate = self.gate()

        with self.assertRaisesRegex(
            ValueError,
            "missing=",
        ):
            (
                GovernedRadarFollowUpCycleGovernor
                .govern(
                    gate,
                    contexts={},
                    policy=self.policy(),
                )
            )

    def test_extra_context_fails_closed(
        self,
    ):
        gate = self.gate(
            1,
            stop_first=True,
        )

        with self.assertRaisesRegex(
            ValueError,
            "extra=",
        ):
            (
                GovernedRadarFollowUpCycleGovernor
                .govern(
                    gate,
                    contexts={
                        gate.evidence_ids[0]:
                        self.context()
                    },
                    policy=self.policy(),
                )
            )

    def test_budget_exhaustion_stops_cycle(
        self,
    ):
        gate = self.gate()

        result = (
            GovernedRadarFollowUpCycleGovernor
            .govern(
                gate,
                contexts=self.contexts(
                    gate,
                    completed_cycles=3,
                ),
                policy=self.policy(
                    max_cycles=3
                ),
            )
        )

        self.assertIs(
            result.entries[0].disposition,
            RadarFollowUpCycleGovernanceDisposition
            .STOP_BUDGET,
        )

        self.assertFalse(
            result.entries[0]
            .reevaluation_authorized
        )

    def test_duplicate_evidence_id_stops_cycle(
        self,
    ):
        gate = self.gate()
        evidence_id = (
            gate.evidence_ids[0]
        )

        result = (
            GovernedRadarFollowUpCycleGovernor
            .govern(
                gate,
                contexts={
                    evidence_id: self.context(
                        seen_evidence_ids=(
                            evidence_id,
                        )
                    )
                },
                policy=self.policy(),
            )
        )

        self.assertIs(
            result.entries[0].disposition,
            RadarFollowUpCycleGovernanceDisposition
            .STOP_DUPLICATE,
        )

    def test_duplicate_content_digest_stops_cycle(
        self,
    ):
        gate = self.gate()

        digest = (
            gate.entries[0]
            .source_entry
            .return_packet
            .provenance
            .digest
            .hex_digest
        )

        result = (
            GovernedRadarFollowUpCycleGovernor
            .govern(
                gate,
                contexts={
                    gate.evidence_ids[0]:
                    self.context(
                        seen_content_digests=(
                            digest,
                        )
                    )
                },
                policy=self.policy(),
            )
        )

        self.assertIs(
            result.entries[0].disposition,
            RadarFollowUpCycleGovernanceDisposition
            .STOP_DUPLICATE,
        )

    def test_semantic_convergence_stops_cycle(
        self,
    ):
        gate = self.gate()
        claim = gate.entries[0].claim

        result = (
            GovernedRadarFollowUpCycleGovernor
            .govern(
                gate,
                contexts=self.contexts(
                    gate,
                    known_claims=(
                        claim,
                    ),
                ),
                policy=self.policy(
                    minimum_novelty=0.0
                ),
            )
        )

        row = result.entries[0]

        self.assertIs(
            row.disposition,
            RadarFollowUpCycleGovernanceDisposition
            .STOP_CONVERGED,
        )

        self.assertEqual(
            row.novelty,
            0.0,
        )

    def test_fresh_evidence_is_admitted(
        self,
    ):
        gate = self.gate()

        result = (
            GovernedRadarFollowUpCycleGovernor
            .govern(
                gate,
                contexts=self.contexts(
                    gate,
                    known_claims=(
                        "totally unrelated legacy",
                    ),
                ),
                policy=self.policy(),
            )
        )

        row = result.entries[0]

        self.assertIs(
            row.disposition,
            RadarFollowUpCycleGovernanceDisposition
            .ADMIT_REEVALUATION,
        )

        self.assertTrue(
            row.reevaluation_authorized
        )

        self.assertGreater(
            row.novelty,
            row.policy.minimum_novelty,
        )

    def test_budget_precedes_duplicate(
        self,
    ):
        gate = self.gate()
        evidence_id = (
            gate.evidence_ids[0]
        )

        result = (
            GovernedRadarFollowUpCycleGovernor
            .govern(
                gate,
                contexts={
                    evidence_id: self.context(
                        completed_cycles=3,
                        seen_evidence_ids=(
                            evidence_id,
                        ),
                    )
                },
                policy=self.policy(
                    max_cycles=3
                ),
            )
        )

        self.assertIs(
            result.entries[0].disposition,
            RadarFollowUpCycleGovernanceDisposition
            .STOP_BUDGET,
        )

    def test_result_id_sets_are_exact(
        self,
    ):
        gate = self.gate(3)

        contexts = self.contexts(
            gate,
            known_claims=(
                "totally unrelated legacy",
            ),
        )

        first_id = (
            gate.evidence_ids[0]
        )

        contexts[
            first_id
        ] = self.context(
            seen_evidence_ids=(
                first_id,
            )
        )

        result = (
            GovernedRadarFollowUpCycleGovernor
            .govern(
                gate,
                contexts=contexts,
                policy=self.policy(),
            )
        )

        self.assertEqual(
            result.evidence_ids,
            gate.evidence_ids,
        )

        self.assertEqual(
            result.stopped_evidence_ids,
            (first_id,),
        )

        self.assertEqual(
            result.admitted_evidence_ids,
            gate.evidence_ids[1:],
        )

    def test_authorization_only_for_admit(
        self,
    ):
        gate = self.gate(2)

        ids = gate.evidence_ids

        result = (
            GovernedRadarFollowUpCycleGovernor
            .govern(
                gate,
                contexts={
                    ids[0]: self.context(
                        seen_evidence_ids=(
                            ids[0],
                        )
                    ),
                    ids[1]: self.context(
                        known_claims=(
                            "unrelated legacy",
                        )
                    ),
                },
                policy=self.policy(),
            )
        )

        self.assertFalse(
            result.entries[0]
            .reevaluation_authorized
        )

        self.assertTrue(
            result.entries[1]
            .reevaluation_authorized
        )

    def test_lineage_and_source_identity_preserved(
        self,
    ):
        gate = self.gate()

        result = (
            GovernedRadarFollowUpCycleGovernor
            .govern(
                gate,
                contexts=self.contexts(
                    gate
                ),
                policy=self.policy(),
            )
        )

        row = result.entries[0]

        self.assertIs(
            row.source_entry,
            gate.entries[0],
        )

        self.assertIs(
            row.evidence,
            gate.entries[0].evidence,
        )

        self.assertEqual(
            row.evidence_id,
            gate.entries[0].evidence_id,
        )

        self.assertEqual(
            row.origin_evidence_id,
            gate.entries[0]
            .origin_evidence_id,
        )

        self.assertEqual(
            row.task_id,
            gate.entries[0].task_id,
        )

    def test_no_cycle_start_radar_request_network_or_persistence(
        self,
    ):
        gate = self.gate()

        row = (
            GovernedRadarFollowUpCycleGovernor
            .govern(
                gate,
                contexts=self.contexts(
                    gate
                ),
                policy=self.policy(),
            )
            .entries[0]
        )

        self.assertTrue(
            row.reevaluation_authorized
        )

        self.assertFalse(
            row.cycle_started
        )

        self.assertFalse(
            row.radar_evaluated
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

    def test_unverified_truth_and_authority_boundaries(
        self,
    ):
        gate = self.gate()

        row = (
            GovernedRadarFollowUpCycleGovernor
            .govern(
                gate,
                contexts=self.contexts(
                    gate
                ),
                policy=self.policy(),
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

        self.assertFalse(
            row.execution_asserted
        )

    def test_deterministic_and_static_boundary(
        self,
    ):
        gate = self.gate()

        contexts = self.contexts(
            gate,
            known_claims=(
                "unrelated legacy",
            ),
        )

        policy = self.policy()

        first = (
            GovernedRadarFollowUpCycleGovernor
            .govern(
                gate,
                contexts=contexts,
                policy=policy,
            )
        )

        second = (
            GovernedRadarFollowUpCycleGovernor
            .govern(
                gate,
                contexts=contexts,
                policy=policy,
            )
        )

        self.assertEqual(
            first,
            second,
        )

        path = Path(
            "src/maestro/research/"
            "radar_research_cycle_governance.py"
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
            "NoveltyRelevanceEvaluator.evaluate",
            calls,
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
