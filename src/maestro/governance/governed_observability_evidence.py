from __future__ import annotations

import hashlib
import json
import math

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any


GOVERNED_OBSERVABILITY_EVIDENCE_VERSION = 1


class GovernedObservabilityInvariantError(
    ValueError
):
    pass


class EvidenceDimension(StrEnum):
    PERFORMANCE = "PERFORMANCE"
    RELIABILITY = "RELIABILITY"
    SECURITY = "SECURITY"
    OUTCOME = "OUTCOME"


class EvidenceValueKind(StrEnum):
    NUMBER = "NUMBER"
    BOOLEAN = "BOOLEAN"
    TEXT = "TEXT"


class CrossGenerationState(StrEnum):
    COMPARABLE = "COMPARABLE"
    INSUFFICIENT = "INSUFFICIENT"


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


def _optional_text(
    value: str | None,
    name: str,
) -> str | None:
    if value is None:
        return None

    return _required_text(
        value,
        name,
    )


def _timestamp(
    value: str,
    name: str,
) -> str:
    text = _required_text(
        value,
        name,
    )

    candidate = (
        text[:-1] + "+00:00"
        if text.endswith("Z")
        else text
    )

    try:
        parsed = datetime.fromisoformat(
            candidate
        )
    except ValueError as exc:
        raise (
            GovernedObservabilityInvariantError(
                f"{name} must be ISO-8601."
            )
        ) from exc

    if (
        parsed.tzinfo is None
        or parsed.utcoffset() is None
    ):
        raise (
            GovernedObservabilityInvariantError(
                f"{name} must be timezone-aware."
            )
        )

    return (
        parsed.astimezone(timezone.utc)
        .isoformat()
    )


def _normalize_value(
    value: bool | int | float | str,
) -> tuple[
    bool | int | float | str,
    EvidenceValueKind,
]:
    if isinstance(value, bool):
        return (
            value,
            EvidenceValueKind.BOOLEAN,
        )

    if isinstance(value, int):
        return (
            value,
            EvidenceValueKind.NUMBER,
        )

    if isinstance(value, float):
        if not math.isfinite(value):
            raise (
                GovernedObservabilityInvariantError(
                    "Numeric evidence must be finite."
                )
            )

        return (
            value,
            EvidenceValueKind.NUMBER,
        )

    if isinstance(value, str):
        return (
            _required_text(
                value,
                "value",
            ),
            EvidenceValueKind.TEXT,
        )

    raise TypeError(
        "Evidence value must be "
        "bool, int, float, or str."
    )


def _stable_id(
    prefix: str,
    payload: dict[str, Any],
) -> str:
    canonical = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    )

    digest = hashlib.sha256(
        canonical.encode("utf-8")
    ).hexdigest()

    return f"{prefix}-{digest[:24]}"


def _assert_passive(
    *,
    judgment_asserted: bool,
    optimality_asserted: bool,
    truth_asserted: bool,
    verdict_asserted: bool,
    promotion_requested: bool,
    security_guarantee_asserted: bool,
    learning_authorized: bool,
    control_requested: bool,
    release_certification_asserted: bool,
    system_truth_asserted: bool,
) -> None:
    fields = {
        "judgment_asserted": (
            judgment_asserted
        ),
        "optimality_asserted": (
            optimality_asserted
        ),
        "truth_asserted": (
            truth_asserted
        ),
        "verdict_asserted": (
            verdict_asserted
        ),
        "promotion_requested": (
            promotion_requested
        ),
        "security_guarantee_asserted": (
            security_guarantee_asserted
        ),
        "learning_authorized": (
            learning_authorized
        ),
        "control_requested": (
            control_requested
        ),
        "release_certification_asserted": (
            release_certification_asserted
        ),
        "system_truth_asserted": (
            system_truth_asserted
        ),
    }

    asserted = sorted(
        name
        for name, value in fields.items()
        if value is not False
    )

    if asserted:
        raise (
            GovernedObservabilityInvariantError(
                "Observability evidence cannot "
                "assert downstream authority: "
                + ", ".join(asserted)
            )
        )


@dataclass(
    frozen=True,
    slots=True,
)
class ObservedEvidenceMeasure:
    dimension: EvidenceDimension
    metric_id: str
    value: bool | int | float | str
    unit: str | None
    evidence_id: str
    source_ref: str
    observed_at: str

    value_kind: EvidenceValueKind | None = None

    def __post_init__(
        self,
    ) -> None:
        if not isinstance(
            self.dimension,
            EvidenceDimension,
        ):
            raise TypeError(
                "dimension must be "
                "EvidenceDimension."
            )

        for name in (
            "metric_id",
            "evidence_id",
            "source_ref",
        ):
            object.__setattr__(
                self,
                name,
                _required_text(
                    getattr(self, name),
                    name,
                ),
            )

        object.__setattr__(
            self,
            "unit",
            _optional_text(
                self.unit,
                "unit",
            ),
        )

        normalized_value, kind = (
            _normalize_value(
                self.value
            )
        )

        object.__setattr__(
            self,
            "value",
            normalized_value,
        )

        if (
            self.value_kind is not None
            and self.value_kind is not kind
        ):
            raise (
                GovernedObservabilityInvariantError(
                    "value_kind does not match "
                    "evidence value."
                )
            )

        object.__setattr__(
            self,
            "value_kind",
            kind,
        )

        object.__setattr__(
            self,
            "observed_at",
            _timestamp(
                self.observed_at,
                "observed_at",
            ),
        )

    @property
    def comparison_key(
        self,
    ) -> tuple[str, str, str, str]:
        return (
            self.dimension.value,
            self.metric_id,
            self.unit or "",
            self.value_kind.value,
        )

    def to_dict(
        self,
    ) -> dict[str, Any]:
        return {
            "dimension": (
                self.dimension.value
            ),
            "metric_id": self.metric_id,
            "value": self.value,
            "value_kind": (
                self.value_kind.value
            ),
            "unit": self.unit,
            "evidence_id": (
                self.evidence_id
            ),
            "source_ref": self.source_ref,
            "observed_at": (
                self.observed_at
            ),
        }


@dataclass(
    frozen=True,
    slots=True,
)
class GovernedGenerationObservation:
    observation_id: str

    generation_id: str
    generation_index: int

    subject_id: str
    subject_kind: str

    measures: tuple[
        ObservedEvidenceMeasure,
        ...,
    ]

    judgment_asserted: bool = False
    optimality_asserted: bool = False
    truth_asserted: bool = False
    verdict_asserted: bool = False
    promotion_requested: bool = False
    security_guarantee_asserted: bool = False
    learning_authorized: bool = False
    control_requested: bool = False
    release_certification_asserted: bool = False
    system_truth_asserted: bool = False

    def __post_init__(
        self,
    ) -> None:
        for name in (
            "observation_id",
            "generation_id",
            "subject_id",
            "subject_kind",
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
            not isinstance(
                self.generation_index,
                int,
            )
            or isinstance(
                self.generation_index,
                bool,
            )
            or self.generation_index < 0
        ):
            raise (
                GovernedObservabilityInvariantError(
                    "generation_index must be "
                    "a non-negative integer."
                )
            )

        measures = tuple(
            self.measures
        )

        if not measures:
            raise (
                GovernedObservabilityInvariantError(
                    "Observation requires at least "
                    "one evidence measure."
                )
            )

        if not all(
            isinstance(
                measure,
                ObservedEvidenceMeasure,
            )
            for measure in measures
        ):
            raise TypeError(
                "measures must contain only "
                "ObservedEvidenceMeasure."
            )

        ordered = tuple(
            sorted(
                measures,
                key=lambda item: (
                    item.comparison_key,
                    item.evidence_id,
                    item.observed_at,
                ),
            )
        )

        keys = [
            item.comparison_key
            for item in ordered
        ]

        if len(keys) != len(set(keys)):
            raise (
                GovernedObservabilityInvariantError(
                    "A generation observation "
                    "cannot contain duplicate "
                    "comparison keys."
                )
            )

        object.__setattr__(
            self,
            "measures",
            ordered,
        )

        expected_observation_id = _stable_id(
            "GOE",
            {
                "generation_id": self.generation_id,
                "generation_index": self.generation_index,
                "subject_id": self.subject_id,
                "subject_kind": self.subject_kind,
                "measures": [
                    item.to_dict()
                    for item in ordered
                ],
            },
        )

        if (
            self.observation_id
            != expected_observation_id
        ):
            raise (
                GovernedObservabilityInvariantError(
                    "observation_id does not match "
                    "observation content."
                )
            )

        _assert_passive(
            judgment_asserted=(
                self.judgment_asserted
            ),
            optimality_asserted=(
                self.optimality_asserted
            ),
            truth_asserted=(
                self.truth_asserted
            ),
            verdict_asserted=(
                self.verdict_asserted
            ),
            promotion_requested=(
                self.promotion_requested
            ),
            security_guarantee_asserted=(
                self.security_guarantee_asserted
            ),
            learning_authorized=(
                self.learning_authorized
            ),
            control_requested=(
                self.control_requested
            ),
            release_certification_asserted=(
                self.release_certification_asserted
            ),
            system_truth_asserted=(
                self.system_truth_asserted
            ),
        )

    @property
    def dimensions(
        self,
    ) -> tuple[EvidenceDimension, ...]:
        return tuple(
            sorted(
                {
                    item.dimension
                    for item in self.measures
                },
                key=lambda item: item.value,
            )
        )

    def to_dict(
        self,
    ) -> dict[str, Any]:
        return {
            "version": (
                GOVERNED_OBSERVABILITY_EVIDENCE_VERSION
            ),
            "observation_id": (
                self.observation_id
            ),
            "generation_id": (
                self.generation_id
            ),
            "generation_index": (
                self.generation_index
            ),
            "subject_id": self.subject_id,
            "subject_kind": (
                self.subject_kind
            ),
            "measures": [
                item.to_dict()
                for item in self.measures
            ],
            "judgment_asserted": False,
            "optimality_asserted": False,
            "truth_asserted": False,
            "verdict_asserted": False,
            "promotion_requested": False,
            "security_guarantee_asserted": False,
            "learning_authorized": False,
            "control_requested": False,
            "release_certification_asserted": False,
            "system_truth_asserted": False,
        }


@dataclass(
    frozen=True,
    slots=True,
)
class GenerationEvidencePoint:
    generation_id: str
    generation_index: int
    observation_id: str
    value: bool | int | float | str
    evidence_id: str
    source_ref: str
    observed_at: str

    def __post_init__(
        self,
    ) -> None:
        for name in (
            "generation_id",
            "observation_id",
            "evidence_id",
            "source_ref",
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
            not isinstance(
                self.generation_index,
                int,
            )
            or isinstance(
                self.generation_index,
                bool,
            )
            or self.generation_index < 0
        ):
            raise (
                GovernedObservabilityInvariantError(
                    "generation_index must be "
                    "a non-negative integer."
                )
            )

        normalized, _ = _normalize_value(
            self.value
        )

        object.__setattr__(
            self,
            "value",
            normalized,
        )

        object.__setattr__(
            self,
            "observed_at",
            _timestamp(
                self.observed_at,
                "observed_at",
            ),
        )

    def to_dict(
        self,
    ) -> dict[str, Any]:
        return {
            "generation_id": (
                self.generation_id
            ),
            "generation_index": (
                self.generation_index
            ),
            "observation_id": (
                self.observation_id
            ),
            "value": self.value,
            "evidence_id": (
                self.evidence_id
            ),
            "source_ref": self.source_ref,
            "observed_at": (
                self.observed_at
            ),
        }


@dataclass(
    frozen=True,
    slots=True,
)
class ComparableEvidenceSeries:
    dimension: EvidenceDimension
    metric_id: str
    value_kind: EvidenceValueKind
    unit: str | None

    points: tuple[
        GenerationEvidencePoint,
        ...,
    ]

    def __post_init__(
        self,
    ) -> None:
        if not isinstance(
            self.dimension,
            EvidenceDimension,
        ):
            raise TypeError(
                "dimension must be "
                "EvidenceDimension."
            )

        if not isinstance(
            self.value_kind,
            EvidenceValueKind,
        ):
            raise TypeError(
                "value_kind must be "
                "EvidenceValueKind."
            )

        object.__setattr__(
            self,
            "metric_id",
            _required_text(
                self.metric_id,
                "metric_id",
            ),
        )

        object.__setattr__(
            self,
            "unit",
            _optional_text(
                self.unit,
                "unit",
            ),
        )

        points = tuple(
            self.points
        )

        if len(points) < 2:
            raise (
                GovernedObservabilityInvariantError(
                    "Comparable evidence series "
                    "requires at least two generations."
                )
            )

        if not all(
            isinstance(
                point,
                GenerationEvidencePoint,
            )
            for point in points
        ):
            raise TypeError(
                "points must contain only "
                "GenerationEvidencePoint."
            )

        for point in points:
            _, point_kind = _normalize_value(
                point.value
            )

            if point_kind is not self.value_kind:
                raise (
                    GovernedObservabilityInvariantError(
                        "Series value_kind does not "
                        "match point evidence value."
                    )
                )

        ordered = tuple(
            sorted(
                points,
                key=lambda point: (
                    point.generation_index,
                    point.generation_id,
                ),
            )
        )

        ids = [
            point.generation_id
            for point in ordered
        ]

        indexes = [
            point.generation_index
            for point in ordered
        ]

        if len(ids) != len(set(ids)):
            raise (
                GovernedObservabilityInvariantError(
                    "Generation IDs in one series "
                    "must be unique."
                )
            )

        if len(indexes) != len(
            set(indexes)
        ):
            raise (
                GovernedObservabilityInvariantError(
                    "Generation indexes in one "
                    "series must be unique."
                )
            )

        object.__setattr__(
            self,
            "points",
            ordered,
        )

    def to_dict(
        self,
    ) -> dict[str, Any]:
        return {
            "dimension": (
                self.dimension.value
            ),
            "metric_id": self.metric_id,
            "value_kind": (
                self.value_kind.value
            ),
            "unit": self.unit,
            "points": [
                point.to_dict()
                for point in self.points
            ],
        }


@dataclass(
    frozen=True,
    slots=True,
)
class GovernedCrossGenerationEvidence:
    comparison_id: str

    subject_id: str
    subject_kind: str

    state: CrossGenerationState

    generation_ids: tuple[str, ...]
    generation_indexes: tuple[int, ...]
    observation_ids: tuple[str, ...]

    series: tuple[
        ComparableEvidenceSeries,
        ...,
    ]

    judgment_asserted: bool = False
    optimality_asserted: bool = False
    truth_asserted: bool = False
    verdict_asserted: bool = False
    promotion_requested: bool = False
    security_guarantee_asserted: bool = False
    learning_authorized: bool = False
    control_requested: bool = False
    release_certification_asserted: bool = False
    system_truth_asserted: bool = False

    def __post_init__(
        self,
    ) -> None:
        for name in (
            "comparison_id",
            "subject_id",
            "subject_kind",
        ):
            object.__setattr__(
                self,
                name,
                _required_text(
                    getattr(self, name),
                    name,
                ),
            )

        if not isinstance(
            self.state,
            CrossGenerationState,
        ):
            raise TypeError(
                "state must be "
                "CrossGenerationState."
            )

        generation_ids = tuple(
            _required_text(
                item,
                "generation_id",
            )
            for item in self.generation_ids
        )

        generation_indexes = tuple(
            self.generation_indexes
        )

        observation_ids = tuple(
            _required_text(
                item,
                "observation_id",
            )
            for item in self.observation_ids
        )

        if len(generation_ids) < 2:
            raise (
                GovernedObservabilityInvariantError(
                    "Cross-generation evidence "
                    "requires at least two generations."
                )
            )

        if not (
            len(generation_ids)
            == len(generation_indexes)
            == len(observation_ids)
        ):
            raise (
                GovernedObservabilityInvariantError(
                    "Generation and observation "
                    "lineage lengths must match."
                )
            )

        if len(generation_ids) != len(
            set(generation_ids)
        ):
            raise (
                GovernedObservabilityInvariantError(
                    "generation_ids must be unique."
                )
            )

        if len(generation_indexes) != len(
            set(generation_indexes)
        ):
            raise (
                GovernedObservabilityInvariantError(
                    "generation_indexes must be unique."
                )
            )

        if len(observation_ids) != len(
            set(observation_ids)
        ):
            raise (
                GovernedObservabilityInvariantError(
                    "observation_ids must be unique."
                )
            )

        if not all(
            isinstance(index, int)
            and not isinstance(index, bool)
            and index >= 0
            for index in generation_indexes
        ):
            raise (
                GovernedObservabilityInvariantError(
                    "generation_indexes must contain "
                    "non-negative integers."
                )
            )

        if generation_indexes != tuple(
            sorted(generation_indexes)
        ):
            raise (
                GovernedObservabilityInvariantError(
                    "generation_indexes must be "
                    "strictly ordered."
                )
            )

        series = tuple(
            self.series
        )

        if not all(
            isinstance(
                item,
                ComparableEvidenceSeries,
            )
            for item in series
        ):
            raise TypeError(
                "series must contain only "
                "ComparableEvidenceSeries."
            )

        ordered_series = tuple(
            sorted(
                series,
                key=lambda item: (
                    item.dimension.value,
                    item.metric_id,
                    item.unit or "",
                    item.value_kind.value,
                ),
            )
        )

        expected_state = (
            CrossGenerationState.COMPARABLE
            if ordered_series
            else CrossGenerationState.INSUFFICIENT
        )

        if self.state is not expected_state:
            raise (
                GovernedObservabilityInvariantError(
                    "Cross-generation state does "
                    "not match comparable evidence."
                )
            )

        expected_lineage = tuple(
            zip(
                generation_ids,
                generation_indexes,
                observation_ids,
                strict=True,
            )
        )

        for item in ordered_series:
            series_lineage = tuple(
                (
                    point.generation_id,
                    point.generation_index,
                    point.observation_id,
                )
                for point in item.points
            )

            if series_lineage != expected_lineage:
                raise (
                    GovernedObservabilityInvariantError(
                        "Comparable series lineage "
                        "does not match comparison "
                        "generation lineage."
                    )
                )

        object.__setattr__(
            self,
            "generation_ids",
            generation_ids,
        )

        object.__setattr__(
            self,
            "generation_indexes",
            generation_indexes,
        )

        object.__setattr__(
            self,
            "observation_ids",
            observation_ids,
        )

        object.__setattr__(
            self,
            "series",
            ordered_series,
        )

        expected_comparison_id = _stable_id(
            "CGE",
            {
                "subject_id": self.subject_id,
                "subject_kind": self.subject_kind,
                "state": self.state.value,
                "generation_ids": list(
                    generation_ids
                ),
                "generation_indexes": list(
                    generation_indexes
                ),
                "observation_ids": list(
                    observation_ids
                ),
                "series": [
                    item.to_dict()
                    for item in ordered_series
                ],
            },
        )

        if (
            self.comparison_id
            != expected_comparison_id
        ):
            raise (
                GovernedObservabilityInvariantError(
                    "comparison_id does not match "
                    "cross-generation evidence."
                )
            )

        _assert_passive(
            judgment_asserted=(
                self.judgment_asserted
            ),
            optimality_asserted=(
                self.optimality_asserted
            ),
            truth_asserted=(
                self.truth_asserted
            ),
            verdict_asserted=(
                self.verdict_asserted
            ),
            promotion_requested=(
                self.promotion_requested
            ),
            security_guarantee_asserted=(
                self.security_guarantee_asserted
            ),
            learning_authorized=(
                self.learning_authorized
            ),
            control_requested=(
                self.control_requested
            ),
            release_certification_asserted=(
                self.release_certification_asserted
            ),
            system_truth_asserted=(
                self.system_truth_asserted
            ),
        )

    def to_dict(
        self,
    ) -> dict[str, Any]:
        return {
            "version": (
                GOVERNED_OBSERVABILITY_EVIDENCE_VERSION
            ),
            "comparison_id": (
                self.comparison_id
            ),
            "subject_id": self.subject_id,
            "subject_kind": (
                self.subject_kind
            ),
            "state": self.state.value,
            "generation_ids": list(
                self.generation_ids
            ),
            "generation_indexes": list(
                self.generation_indexes
            ),
            "observation_ids": list(
                self.observation_ids
            ),
            "series": [
                item.to_dict()
                for item in self.series
            ],
            "judgment_asserted": False,
            "optimality_asserted": False,
            "truth_asserted": False,
            "verdict_asserted": False,
            "promotion_requested": False,
            "security_guarantee_asserted": False,
            "learning_authorized": False,
            "control_requested": False,
            "release_certification_asserted": False,
            "system_truth_asserted": False,
        }


class GovernedObservabilityEvidence:
    @classmethod
    def capture(
        cls,
        *,
        generation_id: str,
        generation_index: int,
        subject_id: str,
        subject_kind: str,
        measures: tuple[
            ObservedEvidenceMeasure,
            ...,
        ],
    ) -> GovernedGenerationObservation:
        generation_id = _required_text(
            generation_id,
            "generation_id",
        )

        subject_id = _required_text(
            subject_id,
            "subject_id",
        )

        subject_kind = _required_text(
            subject_kind,
            "subject_kind",
        )

        if (
            not isinstance(
                generation_index,
                int,
            )
            or isinstance(
                generation_index,
                bool,
            )
            or generation_index < 0
        ):
            raise (
                GovernedObservabilityInvariantError(
                    "generation_index must be "
                    "a non-negative integer."
                )
            )

        ordered = tuple(
            sorted(
                tuple(measures),
                key=lambda item: (
                    item.comparison_key,
                    item.evidence_id,
                    item.observed_at,
                ),
            )
        )

        payload = {
            "generation_id": generation_id,
            "generation_index": (
                generation_index
            ),
            "subject_id": subject_id,
            "subject_kind": subject_kind,
            "measures": [
                item.to_dict()
                for item in ordered
            ],
        }

        return GovernedGenerationObservation(
            observation_id=_stable_id(
                "GOE",
                payload,
            ),
            generation_id=generation_id,
            generation_index=(
                generation_index
            ),
            subject_id=subject_id,
            subject_kind=subject_kind,
            measures=ordered,
        )

    @classmethod
    def compare(
        cls,
        observations: tuple[
            GovernedGenerationObservation,
            ...,
        ],
    ) -> GovernedCrossGenerationEvidence:
        rows = tuple(
            observations
        )

        if len(rows) < 2:
            raise (
                GovernedObservabilityInvariantError(
                    "Comparison requires at least "
                    "two generation observations."
                )
            )

        if not all(
            isinstance(
                row,
                GovernedGenerationObservation,
            )
            for row in rows
        ):
            raise TypeError(
                "observations must contain only "
                "GovernedGenerationObservation."
            )

        subject_pairs = {
            (
                row.subject_id,
                row.subject_kind,
            )
            for row in rows
        }

        if len(subject_pairs) != 1:
            raise (
                GovernedObservabilityInvariantError(
                    "Cross-generation comparison "
                    "requires the same subject."
                )
            )

        generation_ids = [
            row.generation_id
            for row in rows
        ]

        generation_indexes = [
            row.generation_index
            for row in rows
        ]

        if len(generation_ids) != len(
            set(generation_ids)
        ):
            raise (
                GovernedObservabilityInvariantError(
                    "Generation IDs must be unique."
                )
            )

        if len(generation_indexes) != len(
            set(generation_indexes)
        ):
            raise (
                GovernedObservabilityInvariantError(
                    "Generation indexes must be unique."
                )
            )

        ordered_rows = tuple(
            sorted(
                rows,
                key=lambda row: (
                    row.generation_index,
                    row.generation_id,
                ),
            )
        )

        maps = [
            {
                measure.comparison_key: measure
                for measure in row.measures
            }
            for row in ordered_rows
        ]

        common_keys = set(
            maps[0]
        )

        for mapping in maps[1:]:
            common_keys &= set(
                mapping
            )

        series = []

        for key in sorted(common_keys):
            dimension_value, metric_id, unit, kind_value = key

            points = tuple(
                GenerationEvidencePoint(
                    generation_id=(
                        row.generation_id
                    ),
                    generation_index=(
                        row.generation_index
                    ),
                    observation_id=(
                        row.observation_id
                    ),
                    value=(
                        mapping[key].value
                    ),
                    evidence_id=(
                        mapping[key].evidence_id
                    ),
                    source_ref=(
                        mapping[key].source_ref
                    ),
                    observed_at=(
                        mapping[key].observed_at
                    ),
                )
                for row, mapping in zip(
                    ordered_rows,
                    maps,
                    strict=True,
                )
            )

            series.append(
                ComparableEvidenceSeries(
                    dimension=EvidenceDimension(
                        dimension_value
                    ),
                    metric_id=metric_id,
                    value_kind=EvidenceValueKind(
                        kind_value
                    ),
                    unit=unit or None,
                    points=points,
                )
            )

        state = (
            CrossGenerationState.COMPARABLE
            if series
            else CrossGenerationState.INSUFFICIENT
        )

        subject_id = (
            ordered_rows[0].subject_id
        )

        subject_kind = (
            ordered_rows[0].subject_kind
        )

        payload = {
            "subject_id": subject_id,
            "subject_kind": subject_kind,
            "state": state.value,
            "generation_ids": [
                row.generation_id
                for row in ordered_rows
            ],
            "generation_indexes": [
                row.generation_index
                for row in ordered_rows
            ],
            "observation_ids": [
                row.observation_id
                for row in ordered_rows
            ],
            "series": [
                item.to_dict()
                for item in series
            ],
        }

        return GovernedCrossGenerationEvidence(
            comparison_id=_stable_id(
                "CGE",
                payload,
            ),
            subject_id=subject_id,
            subject_kind=subject_kind,
            state=state,
            generation_ids=tuple(
                row.generation_id
                for row in ordered_rows
            ),
            generation_indexes=tuple(
                row.generation_index
                for row in ordered_rows
            ),
            observation_ids=tuple(
                row.observation_id
                for row in ordered_rows
            ),
            series=tuple(series),
        )


__all__ = [
    "GOVERNED_OBSERVABILITY_EVIDENCE_VERSION",
    "GovernedObservabilityInvariantError",
    "EvidenceDimension",
    "EvidenceValueKind",
    "CrossGenerationState",
    "ObservedEvidenceMeasure",
    "GovernedGenerationObservation",
    "GenerationEvidencePoint",
    "ComparableEvidenceSeries",
    "GovernedCrossGenerationEvidence",
    "GovernedObservabilityEvidence",
]
