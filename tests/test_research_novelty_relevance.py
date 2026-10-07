from __future__ import annotations

import ast
import copy
import unittest

from datetime import (
    datetime,
    timezone,
)
from pathlib import Path

from maestro.enums import CouncilId
from maestro.research import (
    ContentDigest,
    ExternalArtifact,
    NoveltyRelevanceEvaluator,
    NoveltyRelevanceInvariantError,
    RadarFactors,
    ResearchClaim,
    ResearchEvidenceBridge,
    ResearchSource,
    SourceProvenance,
    TechnologyRadarInvariantError,
)


class NoveltyRelevanceTests(
    unittest.TestCase
):
    def evidence(
        self,
        statement=(
            "Local inference engine improves "
            "MAESTRO research capability"
        ),
    ):
        now = datetime.now(
            timezone.utc
        ).isoformat()

        source = ResearchSource(
            "https://example.com/"
            "adel03-source",
            label="ADEL0.3 source",
        )

        provenance = SourceProvenance(
            source_id=source.source_id,
            retrieved_at=now,
            digest=ContentDigest.from_bytes(
                statement.encode("utf-8")
            ),
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

    def factors(
        self,
    ):
        return RadarFactors(
            novelty=0.10,
            source_quality=0.80,
            relevance_to_maestro=0.20,
            expected_capability_gain=0.70,
            reproducibility=0.60,
            integration_cost=0.30,
            security_risk=0.10,
        )

    def test_unseen_evidence_has_maximum_novelty(
        self,
    ):
        result = (
            NoveltyRelevanceEvaluator
            .evaluate(
                self.evidence(),
            )
        )

        self.assertEqual(
            result.novelty,
            1.0,
        )

        self.assertFalse(
            result.exact_match
        )

    def test_identical_claim_has_zero_novelty(
        self,
    ):
        evidence = self.evidence()

        result = (
            NoveltyRelevanceEvaluator
            .evaluate(
                evidence,
                known_claims=[
                    evidence.claim
                ],
            )
        )

        self.assertEqual(
            result.novelty,
            0.0,
        )

        self.assertTrue(
            result.exact_match
        )

        self.assertEqual(
            result.max_known_similarity,
            1.0,
        )

    def test_partial_overlap_produces_intermediate_novelty(
        self,
    ):
        result = (
            NoveltyRelevanceEvaluator
            .evaluate(
                self.evidence(),
                known_claims=[
                    "Local inference engine"
                ],
            )
        )

        self.assertGreater(
            result.novelty,
            0.0,
        )

        self.assertLess(
            result.novelty,
            1.0,
        )

    def test_evaluation_is_deterministic(
        self,
    ):
        evidence = self.evidence()

        first = (
            NoveltyRelevanceEvaluator
            .evaluate(
                evidence,
                known_claims=[
                    "Local inference engine"
                ],
                relevance_terms=[
                    "MAESTRO",
                    "research",
                    "capability",
                ],
            )
        )

        second = (
            NoveltyRelevanceEvaluator
            .evaluate(
                evidence,
                known_claims=[
                    "Local inference engine"
                ],
                relevance_terms=[
                    "MAESTRO",
                    "research",
                    "capability",
                ],
            )
        )

        self.assertEqual(
            first,
            second,
        )

    def test_relevant_terms_increase_relevance(
        self,
    ):
        result = (
            NoveltyRelevanceEvaluator
            .evaluate(
                self.evidence(),
                relevance_terms=[
                    "MAESTRO",
                    "research",
                    "capability",
                ],
            )
        )

        self.assertEqual(
            result.relevance_to_maestro,
            1.0,
        )

        self.assertEqual(
            result.matched_relevance_terms,
            (
                "capability",
                "maestro",
                "research",
            ),
        )

    def test_unrelated_context_is_zero_relevance(
        self,
    ):
        result = (
            NoveltyRelevanceEvaluator
            .evaluate(
                self.evidence(),
                relevance_terms=[
                    "agriculture",
                    "marine",
                ],
            )
        )

        self.assertEqual(
            result.relevance_to_maestro,
            0.0,
        )

    def test_missing_context_is_unknown_not_irrelevant(
        self,
    ):
        result = (
            NoveltyRelevanceEvaluator
            .evaluate(
                self.evidence(),
            )
        )

        self.assertIsNone(
            result.relevance_to_maestro
        )

        self.assertFalse(
            result.relevance_known
        )

    def test_scores_remain_bounded(
        self,
    ):
        result = (
            NoveltyRelevanceEvaluator
            .evaluate(
                self.evidence(),
                known_claims=[
                    "unrelated observation",
                    "Local inference engine",
                ],
                relevance_terms=[
                    "MAESTRO",
                    "research",
                    "unknown",
                ],
            )
        )

        self.assertGreaterEqual(
            result.novelty,
            0.0,
        )

        self.assertLessEqual(
            result.novelty,
            1.0,
        )

        self.assertIsNotNone(
            result.relevance_to_maestro
        )

        self.assertGreaterEqual(
            result.relevance_to_maestro,
            0.0,
        )

        self.assertLessEqual(
            result.relevance_to_maestro,
            1.0,
        )

    def test_unverified_boundary_is_preserved(
        self,
    ):
        result = (
            NoveltyRelevanceEvaluator
            .evaluate(
                self.evidence(),
                relevance_terms=[
                    "MAESTRO"
                ],
            )
        )

        self.assertEqual(
            result.verification_status,
            "UNVERIFIED_EXTERNAL",
        )

        self.assertFalse(
            result.system_truth_asserted
        )

    def test_evaluation_does_not_mutate_evidence(
        self,
    ):
        evidence = self.evidence()

        original = copy.deepcopy(
            evidence
        )

        NoveltyRelevanceEvaluator.evaluate(
            evidence,
            known_claims=[
                "Local inference"
            ],
            relevance_terms=[
                "MAESTRO"
            ],
        )

        self.assertEqual(
            evidence,
            original,
        )

    def test_evaluation_can_replace_only_radar_interest_factors(
        self,
    ):
        result = (
            NoveltyRelevanceEvaluator
            .evaluate(
                self.evidence(),
                known_claims=[
                    "Local inference engine"
                ],
                relevance_terms=[
                    "MAESTRO",
                    "research",
                ],
            )
        )

        before = self.factors()

        after = result.apply_to_factors(
            before
        )

        self.assertEqual(
            after.novelty,
            result.novelty,
        )

        self.assertEqual(
            after.relevance_to_maestro,
            result.relevance_to_maestro,
        )

        self.assertEqual(
            after.source_quality,
            before.source_quality,
        )

        self.assertEqual(
            after.expected_capability_gain,
            before.expected_capability_gain,
        )

        self.assertEqual(
            after.reproducibility,
            before.reproducibility,
        )

        self.assertEqual(
            after.integration_cost,
            before.integration_cost,
        )

        self.assertEqual(
            after.security_risk,
            before.security_risk,
        )

    def test_unknown_relevance_cannot_be_silently_promoted_to_factor(
        self,
    ):
        result = (
            NoveltyRelevanceEvaluator
            .evaluate(
                self.evidence()
            )
        )

        with self.assertRaises(
            NoveltyRelevanceInvariantError
        ):
            result.apply_to_factors(
                self.factors()
            )

    def test_non_rx_evidence_is_rejected(
        self,
    ):
        evidence = self.evidence()
        evidence.council = CouncilId.IT

        with self.assertRaises(
            TechnologyRadarInvariantError
        ):
            (
                NoveltyRelevanceEvaluator
                .evaluate(
                    evidence
                )
            )

    def test_high_interest_never_asserts_truth(
        self,
    ):
        evidence = self.evidence()

        result = (
            NoveltyRelevanceEvaluator
            .evaluate(
                evidence,
                relevance_terms=[
                    "Local",
                    "inference",
                    "engine",
                    "improves",
                    "MAESTRO",
                    "research",
                    "capability",
                ],
            )
        )

        self.assertEqual(
            result.novelty,
            1.0,
        )

        self.assertEqual(
            result.relevance_to_maestro,
            1.0,
        )

        self.assertFalse(
            result.system_truth_asserted
        )

        self.assertEqual(
            result.verification_status,
            "UNVERIFIED_EXTERNAL",
        )

    def test_module_has_no_network_learning_or_activation_imports(
        self,
    ):
        path = Path(
            "src/maestro/research/"
            "novelty_relevance.py"
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
            (
                "maestro."
                "outcome_governed_adaptation"
            ),
            (
                "maestro."
                "governed_activation"
            ),
            "maestro.tools",
            "maestro.autonomous",
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
