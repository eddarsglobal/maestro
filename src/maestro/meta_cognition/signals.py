from __future__ import annotations

from .models import MetaSignal, MetaSignalType, EpistemicFlag


class MetaSignalExtractor:
    def extract(
        self,
        *,
        confidence: float,
        evidence_sufficiency: float,
        contradiction_score: float,
        strategy_drift_score: float,
        checkpoint,
        capability_gap: bool = False,
        human_authorization_required: bool = False,
    ) -> list[MetaSignal]:
        signals: list[MetaSignal] = []

        if confidence < 0.55:
            signals.append(MetaSignal(
                MetaSignalType.LOW_CONFIDENCE,
                severity=1.0 - confidence,
                confidence=0.95,
            ))

        if contradiction_score > 0.0:
            signals.append(MetaSignal(
                MetaSignalType.CONTRADICTION,
                severity=contradiction_score,
                confidence=0.95,
            ))

        if evidence_sufficiency < 0.75:
            signals.append(MetaSignal(
                MetaSignalType.EVIDENCE_GAP,
                severity=1.0 - evidence_sufficiency,
                confidence=0.95,
            ))

        if strategy_drift_score >= 0.60:
            signals.append(MetaSignal(
                MetaSignalType.STRATEGY_DRIFT,
                severity=strategy_drift_score,
                confidence=0.90,
            ))

        if checkpoint.retries >= 3:
            signals.append(MetaSignal(
                MetaSignalType.RETRY_LOOP,
                severity=min(1.0, checkpoint.retries / 5.0),
                confidence=1.0,
            ))

        if max(checkpoint.cost_fraction, checkpoint.latency_fraction) >= 0.85:
            signals.append(MetaSignal(
                MetaSignalType.OVERSPEND_RISK,
                severity=max(checkpoint.cost_fraction, checkpoint.latency_fraction),
                confidence=1.0,
            ))

        if capability_gap:
            signals.append(MetaSignal(
                MetaSignalType.CAPABILITY_GAP,
                severity=1.0,
                confidence=1.0,
            ))

        if human_authorization_required:
            signals.append(MetaSignal(
                MetaSignalType.HUMAN_AUTHORIZATION_REQUIRED,
                severity=1.0,
                confidence=1.0,
            ))

        stale = [
            k for k, status in checkpoint.assumptions.items()
            if status in {EpistemicFlag.ASSUMED, EpistemicFlag.UNKNOWN}
        ]
        if stale:
            signals.append(MetaSignal(
                MetaSignalType.STALE_ASSUMPTION,
                severity=min(1.0, len(stale) / max(1, len(checkpoint.assumptions))),
                confidence=0.90,
                details={"assumptions": stale},
            ))

        return signals
