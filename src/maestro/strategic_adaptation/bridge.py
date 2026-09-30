from __future__ import annotations

from .models import StrategyTrigger


class MetaStrategyBridge:
    """
    Maps meta-cognitive signals to strategy adaptation triggers.
    """

    def trigger_from_assessment(self, assessment) -> StrategyTrigger | None:
        actions = {a.value for a in assessment.recommended_actions}
        signals = {s.signal_type.value for s in assessment.signals}

        if "CAPABILITY_GAP" in signals:
            return StrategyTrigger.CAPABILITY_GAP
        if "CONTRADICTION" in signals:
            return StrategyTrigger.CONTRADICTION
        if "RETRY_LOOP" in signals:
            return StrategyTrigger.RETRY_LOOP
        if "EVIDENCE_GAP" in signals:
            return StrategyTrigger.EVIDENCE_GAP
        if "OVERSPEND_RISK" in signals:
            return StrategyTrigger.OVERSPEND
        if "CHANGE_STRATEGY" in actions:
            return StrategyTrigger.META_DRIFT
        return None
