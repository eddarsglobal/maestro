from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class CalibrationObservation:
    predicted_confidence: float
    success: bool
    verified_quality: float


class ConfidenceCalibrationLedger:
    """
    Tracks whether MAESTRO's confidence is calibrated against verified outcomes.
    """

    def __init__(self):
        self.rows: list[CalibrationObservation] = []

    def record(self, predicted_confidence: float, success: bool, verified_quality: float) -> None:
        self.rows.append(CalibrationObservation(
            max(0.0, min(1.0, predicted_confidence)),
            bool(success),
            max(0.0, min(1.0, verified_quality)),
        ))

    def calibration_error(self) -> float | None:
        if not self.rows:
            return None
        errors = []
        for r in self.rows:
            observed = r.verified_quality if r.success else 0.0
            errors.append(abs(r.predicted_confidence - observed))
        return sum(errors) / len(errors)

    def overconfidence_rate(self, margin: float = 0.20) -> float | None:
        if not self.rows:
            return None
        over = 0
        for r in self.rows:
            observed = r.verified_quality if r.success else 0.0
            if r.predicted_confidence - observed > margin:
                over += 1
        return over / len(self.rows)
