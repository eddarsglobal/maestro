from __future__ import annotations

import ast
import unittest

from pathlib import Path
from unittest.mock import patch

import test_research_radar_research_reevaluation_evidence_followup as adel031_tests

from maestro.research import (
    GovernedRadarDecisionEnvelope,
    GovernedRadarEvidenceFollowUp,
    GovernedRadarEvaluationPipeline,
    GovernedRadarFollowUpCandidateBuilder,
    GovernedRadarReevaluationEvidenceFollowUp,
    GovernedRadarReevaluationFollowUpCandidate,
    RadarReviewResponseValue,
    RadarReviewTarget,
    ResearchCapability,
    TechnologyRadar,
)
from maestro.research.radar_research_request_draft import (
    GovernedRadarResearchRequestDraftBuilder,
)


class RadarReevaluationFollowUpCandidateTests(
    unittest.TestCase
):
    def fixture(
        self,
    ):
        return (
            adel031_tests
            .RadarReevaluationEvidenceFollowUpTests()
        )

    def followup_source(
        self,
        values,
        *,
        target=RadarReviewTarget.HUMAN_REVIEW,
    ):
        fixture = self.fixture()

        response = fixture.response_source(
            values,
            target=target,
        )

        return (
            GovernedRadarReevaluationEvidenceFollowUp
            .build(
                response
            )
        )

    def no_followup_source(
        self,
    ):
        fixture = self.fixture()

        response = fixture.no_response_source()

        return (
            GovernedRadarReevaluationEvidenceFollowUp
            .build(
                response
            )
        )

    def test_no_followup_creates_no_candidate_set(
        self,
    ):
        source = self.no_followup_source()

        with patch.object(
            GovernedRadarFollowUpCandidateBuilder,
            "build",
            side_effect=AssertionError(
                "ADEL0.15 BUILDER MUST NOT RUN"
            ),
        ):
            result = (
                GovernedRadarReevaluationFollowUpCandidate
                .build(
                    source
                )
            )

        self.assertIsNone(
            result.candidates
        )

        self.assertFalse(
            result.candidate_set_materialized
        )

        self.assertFalse(
            result.followup_candidate_created
        )

        self.assertEqual(
            result.size,
            0,
        )

    def test_empty_followup_materializes_empty_candidate_set(
        self,
    ):
        source = self.followup_source(
            (
                RadarReviewResponseValue
                .RETAIN_REVIEW,
            )
        )

        self.assertIsNotNone(
            source.followup
        )

        self.assertEqual(
            source.size,
            0,
        )

        result = (
            GovernedRadarReevaluationFollowUpCandidate
            .build(
                source
            )
        )

        self.assertTrue(
            result.candidate_set_materialized
        )

        self.assertFalse(
            result.followup_candidate_created
        )

        self.assertFalse(
            result.query_preparation_performed
        )

        self.assertEqual(
            result.size,
            0,
        )

    def test_need_creates_candidate(
        self,
    ):
        source = self.followup_source(
            (
                RadarReviewResponseValue
                .REQUEST_MORE_EVIDENCE,
            )
        )

        result = (
            GovernedRadarReevaluationFollowUpCandidate
            .build(
                source
            )
        )

        self.assertTrue(
            result.candidate_set_materialized
        )

        self.assertTrue(
            result.followup_candidate_created
        )

        self.assertTrue(
            result.query_preparation_performed
        )

        self.assertEqual(
            result.size,
            1,
        )

    def test_existing_adel015_builder_is_reused(
        self,
    ):
        source = self.followup_source(
            (
                RadarReviewResponseValue
                .REQUEST_MORE_EVIDENCE,
            )
        )

        original = (
            GovernedRadarFollowUpCandidateBuilder
            .build
        )

        with patch.object(
            GovernedRadarFollowUpCandidateBuilder,
            "build",
            wraps=original,
        ) as mocked:
            result = (
                GovernedRadarReevaluationFollowUpCandidate
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

    def test_capability_is_search(
        self,
    ):
        source = self.followup_source(
            (
                RadarReviewResponseValue
                .REQUEST_MORE_EVIDENCE,
            )
        )

        result = (
            GovernedRadarReevaluationFollowUpCandidate
            .build(
                source
            )
        )

        self.assertIs(
            result.entries[0].capability,
            ResearchCapability.SEARCH,
        )

    def test_query_contains_claim(
        self,
    ):
        source = self.followup_source(
            (
                RadarReviewResponseValue
                .REQUEST_MORE_EVIDENCE,
            )
        )

        result = (
            GovernedRadarReevaluationFollowUpCandidate
            .build(
                source
            )
        )

        self.assertIn(
            source.entries[0].need.claim,
            result.entries[0].query,
        )

        self.assertTrue(
            result.entries[0].query_prepared
        )

        self.assertFalse(
            result.entries[0]
            .research_request_created
        )

    def test_preferred_local_is_preserved(
        self,
    ):
        source = self.followup_source(
            (
                RadarReviewResponseValue
                .REQUEST_MORE_EVIDENCE,
            )
        )

        result = (
            GovernedRadarReevaluationFollowUpCandidate
            .build(
                source
            )
        )

        self.assertTrue(
            result.entries[0].preferred_local
        )

    def test_exact_order_ids_and_ranks_preserved(
        self,
    ):
        source = self.followup_source(
            (
                RadarReviewResponseValue
                .REQUEST_MORE_EVIDENCE,
                RadarReviewResponseValue
                .REQUEST_MORE_EVIDENCE,
                RadarReviewResponseValue
                .REQUEST_MORE_EVIDENCE,
            )
        )

        result = (
            GovernedRadarReevaluationFollowUpCandidate
            .build(
                source
            )
        )

        self.assertEqual(
            result.evidence_ids,
            source.evidence_ids,
        )

        self.assertEqual(
            tuple(
                entry.followup_rank
                for entry in result.entries
            ),
            tuple(
                entry.need.rank
                for entry in source.entries
            ),
        )

    def test_payload_factor_target_identity_preserved(
        self,
    ):
        source = self.followup_source(
            (
                RadarReviewResponseValue
                .REQUEST_MORE_EVIDENCE,
            ),
            target=RadarReviewTarget.AY_REVIEW,
        )

        result = (
            GovernedRadarReevaluationFollowUpCandidate
            .build(
                source
            )
        )

        before = source.entries[0].need
        after = result.entries[0].candidate

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
        source = self.followup_source(
            (
                RadarReviewResponseValue
                .REQUEST_MORE_EVIDENCE,
                RadarReviewResponseValue
                .REQUEST_MORE_EVIDENCE,
            )
        )

        result = (
            GovernedRadarReevaluationFollowUpCandidate
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
                after.origin_task_id,
                before.task_id,
            )

            self.assertFalse(
                after.new_task_id_bound
            )

    def test_human_target_has_no_approval(
        self,
    ):
        source = self.followup_source(
            (
                RadarReviewResponseValue
                .REQUEST_MORE_EVIDENCE,
            ),
            target=(
                RadarReviewTarget.HUMAN_REVIEW
            ),
        )

        result = (
            GovernedRadarReevaluationFollowUpCandidate
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
        source = self.followup_source(
            (
                RadarReviewResponseValue
                .REQUEST_MORE_EVIDENCE,
            ),
            target=RadarReviewTarget.AY_REVIEW,
        )

        result = (
            GovernedRadarReevaluationFollowUpCandidate
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
        source = self.followup_source(
            (
                RadarReviewResponseValue
                .REQUEST_MORE_EVIDENCE,
            ),
            target=RadarReviewTarget.EX_REVIEW,
        )

        result = (
            GovernedRadarReevaluationFollowUpCandidate
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

    def test_no_draft_request_binding_or_side_effects(
        self,
    ):
        source = self.followup_source(
            (
                RadarReviewResponseValue
                .REQUEST_MORE_EVIDENCE,
            )
        )

        with (
            patch.object(
                GovernedRadarResearchRequestDraftBuilder,
                "build",
                side_effect=AssertionError(
                    "RESEARCH REQUEST DRAFT CREATED"
                ),
            ),
            patch.object(
                GovernedRadarEvidenceFollowUp,
                "build",
                side_effect=AssertionError(
                    "SECOND FOLLOW-UP BUILD"
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
                GovernedRadarReevaluationFollowUpCandidate
                .build(
                    source
                )
            )

        self.assertFalse(
            result.research_request_draft_created
        )

        self.assertFalse(
            result.new_task_id_bound
        )

        self.assertFalse(
            result.research_request_created
        )

        self.assertFalse(
            result.provider_selected
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

    def test_passive_truth_authority_boundary(
        self,
    ):
        source = self.followup_source(
            (
                RadarReviewResponseValue
                .REQUEST_MORE_EVIDENCE,
            ),
            target=RadarReviewTarget.EX_REVIEW,
        )

        result = (
            GovernedRadarReevaluationFollowUpCandidate
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

        self.assertFalse(
            result.skill_creation_requested
        )

    def test_wrong_source_fails_closed(
        self,
    ):
        with self.assertRaises(
            TypeError
        ):
            (
                GovernedRadarReevaluationFollowUpCandidate
                .build(
                    object()
                )
            )

    def test_deterministic_and_source_unchanged(
        self,
    ):
        source = self.followup_source(
            (
                RadarReviewResponseValue
                .REQUEST_MORE_EVIDENCE,
                RadarReviewResponseValue
                .REQUEST_MORE_EVIDENCE,
            )
        )

        source_entries = source.entries
        source_followup = source.followup
        source_ids = source.evidence_ids

        first = (
            GovernedRadarReevaluationFollowUpCandidate
            .build(
                source
            )
        )

        second = (
            GovernedRadarReevaluationFollowUpCandidate
            .build(
                source
            )
        )

        self.assertEqual(
            first,
            second,
        )

        self.assertEqual(
            first.queries,
            second.queries,
        )

        self.assertIs(
            source.entries,
            source_entries,
        )

        self.assertIs(
            source.followup,
            source_followup,
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
            "radar_research_reevaluation_followup_candidate.py"
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
            "GovernedRadarFollowUpCandidateBuilder.build",
            calls,
        )

        forbidden_calls = {
            "GovernedRadarEvidenceFollowUp.build",
            "GovernedRadarResearchRequestDraftBuilder.build",
            "GovernedRadarResearchTaskBinder.bind",
            "GovernedRadarResearchRequestMaterializer.materialize",
            "GovernedRadarEvaluationPipeline.evaluate",
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
            "radar_research_request_draft",
            "radar_research_task_binding",
            "radar_research_request_materialization",
            "radar_research_routing",
            "durable_store",
            "runtime",
            "web_fetch",
            "transport",
        )

        for imported in imported_modules:
            for fragment in forbidden_modules:
                self.assertNotIn(
                    fragment,
                    imported,
                )


if __name__ == "__main__":
    unittest.main()
