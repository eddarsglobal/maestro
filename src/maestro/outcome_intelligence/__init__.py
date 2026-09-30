from .models import (
    OutcomeDimension,
    AttributionTarget,
    AttributionEffect,
    DimensionResult,
    AttributionFinding,
    VerifiedOutcome,
    MarketLearningDirective,
)
from .attribution import OutcomeAttributor
from .ledger import OutcomeLedger
from .bridge import MissionOutcomeBridge, OutcomeNotVerified
from .outcomes import OutcomeFinalizer
from .counterfactual import CounterfactualComparator, CounterfactualAssessment
from .scorecards import OutcomeScoreCard, OutcomeScoreCardEngine
from .priors import AdvisoryPrior, OutcomePriorEngine
from .drift import OutcomeDriftSignal, OutcomeDriftDetector
from .market_bridge import OutcomeMarketBridge, OutcomeMarketApplyResult
from .outcome_intelligence import OutcomeIntelligence

OUTCOME_LAWS = (
    "APTE-OUTCOME-01 VERIFIED OUTCOME PRECEDES LEARNING",
    "APTE-OUTCOME-02 CORRELATION IS NOT CAUSATION",
    "APTE-OUTCOME-03 STRATEGY CREDIT MUST ACCOUNT FOR CONFOUNDERS",
    "APTE-OUTCOME-04 ONE SUCCESS DOES NOT CREATE A RULE",
    "APTE-OUTCOME-05 FAILURES ARE LEARNING SIGNALS, NOT AUTOMATIC BANS",
    "APTE-OUTCOME-06 BASELINES MUST BE PRESERVED",
    "APTE-OUTCOME-07 CONDITIONAL PERFORMANCE BEATS UNIVERSAL RANKING",
    "APTE-OUTCOME-08 LEARNED PRIORS ARE ADVISORY",
    "APTE-OUTCOME-09 EXTERNAL CHANGES REQUIRE ATTRIBUTION CAUTION",
    "APTE-OUTCOME-10 ACADEMY / PROMOTION GATE CONTROLS ACTIVATION",
    "APTE-OUTCOME-11 OUTCOME MEMORY MUST BE COMPACT AND AUDITABLE",
    "APTE-OUTCOME-12 HUMAN CORRECTION IS SCOPED AND PROVENANCED",
)

__all__ = [
    "OutcomeDimension", "AttributionTarget", "AttributionEffect",
    "DimensionResult", "AttributionFinding", "VerifiedOutcome",
    "MarketLearningDirective", "OutcomeAttributor", "OutcomeLedger",
    "MissionOutcomeBridge", "OutcomeNotVerified", "OutcomeFinalizer",
    "CounterfactualComparator", "CounterfactualAssessment",
    "OutcomeScoreCard", "OutcomeScoreCardEngine", "AdvisoryPrior",
    "OutcomePriorEngine", "OutcomeDriftSignal", "OutcomeDriftDetector",
    "OutcomeIntelligence", "OutcomeMarketBridge", "OutcomeMarketApplyResult", "OUTCOME_LAWS",
]
