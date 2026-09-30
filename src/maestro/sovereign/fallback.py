from __future__ import annotations

from .contracts import IntelligenceRequest, ResourceStatus
from .registry import IntelligenceResourceRegistry
from .router import SovereignIntelligenceRouter


class FallbackPlanner:
    """
    Re-routes after a resource failure without changing mission authority.
    """

    def __init__(self, registry: IntelligenceResourceRegistry):
        self.registry = registry
        self.router = SovereignIntelligenceRouter(registry)

    def after_failure(self, request: IntelligenceRequest, failed_resource_id: str):
        if failed_resource_id in {d.resource_id for d in self.registry.all()}:
            self.registry.set_status(failed_resource_id, ResourceStatus.DEGRADED)
        forbidden = frozenset(set(request.forbidden_resources) | {failed_resource_id})
        replacement = IntelligenceRequest(
            task_id=request.task_id,
            capability=request.capability,
            instruction=request.instruction,
            context_ref=request.context_ref,
            max_tokens=request.max_tokens,
            requires_tools=request.requires_tools,
            preferred_local=request.preferred_local,
            forbidden_resources=forbidden,
            metadata=dict(request.metadata),
        )
        return self.router.decide(replacement)
