from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from maestro.enums import CouncilId
from maestro.models import Mission
from maestro.orchestration.retry_ledger import RetryAttempt, RetryAssessment


class OPSignal(StrEnum):
    NONE = "NONE"
    RETRY_RISK = "RETRY_RISK"
    BREAKOUT_RECOMMENDED = "BREAKOUT_RECOMMENDED"
    HUMAN_REVIEW_RECOMMENDED = "HUMAN_REVIEW_RECOMMENDED"


@dataclass(slots=True)
class OPDecision:
    signal: OPSignal
    assessment: RetryAssessment | None
    reason: str


class LiveOPSupervisor:
    """
    Real-time OP supervision over failed work.

    OP can recommend breakout. EX remains the only authority that can activate RX.
    """

    def __init__(self, kernel):
        self.kernel = kernel

    def observe_failure(
        self,
        mission: Mission,
        *,
        worker: CouncilId,
        criterion_id: str,
        failure_mode: str,
        strategy: str,
        evidence_ids: list[str] | None = None,
    ) -> OPDecision:
        attempt = RetryAttempt(
            task_id=mission.task_id,
            worker=worker,
            criterion_id=criterion_id,
            failure_mode=failure_mode,
            strategy=strategy,
            new_evidence=list(evidence_ids or []),
        )
        assessment = self.kernel.record_retry(mission, attempt)

        if assessment.breakout_recommended:
            return OPDecision(
                OPSignal.BREAKOUT_RECOMMENDED,
                assessment,
                "OP recommends breakout to EX because materially equivalent failure/strategy repeated.",
            )
        if assessment.same_failure_same_strategy_count >= 2:
            return OPDecision(
                OPSignal.RETRY_RISK,
                assessment,
                "OP warns against another blind retry.",
            )
        return OPDecision(OPSignal.NONE, assessment, "No loop escalation yet.")
