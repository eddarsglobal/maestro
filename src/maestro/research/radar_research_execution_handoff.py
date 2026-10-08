from __future__ import annotations

from dataclasses import dataclass

from .radar_research_draft_admission import (
    RadarResearchDraftAdmissionStatus,
)
from .radar_research_routing import (
    RadarResearchRoutingResult,
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


class RadarResearchExecutionHandoffInvariantError(
    ValueError
):
    pass


@dataclass(
    frozen=True,
    slots=True,
)
class RadarResearchExecutionHandoffEntry:
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

    tool_validated: bool = True
    execution_handoff_created: bool = True

    tool_invoked: bool = False
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
                RadarResearchExecutionHandoffInvariantError(
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
                    RadarResearchExecutionHandoffInvariantError(
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
                RadarResearchExecutionHandoffInvariantError(
                    "Only ADMISSIBLE routed "
                    "requests may enter handoff."
                )
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
            raise (
                RadarResearchExecutionHandoffInvariantError(
                    "Validated handoff requires "
                    "provider_id."
                )
            )

        if (
            not isinstance(
                self.decision.tool_name,
                str,
            )
            or not self.decision.tool_name.strip()
        ):
            raise (
                RadarResearchExecutionHandoffInvariantError(
                    "Validated handoff requires "
                    "tool_name."
                )
            )

        if (
            self.decision.provider_id
            not in self.decision.candidates
        ):
            raise (
                RadarResearchExecutionHandoffInvariantError(
                    "Selected provider must "
                    "remain a routing candidate."
                )
            )

        if (
            self.verification_status
            != "UNVERIFIED_EXTERNAL"
        ):
            raise (
                RadarResearchExecutionHandoffInvariantError(
                    "Tool validation must remain "
                    "UNVERIFIED_EXTERNAL."
                )
            )

        if self.system_truth_asserted is not False:
            raise (
                RadarResearchExecutionHandoffInvariantError(
                    "Tool validation cannot "
                    "assert truth."
                )
            )

        required_true = (
            "task_id_bound",
            "research_request_created",
            "provider_selected",
            "routing_decision_created",
            "tool_validated",
            "execution_handoff_created",
        )

        for name in required_true:
            if getattr(
                self,
                name,
            ) is not True:
                raise (
                    RadarResearchExecutionHandoffInvariantError(
                        "Validated handoff requires "
                        f"{name}=True."
                    )
                )

        passive_flags = (
            "tool_invoked",
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
                    RadarResearchExecutionHandoffInvariantError(
                        "Validated handoff cannot "
                        f"assert {name}."
                    )
                )

    @property
    def task_id(
        self,
    ) -> str:
        return self.request.task_id

    @property
    def provider_id(
        self,
    ) -> str:
        return self.decision.provider_id

    @property
    def tool_name(
        self,
    ) -> str:
        return self.decision.tool_name


@dataclass(
    frozen=True,
    slots=True,
)
class RadarResearchExecutionHandoff:
    entries: tuple[
        RadarResearchExecutionHandoffEntry,
        ...
    ]

    def __post_init__(
        self,
    ) -> None:
        for entry in self.entries:
            if not isinstance(
                entry,
                RadarResearchExecutionHandoffEntry,
            ):
                raise TypeError(
                    "entries must contain "
                    "RadarResearchExecutionHandoffEntry."
                )

        ids = tuple(
            entry.evidence_id
            for entry in self.entries
        )

        if len(ids) != len(set(ids)):
            raise (
                RadarResearchExecutionHandoffInvariantError(
                    "Execution handoff requires "
                    "unique evidence IDs."
                )
            )

        ranks = tuple(
            entry.rank
            for entry in self.entries
        )

        if ranks != tuple(sorted(ranks)):
            raise (
                RadarResearchExecutionHandoffInvariantError(
                    "Execution handoff must "
                    "preserve routing order."
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
            entry.task_id
            for entry in self.entries
        )

    @property
    def provider_ids(
        self,
    ) -> tuple[str, ...]:
        return tuple(
            entry.provider_id
            for entry in self.entries
        )

    @property
    def tool_names(
        self,
    ) -> tuple[str, ...]:
        return tuple(
            entry.tool_name
            for entry in self.entries
        )


class GovernedRadarResearchToolValidator:
    """
    ADEL0.21 governed tool-validation boundary.

    It reuses the exact validation semantics already
    enforced by GovernedResearchRuntime.

    Validation reads ToolRegistry metadata only.

    TOOL VALIDATED != TOOL INVOKED.
    TOOL VALIDATED != NETWORK ACCESS.
    TOOL VALIDATED != EXECUTION.
    TOOL VALIDATED != MISSION TRANSITION.
    TOOL VALIDATED != AUTHORIZATION.
    TOOL VALIDATED != ACTIVATION.
    TOOL VALIDATED != TRUTH.

    No handler, ActionFirewall authorization,
    ToolRegistry invocation, network transport,
    persistence, mission transition, learning,
    promotion, activation, execution, skill creation,
    or truth escalation occurs here.
    """

    @staticmethod
    def validate(
        routing: RadarResearchRoutingResult,
        *,
        runtime: GovernedResearchRuntime,
    ) -> RadarResearchExecutionHandoff:
        if not isinstance(
            routing,
            RadarResearchRoutingResult,
        ):
            raise TypeError(
                "routing must be "
                "RadarResearchRoutingResult."
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

        for routed in routing.entries:
            runtime._validate_tool(
                routed.request,
                routed.decision,
            )

            entries.append(
                RadarResearchExecutionHandoffEntry(
                    rank=routed.rank,
                    evidence_id=(
                        routed.evidence_id
                    ),
                    source_ref=(
                        routed.source_ref
                    ),
                    claim=routed.claim,
                    priority_score=(
                        routed.priority_score
                    ),
                    factors=routed.factors,
                    rationale=(
                        routed.rationale
                    ),
                    target=routed.target,
                    admission_status=(
                        routed.admission_status
                    ),
                    admission_reason=(
                        routed.admission_reason
                    ),
                    request=routed.request,
                    decision=routed.decision,
                )
            )

        return RadarResearchExecutionHandoff(
            entries=tuple(entries)
        )


__all__ = [
    "GovernedRadarResearchToolValidator",
    "RadarResearchExecutionHandoff",
    "RadarResearchExecutionHandoffEntry",
    "RadarResearchExecutionHandoffInvariantError",
]
