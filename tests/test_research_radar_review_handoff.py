from __future__ import annotations

import ast
import copy
import unittest

from datetime import (
    datetime,
    timezone,
)
from pathlib import Path

from maestro.research import (
    ContentDigest,
    ExternalArtifact,
    GovernedRadarDecisionEnvelope,
    GovernedRadarEvaluationPipeline,
    GovernedRadarPortfolio,
    GovernedRadarReviewHandoff,
    GovernedRadarReviewPacket,
    RadarDecisionPolicy,
    RadarDisposition,
    RadarPortfolioEntry,
    RadarReviewHandoffInvariantError,
    RadarReviewTarget,
    ResearchClaim,
    ResearchEvidenceBridge,
    ResearchSource,
    SourceProvenance,
)


class RadarReviewHandoffTests(
    unittest.TestCase
):
    def evidence(
        self,
        *,
        statement: str,
        suffix: str,
    ):
        now = datetime.now(
            timezone.utc
        ).isoformat()

        source = ResearchSource(
            (
                "https://example.com/"
                f"adel012-{suffix}"
            ),
            label=(
                f"ADEL0.12 {suffix}"
            ),
        )

        provenance = SourceProvenance(
            source_id=source.source_id,
            retrieved_at=now,
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
            created_at=now,
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
        *,
        risk_signals=(
            "network",
        ),
        mitigations=(),
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
                risk_signals=risk_signals,
                mitigations=mitigations,
            )
        )

    def entry(
        self,
        *,
        suffix: str,
    ):
        return RadarPortfolioEntry(
            evidence=self.evidence(
                statement=(
                    "GPU reasoning improves "
                    "MAESTRO research"
                ),
                suffix=suffix,
            ),
            context=self.context(),
        )

    def packet(
        self,
        *,
        count=1,
        review=True,
    ):
        portfolio = (
            GovernedRadarPortfolio()
            .evaluate(
                tuple(
                    self.entry(
                        suffix=str(index)
                    )
                    for index
                    in range(count)
                )
            )
        )

        policy = (
            RadarDecisionPolicy(
                investigate_min_priority=0.0,
                review_min_priority=0.0,
            )
            if review
            else RadarDecisionPolicy(
                investigate_min_priority=0.0,
                review_min_priority=1.0,
            )
        )

        envelope = (
            GovernedRadarDecisionEnvelope
            .evaluate(
                portfolio,
                policy=policy,
            )
        )

        return (
            GovernedRadarReviewPacket
            .build(
                portfolio,
                envelope,
                policy=policy,
            )
        )

    def assignments(
        self,
        packet,
        *,
        target=RadarReviewTarget.HUMAN_REVIEW,
    ):
        return {
            entry.evidence_id: target
            for entry in packet.entries
            if (
                entry.disposition
                is RadarDisposition.REVIEW
            )
        }

    def test_empty_packet_produces_empty_handoff(
        self,
    ):
        packet = self.packet(
            count=0
        )

        result = (
            GovernedRadarReviewHandoff
            .build(
                packet,
                assignments={},
            )
        )

        self.assertEqual(
            result.size,
            0,
        )

    def test_review_entry_is_handed_off(
        self,
    ):
        packet = self.packet()

        result = (
            GovernedRadarReviewHandoff
            .build(
                packet,
                assignments=(
                    self.assignments(
                        packet
                    )
                ),
            )
        )

        self.assertEqual(
            result.size,
            1,
        )

        self.assertEqual(
            result.entries[0].disposition,
            RadarDisposition.REVIEW,
        )

    def test_non_review_entry_is_not_handed_off(
        self,
    ):
        packet = self.packet(
            review=False
        )

        result = (
            GovernedRadarReviewHandoff
            .build(
                packet,
                assignments={},
            )
        )

        self.assertEqual(
            result.size,
            0,
        )

    def test_human_target(
        self,
    ):
        packet = self.packet()

        result = (
            GovernedRadarReviewHandoff
            .build(
                packet,
                assignments=(
                    self.assignments(
                        packet,
                        target=(
                            RadarReviewTarget
                            .HUMAN_REVIEW
                        ),
                    )
                ),
            )
        )

        self.assertEqual(
            result.entries[0].target,
            RadarReviewTarget.HUMAN_REVIEW,
        )

    def test_ay_target(
        self,
    ):
        packet = self.packet()

        result = (
            GovernedRadarReviewHandoff
            .build(
                packet,
                assignments=(
                    self.assignments(
                        packet,
                        target=(
                            RadarReviewTarget
                            .AY_REVIEW
                        ),
                    )
                ),
            )
        )

        self.assertEqual(
            result.entries[0].target,
            RadarReviewTarget.AY_REVIEW,
        )

    def test_ex_target(
        self,
    ):
        packet = self.packet()

        result = (
            GovernedRadarReviewHandoff
            .build(
                packet,
                assignments=(
                    self.assignments(
                        packet,
                        target=(
                            RadarReviewTarget
                            .EX_REVIEW
                        ),
                    )
                ),
            )
        )

        self.assertEqual(
            result.entries[0].target,
            RadarReviewTarget.EX_REVIEW,
        )

    def test_missing_assignment_fails_closed(
        self,
    ):
        packet = self.packet()

        with self.assertRaises(
            RadarReviewHandoffInvariantError
        ):
            (
                GovernedRadarReviewHandoff
                .build(
                    packet,
                    assignments={},
                )
            )

    def test_extra_assignment_fails_closed(
        self,
    ):
        packet = self.packet()

        assignments = (
            self.assignments(
                packet
            )
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
                GovernedRadarReviewHandoff
                .build(
                    packet,
                    assignments=assignments,
                )
            )

    def test_wrong_target_type_rejected(
        self,
    ):
        packet = self.packet()

        evidence_id = (
            packet.entries[0]
            .evidence_id
        )

        with self.assertRaises(
            TypeError
        ):
            (
                GovernedRadarReviewHandoff
                .build(
                    packet,
                    assignments={
                        evidence_id: "AY"
                    },
                )
            )

    def test_wrong_packet_type_rejected(
        self,
    ):
        with self.assertRaises(
            TypeError
        ):
            (
                GovernedRadarReviewHandoff
                .build(
                    object(),
                    assignments={},
                )
            )

    def test_wrong_assignments_type_rejected(
        self,
    ):
        packet = self.packet()

        with self.assertRaises(
            TypeError
        ):
            (
                GovernedRadarReviewHandoff
                .build(
                    packet,
                    assignments=[],
                )
            )

    def test_packet_order_is_preserved(
        self,
    ):
        packet = self.packet(
            count=3
        )

        result = (
            GovernedRadarReviewHandoff
            .build(
                packet,
                assignments=(
                    self.assignments(
                        packet
                    )
                ),
            )
        )

        expected = tuple(
            entry.evidence_id
            for entry in packet.entries
        )

        self.assertEqual(
            result.evidence_ids,
            expected,
        )

    def test_evidence_payload_is_preserved(
        self,
    ):
        packet = self.packet()

        result = (
            GovernedRadarReviewHandoff
            .build(
                packet,
                assignments=(
                    self.assignments(
                        packet
                    )
                ),
            )
        )

        before = packet.entries[0]
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
        packet = self.packet()

        result = (
            GovernedRadarReviewHandoff
            .build(
                packet,
                assignments=(
                    self.assignments(
                        packet
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
        packet = self.packet()

        result = (
            GovernedRadarReviewHandoff
            .build(
                packet,
                assignments=(
                    self.assignments(
                        packet,
                        target=(
                            RadarReviewTarget
                            .EX_REVIEW
                        ),
                    )
                ),
            )
        )

        row = result.entries[0]

        self.assertFalse(
            row.authorization_asserted
        )
        self.assertFalse(
            row.activation_asserted
        )
        self.assertFalse(
            row.execution_asserted
        )

    def test_handoff_is_deterministic(
        self,
    ):
        packet = self.packet(
            count=2
        )

        assignments = (
            self.assignments(
                packet,
                target=(
                    RadarReviewTarget
                    .AY_REVIEW
                ),
            )
        )

        first = (
            GovernedRadarReviewHandoff
            .build(
                packet,
                assignments=assignments,
            )
        )

        second = (
            GovernedRadarReviewHandoff
            .build(
                packet,
                assignments=assignments,
            )
        )

        self.assertEqual(
            first,
            second,
        )

    def test_inputs_are_not_mutated(
        self,
    ):
        packet = self.packet()

        assignments = (
            self.assignments(
                packet
            )
        )

        packet_before = copy.deepcopy(
            packet
        )
        assignments_before = dict(
            assignments
        )

        (
            GovernedRadarReviewHandoff
            .build(
                packet,
                assignments=assignments,
            )
        )

        self.assertEqual(
            packet,
            packet_before,
        )

        self.assertEqual(
            assignments,
            assignments_before,
        )

    def test_module_has_no_governance_activation_queue_or_learning_imports(
        self,
    ):
        path = Path(
            "src/maestro/research/"
            "radar_review_handoff.py"
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
