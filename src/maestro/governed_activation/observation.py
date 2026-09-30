from __future__ import annotations

from .models import CanaryEvidence


class RuntimeObservationFactory:
    def create(
        self,
        *,
        success_rate: float,
        regression_count: int,
        observed_samples: int,
        evidence_refs,
        latency_budget_pass: bool = True,
        metadata=None,
    ) -> CanaryEvidence:
        return CanaryEvidence(
            success_rate=float(success_rate),
            regression_count=int(regression_count),
            observed_samples=int(observed_samples),
            evidence_refs=tuple(str(x) for x in evidence_refs),
            latency_budget_pass=bool(latency_budget_pass),
            metadata=dict(metadata or {}),
        )
