from __future__ import annotations

from .registry import StrategyRegistry
from .generator import StrategyCandidateGenerator
from .evaluator import StrategyEvaluator
from .selector import StrategySelector
from .journal import StrategyTransitionJournal
from .rollback import StrategyRollbackManager
from .governor import StrategyAdaptationGovernor
from .models import StrategyTransition, StrategyStatus


class StrategicAdaptationEngine:
    """
    Composition root for governed strategy switching.
    """

    def __init__(self):
        self.registry = StrategyRegistry()
        self.generator = StrategyCandidateGenerator()
        self.evaluator = StrategyEvaluator()
        self.selector = StrategySelector()
        self.journal = StrategyTransitionJournal()
        self.rollback = StrategyRollbackManager()
        self.governor = StrategyAdaptationGovernor()

    def propose_and_select(
        self,
        *,
        task_id: str,
        objective: str,
        family: str,
        current_strategy_id: str | None,
        current_method: str,
        trigger,
        available_capabilities: set[str] | None = None,
        risk_score: float = 0.5,
        evidence_urgency: float = 0.5,
        cost_pressure: float = 0.5,
        latency_pressure: float = 0.5,
    ):
        candidates = self.generator.generate(
            task_id=task_id,
            objective=objective,
            family=family,
            current_method=current_method,
            available_capabilities=available_capabilities,
        )

        for c in candidates:
            self.governor.validate_candidate(c)
            try:
                self.registry.register(c)
            except ValueError:
                pass

        evaluations = [
            self.evaluator.evaluate(
                c,
                risk_score=risk_score,
                evidence_urgency=evidence_urgency,
                cost_pressure=cost_pressure,
                latency_pressure=latency_pressure,
            )
            for c in candidates
        ]

        decision = self.selector.select(
            evaluations,
            current_strategy_id=current_strategy_id,
            trigger=trigger,
        )
        selected = self.registry.get(decision.selected_strategy_id)

        return selected, evaluations, decision

    def authorize_transition(
        self,
        *,
        task_id: str,
        current_strategy,
        selected_strategy,
        trigger,
        authorized: bool,
    ):
        self.governor.validate_transition(
            old_objective=current_strategy.objective if current_strategy else selected_strategy.objective,
            new_objective=selected_strategy.objective,
        )

        transition = StrategyTransition(
            task_id=task_id,
            from_strategy_id=current_strategy.strategy_id if current_strategy else None,
            to_strategy_id=selected_strategy.strategy_id,
            trigger=trigger,
            authorized=authorized,
            reversible=selected_strategy.reversible,
        )

        if authorized:
            selected_strategy.status = StrategyStatus.ACTIVE

        self.journal.record(transition)
        return transition
