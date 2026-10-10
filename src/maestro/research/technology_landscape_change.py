from __future__ import annotations

import hashlib
import json
import math

from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import StrEnum
from types import MappingProxyType
from typing import Any

from .technology_radar import RadarObservation


TECHNOLOGY_LANDSCAPE_CHANGE_VERSION = 1


class TechnologyLandscapeChangeInvariantError(
    ValueError
):
    pass


class LandscapeChangeState(StrEnum):
    UNKNOWN = "UNKNOWN"
    UNCHANGED = "UNCHANGED"
    CHANGED = "CHANGED"


def _required_text(
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


def _freeze_json(
    value: Any,
    name: str,
) -> Any:
    if value is None:
        return None

    if isinstance(
        value,
        (str, bool, int),
    ):
        return value

    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError(
                f"{name} must not contain "
                "non-finite numbers."
            )

        return value

    if isinstance(value, Mapping):
        out: dict[str, Any] = {}

        for key in sorted(value):
            if not isinstance(key, str):
                raise TypeError(
                    f"{name} mapping keys "
                    "must be strings."
                )

            normalized_key = _required_text(
                key,
                f"{name} key",
            )

            out[normalized_key] = _freeze_json(
                value[key],
                f"{name}.{normalized_key}",
            )

        return MappingProxyType(out)

    if isinstance(value, (list, tuple)):
        return tuple(
            _freeze_json(
                item,
                f"{name}[]",
            )
            for item in value
        )

    raise TypeError(
        f"{name} contains unsupported "
        f"value type: {type(value).__name__}"
    )


def _thaw_json(
    value: Any,
) -> Any:
    if isinstance(value, Mapping):
        return {
            key: _thaw_json(item)
            for key, item in value.items()
        }

    if isinstance(value, (list, tuple)):
        return [
            _thaw_json(item)
            for item in value
        ]

    return value


def _canonical_json(
    value: Any,
) -> str:
    return json.dumps(
        _thaw_json(value),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    )


def _digest(
    prefix: str,
    value: Any,
) -> str:
    canonical = _canonical_json(value)

    digest = hashlib.sha256(
        canonical.encode("utf-8")
    ).hexdigest()

    return f"{prefix}-{digest[:24]}"


@dataclass(
    frozen=True,
    slots=True,
)
class TechnologyLandscapeObservation:
    """
    One passive externally evidenced technology-state observation.

    The observation is not system truth and grants no downstream
    authority. `state` contains only the externally observed state
    that is relevant to deterministic landscape comparison.
    """

    subject_id: str
    evidence_id: str
    source_ref: str
    claim: str
    state: Mapping[str, Any]

    verification_status: str = (
        "UNVERIFIED_EXTERNAL"
    )

    system_truth_asserted: bool = False

    def __post_init__(
        self,
    ) -> None:
        for name in (
            "subject_id",
            "evidence_id",
            "source_ref",
            "claim",
            "verification_status",
        ):
            object.__setattr__(
                self,
                name,
                _required_text(
                    getattr(self, name),
                    name,
                ),
            )

        if (
            self.verification_status
            != "UNVERIFIED_EXTERNAL"
        ):
            raise TechnologyLandscapeChangeInvariantError(
                "Technology landscape observations "
                "must remain UNVERIFIED_EXTERNAL."
            )

        if self.system_truth_asserted is not False:
            raise TechnologyLandscapeChangeInvariantError(
                "Technology landscape observations "
                "cannot assert system truth."
            )

        if not isinstance(self.state, Mapping):
            raise TypeError(
                "state must be a mapping."
            )

        if not self.state:
            raise TechnologyLandscapeChangeInvariantError(
                "Technology landscape observation "
                "requires non-empty observed state."
            )

        object.__setattr__(
            self,
            "state",
            _freeze_json(
                self.state,
                "state",
            ),
        )

    @classmethod
    def from_radar(
        cls,
        *,
        subject_id: str,
        observation: RadarObservation,
        state: Mapping[str, Any],
    ) -> TechnologyLandscapeObservation:
        if not isinstance(
            observation,
            RadarObservation,
        ):
            raise TypeError(
                "observation must be RadarObservation."
            )

        if (
            observation.verification_status
            != "UNVERIFIED_EXTERNAL"
        ):
            raise TechnologyLandscapeChangeInvariantError(
                "Radar observation must retain "
                "UNVERIFIED_EXTERNAL status."
            )

        if (
            observation.system_truth_asserted
            is not False
        ):
            raise TechnologyLandscapeChangeInvariantError(
                "Radar observation cannot assert "
                "system truth."
            )

        return cls(
            subject_id=subject_id,
            evidence_id=observation.evidence_id,
            source_ref=observation.source_ref,
            claim=observation.claim,
            state=state,
            verification_status=(
                observation.verification_status
            ),
            system_truth_asserted=False,
        )

    @property
    def state_fingerprint(
        self,
    ) -> str:
        return _digest(
            "TLO",
            {
                "subject_id": self.subject_id,
                "state": self.state,
            },
        )

    def to_dict(
        self,
    ) -> dict[str, Any]:
        return {
            "subject_id": self.subject_id,
            "evidence_id": self.evidence_id,
            "source_ref": self.source_ref,
            "claim": self.claim,
            "verification_status": (
                self.verification_status
            ),
            "system_truth_asserted": False,
            "state": _thaw_json(
                self.state
            ),
            "state_fingerprint": (
                self.state_fingerprint
            ),
        }


@dataclass(
    frozen=True,
    slots=True,
)
class TechnologyLandscapeSnapshot:
    """
    Canonical passive landscape state for one declared scope.

    `complete=False` means the available external evidence is
    insufficient to conclude UNCHANGED. Such snapshots therefore
    produce UNKNOWN when compared.
    """

    scope_id: str
    observations: tuple[
        TechnologyLandscapeObservation,
        ...,
    ]

    complete: bool

    snapshot_id: str = field(
        init=False
    )

    def __post_init__(
        self,
    ) -> None:
        object.__setattr__(
            self,
            "scope_id",
            _required_text(
                self.scope_id,
                "scope_id",
            ),
        )

        if not isinstance(self.complete, bool):
            raise TypeError(
                "complete must be a boolean."
            )

        supplied = tuple(
            self.observations
        )

        for observation in supplied:
            if not isinstance(
                observation,
                TechnologyLandscapeObservation,
            ):
                raise TypeError(
                    "observations must contain "
                    "TechnologyLandscapeObservation "
                    "objects only."
                )

        subject_ids = [
            observation.subject_id
            for observation in supplied
        ]

        if (
            len(subject_ids)
            != len(set(subject_ids))
        ):
            raise TechnologyLandscapeChangeInvariantError(
                "Technology landscape snapshot "
                "requires unique subject IDs."
            )

        ordered = tuple(
            sorted(
                supplied,
                key=lambda item: (
                    item.subject_id
                ),
            )
        )

        object.__setattr__(
            self,
            "observations",
            ordered,
        )

        identity_payload = {
            "scope_id": self.scope_id,
            "complete": self.complete,
            "subjects": [
                {
                    "subject_id": (
                        observation.subject_id
                    ),
                    "state": observation.state,
                }
                for observation in ordered
            ],
        }

        object.__setattr__(
            self,
            "snapshot_id",
            _digest(
                "TLS",
                identity_payload,
            ),
        )

    @property
    def evidence_ids(
        self,
    ) -> tuple[str, ...]:
        return tuple(
            sorted({
                observation.evidence_id
                for observation
                in self.observations
            })
        )

    def by_subject(
        self,
    ) -> dict[
        str,
        TechnologyLandscapeObservation,
    ]:
        return {
            observation.subject_id: observation
            for observation in self.observations
        }

    def to_dict(
        self,
    ) -> dict[str, Any]:
        return {
            "landscape_change_version": (
                TECHNOLOGY_LANDSCAPE_CHANGE_VERSION
            ),
            "snapshot_id": self.snapshot_id,
            "scope_id": self.scope_id,
            "complete": self.complete,
            "evidence_ids": list(
                self.evidence_ids
            ),
            "observations": [
                observation.to_dict()
                for observation
                in self.observations
            ],
        }


@dataclass(
    frozen=True,
    slots=True,
)
class TechnologyLandscapeChange:
    """
    Passive evidence result describing whether two comparable
    technology-landscape snapshots differ.

    CHANGE DETECTED is evidence of difference only.
    It is not an update recommendation, capability candidate,
    trust decision, installation request, activation request,
    execution request, Core mutation, or system-truth assertion.
    """

    state: LandscapeChangeState
    scope_id: str

    previous_snapshot_id: str | None = None
    current_snapshot_id: str | None = None

    added_subject_ids: tuple[str, ...] = ()
    removed_subject_ids: tuple[str, ...] = ()
    modified_subject_ids: tuple[str, ...] = ()

    evidence_ids: tuple[str, ...] = ()
    reason: str = "NO_CHANGE"

    update_recommended: bool = False
    capability_candidate_created: bool = False
    trust_asserted: bool = False
    installation_requested: bool = False
    activation_requested: bool = False
    authorization_asserted: bool = False
    execution_requested: bool = False
    core_mutation_requested: bool = False
    system_truth_asserted: bool = False

    change_id: str = field(
        init=False
    )

    def __post_init__(
        self,
    ) -> None:
        if not isinstance(
            self.state,
            LandscapeChangeState,
        ):
            raise TypeError(
                "state must be LandscapeChangeState."
            )

        object.__setattr__(
            self,
            "scope_id",
            _required_text(
                self.scope_id,
                "scope_id",
            ),
        )

        object.__setattr__(
            self,
            "reason",
            _required_text(
                self.reason,
                "reason",
            ),
        )

        for name in (
            "previous_snapshot_id",
            "current_snapshot_id",
        ):
            value = getattr(
                self,
                name,
            )

            if value is not None:
                object.__setattr__(
                    self,
                    name,
                    _required_text(
                        value,
                        name,
                    ),
                )

        for name in (
            "added_subject_ids",
            "removed_subject_ids",
            "modified_subject_ids",
            "evidence_ids",
        ):
            values = tuple(
                sorted(
                    set(
                        _required_text(
                            item,
                            f"{name} item",
                        )
                        for item in getattr(
                            self,
                            name,
                        )
                    )
                )
            )

            object.__setattr__(
                self,
                name,
                values,
            )

        deltas = (
            self.added_subject_ids
            + self.removed_subject_ids
            + self.modified_subject_ids
        )

        if (
            self.state
            is LandscapeChangeState.CHANGED
            and not deltas
        ):
            raise TechnologyLandscapeChangeInvariantError(
                "CHANGED requires at least one "
                "landscape delta."
            )

        if (
            self.state
            is not LandscapeChangeState.CHANGED
            and deltas
        ):
            raise TechnologyLandscapeChangeInvariantError(
                "Only CHANGED may contain "
                "landscape deltas."
            )

        forbidden = {
            "update_recommended": (
                self.update_recommended
            ),
            "capability_candidate_created": (
                self.capability_candidate_created
            ),
            "trust_asserted": (
                self.trust_asserted
            ),
            "installation_requested": (
                self.installation_requested
            ),
            "activation_requested": (
                self.activation_requested
            ),
            "authorization_asserted": (
                self.authorization_asserted
            ),
            "execution_requested": (
                self.execution_requested
            ),
            "core_mutation_requested": (
                self.core_mutation_requested
            ),
            "system_truth_asserted": (
                self.system_truth_asserted
            ),
        }

        asserted = sorted(
            name
            for name, value
            in forbidden.items()
            if value is not False
        )

        if asserted:
            raise TechnologyLandscapeChangeInvariantError(
                "Landscape change evidence cannot "
                "assert downstream authority: "
                + ", ".join(asserted)
            )

        object.__setattr__(
            self,
            "change_id",
            _digest(
                "TLC",
                {
                    "scope_id": self.scope_id,
                    "state": self.state.value,
                    "previous_snapshot_id": (
                        self.previous_snapshot_id
                    ),
                    "current_snapshot_id": (
                        self.current_snapshot_id
                    ),
                    "added_subject_ids": (
                        self.added_subject_ids
                    ),
                    "removed_subject_ids": (
                        self.removed_subject_ids
                    ),
                    "modified_subject_ids": (
                        self.modified_subject_ids
                    ),
                    "evidence_ids": (
                        self.evidence_ids
                    ),
                    "reason": self.reason,
                },
            ),
        )

    @property
    def changed(
        self,
    ) -> bool:
        return (
            self.state
            is LandscapeChangeState.CHANGED
        )

    def to_dict(
        self,
    ) -> dict[str, Any]:
        return {
            "landscape_change_version": (
                TECHNOLOGY_LANDSCAPE_CHANGE_VERSION
            ),
            "change_id": self.change_id,
            "state": self.state.value,
            "scope_id": self.scope_id,
            "previous_snapshot_id": (
                self.previous_snapshot_id
            ),
            "current_snapshot_id": (
                self.current_snapshot_id
            ),
            "added_subject_ids": list(
                self.added_subject_ids
            ),
            "removed_subject_ids": list(
                self.removed_subject_ids
            ),
            "modified_subject_ids": list(
                self.modified_subject_ids
            ),
            "evidence_ids": list(
                self.evidence_ids
            ),
            "reason": self.reason,
            "changed": self.changed,
            "update_recommended": False,
            "capability_candidate_created": False,
            "trust_asserted": False,
            "installation_requested": False,
            "activation_requested": False,
            "authorization_asserted": False,
            "execution_requested": False,
            "core_mutation_requested": False,
            "system_truth_asserted": False,
        }


class TechnologyLandscapeChangeDetector:
    """
    Pure deterministic prior/current landscape comparator.

    This class performs no source access, network operation,
    research request creation, capability derivation, update
    recommendation, installation, activation, execution,
    learning, promotion, Core mutation, or truth assertion.
    """

    @staticmethod
    def _evidence_ids(
        previous: (
            TechnologyLandscapeSnapshot
            | None
        ),
        current: (
            TechnologyLandscapeSnapshot
            | None
        ),
    ) -> tuple[str, ...]:
        values: set[str] = set()

        if previous is not None:
            values.update(
                previous.evidence_ids
            )

        if current is not None:
            values.update(
                current.evidence_ids
            )

        return tuple(
            sorted(values)
        )

    @classmethod
    def _unknown(
        cls,
        *,
        scope_id: str,
        previous: (
            TechnologyLandscapeSnapshot
            | None
        ),
        current: (
            TechnologyLandscapeSnapshot
            | None
        ),
        reason: str,
    ) -> TechnologyLandscapeChange:
        return TechnologyLandscapeChange(
            state=LandscapeChangeState.UNKNOWN,
            scope_id=scope_id,
            previous_snapshot_id=(
                previous.snapshot_id
                if previous is not None
                else None
            ),
            current_snapshot_id=(
                current.snapshot_id
                if current is not None
                else None
            ),
            evidence_ids=cls._evidence_ids(
                previous,
                current,
            ),
            reason=reason,
        )

    @classmethod
    def compare(
        cls,
        previous: (
            TechnologyLandscapeSnapshot
            | None
        ),
        current: (
            TechnologyLandscapeSnapshot
            | None
        ),
    ) -> TechnologyLandscapeChange:
        if previous is None and current is None:
            raise TechnologyLandscapeChangeInvariantError(
                "At least one landscape snapshot "
                "is required."
            )

        if (
            previous is not None
            and not isinstance(
                previous,
                TechnologyLandscapeSnapshot,
            )
        ):
            raise TypeError(
                "previous must be "
                "TechnologyLandscapeSnapshot or None."
            )

        if (
            current is not None
            and not isinstance(
                current,
                TechnologyLandscapeSnapshot,
            )
        ):
            raise TypeError(
                "current must be "
                "TechnologyLandscapeSnapshot or None."
            )

        scope_id = (
            current.scope_id
            if current is not None
            else previous.scope_id
        )

        if previous is None:
            return cls._unknown(
                scope_id=scope_id,
                previous=None,
                current=current,
                reason="MISSING_BASELINE",
            )

        if current is None:
            return cls._unknown(
                scope_id=scope_id,
                previous=previous,
                current=None,
                reason="MISSING_CURRENT",
            )

        if (
            previous.scope_id
            != current.scope_id
        ):
            raise TechnologyLandscapeChangeInvariantError(
                "Landscape snapshots from "
                "different scopes are not comparable."
            )

        if not previous.complete:
            return cls._unknown(
                scope_id=scope_id,
                previous=previous,
                current=current,
                reason="INCOMPLETE_BASELINE",
            )

        if not current.complete:
            return cls._unknown(
                scope_id=scope_id,
                previous=previous,
                current=current,
                reason="INCOMPLETE_CURRENT",
            )

        previous_rows = previous.by_subject()
        current_rows = current.by_subject()

        previous_ids = set(
            previous_rows
        )

        current_ids = set(
            current_rows
        )

        added = tuple(
            sorted(
                current_ids
                - previous_ids
            )
        )

        removed = tuple(
            sorted(
                previous_ids
                - current_ids
            )
        )

        modified = tuple(
            sorted(
                subject_id
                for subject_id
                in (
                    previous_ids
                    & current_ids
                )
                if (
                    previous_rows[
                        subject_id
                    ].state_fingerprint
                    != current_rows[
                        subject_id
                    ].state_fingerprint
                )
            )
        )

        evidence_ids = cls._evidence_ids(
            previous,
            current,
        )

        if (
            added
            or removed
            or modified
        ):
            return TechnologyLandscapeChange(
                state=(
                    LandscapeChangeState.CHANGED
                ),
                scope_id=scope_id,
                previous_snapshot_id=(
                    previous.snapshot_id
                ),
                current_snapshot_id=(
                    current.snapshot_id
                ),
                added_subject_ids=added,
                removed_subject_ids=removed,
                modified_subject_ids=modified,
                evidence_ids=evidence_ids,
                reason="LANDSCAPE_CHANGED",
            )

        return TechnologyLandscapeChange(
            state=(
                LandscapeChangeState.UNCHANGED
            ),
            scope_id=scope_id,
            previous_snapshot_id=(
                previous.snapshot_id
            ),
            current_snapshot_id=(
                current.snapshot_id
            ),
            evidence_ids=evidence_ids,
            reason="NO_CHANGE",
        )


__all__ = [
    "TECHNOLOGY_LANDSCAPE_CHANGE_VERSION",
    "LandscapeChangeState",
    "TechnologyLandscapeChangeInvariantError",
    "TechnologyLandscapeObservation",
    "TechnologyLandscapeSnapshot",
    "TechnologyLandscapeChange",
    "TechnologyLandscapeChangeDetector",
]
