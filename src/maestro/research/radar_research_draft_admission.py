from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Mapping

from .provider_contracts import (
    ResearchCapability,
)
from .radar_research_request_draft import (
    RadarResearchRequestDraftEntry,
    RadarResearchRequestDraftSet,
)
from .radar_review_handoff import (
    RadarReviewTarget,
)
from .radar_review_packet import (
    RadarFactorSnapshot,
)


class RadarResearchDraftAdmissionInvariantError(
    ValueError
):
    pass


class RadarResearchDraftAdmissionStatus(StrEnum):
    ADMISSIBLE = "ADMISSIBLE"
    REJECTED = "REJECTED"


@dataclass(
    frozen=True,
    slots=True,
)
class RadarResearchDraftAdmissionPolicy:
    max_query_chars: int = 4096
    require_preferred_local: bool = True
    allow_forbidden_provider_ids: bool = False

    def __post_init__(
        self,
    ) -> None:
        if (
            isinstance(
                self.max_query_chars,
                bool,
            )
            or not isinstance(
                self.max_query_chars,
                int,
            )
        ):
            raise TypeError(
                "max_query_chars must be integer."
            )

        if self.max_query_chars < 1:
            raise RadarResearchDraftAdmissionInvariantError(
                "max_query_chars must be positive."
            )

        if not isinstance(
            self.require_preferred_local,
            bool,
        ):
            raise TypeError(
                "require_preferred_local must "
                "be boolean."
            )

        if not isinstance(
            self.allow_forbidden_provider_ids,
            bool,
        ):
            raise TypeError(
                "allow_forbidden_provider_ids "
                "must be boolean."
            )


@dataclass(
    frozen=True,
    slots=True,
)
class RadarResearchDraftAdmissionEntry:
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

    status: RadarResearchDraftAdmissionStatus
    reason: str

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
        if not isinstance(
            self.status,
            RadarResearchDraftAdmissionStatus,
        ):
            raise TypeError(
                "status must be "
                "RadarResearchDraftAdmissionStatus."
            )

        if (
            not isinstance(
                self.reason,
                str,
            )
            or not self.reason.strip()
        ):
            raise RadarResearchDraftAdmissionInvariantError(
                "reason must be non-empty."
            )

        if (
            self.verification_status
            != "UNVERIFIED_EXTERNAL"
        ):
            raise RadarResearchDraftAdmissionInvariantError(
                "Admission result must remain "
                "UNVERIFIED_EXTERNAL."
            )

        if self.system_truth_asserted is not False:
            raise RadarResearchDraftAdmissionInvariantError(
                "Admission cannot assert truth."
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
                raise RadarResearchDraftAdmissionInvariantError(
                    "Admission cannot assert "
                    f"{name}."
                )


@dataclass(
    frozen=True,
    slots=True,
)
class RadarResearchDraftAdmissionResult:
    policy: RadarResearchDraftAdmissionPolicy

    entries: tuple[
        RadarResearchDraftAdmissionEntry,
        ...
    ]

    def __post_init__(
        self,
    ) -> None:
        if not isinstance(
            self.policy,
            RadarResearchDraftAdmissionPolicy,
        ):
            raise TypeError(
                "policy must be "
                "RadarResearchDraftAdmissionPolicy."
            )

        for entry in self.entries:
            if not isinstance(
                entry,
                RadarResearchDraftAdmissionEntry,
            ):
                raise TypeError(
                    "entries must contain "
                    "RadarResearchDraftAdmissionEntry."
                )

        ids = tuple(
            entry.evidence_id
            for entry in self.entries
        )

        if len(ids) != len(set(ids)):
            raise RadarResearchDraftAdmissionInvariantError(
                "Admission result requires "
                "unique evidence IDs."
            )

        ranks = tuple(
            entry.rank
            for entry in self.entries
        )

        if ranks != tuple(sorted(ranks)):
            raise RadarResearchDraftAdmissionInvariantError(
                "Admission result must preserve "
                "ascending draft rank order."
            )

    @property
    def size(
        self,
    ) -> int:
        return len(
            self.entries
        )

    @property
    def admissible_ids(
        self,
    ) -> tuple[str, ...]:
        return tuple(
            entry.evidence_id
            for entry in self.entries
            if (
                entry.status
                is RadarResearchDraftAdmissionStatus
                .ADMISSIBLE
            )
        )

    @property
    def rejected_ids(
        self,
    ) -> tuple[str, ...]:
        return tuple(
            entry.evidence_id
            for entry in self.entries
            if (
                entry.status
                is RadarResearchDraftAdmissionStatus
                .REJECTED
            )
        )


class GovernedRadarResearchDraftAdmissionGate:
    """
    Pure ADEL0.17 admission layer.

    Admission is structural eligibility only.

    ADMISSIBLE does NOT mean approved, authorized,
    executable, verified, true, promoted, activated,
    or bound to a mission/task identity.

    This gate creates no ResearchRequest and performs
    no provider selection, runtime routing, execution,
    ToolRegistry invocation, network access,
    persistence, mission transition, learning,
    promotion, activation, skill creation, or
    authority escalation.
    """

    @staticmethod
    def _decision(
        draft: RadarResearchRequestDraftEntry,
        policy: RadarResearchDraftAdmissionPolicy,
    ) -> tuple[
        RadarResearchDraftAdmissionStatus,
        str,
    ]:
        query = draft.arguments["query"]

        if len(query) > policy.max_query_chars:
            return (
                RadarResearchDraftAdmissionStatus
                .REJECTED,
                "QUERY_TOO_LONG",
            )

        if (
            policy.require_preferred_local
            and not draft.preferred_local
        ):
            return (
                RadarResearchDraftAdmissionStatus
                .REJECTED,
                "PREFERRED_LOCAL_REQUIRED",
            )

        if (
            not policy.allow_forbidden_provider_ids
            and draft.forbidden_provider_ids
        ):
            return (
                RadarResearchDraftAdmissionStatus
                .REJECTED,
                "FORBIDDEN_PROVIDER_IDS_PRESENT",
            )

        return (
            RadarResearchDraftAdmissionStatus
            .ADMISSIBLE,
            "STRUCTURALLY_ADMISSIBLE",
        )

    @classmethod
    def evaluate(
        cls,
        drafts: RadarResearchRequestDraftSet,
        *,
        policy: (
            RadarResearchDraftAdmissionPolicy
            | None
        ) = None,
    ) -> RadarResearchDraftAdmissionResult:
        if not isinstance(
            drafts,
            RadarResearchRequestDraftSet,
        ):
            raise TypeError(
                "drafts must be "
                "RadarResearchRequestDraftSet."
            )

        selected_policy = (
            RadarResearchDraftAdmissionPolicy()
            if policy is None
            else policy
        )

        if not isinstance(
            selected_policy,
            RadarResearchDraftAdmissionPolicy,
        ):
            raise TypeError(
                "policy must be "
                "RadarResearchDraftAdmissionPolicy."
            )

        entries = []

        for draft in drafts.entries:
            status, reason = cls._decision(
                draft,
                selected_policy,
            )

            entries.append(
                RadarResearchDraftAdmissionEntry(
                    rank=draft.rank,
                    evidence_id=(
                        draft.evidence_id
                    ),
                    source_ref=(
                        draft.source_ref
                    ),
                    claim=draft.claim,
                    priority_score=(
                        draft.priority_score
                    ),
                    factors=draft.factors,
                    rationale=(
                        draft.rationale
                    ),
                    target=draft.target,
                    capability=(
                        draft.capability
                    ),
                    arguments=(
                        draft.arguments
                    ),
                    preferred_local=(
                        draft.preferred_local
                    ),
                    forbidden_provider_ids=(
                        draft.forbidden_provider_ids
                    ),
                    status=status,
                    reason=reason,
                )
            )

        return RadarResearchDraftAdmissionResult(
            policy=selected_policy,
            entries=tuple(entries),
        )


__all__ = [
    "GovernedRadarResearchDraftAdmissionGate",
    "RadarResearchDraftAdmissionEntry",
    "RadarResearchDraftAdmissionInvariantError",
    "RadarResearchDraftAdmissionPolicy",
    "RadarResearchDraftAdmissionResult",
    "RadarResearchDraftAdmissionStatus",
]
