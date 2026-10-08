from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from .identity import (
    require_durable_research_task_id,
)
from .provider_contracts import (
    ResearchCapability,
)
from .radar_research_draft_admission import (
    RadarResearchDraftAdmissionResult,
    RadarResearchDraftAdmissionStatus,
)
from .radar_review_handoff import (
    RadarReviewTarget,
)
from .radar_review_packet import (
    RadarFactorSnapshot,
)


class RadarResearchTaskBindingInvariantError(
    ValueError
):
    pass


@dataclass(
    frozen=True,
    slots=True,
)
class RadarResearchTaskBindingEntry:
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
    forbidden_provider_ids: tuple[str, ...]

    admission_status: (
        RadarResearchDraftAdmissionStatus
    )
    admission_reason: str

    task_id: str

    verification_status: str = (
        "UNVERIFIED_EXTERNAL"
    )

    system_truth_asserted: bool = False

    task_id_bound: bool = True
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
            raise RadarResearchTaskBindingInvariantError(
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
                raise RadarResearchTaskBindingInvariantError(
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
            raise RadarResearchTaskBindingInvariantError(
                "Task binding supports only "
                "SEARCH drafts."
            )

        if not isinstance(
            self.arguments,
            Mapping,
        ):
            raise TypeError(
                "arguments must be a mapping."
            )

        if set(self.arguments) != {"query"}:
            raise RadarResearchTaskBindingInvariantError(
                "Bound SEARCH arguments must "
                "contain exactly 'query'."
            )

        query = self.arguments["query"]

        if (
            not isinstance(
                query,
                str,
            )
            or not query.strip()
        ):
            raise RadarResearchTaskBindingInvariantError(
                "Bound SEARCH query must "
                "be non-empty."
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

        if (
            self.admission_status
            is not RadarResearchDraftAdmissionStatus
            .ADMISSIBLE
        ):
            raise RadarResearchTaskBindingInvariantError(
                "Only ADMISSIBLE drafts may "
                "receive task binding."
            )

        validated_task_id = (
            require_durable_research_task_id(
                self.task_id
            )
        )

        object.__setattr__(
            self,
            "task_id",
            validated_task_id,
        )

        if (
            self.verification_status
            != "UNVERIFIED_EXTERNAL"
        ):
            raise RadarResearchTaskBindingInvariantError(
                "Task binding must remain "
                "UNVERIFIED_EXTERNAL."
            )

        if self.system_truth_asserted is not False:
            raise RadarResearchTaskBindingInvariantError(
                "Task binding cannot assert truth."
            )

        if self.task_id_bound is not True:
            raise RadarResearchTaskBindingInvariantError(
                "Task binding must assert only "
                "that task identity is bound."
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
                raise RadarResearchTaskBindingInvariantError(
                    "Task binding cannot assert "
                    f"{name}."
                )


@dataclass(
    frozen=True,
    slots=True,
)
class RadarResearchTaskBinding:
    entries: tuple[
        RadarResearchTaskBindingEntry,
        ...
    ]

    def __post_init__(
        self,
    ) -> None:
        for entry in self.entries:
            if not isinstance(
                entry,
                RadarResearchTaskBindingEntry,
            ):
                raise TypeError(
                    "entries must contain "
                    "RadarResearchTaskBindingEntry."
                )

        ids = tuple(
            entry.evidence_id
            for entry in self.entries
        )

        if len(ids) != len(set(ids)):
            raise RadarResearchTaskBindingInvariantError(
                "Task binding requires unique "
                "evidence IDs."
            )

        ranks = tuple(
            entry.rank
            for entry in self.entries
        )

        if ranks != tuple(sorted(ranks)):
            raise RadarResearchTaskBindingInvariantError(
                "Task binding must preserve "
                "ascending admission rank order."
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


class GovernedRadarResearchTaskBinder:
    """
    Pure ADEL0.18 task-identity binding layer.

    Only ADMISSIBLE ADEL0.17 entries may receive
    canonical MAESTRO task identities.

    Binding a task identity does NOT create a
    ResearchRequest.

    TASK BINDING != REQUEST MATERIALIZATION.

    This layer performs no provider selection,
    routing, ResearchRoutingDecision creation,
    runtime execution, ToolRegistry invocation,
    network access, mission state transition,
    RX activation, persistence, verification,
    learning, promotion, authorization,
    activation, execution, skill creation,
    or authority escalation.
    """

    @staticmethod
    def bind(
        admission: RadarResearchDraftAdmissionResult,
        *,
        task_ids: Mapping[str, str],
    ) -> RadarResearchTaskBinding:
        if not isinstance(
            admission,
            RadarResearchDraftAdmissionResult,
        ):
            raise TypeError(
                "admission must be "
                "RadarResearchDraftAdmissionResult."
            )

        if not isinstance(
            task_ids,
            Mapping,
        ):
            raise TypeError(
                "task_ids must be a mapping."
            )

        admissible_entries = tuple(
            entry
            for entry in admission.entries
            if (
                entry.status
                is RadarResearchDraftAdmissionStatus
                .ADMISSIBLE
            )
        )

        admissible_ids = {
            entry.evidence_id
            for entry in admissible_entries
        }

        supplied_ids = set(
            task_ids
        )

        if supplied_ids != admissible_ids:
            raise RadarResearchTaskBindingInvariantError(
                "Task identity mapping must "
                "match ADMISSIBLE evidence IDs "
                "exactly."
            )

        entries = tuple(
            RadarResearchTaskBindingEntry(
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
                capability=(
                    entry.capability
                ),
                arguments=(
                    entry.arguments
                ),
                preferred_local=(
                    entry.preferred_local
                ),
                forbidden_provider_ids=(
                    entry.forbidden_provider_ids
                ),
                admission_status=(
                    entry.status
                ),
                admission_reason=(
                    entry.reason
                ),
                task_id=(
                    task_ids[
                        entry.evidence_id
                    ]
                ),
            )
            for entry
            in admissible_entries
        )

        return RadarResearchTaskBinding(
            entries=entries
        )


__all__ = [
    "GovernedRadarResearchTaskBinder",
    "RadarResearchTaskBinding",
    "RadarResearchTaskBindingEntry",
    "RadarResearchTaskBindingInvariantError",
]
