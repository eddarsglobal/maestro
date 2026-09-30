from __future__ import annotations

from maestro.adaptive import PromotionEvidence

from .models import AdaptationCandidate, AdaptationStatus, PromotionRecommendation


class OutcomePromotionPlanner:
    "Prepare promotion evidence only. It never activates a policy."

    def prepare(
        self,
        candidate: AdaptationCandidate,
        *,
        replay_score: float,
        baseline_score: float,
        regression_count: int,
        shadow_success_rate: float,
        evaluation_samples: int,
        academy_recommended: bool,
    ) -> tuple[PromotionRecommendation, PromotionEvidence]:
        evidence = PromotionEvidence(
            replay_score=float(replay_score),
            baseline_score=float(baseline_score),
            regression_count=int(regression_count),
            shadow_success_rate=float(shadow_success_rate),
            evaluation_samples=int(evaluation_samples),
            academy_recommended=bool(academy_recommended),
            learning_candidate_id=candidate.candidate_id,
        )

        ready = (
            academy_recommended
            and evidence.delta > 0
            and regression_count == 0
            and shadow_success_rate >= 0.90
            and evaluation_samples >= 10
        )

        candidate.status = (
            AdaptationStatus.PROMOTION_READY
            if ready
            else AdaptationStatus.EVALUATING
        )

        recommendation = PromotionRecommendation(
            candidate_id=candidate.candidate_id,
            ready_for_governance=ready,
            reason=(
                "Academy/shadow evidence is sufficient for AY+EX governance review."
                if ready
                else "Candidate remains in shadow/evaluation; activation is not authorized."
            ),
            replay_delta=evidence.delta,
            regression_count=regression_count,
            shadow_success_rate=shadow_success_rate,
            evaluation_samples=evaluation_samples,
            academy_recommended=academy_recommended,
        )
        return recommendation, evidence
