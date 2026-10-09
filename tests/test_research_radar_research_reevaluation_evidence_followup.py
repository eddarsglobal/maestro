from __future__ import annotations

import ast
import unittest

from pathlib import Path
from unittest.mock import patch

import test_research_radar_research_reevaluation_review_response as adel030_tests

from maestro.research import (
    GovernedRadarDecisionEnvelope,
    GovernedRadarEvidenceFollowUp,
    GovernedRadarEvaluationPipeline,
    GovernedRadarFollowUpCandidateBuilder,
    GovernedRadarReevaluationEvidenceFollowUp,
    GovernedRadarReevaluationReviewResponse,
    RadarEvidenceNeedKind,
    RadarReviewResponseValue,
    RadarReviewTarget,
    TechnologyRadar,
)


class RadarReevaluationEvidenceFollowUpTests(
    unittest.TestCase
):
    def fixture(
        self,
    ):
        return (
            adel030_tests
            .RadarReevaluationReviewResponseTests()
        )

    def response_source(
        self,
        values,
        *,
        target=RadarReviewTarget.HUMAN_REVIEW,
    ):
        fixture = self.fixture()

        handoff = fixture.handoff_source(
            len(values),
            target=target,
        )

        mapping = {
            evidence_id: value
            for evidence_id, value
            in zip(
                handoff.evidence_ids,
                values,
                strict=True,
            )
        }

        return (
            GovernedRadarReevaluationReviewResponse
            .respond(
                handoff,
                responses=mapping,
            )
        )

    def no_response_source(
        self,
    ):
        fixture = self.fixture()

        handoff = fixture.no_handoff_source()

        return (
            GovernedRadarReevaluationReviewResponse
            .respond(
                handoff,
                responses={},
            )
        )

    def test_no_response_creates_no_followup(
        self,
    ):
        source = self.no_response_source()

        with patch.object(
            GovernedRadarEvidenceFollowUp,
            "build",
            side_effect=AssertionError(
                "ADEL0.14 BUILDER MUST NOT RUN"
            ),
        ):
            result = (
                GovernedRadarReevaluationEvidenceFollowUp
                .build(
                    source
                )
            )

        self.assertIsNone(
            result.followup
        )

        self.assertFalse(
            result.followup_need_created
        )

        self.assertEqual(
            result.size,
            0,
        )

    def test_retain_review_creates_no_need(
        self,
    ):
        source = self.response_source(
            (
                RadarReviewResponseValue
                .RETAIN_REVIEW,
            )
        )

        result = (
            GovernedRadarReevaluationEvidenceFollowUp
            .build(
                source
            )
        )

        self.assertIsNotNone(
            result.followup
        )

        self.assertEqual(
            result.size,
            0,
        )

        self.assertFalse(
            result.followup_need_created
        )

    def test_return_to_observe_creates_no_need(
        self,
    ):
        source = self.response_source(
            (
                RadarReviewResponseValue
                .RETURN_TO_OBSERVE,
            )
        )

        result = (
            GovernedRadarReevaluationEvidenceFollowUp
            .build(
                source
            )
        )

        self.assertEqual(
            result.size,
            0,
        )

        self.assertFalse(
            result.followup_need_created
        )

    def test_request_more_evidence_creates_need(
        self,
    ):
        source = self.response_source(
            (
                RadarReviewResponseValue
                .REQUEST_MORE_EVIDENCE,
            )
        )

        result = (
            GovernedRadarReevaluationEvidenceFollowUp
            .build(
                source
            )
        )

        self.assertTrue(
            result.followup_need_created
        )

        self.assertEqual(
            result.size,
            1,
        )

        self.assertEqual(
            result.evidence_ids,
            source.request_more_evidence_ids,
        )

    def test_mixed_selects_only_request_more_evidence(
        self,
    ):
        source = self.response_source(
            (
                RadarReviewResponseValue
                .RETAIN_REVIEW,
                RadarReviewResponseValue
                .REQUEST_MORE_EVIDENCE,
                RadarReviewResponseValue
                .RETURN_TO_OBSERVE,
            )
        )

        result = (
            GovernedRadarReevaluationEvidenceFollowUp
            .build(
                source
            )
        )

        self.assertEqual(
            result.evidence_ids,
            source.request_more_evidence_ids,
        )

        self.assertEqual(
            result.size,
            1,
        )

    def test_existing_adel014_builder_is_reused(
        self,
    ):
        source = self.response_source(
            (
                RadarReviewResponseValue
                .REQUEST_MORE_EVIDENCE,
            )
        )

        original = (
            GovernedRadarEvidenceFollowUp
            .build
        )

        with patch.object(
            GovernedRadarEvidenceFollowUp,
            "build",
            wraps=original,
        ) as mocked:
            result = (
                GovernedRadarReevaluationEvidenceFollowUp
                .build(
                    source
                )
            )

        self.assertEqual(
            mocked.call_count,
            1,
        )

        self.assertEqual(
            result.size,
            1,
        )

    def test_need_kind_and_response_are_preserved(
        self,
    ):
        source = self.response_source(
            (
                RadarReviewResponseValue
                .REQUEST_MORE_EVIDENCE,
            )
        )

        result = (
            GovernedRadarReevaluationEvidenceFollowUp
            .build(
                source
            )
        )

        row = result.entries[0]

        self.assertIs(
            row.response,
            RadarReviewResponseValue
            .REQUEST_MORE_EVIDENCE,
        )

        self.assertIs(
            row.need_kind,
            RadarEvidenceNeedKind
            .ADDITIONAL_EXTERNAL_EVIDENCE,
        )

    def test_exact_order_and_ranks_are_preserved(
        self,
    ):
        source = self.response_source(
            (
                RadarReviewResponseValue
                .REQUEST_MORE_EVIDENCE,
                RadarReviewResponseValue
                .RETAIN_REVIEW,
                RadarReviewResponseValue
                .REQUEST_MORE_EVIDENCE,
            )
        )

        result = (
            GovernedRadarReevaluationEvidenceFollowUp
            .build(
                source
            )
        )

        selected = tuple(
            entry
            for entry in source.entries
            if (
                entry
                .request_more_evidence_recommended
            )
        )

        self.assertEqual(
            result.evidence_ids,
            tuple(
                entry.evidence_id
                for entry in selected
            ),
        )

        self.assertEqual(
            tuple(
                row.response_rank
                for row in result.entries
            ),
            tuple(
                entry.response_entry.rank
                for entry in selected
            ),
        )

    def test_payload_factor_target_identity_preserved(
        self,
    ):
        source = self.response_source(
            (
                RadarReviewResponseValue
                .REQUEST_MORE_EVIDENCE,
            ),
            target=RadarReviewTarget.AY_REVIEW,
        )

        result = (
            GovernedRadarReevaluationEvidenceFollowUp
            .build(
                source
            )
        )

        before = (
            source.entries[0]
            .response_entry
        )

        after = (
            result.entries[0]
            .need
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

        self.assertIs(
            after.factors,
            before.factors,
        )

        self.assertEqual(
            after.rationale,
            before.rationale,
        )

        self.assertIs(
            after.target,
            before.target,
        )

    def test_lineage_is_preserved(
        self,
    ):
        source = self.response_source(
            (
                RadarReviewResponseValue
                .REQUEST_MORE_EVIDENCE,
                RadarReviewResponseValue
                .REQUEST_MORE_EVIDENCE,
            )
        )

        result = (
            GovernedRadarReevaluationEvidenceFollowUp
            .build(
                source
            )
        )

        for before, after in zip(
            source.entries,
            result.entries,
            strict=True,
        ):
            self.assertIs(
                after.source_entry,
                before,
            )

            self.assertEqual(
                after.packet_rank,
                before.packet_rank,
            )

            self.assertEqual(
                after.source_rank,
                before.source_rank,
            )

            self.assertEqual(
                after.cycle_number,
                before.cycle_number,
            )

            self.assertEqual(
                after.origin_evidence_id,
                before.origin_evidence_id,
            )

            self.assertEqual(
                after.task_id,
                before.task_id,
            )

    def test_human_target_has_no_approval(
        self,
    ):
        source = self.response_source(
            (
                RadarReviewResponseValue
                .REQUEST_MORE_EVIDENCE,
            ),
            target=(
                RadarReviewTarget.HUMAN_REVIEW
            ),
        )

        result = (
            GovernedRadarReevaluationEvidenceFollowUp
            .build(
                source
            )
        )

        self.assertIs(
            result.entries[0].target,
            RadarReviewTarget.HUMAN_REVIEW,
        )

        self.assertFalse(
            result.entries[0]
            .human_approval_asserted
        )

    def test_ay_target_has_no_validation(
        self,
    ):
        source = self.response_source(
            (
                RadarReviewResponseValue
                .REQUEST_MORE_EVIDENCE,
            ),
            target=RadarReviewTarget.AY_REVIEW,
        )

        result = (
            GovernedRadarReevaluationEvidenceFollowUp
            .build(
                source
            )
        )

        self.assertIs(
            result.entries[0].target,
            RadarReviewTarget.AY_REVIEW,
        )

        self.assertFalse(
            result.entries[0]
            .ay_validation_asserted
        )

    def test_ex_target_has_no_authorization(
        self,
    ):
        source = self.response_source(
            (
                RadarReviewResponseValue
                .REQUEST_MORE_EVIDENCE,
            ),
            target=RadarReviewTarget.EX_REVIEW,
        )

        result = (
            GovernedRadarReevaluationEvidenceFollowUp
            .build(
                source
            )
        )

        self.assertIs(
            result.entries[0].target,
            RadarReviewTarget.EX_REVIEW,
        )

        self.assertFalse(
            result.entries[0]
            .ex_authorization_asserted
        )

    def test_no_candidate_research_or_side_effects(
        self,
    ):
        source = self.response_source(
            (
                RadarReviewResponseValue
                .REQUEST_MORE_EVIDENCE,
            )
        )

        with (
            patch.object(
                GovernedRadarFollowUpCandidateBuilder,
                "build",
                side_effect=AssertionError(
                    "FOLLOW-UP CANDIDATE CREATED"
                ),
            ),
            patch.object(
                GovernedRadarEvaluationPipeline,
                "evaluate",
                side_effect=AssertionError(
                    "SECOND RADAR EVALUATION"
                ),
            ),
            patch.object(
                TechnologyRadar,
                "rank",
                side_effect=AssertionError(
                    "SECOND RANKING"
                ),
            ),
            patch.object(
                GovernedRadarDecisionEnvelope,
                "evaluate",
                side_effect=AssertionError(
                    "SECOND DECISION"
                ),
            ),
        ):
            result = (
                GovernedRadarReevaluationEvidenceFollowUp
                .build(
                    source
                )
            )

        self.assertFalse(
            result.followup_candidate_created
        )

        self.assertFalse(
            result.research_request_created
        )

        self.assertFalse(
            result.provider_selection_created
        )

        self.assertFalse(
            result.routing_decision_created
        )

        self.assertFalse(
            result.network_requested
        )

        self.assertFalse(
            result.tool_execution_requested
        )

        self.assertFalse(
            result.persistence_requested
        )

        self.assertFalse(
            result.mission_transition_requested
        )

        self.assertFalse(
            result.rx_active_entered
        )

    def test_passive_truth_and_authority_boundary(
        self,
    ):
        source = self.response_source(
            (
                RadarReviewResponseValue
                .REQUEST_MORE_EVIDENCE,
            ),
            target=RadarReviewTarget.EX_REVIEW,
        )

        result = (
            GovernedRadarReevaluationEvidenceFollowUp
            .build(
                source
            )
        )

        self.assertEqual(
            result.verification_status,
            "UNVERIFIED_EXTERNAL",
        )

        self.assertFalse(
            result.verdict_asserted
        )

        self.assertFalse(
            result.human_approval_asserted
        )

        self.assertFalse(
            result.ay_validation_asserted
        )

        self.assertFalse(
            result.ex_authorization_asserted
        )

        self.assertFalse(
            result.governance_attestation_asserted
        )

        self.assertFalse(
            result.system_truth_asserted
        )

        self.assertFalse(
            result.learning_asserted
        )

        self.assertFalse(
            result.promotion_asserted
        )

        self.assertFalse(
            result.activation_asserted
        )

        self.assertFalse(
            result.execution_asserted
        )

    def test_wrong_source_fails_closed(
        self,
    ):
        with self.assertRaises(
            TypeError
        ):
            (
                GovernedRadarReevaluationEvidenceFollowUp
                .build(
                    object()
                )
            )

    def test_deterministic_and_source_unchanged(
        self,
    ):
        source = self.response_source(
            (
                RadarReviewResponseValue
                .REQUEST_MORE_EVIDENCE,
                RadarReviewResponseValue
                .RETAIN_REVIEW,
                RadarReviewResponseValue
                .REQUEST_MORE_EVIDENCE,
            )
        )

        source_entries = source.entries
        source_response = source.response
        source_ids = source.evidence_ids

        first = (
            GovernedRadarReevaluationEvidenceFollowUp
            .build(
                source
            )
        )

        second = (
            GovernedRadarReevaluationEvidenceFollowUp
            .build(
                source
            )
        )

        self.assertEqual(
            first,
            second,
        )

        self.assertIs(
            source.entries,
            source_entries,
        )

        self.assertIs(
            source.response,
            source_response,
        )

        self.assertEqual(
            source.evidence_ids,
            source_ids,
        )

    def test_static_boundary_is_exact(
        self,
    ):
        path = Path(
            "src/maestro/research/"
            "radar_research_reevaluation_evidence_followup.py"
        )

        tree = ast.parse(
            path.read_text(
                encoding="utf-8"
            )
        )

        calls = set()
        imported_modules = set()

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
                imported_modules.add(
                    node.module or ""
                )

        self.assertIn(
            "GovernedRadarEvidenceFollowUp.build",
            calls,
        )

        forbidden_calls = {
            "GovernedRadarFollowUpCandidateBuilder.build",
            "GovernedRadarResearchRequestDraftBuilder.build",
            "GovernedRadarEvaluationPipeline.evaluate",
            "GovernedRadarPortfolio.evaluate",
            "TechnologyRadar.rank",
            "GovernedRadarDecisionEnvelope.evaluate",
            "ResearchEvidenceStore.record",
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

        forbidden_modules = (
            "radar_followup_candidate",
            "radar_research_request_draft",
            "durable_store",
            "runtime",
        )

        for imported in imported_modules:
            for fragment in forbidden_modules:
                self.assertNotIn(
                    fragment,
                    imported,
                )


if __name__ == "__main__":
    unittest.main()
