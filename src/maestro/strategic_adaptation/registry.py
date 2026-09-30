from __future__ import annotations

from .models import StrategyCandidate


class StrategyRegistry:
    """
    Strategy methods are registered independently from models/providers.
    """

    def __init__(self):
        self._strategies: dict[str, StrategyCandidate] = {}

    def register(self, strategy: StrategyCandidate) -> None:
        if strategy.strategy_id in self._strategies:
            raise ValueError(f"Duplicate strategy: {strategy.strategy_id}")
        self._strategies[strategy.strategy_id] = strategy

    def get(self, strategy_id: str) -> StrategyCandidate:
        return self._strategies[strategy_id]

    def all(self) -> list[StrategyCandidate]:
        return list(self._strategies.values())

    def by_family(self, family: str) -> list[StrategyCandidate]:
        return [s for s in self._strategies.values() if s.family == family]
