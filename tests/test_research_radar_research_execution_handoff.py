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
    GovernedRadarPortfolio,
    GovernedRadarResearchDraftAdmissionGate,
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
    RadarReviewResponseValue,
    RadarReviewTarget,
    ResearchCapability,
    ResearchClaim,
    ResearchEvidenceBridge,
    ResearchProviderDescriptor,
    ResearchProviderRegistry,
    ResearchProviderStatus,
    ResearchRuntimeConfigurationError,
    ResearchSource,
    SourceProvenance,
)

from maestro.tools.registry import (
    ToolRegistry,
    ToolSpec,
)


class RadarResearchExecutionHandoffTests(
    unittest.TestCase
):
    NOW = "2026-01-01T00:00:00+00:00"

    TASK_A = "TASK-A1B2C3D4E5F6"
    TASK_B = "TASK-B1C2D3E4F5A6"
    TASK_C = "TASK-C1D2E3F4A5B6"

    def provider(
        self,
        provider_id: str,
        *,
        local: bool = True,
        status: ResearchProviderStatus = (
            ResearchProviderStatus.AVAILABLE
        ),
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
            local=local,
            status=status,
            quality_score=0.9,
            cost_score=0.1,
            latency_score=0.1,
        )

    def register_tool(
        self,
        tools: ToolRegistry,
        provider_id: str,
        *,
        councils=frozenset(
            {CouncilId.RX}
        ),
        level=SideEffectLevel.A0_READ_ONLY,
        capabilities=None,
        provider_binding=None,
        policy=False,
        human=False,
        handler=None,
    ):
        if capabilities is None:
            binding = (
                provider_id
                if provider_binding is None
                else provider_binding
            )

            capabilities = (
                "research.search",
                f"research.provider:{binding}",
            )

        if handler is None:
            handler = (
                lambda **kwargs: kwargs
            )

        tools.register(
            ToolSpec(
                name=f"{provider_id}.search",
                description="ADEL0.21 fake search",
                capabilities=capabilities,
                allowed_councils=councils,
                side_effect_level=level,
                requires_policy_approval=policy,
                requires_human_approval=human,
            ),
            handler,
        )

    def runtime(
        self,
        *,
        register_tool=True,
        councils=frozenset(
            {CouncilId.RX}
        ),
        level=SideEffectLevel.A0_READ_ONLY,
        capabilities=None,
        provider_binding=None,
        policy=False,
        human=False,
        handler=None,
    ):
        providers = ResearchProviderRegistry()

        providers.register(
            self.provider("alpha")
        )

        tools = ToolRegistry()

        if register_tool:
            self.register_tool(
                tools,
                "alpha",
                councils=councils,
                level=level,
                capabilities=capabilities,
                provider_binding=(
                    provider_binding
                ),
                policy=policy,
                human=human,
                handler=handler,
            )

        return (
            GovernedResearchRuntime(
                providers,
                tools,
            ),
            tools,
        )

    def evidence(
        self,
        suffix: str,
    ):
        statement = (
            "GPU reasoning improves "
            "MAESTRO research"
        )

        source = ResearchSource(
            (
                "https://example.com/"
                f"adel021-{suffix}"
            ),
            label=f"ADEL0.21 {suffix}",
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

    def routing(
        self,
        runtime,
        count=1,
    ):
        return (
            GovernedRadarResearchRouter
            .route(
                self.materialization(
                    count
                ),
                runtime=runtime,
            )
        )

    def test_empty_routing_validates_nothing(
        self,
    ):
        runtime, _ = self.runtime()

        result = (
            GovernedRadarResearchToolValidator
            .validate(
                self.routing(
                    runtime,
                    0,
                ),
                runtime=runtime,
            )
        )

        self.assertEqual(
            result.size,
            0,
        )

    def test_routed_entry_becomes_validated_handoff(
        self,
    ):
        runtime, _ = self.runtime()

        result = (
            GovernedRadarResearchToolValidator
            .validate(
                self.routing(runtime),
                runtime=runtime,
            )
        )

        self.assertEqual(
            result.size,
            1,
        )

        self.assertTrue(
            result.entries[0]
            .tool_validated
        )

        self.assertTrue(
            result.entries[0]
            .execution_handoff_created
        )

    def test_request_identity_is_preserved(
        self,
    ):
        runtime, _ = self.runtime()
        routing = self.routing(runtime)

        result = (
            GovernedRadarResearchToolValidator
            .validate(
                routing,
                runtime=runtime,
            )
        )

        self.assertIs(
            result.entries[0].request,
            routing.entries[0].request,
        )

    def test_routing_decision_identity_is_preserved(
        self,
    ):
        runtime, _ = self.runtime()
        routing = self.routing(runtime)

        result = (
            GovernedRadarResearchToolValidator
            .validate(
                routing,
                runtime=runtime,
            )
        )

        self.assertIs(
            result.entries[0].decision,
            routing.entries[0].decision,
        )

    def test_missing_tool_fails_closed(
        self,
    ):
        runtime, _ = self.runtime(
            register_tool=False
        )

        routing = self.routing(runtime)

        with self.assertRaises(
            ResearchRuntimeConfigurationError
        ):
            (
                GovernedRadarResearchToolValidator
                .validate(
                    routing,
                    runtime=runtime,
                )
            )

    def test_tool_must_allow_rx(
        self,
    ):
        runtime, _ = self.runtime(
            councils=frozenset(
                {CouncilId.IT}
            )
        )

        routing = self.routing(runtime)

        with self.assertRaises(
            ResearchRuntimeConfigurationError
        ):
            (
                GovernedRadarResearchToolValidator
                .validate(
                    routing,
                    runtime=runtime,
                )
            )

    def test_tool_must_be_a0_read_only(
        self,
    ):
        runtime, _ = self.runtime(
            level=(
                SideEffectLevel
                .A1_REVERSIBLE_LOCAL
            )
        )

        routing = self.routing(runtime)

        with self.assertRaises(
            ResearchRuntimeConfigurationError
        ):
            (
                GovernedRadarResearchToolValidator
                .validate(
                    routing,
                    runtime=runtime,
                )
            )

    def test_tool_must_advertise_research_capability(
        self,
    ):
        runtime, _ = self.runtime(
            capabilities=(
                "repository.read",
                "research.provider:alpha",
            )
        )

        routing = self.routing(runtime)

        with self.assertRaises(
            ResearchRuntimeConfigurationError
        ):
            (
                GovernedRadarResearchToolValidator
                .validate(
                    routing,
                    runtime=runtime,
                )
            )

    def test_provider_tool_binding_must_match(
        self,
    ):
        runtime, _ = self.runtime(
            provider_binding="beta"
        )

        routing = self.routing(runtime)

        with self.assertRaisesRegex(
            ResearchRuntimeConfigurationError,
            "binding mismatch",
        ):
            (
                GovernedRadarResearchToolValidator
                .validate(
                    routing,
                    runtime=runtime,
                )
            )

    def test_approval_requiring_tool_fails_closed(
        self,
    ):
        runtime, _ = self.runtime(
            human=True
        )

        routing = self.routing(runtime)

        with self.assertRaises(
            ResearchRuntimeConfigurationError
        ):
            (
                GovernedRadarResearchToolValidator
                .validate(
                    routing,
                    runtime=runtime,
                )
            )

    def test_validation_does_not_invoke_handler(
        self,
    ):
        calls = []

        def handler(
            **kwargs,
        ):
            calls.append(
                kwargs
            )
            return kwargs

        runtime, tools = self.runtime(
            handler=handler
        )

        routing = self.routing(runtime)

        (
            GovernedRadarResearchToolValidator
            .validate(
                routing,
                runtime=runtime,
            )
        )

        self.assertEqual(
            calls,
            [],
        )

        self.assertEqual(
            tools.history,
            [],
        )

    def test_validation_creates_no_invocation_receipt(
        self,
    ):
        runtime, tools = self.runtime()

        routing = self.routing(runtime)

        (
            GovernedRadarResearchToolValidator
            .validate(
                routing,
                runtime=runtime,
            )
        )

        self.assertIsNone(
            tools.last_invocation_receipt()
        )

    def test_order_and_payload_are_preserved(
        self,
    ):
        runtime, _ = self.runtime()
        routing = self.routing(
            runtime,
            3,
        )

        result = (
            GovernedRadarResearchToolValidator
            .validate(
                routing,
                runtime=runtime,
            )
        )

        self.assertEqual(
            result.evidence_ids,
            routing.evidence_ids,
        )

        self.assertEqual(
            result.task_ids,
            routing.task_ids,
        )

        self.assertEqual(
            result.provider_ids,
            routing.provider_ids,
        )

        for before, after in zip(
            routing.entries,
            result.entries,
        ):
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
            self.assertEqual(
                after.target,
                before.target,
            )
            self.assertEqual(
                after.admission_status,
                before.admission_status,
            )
            self.assertEqual(
                after.admission_reason,
                before.admission_reason,
            )

    def test_unverified_boundary_is_preserved(
        self,
    ):
        runtime, _ = self.runtime()

        row = (
            GovernedRadarResearchToolValidator
            .validate(
                self.routing(runtime),
                runtime=runtime,
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

    def test_validation_flags_are_exact(
        self,
    ):
        runtime, _ = self.runtime()

        row = (
            GovernedRadarResearchToolValidator
            .validate(
                self.routing(runtime),
                runtime=runtime,
            )
            .entries[0]
        )

        self.assertTrue(
            row.task_id_bound
        )
        self.assertTrue(
            row.research_request_created
        )
        self.assertTrue(
            row.provider_selected
        )
        self.assertTrue(
            row.routing_decision_created
        )
        self.assertTrue(
            row.tool_validated
        )
        self.assertTrue(
            row.execution_handoff_created
        )

    def test_validation_has_no_active_side_effects(
        self,
    ):
        runtime, _ = self.runtime()

        row = (
            GovernedRadarResearchToolValidator
            .validate(
                self.routing(runtime),
                runtime=runtime,
            )
            .entries[0]
        )

        self.assertFalse(
            row.tool_invoked
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

    def test_validation_asserts_no_authority(
        self,
    ):
        runtime, _ = self.runtime()

        row = (
            GovernedRadarResearchToolValidator
            .validate(
                self.routing(runtime),
                runtime=runtime,
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
        self.assertFalse(
            row.system_truth_asserted
        )

    def test_validation_is_deterministic_and_ast_boundary_is_exact(
        self,
    ):
        runtime, tools = self.runtime()
        routing = self.routing(runtime)

        first = (
            GovernedRadarResearchToolValidator
            .validate(
                routing,
                runtime=runtime,
            )
        )

        second = (
            GovernedRadarResearchToolValidator
            .validate(
                routing,
                runtime=runtime,
            )
        )

        self.assertEqual(
            first,
            second,
        )

        self.assertEqual(
            tools.history,
            [],
        )

        path = Path(
            "src/maestro/research/"
            "radar_research_execution_handoff.py"
        )

        tree = ast.parse(
            path.read_text(
                encoding="utf-8"
            )
        )

        called = set()

        for node in ast.walk(tree):
            if isinstance(
                node,
                ast.Call,
            ):
                try:
                    called.add(
                        ast.unparse(
                            node.func
                        )
                    )
                except Exception:
                    pass

        self.assertIn(
            "runtime._validate_tool",
            called,
        )

        forbidden = {
            "runtime.execute",
            "runtime.route",
            "runtime.tools.invoke",
            "runtime.tools.register",
            "runtime.providers.register",
            "runtime.providers.unregister",
            "runtime.providers.set_status",
        }

        self.assertTrue(
            called.isdisjoint(
                forbidden
            )
        )


if __name__ == "__main__":
    unittest.main()
