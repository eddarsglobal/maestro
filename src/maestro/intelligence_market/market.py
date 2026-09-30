from __future__ import annotations

from pathlib import Path

from maestro.sovereign import IntelligenceResourceRegistry
from .ledger import IntelligenceMarketLedger
from .selector import IntelligenceMarketSelector
from .models import MarketObservation, MarketPolicy


class IntelligenceMarket:
    """
    Performance market over *eligible* resources only.

    Sovereign registry decides eligibility first.
    Market decides preference second.
    """

    def __init__(
        self,
        registry: IntelligenceResourceRegistry,
        ledger: IntelligenceMarketLedger | None = None,
        policy: MarketPolicy | None = None,
    ):
        self.registry = registry
        self.ledger = ledger or IntelligenceMarketLedger()
        self.selector = IntelligenceMarketSelector(self.ledger, policy)

    def observe(self, observation: MarketObservation) -> None:
        self.ledger.record(observation)

    def choose(
        self,
        *,
        capability,
        task_family: str,
        council_id: str | None,
        requires_tools: bool = False,
        allow_exploration: bool = True,
    ):
        eligible = self.registry.eligible(capability, requires_tools=requires_tools)
        return self.selector.select(
            eligible_resource_ids=[r.resource_id for r in eligible],
            task_family=task_family,
            council_id=council_id,
            allow_exploration=allow_exploration,
        )
