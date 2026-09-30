from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from .contracts import IntelligenceCapability
from .registry import IntelligenceResourceRegistry


class DegradedCapability(StrEnum):
    DETERMINISTIC_ONLY = "DETERMINISTIC_ONLY"
    LIMITED_REASONING = "LIMITED_REASONING"
    FULL_INTELLIGENCE = "FULL_INTELLIGENCE"


@dataclass(slots=True)
class DegradedModeState:
    level: DegradedCapability
    available_capabilities: set[str]
    reason: str


class DegradedModeController:
    """
    MAESTRO preserves deterministic governance when no LLM is available.
    """

    def assess(self, registry: IntelligenceResourceRegistry) -> DegradedModeState:
        available = set()
        for d in registry.all():
            if d.status.value != "UNAVAILABLE":
                available.update(c.value for c in d.capabilities)

        if not available:
            return DegradedModeState(
                DegradedCapability.DETERMINISTIC_ONLY,
                set(),
                "No intelligence resources available; governance/runtime remain active.",
            )

        reasoning = {
            IntelligenceCapability.DIRECT.value,
            IntelligenceCapability.GENERAL_REASONING.value,
        }
        if available & reasoning:
            return DegradedModeState(
                DegradedCapability.FULL_INTELLIGENCE,
                available,
                "Reasoning resources available.",
            )

        return DegradedModeState(
            DegradedCapability.LIMITED_REASONING,
            available,
            "Some intelligence capabilities available, but general reasoning is limited.",
        )
