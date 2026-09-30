from __future__ import annotations

from dataclasses import dataclass

from maestro.sovereign.contracts import ResourceDescriptor


@dataclass(slots=True)
class DiversityPolicy:
    avoid_same_resource_for_critic: bool = True
    prefer_provider_diversity: bool = True
    max_resources_per_provider: int = 2


class DiversityPlanner:
    """
    Diversity is a resilience/evaluation strategy, not truth by voting.
    """

    def __init__(self, policy: DiversityPolicy | None = None):
        self.policy = policy or DiversityPolicy()

    def filter_candidates(
        self,
        candidates: list[ResourceDescriptor],
        *,
        already_used_resources: set[str],
        already_used_providers: list[str],
        require_provider_diversity: bool = False,
    ) -> list[ResourceDescriptor]:
        out = list(candidates)

        if self.policy.avoid_same_resource_for_critic and already_used_resources:
            alternatives = [c for c in out if c.resource_id not in already_used_resources]
            if alternatives:
                out = alternatives

        if require_provider_diversity and self.policy.prefer_provider_diversity and already_used_providers:
            providers = set(already_used_providers)
            diverse = [c for c in out if c.provider_id not in providers]
            if diverse:
                out = diverse

        if already_used_providers:
            counts = {p: already_used_providers.count(p) for p in set(already_used_providers)}
            limited = [
                c for c in out
                if counts.get(c.provider_id, 0) < self.policy.max_resources_per_provider
            ]
            if limited:
                out = limited

        return out
