from __future__ import annotations

from .models import (
    MetaAction,
    MetaAssessment,
    MetaSignalType,
    EpistemicFlag,
)
from .confidence import ConfidenceEstimator
from .contradiction import ContradictionDetector
from .evidence import EvidenceSufficiencyEvaluator
from .drift import StrategyDriftDetector
from .signals import MetaSignalExtractor


class MetaCognitionController:
    """
    Converts observable mission state into bounded operational self-assessment.
    """

    def __init__(self):
        self.confidence = ConfidenceEstimator()
        self.contradiction = ContradictionDetector()
        self.evidence = EvidenceSufficiencyEvaluator()
        self.drift = StrategyDriftDetector()
        self.signals = MetaSignalExtractor()

    def assess(
        self,
        *,
        checkpoint,
        claims: list[dict],
        required_criteria: list[str],
        evidence_by_criterion: dict[str, list[str]],
        verified_fraction: float,
        assumption_fraction: float,
        capability_gap: bool = False,
        human_authorization_required: bool = False,
        blocked_criteria: set[str] | None = None,
    ) -> MetaAssessment:
        evidence_score = self.evidence.score(
            required_criteria=required_criteria,
            evidence_by_criterion=evidence_by_criterion,
            blocked_criteria=blocked_criteria,
        )
        contradiction_score = self.contradiction.score(claims)
        drift_score = self.drift.score(
            progress_score=checkpoint.progress_score,
            evidence_score=evidence_score,
            retries=checkpoint.retries,
            resource_calls=checkpoint.resource_calls,
            cost_fraction=checkpoint.cost_fraction,
            latency_fraction=checkpoint.latency_fraction,
        )
        confidence = self.confidence.estimate(
            evidence_sufficiency=evidence_score,
            contradiction_score=contradiction_score,
            verified_fraction=verified_fraction,
            assumption_fraction=assumption_fraction,
            retry_penalty=min(1.0, checkpoint.retries / 3.0),
        )

        signals = self.signals.extract(
            confidence=confidence,
            evidence_sufficiency=evidence_score,
            contradiction_score=contradiction_score,
            strategy_drift_score=drift_score,
            checkpoint=checkpoint,
            capability_gap=capability_gap,
            human_authorization_required=human_authorization_required,
        )

        actions: list[MetaAction] = []

        signal_types = {s.signal_type for s in signals}

        if MetaSignalType.HUMAN_AUTHORIZATION_REQUIRED in signal_types:
            actions.append(MetaAction.REQUEST_HUMAN_APPROVAL)

        if MetaSignalType.CAPABILITY_GAP in signal_types:
            actions.append(MetaAction.ESCALATE_EX)

        if MetaSignalType.CONTRADICTION in signal_types:
            actions.append(MetaAction.REQUEST_MORE_EVIDENCE)
            actions.append(MetaAction.ESCALATE_AY)

        if MetaSignalType.EVIDENCE_GAP in signal_types:
            actions.append(MetaAction.REQUEST_MORE_EVIDENCE)

        if MetaSignalType.RETRY_LOOP in signal_types or MetaSignalType.STRATEGY_DRIFT in signal_types:
            actions.append(MetaAction.CHANGE_STRATEGY)

        if MetaSignalType.STALE_ASSUMPTION in signal_types:
            actions.append(MetaAction.REVALIDATE_ASSUMPTIONS)

        if MetaSignalType.LOW_CONFIDENCE in signal_types and MetaSignalType.OVERSPEND_RISK not in signal_types:
            actions.append(MetaAction.DEEPEN_COGNITION)

        if MetaSignalType.OVERSPEND_RISK in signal_types and confidence >= 0.75 and evidence_score >= 0.85:
            actions.append(MetaAction.REDUCE_COGNITION)

        if not actions:
            actions.append(MetaAction.CONTINUE)

        # De-duplicate while preserving order.
        deduped = []
        for a in actions:
            if a not in deduped:
                deduped.append(a)

        hard_block = (
            human_authorization_required
            or capability_gap
            or contradiction_score >= 0.80
        )

        if hard_block and MetaAction.BLOCK not in deduped:
            deduped.append(MetaAction.BLOCK)

        if hard_block:
            epistemic = EpistemicFlag.BLOCKED
        elif evidence_score >= 0.95 and verified_fraction >= 0.90 and contradiction_score == 0.0:
            epistemic = EpistemicFlag.VERIFIED
        elif assumption_fraction > 0.25:
            epistemic = EpistemicFlag.ASSUMED
        elif confidence >= 0.75:
            epistemic = EpistemicFlag.INFERRED
        else:
            epistemic = EpistemicFlag.UNKNOWN

        return MetaAssessment(
            task_id=checkpoint.task_id,
            confidence=confidence,
            evidence_sufficiency=evidence_score,
            contradiction_score=contradiction_score,
            strategy_drift_score=drift_score,
            signals=signals,
            recommended_actions=deduped,
            epistemic_status=epistemic,
            safe_to_continue=not hard_block,
            rationale={
                "strategy_id": checkpoint.strategy_id,
                "progress_score": checkpoint.progress_score,
                "retries": checkpoint.retries,
                "resource_calls": checkpoint.resource_calls,
            },
        )
