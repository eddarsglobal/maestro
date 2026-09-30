from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable

from maestro.enums import CouncilId
from maestro.tools.registry import ToolRegistry
from .models import AdaptivePolicy, PolicyKind


@dataclass(slots=True)
class ToolObservation:
    task_family: str
    council: str
    tool_name: str
    success: bool
    latency_ms: float
    cost_units: float


@dataclass(slots=True)
class ToolScore:
    tool_name: str
    score: float
    observations: int
    success_rate: float
    mean_latency_ms: float
    mean_cost_units: float


class ToolPolicyLearner:
    def __init__(self):
        self.observations: list[ToolObservation] = []

    def observe(self, observation: ToolObservation) -> None:
        self.observations.append(observation)

    def rank(
        self,
        *,
        registry: ToolRegistry,
        council: CouncilId,
        task_family: str,
        capability: str,
    ) -> list[ToolScore]:
        allowed = {
            spec.name
            for spec in registry.allowed_tools(council)
            if capability in spec.capabilities
        }

        scores: list[ToolScore] = []
        for tool_name in sorted(allowed):
            obs = [
                x for x in self.observations
                if x.tool_name == tool_name
                and x.task_family == task_family
                and x.council == council.value
            ]
            if not obs:
                scores.append(ToolScore(tool_name, 0.50, 0, 0.0, 0.0, 0.0))
                continue

            success = sum(int(x.success) for x in obs) / len(obs)
            latency = sum(x.latency_ms for x in obs) / len(obs)
            cost = sum(x.cost_units for x in obs) / len(obs)

            latency_penalty = min(0.20, latency / 100_000.0)
            cost_penalty = min(0.20, cost / 100.0)
            score = max(0.0, min(1.0, success - latency_penalty - cost_penalty))
            scores.append(ToolScore(tool_name, score, len(obs), success, latency, cost))

        return sorted(scores, key=lambda x: (-x.score, -x.observations, x.tool_name))

    def propose_policy(
        self,
        *,
        version: int,
        rankings: dict[str, list[str]],
        parent_policy_id: str | None = None,
    ) -> AdaptivePolicy:
        return AdaptivePolicy(
            kind=PolicyKind.TOOL_SELECTION,
            version=version,
            parent_policy_id=parent_policy_id,
            description="Tool preference policy distilled from observed quality/cost/latency.",
            parameters={"rankings": rankings},
        )
