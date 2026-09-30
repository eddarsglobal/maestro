from __future__ import annotations

from pathlib import Path
from typing import Iterable

from maestro.adaptive import AdaptiveController
from maestro.outcome_intelligence import VerifiedOutcome

from .bridges import AdaptivePolicyBridge
from .candidates import AdaptationCandidateFactory
from .eligibility import AdaptationEligibilityGate
from .evaluation import DeterministicEvaluationProfile, PromotionEvaluationGate
from .ledger import AdaptationCandidateLedger
from .memory_bridge import OutcomeMemoryBridge
from .models import AdaptationCandidate, AdaptationStatus
from .patterns import OutcomePatternDetector
from .promotion import OutcomePromotionPlanner
from .rollback import GovernedRollbackBridge
from .shadow import OutcomeShadowEvaluator


class OutcomeGovernedAdaptation:
    # Converts repeated attributable outcomes into governed adaptation candidates.
    # It may propose, record, and stage SHADOW candidates, but exposes no activation shortcut.

    def __init__(self, path: str | Path | None = None):
        self.patterns = OutcomePatternDetector()
        self.factory = AdaptationCandidateFactory()
        self.eligibility = AdaptationEligibilityGate()
        self.evaluation_gate = PromotionEvaluationGate()
        self.ledger = AdaptationCandidateLedger(path)
        self.ledger.load()
        self.policy_bridge = AdaptivePolicyBridge()
        self.shadow = OutcomeShadowEvaluator()
        self.promotion = OutcomePromotionPlanner()
        self.rollback = GovernedRollbackBridge()
        self.memory = OutcomeMemoryBridge()

    def propose_from_outcomes(self, outcomes: Iterable[VerifiedOutcome]) -> list[AdaptationCandidate]:
        candidates: list[AdaptationCandidate] = []
        existing_keys = {row.key for row in self.ledger.all()}

        for pattern in self.patterns.detect(outcomes):
            candidate = self.factory.build(pattern)
            decision = self.eligibility.evaluate(candidate)
            candidate.metadata["eligibility_reason"] = decision.reason

            if not decision.eligible:
                candidate.status = AdaptationStatus.BLOCKED
                continue

            candidate.status = AdaptationStatus.ELIGIBLE
            if candidate.key in existing_keys:
                continue

            self.ledger.record(candidate)
            existing_keys.add(candidate.key)
            candidates.append(candidate)

        return candidates

    def propose_from_memory(
        self,
        outcome_intelligence,
        *,
        task_family: str | None = None,
        resource_id: str | None = None,
    ) -> list[AdaptationCandidate]:
        return self.memory.propose(
            self,
            outcome_intelligence,
            task_family=task_family,
            resource_id=resource_id,
        )

    def stage_shadow(
        self,
        candidate: AdaptationCandidate,
        controller: AdaptiveController,
        *,
        version: int = 1,
    ):
        if candidate.status is not AdaptationStatus.ELIGIBLE:
            raise ValueError("Only ELIGIBLE outcome-derived candidates may enter SHADOW.")

        policy = self.policy_bridge.stage_shadow(
            candidate,
            controller,
            version=version,
        )
        self.ledger.checkpoint(candidate)
        return policy

    def close_no_gain(
        self,
        candidate: AdaptationCandidate,
        *,
        replay_delta: float,
        improvement_count: int,
        regression_count: int,
        academy_recommended: bool,
        baseline_equivalent: bool,
        reason: str = "NO_GAIN_REDUNDANT",
        epsilon: float = 1e-12,
    ) -> AdaptationCandidate:
        # Terminal non-promotion disposition for proven redundant candidates.
        if candidate.status is not AdaptationStatus.EVALUATING:
            raise ValueError(
                "Only EVALUATING candidates may be closed as no-gain."
            )

        delta = float(replay_delta)
        improvements = int(improvement_count)
        regressions = int(regression_count)

        redundant = (
            bool(baseline_equivalent)
            and abs(delta) <= float(epsilon)
            and improvements == 0
            and regressions == 0
            and not bool(academy_recommended)
        )

        if not redundant:
            raise ValueError(
                "Candidate is not proven redundant/no-gain; terminal rejection denied."
            )

        candidate.status = AdaptationStatus.REJECTED
        candidate.metadata["terminal_disposition"] = str(reason)
        candidate.metadata["terminal_evidence"] = {
            "replay_delta": delta,
            "improvement_count": improvements,
            "regression_count": regressions,
            "academy_recommended": bool(academy_recommended),
            "baseline_equivalent": bool(baseline_equivalent),
            "epsilon": float(epsilon),
        }

        self.ledger.checkpoint(candidate)
        return candidate

    def prepare_promotion(
        self,
        candidate: AdaptationCandidate,
        *,
        replay_score: float,
        baseline_score: float,
        regression_count: int,
        shadow_success_rate: float,
        evaluation_samples: int,
        academy_recommended: bool,
        evaluation_profile: DeterministicEvaluationProfile | None = None,
        semantic_success_rate: float | None = None,
        format_success_rate: float | None = None,
        format_regression_count: int = 0,
    ):
        if candidate.status not in {
            AdaptationStatus.SHADOW,
            AdaptationStatus.EVALUATING,
        }:
            raise ValueError(
                "Promotion evidence may only be prepared for a SHADOW/EVALUATING candidate."
            )

        semantic_rate = float(
            shadow_success_rate
            if semantic_success_rate is None
            else semantic_success_rate
        )
        format_rate = float(
            0.0
            if format_success_rate is None
            else format_success_rate
        )

        learning_eligible, gate_reason = self.evaluation_gate.assess(
            evaluation_profile,
            semantic_success_rate=semantic_rate,
            format_success_rate=format_rate,
            semantic_regression_count=int(regression_count),
            format_regression_count=int(format_regression_count),
            evaluation_samples=int(evaluation_samples),
        )

        candidate.metadata["evaluation_learning_eligible"] = bool(
            learning_eligible
        )
        candidate.metadata["evaluation_gate_reason"] = gate_reason
        candidate.metadata["semantic_success_rate"] = semantic_rate
        candidate.metadata["format_success_rate"] = format_rate
        candidate.metadata["semantic_regression_count"] = int(
            regression_count
        )
        candidate.metadata["format_regression_count"] = int(
            format_regression_count
        )

        if evaluation_profile is not None:
            candidate.metadata["evaluation_profile_id"] = (
                evaluation_profile.profile_id
            )
            candidate.metadata["evaluation_profile"] = (
                evaluation_profile.to_dict()
            )
        else:
            candidate.metadata.pop("evaluation_profile_id", None)
            candidate.metadata.pop("evaluation_profile", None)

        recommendation, evidence = self.promotion.prepare(
            candidate,
            replay_score=replay_score,
            baseline_score=baseline_score,
            regression_count=(
                int(regression_count)
                + int(format_regression_count)
            ),
            shadow_success_rate=semantic_rate,
            evaluation_samples=evaluation_samples,
            academy_recommended=(
                bool(academy_recommended)
                and bool(learning_eligible)
            ),
        )

        self.ledger.checkpoint(candidate)
        return recommendation, evidence
