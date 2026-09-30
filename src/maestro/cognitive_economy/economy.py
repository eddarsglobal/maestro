from __future__ import annotations

from .complexity import ComplexityEstimator
from .policy import CognitiveEconomyPolicy
from .planner import CognitiveSpendPlanner
from .utility import MarginalUtilityEngine
from .ledger import CognitiveEconomyLedger
from .adaptive_depth import AdaptiveDepthController
from .governor import CognitiveEconomyGovernor


class CognitiveEconomy:
    """
    Composition root for deciding how much cognition a mission deserves.
    """

    def __init__(self):
        self.complexity = ComplexityEstimator()
        self.policy = CognitiveEconomyPolicy()
        self.planner = CognitiveSpendPlanner(self.policy)
        self.utility = MarginalUtilityEngine()
        self.ledger = CognitiveEconomyLedger()
        self.adaptive_depth = AdaptiveDepthController()

    def profile_and_plan(self, **kwargs):
        profile = self.complexity.estimate(**kwargs)
        plan = self.planner.plan(profile)
        return profile, plan

    def governor(self, plan):
        return CognitiveEconomyGovernor(plan)
