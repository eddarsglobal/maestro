from __future__ import annotations

import ast
import unittest

from pathlib import Path

from maestro.enums import (
    CouncilId,
    EvidenceKind,
    SideEffectLevel,
)
from maestro.models import (
    Evidence,
)

from maestro.research import (
    ContentDigest,
    ExternalArtifact,
    GovernedRadarDecisionEnvelope,
    GovernedRadarEvidenceFollowUp,
    GovernedRadarEvaluationPipeline,
    GovernedRadarFollowUpCandidateBuilder,
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
    TrustState,
)

from maestro.tools.registry import (
    ToolRegistry,
    ToolSpec,
)


class RadarResearchEvidenceReintegrationTests(
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
        *,
        claim_statement=(
            "External source reports a "
            "research observation."
        ),
        uri="https://example.com/returned",
    ):
        body = (
            claim_statement.encode(
                "utf-8"
            )
        )

        source = ResearchSource(
            uri,
            label=(
                "ADEL0.22C external source"
            ),
        )

        provenance = SourceProvenance(
            source_id=source.source_id,
            retrieved_at=self.NOW,
            digest=ContentDigest.from_bytes(
                body
            ),
            author="External Provider",
            version="1",
        )

        return RadarResearchProviderReturnPacket(
            provider_id="alpha",
            tool_name="alpha.search",
            source=source,
            provenance=provenance,
            claim_statement=claim_statement,
            artifact_kind="DOCUMENT",
            media_type="text/plain",
        )

    def runtime(
        self,
        *,
        handler=None,
    ):
        providers = ResearchProviderRegistry()

        providers.register(
            self.provider()
        )

        tools = ToolRegistry()

        if handler is None:
            handler = (
                lambda **kwargs: self.packet()
            )

        tools.register(
            ToolSpec(
                name="alpha.search",
                description=(
                    "ADEL0.22C search"
                ),
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
            "MAESTRO research"
        )

        source = ResearchSource(
            (
                "https://example.com/"
                f"adel022c-{suffix}"
            ),
            label=f"ADEL0.22C {suffix}",
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

    def admitted(
        self,
        runtime,
        count=1,
    ):
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

        return (
            GovernedRadarResearchProviderReturnAdmission
            .admit(
                execution
            )
        )

    def test_empty_admission_reintegrates_nothing(
        self,
    ):
        runtime = self.runtime()

        result = (
            GovernedRadarResearchEvidenceReintegrator
            .reintegrate(
                self.admitted(
                    runtime,
                    0,
                )
            )
        )

        self.assertEqual(
            result.size,
            0,
        )

    def test_creates_artifact_claim_and_evidence(
        self,
    ):
        runtime = self.runtime()

        row = (
            GovernedRadarResearchEvidenceReintegrator
            .reintegrate(
                self.admitted(runtime)
            )
            .entries[0]
        )

        self.assertIsInstance(
            row.artifact,
            ExternalArtifact,
        )

        self.assertIsInstance(
            row.research_claim,
            ResearchClaim,
        )

        self.assertIsInstance(
            row.evidence,
            Evidence,
        )

    def test_source_and_provenance_identity_preserved(
        self,
    ):
        runtime = self.runtime()
        admitted = self.admitted(runtime)

        row = (
            GovernedRadarResearchEvidenceReintegrator
            .reintegrate(admitted)
            .entries[0]
        )

        packet = (
            admitted.entries[0]
            .return_packet
        )

        self.assertIs(
            row.artifact.source,
            packet.source,
        )

        self.assertIs(
            row.artifact.provenance,
            packet.provenance,
        )

    def test_artifact_metadata_matches_return_packet(
        self,
    ):
        runtime = self.runtime()
        admitted = self.admitted(runtime)

        row = (
            GovernedRadarResearchEvidenceReintegrator
            .reintegrate(admitted)
            .entries[0]
        )

        packet = (
            admitted.entries[0]
            .return_packet
        )

        self.assertEqual(
            row.artifact.artifact_kind,
            packet.artifact_kind,
        )

        self.assertEqual(
            row.artifact.media_type,
            packet.media_type,
        )

    def test_claim_binds_exact_constructed_artifact(
        self,
    ):
        runtime = self.runtime()

        row = (
            GovernedRadarResearchEvidenceReintegrator
            .reintegrate(
                self.admitted(runtime)
            )
            .entries[0]
        )

        self.assertEqual(
            row.research_claim.artifact_ids,
            (
                row.artifact.artifact_id,
            ),
        )

    def test_claim_and_artifact_remain_untrusted(
        self,
    ):
        runtime = self.runtime()

        row = (
            GovernedRadarResearchEvidenceReintegrator
            .reintegrate(
                self.admitted(runtime)
            )
            .entries[0]
        )

        self.assertIs(
            row.artifact.trust_state,
            TrustState.UNTRUSTED,
        )

        self.assertIs(
            row.research_claim.trust_state,
            TrustState.UNTRUSTED,
        )

    def test_evidence_is_rx_web_source(
        self,
    ):
        runtime = self.runtime()

        row = (
            GovernedRadarResearchEvidenceReintegrator
            .reintegrate(
                self.admitted(runtime)
            )
            .entries[0]
        )

        self.assertIs(
            row.evidence.council,
            CouncilId.RX,
        )

        self.assertIs(
            row.evidence.kind,
            EvidenceKind.WEB_SOURCE,
        )

        self.assertEqual(
            row.evidence.source_ref,
            row.research_claim.claim_id,
        )

    def test_bridge_verification_boundary_preserved(
        self,
    ):
        runtime = self.runtime()

        row = (
            GovernedRadarResearchEvidenceReintegrator
            .reintegrate(
                self.admitted(runtime)
            )
            .entries[0]
        )

        verification = (
            row.evidence.payload[
                "verification"
            ]
        )

        self.assertEqual(
            verification["status"],
            "UNVERIFIED_EXTERNAL",
        )

        self.assertEqual(
            verification[
                "required_authority"
            ],
            CouncilId.AY.value,
        )

        self.assertFalse(
            verification[
                "system_truth_asserted"
            ]
        )

    def test_ids_are_deterministic(
        self,
    ):
        runtime = self.runtime()
        admitted = self.admitted(runtime)

        first = (
            GovernedRadarResearchEvidenceReintegrator
            .reintegrate(admitted)
        )

        second = (
            GovernedRadarResearchEvidenceReintegrator
            .reintegrate(admitted)
        )

        self.assertEqual(
            first.entries[0]
            .artifact.artifact_id,
            second.entries[0]
            .artifact.artifact_id,
        )

        self.assertEqual(
            first.entries[0]
            .research_claim.claim_id,
            second.entries[0]
            .research_claim.claim_id,
        )

        self.assertEqual(
            first.entries[0]
            .evidence.evidence_id,
            second.entries[0]
            .evidence.evidence_id,
        )

        self.assertEqual(
            first,
            second,
        )

    def test_timestamps_derive_from_provenance(
        self,
    ):
        runtime = self.runtime()
        admitted = self.admitted(runtime)

        row = (
            GovernedRadarResearchEvidenceReintegrator
            .reintegrate(admitted)
            .entries[0]
        )

        retrieved_at = (
            admitted.entries[0]
            .return_packet
            .provenance
            .retrieved_at
        )

        self.assertEqual(
            row.research_claim.created_at,
            retrieved_at,
        )

        self.assertEqual(
            row.evidence.created_at,
            retrieved_at,
        )

    def test_order_and_lineage_are_preserved(
        self,
    ):
        runtime = self.runtime()
        admitted = self.admitted(
            runtime,
            3,
        )

        result = (
            GovernedRadarResearchEvidenceReintegrator
            .reintegrate(admitted)
        )

        self.assertEqual(
            result.origin_evidence_ids,
            admitted.evidence_ids,
        )

        self.assertEqual(
            result.task_ids,
            admitted.task_ids,
        )

        self.assertEqual(
            result.provider_ids,
            admitted.provider_ids,
        )

        self.assertEqual(
            result.tool_names,
            admitted.tool_names,
        )

    def test_returned_evidence_ids_are_unique(
        self,
    ):
        runtime = self.runtime()

        result = (
            GovernedRadarResearchEvidenceReintegrator
            .reintegrate(
                self.admitted(
                    runtime,
                    3,
                )
            )
        )

        self.assertEqual(
            len(result.evidence_ids),
            len(set(result.evidence_ids)),
        )

    def test_reintegration_flags_are_exact(
        self,
    ):
        runtime = self.runtime()

        row = (
            GovernedRadarResearchEvidenceReintegrator
            .reintegrate(
                self.admitted(runtime)
            )
            .entries[0]
        )

        self.assertTrue(
            row.provider_return_admitted
        )
        self.assertTrue(
            row.external_artifact_created
        )
        self.assertTrue(
            row.research_claim_created
        )
        self.assertTrue(
            row.evidence_created
        )
        self.assertTrue(
            row.evidence_model_reintegrated
        )

    def test_no_persistence_radar_or_followup(
        self,
    ):
        runtime = self.runtime()

        row = (
            GovernedRadarResearchEvidenceReintegrator
            .reintegrate(
                self.admitted(runtime)
            )
            .entries[0]
        )

        self.assertFalse(
            row.evidence_persisted
        )
        self.assertFalse(
            row.radar_evaluated
        )
        self.assertFalse(
            row.followup_authorized
        )
        self.assertFalse(
            row.persistence_requested
        )
        self.assertFalse(
            row.mission_transition_requested
        )
        self.assertFalse(
            row.new_network_requested
        )

    def test_no_truth_learning_or_authority(
        self,
    ):
        runtime = self.runtime()

        row = (
            GovernedRadarResearchEvidenceReintegrator
            .reintegrate(
                self.admitted(runtime)
            )
            .entries[0]
        )

        self.assertEqual(
            row.verification_status,
            "UNVERIFIED_EXTERNAL",
        )

        self.assertEqual(
            row.network_access_status,
            "UNKNOWN",
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

    def test_invalid_claim_content_fails_closed(
        self,
    ):
        runtime = self.runtime(
            handler=lambda **kwargs: (
                self.packet(
                    claim_statement=(
                        "invalid\x00claim"
                    )
                )
            )
        )

        admitted = self.admitted(runtime)

        with self.assertRaises(
            ValueError
        ):
            (
                GovernedRadarResearchEvidenceReintegrator
                .reintegrate(admitted)
            )

    def test_wrong_input_fails_closed(
        self,
    ):
        with self.assertRaises(
            TypeError
        ):
            (
                GovernedRadarResearchEvidenceReintegrator
                .reintegrate(
                    object()
                )
            )

    def test_static_boundary_is_exact(
        self,
    ):
        path = Path(
            "src/maestro/research/"
            "radar_research_evidence_reintegration.py"
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
            "ResearchEvidenceBridge.to_evidence",
            calls,
        )

        forbidden_calls = {
            "runtime.execute",
            "runtime.execute_exact",
            "runtime.route",
            "runtime.tools.invoke",
            "ResearchEvidenceStore",
            "TechnologyRadar",
            "TechnologyRadar.assess",
            "GovernedRadarEvaluationPipeline.evaluate",
        }

        self.assertTrue(
            calls.isdisjoint(
                forbidden_calls
            )
        )

        forbidden_import_fragments = (
            "durable_store",
            "technology_radar",
            "radar_evaluation_pipeline",
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
