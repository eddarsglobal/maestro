from __future__ import annotations

import ast
import copy
import unittest

from pathlib import Path

from maestro.research import (
    ContentDigest,
    ExternalArtifact,
    GovernedRadarDecisionEnvelope,
    GovernedRadarEvidenceFollowUp,
    GovernedRadarEvaluationPipeline,
    GovernedRadarPortfolio,
    GovernedRadarReviewHandoff,
    GovernedRadarReviewPacket,
    GovernedRadarReviewResponse,
    RadarDecisionPolicy,
    RadarEvidenceNeedKind,
    RadarPortfolioEntry,
    RadarReviewResponseValue,
    RadarReviewTarget,
    ResearchClaim,
    ResearchEvidenceBridge,
    ResearchSource,
    SourceProvenance,
)


class RadarEvidenceFollowUpTests(
    unittest.TestCase
):
    NOW = "2026-01-01T00:00:00+00:00"

    def evidence(
        self,
        *,
        suffix: str,
    ):
        statement = (
            "GPU reasoning improves "
            "MAESTRO research"
        )

        source = ResearchSource(
            (
                "https://example.com/"
                f"adel014-{suffix}"
            ),
            label=(
                f"ADEL0.14 {suffix}"
            ),
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
            ResearchEvidenceBridge
            .to_evidence(
                task_id=(
                    "TASK-A1B2C3D4E5F6"
                ),
                claim=claim,
                artifacts=[artifact],
            )
        )

    def context(
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

    def handoff(
        self,
        *,
        count=1,
        target=(
            RadarReviewTarget
            .HUMAN_REVIEW
        ),
    ):
        portfolio = (
            GovernedRadarPortfolio()
            .evaluate(
                tuple(
                    RadarPortfolioEntry(
                        evidence=(
                            self.evidence(
                                suffix=str(index)
                            )
                        ),
                        context=self.context(),
                    )
                    for index
                    in range(count)
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

        assignments = {
            entry.evidence_id: target
            for entry in packet.entries
        }

        return (
            GovernedRadarReviewHandoff
            .build(
                packet,
                assignments=assignments,
            )
        )

    def response(
        self,
        *,
        values,
        target=(
            RadarReviewTarget
            .HUMAN_REVIEW
        ),
    ):
        handoff = self.handoff(
            count=len(values),
            target=target,
        )

        mapping = {
            entry.evidence_id: value
            for entry, value
            in zip(
                handoff.entries,
                values,
                strict=True,
            )
        }

        return (
            GovernedRadarReviewResponse
            .build(
                handoff,
                responses=mapping,
            )
        )

    def test_empty_response_produces_empty_followup(
        self,
    ):
        response = self.response(
            values=()
        )

        result = (
            GovernedRadarEvidenceFollowUp
            .build(
                response
            )
        )

        self.assertEqual(
            result.size,
            0,
        )

    def test_request_more_evidence_creates_need(
        self,
    ):
        response = self.response(
            values=(
                RadarReviewResponseValue
                .REQUEST_MORE_EVIDENCE,
            )
        )

        result = (
            GovernedRadarEvidenceFollowUp
            .build(
                response
            )
        )

        self.assertEqual(
            result.size,
            1,
        )

    def test_retain_review_creates_no_need(
        self,
    ):
        response = self.response(
            values=(
                RadarReviewResponseValue
                .RETAIN_REVIEW,
            )
        )

        result = (
            GovernedRadarEvidenceFollowUp
            .build(
                response
            )
        )

        self.assertEqual(
            result.size,
            0,
        )

    def test_return_to_observe_creates_no_need(
        self,
    ):
        response = self.response(
            values=(
                RadarReviewResponseValue
                .RETURN_TO_OBSERVE,
            )
        )

        result = (
            GovernedRadarEvidenceFollowUp
            .build(
                response
            )
        )

        self.assertEqual(
            result.size,
            0,
        )

    def test_mixed_response_selects_only_more_evidence(
        self,
    ):
        response = self.response(
            values=(
                RadarReviewResponseValue
                .RETAIN_REVIEW,
                RadarReviewResponseValue
                .REQUEST_MORE_EVIDENCE,
                RadarReviewResponseValue
                .RETURN_TO_OBSERVE,
            )
        )

        result = (
            GovernedRadarEvidenceFollowUp
            .build(
                response
            )
        )

        self.assertEqual(
            result.size,
            1,
        )

        self.assertEqual(
            result.evidence_ids,
            (
                response.entries[1]
                .evidence_id,
            ),
        )

    def test_need_kind_is_passive_external_evidence(
        self,
    ):
        response = self.response(
            values=(
                RadarReviewResponseValue
                .REQUEST_MORE_EVIDENCE,
            )
        )

        result = (
            GovernedRadarEvidenceFollowUp
            .build(
                response
            )
        )

        self.assertEqual(
            result.needs[0].need_kind,
            (
                RadarEvidenceNeedKind
                .ADDITIONAL_EXTERNAL_EVIDENCE
            ),
        )

    def test_response_value_is_preserved(
        self,
    ):
        response = self.response(
            values=(
                RadarReviewResponseValue
                .REQUEST_MORE_EVIDENCE,
            )
        )

        result = (
            GovernedRadarEvidenceFollowUp
            .build(
                response
            )
        )

        self.assertEqual(
            result.needs[0].response,
            (
                RadarReviewResponseValue
                .REQUEST_MORE_EVIDENCE
            ),
        )

    def test_target_is_preserved(
        self,
    ):
        response = self.response(
            values=(
                RadarReviewResponseValue
                .REQUEST_MORE_EVIDENCE,
            ),
            target=(
                RadarReviewTarget
                .AY_REVIEW
            ),
        )

        result = (
            GovernedRadarEvidenceFollowUp
            .build(
                response
            )
        )

        self.assertEqual(
            result.needs[0].target,
            RadarReviewTarget.AY_REVIEW,
        )

    def test_selected_order_is_preserved(
        self,
    ):
        response = self.response(
            values=(
                RadarReviewResponseValue
                .REQUEST_MORE_EVIDENCE,
                RadarReviewResponseValue
                .RETAIN_REVIEW,
                RadarReviewResponseValue
                .REQUEST_MORE_EVIDENCE,
            )
        )

        result = (
            GovernedRadarEvidenceFollowUp
            .build(
                response
            )
        )

        self.assertEqual(
            result.evidence_ids,
            (
                response.entries[0]
                .evidence_id,
                response.entries[2]
                .evidence_id,
            ),
        )

    def test_evidence_payload_is_preserved(
        self,
    ):
        response = self.response(
            values=(
                RadarReviewResponseValue
                .REQUEST_MORE_EVIDENCE,
            )
        )

        result = (
            GovernedRadarEvidenceFollowUp
            .build(
                response
            )
        )

        before = response.entries[0]
        after = result.needs[0]

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

    def test_unverified_boundary_is_preserved(
        self,
    ):
        response = self.response(
            values=(
                RadarReviewResponseValue
                .REQUEST_MORE_EVIDENCE,
            )
        )

        result = (
            GovernedRadarEvidenceFollowUp
            .build(
                response
            )
        )

        need = result.needs[0]

        self.assertEqual(
            need.verification_status,
            "UNVERIFIED_EXTERNAL",
        )
        self.assertFalse(
            need.system_truth_asserted
        )

    def test_no_research_request_or_side_effect_is_created(
        self,
    ):
        response = self.response(
            values=(
                RadarReviewResponseValue
                .REQUEST_MORE_EVIDENCE,
            )
        )

        result = (
            GovernedRadarEvidenceFollowUp
            .build(
                response
            )
        )

        need = result.needs[0]

        self.assertFalse(
            need.research_request_created
        )
        self.assertFalse(
            need.network_requested
        )
        self.assertFalse(
            need.tool_execution_requested
        )
        self.assertFalse(
            need.mission_transition_requested
        )
        self.assertFalse(
            need.persistence_requested
        )

    def test_no_authority_is_asserted(
        self,
    ):
        response = self.response(
            values=(
                RadarReviewResponseValue
                .REQUEST_MORE_EVIDENCE,
            )
        )

        result = (
            GovernedRadarEvidenceFollowUp
            .build(
                response
            )
        )

        need = result.needs[0]

        self.assertFalse(
            need.authorization_asserted
        )
        self.assertFalse(
            need.promotion_asserted
        )
        self.assertFalse(
            need.activation_asserted
        )
        self.assertFalse(
            need.execution_asserted
        )

    def test_followup_is_deterministic(
        self,
    ):
        response = self.response(
            values=(
                RadarReviewResponseValue
                .REQUEST_MORE_EVIDENCE,
                RadarReviewResponseValue
                .REQUEST_MORE_EVIDENCE,
            )
        )

        first = (
            GovernedRadarEvidenceFollowUp
            .build(
                response
            )
        )

        second = (
            GovernedRadarEvidenceFollowUp
            .build(
                response
            )
        )

        self.assertEqual(
            first,
            second,
        )

    def test_wrong_response_type_rejected(
        self,
    ):
        with self.assertRaises(
            TypeError
        ):
            (
                GovernedRadarEvidenceFollowUp
                .build(
                    object()
                )
            )

    def test_input_is_not_mutated(
        self,
    ):
        response = self.response(
            values=(
                RadarReviewResponseValue
                .REQUEST_MORE_EVIDENCE,
            )
        )

        before = copy.deepcopy(
            response
        )

        (
            GovernedRadarEvidenceFollowUp
            .build(
                response
            )
        )

        self.assertEqual(
            response,
            before,
        )

    def test_non_selected_entries_do_not_leak(
        self,
    ):
        response = self.response(
            values=(
                RadarReviewResponseValue
                .RETAIN_REVIEW,
                RadarReviewResponseValue
                .RETURN_TO_OBSERVE,
            )
        )

        result = (
            GovernedRadarEvidenceFollowUp
            .build(
                response
            )
        )

        self.assertEqual(
            result.needs,
            (),
        )

    def test_module_has_no_runtime_network_queue_or_governance_imports(
        self,
    ):
        path = Path(
            "src/maestro/research/"
            "radar_evidence_followup.py"
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
