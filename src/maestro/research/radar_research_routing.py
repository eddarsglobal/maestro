from __future__ import annotations

from dataclasses import dataclass

from .radar_research_draft_admission import (
    RadarResearchDraftAdmissionStatus,
)
from .radar_research_request_materialization import (
    RadarResearchRequestMaterialization,
)
from .radar_review_handoff import (
    RadarReviewTarget,
)
from .radar_review_packet import (
    RadarFactorSnapshot,
)
from .runtime import (
    GovernedResearchRuntime,
)
from .runtime_contracts import (
    ResearchRequest,
    ResearchRoutingDecision,
)


class RadarResearchRoutingInvariantError(
    ValueError
):
    pass


@dataclass(
    frozen=True,
    slots=True,
)
class RadarResearchRoutingEntry:
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
    decision: ResearchRoutingDecision

    verification_status: str = (
        "UNVERIFIED_EXTERNAL"
    )

    system_truth_asserted: bool = False

    task_id_bound: bool = True
    research_request_created: bool = True

    provider_selected: bool = True
    routing_decision_created: bool = True

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
            raise RadarResearchRoutingInvariantError(
                "rank must be a positive integer."
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
                raise RadarResearchRoutingInvariantError(
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
            self.admission_status
            is not RadarResearchDraftAdmissionStatus
            .ADMISSIBLE
        ):
            raise RadarResearchRoutingInvariantError(
                "Only ADMISSIBLE materialized "
                "requests may be routed."
            )

        if not isinstance(
            self.request,
            ResearchRequest,
        ):
            raise TypeError(
                "request must be "
                "ResearchRequest."
            )

        if not isinstance(
            self.decision,
            ResearchRoutingDecision,
        ):
            raise TypeError(
                "decision must be "
                "ResearchRoutingDecision."
            )

        if (
            not isinstance(
                self.decision.provider_id,
                str,
            )
            or not self.decision.provider_id.strip()
        ):
            raise RadarResearchRoutingInvariantError(
                "Routing decision requires "
                "provider_id."
            )

        if (
            not isinstance(
                self.decision.tool_name,
                str,
            )
            or not self.decision.tool_name.strip()
        ):
            raise RadarResearchRoutingInvariantError(
                "Routing decision requires "
                "tool_name."
            )

        if (
            not isinstance(
                self.decision.candidates,
                tuple,
            )
            or not self.decision.candidates
        ):
            raise RadarResearchRoutingInvariantError(
                "Routing decision requires "
                "candidate providers."
            )

        if (
            len(
                self.decision.candidates
            )
            != len(
                set(
                    self.decision.candidates
                )
            )
        ):
            raise RadarResearchRoutingInvariantError(
                "Routing candidates must "
                "be unique."
            )

        if (
            self.decision.provider_id
            not in self.decision.candidates
        ):
            raise RadarResearchRoutingInvariantError(
                "Selected provider must "
                "belong to candidates."
            )

        if (
            not isinstance(
                self.decision.reason,
                str,
            )
            or not self.decision.reason.strip()
        ):
            raise RadarResearchRoutingInvariantError(
                "Routing decision requires "
                "a reason."
            )

        if (
            self.verification_status
            != "UNVERIFIED_EXTERNAL"
        ):
            raise RadarResearchRoutingInvariantError(
                "Routing must remain "
                "UNVERIFIED_EXTERNAL."
            )

        if self.system_truth_asserted is not False:
            raise RadarResearchRoutingInvariantError(
                "Routing cannot assert truth."
            )

        required_true = (
            "task_id_bound",
            "research_request_created",
            "provider_selected",
            "routing_decision_created",
        )

        for name in required_true:
            if getattr(
                self,
                name,
            ) is not True:
                raise RadarResearchRoutingInvariantError(
                    "Routing requires "
                    f"{name}=True."
                )

        passive_flags = (
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
                raise RadarResearchRoutingInvariantError(
                    "Routing cannot assert "
                    f"{name}."
                )


@dataclass(
    frozen=True,
    slots=True,
)
class RadarResearchRoutingResult:
    entries: tuple[
        RadarResearchRoutingEntry,
        ...
    ]

    def __post_init__(
        self,
    ) -> None:
        for entry in self.entries:
            if not isinstance(
                entry,
                RadarResearchRoutingEntry,
            ):
                raise TypeError(
                    "entries must contain "
                    "RadarResearchRoutingEntry."
                )

        ids = tuple(
            entry.evidence_id
            for entry in self.entries
        )

        if len(ids) != len(set(ids)):
            raise RadarResearchRoutingInvariantError(
                "Routing requires unique "
                "evidence IDs."
            )

        ranks = tuple(
            entry.rank
            for entry in self.entries
        )

        if ranks != tuple(sorted(ranks)):
            raise RadarResearchRoutingInvariantError(
                "Routing must preserve "
                "ascending materialization order."
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
    def provider_ids(
        self,
    ) -> tuple[str, ...]:
        return tuple(
            entry.decision.provider_id
            for entry in self.entries
        )


class GovernedRadarResearchRouter:
    """
    ADEL0.20 governed routing boundary.

    Uses the existing GovernedResearchRuntime.route()
    operation because that operation is a passive,
    deterministic provider-eligibility and ranking
    boundary.

    ROUTED != TOOL VALIDATED.
    ROUTED != TOOL EXECUTION.
    ROUTED != NETWORK ACCESS.
    ROUTED != AUTHORIZATION.
    ROUTED != ACTIVATION.
    ROUTED != TRUTH.

    This layer never calls runtime.execute(),
    runtime._validate_tool(), ToolRegistry.invoke(),
    provider-registry mutation methods, network
    transport, persistence, mission transition,
    learning, promotion, activation, execution,
    skill creation, or truth escalation.
    """

    @staticmethod
    def route(
        materialization: (
            RadarResearchRequestMaterialization
        ),
        *,
        runtime: GovernedResearchRuntime,
    ) -> RadarResearchRoutingResult:
        if not isinstance(
            materialization,
            RadarResearchRequestMaterialization,
        ):
            raise TypeError(
                "materialization must be "
                "RadarResearchRequestMaterialization."
            )

        if not isinstance(
            runtime,
            GovernedResearchRuntime,
        ):
            raise TypeError(
                "runtime must be "
                "GovernedResearchRuntime."
            )

        entries = []

        for materialized in (
            materialization.entries
        ):
            decision = runtime.route(
                materialized.request
            )

            entries.append(
                RadarResearchRoutingEntry(
                    rank=materialized.rank,
                    evidence_id=(
                        materialized.evidence_id
                    ),
                    source_ref=(
                        materialized.source_ref
                    ),
                    claim=materialized.claim,
                    priority_score=(
                        materialized.priority_score
                    ),
                    factors=(
                        materialized.factors
                    ),
                    rationale=(
                        materialized.rationale
                    ),
                    target=(
                        materialized.target
                    ),
                    admission_status=(
                        materialized
                        .admission_status
                    ),
                    admission_reason=(
                        materialized
                        .admission_reason
                    ),
                    request=(
                        materialized.request
                    ),
                    decision=decision,
                )
            )

        return RadarResearchRoutingResult(
            entries=tuple(entries)
        )


__all__ = [
    "GovernedRadarResearchRouter",
    "RadarResearchRoutingEntry",
    "RadarResearchRoutingInvariantError",
    "RadarResearchRoutingResult",
]
