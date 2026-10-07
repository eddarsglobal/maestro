from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Mapping

from .radar_review_handoff import (
    RadarReviewHandoff,
    RadarReviewTarget,
)
from .radar_review_packet import (
    RadarFactorSnapshot,
)


class RadarReviewResponseInvariantError(
    ValueError
):
    pass


class RadarReviewResponseValue(StrEnum):
    RETAIN_REVIEW = "RETAIN_REVIEW"
    REQUEST_MORE_EVIDENCE = "REQUEST_MORE_EVIDENCE"
    RETURN_TO_OBSERVE = "RETURN_TO_OBSERVE"


@dataclass(
    frozen=True,
    slots=True,
)
class RadarReviewResponseEntry:
    rank: int
    evidence_id: str
    source_ref: str
    claim: str
    priority_score: float
    factors: RadarFactorSnapshot
    rationale: str
    target: RadarReviewTarget
    response: RadarReviewResponseValue
    verification_status: str = (
        "UNVERIFIED_EXTERNAL"
    )
    system_truth_asserted: bool = False
    authorization_asserted: bool = False
    promotion_asserted: bool = False
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
            raise RadarReviewResponseInvariantError(
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
                raise RadarReviewResponseInvariantError(
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

        if not isinstance(
            self.response,
            RadarReviewResponseValue,
        ):
            raise TypeError(
                "response must be "
                "RadarReviewResponseValue."
            )

        if (
            self.verification_status
            != "UNVERIFIED_EXTERNAL"
        ):
            raise RadarReviewResponseInvariantError(
                "Review response must remain "
                "UNVERIFIED_EXTERNAL."
            )

        if self.system_truth_asserted is not False:
            raise RadarReviewResponseInvariantError(
                "Review response cannot assert "
                "system truth."
            )

        if self.authorization_asserted is not False:
            raise RadarReviewResponseInvariantError(
                "Review response cannot assert "
                "authorization."
            )

        if self.promotion_asserted is not False:
            raise RadarReviewResponseInvariantError(
                "Review response cannot assert "
                "promotion."
            )

        if self.activation_asserted is not False:
            raise RadarReviewResponseInvariantError(
                "Review response cannot assert "
                "activation."
            )

        if self.execution_asserted is not False:
            raise RadarReviewResponseInvariantError(
                "Review response cannot assert "
                "execution."
            )


@dataclass(
    frozen=True,
    slots=True,
)
class RadarReviewResponse:
    entries: tuple[
        RadarReviewResponseEntry,
        ...
    ]

    def __post_init__(
        self,
    ) -> None:
        for entry in self.entries:
            if not isinstance(
                entry,
                RadarReviewResponseEntry,
            ):
                raise TypeError(
                    "entries must contain "
                    "RadarReviewResponseEntry "
                    "objects."
                )

        ids = tuple(
            entry.evidence_id
            for entry in self.entries
        )

        if len(ids) != len(set(ids)):
            raise RadarReviewResponseInvariantError(
                "Review response requires "
                "unique evidence IDs."
            )

        ranks = tuple(
            entry.rank
            for entry in self.entries
        )

        if ranks != tuple(sorted(ranks)):
            raise RadarReviewResponseInvariantError(
                "Review response must preserve "
                "ascending handoff rank order."
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


class GovernedRadarReviewResponse:
    """
    Pure ADEL0.13 review-response layer.

    It records an explicit passive response for
    every entry in an ADEL0.12 review handoff.

    RETAIN_REVIEW, REQUEST_MORE_EVIDENCE and
    RETURN_TO_OBSERVE are research-review
    recommendations only.

    They are not Verdict values, human approval,
    AY validation, EX authorization, governance
    attestations, promotion decisions, activation
    states, execution permissions, mission-state
    transitions, or truth assertions.

    This layer performs no network access,
    persistence, queue insertion, verification,
    learning, promotion, authorization,
    activation, execution, security scanning,
    skill creation, or authority escalation.
    """

    @staticmethod
    def build(
        handoff: RadarReviewHandoff,
        *,
        responses: Mapping[
            str,
            RadarReviewResponseValue,
        ],
    ) -> RadarReviewResponse:
        if not isinstance(
            handoff,
            RadarReviewHandoff,
        ):
            raise TypeError(
                "handoff must be "
                "RadarReviewHandoff."
            )

        if not isinstance(
            responses,
            Mapping,
        ):
            raise TypeError(
                "responses must be a mapping."
            )

        normalized: dict[
            str,
            RadarReviewResponseValue,
        ] = {}

        for evidence_id, response in (
            responses.items()
        ):
            if (
                not isinstance(
                    evidence_id,
                    str,
                )
                or not evidence_id
            ):
                raise RadarReviewResponseInvariantError(
                    "response evidence IDs must "
                    "be non-empty strings."
                )

            if not isinstance(
                response,
                RadarReviewResponseValue,
            ):
                raise TypeError(
                    "response values must be "
                    "RadarReviewResponseValue."
                )

            normalized[evidence_id] = response

        handoff_ids = set(
            handoff.evidence_ids
        )

        response_ids = set(
            normalized
        )

        if response_ids != handoff_ids:
            missing = sorted(
                handoff_ids - response_ids
            )

            extra = sorted(
                response_ids - handoff_ids
            )

            raise RadarReviewResponseInvariantError(
                "Responses must cover exactly "
                "the handoff evidence IDs; "
                f"missing={missing}, "
                f"extra={extra}."
            )

        rows = tuple(
            RadarReviewResponseEntry(
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
                target=entry.target,
                response=normalized[
                    entry.evidence_id
                ],
            )
            for entry in handoff.entries
        )

        return RadarReviewResponse(
            entries=rows
        )


__all__ = [
    "GovernedRadarReviewResponse",
    "RadarReviewResponse",
    "RadarReviewResponseEntry",
    "RadarReviewResponseInvariantError",
    "RadarReviewResponseValue",
]
