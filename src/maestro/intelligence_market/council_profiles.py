from __future__ import annotations

from dataclasses import dataclass, field

from maestro.sovereign.contracts import IntelligenceCapability


@dataclass(slots=True)
class CouncilCapabilityProfile:
    council_id: str
    primary_capabilities: frozenset[IntelligenceCapability]
    task_families: frozenset[str] = frozenset()
    notes: str = ""


class CouncilProfileRegistry:
    """
    Maps Councils to intelligence capability needs without binding them to models.
    """

    def __init__(self):
        self._profiles: dict[str, CouncilCapabilityProfile] = {}

    def register(self, profile: CouncilCapabilityProfile) -> None:
        self._profiles[profile.council_id] = profile

    def get(self, council_id: str) -> CouncilCapabilityProfile | None:
        return self._profiles.get(council_id)

    @classmethod
    def genesis_defaults(cls) -> "CouncilProfileRegistry":
        r = cls()
        r.register(CouncilCapabilityProfile("EX", frozenset({IntelligenceCapability.GENERAL_REASONING}), frozenset({"ROUTING","PLANNING"})))
        r.register(CouncilCapabilityProfile("AY", frozenset({IntelligenceCapability.GENERAL_REASONING, IntelligenceCapability.HEAVY_REASONING}), frozenset({"VALIDATION","AUDIT"})))
        r.register(CouncilCapabilityProfile("IT", frozenset({IntelligenceCapability.CODE, IntelligenceCapability.HEAVY_CODE}), frozenset({"CODE","DEBUG","REVIEW"})))
        r.register(CouncilCapabilityProfile("SC", frozenset({IntelligenceCapability.GENERAL_REASONING, IntelligenceCapability.CODE}), frozenset({"SECURITY","AUDIT"})))
        r.register(CouncilCapabilityProfile("RX", frozenset({IntelligenceCapability.GENERAL_REASONING}), frozenset({"RESEARCH"})))
        return r
