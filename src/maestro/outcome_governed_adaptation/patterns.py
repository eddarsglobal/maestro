from __future__ import annotations

from collections import defaultdict
from typing import Iterable

from maestro.outcome_intelligence import (
    AttributionEffect,
    AttributionTarget,
    VerifiedOutcome,
)

from .models import OutcomePattern


class OutcomePatternDetector:
    """Detect repeated attributable patterns without mixing different subjects."""

    SUPPORTED_TARGETS = {
        AttributionTarget.RESOURCE,
        AttributionTarget.CONTEXT,
        AttributionTarget.TOOL,
        AttributionTarget.STRATEGY,
    }

    def __init__(
        self,
        *,
        min_support: int = 3,
        min_attribution_confidence: float = 0.55,
        max_counter_ratio: float = 0.34,
    ):
        self.min_support = max(2, int(min_support))
        self.min_attribution_confidence = float(min_attribution_confidence)
        self.max_counter_ratio = float(max_counter_ratio)

    def _subject_id(
        self,
        outcome: VerifiedOutcome,
        target: AttributionTarget,
    ) -> str | None:
        if target is AttributionTarget.RESOURCE:
            return outcome.resource_id

        meta = outcome.metadata if isinstance(outcome.metadata, dict) else {}
        keys = {
            AttributionTarget.CONTEXT: ("context_id", "context_ref"),
            AttributionTarget.TOOL: ("tool_id", "tool_name"),
            AttributionTarget.STRATEGY: ("strategy_id", "strategy_key"),
        }.get(target, ())

        for key in keys:
            value = meta.get(key)
            if value is not None and str(value).strip():
                return str(value)
        return None

    def detect(self, outcomes: Iterable[VerifiedOutcome]) -> list[OutcomePattern]:
        rows = [o for o in outcomes if o.ay_verified]
        grouped: dict[
            tuple[str, str, str, str],
            list[tuple[VerifiedOutcome, float]],
        ] = defaultdict(list)

        for outcome in rows:
            for finding in outcome.attributions:
                if finding.target not in self.SUPPORTED_TARGETS:
                    continue
                if finding.effect not in {
                    AttributionEffect.CREDIT,
                    AttributionEffect.BLAME,
                }:
                    continue
                if finding.confidence < self.min_attribution_confidence:
                    continue

                subject_id = self._subject_id(outcome, finding.target)
                if subject_id is None:
                    # Never combine unattributed subjects into one pattern.
                    continue

                key = (
                    outcome.task_family,
                    finding.target.value,
                    finding.effect.value,
                    subject_id,
                )
                grouped[key].append((outcome, finding.confidence))

        patterns: list[OutcomePattern] = []

        for (task_family, target, effect, subject_id), support_rows in grouped.items():
            unique_support = {
                o.outcome_id: (o, confidence)
                for o, confidence in support_rows
            }
            support = list(unique_support.values())
            distinct_tasks = len({o.task_id for o, _ in support})

            if len(support) < self.min_support or distinct_tasks < self.min_support:
                continue

            opposite = (
                AttributionEffect.BLAME.value
                if effect == AttributionEffect.CREDIT.value
                else AttributionEffect.CREDIT.value
            )
            counter_rows = grouped.get(
                (task_family, target, opposite, subject_id),
                [],
            )
            unique_counter = {
                o.outcome_id: (o, confidence)
                for o, confidence in counter_rows
            }

            support_ids = tuple(sorted(unique_support))
            counter_ids = tuple(sorted(unique_counter))
            total = len(support_ids) + len(counter_ids)
            counter_ratio = len(counter_ids) / total if total else 0.0

            if counter_ratio > self.max_counter_ratio:
                continue

            mean_confidence = sum(c for _, c in support) / len(support)

            patterns.append(
                OutcomePattern(
                    task_family=task_family,
                    attribution_target=target,
                    effect=effect,
                    support_outcome_ids=support_ids,
                    counter_outcome_ids=counter_ids,
                    mean_confidence=mean_confidence,
                    distinct_tasks=distinct_tasks,
                    subject_id=subject_id,
                    metadata={
                        "counter_ratio": counter_ratio,
                        "min_support": self.min_support,
                        "min_attribution_confidence": self.min_attribution_confidence,
                    },
                )
            )

        return sorted(
            patterns,
            key=lambda p: (
                p.task_family,
                p.attribution_target,
                p.effect,
                p.subject_id or "",
                p.pattern_id,
            ),
        )
