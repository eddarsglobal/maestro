from __future__ import annotations

import math
from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import StrEnum
from types import MappingProxyType
from typing import Any

from .provider_contracts import (
    ResearchCapability,
)


def _require_runtime_name(
    value: str,
    name: str,
) -> str:
    if not isinstance(value, str):
        raise TypeError(
            f"{name} must be a string."
        )

    normalized = value.strip()

    if not normalized:
        raise ValueError(
            f"{name} must not be empty."
        )

    if "\x00" in normalized:
        raise ValueError(
            f"{name} must not contain NUL."
        )

    return normalized


def _freeze_research_json(
    value: Any,
    *,
    name: str,
) -> Any:
    if isinstance(value, Mapping):
        frozen = {}

        for key, item in value.items():
            if not isinstance(key, str):
                raise TypeError(
                    f"{name} keys must be strings."
                )

            if not key:
                raise ValueError(
                    f"{name} keys must not be empty."
                )

            if "\x00" in key:
                raise ValueError(
                    f"{name} keys must not contain NUL."
                )

            frozen[key] = (
                _freeze_research_json(
                    item,
                    name=f"{name}.{key}",
                )
            )

        return MappingProxyType(frozen)

    if isinstance(value, (list, tuple)):
        return tuple(
            _freeze_research_json(
                item,
                name=name,
            )
            for item in value
        )

    if value is None or isinstance(
        value,
        (str, bool, int),
    ):
        return value

    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError(
                f"{name} floats must be finite."
            )

        return value

    raise TypeError(
        f"{name} must contain only "
        "JSON-compatible values."
    )


def _thaw_research_json(
    value: Any,
) -> Any:
    if isinstance(value, Mapping):
        return {
            str(key): (
                _thaw_research_json(item)
            )
            for key, item in value.items()
        }

    if isinstance(value, tuple):
        return [
            _thaw_research_json(item)
            for item in value
        ]

    return value


MAX_RESEARCH_FALLBACK_ATTEMPTS = 8


class ResearchAttemptStatus(StrEnum):
    SUCCEEDED = "SUCCEEDED"
    EXECUTION_FAILED = "EXECUTION_FAILED"


@dataclass(frozen=True, slots=True)
class ResearchFallbackPolicy:
    max_attempts: int = 3

    def __post_init__(self) -> None:
        if (
            isinstance(
                self.max_attempts,
                bool,
            )
            or not isinstance(
                self.max_attempts,
                int,
            )
        ):
            raise TypeError(
                "max_attempts must be an integer."
            )

        if not (
            1
            <= self.max_attempts
            <= MAX_RESEARCH_FALLBACK_ATTEMPTS
        ):
            raise ValueError(
                "max_attempts must be between "
                "1 and "
                f"{MAX_RESEARCH_FALLBACK_ATTEMPTS}."
            )


@dataclass(frozen=True, slots=True)
class ResearchExecutionAttempt:
    attempt_number: int
    provider_id: str
    tool_name: str
    status: ResearchAttemptStatus
    error_type: str | None = None

    def __post_init__(self) -> None:
        if (
            isinstance(
                self.attempt_number,
                bool,
            )
            or not isinstance(
                self.attempt_number,
                int,
            )
            or self.attempt_number < 1
        ):
            raise ValueError(
                "attempt_number must be a "
                "positive integer."
            )

        object.__setattr__(
            self,
            "provider_id",
            _require_runtime_name(
                self.provider_id,
                "provider_id",
            ),
        )

        object.__setattr__(
            self,
            "tool_name",
            _require_runtime_name(
                self.tool_name,
                "tool_name",
            ),
        )

        if not isinstance(
            self.status,
            ResearchAttemptStatus,
        ):
            raise TypeError(
                "status must be a "
                "ResearchAttemptStatus."
            )

        if self.error_type is not None:
            object.__setattr__(
                self,
                "error_type",
                _require_runtime_name(
                    self.error_type,
                    "error_type",
                ),
            )


@dataclass(frozen=True, slots=True)
class ResearchRequest:
    task_id: str
    capability: ResearchCapability

    arguments: Mapping[
        str,
        Any,
    ] = field(
        default_factory=dict
    )

    preferred_local: bool = True

    forbidden_provider_ids: frozenset[
        str
    ] = frozenset()

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "task_id",
            _require_runtime_name(
                self.task_id,
                "task_id",
            ),
        )

        if not isinstance(
            self.capability,
            ResearchCapability,
        ):
            raise TypeError(
                "capability must be a "
                "ResearchCapability."
            )

        if not isinstance(
            self.arguments,
            Mapping,
        ):
            raise TypeError(
                "arguments must be a mapping."
            )

        frozen_arguments = (
            _freeze_research_json(
                self.arguments,
                name="arguments",
            )
        )

        object.__setattr__(
            self,
            "arguments",
            frozen_arguments,
        )

        if not isinstance(
            self.preferred_local,
            bool,
        ):
            raise TypeError(
                "preferred_local must be "
                "a boolean."
            )

        forbidden = frozenset(
            _require_runtime_name(
                provider_id,
                "forbidden provider_id",
            )
            for provider_id
            in self.forbidden_provider_ids
        )

        object.__setattr__(
            self,
            "forbidden_provider_ids",
            forbidden,
        )


@dataclass(frozen=True, slots=True)
class ResearchRoutingDecision:
    provider_id: str
    tool_name: str
    candidates: tuple[str, ...]
    reason: str


@dataclass(frozen=True, slots=True)
class ResearchExecutionResult:
    task_id: str
    capability: ResearchCapability
    provider_id: str
    tool_name: str
    output: Any
    attempts: tuple[
        ResearchExecutionAttempt,
        ...
    ] = ()
