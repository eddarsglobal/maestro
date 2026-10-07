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
    GovernedRadarEvaluationPipeline,
    GovernedRadarPortfolio,
    RadarPortfolioEntry,
    RadarPortfolioInvariantError,
    ResearchClaim,
    ResearchEvidenceBridge,
    ResearchSource,
    SourceProvenance,
)


class RadarPortfolioTests(
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
                f"adel09-{suffix}"
            ),
            label=(
                f"ADEL0.9 {suffix}"
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
        relevance_terms=(
            "MAESTRO",
            "research",
        ),
        capability_terms=(
            "GPU",
            "reasoning",
        ),
        risk_signals=(
            "network",
            "execution",
        ),
        mitigations=(
            "network",
        ),
    ):
        return (
            GovernedRadarEvaluationPipeline
            .context(
                known_claims=[
                    "legacy baseline"
                ],
                relevance_terms=(
                    relevance_terms
                ),
                capability_terms=(
                    capability_terms
                ),
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
                risk_signals=(
                    risk_signals
                ),
                mitigations=(
                    mitigations
                ),
            )
        )

    def entry(
        self,
        *,
        statement: str,
        suffix: str,
        context=None,
    ):
        return RadarPortfolioEntry(
            evidence=self.evidence(
                statement=statement,
                suffix=suffix,
            ),
            context=(
                context
                if context is not None
                else self.context()
            ),
        )

    def test_empty_portfolio_is_valid(
        self,
    ):
        result = (
            GovernedRadarPortfolio()
            .evaluate(())
        )

        self.assertEqual(
            result.size,
            0,
        )

        self.assertEqual(
            result.ranked_observations,
            (),
        )

    def test_single_entry_is_evaluated(
        self,
    ):
        entry = self.entry(
            statement=(
                "GPU reasoning improves "
                "MAESTRO research"
            ),
            suffix="one",
        )

        result = (
            GovernedRadarPortfolio()
            .evaluate([entry])
        )

        self.assertEqual(
            result.size,
            1,
        )

        self.assertEqual(
            result.ranked_evidence_ids,
            (
                entry.evidence.evidence_id,
            ),
        )

    def test_multiple_entries_are_evaluated(
        self,
    ):
        entries = (
            self.entry(
                statement=(
                    "GPU reasoning improves "
                    "MAESTRO research"
                ),
                suffix="one",
            ),
            self.entry(
                statement=(
                    "GPU reasoning runtime "
                    "supports MAESTRO research"
                ),
                suffix="two",
            ),
        )

        result = (
            GovernedRadarPortfolio()
            .evaluate(entries)
        )

        self.assertEqual(
            result.size,
            2,
        )

        self.assertEqual(
            len(
                result.ranked_observations
            ),
            2,
        )

    def test_ranking_is_priority_descending(
        self,
    ):
        high = self.entry(
            statement=(
                "GPU reasoning MAESTRO "
                "research"
            ),
            suffix="high",
            context=self.context(
                risk_signals=(
                    "network",
                ),
                mitigations=(
                    "network",
                ),
            ),
        )

        low = self.entry(
            statement=(
                "GPU reasoning MAESTRO "
                "research"
            ),
            suffix="low",
            context=self.context(
                risk_signals=(
                    "network",
                ),
                mitigations=(),
            ),
        )

        result = (
            GovernedRadarPortfolio()
            .evaluate(
                (
                    low,
                    high,
                )
            )
        )

        self.assertGreaterEqual(
            result.ranked_observations[0]
            .priority_score,
            result.ranked_observations[1]
            .priority_score,
        )

    def test_tie_break_is_evidence_id(
        self,
    ):
        first = self.entry(
            statement=(
                "GPU reasoning improves "
                "MAESTRO research"
            ),
            suffix="a",
        )

        second = self.entry(
            statement=(
                "GPU reasoning improves "
                "MAESTRO research"
            ),
            suffix="b",
        )

        result = (
            GovernedRadarPortfolio()
            .evaluate(
                (
                    second,
                    first,
                )
            )
        )

        expected = tuple(
            sorted(
                (
                    first.evidence.evidence_id,
                    second.evidence.evidence_id,
                )
            )
        )

        self.assertEqual(
            result.ranked_evidence_ids,
            expected,
        )

    def test_duplicate_evidence_ids_fail_closed(
        self,
    ):
        entry = self.entry(
            statement=(
                "GPU reasoning improves "
                "MAESTRO research"
            ),
            suffix="dup",
        )

        with self.assertRaises(
            RadarPortfolioInvariantError
        ):
            (
                GovernedRadarPortfolio()
                .evaluate(
                    (
                        entry,
                        entry,
                    )
                )
            )

    def test_wrong_entry_type_is_rejected(
        self,
    ):
        with self.assertRaises(
            TypeError
        ):
            (
                GovernedRadarPortfolio()
                .evaluate(
                    (
                        object(),
                    )
                )
            )

    def test_string_entries_are_rejected(
        self,
    ):
        with self.assertRaises(
            TypeError
        ):
            (
                GovernedRadarPortfolio()
                .evaluate(
                    "invalid"
                )
            )

    def test_entry_requires_evidence(
        self,
    ):
        with self.assertRaises(
            TypeError
        ):
            RadarPortfolioEntry(
                evidence=object(),
                context=self.context(),
            )

    def test_entry_requires_context(
        self,
    ):
        evidence = self.evidence(
            statement=(
                "GPU reasoning improves "
                "MAESTRO research"
            ),
            suffix="context",
        )

        with self.assertRaises(
            TypeError
        ):
            RadarPortfolioEntry(
                evidence=evidence,
                context=object(),
            )

    def test_portfolio_is_deterministic(
        self,
    ):
        entries = (
            self.entry(
                statement=(
                    "GPU reasoning improves "
                    "MAESTRO research"
                ),
                suffix="one",
            ),
            self.entry(
                statement=(
                    "GPU runtime improves "
                    "MAESTRO research"
                ),
                suffix="two",
            ),
        )

        portfolio = (
            GovernedRadarPortfolio()
        )

        first = portfolio.evaluate(
            entries
        )

        second = portfolio.evaluate(
            entries
        )

        self.assertEqual(
            first,
            second,
        )

    def test_portfolio_does_not_mutate_evidence(
        self,
    ):
        entry = self.entry(
            statement=(
                "GPU reasoning improves "
                "MAESTRO research"
            ),
            suffix="immutable",
        )

        original = copy.deepcopy(
            entry.evidence
        )

        (
            GovernedRadarPortfolio()
            .evaluate([entry])
        )

        self.assertEqual(
            entry.evidence,
            original,
        )

    def test_ranked_observations_preserve_unverified_boundary(
        self,
    ):
        result = (
            GovernedRadarPortfolio()
            .evaluate(
                (
                    self.entry(
                        statement=(
                            "GPU reasoning improves "
                            "MAESTRO research"
                        ),
                        suffix="one",
                    ),
                    self.entry(
                        statement=(
                            "GPU runtime improves "
                            "MAESTRO research"
                        ),
                        suffix="two",
                    ),
                )
            )
        )

        for row in (
            result.ranked_observations
        ):
            self.assertEqual(
                row.verification_status,
                "UNVERIFIED_EXTERNAL",
            )

            self.assertFalse(
                row.system_truth_asserted
            )

    def test_portfolio_does_not_assert_truth(
        self,
    ):
        result = (
            GovernedRadarPortfolio()
            .evaluate(
                (
                    self.entry(
                        statement=(
                            "GPU reasoning improves "
                            "MAESTRO research"
                        ),
                        suffix="truth",
                    ),
                )
            )
        )

        for evaluation in (
            result.evaluations
        ):
            self.assertFalse(
                evaluation.observation
                .system_truth_asserted
            )

    def test_result_ids_match_evaluations(
        self,
    ):
        entries = (
            self.entry(
                statement=(
                    "GPU reasoning improves "
                    "MAESTRO research"
                ),
                suffix="one",
            ),
            self.entry(
                statement=(
                    "GPU runtime improves "
                    "MAESTRO research"
                ),
                suffix="two",
            ),
        )

        result = (
            GovernedRadarPortfolio()
            .evaluate(entries)
        )

        evaluation_ids = {
            evaluation.evidence_id
            for evaluation
            in result.evaluations
        }

        ranked_ids = set(
            result.ranked_evidence_ids
        )

        self.assertEqual(
            evaluation_ids,
            ranked_ids,
        )

    def test_pipeline_failure_propagates_fail_closed(
        self,
    ):
        entry = self.entry(
            statement=(
                "GPU reasoning improves "
                "MAESTRO research"
            ),
            suffix="unknown",
            context=(
                GovernedRadarEvaluationPipeline
                .context(
                    capability_terms=[
                        "GPU"
                    ],
                    integration_requirements=[
                        "python"
                    ],
                    available_integration_support=[
                        "python"
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
            ),
        )

        with self.assertRaises(
            ValueError
        ):
            (
                GovernedRadarPortfolio()
                .evaluate([entry])
            )

    def test_generator_entries_are_materialized_once(
        self,
    ):
        entries = (
            self.entry(
                statement=(
                    "GPU reasoning improves "
                    "MAESTRO research"
                ),
                suffix=str(index),
            )
            for index in range(2)
        )

        result = (
            GovernedRadarPortfolio()
            .evaluate(entries)
        )

        self.assertEqual(
            result.size,
            2,
        )

    def test_module_has_no_network_learning_activation_or_authority_imports(
        self,
    ):
        path = Path(
            "src/maestro/research/"
            "radar_portfolio.py"
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
