from __future__ import annotations

import ast
import unittest

from pathlib import Path
from unittest.mock import patch

import test_research_radar_research_reevaluation_review_packet as adel028_tests

from maestro.research import (
    GovernedRadarDecisionEnvelope,
    GovernedRadarEvaluationPipeline,
    GovernedRadarReevaluationReviewHandoff,
    GovernedRadarReevaluationReviewPacketMaterializer,
    GovernedRadarReviewHandoff,
    RadarReviewHandoffInvariantError,
    RadarReviewTarget,
    TechnologyRadar,
)


class RadarReevaluationReviewHandoffTests(
    unittest.TestCase
):
    def fixture(
        self,
    ):
        return (
            adel028_tests
            .RadarReevaluationReviewPacketTests()
        )

    def review_source(
        self,
        count=1,
    ):
        fixture = self.fixture()

        decision = fixture.decision(
            count,
            policy=fixture.review_policy(),
        )

        return (
            GovernedRadarReevaluationReviewPacketMaterializer
            .materialize(
                decision
            )
        )

    def no_packet_source(
        self,
    ):
        fixture = self.fixture()

        decision = fixture.decision(
            0,
            policy=fixture.review_policy(),
        )

        return (
            GovernedRadarReevaluationReviewPacketMaterializer
            .materialize(
                decision
            )
        )

    def assignments(
        self,
        source,
        *,
        target=RadarReviewTarget.HUMAN_REVIEW,
    ):
        return {
            evidence_id: target
            for evidence_id
            in source.evidence_ids
        }

    def test_no_packet_empty_assignments_creates_no_handoff(
        self,
    ):
        source = self.no_packet_source()

        result = (
            GovernedRadarReevaluationReviewHandoff
            .handoff(
                source,
                assignments={},
            )
        )

        self.assertIsNone(
            result.handoff
        )

        self.assertFalse(
            result.review_handoff_created
        )

        self.assertEqual(
            result.size,
            0,
        )

    def test_no_packet_nonempty_assignments_fail_closed(
        self,
    ):
        source = self.no_packet_source()

        with self.assertRaises(
            ValueError
        ):
            (
                GovernedRadarReevaluationReviewHandoff
                .handoff(
                    source,
                    assignments={
                        "EVIDENCE-UNKNOWN": (
                            RadarReviewTarget
                            .HUMAN_REVIEW
                        ),
                    },
                )
            )

    def test_human_review_target_is_routing_only(
        self,
    ):
        source = self.review_source()

        result = (
            GovernedRadarReevaluationReviewHandoff
            .handoff(
                source,
                assignments=self.assignments(
                    source,
                    target=(
                        RadarReviewTarget
                        .HUMAN_REVIEW
                    ),
                ),
            )
        )

        self.assertTrue(
            result.human_review_routed
        )

        self.assertFalse(
            result.human_approval_asserted
        )

    def test_ay_review_target_is_routing_only(
        self,
    ):
        source = self.review_source()

        result = (
            GovernedRadarReevaluationReviewHandoff
            .handoff(
                source,
                assignments=self.assignments(
                    source,
                    target=(
                        RadarReviewTarget
                        .AY_REVIEW
                    ),
                ),
            )
        )

        self.assertTrue(
            result.ay_review_routed
        )

        self.assertFalse(
            result.ay_validation_asserted
        )

    def test_ex_review_target_is_routing_only(
        self,
    ):
        source = self.review_source()

        result = (
            GovernedRadarReevaluationReviewHandoff
            .handoff(
                source,
                assignments=self.assignments(
                    source,
                    target=(
                        RadarReviewTarget
                        .EX_REVIEW
                    ),
                ),
            )
        )

        self.assertTrue(
            result.ex_review_routed
        )

        self.assertFalse(
            result.ex_authorization_asserted
        )

    def test_missing_assignment_fails_closed(
        self,
    ):
        source = self.review_source(
            2
        )

        assignments = self.assignments(
            source
        )

        assignments.pop(
            source.evidence_ids[-1]
        )

        with self.assertRaises(
            RadarReviewHandoffInvariantError
        ):
            (
                GovernedRadarReevaluationReviewHandoff
                .handoff(
                    source,
                    assignments=assignments,
                )
            )

    def test_extra_assignment_fails_closed(
        self,
    ):
        source = self.review_source()

        assignments = self.assignments(
            source
        )

        assignments[
            "EVIDENCE-UNKNOWN"
        ] = (
            RadarReviewTarget.HUMAN_REVIEW
        )

        with self.assertRaises(
            RadarReviewHandoffInvariantError
        ):
            (
                GovernedRadarReevaluationReviewHandoff
                .handoff(
                    source,
                    assignments=assignments,
                )
            )

    def test_wrong_target_type_fails_closed(
        self,
    ):
        source = self.review_source()

        with self.assertRaises(
            TypeError
        ):
            (
                GovernedRadarReevaluationReviewHandoff
                .handoff(
                    source,
                    assignments={
                        source.evidence_ids[0]:
                        "AY_REVIEW",
                    },
                )
            )

    def test_wrong_source_fails_closed(
        self,
    ):
        with self.assertRaises(
            TypeError
        ):
            (
                GovernedRadarReevaluationReviewHandoff
                .handoff(
                    object(),
                    assignments={},
                )
            )

    def test_wrong_assignments_type_fails_closed(
        self,
    ):
        source = self.review_source()

        with self.assertRaises(
            TypeError
        ):
            (
                GovernedRadarReevaluationReviewHandoff
                .handoff(
                    source,
                    assignments=[],
                )
            )

    def test_exact_coverage_and_order_preserved(
        self,
    ):
        source = self.review_source(
            3
        )

        result = (
            GovernedRadarReevaluationReviewHandoff
            .handoff(
                source,
                assignments=self.assignments(
                    source
                ),
            )
        )

        self.assertEqual(
            result.evidence_ids,
            source.evidence_ids,
        )

        self.assertEqual(
            result.handoff.evidence_ids,
            source.evidence_ids,
        )

        self.assertEqual(
            result.packet_ranks,
            source.packet_ranks,
        )

    def test_payload_and_factor_identity_preserved(
        self,
    ):
        source = self.review_source()

        result = (
            GovernedRadarReevaluationReviewHandoff
            .handoff(
                source,
                assignments=self.assignments(
                    source
                ),
            )
        )

        before = (
            source.entries[0]
            .packet_entry
        )

        after = (
            result.entries[0]
            .handoff_entry
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

    def test_lineage_and_source_rank_preserved(
        self,
    ):
        source = self.review_source(
            2
        )

        result = (
            GovernedRadarReevaluationReviewHandoff
            .handoff(
                source,
                assignments=self.assignments(
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

    def test_no_recomputation_of_prior_boundaries(
        self,
    ):
        source = self.review_source(
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
                GovernedRadarReevaluationReviewPacketMaterializer,
                "materialize",
                side_effect=AssertionError(
                    "SECOND PACKET MATERIALIZATION"
                ),
            ),
        ):
            result = (
                GovernedRadarReevaluationReviewHandoff
                .handoff(
                    source,
                    assignments=self.assignments(
                        source
                    ),
                )
            )

        self.assertEqual(
            result.size,
            2,
        )

    def test_no_response_approval_or_authority(
        self,
    ):
        source = self.review_source()

        result = (
            GovernedRadarReevaluationReviewHandoff
            .handoff(
                source,
                assignments=self.assignments(
                    source,
                    target=(
                        RadarReviewTarget
                        .EX_REVIEW
                    ),
                ),
            )
        )

        self.assertFalse(
            result.review_response_created
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
            result.system_truth_asserted
        )

        for row in result.entries:
            self.assertFalse(
                row.review_response_created
            )

            self.assertFalse(
                row.human_approval_asserted
            )

            self.assertFalse(
                row.ay_validation_asserted
            )

            self.assertFalse(
                row.ex_authorization_asserted
            )

    def test_no_followup_research_network_or_persistence(
        self,
    ):
        source = self.review_source()

        result = (
            GovernedRadarReevaluationReviewHandoff
            .handoff(
                source,
                assignments=self.assignments(
                    source
                ),
            )
        )

        self.assertFalse(
            result.followup_created
        )

        self.assertFalse(
            result.new_research_request_created
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
        source = self.review_source(
            3
        )

        assignments = self.assignments(
            source,
            target=(
                RadarReviewTarget.AY_REVIEW
            ),
        )

        original_entries = source.entries
        original_packet = source.packet
        original_ids = source.evidence_ids
        assignments_before = dict(
            assignments
        )

        first = (
            GovernedRadarReevaluationReviewHandoff
            .handoff(
                source,
                assignments=assignments,
            )
        )

        second = (
            GovernedRadarReevaluationReviewHandoff
            .handoff(
                source,
                assignments=assignments,
            )
        )

        self.assertEqual(
            first,
            second,
        )

        self.assertIs(
            source.entries,
            original_entries,
        )

        self.assertIs(
            source.packet,
            original_packet,
        )

        self.assertEqual(
            source.evidence_ids,
            original_ids,
        )

        self.assertEqual(
            assignments,
            assignments_before,
        )

    def test_static_boundary_is_exact(
        self,
    ):
        path = Path(
            "src/maestro/research/"
            "radar_research_reevaluation_review_handoff.py"
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
            "GovernedRadarReviewHandoff.build",
            calls,
        )

        forbidden_calls = {
            "GovernedRadarReviewResponse.build",
            "GovernedRadarEvaluationPipeline.evaluate",
            "GovernedRadarPortfolio.evaluate",
            "TechnologyRadar.rank",
            "GovernedRadarDecisionEnvelope.evaluate",
            "GovernedRadarEvidenceFollowUp.build",
            "GovernedRadarResearchRequestDraftBuilder.build",
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
            "radar_review_response",
            "radar_evidence_followup",
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
