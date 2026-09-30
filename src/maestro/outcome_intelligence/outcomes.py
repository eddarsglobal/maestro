from __future__ import annotations

from .attribution import OutcomeAttributor
from .models import VerifiedOutcome


class OutcomeFinalizer:
    def __init__(self, attributor: OutcomeAttributor | None = None):
        self.attributor = attributor or OutcomeAttributor()

    def finalize(self, outcome: VerifiedOutcome) -> VerifiedOutcome:
        if not outcome.ay_verified:
            raise ValueError("Outcome must be AY-verified before finalization.")
        outcome.attributions = self.attributor.attribute(outcome)
        return outcome
