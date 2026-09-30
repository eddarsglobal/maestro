from __future__ import annotations

from dataclasses import dataclass

from .contracts import IntelligenceRequest, ResourceDescriptor
from .registry import IntelligenceResourceRegistry


@dataclass(slots=True)
class RoutingDecision:
    resource_id: str
    reason: str
    candidates: list[str]


class SovereignIntelligenceRouter:
    """
    MAESTRO selects intelligence resources. No model selects itself.
    """

    def __init__(self, registry: IntelligenceResourceRegistry):
        self.registry = registry

    def decide(self, request: IntelligenceRequest) -> RoutingDecision:
        candidates = self.registry.eligible(
            request.capability,
            requires_tools=request.requires_tools,
            forbidden_resources=request.forbidden_resources,
        )
        if not candidates:
            raise LookupError(f"No eligible intelligence resource for {request.capability.value}")

        def score(d: ResourceDescriptor) -> tuple:
            # Capability/eligibility is handled first. Then local preference,
            # quality, cost, latency, deterministic resource_id tie-break.
            local_penalty = 0 if (request.preferred_local and d.local) else 1
            degraded_penalty = 1 if d.status.value == "DEGRADED" else 0
            return (
                degraded_penalty,
                local_penalty,
                -d.quality_score,
                d.cost_score,
                d.latency_score,
                d.resource_id,
            )

        chosen = min(candidates, key=score)
        return RoutingDecision(
            resource_id=chosen.resource_id,
            reason="eligible capability + sovereignty policy ranking",
            candidates=[c.resource_id for c in candidates],
        )
