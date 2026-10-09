from __future__ import annotations

from dataclasses import dataclass

from .radar_evidence_followup import (
    GovernedRadarEvidenceFollowUp,
    RadarEvidenceFollowUp,
    RadarEvidenceFollowUpNeed,
    RadarEvidenceNeedKind,
)
from .radar_review_handoff import (
    RadarReviewTarget,
)
from .radar_review_response import (
    RadarReviewResponseValue,
)
from .radar_research_reevaluation_review_response import (
    RadarReevaluationReviewResponseEntry,
    RadarReevaluationReviewResponseResult,
)


class RadarReevaluationEvidenceFollowUpInvariantError(
    ValueError
):
    pass


@dataclass(
    frozen=True,
    slots=True,
)
class RadarReevaluationEvidenceFollowUpEntry:
    source_entry: RadarReevaluationReviewResponseEntry
    need: RadarEvidenceFollowUpNeed

    followup_need_created: bool = True

    followup_candidate_created: bool = False
    research_request_created: bool = False
    provider_selection_created: bool = False
    routing_decision_created: bool = False

    network_requested: bool = False
    tool_execution_requested: bool = False
    persistence_requested: bool = False
    mission_transition_requested: bool = False
    rx_active_entered: bool = False

    verdict_asserted: bool = False
    rejection_asserted: bool = False
    human_approval_asserted: bool = False
    ay_validation_asserted: bool = False
    ex_authorization_asserted: bool = False
    governance_attestation_asserted: bool = False

    verification_status: str = (
        "UNVERIFIED_EXTERNAL"
    )

    system_truth_asserted: bool = False

    learning_asserted: bool = False
    promotion_asserted: bool = False
    activation_asserted: bool = False
    execution_asserted: bool = False

    def __post_init__(
        self,
    ) -> None:
        if not isinstance(
            self.source_entry,
            RadarReevaluationReviewResponseEntry,
        ):
            raise TypeError(
                "source_entry must be "
                "RadarReevaluationReviewResponseEntry."
            )

        if not isinstance(
            self.need,
            RadarEvidenceFollowUpNeed,
        ):
            raise TypeError(
                "need must be "
                "RadarEvidenceFollowUpNeed."
            )

        source = self.source_entry
        need = self.need

        if (
            source.request_more_evidence_recommended
            is not True
        ):
            raise (
                RadarReevaluationEvidenceFollowUpInvariantError(
                    "Only REQUEST_MORE_EVIDENCE "
                    "responses may create a "
                    "follow-up need."
                )
            )

        if (
            source.response
            is not RadarReviewResponseValue
            .REQUEST_MORE_EVIDENCE
        ):
            raise (
                RadarReevaluationEvidenceFollowUpInvariantError(
                    "Source response must be "
                    "REQUEST_MORE_EVIDENCE."
                )
            )

        if (
            need.response
            is not RadarReviewResponseValue
            .REQUEST_MORE_EVIDENCE
        ):
            raise (
                RadarReevaluationEvidenceFollowUpInvariantError(
                    "Follow-up need must preserve "
                    "REQUEST_MORE_EVIDENCE."
                )
            )

        if (
            need.need_kind
            is not RadarEvidenceNeedKind
            .ADDITIONAL_EXTERNAL_EVIDENCE
        ):
            raise (
                RadarReevaluationEvidenceFollowUpInvariantError(
                    "Follow-up need must remain "
                    "ADDITIONAL_EXTERNAL_EVIDENCE."
                )
            )

        response = source.response_entry

        if need.rank != response.rank:
            raise (
                RadarReevaluationEvidenceFollowUpInvariantError(
                    "Follow-up rank mismatch."
                )
            )

        if need.evidence_id != response.evidence_id:
            raise (
                RadarReevaluationEvidenceFollowUpInvariantError(
                    "Follow-up Evidence identity "
                    "mismatch."
                )
            )

        if need.source_ref != response.source_ref:
            raise (
                RadarReevaluationEvidenceFollowUpInvariantError(
                    "Follow-up source_ref mismatch."
                )
            )

        if need.claim != response.claim:
            raise (
                RadarReevaluationEvidenceFollowUpInvariantError(
                    "Follow-up claim mismatch."
                )
            )

        if (
            need.priority_score
            != response.priority_score
        ):
            raise (
                RadarReevaluationEvidenceFollowUpInvariantError(
                    "Follow-up priority score "
                    "mismatch."
                )
            )

        if need.factors is not response.factors:
            raise (
                RadarReevaluationEvidenceFollowUpInvariantError(
                    "Follow-up must preserve exact "
                    "factor snapshot identity."
                )
            )

        if need.rationale != response.rationale:
            raise (
                RadarReevaluationEvidenceFollowUpInvariantError(
                    "Follow-up rationale mismatch."
                )
            )

        if need.target is not response.target:
            raise (
                RadarReevaluationEvidenceFollowUpInvariantError(
                    "Follow-up target mismatch."
                )
            )

        if (
            need.verification_status
            != "UNVERIFIED_EXTERNAL"
        ):
            raise (
                RadarReevaluationEvidenceFollowUpInvariantError(
                    "Follow-up need must remain "
                    "UNVERIFIED_EXTERNAL."
                )
            )

        if need.system_truth_asserted is not False:
            raise (
                RadarReevaluationEvidenceFollowUpInvariantError(
                    "Follow-up need cannot assert "
                    "system truth."
                )
            )

        passive_need_flags = (
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

        for name in passive_need_flags:
            if getattr(
                need,
                name,
            ) is not False:
                raise (
                    RadarReevaluationEvidenceFollowUpInvariantError(
                        "ADEL0.14 need crossed "
                        f"forbidden boundary {name}."
                    )
                )

        if (
            self.verification_status
            != "UNVERIFIED_EXTERNAL"
        ):
            raise (
                RadarReevaluationEvidenceFollowUpInvariantError(
                    "ADEL0.31 must remain "
                    "UNVERIFIED_EXTERNAL."
                )
            )

        if self.followup_need_created is not True:
            raise (
                RadarReevaluationEvidenceFollowUpInvariantError(
                    "followup_need_created must "
                    "be True for a selected entry."
                )
            )

        required_false = (
            "followup_candidate_created",
            "research_request_created",
            "provider_selection_created",
            "routing_decision_created",
            "network_requested",
            "tool_execution_requested",
            "persistence_requested",
            "mission_transition_requested",
            "rx_active_entered",
            "verdict_asserted",
            "rejection_asserted",
            "human_approval_asserted",
            "ay_validation_asserted",
            "ex_authorization_asserted",
            "governance_attestation_asserted",
            "system_truth_asserted",
            "learning_asserted",
            "promotion_asserted",
            "activation_asserted",
            "execution_asserted",
        )

        for name in required_false:
            if getattr(
                self,
                name,
            ) is not False:
                raise (
                    RadarReevaluationEvidenceFollowUpInvariantError(
                        "Follow-up need boundary "
                        f"cannot assert {name}."
                    )
                )

    @property
    def evidence_id(
        self,
    ) -> str:
        return self.need.evidence_id

    @property
    def response(
        self,
    ) -> RadarReviewResponseValue:
        return self.need.response

    @property
    def target(
        self,
    ) -> RadarReviewTarget:
        return self.need.target

    @property
    def need_kind(
        self,
    ) -> RadarEvidenceNeedKind:
        return self.need.need_kind

    @property
    def response_rank(
        self,
    ) -> int:
        return self.need.rank

    @property
    def packet_rank(
        self,
    ) -> int:
        return self.source_entry.packet_rank

    @property
    def source_rank(
        self,
    ) -> int:
        return self.source_entry.source_rank

    @property
    def cycle_number(
        self,
    ) -> int:
        return self.source_entry.cycle_number

    @property
    def origin_evidence_id(
        self,
    ) -> str:
        return (
            self.source_entry
            .origin_evidence_id
        )

    @property
    def task_id(
        self,
    ) -> str:
        return self.source_entry.task_id


@dataclass(
    frozen=True,
    slots=True,
)
class RadarReevaluationEvidenceFollowUpResult:
    source: RadarReevaluationReviewResponseResult

    followup: RadarEvidenceFollowUp | None

    entries: tuple[
        RadarReevaluationEvidenceFollowUpEntry,
        ...
    ]

    followup_need_created: bool = False

    followup_candidate_created: bool = False
    research_request_created: bool = False
    provider_selection_created: bool = False
    routing_decision_created: bool = False

    network_requested: bool = False
    tool_execution_requested: bool = False
    persistence_requested: bool = False
    mission_transition_requested: bool = False
    rx_active_entered: bool = False

    verdict_asserted: bool = False
    human_approval_asserted: bool = False
    ay_validation_asserted: bool = False
    ex_authorization_asserted: bool = False
    governance_attestation_asserted: bool = False

    verification_status: str = (
        "UNVERIFIED_EXTERNAL"
    )

    system_truth_asserted: bool = False

    learning_asserted: bool = False
    promotion_asserted: bool = False
    activation_asserted: bool = False
    execution_asserted: bool = False

    def __post_init__(
        self,
    ) -> None:
        if not isinstance(
            self.source,
            RadarReevaluationReviewResponseResult,
        ):
            raise TypeError(
                "source must be "
                "RadarReevaluationReviewResponseResult."
            )

        if self.source.response is None:
            if (
                self.source.review_response_created
                is not False
            ):
                raise (
                    RadarReevaluationEvidenceFollowUpInvariantError(
                        "Missing response requires "
                        "review_response_created=False."
                    )
                )

            if self.followup is not None:
                raise (
                    RadarReevaluationEvidenceFollowUpInvariantError(
                        "No response may create "
                        "a follow-up container."
                    )
                )

            if self.entries:
                raise (
                    RadarReevaluationEvidenceFollowUpInvariantError(
                        "No response may create "
                        "follow-up needs."
                    )
                )

            if self.followup_need_created is not False:
                raise (
                    RadarReevaluationEvidenceFollowUpInvariantError(
                        "No response requires "
                        "followup_need_created=False."
                    )
                )

        else:
            if (
                self.source.review_response_created
                is not True
            ):
                raise (
                    RadarReevaluationEvidenceFollowUpInvariantError(
                        "Existing response requires "
                        "review_response_created=True."
                    )
                )

            if not isinstance(
                self.followup,
                RadarEvidenceFollowUp,
            ):
                raise TypeError(
                    "followup must be "
                    "RadarEvidenceFollowUp."
                )

            expected_source_entries = tuple(
                entry
                for entry in self.source.entries
                if (
                    entry
                    .request_more_evidence_recommended
                )
            )

            expected_ids = tuple(
                entry.evidence_id
                for entry in expected_source_entries
            )

            if (
                self.followup.evidence_ids
                != expected_ids
            ):
                raise (
                    RadarReevaluationEvidenceFollowUpInvariantError(
                        "Follow-up must contain "
                        "exact REQUEST_MORE_EVIDENCE "
                        "IDs in response order."
                    )
                )

            if self.evidence_ids != expected_ids:
                raise (
                    RadarReevaluationEvidenceFollowUpInvariantError(
                        "Wrapper entries must "
                        "contain exact selected IDs."
                    )
                )

            if (
                self.followup_need_created
                is not bool(expected_ids)
            ):
                raise (
                    RadarReevaluationEvidenceFollowUpInvariantError(
                        "followup_need_created must "
                        "match selected need count."
                    )
                )

            if (
                len(self.entries)
                != len(expected_source_entries)
            ):
                raise (
                    RadarReevaluationEvidenceFollowUpInvariantError(
                        "Follow-up wrapper entry "
                        "count mismatch."
                    )
                )

            for index, entry in enumerate(
                self.entries
            ):
                if not isinstance(
                    entry,
                    RadarReevaluationEvidenceFollowUpEntry,
                ):
                    raise TypeError(
                        "entries must contain "
                        "RadarReevaluationEvidenceFollowUpEntry."
                    )

                if (
                    entry.source_entry
                    is not expected_source_entries[index]
                ):
                    raise (
                        RadarReevaluationEvidenceFollowUpInvariantError(
                            "Exact ADEL0.30 source "
                            "identity must be "
                            "preserved."
                        )
                    )

                if (
                    entry.need
                    is not self.followup.needs[index]
                ):
                    raise (
                        RadarReevaluationEvidenceFollowUpInvariantError(
                            "Exact ADEL0.14 need "
                            "identity must be "
                            "preserved."
                        )
                    )

        if (
            self.verification_status
            != "UNVERIFIED_EXTERNAL"
        ):
            raise (
                RadarReevaluationEvidenceFollowUpInvariantError(
                    "ADEL0.31 result must remain "
                    "UNVERIFIED_EXTERNAL."
                )
            )

        required_false = (
            "followup_candidate_created",
            "research_request_created",
            "provider_selection_created",
            "routing_decision_created",
            "network_requested",
            "tool_execution_requested",
            "persistence_requested",
            "mission_transition_requested",
            "rx_active_entered",
            "verdict_asserted",
            "human_approval_asserted",
            "ay_validation_asserted",
            "ex_authorization_asserted",
            "governance_attestation_asserted",
            "system_truth_asserted",
            "learning_asserted",
            "promotion_asserted",
            "activation_asserted",
            "execution_asserted",
        )

        for name in required_false:
            if getattr(
                self,
                name,
            ) is not False:
                raise (
                    RadarReevaluationEvidenceFollowUpInvariantError(
                        "Follow-up result cannot "
                        f"assert {name}."
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
    def targets(
        self,
    ) -> tuple[
        RadarReviewTarget,
        ...
    ]:
        return tuple(
            entry.target
            for entry in self.entries
        )

    @property
    def cycle_numbers(
        self,
    ) -> tuple[int, ...]:
        return tuple(
            entry.cycle_number
            for entry in self.entries
        )


class GovernedRadarReevaluationEvidenceFollowUp:
    """
    ADEL0.31 governed re-evaluation evidence
    follow-up need boundary.

    It reuses the passive ADEL0.14
    GovernedRadarEvidenceFollowUp.build()
    primitive.

    ADEL0.14 itself selects only
    REQUEST_MORE_EVIDENCE responses.

    RETAIN_REVIEW creates no need.
    RETURN_TO_OBSERVE creates no need.

    REQUEST_MORE_EVIDENCE may create a passive
    ADDITIONAL_EXTERNAL_EVIDENCE need.

    A follow-up need is NOT a follow-up candidate,
    ResearchRequest, provider selection, routing
    decision, network request, tool execution,
    mission transition, RX_ACTIVE transition,
    persistence action, authorization or truth
    assertion.

    No ADEL0.30 response means no follow-up
    container and no need.

    FOLLOW-UP NEED != FOLLOW-UP CANDIDATE.
    FOLLOW-UP NEED != RESEARCH REQUEST.
    FOLLOW-UP NEED != PROVIDER SELECTION.
    FOLLOW-UP NEED != ROUTING.
    FOLLOW-UP NEED != NETWORK.
    FOLLOW-UP NEED != EXECUTION.
    FOLLOW-UP NEED != TRUTH.
    """

    @staticmethod
    def build(
        source: RadarReevaluationReviewResponseResult,
    ) -> RadarReevaluationEvidenceFollowUpResult:
        if not isinstance(
            source,
            RadarReevaluationReviewResponseResult,
        ):
            raise TypeError(
                "source must be "
                "RadarReevaluationReviewResponseResult."
            )

        if source.response is None:
            return (
                RadarReevaluationEvidenceFollowUpResult(
                    source=source,
                    followup=None,
                    entries=(),
                    followup_need_created=False,
                )
            )

        followup = (
            GovernedRadarEvidenceFollowUp
            .build(
                source.response
            )
        )

        selected_source_entries = tuple(
            entry
            for entry in source.entries
            if (
                entry
                .request_more_evidence_recommended
            )
        )

        entries = tuple(
            RadarReevaluationEvidenceFollowUpEntry(
                source_entry=source_entry,
                need=need,
            )
            for source_entry, need
            in zip(
                selected_source_entries,
                followup.needs,
                strict=True,
            )
        )

        return (
            RadarReevaluationEvidenceFollowUpResult(
                source=source,
                followup=followup,
                entries=entries,
                followup_need_created=bool(
                    entries
                ),
            )
        )


__all__ = [
    "GovernedRadarReevaluationEvidenceFollowUp",
    "RadarReevaluationEvidenceFollowUpEntry",
    "RadarReevaluationEvidenceFollowUpInvariantError",
    "RadarReevaluationEvidenceFollowUpResult",
]
