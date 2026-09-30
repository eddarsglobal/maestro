from __future__ import annotations

from dataclasses import dataclass

from .models import OutcomeDimension, VerifiedOutcome


@dataclass(slots=True)
class OutcomeScoreCard:
    task_family: str
    resource_id: str | None
    samples: int
    system_success_rate: float
    semantic_pass_rate: float | None
    format_pass_rate: float | None


def _rate(rows: list[VerifiedOutcome], dim: OutcomeDimension) -> float | None:
    values = []
    for row in rows:
        result = row.dimension(dim)
        if result is not None and result.passed is not None:
            values.append(1.0 if result.passed else 0.0)
    return (sum(values) / len(values)) if values else None


class OutcomeScoreCardEngine:
    def build(self, rows: list[VerifiedOutcome], *, task_family: str, resource_id: str | None) -> OutcomeScoreCard:
        selected = [r for r in rows if r.task_family == task_family and r.resource_id == resource_id]
        if not selected:
            raise LookupError("No outcomes for requested scorecard.")
        return OutcomeScoreCard(
            task_family=task_family,
            resource_id=resource_id,
            samples=len(selected),
            system_success_rate=sum(1.0 if r.system_success else 0.0 for r in selected) / len(selected),
            semantic_pass_rate=_rate(selected, OutcomeDimension.SEMANTIC_CORRECTNESS),
            format_pass_rate=_rate(selected, OutcomeDimension.FORMAT_COMPLIANCE),
        )
