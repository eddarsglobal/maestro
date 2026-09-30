from __future__ import annotations

from maestro.academy.models import PolicyVariant
from maestro.adaptive import AdaptiveController, AdaptivePolicy, PolicyKind

from .models import AdaptationCandidate, AdaptationDomain, AdaptationStatus


class UnsupportedAdaptationDomain(RuntimeError):
    pass


class AdaptivePolicyBridge:
    DOMAIN_TO_KIND = {
        AdaptationDomain.ROUTING: PolicyKind.ROUTING,
        AdaptationDomain.CONTEXT: PolicyKind.CONTEXT,
        AdaptationDomain.TOOL_SELECTION: PolicyKind.TOOL_SELECTION,
        AdaptationDomain.MODEL_SELECTION: PolicyKind.MODEL_SELECTION,
        AdaptationDomain.RETRY_STRATEGY: PolicyKind.RETRY_STRATEGY,
        AdaptationDomain.SKILL: PolicyKind.SKILL,
    }

    def to_policy(self, candidate: AdaptationCandidate, *, version: int = 1) -> AdaptivePolicy:
        kind = self.DOMAIN_TO_KIND.get(candidate.domain)
        if kind is None:
            raise UnsupportedAdaptationDomain(
                "Strategic adaptation remains proposal-only until routed through StrategicAdaptationEngine."
            )
        return AdaptivePolicy(
            kind=kind,
            version=version,
            description=candidate.statement,
            parameters={
                **candidate.proposed_change,
                "source_candidate_id": candidate.candidate_id,
                "source_pattern_id": candidate.pattern_id,
                "outcome_support": list(candidate.support_outcome_ids),
            },
        )

    def to_academy_variant(self, candidate: AdaptationCandidate, *, version: str = "shadow-1") -> PolicyVariant:
        return PolicyVariant(
            policy_id=candidate.candidate_id,
            version=version,
            description=candidate.statement,
            parameters=dict(candidate.proposed_change),
        )

    def stage_shadow(
        self,
        candidate: AdaptationCandidate,
        controller: AdaptiveController,
        *,
        version: int = 1,
    ) -> AdaptivePolicy:
        policy = self.to_policy(candidate, version=version)
        controller.stage_candidate(policy)
        candidate.status = AdaptationStatus.SHADOW
        candidate.metadata["shadow_policy_id"] = policy.policy_id
        return policy
