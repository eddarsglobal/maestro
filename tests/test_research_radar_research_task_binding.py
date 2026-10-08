from __future__ import annotations

import ast
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
    GovernedRadarResearchTaskBinder,
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


class RadarResearchTaskBindingTests(
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
                f"adel018-{suffix}"
            ),
            label=f"ADEL0.18 {suffix}",
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

    def admission(
        self,
        count=1,
    ):
        return (
            GovernedRadarResearchDraftAdmissionGate
            .evaluate(
                self.drafts(count)
            )
        )

    def task_map(
        self,
        admission,
    ):
        values = (
            self.TASK_A,
            self.TASK_B,
            self.TASK_C,
        )

        return {
            entry.evidence_id: values[index]
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

    def test_empty_admission_binds_nothing(
        self,
    ):
        admission = self.admission(0)

        result = (
            GovernedRadarResearchTaskBinder
            .bind(
                admission,
                task_ids={},
            )
        )

        self.assertEqual(
            result.size,
            0,
        )

    def test_admissible_entry_receives_task_binding(
        self,
    ):
        admission = self.admission()

        result = (
            GovernedRadarResearchTaskBinder
            .bind(
                admission,
                task_ids=(
                    self.task_map(
                        admission
                    )
                ),
            )
        )

        self.assertEqual(
            result.size,
            1,
        )
        self.assertTrue(
            result.entries[0].task_id_bound
        )

    def test_rejected_entry_is_not_bound(
        self,
    ):
        drafts = self.drafts()

        admission = (
            GovernedRadarResearchDraftAdmissionGate
            .evaluate(
                drafts,
                policy=(
                    RadarResearchDraftAdmissionPolicy(
                        max_query_chars=1
                    )
                ),
            )
        )

        self.assertEqual(
            admission.entries[0].status,
            RadarResearchDraftAdmissionStatus
            .REJECTED,
        )

        result = (
            GovernedRadarResearchTaskBinder
            .bind(
                admission,
                task_ids={},
            )
        )

        self.assertEqual(
            result.size,
            0,
        )

    def test_missing_task_mapping_fails_closed(
        self,
    ):
        admission = self.admission()

        with self.assertRaises(
            ValueError
        ):
            (
                GovernedRadarResearchTaskBinder
                .bind(
                    admission,
                    task_ids={},
                )
            )

    def test_extra_task_mapping_fails_closed(
        self,
    ):
        admission = self.admission()

        mapping = self.task_map(
            admission
        )

        mapping["EVD-NOTADMISSIBLE"] = (
            self.TASK_B
        )

        with self.assertRaises(
            ValueError
        ):
            (
                GovernedRadarResearchTaskBinder
                .bind(
                    admission,
                    task_ids=mapping,
                )
            )

    def test_canonical_task_id_is_preserved(
        self,
    ):
        admission = self.admission()

        result = (
            GovernedRadarResearchTaskBinder
            .bind(
                admission,
                task_ids={
                    admission.entries[0]
                    .evidence_id: self.TASK_B,
                },
            )
        )

        self.assertEqual(
            result.entries[0].task_id,
            self.TASK_B,
        )

    def test_invalid_task_id_fails_closed(
        self,
    ):
        admission = self.admission()

        with self.assertRaises(
            ValueError
        ):
            (
                GovernedRadarResearchTaskBinder
                .bind(
                    admission,
                    task_ids={
                        admission.entries[0]
                        .evidence_id: (
                            "runtime-task"
                        ),
                    },
                )
            )

    def test_order_is_preserved(
        self,
    ):
        admission = self.admission(3)

        result = (
            GovernedRadarResearchTaskBinder
            .bind(
                admission,
                task_ids=(
                    self.task_map(
                        admission
                    )
                ),
            )
        )

        self.assertEqual(
            result.evidence_ids,
            tuple(
                entry.evidence_id
                for entry
                in admission.entries
            ),
        )

    def test_payload_is_preserved(
        self,
    ):
        admission = self.admission()

        result = (
            GovernedRadarResearchTaskBinder
            .bind(
                admission,
                task_ids=(
                    self.task_map(
                        admission
                    )
                ),
            )
        )

        before = admission.entries[0]
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
            after.arguments,
            before.arguments,
        )

    def test_admission_provenance_is_preserved(
        self,
    ):
        admission = self.admission()

        result = (
            GovernedRadarResearchTaskBinder
            .bind(
                admission,
                task_ids=(
                    self.task_map(
                        admission
                    )
                ),
            )
        )

        row = result.entries[0]

        self.assertEqual(
            row.admission_status,
            RadarResearchDraftAdmissionStatus
            .ADMISSIBLE,
        )
        self.assertEqual(
            row.admission_reason,
            admission.entries[0].reason,
        )

    def test_unverified_boundary_is_preserved(
        self,
    ):
        admission = self.admission()

        row = (
            GovernedRadarResearchTaskBinder
            .bind(
                admission,
                task_ids=(
                    self.task_map(
                        admission
                    )
                ),
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

    def test_task_binding_does_not_create_research_request(
        self,
    ):
        admission = self.admission()

        row = (
            GovernedRadarResearchTaskBinder
            .bind(
                admission,
                task_ids=(
                    self.task_map(
                        admission
                    )
                ),
            )
            .entries[0]
        )

        self.assertTrue(
            row.task_id_bound
        )
        self.assertFalse(
            row.research_request_created
        )

    def test_task_binding_does_not_select_provider_or_route(
        self,
    ):
        admission = self.admission()

        row = (
            GovernedRadarResearchTaskBinder
            .bind(
                admission,
                task_ids=(
                    self.task_map(
                        admission
                    )
                ),
            )
            .entries[0]
        )

        self.assertFalse(
            row.provider_selected
        )
        self.assertFalse(
            row.routing_decision_created
        )

    def test_task_binding_has_no_runtime_side_effects(
        self,
    ):
        admission = self.admission()

        row = (
            GovernedRadarResearchTaskBinder
            .bind(
                admission,
                task_ids=(
                    self.task_map(
                        admission
                    )
                ),
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

    def test_task_binding_asserts_no_authority(
        self,
    ):
        admission = self.admission()

        row = (
            GovernedRadarResearchTaskBinder
            .bind(
                admission,
                task_ids=(
                    self.task_map(
                        admission
                    )
                ),
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

    def test_binder_is_deterministic(
        self,
    ):
        admission = self.admission(2)
        mapping = self.task_map(
            admission
        )

        first = (
            GovernedRadarResearchTaskBinder
            .bind(
                admission,
                task_ids=mapping,
            )
        )

        second = (
            GovernedRadarResearchTaskBinder
            .bind(
                admission,
                task_ids=mapping,
            )
        )

        self.assertEqual(
            first,
            second,
        )

    def test_wrong_inputs_fail_closed(
        self,
    ):
        admission = self.admission()

        with self.assertRaises(
            TypeError
        ):
            (
                GovernedRadarResearchTaskBinder
                .bind(
                    object(),
                    task_ids={},
                )
            )

        with self.assertRaises(
            TypeError
        ):
            (
                GovernedRadarResearchTaskBinder
                .bind(
                    admission,
                    task_ids=object(),
                )
            )

    def test_module_has_no_request_runtime_or_authority_imports(
        self,
    ):
        path = Path(
            "src/maestro/research/"
            "radar_research_task_binding.py"
        )

        tree = ast.parse(
            path.read_text(
                encoding="utf-8"
            )
        )

        imported = set()

        for node in ast.walk(tree):
            if isinstance(
                node,
                ast.Import,
            ):
                for alias in node.names:
                    imported.add(
                        alias.name
                    )

            elif isinstance(
                node,
                ast.ImportFrom,
            ):
                if node.module:
                    imported.add(
                        node.module
                    )

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
