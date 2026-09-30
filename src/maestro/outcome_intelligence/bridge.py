from __future__ import annotations

from maestro.enums import CouncilId, VerdictScope
from maestro.models import Mission

from .models import DimensionResult, VerifiedOutcome


class OutcomeNotVerified(RuntimeError):
    pass


class MissionOutcomeBridge:
    """Convert a completed/audited Mission into an outcome only after AY SYSTEM verdict."""

    def from_mission(
        self,
        mission: Mission,
        *,
        task_family: str,
        resource_id: str | None,
        dimensions: list[DimensionResult] | tuple[DimensionResult, ...],
        metadata: dict | None = None,
    ) -> VerifiedOutcome:
        verdict = mission.system_verdict
        if verdict is None:
            raise OutcomeNotVerified("Mission has no SYSTEM verdict.")
        if verdict.council != CouncilId.AY or verdict.scope != VerdictScope.SYSTEM:
            raise OutcomeNotVerified("Only AY SYSTEM verdict can verify an outcome.")

        return VerifiedOutcome(
            task_id=mission.task_id,
            task_family=task_family,
            system_verdict=verdict.value.value,
            ay_verified=True,
            resource_id=resource_id,
            dimensions=tuple(dimensions),
            evidence_ids=tuple(verdict.evidence_ids),
            metadata=dict(metadata or {}),
        )
