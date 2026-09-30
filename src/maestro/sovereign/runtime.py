from __future__ import annotations

from .contracts import IntelligenceRequest, IntelligenceResponse, ResourceStatus
from .registry import IntelligenceResourceRegistry
from .router import SovereignIntelligenceRouter
from .fallback import FallbackPlanner
from .degraded import DegradedModeController


class SovereignIntelligenceRuntime:
    def __init__(self, registry: IntelligenceResourceRegistry | None = None):
        self.registry = registry or IntelligenceResourceRegistry()
        self.router = SovereignIntelligenceRouter(self.registry)
        self.fallback = FallbackPlanner(self.registry)
        self.degraded = DegradedModeController()

    def execute(self, request: IntelligenceRequest) -> IntelligenceResponse:
        decision = self.router.decide(request)
        adapter = self.registry.adapter(decision.resource_id)

        try:
            result = adapter.execute(request)
        except Exception as exc:
            fallback = self.fallback.after_failure(request, decision.resource_id)
            replacement = self.registry.adapter(fallback.resource_id)
            result = replacement.execute(request)
            result.metadata.setdefault("fallback_from", decision.resource_id)
            result.metadata.setdefault("fallback_reason", str(exc))
            return result

        if not result.success:
            fallback = self.fallback.after_failure(request, decision.resource_id)
            replacement = self.registry.adapter(fallback.resource_id)
            replacement_result = replacement.execute(request)
            replacement_result.metadata.setdefault("fallback_from", decision.resource_id)
            return replacement_result

        return result
