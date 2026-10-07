from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Mapping

from .radar_decision_envelope import (
    RadarDisposition,
)
from .radar_review_packet import (
    RadarFactorSnapshot,
    RadarReviewPacket,
)


class RadarReviewHandoffInvariantError(
    ValueError
):
    pass


class RadarReviewTarget(StrEnum):
    HUMAN_REVIEW = "HUMAN_REVIEW"
    AY_REVIEW = "AY_REVIEW"
    EX_REVIEW = "EX_REVIEW"


@dataclass(
    frozen=True,
    slots=True,
)
class RadarReviewAssignment:
    evidence_id: str
    target: RadarReviewTarget

    def __post_init__(
        self,
    ) -> None:
        if (
            not isinstance(
                self.evidence_id,
                str,
            )
            or not self.evidence_id
        ):
            raise RadarReviewHandoffInvariantError(
                "evidence_id must be non-empty."
            )

        if not isinstance(
            self.target,
            RadarReviewTarget,
        ):
            raise TypeError(
                "target must be RadarReviewTarget."
            )


@dataclass(
    frozen=True,
    slots=True,
)
class RadarReviewHandoffEntry:
    rank: int
    evidence_id: str
    source_ref: str
    claim: str
    priority_score: float
    factors: RadarFactorSnapshot
    rationale: str
    target: RadarReviewTarget
    disposition: RadarDisposition = (
        RadarDisposition.REVIEW
    )
    verification_status: str = (
        "UNVERIFIED_EXTERNAL"
    )
    system_truth_asserted: bool = False
    authorization_asserted: bool = False
    activation_asserted: bool = False
    execution_asserted: bool = False

    def __post_init__(
        self,
    ) -> None:
        if (
            not isinstance(
                self.rank,
                int,
            )
            or isinstance(
                self.rank,
                bool,
            )
            or self.rank < 1
        ):
            raise RadarReviewHandoffInvariantError(
                "rank must be a positive integer."
            )

        for name in (
            "evidence_id",
            "source_ref",
            "claim",
            "rationale",
        ):
            value = getattr(
                self,
                name,
            )

            if (
                not isinstance(
                    value,
                    str,
                )
                or not value
            ):
                raise RadarReviewHandoffInvariantError(
                    f"{name} must be non-empty."
                )

        if not isinstance(
            self.factors,
            RadarFactorSnapshot,
        ):
            raise TypeError(
                "factors must be "
                "RadarFactorSnapshot."
            )

        if not isinstance(
            self.target,
            RadarReviewTarget,
        ):
            raise TypeError(
                "target must be RadarReviewTarget."
            )

        if (
            self.disposition
            is not RadarDisposition.REVIEW
        ):
            raise RadarReviewHandoffInvariantError(
                "Review handoff accepts "
                "REVIEW disposition only."
            )

        if (
            self.verification_status
            != "UNVERIFIED_EXTERNAL"
        ):
            raise RadarReviewHandoffInvariantError(
                "Review handoff must remain "
                "UNVERIFIED_EXTERNAL."
            )

        if (
            self.system_truth_asserted
            is not False
        ):
            raise RadarReviewHandoffInvariantError(
                "Review handoff cannot assert "
                "system truth."
            )

        if (
            self.authorization_asserted
            is not False
        ):
            raise RadarReviewHandoffInvariantError(
                "Review handoff cannot assert "
                "authorization."
            )

        if (
            self.activation_asserted
            is not False
        ):
            raise RadarReviewHandoffInvariantError(
                "Review handoff cannot assert "
                "activation."
            )

        if (
            self.execution_asserted
            is not False
        ):
            raise RadarReviewHandoffInvariantError(
                "Review handoff cannot assert "
                "execution."
            )


@dataclass(
    frozen=True,
    slots=True,
)
class RadarReviewHandoff:
    entries: tuple[
        RadarReviewHandoffEntry,
        ...
    ]

    def __post_init__(
        self,
    ) -> None:
        ids = tuple(
            entry.evidence_id
            for entry in self.entries
        )

        if len(ids) != len(set(ids)):
            raise RadarReviewHandoffInvariantError(
                "Review handoff requires "
                "unique evidence IDs."
            )

        ranks = tuple(
            entry.rank
            for entry in self.entries
        )

        if tuple(sorted(ranks)) != ranks:
            raise RadarReviewHandoffInvariantError(
                "Review handoff must preserve "
                "ascending packet rank order."
            )

        for entry in self.entries:
            if not isinstance(
                entry,
                RadarReviewHandoffEntry,
            ):
                raise TypeError(
                    "entries must contain "
                    "RadarReviewHandoffEntry "
                    "objects."
                )

    @property
    def size(
        self,
    ) -> int:
        return len(
            self.entries
        )

    @property
    def evidence_ids(
        self,
    ) -> tuple[str, ...]:
        return tuple(
            entry.evidence_id
            for entry in self.entries
        )


class GovernedRadarReviewHandoff:
    """
    Pure ADEL0.12 review-routing layer.

    It selects REVIEW entries from an existing
    ADEL0.11 RadarReviewPacket and binds each
    selected entry to an explicit passive review
    target supplied by the caller.

    HUMAN_REVIEW, AY_REVIEW and EX_REVIEW are
    routing labels only.

    They are not MetaAction requests, mission
    state transitions, governance attestations,
    AY validation, EX authorization, promotion,
    activation, execution permission, or truth.

    This layer performs no queue insertion,
    persistence, network access, verification,
    learning, promotion, authorization,
    activation, execution, security scanning,
    skill creation, or authority escalation.
    """

    @staticmethod
    def build(
        packet: RadarReviewPacket,
        *,
        assignments: Mapping[
            str,
            RadarReviewTarget,
        ],
    ) -> RadarReviewHandoff:
        if not isinstance(
            packet,
            RadarReviewPacket,
        ):
            raise TypeError(
                "packet must be "
                "RadarReviewPacket."
            )

        if not isinstance(
            assignments,
            Mapping,
        ):
            raise TypeError(
                "assignments must be a mapping."
            )

        normalized: dict[
            str,
            RadarReviewTarget,
        ] = {}

        for evidence_id, target in (
            assignments.items()
        ):
            if (
                not isinstance(
                    evidence_id,
                    str,
                )
                or not evidence_id
            ):
                raise RadarReviewHandoffInvariantError(
                    "assignment evidence IDs "
                    "must be non-empty strings."
                )

            if not isinstance(
                target,
                RadarReviewTarget,
            ):
                raise TypeError(
                    "assignment targets must be "
                    "RadarReviewTarget."
                )

            normalized[evidence_id] = target

        review_entries = tuple(
            entry
            for entry in packet.entries
            if (
                entry.disposition
                is RadarDisposition.REVIEW
            )
        )

        review_ids = {
            entry.evidence_id
            for entry in review_entries
        }

        assignment_ids = set(
            normalized
        )

        if assignment_ids != review_ids:
            missing = sorted(
                review_ids - assignment_ids
            )
            extra = sorted(
                assignment_ids - review_ids
            )

            raise RadarReviewHandoffInvariantError(
                "Assignments must cover exactly "
                "the REVIEW evidence IDs; "
                f"missing={missing}, "
                f"extra={extra}."
            )

        rows = tuple(
            RadarReviewHandoffEntry(
                rank=entry.rank,
                evidence_id=(
                    entry.evidence_id
                ),
                source_ref=(
                    entry.source_ref
                ),
                claim=entry.claim,
                priority_score=(
                    entry.priority_score
                ),
                factors=entry.factors,
                rationale=(
                    entry.rationale
                ),
                target=normalized[
                    entry.evidence_id
                ],
            )
            for entry in review_entries
        )

        return RadarReviewHandoff(
            entries=rows
        )


__all__ = [
    "GovernedRadarReviewHandoff",
    "RadarReviewAssignment",
    "RadarReviewHandoff",
    "RadarReviewHandoffEntry",
    "RadarReviewHandoffInvariantError",
    "RadarReviewTarget",
]
