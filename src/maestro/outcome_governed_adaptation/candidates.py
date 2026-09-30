from __future__ import annotations

from maestro.outcome_intelligence import AttributionEffect, AttributionTarget

from .models import AdaptationCandidate, AdaptationDomain, OutcomePattern


class AdaptationCandidateFactory:
    TARGET_TO_DOMAIN = {
        AttributionTarget.RESOURCE.value: AdaptationDomain.MODEL_SELECTION,
        AttributionTarget.CONTEXT.value: AdaptationDomain.CONTEXT,
        AttributionTarget.TOOL.value: AdaptationDomain.TOOL_SELECTION,
        AttributionTarget.STRATEGY.value: AdaptationDomain.STRATEGY,
    }

    def build(self, pattern: OutcomePattern) -> AdaptationCandidate:
        domain = self.TARGET_TO_DOMAIN.get(pattern.attribution_target)
        if domain is None:
            raise ValueError("Outcome target is not eligible for governed adaptation.")

        action = (
            "PREFER_CONDITIONALLY"
            if pattern.effect == AttributionEffect.CREDIT.value
            else "DEPRIORITIZE_CONDITIONALLY"
        )

        if not pattern.subject_id:
            raise ValueError(
                "Outcome pattern lacks a concrete adaptation subject."
            )

        key = (
            f"{domain.value}:{pattern.task_family}:"
            f"{pattern.attribution_target}:{pattern.subject_id}:{pattern.effect}"
        )
        statement = (
            f"For task family {pattern.task_family}, repeated verified outcomes "
            f"support {action.lower()} subject {pattern.subject_id!r} "
            f"for {pattern.attribution_target.lower()} decisions."
        )

        return AdaptationCandidate(
            domain=domain,
            task_family=pattern.task_family,
            key=key,
            statement=statement,
            proposed_change={
                "action": action,
                "scope": "TASK_FAMILY",
                "task_family": pattern.task_family,
                "attribution_target": pattern.attribution_target,
                "subject_id": pattern.subject_id,
                "effect": pattern.effect,
                "authority_change": False,
            },
            pattern_id=pattern.pattern_id,
            support_outcome_ids=pattern.support_outcome_ids,
            counter_outcome_ids=pattern.counter_outcome_ids,
            confidence=pattern.mean_confidence,
            metadata={
                "distinct_tasks": pattern.distinct_tasks,
                "counter_ratio": pattern.counter_ratio,
                "subject_id": pattern.subject_id,
            },
        )
