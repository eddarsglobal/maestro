from __future__ import annotations

from maestro.intelligence_market import IntelligenceMarket
from .compiler import CognitivePlanCompiler
from .executor import CognitiveFabricExecutor


class CognitiveFabric:
    """
    Composition root for bounded multi-resource cognition.
    """

    def __init__(
        self,
        sovereign_runtime,
        intelligence_market: IntelligenceMarket,
        *,
        allow_market_exploration: bool = False,
    ):
        self.sovereign = sovereign_runtime
        self.market = intelligence_market
        self.compiler = CognitivePlanCompiler()
        self.executor = CognitiveFabricExecutor(
            sovereign_runtime,
            intelligence_market,
            allow_market_exploration=allow_market_exploration,
        )

    def run(self, plan):
        return self.executor.execute(plan)
