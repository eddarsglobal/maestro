from __future__ import annotations

import ast
import unittest

from pathlib import Path
from unittest.mock import patch

import test_research_radar_research_reevaluation_review_handoff as adel029_tests

from maestro.research import (
    GovernedRadarDecisionEnvelope,
    GovernedRadarEvidenceFollowUp,
    GovernedRadarEvaluationPipeline,
    GovernedRadarReevaluationReviewHandoff,
    GovernedRadarReevaluationReviewResponse,
    GovernedRadarReviewResponse,
    RadarReviewResponseInvariantError,
    RadarReviewResponseValue,
    RadarReviewTarget,
    TechnologyRadar,
)


class RadarReevaluationReviewResponseTests(
    unittest.TestCase
):
    def fixture(
        self,
    ):
        return (
            adel029_tests
            .RadarReevaluationReviewHandoffTests()
        )

    def handoff_source(
        self,
        count=1,
        *,
        target=RadarReviewTarget.HUMAN_REVIEW,
    ):
        fixture = self.fixture()

        source = fixture.review_source(
            count
        )

        return (
            GovernedRadarReevaluationReviewHandoff
            .handoff(
                source,
                assignments=fixture.assignments(
                    source,
                    target=target,
                ),
            )
        )

    def no_handoff_source(
        self,
    ):
        fixture = self.fixture()

        source = fixture.no_packet_source()

        return (
            GovernedRadarReevaluationReviewHandoff
            .handoff(
                source,
                assignments={},
            )
        )

    def responses(
        self,
        source,
        *,
        value=RadarReviewResponseValue.RETAIN_REVIEW,
    ):
        return {
            evidence_id: value
            for evidence_id
            in source.evidence_ids
        }

    def test_no_handoff_empty_responses_creates_no_response(
        self,
    ):
        source = self.no_handoff_source()

        result = (
            GovernedRadarReevaluationReviewResponse
            .respond(
                source,
                responses={},
            )
        )

        self.assertIsNone(
            result.response
        )

        self.assertFalse(
            result.review_response_created
        )

        self.assertEqual(
            result.size,
            0,
        )

    def test_no_handoff_nonempty_responses_fail_closed(
        self,
    ):
        source = self.no_handoff_source()

        with self.assertRaises(
            ValueError
        ):
            (
                GovernedRadarReevaluationReviewResponse
                .respond(
                    source,
                    responses={
                        "EVIDENCE-UNKNOWN": (
                            RadarReviewResponseValue
                            .RETAIN_REVIEW
                        ),
                    },
                )
            )

    def test_retain_review_is_recommendation_only(
        self,
    ):
        source = self.handoff_source()

        result = (
            GovernedRadarReevaluationReviewResponse
            .respond(
                source,
                responses=self.responses(
                    source,
                    value=(
                        RadarReviewResponseValue
                        .RETAIN_REVIEW
                    ),
                ),
            )
        )

        row = result.entries[0]

        self.assertTrue(
            row.retain_review_recommended
        )

        self.assertFalse(
            row.human_approval_asserted
        )

        self.assertFalse(
            row.verdict_asserted
        )

    def test_request_more_evidence_is_recommendation_only(
        self,
    ):
        source = self.handoff_source()

        result = (
            GovernedRadarReevaluationReviewResponse
            .respond(
                source,
                responses=self.responses(
                    source,
                    value=(
                        RadarReviewResponseValue
                        .REQUEST_MORE_EVIDENCE
                    ),
                ),
            )
        )

        row = result.entries[0]

        self.assertTrue(
            row.request_more_evidence_recommended
        )

        self.assertFalse(
            row.followup_created
        )

        self.assertFalse(
            row.new_research_request_created
        )

        self.assertFalse(
            result.followup_created
        )

        self.assertFalse(
            result.new_research_request_created
        )

    def test_return_to_observe_is_recommendation_only(
        self,
    ):
        source = self.handoff_source()

        result = (
            GovernedRadarReevaluationReviewResponse
            .respond(
                source,
                responses=self.responses(
                    source,
                    value=(
                        RadarReviewResponseValue
                        .RETURN_TO_OBSERVE
                    ),
                ),
            )
        )

        row = result.entries[0]

        self.assertTrue(
            row.return_to_observe_recommended
        )

        self.assertFalse(
            row.rejection_asserted
        )

        self.assertFalse(
            row.verdict_asserted
        )

    def test_human_target_preserved_without_approval(
        self,
    ):
        source = self.handoff_source(
            target=(
                RadarReviewTarget.HUMAN_REVIEW
            ),
        )

        result = (
            GovernedRadarReevaluationReviewResponse
            .respond(
                source,
                responses=self.responses(
                    source
                ),
            )
        )

        self.assertIs(
            result.entries[0].target,
            RadarReviewTarget.HUMAN_REVIEW,
        )

        self.assertFalse(
            result.human_approval_asserted
        )

    def test_ay_target_preserved_without_validation(
        self,
    ):
        source = self.handoff_source(
            target=RadarReviewTarget.AY_REVIEW,
        )

        result = (
            GovernedRadarReevaluationReviewResponse
            .respond(
                source,
                responses=self.responses(
                    source
                ),
            )
        )

        self.assertIs(
            result.entries[0].target,
            RadarReviewTarget.AY_REVIEW,
        )

        self.assertFalse(
            result.ay_validation_asserted
        )

    def test_ex_target_preserved_without_authorization(
        self,
    ):
        source = self.handoff_source(
            target=RadarReviewTarget.EX_REVIEW,
        )

        result = (
            GovernedRadarReevaluationReviewResponse
            .respond(
                source,
                responses=self.responses(
                    source
                ),
            )
        )

        self.assertIs(
            result.entries[0].target,
            RadarReviewTarget.EX_REVIEW,
        )

        self.assertFalse(
            result.ex_authorization_asserted
        )

    def test_missing_response_fails_closed(
        self,
    ):
        source = self.handoff_source(
            2
        )

        responses = self.responses(
            source
        )

        responses.pop(
            source.evidence_ids[-1]
        )

        with self.assertRaises(
            RadarReviewResponseInvariantError
        ):
            (
                GovernedRadarReevaluationReviewResponse
                .respond(
                    source,
                    responses=responses,
                )
            )

    def test_extra_response_fails_closed(
        self,
    ):
        source = self.handoff_source()

        responses = self.responses(
            source
        )

        responses[
            "EVIDENCE-UNKNOWN"
        ] = (
            RadarReviewResponseValue.RETAIN_REVIEW
        )

        with self.assertRaises(
            RadarReviewResponseInvariantError
        ):
            (
                GovernedRadarReevaluationReviewResponse
                .respond(
                    source,
                    responses=responses,
                )
            )

    def test_invalid_inputs_fail_closed(
        self,
    ):
        source = self.handoff_source()

        with self.subTest(
            case="wrong response value"
        ):
            with self.assertRaises(
                TypeError
            ):
                (
                    GovernedRadarReevaluationReviewResponse
                    .respond(
                        source,
                        responses={
                            source.evidence_ids[0]:
                            "APPROVED",
                        },
                    )
                )

        with self.subTest(
            case="wrong source"
        ):
            with self.assertRaises(
                TypeError
            ):
                (
                    GovernedRadarReevaluationReviewResponse
                    .respond(
                        object(),
                        responses={},
                    )
                )

        with self.subTest(
            case="wrong responses mapping"
        ):
            with self.assertRaises(
                TypeError
            ):
                (
                    GovernedRadarReevaluationReviewResponse
                    .respond(
                        source,
                        responses=[],
                    )
                )

    def test_exact_coverage_and_order_preserved(
        self,
    ):
        source = self.handoff_source(
            3
        )

        result = (
            GovernedRadarReevaluationReviewResponse
            .respond(
                source,
                responses=self.responses(
                    source,
                    value=(
                        RadarReviewResponseValue
                        .REQUEST_MORE_EVIDENCE
                    ),
                ),
            )
        )

        self.assertEqual(
            result.evidence_ids,
            source.evidence_ids,
        )

        self.assertEqual(
            result.response.evidence_ids,
            source.evidence_ids,
        )

        self.assertEqual(
            result.responses,
            (
                RadarReviewResponseValue
                .REQUEST_MORE_EVIDENCE,
            )
            * 3,
        )

    def test_payload_factor_and_target_identity_preserved(
        self,
    ):
        source = self.handoff_source(
            target=RadarReviewTarget.AY_REVIEW,
        )

        result = (
            GovernedRadarReevaluationReviewResponse
            .respond(
                source,
                responses=self.responses(
                    source
                ),
            )
        )

        before = (
            source.entries[0]
            .handoff_entry
        )

        after = (
            result.entries[0]
            .response_entry
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

    def test_lineage_preserved(
        self,
    ):
        source = self.handoff_source(
            2
        )

        result = (
            GovernedRadarReevaluationReviewResponse
            .respond(
                source,
                responses=self.responses(
                    source
                ),
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

    def test_no_recomputation_or_followup_creation(
        self,
    ):
        source = self.handoff_source(
            2
        )

        with (
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
            patch.object(
                GovernedRadarReevaluationReviewHandoff,
                "handoff",
                side_effect=AssertionError(
                    "SECOND HANDOFF"
                ),
            ),
            patch.object(
                GovernedRadarEvidenceFollowUp,
                "build",
                side_effect=AssertionError(
                    "FOLLOW-UP CREATED"
                ),
            ),
        ):
            result = (
                GovernedRadarReevaluationReviewResponse
                .respond(
                    source,
                    responses=self.responses(
                        source,
                        value=(
                            RadarReviewResponseValue
                            .REQUEST_MORE_EVIDENCE
                        ),
                    ),
                )
            )

        self.assertEqual(
            result.size,
            2,
        )

        self.assertFalse(
            result.followup_created
        )

    def test_passive_truth_authority_and_side_effect_boundary(
        self,
    ):
        source = self.handoff_source(
            target=RadarReviewTarget.EX_REVIEW,
        )

        result = (
            GovernedRadarReevaluationReviewResponse
            .respond(
                source,
                responses=self.responses(
                    source,
                    value=(
                        RadarReviewResponseValue
                        .REQUEST_MORE_EVIDENCE
                    ),
                ),
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
            result.rejection_asserted
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

    def test_deterministic_and_inputs_unchanged(
        self,
    ):
        source = self.handoff_source(
            3
        )

        responses = self.responses(
            source,
            value=(
                RadarReviewResponseValue
                .RETURN_TO_OBSERVE
            ),
        )

        source_entries = source.entries
        source_handoff = source.handoff
        source_ids = source.evidence_ids
        responses_before = dict(
            responses
        )

        first = (
            GovernedRadarReevaluationReviewResponse
            .respond(
                source,
                responses=responses,
            )
        )

        second = (
            GovernedRadarReevaluationReviewResponse
            .respond(
                source,
                responses=responses,
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
            source.handoff,
            source_handoff,
        )

        self.assertEqual(
            source.evidence_ids,
            source_ids,
        )

        self.assertEqual(
            responses,
            responses_before,
        )

    def test_static_boundary_is_exact(
        self,
    ):
        path = Path(
            "src/maestro/research/"
            "radar_research_reevaluation_review_response.py"
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
            "GovernedRadarReviewResponse.build",
            calls,
        )

        forbidden_calls = {
            "GovernedRadarEvidenceFollowUp.build",
            "GovernedRadarFollowUpCandidateBuilder.build",
            "GovernedRadarResearchRequestDraftBuilder.build",
            "GovernedRadarEvaluationPipeline.evaluate",
            "GovernedRadarPortfolio.evaluate",
            "TechnologyRadar.rank",
            "GovernedRadarDecisionEnvelope.evaluate",
            "GovernedRadarReviewHandoff.build",
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
            "radar_evidence_followup",
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
