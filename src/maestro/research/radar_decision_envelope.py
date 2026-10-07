from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from math import isfinite

from .radar_portfolio import (
    RadarPortfolioResult,
)


class RadarDecisionEnvelopeInvariantError(
    ValueError
):
    pass


class RadarDisposition(StrEnum):
    OBSERVE = "OBSERVE"
    INVESTIGATE = "INVESTIGATE"
    REVIEW = "REVIEW"


def _threshold(
    value: float,
    name: str,
) -> float:
    if isinstance(
        value,
        bool,
    ) or not isinstance(
        value,
        (int, float),
    ):
        raise TypeError(
            f"{name} must be a real number."
        )

    normalized = float(
        value
    )

    if not isfinite(
        normalized
    ):
        raise RadarDecisionEnvelopeInvariantError(
            f"{name} must be finite."
        )

    if not (
        0.0
        <= normalized
        <= 1.0
    ):
        raise RadarDecisionEnvelopeInvariantError(
            f"{name} must be within [0, 1]."
        )

    return normalized


@dataclass(
    frozen=True,
    slots=True,
)
class RadarDecisionPolicy:
    investigate_min_priority: float
    review_min_priority: float

    def __post_init__(
        self,
    ) -> None:
        investigate = _threshold(
            self.investigate_min_priority,
            "investigate_min_priority",
        )

        review = _threshold(
            self.review_min_priority,
            "review_min_priority",
        )

        if investigate > review:
            raise RadarDecisionEnvelopeInvariantError(
                "investigate_min_priority "
                "cannot exceed "
                "review_min_priority."
            )

        object.__setattr__(
            self,
            "investigate_min_priority",
            investigate,
        )

        object.__setattr__(
            self,
            "review_min_priority",
            review,
        )


@dataclass(
    frozen=True,
    slots=True,
)
class RadarDecisionEntry:
    rank: int
    evidence_id: str
    priority_score: float
    disposition: RadarDisposition
    verification_status: str = (
        "UNVERIFIED_EXTERNAL"
    )
    system_truth_asserted: bool = False

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
            raise RadarDecisionEnvelopeInvariantError(
                "rank must be a positive integer."
            )

        if (
            not isinstance(
                self.evidence_id,
                str,
            )
            or not self.evidence_id
        ):
            raise RadarDecisionEnvelopeInvariantError(
                "evidence_id must be non-empty."
            )

        score = _threshold(
            self.priority_score,
            "priority_score",
        )

        object.__setattr__(
            self,
            "priority_score",
            score,
        )

        if not isinstance(
            self.disposition,
            RadarDisposition,
        ):
            raise TypeError(
                "disposition must be "
                "RadarDisposition."
            )

        if (
            self.verification_status
            != "UNVERIFIED_EXTERNAL"
        ):
            raise RadarDecisionEnvelopeInvariantError(
                "Radar decision envelope must "
                "remain UNVERIFIED_EXTERNAL."
            )

        if (
            self.system_truth_asserted
            is not False
        ):
            raise RadarDecisionEnvelopeInvariantError(
                "Radar decision envelope "
                "cannot assert system truth."
            )


@dataclass(
    frozen=True,
    slots=True,
)
class RadarDecisionEnvelope:
    entries: tuple[
        RadarDecisionEntry,
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
            raise RadarDecisionEnvelopeInvariantError(
                "Decision envelope requires "
                "unique evidence IDs."
            )

        expected_ranks = tuple(
            range(
                1,
                len(self.entries) + 1,
            )
        )

        actual_ranks = tuple(
            entry.rank
            for entry in self.entries
        )

        if actual_ranks != expected_ranks:
            raise RadarDecisionEnvelopeInvariantError(
                "Decision envelope ranks must "
                "be contiguous and ordered."
            )

        for entry in self.entries:
            if not isinstance(
                entry,
                RadarDecisionEntry,
            ):
                raise TypeError(
                    "entries must contain "
                    "RadarDecisionEntry objects."
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


class GovernedRadarDecisionEnvelope:
    """
    Pure ADEL0.10 recommendation envelope.

    It maps an already-ranked ADEL0.9 Radar
    portfolio to passive research dispositions
    using explicit caller-supplied thresholds.

    OBSERVE, INVESTIGATE and REVIEW are research
    recommendations only.

    They are not Verdict values, governance
    attestations, promotion decisions,
    authorization decisions, activation states,
    execution permissions, or truth assertions.

    This layer performs no network access,
    persistence, learning, promotion,
    verification, activation, security scanning,
    tool execution, skill creation, or authority
    escalation.
    """

    @staticmethod
    def evaluate(
        portfolio: RadarPortfolioResult,
        *,
        policy: RadarDecisionPolicy,
    ) -> RadarDecisionEnvelope:
        if not isinstance(
            portfolio,
            RadarPortfolioResult,
        ):
            raise TypeError(
                "portfolio must be "
                "RadarPortfolioResult."
            )

        if not isinstance(
            policy,
            RadarDecisionPolicy,
        ):
            raise TypeError(
                "policy must be "
                "RadarDecisionPolicy."
            )

        entries: list[
            RadarDecisionEntry
        ] = []

        for index, observation in enumerate(
            portfolio.ranked_observations,
            start=1,
        ):
            if (
                observation.verification_status
                != "UNVERIFIED_EXTERNAL"
            ):
                raise RadarDecisionEnvelopeInvariantError(
                    "Decision envelope accepts "
                    "UNVERIFIED_EXTERNAL "
                    "observations only."
                )

            if (
                observation.system_truth_asserted
                is not False
            ):
                raise RadarDecisionEnvelopeInvariantError(
                    "Decision envelope cannot "
                    "consume an observation "
                    "asserting system truth."
                )

            score = observation.priority_score

            if (
                score
                >= policy.review_min_priority
            ):
                disposition = (
                    RadarDisposition.REVIEW
                )

            elif (
                score
                >= policy
                .investigate_min_priority
            ):
                disposition = (
                    RadarDisposition.INVESTIGATE
                )

            else:
                disposition = (
                    RadarDisposition.OBSERVE
                )

            entries.append(
                RadarDecisionEntry(
                    rank=index,
                    evidence_id=(
                        observation.evidence_id
                    ),
                    priority_score=score,
                    disposition=disposition,
                )
            )

        return RadarDecisionEnvelope(
            entries=tuple(entries)
        )


__all__ = [
    "GovernedRadarDecisionEnvelope",
    "RadarDecisionEnvelope",
    "RadarDecisionEntry",
    "RadarDecisionEnvelopeInvariantError",
    "RadarDecisionPolicy",
    "RadarDisposition",
]
