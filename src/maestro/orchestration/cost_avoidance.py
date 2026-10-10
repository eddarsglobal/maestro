from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any


ORCHESTRATION_COST_AVOIDANCE_VERSION = 1


class OrchestrationCostInvariantError(ValueError):
    pass


class OrchestrationPath(StrEnum):
    ATOMIC = "ATOMIC"
    COGNITIVE = "COGNITIVE"
    FABRIC = "FABRIC"


_PATH_COST_RANK = {
    OrchestrationPath.ATOMIC: 0,
    OrchestrationPath.COGNITIVE: 1,
    OrchestrationPath.FABRIC: 2,
}


def _required_text(value: str, name: str) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{name} must be a string.")

    normalized = value.strip()

    if not normalized:
        raise ValueError(f"{name} must not be empty.")

    return normalized


def _non_negative_int(value: int, name: str) -> int:
    if (
        isinstance(value, bool)
        or not isinstance(value, int)
        or value < 0
    ):
        raise ValueError(
            f"{name} must be a non-negative integer."
        )

    return value


def _optional_non_negative_int(
    value: int | None,
    name: str,
) -> int | None:
    if value is None:
        return None

    return _non_negative_int(value, name)


def _council_ids(
    values: frozenset[str],
) -> frozenset[str]:
    if not isinstance(values, frozenset):
        raise TypeError(
            "required_council_ids must be a frozenset."
        )

    normalized = frozenset(
        _required_text(value, "council_id")
        for value in values
    )

    return normalized


@dataclass(frozen=True, slots=True)
class WorkRequirements:
    """Minimum governed orchestration requirements for one work unit."""

    work_id: str
    requires_cognition: bool = False
    required_council_ids: frozenset[str] = frozenset()
    required_resource_calls: int = 0
    required_cognitive_depth: int = 0
    requires_distribution: bool = False
    requires_remote_capacity: bool = False
    requires_cross_node_state: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "work_id",
            _required_text(self.work_id, "work_id"),
        )

        for name in (
            "requires_cognition",
            "requires_distribution",
            "requires_remote_capacity",
            "requires_cross_node_state",
        ):
            if not isinstance(getattr(self, name), bool):
                raise TypeError(f"{name} must be bool.")

        object.__setattr__(
            self,
            "required_council_ids",
            _council_ids(self.required_council_ids),
        )

        object.__setattr__(
            self,
            "required_resource_calls",
            _non_negative_int(
                self.required_resource_calls,
                "required_resource_calls",
            ),
        )

        object.__setattr__(
            self,
            "required_cognitive_depth",
            _non_negative_int(
                self.required_cognitive_depth,
                "required_cognitive_depth",
            ),
        )

    @property
    def cognition_required(self) -> bool:
        return bool(
            self.requires_cognition
            or self.required_council_ids
            or self.required_resource_calls > 0
            or self.required_cognitive_depth > 0
        )

    @property
    def fabric_required(self) -> bool:
        return bool(
            self.requires_distribution
            or self.requires_remote_capacity
            or self.requires_cross_node_state
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "work_id": self.work_id,
            "requires_cognition": self.requires_cognition,
            "required_council_ids": sorted(
                self.required_council_ids
            ),
            "required_resource_calls": (
                self.required_resource_calls
            ),
            "required_cognitive_depth": (
                self.required_cognitive_depth
            ),
            "requires_distribution": (
                self.requires_distribution
            ),
            "requires_remote_capacity": (
                self.requires_remote_capacity
            ),
            "requires_cross_node_state": (
                self.requires_cross_node_state
            ),
            "cognition_required": self.cognition_required,
            "fabric_required": self.fabric_required,
        }


@dataclass(frozen=True, slots=True)
class OrchestrationCostPolicy:
    """Hard ceilings for orchestration before execution exists."""

    allow_cognitive: bool = True
    allow_fabric: bool = True
    max_council_count: int | None = None
    max_resource_calls: int | None = None
    max_cognitive_depth: int | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.allow_cognitive, bool):
            raise TypeError("allow_cognitive must be bool.")

        if not isinstance(self.allow_fabric, bool):
            raise TypeError("allow_fabric must be bool.")

        for name in (
            "max_council_count",
            "max_resource_calls",
            "max_cognitive_depth",
        ):
            object.__setattr__(
                self,
                name,
                _optional_non_negative_int(
                    getattr(self, name),
                    name,
                ),
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "allow_cognitive": self.allow_cognitive,
            "allow_fabric": self.allow_fabric,
            "max_council_count": self.max_council_count,
            "max_resource_calls": self.max_resource_calls,
            "max_cognitive_depth": self.max_cognitive_depth,
        }


def _minimum_path(
    requirements: WorkRequirements,
) -> OrchestrationPath:
    if requirements.fabric_required:
        return OrchestrationPath.FABRIC

    if requirements.cognition_required:
        return OrchestrationPath.COGNITIVE

    return OrchestrationPath.ATOMIC


@dataclass(frozen=True, slots=True)
class OrchestrationPathDecision:
    """Passive decision describing the least sufficient path."""

    requirements: WorkRequirements
    policy: OrchestrationCostPolicy
    selected_path: OrchestrationPath
    path_cost_rank: int
    required_council_ids: tuple[str, ...]
    required_resource_calls: int
    required_cognitive_depth: int
    cognition_required: bool
    fabric_required: bool
    selection_only: bool = True
    council_activation_authorized: bool = False
    intelligence_execution_authorized: bool = False
    fabric_dispatch_authorized: bool = False
    network_authorized: bool = False
    system_truth_asserted: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.requirements, WorkRequirements):
            raise TypeError(
                "requirements must be WorkRequirements."
            )

        if not isinstance(self.policy, OrchestrationCostPolicy):
            raise TypeError(
                "policy must be OrchestrationCostPolicy."
            )

        if not isinstance(self.selected_path, OrchestrationPath):
            raise TypeError(
                "selected_path must be OrchestrationPath."
            )

        expected_path = _minimum_path(self.requirements)

        if self.selected_path is not expected_path:
            raise OrchestrationCostInvariantError(
                "Decision does not use the least "
                "orchestration sufficient for the work."
            )

        expected_rank = _PATH_COST_RANK[expected_path]

        if self.path_cost_rank != expected_rank:
            raise OrchestrationCostInvariantError(
                "path_cost_rank does not match path."
            )

        expected_councils = tuple(
            sorted(self.requirements.required_council_ids)
        )

        if self.required_council_ids != expected_councils:
            raise OrchestrationCostInvariantError(
                "Decision added or removed Council requirements."
            )

        if (
            self.required_resource_calls
            != self.requirements.required_resource_calls
        ):
            raise OrchestrationCostInvariantError(
                "Decision changed resource-call requirements."
            )

        if (
            self.required_cognitive_depth
            != self.requirements.required_cognitive_depth
        ):
            raise OrchestrationCostInvariantError(
                "Decision changed cognitive-depth requirements."
            )

        if (
            self.cognition_required
            is not self.requirements.cognition_required
        ):
            raise OrchestrationCostInvariantError(
                "Cognition requirement mismatch."
            )

        if (
            self.fabric_required
            is not self.requirements.fabric_required
        ):
            raise OrchestrationCostInvariantError(
                "Fabric requirement mismatch."
            )

        authority = {
            "selection_only": self.selection_only is not True,
            "council_activation_authorized": (
                self.council_activation_authorized is not False
            ),
            "intelligence_execution_authorized": (
                self.intelligence_execution_authorized is not False
            ),
            "fabric_dispatch_authorized": (
                self.fabric_dispatch_authorized is not False
            ),
            "network_authorized": (
                self.network_authorized is not False
            ),
            "system_truth_asserted": (
                self.system_truth_asserted is not False
            ),
        }

        violated = sorted(
            name
            for name, value in authority.items()
            if value
        )

        if violated:
            raise OrchestrationCostInvariantError(
                "Path selection cannot assert downstream "
                "authority: "
                + ", ".join(violated)
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": ORCHESTRATION_COST_AVOIDANCE_VERSION,
            "requirements": self.requirements.to_dict(),
            "policy": self.policy.to_dict(),
            "selected_path": self.selected_path.value,
            "path_cost_rank": self.path_cost_rank,
            "required_council_ids": list(
                self.required_council_ids
            ),
            "required_resource_calls": (
                self.required_resource_calls
            ),
            "required_cognitive_depth": (
                self.required_cognitive_depth
            ),
            "cognition_required": self.cognition_required,
            "fabric_required": self.fabric_required,
            "selection_only": True,
            "council_activation_authorized": False,
            "intelligence_execution_authorized": False,
            "fabric_dispatch_authorized": False,
            "network_authorized": False,
            "system_truth_asserted": False,
        }


class GovernedOrchestrationPathSelector:
    """
    Select the least orchestration sufficient for a work unit.

    ATOMIC uses no cognitive or Fabric requirement.
    COGNITIVE is selected only when cognition is required and
    Fabric is not required.
    FABRIC is selected only when distribution, remote capacity,
    or cross-node state requires the Fabric boundary.

    This selector performs no Council activation, model/resource
    execution, Fabric dispatch, network access, or authorization.
    """

    @classmethod
    def select(
        cls,
        requirements: WorkRequirements,
        policy: OrchestrationCostPolicy | None = None,
    ) -> OrchestrationPathDecision:
        if not isinstance(requirements, WorkRequirements):
            raise TypeError(
                "requirements must be WorkRequirements."
            )

        active_policy = policy or OrchestrationCostPolicy()

        if not isinstance(active_policy, OrchestrationCostPolicy):
            raise TypeError(
                "policy must be OrchestrationCostPolicy."
            )

        council_count = len(
            requirements.required_council_ids
        )

        if (
            requirements.cognition_required
            and not active_policy.allow_cognitive
        ):
            raise LookupError(
                "Cognitive orchestration is not allowed "
                "by policy."
            )

        if (
            requirements.fabric_required
            and not active_policy.allow_fabric
        ):
            raise LookupError(
                "Fabric orchestration is not allowed "
                "by policy."
            )

        if (
            active_policy.max_council_count is not None
            and council_count
            > active_policy.max_council_count
        ):
            raise LookupError(
                "Required Council count exceeds policy."
            )

        if (
            active_policy.max_resource_calls is not None
            and requirements.required_resource_calls
            > active_policy.max_resource_calls
        ):
            raise LookupError(
                "Required resource calls exceed policy."
            )

        if (
            active_policy.max_cognitive_depth is not None
            and requirements.required_cognitive_depth
            > active_policy.max_cognitive_depth
        ):
            raise LookupError(
                "Required cognitive depth exceeds policy."
            )

        selected_path = _minimum_path(requirements)

        return OrchestrationPathDecision(
            requirements=requirements,
            policy=active_policy,
            selected_path=selected_path,
            path_cost_rank=_PATH_COST_RANK[selected_path],
            required_council_ids=tuple(
                sorted(requirements.required_council_ids)
            ),
            required_resource_calls=(
                requirements.required_resource_calls
            ),
            required_cognitive_depth=(
                requirements.required_cognitive_depth
            ),
            cognition_required=(
                requirements.cognition_required
            ),
            fabric_required=(
                requirements.fabric_required
            ),
        )


__all__ = [
    "ORCHESTRATION_COST_AVOIDANCE_VERSION",
    "OrchestrationCostInvariantError",
    "OrchestrationPath",
    "WorkRequirements",
    "OrchestrationCostPolicy",
    "OrchestrationPathDecision",
    "GovernedOrchestrationPathSelector",
]
