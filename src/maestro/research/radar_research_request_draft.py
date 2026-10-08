from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping

from .provider_contracts import (
    ResearchCapability,
)
from .radar_followup_candidate import (
    RadarFollowUpCandidateSet,
)
from .radar_review_handoff import (
    RadarReviewTarget,
)
from .radar_review_packet import (
    RadarFactorSnapshot,
)


class RadarResearchRequestDraftInvariantError(
    ValueError
):
    pass


@dataclass(
    frozen=True,
    slots=True,
)
class RadarResearchRequestDraftEntry:
    rank: int
    evidence_id: str
    source_ref: str
    claim: str
    priority_score: float
    factors: RadarFactorSnapshot
    rationale: str
    target: RadarReviewTarget

    capability: ResearchCapability
    arguments: Mapping[str, str]
    preferred_local: bool
    forbidden_provider_ids: tuple[str, ...] = ()

    verification_status: str = (
        "UNVERIFIED_EXTERNAL"
    )

    system_truth_asserted: bool = False

    task_id_bound: bool = False
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
            raise RadarResearchRequestDraftInvariantError(
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
                or not value.strip()
            ):
                raise RadarResearchRequestDraftInvariantError(
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
            raise RadarResearchRequestDraftInvariantError(
                "Radar request drafts must use "
                "SEARCH capability."
            )

        if not isinstance(
            self.arguments,
            Mapping,
        ):
            raise TypeError(
                "arguments must be a mapping."
            )

        arguments = dict(
            self.arguments
        )

        if set(arguments) != {"query"}:
            raise RadarResearchRequestDraftInvariantError(
                "SEARCH draft arguments must "
                "contain exactly 'query'."
            )

        query = arguments["query"]

        if (
            not isinstance(
                query,
                str,
            )
            or not query.strip()
        ):
            raise RadarResearchRequestDraftInvariantError(
                "SEARCH query must be non-empty."
            )

        object.__setattr__(
            self,
            "arguments",
            MappingProxyType(
                {
                    "query": query,
                }
            ),
        )

        if not isinstance(
            self.preferred_local,
            bool,
        ):
            raise TypeError(
                "preferred_local must be boolean."
            )

        if not isinstance(
            self.forbidden_provider_ids,
            tuple,
        ):
            raise TypeError(
                "forbidden_provider_ids must "
                "be a tuple."
            )

        for provider_id in (
            self.forbidden_provider_ids
        ):
            if (
                not isinstance(
                    provider_id,
                    str,
                )
                or not provider_id.strip()
            ):
                raise RadarResearchRequestDraftInvariantError(
                    "forbidden provider IDs must "
                    "be non-empty strings."
                )

        if len(
            self.forbidden_provider_ids
        ) != len(
            set(
                self.forbidden_provider_ids
            )
        ):
            raise RadarResearchRequestDraftInvariantError(
                "forbidden provider IDs must "
                "be unique."
            )

        if (
            self.verification_status
            != "UNVERIFIED_EXTERNAL"
        ):
            raise RadarResearchRequestDraftInvariantError(
                "Request draft must remain "
                "UNVERIFIED_EXTERNAL."
            )

        if self.system_truth_asserted is not False:
            raise RadarResearchRequestDraftInvariantError(
                "Request draft cannot assert "
                "system truth."
            )

        passive_flags = (
            "task_id_bound",
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
                raise RadarResearchRequestDraftInvariantError(
                    "Request draft cannot assert "
                    f"{name}."
                )


@dataclass(
    frozen=True,
    slots=True,
)
class RadarResearchRequestDraftSet:
    entries: tuple[
        RadarResearchRequestDraftEntry,
        ...
    ]

    def __post_init__(
        self,
    ) -> None:
        for entry in self.entries:
            if not isinstance(
                entry,
                RadarResearchRequestDraftEntry,
            ):
                raise TypeError(
                    "entries must contain "
                    "RadarResearchRequestDraftEntry "
                    "objects."
                )

        ids = tuple(
            entry.evidence_id
            for entry in self.entries
        )

        if len(ids) != len(set(ids)):
            raise RadarResearchRequestDraftInvariantError(
                "Request draft set requires "
                "unique evidence IDs."
            )

        ranks = tuple(
            entry.rank
            for entry in self.entries
        )

        if ranks != tuple(sorted(ranks)):
            raise RadarResearchRequestDraftInvariantError(
                "Request draft set must preserve "
                "ascending candidate rank order."
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


class GovernedRadarResearchRequestDraftBuilder:
    """
    Pure ADEL0.16 request-draft layer.

    Converts passive ADEL0.15 SEARCH candidates
    into passive declarative request drafts.

    A draft is NOT a ResearchRequest.

    No task execution identity is bound here.

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
    def build(
        candidates: RadarFollowUpCandidateSet,
    ) -> RadarResearchRequestDraftSet:
        if not isinstance(
            candidates,
            RadarFollowUpCandidateSet,
        ):
            raise TypeError(
                "candidates must be "
                "RadarFollowUpCandidateSet."
            )

        entries = tuple(
            RadarResearchRequestDraftEntry(
                rank=candidate.rank,
                evidence_id=(
                    candidate.evidence_id
                ),
                source_ref=(
                    candidate.source_ref
                ),
                claim=candidate.claim,
                priority_score=(
                    candidate.priority_score
                ),
                factors=candidate.factors,
                rationale=(
                    candidate.rationale
                ),
                target=candidate.target,
                capability=(
                    candidate.capability
                ),
                arguments={
                    "query": candidate.query,
                },
                preferred_local=(
                    candidate.preferred_local
                ),
                forbidden_provider_ids=(),
            )
            for candidate
            in candidates.entries
        )

        return RadarResearchRequestDraftSet(
            entries=entries
        )


__all__ = [
    "GovernedRadarResearchRequestDraftBuilder",
    "RadarResearchRequestDraftEntry",
    "RadarResearchRequestDraftInvariantError",
    "RadarResearchRequestDraftSet",
]
