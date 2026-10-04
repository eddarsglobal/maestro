from __future__ import annotations

import math
from collections.abc import Mapping
from dataclasses import dataclass, field
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
