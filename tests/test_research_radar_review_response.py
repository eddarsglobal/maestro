from __future__ import annotations

import ast
import copy
import unittest

from pathlib import Path

from maestro.research import (
    ContentDigest,
    ExternalArtifact,
    GovernedRadarDecisionEnvelope,
    GovernedRadarPortfolio,
    GovernedRadarReviewHandoff,
    GovernedRadarReviewPacket,
    GovernedRadarReviewResponse,
    GovernedRadarEvaluationPipeline,
    RadarDecisionPolicy,
    RadarPortfolioEntry,
    RadarReviewResponseInvariantError,
    RadarReviewResponseValue,
    RadarReviewTarget,
    ResearchClaim,
    ResearchEvidenceBridge,
    ResearchSource,
    SourceProvenance,
)


class RadarReviewResponseTests(
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
                f"adel013-{suffix}"
            ),
            label=(
                f"ADEL0.13 {suffix}"
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

    def responses(
        self,
        handoff,
        *,
        value=(
            RadarReviewResponseValue
            .RETAIN_REVIEW
        ),
    ):
        return {
            entry.evidence_id: value
            for entry in handoff.entries
        }

    def test_empty_handoff_produces_empty_response(
        self,
    ):
        handoff = self.handoff(
            count=0
        )

        result = (
            GovernedRadarReviewResponse
            .build(
                handoff,
                responses={},
            )
        )

        self.assertEqual(
            result.size,
            0,
        )

    def test_single_response(
        self,
    ):
        handoff = self.handoff()

        result = (
            GovernedRadarReviewResponse
            .build(
                handoff,
                responses=(
                    self.responses(
                        handoff
                    )
                ),
            )
        )

        self.assertEqual(
            result.size,
            1,
        )

    def test_retain_review_response(
        self,
    ):
        handoff = self.handoff()

        result = (
            GovernedRadarReviewResponse
            .build(
                handoff,
                responses=(
                    self.responses(
                        handoff,
                        value=(
                            RadarReviewResponseValue
                            .RETAIN_REVIEW
                        ),
                    )
                ),
            )
        )

        self.assertEqual(
            result.entries[0].response,
            RadarReviewResponseValue.RETAIN_REVIEW,
        )

    def test_request_more_evidence_response(
        self,
    ):
        handoff = self.handoff()

        result = (
            GovernedRadarReviewResponse
            .build(
                handoff,
                responses=(
                    self.responses(
                        handoff,
                        value=(
                            RadarReviewResponseValue
                            .REQUEST_MORE_EVIDENCE
                        ),
                    )
                ),
            )
        )

        self.assertEqual(
            result.entries[0].response,
            (
                RadarReviewResponseValue
                .REQUEST_MORE_EVIDENCE
            ),
        )

    def test_return_to_observe_response(
        self,
    ):
        handoff = self.handoff()

        result = (
            GovernedRadarReviewResponse
            .build(
                handoff,
                responses=(
                    self.responses(
                        handoff,
                        value=(
                            RadarReviewResponseValue
                            .RETURN_TO_OBSERVE
                        ),
                    )
                ),
            )
        )

        self.assertEqual(
            result.entries[0].response,
            (
                RadarReviewResponseValue
                .RETURN_TO_OBSERVE
            ),
        )

    def test_target_is_preserved(
        self,
    ):
        handoff = self.handoff(
            target=(
                RadarReviewTarget
                .AY_REVIEW
            )
        )

        result = (
            GovernedRadarReviewResponse
            .build(
                handoff,
                responses=(
                    self.responses(
                        handoff
                    )
                ),
            )
        )

        self.assertEqual(
            result.entries[0].target,
            RadarReviewTarget.AY_REVIEW,
        )

    def test_handoff_order_is_preserved(
        self,
    ):
        handoff = self.handoff(
            count=3
        )

        result = (
            GovernedRadarReviewResponse
            .build(
                handoff,
                responses=(
                    self.responses(
                        handoff
                    )
                ),
            )
        )

        self.assertEqual(
            result.evidence_ids,
            handoff.evidence_ids,
        )

    def test_evidence_payload_is_preserved(
        self,
    ):
        handoff = self.handoff()

        result = (
            GovernedRadarReviewResponse
            .build(
                handoff,
                responses=(
                    self.responses(
                        handoff
                    )
                ),
            )
        )

        before = handoff.entries[0]
        after = result.entries[0]

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

    def test_unverified_boundary_preserved(
        self,
    ):
        handoff = self.handoff()

        result = (
            GovernedRadarReviewResponse
            .build(
                handoff,
                responses=(
                    self.responses(
                        handoff
                    )
                ),
            )
        )

        row = result.entries[0]

        self.assertEqual(
            row.verification_status,
            "UNVERIFIED_EXTERNAL",
        )
        self.assertFalse(
            row.system_truth_asserted
        )

    def test_no_authority_is_asserted(
        self,
    ):
        handoff = self.handoff(
            target=(
                RadarReviewTarget
                .EX_REVIEW
            )
        )

        result = (
            GovernedRadarReviewResponse
            .build(
                handoff,
                responses=(
                    self.responses(
                        handoff
                    )
                ),
            )
        )

        row = result.entries[0]

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

    def test_response_is_deterministic(
        self,
    ):
        handoff = self.handoff(
            count=2
        )

        responses = self.responses(
            handoff,
            value=(
                RadarReviewResponseValue
                .REQUEST_MORE_EVIDENCE
            ),
        )

        first = (
            GovernedRadarReviewResponse
            .build(
                handoff,
                responses=responses,
            )
        )

        second = (
            GovernedRadarReviewResponse
            .build(
                handoff,
                responses=responses,
            )
        )

        self.assertEqual(
            first,
            second,
        )

    def test_wrong_handoff_type_rejected(
        self,
    ):
        with self.assertRaises(
            TypeError
        ):
            (
                GovernedRadarReviewResponse
                .build(
                    object(),
                    responses={},
                )
            )

    def test_wrong_responses_type_rejected(
        self,
    ):
        handoff = self.handoff()

        with self.assertRaises(
            TypeError
        ):
            (
                GovernedRadarReviewResponse
                .build(
                    handoff,
                    responses=[],
                )
            )

    def test_wrong_response_value_rejected(
        self,
    ):
        handoff = self.handoff()

        evidence_id = (
            handoff.entries[0]
            .evidence_id
        )

        with self.assertRaises(
            TypeError
        ):
            (
                GovernedRadarReviewResponse
                .build(
                    handoff,
                    responses={
                        evidence_id: "APPROVED"
                    },
                )
            )

    def test_missing_response_fails_closed(
        self,
    ):
        handoff = self.handoff()

        with self.assertRaises(
            RadarReviewResponseInvariantError
        ):
            (
                GovernedRadarReviewResponse
                .build(
                    handoff,
                    responses={},
                )
            )

    def test_extra_response_fails_closed(
        self,
    ):
        handoff = self.handoff()

        responses = self.responses(
            handoff
        )

        responses[
            "EVIDENCE-UNKNOWN"
        ] = (
            RadarReviewResponseValue
            .RETAIN_REVIEW
        )

        with self.assertRaises(
            RadarReviewResponseInvariantError
        ):
            (
                GovernedRadarReviewResponse
                .build(
                    handoff,
                    responses=responses,
                )
            )

    def test_inputs_are_not_mutated(
        self,
    ):
        handoff = self.handoff()

        responses = self.responses(
            handoff
        )

        handoff_before = copy.deepcopy(
            handoff
        )
        responses_before = dict(
            responses
        )

        (
            GovernedRadarReviewResponse
            .build(
                handoff,
                responses=responses,
            )
        )

        self.assertEqual(
            handoff,
            handoff_before,
        )
        self.assertEqual(
            responses,
            responses_before,
        )

    def test_module_has_no_governance_promotion_activation_or_queue_imports(
        self,
    ):
        path = Path(
            "src/maestro/research/"
            "radar_review_response.py"
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
