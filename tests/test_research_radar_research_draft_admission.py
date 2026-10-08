from __future__ import annotations

import ast
import copy
import unittest

from dataclasses import replace
from pathlib import Path

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
    GovernedRadarReviewHandoff,
    GovernedRadarReviewPacket,
    GovernedRadarReviewResponse,
    RadarDecisionPolicy,
    RadarPortfolioEntry,
    RadarResearchDraftAdmissionPolicy,
    RadarResearchDraftAdmissionStatus,
    RadarResearchRequestDraftSet,
    RadarReviewResponseValue,
    RadarReviewTarget,
    ResearchClaim,
    ResearchEvidenceBridge,
    ResearchSource,
    SourceProvenance,
)


class RadarResearchDraftAdmissionTests(
    unittest.TestCase
):
    NOW = "2026-01-01T00:00:00+00:00"

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
                f"adel017-{suffix}"
            ),
            label=f"ADEL0.17 {suffix}",
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
            task_id="TASK-A1B2C3D4E5F6",
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

    def with_entry(
        self,
        entry,
    ):
        return RadarResearchRequestDraftSet(
            entries=(entry,)
        )

    def test_empty_drafts_produce_empty_result(
        self,
    ):
        result = (
            GovernedRadarResearchDraftAdmissionGate
            .evaluate(
                self.drafts(0)
            )
        )

        self.assertEqual(result.size, 0)

    def test_valid_draft_is_admissible(
        self,
    ):
        result = (
            GovernedRadarResearchDraftAdmissionGate
            .evaluate(
                self.drafts()
            )
        )

        self.assertEqual(
            result.entries[0].status,
            RadarResearchDraftAdmissionStatus
            .ADMISSIBLE,
        )

    def test_default_reason_is_structural(
        self,
    ):
        result = (
            GovernedRadarResearchDraftAdmissionGate
            .evaluate(
                self.drafts()
            )
        )

        self.assertEqual(
            result.entries[0].reason,
            "STRUCTURALLY_ADMISSIBLE",
        )

    def test_query_too_long_is_rejected(
        self,
    ):
        drafts = self.drafts()

        entry = replace(
            drafts.entries[0],
            arguments={
                "query": "x" * 10,
            },
        )

        result = (
            GovernedRadarResearchDraftAdmissionGate
            .evaluate(
                self.with_entry(entry),
                policy=(
                    RadarResearchDraftAdmissionPolicy(
                        max_query_chars=5
                    )
                ),
            )
        )

        self.assertEqual(
            result.entries[0].status,
            RadarResearchDraftAdmissionStatus
            .REJECTED,
        )

        self.assertEqual(
            result.entries[0].reason,
            "QUERY_TOO_LONG",
        )

    def test_non_local_is_rejected_by_default(
        self,
    ):
        drafts = self.drafts()

        entry = replace(
            drafts.entries[0],
            preferred_local=False,
        )

        result = (
            GovernedRadarResearchDraftAdmissionGate
            .evaluate(
                self.with_entry(entry)
            )
        )

        self.assertEqual(
            result.entries[0].reason,
            "PREFERRED_LOCAL_REQUIRED",
        )

    def test_policy_can_allow_non_local(
        self,
    ):
        drafts = self.drafts()

        entry = replace(
            drafts.entries[0],
            preferred_local=False,
        )

        result = (
            GovernedRadarResearchDraftAdmissionGate
            .evaluate(
                self.with_entry(entry),
                policy=(
                    RadarResearchDraftAdmissionPolicy(
                        require_preferred_local=False
                    )
                ),
            )
        )

        self.assertEqual(
            result.entries[0].status,
            RadarResearchDraftAdmissionStatus
            .ADMISSIBLE,
        )

    def test_forbidden_provider_ids_rejected_by_default(
        self,
    ):
        drafts = self.drafts()

        entry = replace(
            drafts.entries[0],
            forbidden_provider_ids=(
                "provider-x",
            ),
        )

        result = (
            GovernedRadarResearchDraftAdmissionGate
            .evaluate(
                self.with_entry(entry)
            )
        )

        self.assertEqual(
            result.entries[0].reason,
            "FORBIDDEN_PROVIDER_IDS_PRESENT",
        )

    def test_policy_can_allow_forbidden_ids(
        self,
    ):
        drafts = self.drafts()

        entry = replace(
            drafts.entries[0],
            forbidden_provider_ids=(
                "provider-x",
            ),
        )

        result = (
            GovernedRadarResearchDraftAdmissionGate
            .evaluate(
                self.with_entry(entry),
                policy=(
                    RadarResearchDraftAdmissionPolicy(
                        allow_forbidden_provider_ids=True
                    )
                ),
            )
        )

        self.assertEqual(
            result.entries[0].status,
            RadarResearchDraftAdmissionStatus
            .ADMISSIBLE,
        )

    def test_order_is_preserved(
        self,
    ):
        drafts = self.drafts(3)

        result = (
            GovernedRadarResearchDraftAdmissionGate
            .evaluate(
                drafts
            )
        )

        self.assertEqual(
            tuple(
                entry.evidence_id
                for entry in result.entries
            ),
            drafts.evidence_ids,
        )

    def test_payload_is_preserved(
        self,
    ):
        drafts = self.drafts()

        result = (
            GovernedRadarResearchDraftAdmissionGate
            .evaluate(
                drafts
            )
        )

        before = drafts.entries[0]
        after = result.entries[0]

        self.assertEqual(after.rank, before.rank)
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
            after.arguments,
            before.arguments,
        )

    def test_unverified_boundary_preserved(
        self,
    ):
        row = (
            GovernedRadarResearchDraftAdmissionGate
            .evaluate(
                self.drafts()
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

    def test_admissible_does_not_bind_task_or_create_request(
        self,
    ):
        row = (
            GovernedRadarResearchDraftAdmissionGate
            .evaluate(
                self.drafts()
            )
            .entries[0]
        )

        self.assertFalse(row.task_id_bound)
        self.assertFalse(
            row.research_request_created
        )

    def test_admissible_does_not_select_provider_or_route(
        self,
    ):
        row = (
            GovernedRadarResearchDraftAdmissionGate
            .evaluate(
                self.drafts()
            )
            .entries[0]
        )

        self.assertFalse(
            row.provider_selected
        )
        self.assertFalse(
            row.routing_decision_created
        )

    def test_admissible_has_no_runtime_side_effects(
        self,
    ):
        row = (
            GovernedRadarResearchDraftAdmissionGate
            .evaluate(
                self.drafts()
            )
            .entries[0]
        )

        self.assertFalse(row.network_requested)
        self.assertFalse(
            row.tool_execution_requested
        )
        self.assertFalse(
            row.mission_transition_requested
        )
        self.assertFalse(
            row.persistence_requested
        )

    def test_admissible_asserts_no_authority(
        self,
    ):
        row = (
            GovernedRadarResearchDraftAdmissionGate
            .evaluate(
                self.drafts()
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

    def test_gate_is_deterministic(
        self,
    ):
        drafts = self.drafts(2)

        first = (
            GovernedRadarResearchDraftAdmissionGate
            .evaluate(
                drafts
            )
        )

        second = (
            GovernedRadarResearchDraftAdmissionGate
            .evaluate(
                drafts
            )
        )

        self.assertEqual(first, second)

    def test_wrong_inputs_fail_closed(
        self,
    ):
        with self.assertRaises(TypeError):
            (
                GovernedRadarResearchDraftAdmissionGate
                .evaluate(
                    object()
                )
            )

        with self.assertRaises(TypeError):
            (
                GovernedRadarResearchDraftAdmissionGate
                .evaluate(
                    self.drafts(),
                    policy=object(),
                )
            )

        with self.assertRaises(
            ValueError
        ):
            RadarResearchDraftAdmissionPolicy(
                max_query_chars=0
            )

    def test_module_has_no_active_authority_imports(
        self,
    ):
        path = Path(
            "src/maestro/research/"
            "radar_research_draft_admission.py"
        )

        tree = ast.parse(
            path.read_text(
                encoding="utf-8"
            )
        )

        imported = set()

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imported.add(alias.name)

            elif isinstance(
                node,
                ast.ImportFrom,
            ):
                if node.module:
                    imported.add(node.module)

        forbidden = (
            "socket",
            "http",
            "urllib",
            "requests",
            "subprocess",
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
            "maestro.research.runtime",
            "maestro.research.runtime_contracts",
            "maestro.research.transport",
            "maestro.research.web_fetch",
            "maestro.research.composition",
            "maestro.research.provider_registry",
            "maestro.research.durable_store",
        )

        violations = sorted(
            name
            for name in imported
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


if __name__ == "__main__":
    unittest.main()
