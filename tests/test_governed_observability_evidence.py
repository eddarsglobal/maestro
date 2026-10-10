from __future__ import annotations

import ast
import math
import unittest

from dataclasses import replace
from pathlib import Path

from maestro.governance.governed_observability_evidence import (
    ComparableEvidenceSeries,
    CrossGenerationState,
    EvidenceDimension,
    EvidenceValueKind,
    GenerationEvidencePoint,
    GovernedCrossGenerationEvidence,
    GovernedGenerationObservation,
    GovernedObservabilityEvidence,
    GovernedObservabilityInvariantError,
    ObservedEvidenceMeasure,
)


DOC = Path(
    "docs/"
    "GOVERNED_OBSERVABILITY_EVIDENCE_CONSTITUTION.md"
)

SOURCE = Path(
    "src/maestro/governance/"
    "governed_observability_evidence.py"
)


def measure(
    dimension: EvidenceDimension,
    metric_id: str,
    value,
    unit: str | None,
    evidence_id: str,
    *,
    observed_at: str = "2026-10-10T12:00:00Z",
) -> ObservedEvidenceMeasure:
    return ObservedEvidenceMeasure(
        dimension=dimension,
        metric_id=metric_id,
        value=value,
        unit=unit,
        evidence_id=evidence_id,
        source_ref=f"source://{evidence_id}",
        observed_at=observed_at,
    )


def four_dimensions(
    prefix: str,
    latency: float,
    reliability: float,
    security: bool,
    outcome: float,
):
    return (
        measure(
            EvidenceDimension.PERFORMANCE,
            "latency-p95",
            latency,
            "ms",
            f"{prefix}-PERF",
        ),
        measure(
            EvidenceDimension.RELIABILITY,
            "success-rate",
            reliability,
            "ratio",
            f"{prefix}-REL",
        ),
        measure(
            EvidenceDimension.SECURITY,
            "validator-integrity",
            security,
            None,
            f"{prefix}-SEC",
        ),
        measure(
            EvidenceDimension.OUTCOME,
            "mission-success-rate",
            outcome,
            "ratio",
            f"{prefix}-OUT",
        ),
    )


def observation(
    generation_id: str,
    generation_index: int,
    measures,
    *,
    subject_id: str = "RESOURCE-X",
    subject_kind: str = "RESOURCE",
):
    return GovernedObservabilityEvidence.capture(
        generation_id=generation_id,
        generation_index=generation_index,
        subject_id=subject_id,
        subject_kind=subject_kind,
        measures=tuple(measures),
    )


class GovernedObservabilityEvidenceTests(
    unittest.TestCase
):
    def test_01_constitution_contains_ten_laws_and_core_invariants(self):
        text = DOC.read_text(
            encoding="utf-8"
        )

        for number in range(1, 11):
            self.assertIn(
                f"GOE-{number:02d}",
                text,
            )

        for invariant in (
            "OBSERVED != JUDGED",
            "MEASURED != OPTIMAL",
            "TELEMETRY != TRUTH",
            "EVIDENCE != VERDICT",
            "PERFORMANCE EVIDENCE != PROMOTION",
            "SECURITY SIGNAL != SECURITY GUARANTEE",
            "OUTCOME OBSERVED != LEARNING AUTHORIZED",
            "OBSERVABILITY != CONTROL",
            "COMPARABLE != BETTER",
            "OBSERVATION != RELEASE CERTIFICATION",
        ):
            self.assertIn(
                invariant,
                text,
            )

    def test_02_four_dimensions_remain_observable_across_generations(self):
        g1 = observation(
            "GEN-1",
            1,
            four_dimensions(
                "G1",
                120.0,
                0.94,
                True,
                0.88,
            ),
        )

        g2 = observation(
            "GEN-2",
            2,
            four_dimensions(
                "G2",
                110.0,
                0.96,
                True,
                0.91,
            ),
        )

        result = (
            GovernedObservabilityEvidence.compare(
                (g2, g1)
            )
        )

        self.assertIs(
            result.state,
            CrossGenerationState.COMPARABLE,
        )

        self.assertEqual(
            result.generation_ids,
            (
                "GEN-1",
                "GEN-2",
            ),
        )

        self.assertEqual(
            result.generation_indexes,
            (
                1,
                2,
            ),
        )

        self.assertEqual(
            {
                row.dimension
                for row in result.series
            },
            {
                EvidenceDimension.PERFORMANCE,
                EvidenceDimension.RELIABILITY,
                EvidenceDimension.SECURITY,
                EvidenceDimension.OUTCOME,
            },
        )

        self.assertEqual(
            len(result.series),
            4,
        )

        self.assertFalse(
            result.judgment_asserted
        )
        self.assertFalse(
            result.verdict_asserted
        )

    def test_03_no_common_metric_is_insufficient_not_verdict(self):
        g1 = observation(
            "GEN-1",
            1,
            (
                measure(
                    EvidenceDimension.PERFORMANCE,
                    "latency",
                    100,
                    "ms",
                    "E1",
                ),
            ),
        )

        g2 = observation(
            "GEN-2",
            2,
            (
                measure(
                    EvidenceDimension.SECURITY,
                    "integrity",
                    True,
                    None,
                    "E2",
                ),
            ),
        )

        result = (
            GovernedObservabilityEvidence.compare(
                (g1, g2)
            )
        )

        self.assertIs(
            result.state,
            CrossGenerationState.INSUFFICIENT,
        )

        self.assertEqual(
            result.series,
            (),
        )

        self.assertFalse(
            result.verdict_asserted
        )

        self.assertFalse(
            result.system_truth_asserted
        )

    def test_04_partial_comparability_is_metric_specific(self):
        g1 = observation(
            "GEN-1",
            1,
            (
                measure(
                    EvidenceDimension.PERFORMANCE,
                    "latency",
                    100,
                    "ms",
                    "G1-P",
                ),
                measure(
                    EvidenceDimension.RELIABILITY,
                    "success-rate",
                    0.90,
                    "ratio",
                    "G1-R",
                ),
            ),
        )

        g2 = observation(
            "GEN-2",
            2,
            (
                measure(
                    EvidenceDimension.PERFORMANCE,
                    "latency",
                    90,
                    "ms",
                    "G2-P",
                ),
                measure(
                    EvidenceDimension.SECURITY,
                    "integrity",
                    True,
                    None,
                    "G2-S",
                ),
            ),
        )

        result = (
            GovernedObservabilityEvidence.compare(
                (g1, g2)
            )
        )

        self.assertIs(
            result.state,
            CrossGenerationState.COMPARABLE,
        )

        self.assertEqual(
            len(result.series),
            1,
        )

        self.assertEqual(
            result.series[0].metric_id,
            "latency",
        )

        self.assertFalse(
            result.optimality_asserted
        )

        self.assertFalse(
            result.promotion_requested
        )

    def test_05_subject_duplicate_generation_and_metric_mismatches_fail_closed(self):
        left = observation(
            "GEN-1",
            1,
            (
                measure(
                    EvidenceDimension.PERFORMANCE,
                    "latency",
                    100,
                    "ms",
                    "L",
                ),
            ),
            subject_id="RESOURCE-A",
        )

        right = observation(
            "GEN-2",
            2,
            (
                measure(
                    EvidenceDimension.PERFORMANCE,
                    "latency",
                    90,
                    "ms",
                    "R",
                ),
            ),
            subject_id="RESOURCE-B",
        )

        with self.assertRaises(
            GovernedObservabilityInvariantError
        ):
            GovernedObservabilityEvidence.compare(
                (left, right)
            )

        duplicate_id_a = observation(
            "GEN-X",
            1,
            (
                measure(
                    EvidenceDimension.PERFORMANCE,
                    "latency",
                    100,
                    "ms",
                    "D1",
                ),
            ),
        )

        duplicate_id_b = observation(
            "GEN-X",
            2,
            (
                measure(
                    EvidenceDimension.PERFORMANCE,
                    "latency",
                    90,
                    "ms",
                    "D2",
                ),
            ),
        )

        with self.assertRaises(
            GovernedObservabilityInvariantError
        ):
            GovernedObservabilityEvidence.compare(
                (
                    duplicate_id_a,
                    duplicate_id_b,
                )
            )

        duplicate_index = observation(
            "GEN-Y",
            1,
            (
                measure(
                    EvidenceDimension.PERFORMANCE,
                    "latency",
                    80,
                    "ms",
                    "D3",
                ),
            ),
        )

        with self.assertRaises(
            GovernedObservabilityInvariantError
        ):
            GovernedObservabilityEvidence.compare(
                (
                    duplicate_id_a,
                    duplicate_index,
                )
            )

        first = measure(
            EvidenceDimension.PERFORMANCE,
            "latency",
            100,
            "ms",
            "M1",
        )

        second = measure(
            EvidenceDimension.PERFORMANCE,
            "latency",
            90,
            "ms",
            "M2",
        )

        with self.assertRaises(
            GovernedObservabilityInvariantError
        ):
            observation(
                "GEN-M",
                3,
                (
                    first,
                    second,
                ),
            )

    def test_06_timestamps_and_numeric_values_fail_closed(self):
        with self.assertRaises(
            GovernedObservabilityInvariantError
        ):
            measure(
                EvidenceDimension.PERFORMANCE,
                "latency",
                100,
                "ms",
                "NAIVE",
                observed_at=(
                    "2026-10-10T12:00:00"
                ),
            )

        aware = measure(
            EvidenceDimension.PERFORMANCE,
            "latency",
            100,
            "ms",
            "AWARE",
            observed_at=(
                "2026-10-10T14:00:00+02:00"
            ),
        )

        self.assertEqual(
            aware.observed_at,
            "2026-10-10T12:00:00+00:00",
        )

        for value in (
            math.nan,
            math.inf,
            -math.inf,
        ):
            with self.subTest(
                value=value
            ):
                with self.assertRaises(
                    GovernedObservabilityInvariantError
                ):
                    measure(
                        EvidenceDimension.PERFORMANCE,
                        "metric",
                        value,
                        None,
                        "NONFINITE",
                    )

    def test_07_identity_lineage_and_value_kind_spoofs_fail_closed(self):
        item = measure(
            EvidenceDimension.PERFORMANCE,
            "latency",
            100,
            "ms",
            "OBS-E",
        )

        with self.assertRaises(
            GovernedObservabilityInvariantError
        ):
            GovernedGenerationObservation(
                observation_id="GOE-SPOOF",
                generation_id="GEN-1",
                generation_index=1,
                subject_id="RESOURCE-X",
                subject_kind="RESOURCE",
                measures=(item,),
            )

        with self.assertRaises(
            GovernedObservabilityInvariantError
        ):
            ComparableEvidenceSeries(
                dimension=(
                    EvidenceDimension.PERFORMANCE
                ),
                metric_id="latency",
                value_kind=(
                    EvidenceValueKind.NUMBER
                ),
                unit="ms",
                points=(
                    GenerationEvidencePoint(
                        "GEN-1",
                        1,
                        "OBS-1",
                        True,
                        "E-1",
                        "source://1",
                        "2026-10-10T12:00:00Z",
                    ),
                    GenerationEvidencePoint(
                        "GEN-2",
                        2,
                        "OBS-2",
                        False,
                        "E-2",
                        "source://2",
                        "2026-10-10T13:00:00Z",
                    ),
                ),
            )

        series = ComparableEvidenceSeries(
            dimension=(
                EvidenceDimension.PERFORMANCE
            ),
            metric_id="latency",
            value_kind=(
                EvidenceValueKind.NUMBER
            ),
            unit="ms",
            points=(
                GenerationEvidencePoint(
                    "GEN-1",
                    1,
                    "OBS-1",
                    100,
                    "E-1",
                    "source://1",
                    "2026-10-10T12:00:00Z",
                ),
                GenerationEvidencePoint(
                    "GEN-FOREIGN",
                    2,
                    "OBS-FOREIGN",
                    90,
                    "E-2",
                    "source://2",
                    "2026-10-10T13:00:00Z",
                ),
            ),
        )

        with self.assertRaises(
            GovernedObservabilityInvariantError
        ):
            GovernedCrossGenerationEvidence(
                comparison_id="CGE-SPOOF",
                subject_id="RESOURCE-X",
                subject_kind="RESOURCE",
                state=(
                    CrossGenerationState.COMPARABLE
                ),
                generation_ids=(
                    "GEN-1",
                    "GEN-2",
                ),
                generation_indexes=(
                    1,
                    2,
                ),
                observation_ids=(
                    "OBS-1",
                    "OBS-2",
                ),
                series=(series,),
            )

    def test_08_observation_and_comparison_are_deterministic(self):
        perf = measure(
            EvidenceDimension.PERFORMANCE,
            "latency",
            100,
            "ms",
            "PERF",
        )

        rel = measure(
            EvidenceDimension.RELIABILITY,
            "success-rate",
            0.99,
            "ratio",
            "REL",
        )

        first = observation(
            "GEN-1",
            1,
            (
                perf,
                rel,
            ),
        )

        reordered = observation(
            "GEN-1",
            1,
            (
                rel,
                perf,
            ),
        )

        self.assertEqual(
            first.observation_id,
            reordered.observation_id,
        )

        self.assertEqual(
            first.to_dict(),
            reordered.to_dict(),
        )

        later = observation(
            "GEN-2",
            2,
            (
                measure(
                    EvidenceDimension.PERFORMANCE,
                    "latency",
                    90,
                    "ms",
                    "PERF-2",
                ),
                measure(
                    EvidenceDimension.RELIABILITY,
                    "success-rate",
                    0.98,
                    "ratio",
                    "REL-2",
                ),
            ),
        )

        a = GovernedObservabilityEvidence.compare(
            (
                first,
                later,
            )
        )

        b = GovernedObservabilityEvidence.compare(
            (
                later,
                first,
            )
        )

        self.assertEqual(
            a.comparison_id,
            b.comparison_id,
        )

        self.assertEqual(
            a.to_dict(),
            b.to_dict(),
        )

    def test_09_authority_escalation_fails_closed(self):
        a = observation(
            "GEN-1",
            1,
            (
                measure(
                    EvidenceDimension.PERFORMANCE,
                    "latency",
                    100,
                    "ms",
                    "AUTH-1",
                ),
            ),
        )

        b = observation(
            "GEN-2",
            2,
            (
                measure(
                    EvidenceDimension.PERFORMANCE,
                    "latency",
                    90,
                    "ms",
                    "AUTH-2",
                ),
            ),
        )

        comparison = (
            GovernedObservabilityEvidence.compare(
                (a, b)
            )
        )

        fields = (
            "judgment_asserted",
            "optimality_asserted",
            "truth_asserted",
            "verdict_asserted",
            "promotion_requested",
            "security_guarantee_asserted",
            "learning_authorized",
            "control_requested",
            "release_certification_asserted",
            "system_truth_asserted",
        )

        for target in (
            a,
            comparison,
        ):
            for field_name in fields:
                with self.subTest(
                    target=type(target).__name__,
                    field=field_name,
                ):
                    with self.assertRaises(
                        GovernedObservabilityInvariantError
                    ):
                        replace(
                            target,
                            **{
                                field_name: True
                            },
                        )

    def test_10_module_is_passive_and_bmf024_separate(self):
        text = SOURCE.read_text(
            encoding="utf-8"
        )

        tree = ast.parse(text)

        imports = set()
        calls = set()

        for node in ast.walk(tree):
            if isinstance(
                node,
                ast.Import,
            ):
                imports.update(
                    alias.name
                    for alias in node.names
                )

            elif isinstance(
                node,
                ast.ImportFrom,
            ):
                if node.module:
                    imports.add(
                        node.module
                    )

            elif isinstance(
                node,
                ast.Call,
            ):
                if isinstance(
                    node.func,
                    ast.Name,
                ):
                    calls.add(
                        node.func.id
                    )

                elif isinstance(
                    node.func,
                    ast.Attribute,
                ):
                    calls.add(
                        node.func.attr
                    )

        forbidden_import_roots = (
            "subprocess",
            "socket",
            "requests",
            "httpx",
            "aiohttp",
            "urllib",
        )

        bad_imports = {
            name
            for name in imports
            if any(
                name == root
                or name.startswith(
                    root + "."
                )
                for root
                in forbidden_import_roots
            )
        }

        forbidden_calls = {
            "promote",
            "activate",
            "authorize",
            "install",
            "execute",
            "dispatch",
            "learn",
            "train",
            "migrate",
            "certify",
        }

        self.assertEqual(
            bad_imports,
            set(),
        )

        self.assertEqual(
            calls & forbidden_calls,
            set(),
        )

        for forbidden_symbol in (
            "ReleaseGate",
            "ReleaseCertification",
            "PromotionGate",
            "LearningEngine",
            "ClusterObservability",
            "OllamaMetricsRecorder",
        ):
            self.assertNotIn(
                forbidden_symbol,
                text,
            )


if __name__ == "__main__":
    unittest.main()
