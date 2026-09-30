from .models import (
    AdaptationCandidate,
    AdaptationDomain,
    AdaptationStatus,
    CandidateEligibility,
    OutcomePattern,
    PromotionRecommendation,
)
from .patterns import OutcomePatternDetector
from .candidates import AdaptationCandidateFactory
from .eligibility import AdaptationEligibilityGate
from .evaluation import DeterministicEvaluationProfile, PromotionEvaluationGate
from .ledger import AdaptationCandidateLedger
from .memory_bridge import OutcomeMemoryBridge
from .bridges import AdaptivePolicyBridge, UnsupportedAdaptationDomain
from .shadow import OutcomeShadowEvaluator
from .promotion import OutcomePromotionPlanner
from .rollback import GovernedRollbackBridge
from .engine import OutcomeGovernedAdaptation

OUTCOME_ADAPTATION_LAWS = (
    "APTE-OGA-01 OUTCOMES MAY INFORM ADAPTATION; OUTCOMES MAY NOT AUTHORIZE ADAPTATION",
    "APTE-OGA-02 ONE OUTCOME MUST NOT CREATE A POLICY",
    "APTE-OGA-03 ATTRIBUTION PRECEDES ADAPTATION",
    "APTE-OGA-04 COUNTER-EVIDENCE MUST REMAIN VISIBLE",
    "APTE-OGA-05 CANDIDATES ENTER SHADOW BEFORE ACTIVATION",
    "APTE-OGA-06 ACADEMY RECOMMENDATION IS EVIDENCE, NOT AUTHORITY",
    "APTE-OGA-07 AY VALIDATION AND EX AUTHORIZATION REMAIN REQUIRED FOR ACTIVATION",
    "APTE-OGA-08 NO CONSTITUTIONAL OR AUTHORITY EXPANSION THROUGH LEARNING",
    "APTE-OGA-09 ROLLBACK REMAINS GOVERNED",
    "APTE-OGA-10 ADAPTATION PROVENANCE MUST BE AUDITABLE",
    "APTE-OGA-11 ADAPTATION PATTERNS MUST BE BOUND TO A CONCRETE SUBJECT",
    "APTE-OGA-12 VERIFIED OUTCOME MEMORY MUST SURVIVE RESTART",
    "APTE-OGA-13 CROSS-VERSION OUTCOME IMPORT MUST PRESERVE PROVENANCE AND IDS",
    "APTE-OGA-14 CANDIDATE LIFECYCLE TRANSITIONS MUST SURVIVE RESTART",
    "APTE-OGA-15 NO-GAIN ADAPTATIONS MUST TERMINATE WITHOUT PROMOTION",
    "APTE-OGA-16 LEARNING-GRADE EVALUATION REQUIRES DETERMINISTIC PROFILE AND SEMANTIC/FORMAT EVIDENCE",
)

__all__ = [
    "AdaptationCandidate", "AdaptationDomain", "AdaptationStatus",
    "CandidateEligibility", "OutcomePattern", "PromotionRecommendation",
    "OutcomePatternDetector", "AdaptationCandidateFactory",
    "AdaptationEligibilityGate", "AdaptationCandidateLedger", "DeterministicEvaluationProfile", "PromotionEvaluationGate", "OutcomeMemoryBridge",
    "AdaptivePolicyBridge", "UnsupportedAdaptationDomain",
    "OutcomeShadowEvaluator", "OutcomePromotionPlanner",
    "GovernedRollbackBridge", "OutcomeGovernedAdaptation",
    "OUTCOME_ADAPTATION_LAWS",
]
