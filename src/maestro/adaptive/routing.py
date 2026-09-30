from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

from maestro.councils.registry import COUNCILS
from .models import AdaptivePolicy, PolicyKind


@dataclass(slots=True)
class RoutingDecision:
    councils: set[str]
    matched_rule: str | None
    confidence: float
    rationale: list[str]


class AdaptiveRoutingEngine:
    """
    Deterministic learned routing layer.

    Policy parameters:
    {
      "rules": {
        "PAYMENT": ["PM","IT","SC","FN","OP","AY"],
        ...
      },
      "tag_rules": {"privacy": ["JR","DT"]},
      "default": ["AY"]
    }
    """

    def route(
        self,
        policy: AdaptivePolicy,
        *,
        task_family: str,
        tags: Iterable[str] = (),
        mandatory_councils: Iterable[str] = (),
    ) -> RoutingDecision:
        if policy.kind is not PolicyKind.ROUTING:
            raise ValueError("Routing engine requires ROUTING policy.")

        params = policy.parameters
        rules = dict(params.get("rules", {}))
        tag_rules = dict(params.get("tag_rules", {}))
        default = set(params.get("default", ["AY"]))

        selected = set(rules.get(task_family, default))
        matched = task_family if task_family in rules else None
        rationale = [f"task_family={task_family}"]

        for tag in sorted(set(tags)):
            if tag in tag_rules:
                selected.update(tag_rules[tag])
                rationale.append(f"tag_rule={tag}")

        selected.update(mandatory_councils)

        known = {c.value for c in COUNCILS}
        unknown = selected - known
        if unknown:
            rationale.append(f"dynamic_or_unknown={sorted(unknown)}")

        confidence = 0.95 if matched else 0.60
        if mandatory_councils:
            confidence = min(1.0, confidence + 0.03)

        return RoutingDecision(
            councils=selected,
            matched_rule=matched,
            confidence=confidence,
            rationale=rationale,
        )

    def propose_from_examples(
        self,
        *,
        version: int,
        examples: list[tuple[str, set[str]]],
        parent_policy_id: str | None = None,
    ) -> AdaptivePolicy:
        grouped: dict[str, list[set[str]]] = {}
        for family, councils in examples:
            grouped.setdefault(family, []).append(set(councils))

        rules: dict[str, list[str]] = {}
        for family, sets in grouped.items():
            # Conservative learned route = union of councils observed in verified-success examples.
            union = set().union(*sets)
            rules[family] = sorted(union)

        return AdaptivePolicy(
            kind=PolicyKind.ROUTING,
            version=version,
            parent_policy_id=parent_policy_id,
            description="Routing policy distilled from verified successful examples.",
            parameters={"rules": rules, "tag_rules": {}, "default": ["AY"]},
        )
