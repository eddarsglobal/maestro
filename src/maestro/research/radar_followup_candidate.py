from __future__ import annotations

from dataclasses import dataclass

from .provider_contracts import (
    ResearchCapability,
)
from .radar_evidence_followup import (
    RadarEvidenceFollowUp,
    RadarEvidenceFollowUpNeed,
)
from .radar_review_handoff import (
    RadarReviewTarget,
)
from .radar_review_packet import (
    RadarFactorSnapshot,
)


class RadarFollowUpCandidateInvariantError(
    ValueError
):
    pass


@dataclass(
    frozen=True,
    slots=True,
)
class RadarFollowUpCandidate:
    rank: int
    evidence_id: str
    source_ref: str
    claim: str
    priority_score: float
    factors: RadarFactorSnapshot
    rationale: str
    target: RadarReviewTarget

    capability: ResearchCapability = (
        ResearchCapability.SEARCH
    )

    query: str = ""

    preferred_local: bool = True

    verification_status: str = (
        "UNVERIFIED_EXTERNAL"
    )

    system_truth_asserted: bool = False

    research_request_created: bool = False
    provider_selected: bool = False
    routing_decision_created: bool = False
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
            raise RadarFollowUpCandidateInvariantError(
                "rank must be a positive integer."
            )

        for name in (
            "evidence_id",
            "source_ref",
            "claim",
            "rationale",
            "query",
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
                or not value.strip()
            ):
                raise RadarFollowUpCandidateInvariantError(
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
            self.capability,
            ResearchCapability,
        ):
            raise TypeError(
                "capability must be "
                "ResearchCapability."
            )

        if (
            self.capability
            is not ResearchCapability.SEARCH
        ):
            raise RadarFollowUpCandidateInvariantError(
                "Radar follow-up candidates must "
                "use SEARCH capability."
            )

        if not isinstance(
            self.preferred_local,
            bool,
        ):
            raise TypeError(
                "preferred_local must be boolean."
            )

        if (
            self.verification_status
            != "UNVERIFIED_EXTERNAL"
        ):
            raise RadarFollowUpCandidateInvariantError(
                "Follow-up candidate must remain "
                "UNVERIFIED_EXTERNAL."
            )

        if self.system_truth_asserted is not False:
            raise RadarFollowUpCandidateInvariantError(
                "Follow-up candidate cannot assert "
                "system truth."
            )

        passive_flags = (
            "research_request_created",
            "provider_selected",
            "routing_decision_created",
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
                raise RadarFollowUpCandidateInvariantError(
                    "Follow-up candidate cannot assert "
                    f"{name}."
                )


@dataclass(
    frozen=True,
    slots=True,
)
class RadarFollowUpCandidateSet:
    entries: tuple[
        RadarFollowUpCandidate,
        ...
    ]

    def __post_init__(
        self,
    ) -> None:
        for entry in self.entries:
            if not isinstance(
                entry,
                RadarFollowUpCandidate,
            ):
                raise TypeError(
                    "entries must contain "
                    "RadarFollowUpCandidate objects."
                )

        ids = tuple(
            entry.evidence_id
            for entry in self.entries
        )

        if len(ids) != len(set(ids)):
            raise RadarFollowUpCandidateInvariantError(
                "Candidate set requires unique "
                "evidence IDs."
            )

        ranks = tuple(
            entry.rank
            for entry in self.entries
        )

        if ranks != tuple(sorted(ranks)):
            raise RadarFollowUpCandidateInvariantError(
                "Candidate set must preserve "
                "ascending follow-up rank order."
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


class GovernedRadarFollowUpCandidateBuilder:
    """
    Pure ADEL0.15 candidate-preparation layer.

    Converts passive ADEL0.14 evidence-follow-up
    needs into passive SEARCH candidates.

    A candidate is NOT a ResearchRequest.

    This layer performs no provider selection,
    ResearchRoutingDecision creation, runtime
    routing, runtime execution, ToolRegistry
    invocation, network access, mission state
    transition, RX activation, persistence,
    verification, learning, promotion,
    authorization, activation, execution,
    skill creation, or authority escalation.
    """

    @staticmethod
    def _query(
        need: RadarEvidenceFollowUpNeed,
    ) -> str:
        return (
            "Find independent external evidence "
            "relevant to this claim: "
            f"{need.claim}"
        )

    @classmethod
    def build(
        cls,
        followup: RadarEvidenceFollowUp,
    ) -> RadarFollowUpCandidateSet:
        if not isinstance(
            followup,
            RadarEvidenceFollowUp,
        ):
            raise TypeError(
                "followup must be "
                "RadarEvidenceFollowUp."
            )

        entries = tuple(
            RadarFollowUpCandidate(
                rank=need.rank,
                evidence_id=(
                    need.evidence_id
                ),
                source_ref=(
                    need.source_ref
                ),
                claim=need.claim,
                priority_score=(
                    need.priority_score
                ),
                factors=need.factors,
                rationale=(
                    need.rationale
                ),
                target=need.target,
                capability=(
                    ResearchCapability.SEARCH
                ),
                query=cls._query(
                    need
                ),
                preferred_local=True,
            )
            for need in followup.needs
        )

        return RadarFollowUpCandidateSet(
            entries=entries
        )


__all__ = [
    "GovernedRadarFollowUpCandidateBuilder",
    "RadarFollowUpCandidate",
    "RadarFollowUpCandidateInvariantError",
    "RadarFollowUpCandidateSet",
]
