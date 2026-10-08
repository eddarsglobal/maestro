from __future__ import annotations

import ast
import hashlib
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
    GovernedRadarPortfolio,
    GovernedRadarResearchDraftAdmissionGate,
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
    RadarResearchProviderReturnAdmissionError,
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

from maestro.research.web_fetch import (
    GovernedWebFetchResult,
)

from maestro.tools.registry import (
    ToolRegistry,
    ToolSpec,
)


class RadarResearchProviderReturnAdmissionTests(
    unittest.TestCase
):
    NOW = "2026-10-08T06:00:00+00:00"

    TASK_A = "TASK-A1B2C3D4E5F6"
    TASK_B = "TASK-B1C2D3E4F5A6"
    TASK_C = "TASK-C1D2E3F4A5B6"

    def provider(
        self,
        provider_id="alpha",
    ):
        return ResearchProviderDescriptor(
            provider_id=provider_id,
            capabilities=frozenset(
                {
                    ResearchCapability.SEARCH,
                }
            ),
            tool_names={
                ResearchCapability.SEARCH: (
                    f"{provider_id}.search"
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
        provider_id="alpha",
        tool_name="alpha.search",
        claim_statement=(
            "External source reports a "
            "research observation."
        ),
        uri="https://example.com/returned",
        artifact_kind="DOCUMENT",
        media_type="text/plain",
    ):
        body = (
            claim_statement.encode(
                "utf-8"
            )
        )

        source = ResearchSource(
            uri,
            label="ADEL0.22B external source",
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
            provider_id=provider_id,
            tool_name=tool_name,
            source=source,
            provenance=provenance,
            claim_statement=claim_statement,
            artifact_kind=artifact_kind,
            media_type=media_type,
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
                description="ADEL0.22B search",
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

    def evidence(
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
                f"adel022b-{suffix}"
            ),
            label=f"ADEL0.22B {suffix}",
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
            known_claims=["legacy baseline"],
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
            risk_signals=["network"],
            mitigations=["network"],
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
                        evidence=self.evidence(
                            str(index)
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

    def execution(
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

        return (
            GovernedRadarResearchExactExecutor
            .execute(
                handoff,
                runtime=runtime,
            )
        )

    def test_empty_execution_admits_nothing(
        self,
    ):
        runtime = self.runtime()

        result = (
            GovernedRadarResearchProviderReturnAdmission
            .admit(
                self.execution(
                    runtime,
                    0,
                )
            )
        )

        self.assertEqual(
            result.size,
            0,
        )

    def test_canonical_packet_is_admitted(
        self,
    ):
        runtime = self.runtime()

        result = (
            GovernedRadarResearchProviderReturnAdmission
            .admit(
                self.execution(runtime)
            )
        )

        self.assertEqual(
            result.size,
            1,
        )

        self.assertTrue(
            result.entries[0]
            .provider_return_admitted
        )

    def test_arbitrary_mapping_is_rejected(
        self,
    ):
        runtime = self.runtime(
            handler=lambda **kwargs: {
                "query": "maestro",
                "results": ["one"],
            }
        )

        execution = self.execution(
            runtime
        )

        with self.assertRaises(
            RadarResearchProviderReturnAdmissionError
        ):
            (
                GovernedRadarResearchProviderReturnAdmission
                .admit(execution)
            )

    def test_string_output_is_rejected(
        self,
    ):
        runtime = self.runtime(
            handler=lambda **kwargs: (
                "external result"
            )
        )

        execution = self.execution(
            runtime
        )

        with self.assertRaises(
            RadarResearchProviderReturnAdmissionError
        ):
            (
                GovernedRadarResearchProviderReturnAdmission
                .admit(execution)
            )

    def test_raw_governed_fetch_result_is_rejected(
        self,
    ):
        body = b"FETCH BODY"

        output = GovernedWebFetchResult(
            final_url=(
                "https://example.com/final"
            ),
            method="GET",
            status=200,
            content_type="text/plain",
            body=body,
            body_sha256=(
                hashlib.sha256(
                    body
                ).hexdigest()
            ),
            redirects=(),
        )

        runtime = self.runtime(
            handler=lambda **kwargs: output
        )

        execution = self.execution(
            runtime
        )

        with self.assertRaises(
            RadarResearchProviderReturnAdmissionError
        ):
            (
                GovernedRadarResearchProviderReturnAdmission
                .admit(execution)
            )

    def test_provider_identity_mismatch_is_rejected(
        self,
    ):
        runtime = self.runtime(
            handler=lambda **kwargs: (
                self.packet(
                    provider_id="beta"
                )
            )
        )

        execution = self.execution(
            runtime
        )

        with self.assertRaisesRegex(
            RadarResearchProviderReturnAdmissionError,
            "provider_id mismatch",
        ):
            (
                GovernedRadarResearchProviderReturnAdmission
                .admit(execution)
            )

    def test_tool_identity_mismatch_is_rejected(
        self,
    ):
        runtime = self.runtime(
            handler=lambda **kwargs: (
                self.packet(
                    tool_name="beta.search"
                )
            )
        )

        execution = self.execution(
            runtime
        )

        with self.assertRaisesRegex(
            RadarResearchProviderReturnAdmissionError,
            "tool_name mismatch",
        ):
            (
                GovernedRadarResearchProviderReturnAdmission
                .admit(execution)
            )

    def test_source_provenance_mismatch_is_rejected(
        self,
    ):
        source = ResearchSource(
            "https://example.com/one"
        )

        other = ResearchSource(
            "https://example.com/two"
        )

        provenance = SourceProvenance(
            source_id=other.source_id,
            retrieved_at=self.NOW,
            digest=ContentDigest.from_bytes(
                b"content"
            ),
        )

        with self.assertRaises(
            RadarResearchProviderReturnAdmissionError
        ):
            RadarResearchProviderReturnPacket(
                provider_id="alpha",
                tool_name="alpha.search",
                source=source,
                provenance=provenance,
                claim_statement="claim",
                artifact_kind="DOCUMENT",
                media_type="text/plain",
            )

    def test_packet_rejects_empty_semantic_fields(
        self,
    ):
        cases = (
            {
                "claim_statement": "",
            },
            {
                "artifact_kind": " ",
            },
            {
                "media_type": "",
            },
            {
                "provider_id": "",
            },
            {
                "tool_name": " ",
            },
        )

        for override in cases:
            with self.subTest(
                override=override
            ):
                kwargs = {
                    "provider_id": "alpha",
                    "tool_name": "alpha.search",
                    "claim_statement": "claim",
                    "artifact_kind": "DOCUMENT",
                    "media_type": "text/plain",
                }

                kwargs.update(
                    override
                )

                source = ResearchSource(
                    "https://example.com/x"
                )

                provenance = SourceProvenance(
                    source_id=source.source_id,
                    retrieved_at=self.NOW,
                    digest=ContentDigest.from_bytes(
                        b"x"
                    ),
                )

                with self.assertRaises(
                    RadarResearchProviderReturnAdmissionError
                ):
                    RadarResearchProviderReturnPacket(
                        source=source,
                        provenance=provenance,
                        **kwargs,
                    )

    def test_result_and_packet_identity_are_preserved(
        self,
    ):
        runtime = self.runtime()
        execution = self.execution(runtime)

        admitted = (
            GovernedRadarResearchProviderReturnAdmission
            .admit(execution)
        )

        self.assertIs(
            admitted.entries[0].result,
            execution.entries[0].result,
        )

        self.assertIs(
            admitted.entries[0].return_packet,
            execution.entries[0].result.output,
        )

    def test_order_and_lineage_are_preserved(
        self,
    ):
        runtime = self.runtime()
        execution = self.execution(
            runtime,
            3,
        )

        result = (
            GovernedRadarResearchProviderReturnAdmission
            .admit(execution)
        )

        self.assertEqual(
            result.evidence_ids,
            execution.evidence_ids,
        )

        self.assertEqual(
            result.task_ids,
            execution.task_ids,
        )

        self.assertEqual(
            result.provider_ids,
            execution.provider_ids,
        )

        self.assertEqual(
            result.tool_names,
            execution.tool_names,
        )

    def test_admission_flags_are_exact(
        self,
    ):
        runtime = self.runtime()

        row = (
            GovernedRadarResearchProviderReturnAdmission
            .admit(
                self.execution(runtime)
            )
            .entries[0]
        )

        self.assertTrue(
            row.execution_completed
        )
        self.assertTrue(
            row.execution_result_created
        )
        self.assertTrue(
            row.provider_return_received
        )
        self.assertTrue(
            row.provider_return_admitted
        )

    def test_unverified_boundary_is_preserved(
        self,
    ):
        runtime = self.runtime()

        row = (
            GovernedRadarResearchProviderReturnAdmission
            .admit(
                self.execution(runtime)
            )
            .entries[0]
        )

        self.assertEqual(
            row.verification_status,
            "UNVERIFIED_EXTERNAL",
        )

        self.assertFalse(
            row.system_truth_asserted
        )

    def test_network_status_remains_unknown(
        self,
    ):
        runtime = self.runtime()

        row = (
            GovernedRadarResearchProviderReturnAdmission
            .admit(
                self.execution(runtime)
            )
            .entries[0]
        )

        self.assertEqual(
            row.network_access_status,
            "UNKNOWN",
        )

    def test_no_claim_artifact_or_evidence_is_created(
        self,
    ):
        runtime = self.runtime()

        row = (
            GovernedRadarResearchProviderReturnAdmission
            .admit(
                self.execution(runtime)
            )
            .entries[0]
        )

        self.assertFalse(
            row.research_claim_created
        )
        self.assertFalse(
            row.external_artifact_created
        )
        self.assertFalse(
            row.evidence_created
        )
        self.assertFalse(
            row.evidence_reintegrated
        )

    def test_no_governance_or_learning_authority(
        self,
    ):
        runtime = self.runtime()

        row = (
            GovernedRadarResearchProviderReturnAdmission
            .admit(
                self.execution(runtime)
            )
            .entries[0]
        )

        self.assertFalse(
            row.persistence_requested
        )
        self.assertFalse(
            row.mission_transition_requested
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

    def test_admission_is_deterministic(
        self,
    ):
        runtime = self.runtime()
        execution = self.execution(runtime)

        first = (
            GovernedRadarResearchProviderReturnAdmission
            .admit(execution)
        )

        second = (
            GovernedRadarResearchProviderReturnAdmission
            .admit(execution)
        )

        self.assertEqual(
            first,
            second,
        )

    def test_wrong_input_and_static_boundary_fail_closed(
        self,
    ):
        with self.assertRaises(
            TypeError
        ):
            (
                GovernedRadarResearchProviderReturnAdmission
                .admit(
                    object()
                )
            )

        path = Path(
            "src/maestro/research/"
            "radar_research_return_admission.py"
        )

        tree = ast.parse(
            path.read_text(
                encoding="utf-8"
            )
        )

        calls = set()

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

        forbidden = {
            "ResearchEvidenceBridge.to_evidence",
            "runtime.execute",
            "runtime.execute_exact",
            "runtime.route",
            "runtime.tools.invoke",
            "ResearchEvidenceStore",
        }

        self.assertTrue(
            calls.isdisjoint(
                forbidden
            )
        )


if __name__ == "__main__":
    unittest.main()
