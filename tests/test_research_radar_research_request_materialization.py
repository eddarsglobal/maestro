from __future__ import annotations

import ast
import unittest

from pathlib import Path
from types import MappingProxyType

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
    GovernedRadarResearchTaskBinder,
    GovernedRadarReviewHandoff,
    GovernedRadarReviewPacket,
    GovernedRadarReviewResponse,
    RadarDecisionPolicy,
    RadarPortfolioEntry,
    RadarResearchDraftAdmissionStatus,
    RadarResearchRequestMaterializationEntry,
    RadarReviewResponseValue,
    RadarReviewTarget,
    ResearchCapability,
    ResearchClaim,
    ResearchEvidenceBridge,
    ResearchRequest,
    ResearchSource,
    SourceProvenance,
)


class RadarResearchRequestMaterializationTests(
    unittest.TestCase
):
    NOW = "2026-01-01T00:00:00+00:00"

    TASK_A = "TASK-A1B2C3D4E5F6"
    TASK_B = "TASK-B1C2D3E4F5A6"
    TASK_C = "TASK-C1D2E3F4A5B6"

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
                f"adel019-{suffix}"
            ),
            label=f"ADEL0.19 {suffix}",
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

    def drafts(
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

        return (
            GovernedRadarResearchRequestDraftBuilder
            .build(
                candidates
            )
        )

    def binding(
        self,
        count=1,
    ):
        admission = (
            GovernedRadarResearchDraftAdmissionGate
            .evaluate(
                self.drafts(count)
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

        return (
            GovernedRadarResearchTaskBinder
            .bind(
                admission,
                task_ids=task_ids,
            )
        )

    def test_empty_binding_materializes_nothing(
        self,
    ):
        result = (
            GovernedRadarResearchRequestMaterializer
            .materialize(
                self.binding(0)
            )
        )

        self.assertEqual(
            result.size,
            0,
        )

    def test_bound_entry_materializes_request(
        self,
    ):
        result = (
            GovernedRadarResearchRequestMaterializer
            .materialize(
                self.binding()
            )
        )

        self.assertEqual(
            result.size,
            1,
        )
        self.assertTrue(
            result.entries[0]
            .research_request_created
        )

    def test_materialized_object_is_research_request(
        self,
    ):
        row = (
            GovernedRadarResearchRequestMaterializer
            .materialize(
                self.binding()
            )
            .entries[0]
        )

        self.assertIsInstance(
            row.request,
            ResearchRequest,
        )

    def test_task_id_is_preserved(
        self,
    ):
        binding = self.binding()

        result = (
            GovernedRadarResearchRequestMaterializer
            .materialize(
                binding
            )
        )

        self.assertEqual(
            result.entries[0]
            .request.task_id,
            binding.entries[0].task_id,
        )

    def test_request_contract_payload_is_preserved(
        self,
    ):
        binding = self.binding()

        request = (
            GovernedRadarResearchRequestMaterializer
            .materialize(
                binding
            )
            .entries[0]
            .request
        )

        bound = binding.entries[0]

        self.assertEqual(
            request.capability,
            bound.capability,
        )
        self.assertEqual(
            request.arguments,
            bound.arguments,
        )
        self.assertEqual(
            request.preferred_local,
            bound.preferred_local,
        )
        self.assertEqual(
            request.forbidden_provider_ids,
            frozenset(
                bound.forbidden_provider_ids
            ),
        )

    def test_request_arguments_are_immutable(
        self,
    ):
        request = (
            GovernedRadarResearchRequestMaterializer
            .materialize(
                self.binding()
            )
            .entries[0]
            .request
        )

        self.assertIsInstance(
            request.arguments,
            MappingProxyType,
        )

        with self.assertRaises(
            TypeError
        ):
            request.arguments[
                "query"
            ] = "mutated"

    def test_order_is_preserved(
        self,
    ):
        binding = self.binding(3)

        result = (
            GovernedRadarResearchRequestMaterializer
            .materialize(
                binding
            )
        )

        self.assertEqual(
            result.evidence_ids,
            binding.evidence_ids,
        )

        self.assertEqual(
            result.task_ids,
            binding.task_ids,
        )

    def test_evidence_payload_is_preserved(
        self,
    ):
        binding = self.binding()

        result = (
            GovernedRadarResearchRequestMaterializer
            .materialize(
                binding
            )
        )

        before = binding.entries[0]
        after = result.entries[0]

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

    def test_admission_provenance_is_preserved(
        self,
    ):
        binding = self.binding()

        row = (
            GovernedRadarResearchRequestMaterializer
            .materialize(
                binding
            )
            .entries[0]
        )

        self.assertEqual(
            row.admission_status,
            binding.entries[0]
            .admission_status,
        )
        self.assertEqual(
            row.admission_reason,
            binding.entries[0]
            .admission_reason,
        )

    def test_unverified_boundary_is_preserved(
        self,
    ):
        row = (
            GovernedRadarResearchRequestMaterializer
            .materialize(
                self.binding()
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

    def test_materialization_flags_are_exact(
        self,
    ):
        row = (
            GovernedRadarResearchRequestMaterializer
            .materialize(
                self.binding()
            )
            .entries[0]
        )

        self.assertTrue(
            row.task_id_bound
        )
        self.assertTrue(
            row.research_request_created
        )

    def test_materialization_does_not_select_provider_or_route(
        self,
    ):
        row = (
            GovernedRadarResearchRequestMaterializer
            .materialize(
                self.binding()
            )
            .entries[0]
        )

        self.assertFalse(
            row.provider_selected
        )
        self.assertFalse(
            row.routing_decision_created
        )
        self.assertFalse(
            row.tool_validated
        )

    def test_materialization_has_no_runtime_side_effects(
        self,
    ):
        row = (
            GovernedRadarResearchRequestMaterializer
            .materialize(
                self.binding()
            )
            .entries[0]
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

    def test_materialization_asserts_no_authority(
        self,
    ):
        row = (
            GovernedRadarResearchRequestMaterializer
            .materialize(
                self.binding()
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

    def test_materializer_is_deterministic(
        self,
    ):
        binding = self.binding(2)

        first = (
            GovernedRadarResearchRequestMaterializer
            .materialize(
                binding
            )
        )

        second = (
            GovernedRadarResearchRequestMaterializer
            .materialize(
                binding
            )
        )

        self.assertEqual(
            first,
            second,
        )

    def test_wrong_input_fails_closed(
        self,
    ):
        with self.assertRaises(
            TypeError
        ):
            (
                GovernedRadarResearchRequestMaterializer
                .materialize(
                    object()
                )
            )

    def test_invalid_materialization_entry_fails_closed(
        self,
    ):
        binding = self.binding()
        bound = binding.entries[0]

        invalid_request = ResearchRequest(
            task_id=bound.task_id,
            capability=ResearchCapability.FETCH,
            arguments={
                "url": (
                    "https://example.com"
                )
            },
        )

        with self.assertRaises(
            ValueError
        ):
            RadarResearchRequestMaterializationEntry(
                rank=bound.rank,
                evidence_id=bound.evidence_id,
                source_ref=bound.source_ref,
                claim=bound.claim,
                priority_score=(
                    bound.priority_score
                ),
                factors=bound.factors,
                rationale=bound.rationale,
                target=bound.target,
                admission_status=(
                    bound.admission_status
                ),
                admission_reason=(
                    bound.admission_reason
                ),
                request=invalid_request,
            )

    def test_module_imports_request_contract_only_not_active_runtime(
        self,
    ):
        path = Path(
            "src/maestro/research/"
            "radar_research_request_materialization.py"
        )

        source = path.read_text(
            encoding="utf-8"
        )

        tree = ast.parse(
            source
        )

        imports = []
        runtime_contract_names = set()

        for node in ast.walk(tree):
            if isinstance(
                node,
                ast.Import,
            ):
                for alias in node.names:
                    imports.append(
                        alias.name
                    )

            elif isinstance(
                node,
                ast.ImportFrom,
            ):
                full_name = (
                    "." * node.level
                    + (
                        node.module
                        or ""
                    )
                )

                imports.append(
                    full_name
                )

                if (
                    node.level == 1
                    and node.module
                    == "runtime_contracts"
                ):
                    runtime_contract_names.update(
                        alias.name
                        for alias
                        in node.names
                    )

        forbidden = (
            "socket",
            "http",
            "urllib",
            "requests",
            "subprocess",
            ".runtime",
            ".provider_registry",
            ".transport",
            ".web_fetch",
            ".durable_store",
            "maestro.learning",
            "maestro.adaptive",
            "maestro.strategic_adaptation",
            "maestro.outcome_governed_adaptation",
            "maestro.governed_activation",
            "maestro.governance",
            "maestro.meta_cognition",
            "maestro.fabric",
            "maestro.tools",
            "maestro.autonomous",
            "maestro.sovereign",
            "maestro.state_machine",
            "maestro.runtime",
        )

        violations = sorted(
            name
            for name in imports
            if any(
                name == prefix
                or name.startswith(
                    prefix + "."
                )
                for prefix in forbidden
            )
        )

        self.assertEqual(
            violations,
            [],
        )

        self.assertEqual(
            runtime_contract_names,
            {"ResearchRequest"},
        )

        self.assertNotIn(
            ".route(",
            source,
        )
        self.assertNotIn(
            ".execute(",
            source,
        )
        self.assertNotIn(
            "tools.invoke",
            source,
        )


if __name__ == "__main__":
    unittest.main()
