from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any

from maestro.sovereign.generic_descriptors import (
    GenericResourceDescriptor,
)


MINIMUM_SUFFICIENT_RESOURCE_VERSION = 1


class MinimumSufficientResourceInvariantError(ValueError):
    pass


def _required_text(value: str, name: str) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{name} must be a string.")

    normalized = value.strip()

    if not normalized:
        raise ValueError(f"{name} must not be empty.")

    return normalized


def _score(value: float, name: str) -> float:
    if isinstance(value, bool) or not isinstance(
        value,
        (int, float),
    ):
        raise TypeError(
            f"{name} must be a numeric score."
        )

    normalized = float(value)

    if not 0.0 <= normalized <= 1.0:
        raise ValueError(
            f"{name} must be between 0.0 and 1.0."
        )

    return normalized


def _string_frozenset(
    values: frozenset[str],
    name: str,
    *,
    require_nonempty: bool = False,
) -> frozenset[str]:
    if not isinstance(values, frozenset):
        raise TypeError(
            f"{name} must be a frozenset."
        )

    normalized = frozenset(
        _required_text(item, name)
        for item in values
    )

    if require_nonempty and not normalized:
        raise MinimumSufficientResourceInvariantError(
            f"{name} must not be empty."
        )

    return normalized


def _evidence_refs(
    values: tuple[str, ...],
) -> tuple[str, ...]:
    if not isinstance(values, tuple):
        raise TypeError(
            "evidence_refs must be a tuple."
        )

    normalized = tuple(
        _required_text(item, "evidence_ref")
        for item in values
    )

    if len(normalized) != len(set(normalized)):
        raise MinimumSufficientResourceInvariantError(
            "evidence_refs must be unique."
        )

    return normalized


@dataclass(frozen=True, slots=True)
class GovernedResourceEconomyProfile:
    """
    Passive economic evidence for one generic resource.

    Scores describe a resource for selection only.
    They grant no trust, execution, or other authority.
    """

    resource_id: str
    quality_score: float
    cost_score: float
    latency_score: float
    resource_mass_score: float
    evidence_refs: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "resource_id",
            _required_text(
                self.resource_id,
                "resource_id",
            ),
        )

        for name in (
            "quality_score",
            "cost_score",
            "latency_score",
            "resource_mass_score",
        ):
            object.__setattr__(
                self,
                name,
                _score(
                    getattr(self, name),
                    name,
                ),
            )

        object.__setattr__(
            self,
            "evidence_refs",
            _evidence_refs(self.evidence_refs),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "resource_id": self.resource_id,
            "quality_score": self.quality_score,
            "cost_score": self.cost_score,
            "latency_score": self.latency_score,
            "resource_mass_score": (
                self.resource_mass_score
            ),
            "evidence_refs": list(self.evidence_refs),
        }


@dataclass(frozen=True, slots=True)
class MinimumSufficientResourcePolicy:
    """Explicit mission envelope for minimum-sufficient selection."""

    required_capability_ids: frozenset[str]
    min_quality_score: float = 0.0
    max_cost_score: float = 1.0
    max_latency_score: float = 1.0
    max_resource_mass_score: float = 1.0
    forbidden_resource_ids: frozenset[str] = frozenset()

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "required_capability_ids",
            _string_frozenset(
                self.required_capability_ids,
                "required_capability_ids",
                require_nonempty=True,
            ),
        )

        object.__setattr__(
            self,
            "forbidden_resource_ids",
            _string_frozenset(
                self.forbidden_resource_ids,
                "forbidden_resource_ids",
            ),
        )

        for name in (
            "min_quality_score",
            "max_cost_score",
            "max_latency_score",
            "max_resource_mass_score",
        ):
            object.__setattr__(
                self,
                name,
                _score(
                    getattr(self, name),
                    name,
                ),
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "required_capability_ids": sorted(
                self.required_capability_ids
            ),
            "min_quality_score": (
                self.min_quality_score
            ),
            "max_cost_score": self.max_cost_score,
            "max_latency_score": (
                self.max_latency_score
            ),
            "max_resource_mass_score": (
                self.max_resource_mass_score
            ),
            "forbidden_resource_ids": sorted(
                self.forbidden_resource_ids
            ),
        }


@dataclass(frozen=True, slots=True)
class MinimumSufficientResourceCandidate:
    resource: GenericResourceDescriptor
    economy: GovernedResourceEconomyProfile
    excess_capability_count: int
    rank: tuple[
        int,
        float,
        float,
        float,
        float,
        str,
    ]

    def __post_init__(self) -> None:
        if not isinstance(
            self.resource,
            GenericResourceDescriptor,
        ):
            raise TypeError(
                "resource must be a "
                "GenericResourceDescriptor."
            )

        if not isinstance(
            self.economy,
            GovernedResourceEconomyProfile,
        ):
            raise TypeError(
                "economy must be a "
                "GovernedResourceEconomyProfile."
            )

        if self.resource.resource_id != self.economy.resource_id:
            raise MinimumSufficientResourceInvariantError(
                "Resource/economy identity mismatch."
            )

        if (
            isinstance(self.excess_capability_count, bool)
            or not isinstance(
                self.excess_capability_count,
                int,
            )
            or self.excess_capability_count < 0
        ):
            raise MinimumSufficientResourceInvariantError(
                "excess_capability_count must be "
                "a non-negative integer."
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "resource": self.resource.to_dict(),
            "economy": self.economy.to_dict(),
            "excess_capability_count": (
                self.excess_capability_count
            ),
            "rank": list(self.rank),
        }


@dataclass(frozen=True, slots=True)
class MinimumSufficientResourceDecision:
    policy: MinimumSufficientResourcePolicy
    selected_resource_id: str
    sufficient_candidates: tuple[
        MinimumSufficientResourceCandidate,
        ...,
    ]
    rejected_resource_ids: tuple[str, ...]
    selection_only: bool = True
    execution_authorized: bool = False
    activation_authorized: bool = False
    trust_asserted: bool = False
    system_truth_asserted: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "selected_resource_id",
            _required_text(
                self.selected_resource_id,
                "selected_resource_id",
            ),
        )

        if not isinstance(
            self.policy,
            MinimumSufficientResourcePolicy,
        ):
            raise TypeError(
                "policy must be a "
                "MinimumSufficientResourcePolicy."
            )

        if not isinstance(
            self.sufficient_candidates,
            tuple,
        ):
            raise TypeError(
                "sufficient_candidates must be a tuple."
            )

        if not self.sufficient_candidates:
            raise MinimumSufficientResourceInvariantError(
                "Decision requires at least one "
                "sufficient candidate."
            )

        for candidate in self.sufficient_candidates:
            if not isinstance(
                candidate,
                MinimumSufficientResourceCandidate,
            ):
                raise TypeError(
                    "sufficient_candidates contains "
                    "an invalid candidate."
                )

        expected_selected = (
            self.sufficient_candidates[0]
            .resource.resource_id
        )

        if self.selected_resource_id != expected_selected:
            raise MinimumSufficientResourceInvariantError(
                "Selected resource must be the first "
                "minimum-ranked sufficient candidate."
            )

        if not isinstance(
            self.rejected_resource_ids,
            tuple,
        ):
            raise TypeError(
                "rejected_resource_ids must be a tuple."
            )

        forbidden = {
            "selection_only": self.selection_only is not True,
            "execution_authorized": (
                self.execution_authorized is not False
            ),
            "activation_authorized": (
                self.activation_authorized is not False
            ),
            "trust_asserted": (
                self.trust_asserted is not False
            ),
            "system_truth_asserted": (
                self.system_truth_asserted is not False
            ),
        }

        violated = sorted(
            name
            for name, bad in forbidden.items()
            if bad
        )

        if violated:
            raise MinimumSufficientResourceInvariantError(
                "Selection decision cannot assert "
                "downstream authority: "
                + ", ".join(violated)
            )

    @property
    def selected(self) -> MinimumSufficientResourceCandidate:
        return self.sufficient_candidates[0]

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": MINIMUM_SUFFICIENT_RESOURCE_VERSION,
            "policy": self.policy.to_dict(),
            "selected_resource_id": (
                self.selected_resource_id
            ),
            "sufficient_candidates": [
                candidate.to_dict()
                for candidate in self.sufficient_candidates
            ],
            "rejected_resource_ids": list(
                self.rejected_resource_ids
            ),
            "selection_only": True,
            "execution_authorized": False,
            "activation_authorized": False,
            "trust_asserted": False,
            "system_truth_asserted": False,
        }


class MinimumSufficientResourceSelector:
    """
    Pure BMF-013 selector over generic governed resources.

    Sufficiency is established before optimization.
    Extra capability is treated as over-provisioning.

    Rank order after sufficiency:
      1. least excess capability mass;
      2. least governed resource mass;
      3. least cost;
      4. least latency;
      5. highest quality;
      6. deterministic resource_id.

    Selection does not execute, activate, trust, or authorize.
    """

    @staticmethod
    def _candidate(
        resource: GenericResourceDescriptor,
        economy: GovernedResourceEconomyProfile,
        policy: MinimumSufficientResourcePolicy,
    ) -> MinimumSufficientResourceCandidate | None:
        if resource.resource_id in policy.forbidden_resource_ids:
            return None

        if not policy.required_capability_ids.issubset(
            resource.capability_ids
        ):
            return None

        if economy.quality_score < policy.min_quality_score:
            return None

        if economy.cost_score > policy.max_cost_score:
            return None

        if economy.latency_score > policy.max_latency_score:
            return None

        if (
            economy.resource_mass_score
            > policy.max_resource_mass_score
        ):
            return None

        excess = len(
            resource.capability_ids
            - policy.required_capability_ids
        )

        rank = (
            excess,
            economy.resource_mass_score,
            economy.cost_score,
            economy.latency_score,
            -economy.quality_score,
            resource.resource_id,
        )

        return MinimumSufficientResourceCandidate(
            resource=resource,
            economy=economy,
            excess_capability_count=excess,
            rank=rank,
        )

    @classmethod
    def select(
        cls,
        resources: Iterable[GenericResourceDescriptor],
        economy_profiles: Iterable[
            GovernedResourceEconomyProfile
        ],
        policy: MinimumSufficientResourcePolicy,
    ) -> MinimumSufficientResourceDecision:
        if not isinstance(
            policy,
            MinimumSufficientResourcePolicy,
        ):
            raise TypeError(
                "policy must be a "
                "MinimumSufficientResourcePolicy."
            )

        resource_rows = tuple(resources)
        economy_rows = tuple(economy_profiles)

        for resource in resource_rows:
            if not isinstance(
                resource,
                GenericResourceDescriptor,
            ):
                raise TypeError(
                    "resources must contain "
                    "GenericResourceDescriptor objects."
                )

        for profile in economy_rows:
            if not isinstance(
                profile,
                GovernedResourceEconomyProfile,
            ):
                raise TypeError(
                    "economy_profiles must contain "
                    "GovernedResourceEconomyProfile objects."
                )

        resource_ids = [
            resource.resource_id
            for resource in resource_rows
        ]

        economy_ids = [
            profile.resource_id
            for profile in economy_rows
        ]

        if len(resource_ids) != len(set(resource_ids)):
            raise MinimumSufficientResourceInvariantError(
                "Resource IDs must be unique."
            )

        if len(economy_ids) != len(set(economy_ids)):
            raise MinimumSufficientResourceInvariantError(
                "Economy profile resource IDs must be unique."
            )

        if set(resource_ids) != set(economy_ids):
            raise MinimumSufficientResourceInvariantError(
                "Every resource requires exactly one "
                "governed economy profile."
            )

        economy_by_id = {
            profile.resource_id: profile
            for profile in economy_rows
        }

        sufficient = []
        rejected = []

        for resource in resource_rows:
            candidate = cls._candidate(
                resource,
                economy_by_id[resource.resource_id],
                policy,
            )

            if candidate is None:
                rejected.append(resource.resource_id)
            else:
                sufficient.append(candidate)

        if not sufficient:
            raise LookupError(
                "No resource satisfies the governed "
                "minimum-sufficiency envelope."
            )

        ordered = tuple(
            sorted(
                sufficient,
                key=lambda candidate: candidate.rank,
            )
        )

        return MinimumSufficientResourceDecision(
            policy=policy,
            selected_resource_id=(
                ordered[0].resource.resource_id
            ),
            sufficient_candidates=ordered,
            rejected_resource_ids=tuple(
                sorted(rejected)
            ),
        )


__all__ = [
    "MINIMUM_SUFFICIENT_RESOURCE_VERSION",
    "MinimumSufficientResourceInvariantError",
    "GovernedResourceEconomyProfile",
    "MinimumSufficientResourcePolicy",
    "MinimumSufficientResourceCandidate",
    "MinimumSufficientResourceDecision",
    "MinimumSufficientResourceSelector",
]
