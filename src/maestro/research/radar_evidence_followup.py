from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from .radar_review_handoff import (
    RadarReviewTarget,
)
from .radar_review_packet import (
    RadarFactorSnapshot,
)
from .radar_review_response import (
    RadarReviewResponse,
    RadarReviewResponseValue,
)


class RadarEvidenceFollowUpInvariantError(
    ValueError
):
    pass


class RadarEvidenceNeedKind(StrEnum):
    ADDITIONAL_EXTERNAL_EVIDENCE = (
        "ADDITIONAL_EXTERNAL_EVIDENCE"
    )


@dataclass(
    frozen=True,
    slots=True,
)
class RadarEvidenceFollowUpNeed:
    rank: int
    evidence_id: str
    source_ref: str
    claim: str
    priority_score: float
    factors: RadarFactorSnapshot
    rationale: str
    target: RadarReviewTarget

    response: RadarReviewResponseValue = (
        RadarReviewResponseValue
        .REQUEST_MORE_EVIDENCE
    )

    need_kind: RadarEvidenceNeedKind = (
        RadarEvidenceNeedKind
        .ADDITIONAL_EXTERNAL_EVIDENCE
    )

    verification_status: str = (
        "UNVERIFIED_EXTERNAL"
    )

    system_truth_asserted: bool = False

    research_request_created: bool = False
    network_requested: bool = False
    tool_execution_requested: bool = False
    mission_transition_requested: bool = False
    persistence_requested: bool = False

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
            raise RadarEvidenceFollowUpInvariantError(
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
                raise RadarEvidenceFollowUpInvariantError(
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
            self.response
            is not RadarReviewResponseValue
            .REQUEST_MORE_EVIDENCE
        ):
            raise RadarEvidenceFollowUpInvariantError(
                "Evidence follow-up accepts "
                "REQUEST_MORE_EVIDENCE only."
            )

        if not isinstance(
            self.need_kind,
            RadarEvidenceNeedKind,
        ):
            raise TypeError(
                "need_kind must be "
                "RadarEvidenceNeedKind."
            )

        if (
            self.need_kind
            is not RadarEvidenceNeedKind
            .ADDITIONAL_EXTERNAL_EVIDENCE
        ):
            raise RadarEvidenceFollowUpInvariantError(
                "Unsupported evidence need kind."
            )

        if (
            self.verification_status
            != "UNVERIFIED_EXTERNAL"
        ):
            raise RadarEvidenceFollowUpInvariantError(
                "Evidence follow-up must remain "
                "UNVERIFIED_EXTERNAL."
            )

        if self.system_truth_asserted is not False:
            raise RadarEvidenceFollowUpInvariantError(
                "Evidence follow-up cannot assert "
                "system truth."
            )

        passive_flags = (
            "research_request_created",
            "network_requested",
            "tool_execution_requested",
            "mission_transition_requested",
            "persistence_requested",
            "authorization_asserted",
            "promotion_asserted",
            "activation_asserted",
            "execution_asserted",
        )

        for name in passive_flags:
            if getattr(
                self,
                name,
            ) is not False:
                raise RadarEvidenceFollowUpInvariantError(
                    "Evidence follow-up cannot assert "
                    f"{name}."
                )


@dataclass(
    frozen=True,
    slots=True,
)
class RadarEvidenceFollowUp:
    needs: tuple[
        RadarEvidenceFollowUpNeed,
        ...
    ]

    def __post_init__(
        self,
    ) -> None:
        for need in self.needs:
            if not isinstance(
                need,
                RadarEvidenceFollowUpNeed,
            ):
                raise TypeError(
                    "needs must contain "
                    "RadarEvidenceFollowUpNeed "
                    "objects."
                )

        ids = tuple(
            need.evidence_id
            for need in self.needs
        )

        if len(ids) != len(set(ids)):
            raise RadarEvidenceFollowUpInvariantError(
                "Evidence follow-up requires "
                "unique evidence IDs."
            )

        ranks = tuple(
            need.rank
            for need in self.needs
        )

        if ranks != tuple(sorted(ranks)):
            raise RadarEvidenceFollowUpInvariantError(
                "Evidence follow-up must preserve "
                "ascending review-response rank "
                "order."
            )

    @property
    def size(
        self,
    ) -> int:
        return len(
            self.needs
        )

    @property
    def evidence_ids(
        self,
    ) -> tuple[str, ...]:
        return tuple(
            need.evidence_id
            for need in self.needs
        )


class GovernedRadarEvidenceFollowUp:
    """
    Pure ADEL0.14 evidence-follow-up need layer.

    It selects only REQUEST_MORE_EVIDENCE entries
    from an ADEL0.13 RadarReviewResponse.

    The output expresses that additional external
    evidence is needed.

    It is deliberately NOT a ResearchRequest and
    does not call GovernedResearchRuntime.route()
    or GovernedResearchRuntime.execute().

    It does not create provider routing, perform
    ToolRegistry invocation, fetch sources, mutate
    mission state, enter RX_ACTIVE, persist data,
    verify truth, learn, promote, authorize,
    activate, execute, create skills, or escalate
    authority.
    """

    @staticmethod
    def build(
        response: RadarReviewResponse,
    ) -> RadarEvidenceFollowUp:
        if not isinstance(
            response,
            RadarReviewResponse,
        ):
            raise TypeError(
                "response must be "
                "RadarReviewResponse."
            )

        selected = tuple(
            entry
            for entry in response.entries
            if (
                entry.response
                is RadarReviewResponseValue
                .REQUEST_MORE_EVIDENCE
            )
        )

        needs = tuple(
            RadarEvidenceFollowUpNeed(
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
            )
            for entry in selected
        )

        return RadarEvidenceFollowUp(
            needs=needs
        )


__all__ = [
    "GovernedRadarEvidenceFollowUp",
    "RadarEvidenceFollowUp",
    "RadarEvidenceFollowUpInvariantError",
    "RadarEvidenceFollowUpNeed",
    "RadarEvidenceNeedKind",
]
