from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class ShadowObservation:
    task_id: str
    active_policy_id: str
    shadow_policy_id: str
    active_score: float
    shadow_score: float
    active_output_ref: str | None = None
    shadow_output_ref: str | None = None

    @property
    def delta(self) -> float:
        return self.shadow_score - self.active_score


class LiveShadowEvaluator:
    def __init__(self):
        self.observations: list[ShadowObservation] = []

    def record(self, observation: ShadowObservation) -> None:
        self.observations.append(observation)

    def summarize(self, shadow_policy_id: str) -> dict[str, Any]:
        obs = [o for o in self.observations if o.shadow_policy_id == shadow_policy_id]
        if not obs:
            return {"samples": 0, "mean_delta": 0.0, "wins": 0, "losses": 0}
        deltas = [o.delta for o in obs]
        return {
            "samples": len(obs),
            "mean_delta": sum(deltas) / len(deltas),
            "wins": sum(1 for d in deltas if d > 0),
            "losses": sum(1 for d in deltas if d < 0),
        }
