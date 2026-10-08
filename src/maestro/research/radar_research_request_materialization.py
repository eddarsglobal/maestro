from __future__ import annotations

from dataclasses import dataclass

from .identity import (
    require_durable_research_task_id,
)
from .provider_contracts import (
    ResearchCapability,
)
from .radar_research_draft_admission import (
    RadarResearchDraftAdmissionStatus,
)
from .radar_research_task_binding import (
    RadarResearchTaskBinding,
)
from .radar_review_handoff import (
    RadarReviewTarget,
)
from .radar_review_packet import (
    RadarFactorSnapshot,
)
from .runtime_contracts import (
    ResearchRequest,
)


class RadarResearchRequestMaterializationInvariantError(
    ValueError
):
    pass


@dataclass(
    frozen=True,
    slots=True,
)
class RadarResearchRequestMaterializationEntry:
    rank: int
    evidence_id: str
    source_ref: str
    claim: str
    priority_score: float
    factors: RadarFactorSnapshot
    rationale: str
    target: RadarReviewTarget

    admission_status: (
        RadarResearchDraftAdmissionStatus
    )
    admission_reason: str

    request: ResearchRequest

    verification_status: str = (
        "UNVERIFIED_EXTERNAL"
    )

    system_truth_asserted: bool = False

    task_id_bound: bool = True
    research_request_created: bool = True

    provider_selected: bool = False
    routing_decision_created: bool = False
    tool_validated: bool = False
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
            raise (
                RadarResearchRequestMaterializationInvariantError(
                    "rank must be a positive integer."
                )
            )

        for name in (
            "evidence_id",
            "source_ref",
            "claim",
            "rationale",
            "admission_reason",
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
                raise (
                    RadarResearchRequestMaterializationInvariantError(
                        f"{name} must be non-empty."
                    )
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
                "target must be "
                "RadarReviewTarget."
            )

        if (
            self.admission_status
            is not RadarResearchDraftAdmissionStatus
            .ADMISSIBLE
        ):
            raise (
                RadarResearchRequestMaterializationInvariantError(
                    "Only ADMISSIBLE task bindings "
                    "may be materialized."
                )
            )

        if not isinstance(
            self.request,
            ResearchRequest,
        ):
            raise TypeError(
                "request must be a "
                "ResearchRequest."
            )

        require_durable_research_task_id(
            self.request.task_id
        )

        if (
            self.request.capability
            is not ResearchCapability.SEARCH
        ):
            raise (
                RadarResearchRequestMaterializationInvariantError(
                    "Radar materialization supports "
                    "only SEARCH requests."
                )
            )

        if set(
            self.request.arguments
        ) != {"query"}:
            raise (
                RadarResearchRequestMaterializationInvariantError(
                    "Materialized SEARCH request "
                    "must contain exactly 'query'."
                )
            )

        query = (
            self.request.arguments[
                "query"
            ]
        )

        if (
            not isinstance(
                query,
                str,
            )
            or not query.strip()
        ):
            raise (
                RadarResearchRequestMaterializationInvariantError(
                    "Materialized SEARCH query "
                    "must be non-empty."
                )
            )

        if (
            self.verification_status
            != "UNVERIFIED_EXTERNAL"
        ):
            raise (
                RadarResearchRequestMaterializationInvariantError(
                    "Materialized request must "
                    "remain UNVERIFIED_EXTERNAL."
                )
            )

        if self.system_truth_asserted is not False:
            raise (
                RadarResearchRequestMaterializationInvariantError(
                    "Materialization cannot "
                    "assert truth."
                )
            )

        if self.task_id_bound is not True:
            raise (
                RadarResearchRequestMaterializationInvariantError(
                    "Materialization requires "
                    "bound task identity."
                )
            )

        if (
            self.research_request_created
            is not True
        ):
            raise (
                RadarResearchRequestMaterializationInvariantError(
                    "Materialization must mark "
                    "ResearchRequest creation."
                )
            )

        passive_flags = (
            "provider_selected",
            "routing_decision_created",
            "tool_validated",
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
                raise (
                    RadarResearchRequestMaterializationInvariantError(
                        "Materialization cannot "
                        f"assert {name}."
                    )
                )

    @property
    def task_id(
        self,
    ) -> str:
        return self.request.task_id


@dataclass(
    frozen=True,
    slots=True,
)
class RadarResearchRequestMaterialization:
    entries: tuple[
        RadarResearchRequestMaterializationEntry,
        ...
    ]

    def __post_init__(
        self,
    ) -> None:
        for entry in self.entries:
            if not isinstance(
                entry,
                RadarResearchRequestMaterializationEntry,
            ):
                raise TypeError(
                    "entries must contain "
                    "RadarResearchRequestMaterializationEntry."
                )

        ids = tuple(
            entry.evidence_id
            for entry in self.entries
        )

        if len(ids) != len(set(ids)):
            raise (
                RadarResearchRequestMaterializationInvariantError(
                    "Materialization requires "
                    "unique evidence IDs."
                )
            )

        ranks = tuple(
            entry.rank
            for entry in self.entries
        )

        if ranks != tuple(sorted(ranks)):
            raise (
                RadarResearchRequestMaterializationInvariantError(
                    "Materialization must preserve "
                    "ascending binding rank order."
                )
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

    @property
    def task_ids(
        self,
    ) -> tuple[str, ...]:
        return tuple(
            entry.request.task_id
            for entry in self.entries
        )

    @property
    def requests(
        self,
    ) -> tuple[
        ResearchRequest,
        ...
    ]:
        return tuple(
            entry.request
            for entry in self.entries
        )


class GovernedRadarResearchRequestMaterializer:
    """
    Pure ADEL0.19 request-materialization layer.

    Converts an ADEL0.18 governed task binding into
    immutable ResearchRequest contracts.

    Creating a ResearchRequest is NOT routing.

    REQUEST MATERIALIZED != ROUTED.
    REQUEST MATERIALIZED != PROVIDER SELECTED.
    REQUEST MATERIALIZED != TOOL VALIDATED.
    REQUEST MATERIALIZED != NETWORK REQUESTED.
    REQUEST MATERIALIZED != EXECUTED.

    This layer performs no provider discovery,
    provider ranking, ResearchRoutingDecision
    creation, runtime route(), runtime execute(),
    ToolRegistry lookup/invocation, network access,
    mission transition, RX activation, persistence,
    verification, learning, promotion,
    authorization, activation, execution,
    skill creation, or authority escalation.
    """

    @staticmethod
    def materialize(
        binding: RadarResearchTaskBinding,
    ) -> RadarResearchRequestMaterialization:
        if not isinstance(
            binding,
            RadarResearchTaskBinding,
        ):
            raise TypeError(
                "binding must be "
                "RadarResearchTaskBinding."
            )

        entries = []

        for bound in binding.entries:
            request = ResearchRequest(
                task_id=bound.task_id,
                capability=bound.capability,
                arguments=bound.arguments,
                preferred_local=(
                    bound.preferred_local
                ),
                forbidden_provider_ids=(
                    frozenset(
                        bound.forbidden_provider_ids
                    )
                ),
            )

            entries.append(
                RadarResearchRequestMaterializationEntry(
                    rank=bound.rank,
                    evidence_id=(
                        bound.evidence_id
                    ),
                    source_ref=(
                        bound.source_ref
                    ),
                    claim=bound.claim,
                    priority_score=(
                        bound.priority_score
                    ),
                    factors=bound.factors,
                    rationale=(
                        bound.rationale
                    ),
                    target=bound.target,
                    admission_status=(
                        bound.admission_status
                    ),
                    admission_reason=(
                        bound.admission_reason
                    ),
                    request=request,
                )
            )

        return RadarResearchRequestMaterialization(
            entries=tuple(entries)
        )


__all__ = [
    "GovernedRadarResearchRequestMaterializer",
    "RadarResearchRequestMaterialization",
    "RadarResearchRequestMaterializationEntry",
    "RadarResearchRequestMaterializationInvariantError",
]
