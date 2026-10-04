from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import StrEnum
from types import MappingProxyType
from typing import Any, Mapping


def _require_name(
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


def _require_score(
    value: float,
    name: str,
    *,
    minimum: float,
    maximum: float | None = None,
) -> float:
    if isinstance(value, bool):
        raise TypeError(
            f"{name} must be numeric."
        )

    try:
        score = float(value)
    except (TypeError, ValueError) as exc:
        raise TypeError(
            f"{name} must be numeric."
        ) from exc

    if not math.isfinite(score):
        raise ValueError(
            f"{name} must be finite."
        )

    if score < minimum:
        raise ValueError(
            f"{name} must be >= {minimum}."
        )

    if (
        maximum is not None
        and score > maximum
    ):
        raise ValueError(
            f"{name} must be <= {maximum}."
        )

    return score


class ResearchCapability(StrEnum):
    SEARCH = "SEARCH"
    FETCH = "FETCH"


class ResearchProviderStatus(StrEnum):
    AVAILABLE = "AVAILABLE"
    DEGRADED = "DEGRADED"
    UNAVAILABLE = "UNAVAILABLE"


@dataclass(frozen=True, slots=True)
class ResearchProviderDescriptor:
    """
    Provider-neutral RX source-access descriptor.

    A descriptor carries routing metadata only.
    It owns no execution or constitutional authority.
    """

    provider_id: str
    capabilities: frozenset[
        ResearchCapability
    ]
    tool_names: Mapping[
        ResearchCapability,
        str,
    ]

    status: ResearchProviderStatus = (
        ResearchProviderStatus.AVAILABLE
    )

    local: bool = False
    cost_score: float = 0.0
    latency_score: float = 0.0
    quality_score: float = 0.5

    metadata: Mapping[
        str,
        Any,
    ] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "provider_id",
            _require_name(
                self.provider_id,
                "provider_id",
            ),
        )

        capabilities = frozenset(
            self.capabilities
        )

        if not capabilities:
            raise ValueError(
                "Research provider requires "
                "at least one capability."
            )

        for capability in capabilities:
            if not isinstance(
                capability,
                ResearchCapability,
            ):
                raise TypeError(
                    "capabilities must contain "
                    "ResearchCapability values."
                )

        object.__setattr__(
            self,
            "capabilities",
            capabilities,
        )

        if not isinstance(
            self.tool_names,
            Mapping,
        ):
            raise TypeError(
                "tool_names must be a mapping."
            )

        tools = dict(
            self.tool_names
        )

        for capability, tool_name in tools.items():
            if not isinstance(
                capability,
                ResearchCapability,
            ):
                raise TypeError(
                    "tool_names keys must be "
                    "ResearchCapability values."
                )

            tools[capability] = (
                _require_name(
                    tool_name,
                    "tool name",
                )
            )

        if set(tools) != set(capabilities):
            raise ValueError(
                "Every research capability "
                "must have exactly one tool name."
            )

        object.__setattr__(
            self,
            "tool_names",
            MappingProxyType(tools),
        )

        if not isinstance(
            self.status,
            ResearchProviderStatus,
        ):
            raise TypeError(
                "status must be a "
                "ResearchProviderStatus."
            )

        if not isinstance(self.local, bool):
            raise TypeError(
                "local must be a boolean."
            )

        object.__setattr__(
            self,
            "cost_score",
            _require_score(
                self.cost_score,
                "cost_score",
                minimum=0.0,
            ),
        )

        object.__setattr__(
            self,
            "latency_score",
            _require_score(
                self.latency_score,
                "latency_score",
                minimum=0.0,
            ),
        )

        object.__setattr__(
            self,
            "quality_score",
            _require_score(
                self.quality_score,
                "quality_score",
                minimum=0.0,
                maximum=1.0,
            ),
        )

        if not isinstance(
            self.metadata,
            Mapping,
        ):
            raise TypeError(
                "metadata must be a mapping."
            )

        object.__setattr__(
            self,
            "metadata",
            MappingProxyType(
                dict(self.metadata)
            ),
        )

    def tool_name_for(
        self,
        capability: ResearchCapability,
    ) -> str:
        if not isinstance(
            capability,
            ResearchCapability,
        ):
            raise TypeError(
                "capability must be a "
                "ResearchCapability."
            )

        return self.tool_names[
            capability
        ]

    def to_dict(self) -> dict[str, Any]:
        return {
            "provider_id": self.provider_id,
            "capabilities": sorted(
                capability.value
                for capability
                in self.capabilities
            ),
            "tool_names": {
                capability.value: (
                    self.tool_names[
                        capability
                    ]
                )
                for capability
                in sorted(
                    self.tool_names,
                    key=lambda item: (
                        item.value
                    ),
                )
            },
            "status": self.status.value,
            "local": self.local,
            "cost_score": self.cost_score,
            "latency_score": (
                self.latency_score
            ),
            "quality_score": (
                self.quality_score
            ),
            "metadata": dict(
                self.metadata
            ),
        }
