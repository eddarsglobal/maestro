from __future__ import annotations

from .controller import MetaCognitionController
from .governor import MetaCognitionGovernor
from .calibration import ConfidenceCalibrationLedger


class MetaCognition:
    """
    Composition root for MAESTRO operational self-monitoring.
    """

    def __init__(self):
        self.controller = MetaCognitionController()
        self.governor = MetaCognitionGovernor()
        self.calibration = ConfidenceCalibrationLedger()

    def assess(self, **kwargs):
        assessment = self.controller.assess(**kwargs)
        self.governor.validate_recommendations(assessment)
        return assessment
