from __future__ import annotations

from .models import StrategyDecision, StrategyTrigger


class StrategySelector:
    def select(
        self,
        evaluations,
        *,
        current_strategy_id: str | None,
        trigger: StrategyTrigger,
        minimum_switch_score: float = 0.60,
    ) -> StrategyDecision:
        if not evaluations:
            raise LookupError("No strategy evaluations available.")

        best = max(evaluations, key=lambda e: (e.score, e.confidence, e.strategy_id))
        switch = (
            best.score >= minimum_switch_score
            and best.strategy_id != current_strategy_id
        )

        return StrategyDecision(
            selected_strategy_id=best.strategy_id,
            previous_strategy_id=current_strategy_id,
            trigger=trigger,
            switch_required=switch,
            confidence=best.confidence,
            rationale={
                "score": best.score,
                "minimum_switch_score": minimum_switch_score,
                "reversible": best.reversible,
            },
        )
