from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .models import AdaptivePolicy, PolicyKind


@dataclass(frozen=True, slots=True)
class ContextDecision:
    max_chars: int
    include_dependency_outputs: bool
    include_evidence: bool
    evidence_limit: int
    include_project_summary: bool


class AdaptiveContextPolicy:
    """
    Learns how much context a Council/task family should receive without
    modifying the underlying constitutional context rules.
    """

    def decide(
        self,
        policy: AdaptivePolicy,
        *,
        council: str,
        task_family: str,
        risk: int,
    ) -> ContextDecision:
        if policy.kind is not PolicyKind.CONTEXT:
            raise ValueError("Context engine requires CONTEXT policy.")

        params = policy.parameters
        base = int(params.get("base_max_chars", 12000))
        council_overrides = params.get("council_overrides", {})
        family_overrides = params.get("family_overrides", {})

        cfg: dict[str, Any] = {
            "max_chars": base,
            "include_dependency_outputs": True,
            "include_evidence": True,
            "evidence_limit": 32,
            "include_project_summary": False,
        }
        cfg.update(council_overrides.get(council, {}))
        cfg.update(family_overrides.get(task_family, {}))

        if risk >= 4:
            cfg["evidence_limit"] = max(int(cfg["evidence_limit"]), 64)
            cfg["include_project_summary"] = True

        return ContextDecision(
            max_chars=max(1000, int(cfg["max_chars"])),
            include_dependency_outputs=bool(cfg["include_dependency_outputs"]),
            include_evidence=bool(cfg["include_evidence"]),
            evidence_limit=max(0, int(cfg["evidence_limit"])),
            include_project_summary=bool(cfg["include_project_summary"]),
        )

    def propose_budget_update(
        self,
        *,
        version: int,
        parent_policy_id: str | None,
        current_base_max_chars: int,
        successful_context_sizes: list[int],
    ) -> AdaptivePolicy:
        if not successful_context_sizes:
            proposed = current_base_max_chars
        else:
            ordered = sorted(successful_context_sizes)
            # p75-ish without external statistics dependency.
            idx = min(len(ordered) - 1, int(0.75 * (len(ordered) - 1)))
            proposed = max(2000, min(current_base_max_chars, ordered[idx]))

        return AdaptivePolicy(
            kind=PolicyKind.CONTEXT,
            version=version,
            parent_policy_id=parent_policy_id,
            description="Context budget candidate distilled from successful runs.",
            parameters={
                "base_max_chars": proposed,
                "council_overrides": {},
                "family_overrides": {},
            },
        )
