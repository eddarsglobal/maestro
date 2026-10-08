from __future__ import annotations

import ast
import unittest

from pathlib import Path

from maestro.enums import (
    CouncilId,
    SideEffectLevel,
    ToolExecutionStatus,
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
    ResearchExecutionResult,
    ResearchProviderDescriptor,
    ResearchProviderRegistry,
    ResearchProviderStatus,
    ResearchRequest,
    ResearchRuntimeConfigurationError,
    ResearchSource,
    SourceProvenance,
)

from maestro.research.runtime_contracts import (
    ResearchAttemptStatus,
)

from maestro.tools.registry import (
    ToolRegistry,
    ToolSpec,
)


class RadarResearchExactExecutionTests(
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
        quality: float = 0.9,
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
            local=True,
            status=status,
            quality_score=quality,
            cost_score=0.1,
            latency_score=0.1,
        )

    def register_tool(
        self,
        tools: ToolRegistry,
        provider_id: str,
        *,
        provider_binding=None,
        human=False,
        handler=None,
    ):
        binding = (
            provider_id
            if provider_binding is None
            else provider_binding
        )

        if handler is None:
            handler = (
                lambda **kwargs: kwargs
            )

        tools.register(
            ToolSpec(
                name=f"{provider_id}.search",
                description="ADEL0.22A exact tool",
                capabilities=(
                    "research.search",
                    f"research.provider:{binding}",
                ),
                allowed_councils=frozenset(
                    {CouncilId.RX}
                ),
                side_effect_level=(
                    SideEffectLevel.A0_READ_ONLY
                ),
                requires_policy_approval=False,
                requires_human_approval=human,
            ),
            handler,
        )

    def runtime(
        self,
        *,
        include_beta=False,
        alpha_handler=None,
        beta_handler=None,
    ):
        providers = ResearchProviderRegistry()

        providers.register(
            self.provider(
                "alpha",
                quality=0.9,
            )
        )

        if include_beta:
            providers.register(
                self.provider(
                    "beta",
                    quality=0.1,
                )
            )

        tools = ToolRegistry()

        self.register_tool(
            tools,
            "alpha",
            handler=alpha_handler,
        )

        if include_beta:
            self.register_tool(
                tools,
                "beta",
                handler=beta_handler,
            )

        return (
            GovernedResearchRuntime(
                providers,
                tools,
            ),
            providers,
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
                f"adel022a-{suffix}"
            ),
            label=f"ADEL0.22A {suffix}",
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

    def handoff(
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

        return (
            GovernedRadarResearchToolValidator
            .validate(
                routing,
                runtime=runtime,
            )
        )

    def test_empty_handoff_executes_nothing(
        self,
    ):
        runtime, _, tools = self.runtime()

        result = (
            GovernedRadarResearchExactExecutor
            .execute(
                self.handoff(
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

        self.assertEqual(
            tools.history,
            [],
        )

    def test_exact_execution_returns_result(
        self,
    ):
        runtime, _, _ = self.runtime()

        result = (
            GovernedRadarResearchExactExecutor
            .execute(
                self.handoff(runtime),
                runtime=runtime,
            )
        )

        self.assertEqual(
            result.size,
            1,
        )

        self.assertIsInstance(
            result.entries[0].result,
            ResearchExecutionResult,
        )

    def test_result_matches_validated_provider_and_tool(
        self,
    ):
        runtime, _, _ = self.runtime()

        handoff = self.handoff(runtime)

        row = (
            GovernedRadarResearchExactExecutor
            .execute(
                handoff,
                runtime=runtime,
            )
            .entries[0]
        )

        before = handoff.entries[0]

        self.assertEqual(
            row.result.provider_id,
            before.provider_id,
        )

        self.assertEqual(
            row.result.tool_name,
            before.tool_name,
        )

    def test_request_and_decision_identity_preserved(
        self,
    ):
        runtime, _, _ = self.runtime()

        handoff = self.handoff(runtime)

        row = (
            GovernedRadarResearchExactExecutor
            .execute(
                handoff,
                runtime=runtime,
            )
            .entries[0]
        )

        self.assertIs(
            row.request,
            handoff.entries[0].request,
        )

        self.assertIs(
            row.decision,
            handoff.entries[0].decision,
        )

    def test_single_success_attempt_is_exact(
        self,
    ):
        runtime, _, _ = self.runtime()

        row = (
            GovernedRadarResearchExactExecutor
            .execute(
                self.handoff(runtime),
                runtime=runtime,
            )
            .entries[0]
        )

        self.assertEqual(
            len(row.result.attempts),
            1,
        )

        attempt = row.result.attempts[0]

        self.assertEqual(
            attempt.attempt_number,
            1,
        )

        self.assertEqual(
            attempt.provider_id,
            row.provider_id,
        )

        self.assertEqual(
            attempt.tool_name,
            row.tool_name,
        )

        self.assertIs(
            attempt.status,
            ResearchAttemptStatus.SUCCEEDED,
        )

    def test_better_provider_added_after_handoff_does_not_re_route(
        self,
    ):
        calls = []

        def alpha_handler(
            **kwargs,
        ):
            calls.append("alpha")
            return kwargs

        runtime, providers, _ = self.runtime(
            alpha_handler=alpha_handler
        )

        handoff = self.handoff(runtime)

        providers.register(
            self.provider(
                "beta",
                quality=1.0,
            )
        )

        result = (
            GovernedRadarResearchExactExecutor
            .execute(
                handoff,
                runtime=runtime,
            )
        )

        self.assertEqual(
            result.provider_ids,
            ("alpha",),
        )

        self.assertEqual(
            calls,
            ["alpha"],
        )

    def test_provider_becoming_unavailable_fails_closed(
        self,
    ):
        calls = []

        def handler(
            **kwargs,
        ):
            calls.append(kwargs)
            return kwargs

        runtime, providers, tools = self.runtime(
            alpha_handler=handler
        )

        handoff = self.handoff(runtime)

        providers.set_status(
            "alpha",
            ResearchProviderStatus.UNAVAILABLE,
        )

        with self.assertRaises(
            ResearchRuntimeConfigurationError
        ):
            (
                GovernedRadarResearchExactExecutor
                .execute(
                    handoff,
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

    def test_exact_tool_binding_change_fails_closed(
        self,
    ):
        runtime, _, _ = self.runtime()
        handoff = self.handoff(runtime)

        replacement = ToolRegistry()

        self.register_tool(
            replacement,
            "alpha",
            provider_binding="beta",
        )

        runtime.tools = replacement

        with self.assertRaisesRegex(
            ResearchRuntimeConfigurationError,
            "binding mismatch",
        ):
            (
                GovernedRadarResearchExactExecutor
                .execute(
                    handoff,
                    runtime=runtime,
                )
            )

        self.assertEqual(
            replacement.history,
            [],
        )

    def test_exact_execution_revalidates_tool_policy(
        self,
    ):
        runtime, _, _ = self.runtime()
        handoff = self.handoff(runtime)

        replacement = ToolRegistry()

        self.register_tool(
            replacement,
            "alpha",
            human=True,
        )

        runtime.tools = replacement

        with self.assertRaises(
            ResearchRuntimeConfigurationError
        ):
            (
                GovernedRadarResearchExactExecutor
                .execute(
                    handoff,
                    runtime=runtime,
                )
            )

        self.assertEqual(
            replacement.history,
            [],
        )

    def test_handler_failure_does_not_fallback(
        self,
    ):
        beta_calls = []

        def fail_alpha(
            **kwargs,
        ):
            raise ValueError(
                "alpha failure"
            )

        def beta_handler(
            **kwargs,
        ):
            beta_calls.append(kwargs)
            return kwargs

        runtime, _, tools = self.runtime(
            include_beta=True,
            alpha_handler=fail_alpha,
            beta_handler=beta_handler,
        )

        handoff = self.handoff(runtime)

        with self.assertRaisesRegex(
            ValueError,
            "alpha failure",
        ):
            (
                GovernedRadarResearchExactExecutor
                .execute(
                    handoff,
                    runtime=runtime,
                )
            )

        self.assertEqual(
            beta_calls,
            [],
        )

        self.assertEqual(
            len(tools.history),
            1,
        )

        self.assertIs(
            tools.history[0].status,
            ToolExecutionStatus.FAILED,
        )

        self.assertEqual(
            tools.history[0].tool_ref,
            tools.tool_reference(
                "alpha.search"
            ),
        )

    def test_execution_crosses_tool_registry_as_rx(
        self,
    ):
        runtime, _, tools = self.runtime()

        (
            GovernedRadarResearchExactExecutor
            .execute(
                self.handoff(runtime),
                runtime=runtime,
            )
        )

        self.assertEqual(
            len(tools.history),
            1,
        )

        invocation = tools.history[0]

        self.assertIs(
            invocation.actor,
            CouncilId.RX,
        )

        self.assertIs(
            invocation.status,
            ToolExecutionStatus.EXECUTED,
        )

        self.assertEqual(
            invocation.tool_ref,
            tools.tool_reference(
                "alpha.search"
            ),
        )

    def test_execution_thaws_nested_arguments(
        self,
    ):
        runtime, _, _ = self.runtime()

        request = ResearchRequest(
            task_id=self.TASK_A,
            capability=ResearchCapability.SEARCH,
            arguments={
                "filters": {
                    "domains": [
                        "example.com",
                    ]
                }
            },
        )

        decision = runtime.route(
            request
        )

        result = runtime.execute_exact(
            request,
            decision,
        )

        self.assertEqual(
            result.output[
                "filters"
            ][
                "domains"
            ],
            ["example.com"],
        )

    def test_order_and_payload_are_preserved(
        self,
    ):
        runtime, _, _ = self.runtime()
        handoff = self.handoff(
            runtime,
            3,
        )

        result = (
            GovernedRadarResearchExactExecutor
            .execute(
                handoff,
                runtime=runtime,
            )
        )

        self.assertEqual(
            result.evidence_ids,
            handoff.evidence_ids,
        )

        self.assertEqual(
            result.task_ids,
            handoff.task_ids,
        )

        self.assertEqual(
            result.provider_ids,
            handoff.provider_ids,
        )

        self.assertEqual(
            result.tool_names,
            handoff.tool_names,
        )

        for before, after in zip(
            handoff.entries,
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

    def test_execution_flags_are_exact(
        self,
    ):
        runtime, _, _ = self.runtime()

        row = (
            GovernedRadarResearchExactExecutor
            .execute(
                self.handoff(runtime),
                runtime=runtime,
            )
            .entries[0]
        )

        self.assertTrue(
            row.tool_validated
        )
        self.assertTrue(
            row.execution_handoff_created
        )
        self.assertTrue(
            row.tool_execution_requested
        )
        self.assertTrue(
            row.tool_invoked
        )
        self.assertTrue(
            row.action_firewall_crossed
        )
        self.assertTrue(
            row.execution_completed
        )
        self.assertTrue(
            row.execution_result_created
        )
        self.assertTrue(
            row.execution_asserted
        )

    def test_network_status_is_unknown_and_no_evidence_reintegration(
        self,
    ):
        runtime, _, _ = self.runtime()

        row = (
            GovernedRadarResearchExactExecutor
            .execute(
                self.handoff(runtime),
                runtime=runtime,
            )
            .entries[0]
        )

        self.assertEqual(
            row.network_access_status,
            "UNKNOWN",
        )

        self.assertFalse(
            row.evidence_created
        )

        self.assertFalse(
            row.evidence_reintegrated
        )

    def test_execution_asserts_no_truth_or_governance_authority(
        self,
    ):
        runtime, _, _ = self.runtime()

        row = (
            GovernedRadarResearchExactExecutor
            .execute(
                self.handoff(runtime),
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
        self.assertFalse(
            row.authorization_asserted
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
            row.mission_transition_requested
        )
        self.assertFalse(
            row.persistence_requested
        )

    def test_wrong_inputs_fail_closed(
        self,
    ):
        runtime, _, _ = self.runtime()

        with self.assertRaises(
            TypeError
        ):
            (
                GovernedRadarResearchExactExecutor
                .execute(
                    object(),
                    runtime=runtime,
                )
            )

        with self.assertRaises(
            TypeError
        ):
            (
                GovernedRadarResearchExactExecutor
                .execute(
                    self.handoff(runtime),
                    runtime=object(),
                )
            )

        with self.assertRaises(
            TypeError
        ):
            runtime.execute_exact(
                object(),
                object(),
            )

        request = ResearchRequest(
            task_id=self.TASK_A,
            capability=ResearchCapability.SEARCH,
            arguments={
                "query": "maestro",
            },
        )

        with self.assertRaises(
            TypeError
        ):
            runtime.execute_exact(
                request,
                object(),
            )

    def test_ast_boundary_no_route_no_evidence_bridge(
        self,
    ):
        radar_path = Path(
            "src/maestro/research/"
            "radar_research_exact_execution.py"
        )

        radar_tree = ast.parse(
            radar_path.read_text(
                encoding="utf-8"
            )
        )

        radar_calls = set()

        for node in ast.walk(
            radar_tree
        ):
            if isinstance(
                node,
                ast.Call,
            ):
                try:
                    radar_calls.add(
                        ast.unparse(
                            node.func
                        )
                    )
                except Exception:
                    pass

        self.assertIn(
            "runtime.execute_exact",
            radar_calls,
        )

        radar_forbidden = {
            "runtime.execute",
            "runtime.route",
            "runtime.tools.invoke",
            "ResearchEvidenceBridge.to_evidence",
        }

        self.assertTrue(
            radar_calls.isdisjoint(
                radar_forbidden
            )
        )

        runtime_path = Path(
            "src/maestro/research/runtime.py"
        )

        runtime_tree = ast.parse(
            runtime_path.read_text(
                encoding="utf-8"
            )
        )

        target = None

        for node in ast.walk(
            runtime_tree
        ):
            if (
                isinstance(
                    node,
                    ast.FunctionDef,
                )
                and node.name
                == "execute_exact"
            ):
                target = node
                break

        self.assertIsNotNone(
            target
        )

        calls = set()

        for node in ast.walk(
            target
        ):
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

        self.assertIn(
            "self.providers.eligible",
            calls,
        )
        self.assertIn(
            "self._validate_tool",
            calls,
        )
        self.assertIn(
            "self.tools.invoke",
            calls,
        )

        self.assertNotIn(
            "self.route",
            calls,
        )
        self.assertNotIn(
            "self._with_forbidden_provider_ids",
            calls,
        )


if __name__ == "__main__":
    unittest.main()
