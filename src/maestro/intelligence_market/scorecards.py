from __future__ import annotations

from statistics import mean, pstdev
from typing import Iterable

from .models import MarketObservation, ResourceScoreCard, MarketPolicy


def _bounded(value: float) -> float:
    return max(0.0, min(1.0, value))


class ScoreCardEngine:
    def __init__(self, policy: MarketPolicy | None = None):
        self.policy = policy or MarketPolicy()

    def build(
        self,
        observations: list[MarketObservation],
        *,
        resource_id: str,
        task_family: str,
        council_id: str | None,
    ) -> ResourceScoreCard:
        rows = [
            o for o in observations
            if o.resource_id == resource_id
            and o.task_family == task_family
            and o.council_id == council_id
        ]
        if not rows:
            raise LookupError("No observations for requested scorecard.")

        success_rate = mean(1.0 if o.success else 0.0 for o in rows)
        quality = mean(_bounded(o.quality) for o in rows)
        cost = mean(_bounded(o.cost_score) for o in rows)
        context_fit = mean(_bounded(o.context_fit) for o in rows)
        tool_fit = mean(_bounded(o.tool_fit) for o in rows)
        local_ratio = mean(1.0 if o.local else 0.0 for o in rows)

        latencies = [o.latency_ms for o in rows if o.latency_ms is not None]
        latency_ms = mean(latencies) if latencies else None

        # Reliability rewards consistency of quality while preserving success rate.
        qualities = [_bounded(o.quality) for o in rows]
        variability = pstdev(qualities) if len(qualities) > 1 else 0.0
        reliability = _bounded(success_rate * (1.0 - min(1.0, variability)))

        # Normalize latency as 1 / (1 + seconds): lower is better, bounded.
        latency_score = 1.0
        if latency_ms is not None:
            latency_score = 1.0 / (1.0 + max(0.0, latency_ms) / 1000.0)

        cost_efficiency = 1.0 - cost
        locality = local_ratio

        p = self.policy
        weighted = (
            quality * p.quality_weight
            + success_rate * p.success_weight
            + reliability * p.reliability_weight
            + latency_score * p.latency_weight
            + cost_efficiency * p.cost_weight
            + context_fit * p.context_weight
            + tool_fit * p.tool_weight
            + locality * p.locality_weight
        )
        score = weighted / p.total_weight()

        return ResourceScoreCard(
            resource_id=resource_id,
            task_family=task_family,
            council_id=council_id,
            samples=len(rows),
            success_rate=success_rate,
            mean_quality=quality,
            mean_latency_ms=latency_ms,
            mean_cost_score=cost,
            reliability=reliability,
            context_fit=context_fit,
            tool_fit=tool_fit,
            local_ratio=local_ratio,
            market_score=_bounded(score),
        )
