from __future__ import annotations

from maestro.cognitive_economy import MarginalUtilityDecision


class MetaEconomyBridge:
    """
    Uses meta-assessment to suggest whether cognitive depth should change.
    """

    def recommend_depth_change(self, assessment):
        actions = {a.value for a in assessment.recommended_actions}
        if "DEEPEN_COGNITION" in actions:
            return "DEEPEN"
        if "REDUCE_COGNITION" in actions:
            return "REDUCE"
        return "KEEP"
