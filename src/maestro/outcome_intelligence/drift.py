from __future__ import annotations

from dataclasses import dataclass

from .models import OutcomeDimension, VerifiedOutcome


@dataclass(slots=True)
class OutcomeDriftSignal:
    detected: bool
    reason: str
    recent_rate: float | None = None
    baseline_rate: float | None = None


class OutcomeDriftDetector:
    def detect(self, baseline: list[VerifiedOutcome], recent: list[VerifiedOutcome], *, dimension: OutcomeDimension, threshold: float = 0.25) -> OutcomeDriftSignal:
        def rate(rows):
            values = []
            for row in rows:
                value = row.dimension(dimension)
                if value is not None and value.passed is not None:
                    values.append(1.0 if value.passed else 0.0)
            return sum(values) / len(values) if values else None

        base = rate(baseline)
        now = rate(recent)
        if base is None or now is None:
            return OutcomeDriftSignal(False, "insufficient comparable evidence", now, base)
        detected = (base - now) >= threshold
        return OutcomeDriftSignal(detected, "material degradation" if detected else "no material degradation", now, base)
