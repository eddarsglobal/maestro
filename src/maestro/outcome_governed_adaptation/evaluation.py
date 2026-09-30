from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field

from maestro.sovereign import InferenceExecutionProfile


_REQUIRED_DIMENSIONS = (
    "SEMANTIC_CORRECTNESS",
    "FORMAT_COMPLIANCE",
)


@dataclass(frozen=True)
class DeterministicEvaluationProfile:
    provider_id: str
    route: str
    temperature: float
    seed: int
    num_predict: int
    think: bool | None = None
    suite_version: str = "academy-v1.1.0"
    scoring_dimensions: tuple[str, ...] = field(
        default=_REQUIRED_DIMENSIONS
    )

    def __post_init__(self) -> None:
        if not self.provider_id:
            raise ValueError("provider_id is required")
        if not self.route:
            raise ValueError("route is required")
        if int(self.num_predict) <= 0:
            raise ValueError("num_predict must be > 0")
        if not self.suite_version:
            raise ValueError("suite_version is required")

    @property
    def learning_eligible(self) -> bool:
        dimensions = set(self.scoring_dimensions)
        return (
            float(self.temperature) == 0.0
            and self.seed is not None
            and int(self.num_predict) > 0
            and set(_REQUIRED_DIMENSIONS).issubset(dimensions)
        )

    def to_dict(self) -> dict:
        return {
            "provider_id": self.provider_id,
            "route": self.route,
            "temperature": float(self.temperature),
            "seed": int(self.seed),
            "num_predict": int(self.num_predict),
            "think": self.think,
            "suite_version": self.suite_version,
            "scoring_dimensions": list(self.scoring_dimensions),
        }

    @property
    def profile_id(self) -> str:
        payload = json.dumps(
            self.to_dict(),
            sort_keys=True,
            separators=(",", ":"),
        )
        return (
            "EVP-"
            + hashlib.sha256(payload.encode("utf-8")).hexdigest()[:12].upper()
        )

    def to_execution_profile(self) -> InferenceExecutionProfile:
        return InferenceExecutionProfile(
            temperature=float(self.temperature),
            seed=int(self.seed),
            thinking=self.think,
            profile_ref=self.profile_id,
        )

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            provider_id=str(data["provider_id"]),
            route=str(data["route"]),
            temperature=float(data["temperature"]),
            seed=int(data["seed"]),
            num_predict=int(data["num_predict"]),
            think=data.get("think"),
            suite_version=str(
                data.get("suite_version") or "academy-v1.1.0"
            ),
            scoring_dimensions=tuple(
                str(x)
                for x in data.get(
                    "scoring_dimensions",
                    _REQUIRED_DIMENSIONS,
                )
            ),
        )


class PromotionEvaluationGate:
    def assess(
        self,
        profile: DeterministicEvaluationProfile | None,
        *,
        semantic_success_rate: float,
        format_success_rate: float,
        semantic_regression_count: int,
        format_regression_count: int,
        evaluation_samples: int,
        min_success_rate: float = 0.90,
        min_samples: int = 10,
    ) -> tuple[bool, str]:
        if profile is None:
            return False, "missing deterministic evaluation profile"

        if not profile.learning_eligible:
            return False, "evaluation profile is not learning-eligible"

        if int(evaluation_samples) < int(min_samples):
            return False, "insufficient evaluation samples"

        if int(semantic_regression_count) != 0:
            return False, "semantic regressions detected"

        if int(format_regression_count) != 0:
            return False, "format regressions detected"

        if float(semantic_success_rate) < float(min_success_rate):
            return False, "semantic success rate below threshold"

        if float(format_success_rate) < float(min_success_rate):
            return False, "format success rate below threshold"

        return True, "deterministic semantic+format evidence is learning-eligible"
