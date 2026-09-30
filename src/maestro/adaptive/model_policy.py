from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .models import AdaptivePolicy, PolicyKind


@dataclass(frozen=True, slots=True)
class ModelProfile:
    model_id: str
    provider: str
    capabilities: frozenset[str]
    max_risk: int = 5


@dataclass(slots=True)
class ModelObservation:
    model_id: str
    council: str
    task_family: str
    quality: float
    success: bool
    latency_ms: float
    cost_units: float


@dataclass(slots=True)
class ModelScore:
    model_id: str
    score: float
    observations: int
    mean_quality: float
    success_rate: float
    mean_cost: float
    mean_latency: float


class ModelPolicyLearner:
    def __init__(self):
        self.observations: list[ModelObservation] = []

    def observe(self, observation: ModelObservation) -> None:
        self.observations.append(observation)

    def rank(
        self,
        *,
        profiles: Iterable[ModelProfile],
        council: str,
        task_family: str,
        required_capabilities: set[str],
        risk: int,
        min_quality: float = 0.80,
    ) -> list[ModelScore]:
        eligible = [
            p for p in profiles
            if required_capabilities.issubset(p.capabilities)
            and risk <= p.max_risk
        ]

        scores: list[ModelScore] = []
        for profile in eligible:
            obs = [
                x for x in self.observations
                if x.model_id == profile.model_id
                and x.council == council
                and x.task_family == task_family
            ]
            if not obs:
                scores.append(ModelScore(profile.model_id, 0.40, 0, 0.0, 0.0, 0.0, 0.0))
                continue

            quality = sum(x.quality for x in obs) / len(obs)
            success = sum(int(x.success) for x in obs) / len(obs)
            cost = sum(x.cost_units for x in obs) / len(obs)
            latency = sum(x.latency_ms for x in obs) / len(obs)

            if quality < min_quality:
                score = 0.0
            else:
                score = (
                    0.55 * quality
                    + 0.35 * success
                    + 0.10 * max(0.0, 1.0 - min(1.0, cost / 100.0))
                    - min(0.10, latency / 200_000.0)
                )
            scores.append(ModelScore(profile.model_id, max(0.0, score), len(obs), quality, success, cost, latency))

        return sorted(scores, key=lambda x: (-x.score, -x.observations, x.mean_cost, x.model_id))

    def propose_policy(
        self,
        *,
        version: int,
        selections: dict[str, str],
        parent_policy_id: str | None = None,
    ) -> AdaptivePolicy:
        return AdaptivePolicy(
            kind=PolicyKind.MODEL_SELECTION,
            version=version,
            parent_policy_id=parent_policy_id,
            description="Provider-neutral model-selection policy learned from eval observations.",
            parameters={"selections": selections},
        )
