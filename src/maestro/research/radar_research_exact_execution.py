from __future__ import annotations

from dataclasses import dataclass

from .radar_research_draft_admission import (
    RadarResearchDraftAdmissionStatus,
)
from .radar_research_execution_handoff import (
    RadarResearchExecutionHandoff,
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
    ResearchAttemptStatus,
    ResearchExecutionResult,
    ResearchRequest,
    ResearchRoutingDecision,
)


class RadarResearchExactExecutionInvariantError(
    ValueError
):
    pass


@dataclass(
    frozen=True,
    slots=True,
)
class RadarResearchExactExecutionEntry:
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
    result: ResearchExecutionResult

    verification_status: str = (
        "UNVERIFIED_EXTERNAL"
    )

    network_access_status: str = "UNKNOWN"

    system_truth_asserted: bool = False

    task_id_bound: bool = True
    research_request_created: bool = True
    provider_selected: bool = True
    routing_decision_created: bool = True
    tool_validated: bool = True
    execution_handoff_created: bool = True

    tool_execution_requested: bool = True
    tool_invoked: bool = True
    action_firewall_crossed: bool = True
    execution_completed: bool = True
    execution_result_created: bool = True
    execution_asserted: bool = True

    evidence_created: bool = False
    evidence_reintegrated: bool = False

    mission_transition_requested: bool = False
    persistence_requested: bool = False
    learning_asserted: bool = False
    authorization_asserted: bool = False
    promotion_asserted: bool = False
    activation_asserted: bool = False

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
                RadarResearchExactExecutionInvariantError(
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
                    RadarResearchExactExecutionInvariantError(
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
                RadarResearchExactExecutionInvariantError(
                    "Exact execution requires "
                    "ADMISSIBLE research."
                )
            )

        if not isinstance(
            self.request,
            ResearchRequest,
        ):
            raise TypeError(
                "request must be ResearchRequest."
            )

        if not isinstance(
            self.decision,
            ResearchRoutingDecision,
        ):
            raise TypeError(
                "decision must be "
                "ResearchRoutingDecision."
            )

        if not isinstance(
            self.result,
            ResearchExecutionResult,
        ):
            raise TypeError(
                "result must be "
                "ResearchExecutionResult."
            )

        if (
            self.result.task_id
            != self.request.task_id
        ):
            raise (
                RadarResearchExactExecutionInvariantError(
                    "Execution result task_id "
                    "must match the handoff request."
                )
            )

        if (
            self.result.capability
            is not self.request.capability
        ):
            raise (
                RadarResearchExactExecutionInvariantError(
                    "Execution result capability "
                    "must match the request."
                )
            )

        if (
            self.result.provider_id
            != self.decision.provider_id
        ):
            raise (
                RadarResearchExactExecutionInvariantError(
                    "Exact execution cannot change "
                    "the validated provider."
                )
            )

        if (
            self.result.tool_name
            != self.decision.tool_name
        ):
            raise (
                RadarResearchExactExecutionInvariantError(
                    "Exact execution cannot change "
                    "the validated tool."
                )
            )

        if len(
            self.result.attempts
        ) != 1:
            raise (
                RadarResearchExactExecutionInvariantError(
                    "Exact execution must contain "
                    "exactly one attempt."
                )
            )

        attempt = self.result.attempts[0]

        if attempt.attempt_number != 1:
            raise (
                RadarResearchExactExecutionInvariantError(
                    "Exact execution attempt must "
                    "be attempt number 1."
                )
            )

        if (
            attempt.provider_id
            != self.decision.provider_id
            or attempt.tool_name
            != self.decision.tool_name
        ):
            raise (
                RadarResearchExactExecutionInvariantError(
                    "Exact execution attempt must "
                    "preserve provider/tool."
                )
            )

        if (
            attempt.status
            is not ResearchAttemptStatus.SUCCEEDED
        ):
            raise (
                RadarResearchExactExecutionInvariantError(
                    "Successful exact execution "
                    "requires SUCCEEDED attempt."
                )
            )

        if (
            self.verification_status
            != "UNVERIFIED_EXTERNAL"
        ):
            raise (
                RadarResearchExactExecutionInvariantError(
                    "Executed research remains "
                    "UNVERIFIED_EXTERNAL."
                )
            )

        if self.network_access_status != "UNKNOWN":
            raise (
                RadarResearchExactExecutionInvariantError(
                    "Network access must remain "
                    "UNKNOWN without telemetry."
                )
            )

        if self.system_truth_asserted is not False:
            raise (
                RadarResearchExactExecutionInvariantError(
                    "Execution cannot assert truth."
                )
            )

        required_true = (
            "task_id_bound",
            "research_request_created",
            "provider_selected",
            "routing_decision_created",
            "tool_validated",
            "execution_handoff_created",
            "tool_execution_requested",
            "tool_invoked",
            "action_firewall_crossed",
            "execution_completed",
            "execution_result_created",
            "execution_asserted",
        )

        for name in required_true:
            if getattr(
                self,
                name,
            ) is not True:
                raise (
                    RadarResearchExactExecutionInvariantError(
                        "Exact execution requires "
                        f"{name}=True."
                    )
                )

        required_false = (
            "evidence_created",
            "evidence_reintegrated",
            "mission_transition_requested",
            "persistence_requested",
            "learning_asserted",
            "authorization_asserted",
            "promotion_asserted",
            "activation_asserted",
        )

        for name in required_false:
            if getattr(
                self,
                name,
            ) is not False:
                raise (
                    RadarResearchExactExecutionInvariantError(
                        "Exact execution cannot "
                        f"assert {name}."
                    )
                )

    @property
    def task_id(
        self,
    ) -> str:
        return self.result.task_id

    @property
    def provider_id(
        self,
    ) -> str:
        return self.result.provider_id

    @property
    def tool_name(
        self,
    ) -> str:
        return self.result.tool_name


@dataclass(
    frozen=True,
    slots=True,
)
class RadarResearchExactExecutionResult:
    entries: tuple[
        RadarResearchExactExecutionEntry,
        ...
    ]

    def __post_init__(
        self,
    ) -> None:
        for entry in self.entries:
            if not isinstance(
                entry,
                RadarResearchExactExecutionEntry,
            ):
                raise TypeError(
                    "entries must contain "
                    "RadarResearchExactExecutionEntry."
                )

        ids = tuple(
            entry.evidence_id
            for entry in self.entries
        )

        if len(ids) != len(set(ids)):
            raise (
                RadarResearchExactExecutionInvariantError(
                    "Exact execution requires "
                    "unique evidence IDs."
                )
            )

        ranks = tuple(
            entry.rank
            for entry in self.entries
        )

        if ranks != tuple(sorted(ranks)):
            raise (
                RadarResearchExactExecutionInvariantError(
                    "Exact execution must preserve "
                    "handoff rank order."
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


class GovernedRadarResearchExactExecutor:
    """
    ADEL0.22A exact governed execution boundary.

    Consumes an already-routed and already-validated
    ADEL0.21 handoff.

    The exact provider and tool are preserved.

    This layer does not call route() and does not
    perform provider fallback.

    EXECUTED != VERIFIED.
    EXECUTED != EVIDENCE.
    EXECUTED != REINTEGRATED.
    EXECUTED != TRUTH.
    EXECUTED != LEARNING.
    EXECUTED != PROMOTION.
    EXECUTED != ACTIVATION.

    Network access is UNKNOWN unless an independent
    telemetry boundary proves otherwise.
    """

    @staticmethod
    def execute(
        handoff: RadarResearchExecutionHandoff,
        *,
        runtime: GovernedResearchRuntime,
    ) -> RadarResearchExactExecutionResult:
        if not isinstance(
            handoff,
            RadarResearchExecutionHandoff,
        ):
            raise TypeError(
                "handoff must be "
                "RadarResearchExecutionHandoff."
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

        for handed in handoff.entries:
            result = runtime.execute_exact(
                handed.request,
                handed.decision,
            )

            entries.append(
                RadarResearchExactExecutionEntry(
                    rank=handed.rank,
                    evidence_id=(
                        handed.evidence_id
                    ),
                    source_ref=(
                        handed.source_ref
                    ),
                    claim=handed.claim,
                    priority_score=(
                        handed.priority_score
                    ),
                    factors=handed.factors,
                    rationale=(
                        handed.rationale
                    ),
                    target=handed.target,
                    admission_status=(
                        handed.admission_status
                    ),
                    admission_reason=(
                        handed.admission_reason
                    ),
                    request=handed.request,
                    decision=handed.decision,
                    result=result,
                )
            )

        return RadarResearchExactExecutionResult(
            entries=tuple(entries)
        )


__all__ = [
    "GovernedRadarResearchExactExecutor",
    "RadarResearchExactExecutionEntry",
    "RadarResearchExactExecutionInvariantError",
    "RadarResearchExactExecutionResult",
]
