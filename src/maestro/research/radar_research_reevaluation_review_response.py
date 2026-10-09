from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from .radar_review_response import (
    GovernedRadarReviewResponse,
    RadarReviewResponse,
    RadarReviewResponseEntry,
    RadarReviewResponseValue,
)
from .radar_research_reevaluation_review_handoff import (
    RadarReevaluationReviewHandoffEntry,
    RadarReevaluationReviewHandoffResult,
)


class RadarReevaluationReviewResponseInvariantError(
    ValueError
):
    pass


@dataclass(
    frozen=True,
    slots=True,
)
class RadarReevaluationReviewResponseEntry:
    source_entry: RadarReevaluationReviewHandoffEntry
    response_entry: RadarReviewResponseEntry
    response_value: RadarReviewResponseValue

    review_response_created: bool = True

    verdict_asserted: bool = False
    rejection_asserted: bool = False
    human_approval_asserted: bool = False
    ay_validation_asserted: bool = False
    ex_authorization_asserted: bool = False
    governance_attestation_asserted: bool = False

    followup_created: bool = False
    new_research_request_created: bool = False

    network_requested: bool = False
    tool_execution_requested: bool = False
    persistence_requested: bool = False
    mission_transition_requested: bool = False

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
            RadarReevaluationReviewHandoffEntry,
        ):
            raise TypeError(
                "source_entry must be "
                "RadarReevaluationReviewHandoffEntry."
            )

        if not isinstance(
            self.response_entry,
            RadarReviewResponseEntry,
        ):
            raise TypeError(
                "response_entry must be "
                "RadarReviewResponseEntry."
            )

        if not isinstance(
            self.response_value,
            RadarReviewResponseValue,
        ):
            raise TypeError(
                "response_value must be "
                "RadarReviewResponseValue."
            )

        source = self.source_entry
        response = self.response_entry

        if source.review_handoff_created is not True:
            raise (
                RadarReevaluationReviewResponseInvariantError(
                    "Review response requires an "
                    "existing ADEL0.29 handoff entry."
                )
            )

        if (
            response.evidence_id
            != source.evidence_id
        ):
            raise (
                RadarReevaluationReviewResponseInvariantError(
                    "Response Evidence identity "
                    "mismatch."
                )
            )

        if response.rank != source.handoff_entry.rank:
            raise (
                RadarReevaluationReviewResponseInvariantError(
                    "Response rank must preserve "
                    "handoff rank."
                )
            )

        if response.target is not source.target:
            raise (
                RadarReevaluationReviewResponseInvariantError(
                    "Response target must preserve "
                    "handoff routing target."
                )
            )

        if response.response is not self.response_value:
            raise (
                RadarReevaluationReviewResponseInvariantError(
                    "Response value must preserve "
                    "explicit caller response."
                )
            )

        handoff = source.handoff_entry

        if response.source_ref != handoff.source_ref:
            raise (
                RadarReevaluationReviewResponseInvariantError(
                    "Response source_ref mismatch."
                )
            )

        if response.claim != handoff.claim:
            raise (
                RadarReevaluationReviewResponseInvariantError(
                    "Response claim mismatch."
                )
            )

        if (
            response.priority_score
            != handoff.priority_score
        ):
            raise (
                RadarReevaluationReviewResponseInvariantError(
                    "Response priority score "
                    "mismatch."
                )
            )

        if response.factors is not handoff.factors:
            raise (
                RadarReevaluationReviewResponseInvariantError(
                    "Response must preserve exact "
                    "factor snapshot identity."
                )
            )

        if response.rationale != handoff.rationale:
            raise (
                RadarReevaluationReviewResponseInvariantError(
                    "Response rationale mismatch."
                )
            )

        if (
            response.verification_status
            != "UNVERIFIED_EXTERNAL"
        ):
            raise (
                RadarReevaluationReviewResponseInvariantError(
                    "Response must remain "
                    "UNVERIFIED_EXTERNAL."
                )
            )

        if response.system_truth_asserted is not False:
            raise (
                RadarReevaluationReviewResponseInvariantError(
                    "Response cannot assert "
                    "system truth."
                )
            )

        if response.authorization_asserted is not False:
            raise (
                RadarReevaluationReviewResponseInvariantError(
                    "Response cannot assert "
                    "authorization."
                )
            )

        if response.promotion_asserted is not False:
            raise (
                RadarReevaluationReviewResponseInvariantError(
                    "Response cannot assert "
                    "promotion."
                )
            )

        if response.activation_asserted is not False:
            raise (
                RadarReevaluationReviewResponseInvariantError(
                    "Response cannot assert "
                    "activation."
                )
            )

        if response.execution_asserted is not False:
            raise (
                RadarReevaluationReviewResponseInvariantError(
                    "Response cannot assert "
                    "execution."
                )
            )

        if (
            self.verification_status
            != "UNVERIFIED_EXTERNAL"
        ):
            raise (
                RadarReevaluationReviewResponseInvariantError(
                    "ADEL0.30 must remain "
                    "UNVERIFIED_EXTERNAL."
                )
            )

        if self.review_response_created is not True:
            raise (
                RadarReevaluationReviewResponseInvariantError(
                    "review_response_created must "
                    "be True."
                )
            )

        required_false = (
            "verdict_asserted",
            "rejection_asserted",
            "human_approval_asserted",
            "ay_validation_asserted",
            "ex_authorization_asserted",
            "governance_attestation_asserted",
            "followup_created",
            "new_research_request_created",
            "network_requested",
            "tool_execution_requested",
            "persistence_requested",
            "mission_transition_requested",
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
                    RadarReevaluationReviewResponseInvariantError(
                        "Response boundary cannot "
                        f"assert {name}."
                    )
                )

    @property
    def evidence_id(
        self,
    ) -> str:
        return self.response_entry.evidence_id

    @property
    def target(
        self,
    ):
        return self.response_entry.target

    @property
    def response(
        self,
    ) -> RadarReviewResponseValue:
        return self.response_entry.response

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

    @property
    def retain_review_recommended(
        self,
    ) -> bool:
        return (
            self.response
            is RadarReviewResponseValue.RETAIN_REVIEW
        )

    @property
    def request_more_evidence_recommended(
        self,
    ) -> bool:
        return (
            self.response
            is RadarReviewResponseValue
            .REQUEST_MORE_EVIDENCE
        )

    @property
    def return_to_observe_recommended(
        self,
    ) -> bool:
        return (
            self.response
            is RadarReviewResponseValue
            .RETURN_TO_OBSERVE
        )


@dataclass(
    frozen=True,
    slots=True,
)
class RadarReevaluationReviewResponseResult:
    source: RadarReevaluationReviewHandoffResult

    response: RadarReviewResponse | None

    entries: tuple[
        RadarReevaluationReviewResponseEntry,
        ...
    ]

    review_response_created: bool = False

    verdict_asserted: bool = False
    rejection_asserted: bool = False
    human_approval_asserted: bool = False
    ay_validation_asserted: bool = False
    ex_authorization_asserted: bool = False
    governance_attestation_asserted: bool = False

    followup_created: bool = False
    new_research_request_created: bool = False

    network_requested: bool = False
    tool_execution_requested: bool = False
    persistence_requested: bool = False
    mission_transition_requested: bool = False

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
            RadarReevaluationReviewHandoffResult,
        ):
            raise TypeError(
                "source must be "
                "RadarReevaluationReviewHandoffResult."
            )

        if self.source.handoff is None:
            if self.source.review_handoff_created is not False:
                raise (
                    RadarReevaluationReviewResponseInvariantError(
                        "Missing handoff requires "
                        "review_handoff_created=False."
                    )
                )

            if self.response is not None:
                raise (
                    RadarReevaluationReviewResponseInvariantError(
                        "No handoff may create "
                        "a response."
                    )
                )

            if self.entries:
                raise (
                    RadarReevaluationReviewResponseInvariantError(
                        "No handoff may create "
                        "response entries."
                    )
                )

            if self.review_response_created is not False:
                raise (
                    RadarReevaluationReviewResponseInvariantError(
                        "No handoff requires "
                        "review_response_created=False."
                    )
                )

        else:
            if self.source.review_handoff_created is not True:
                raise (
                    RadarReevaluationReviewResponseInvariantError(
                        "Existing handoff requires "
                        "review_handoff_created=True."
                    )
                )

            if not isinstance(
                self.response,
                RadarReviewResponse,
            ):
                raise TypeError(
                    "response must be "
                    "RadarReviewResponse."
                )

            if self.review_response_created is not True:
                raise (
                    RadarReevaluationReviewResponseInvariantError(
                        "Existing handoff response "
                        "must be marked created."
                    )
                )

            if (
                self.response.evidence_ids
                != self.source.evidence_ids
            ):
                raise (
                    RadarReevaluationReviewResponseInvariantError(
                        "Response must cover exact "
                        "ADEL0.29 handoff IDs."
                    )
                )

            if (
                len(self.entries)
                != self.source.size
            ):
                raise (
                    RadarReevaluationReviewResponseInvariantError(
                        "Response wrapper entry "
                        "count mismatch."
                    )
                )

            for index, entry in enumerate(
                self.entries
            ):
                if not isinstance(
                    entry,
                    RadarReevaluationReviewResponseEntry,
                ):
                    raise TypeError(
                        "entries must contain "
                        "RadarReevaluationReviewResponseEntry."
                    )

                if (
                    entry.source_entry
                    is not self.source.entries[index]
                ):
                    raise (
                        RadarReevaluationReviewResponseInvariantError(
                            "Exact ADEL0.29 source "
                            "identity must be "
                            "preserved."
                        )
                    )

                if (
                    entry.response_entry
                    is not self.response.entries[index]
                ):
                    raise (
                        RadarReevaluationReviewResponseInvariantError(
                            "Exact response entry "
                            "identity must be "
                            "preserved."
                        )
                    )

        if (
            self.verification_status
            != "UNVERIFIED_EXTERNAL"
        ):
            raise (
                RadarReevaluationReviewResponseInvariantError(
                    "ADEL0.30 result must remain "
                    "UNVERIFIED_EXTERNAL."
                )
            )

        required_false = (
            "verdict_asserted",
            "rejection_asserted",
            "human_approval_asserted",
            "ay_validation_asserted",
            "ex_authorization_asserted",
            "governance_attestation_asserted",
            "followup_created",
            "new_research_request_created",
            "network_requested",
            "tool_execution_requested",
            "persistence_requested",
            "mission_transition_requested",
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
                    RadarReevaluationReviewResponseInvariantError(
                        "Response result cannot "
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
    def responses(
        self,
    ) -> tuple[
        RadarReviewResponseValue,
        ...
    ]:
        return tuple(
            entry.response
            for entry in self.entries
        )

    @property
    def targets(
        self,
    ):
        return tuple(
            entry.target
            for entry in self.entries
        )

    @property
    def retain_review_evidence_ids(
        self,
    ) -> tuple[str, ...]:
        return tuple(
            entry.evidence_id
            for entry in self.entries
            if entry.retain_review_recommended
        )

    @property
    def request_more_evidence_ids(
        self,
    ) -> tuple[str, ...]:
        return tuple(
            entry.evidence_id
            for entry in self.entries
            if entry.request_more_evidence_recommended
        )

    @property
    def return_to_observe_evidence_ids(
        self,
    ) -> tuple[str, ...]:
        return tuple(
            entry.evidence_id
            for entry in self.entries
            if entry.return_to_observe_recommended
        )


class GovernedRadarReevaluationReviewResponse:
    """
    ADEL0.30 governed re-evaluation review response.

    It reuses the passive ADEL0.13
    GovernedRadarReviewResponse.build() primitive.

    Every handed-off Evidence requires exactly one
    explicit RadarReviewResponseValue.

    Missing, extra or invalid response values fail
    closed.

    RETAIN_REVIEW, REQUEST_MORE_EVIDENCE and
    RETURN_TO_OBSERVE remain passive research
    review recommendations only.

    RETAIN_REVIEW != APPROVAL.

    REQUEST_MORE_EVIDENCE != FOLLOW-UP.
    REQUEST_MORE_EVIDENCE != RESEARCH REQUEST.

    RETURN_TO_OBSERVE != REJECTION.

    A response does not constitute a Verdict,
    human approval, AY validation, EX
    authorization, governance attestation,
    promotion, activation, execution permission,
    mission transition or truth assertion.

    No handoff means no response and requires an
    empty response mapping.

    This boundary performs no follow-up creation,
    ResearchRequest creation, network access,
    tool execution, persistence, mission
    transition, learning, promotion, activation,
    execution authority or skill creation.
    """

    @staticmethod
    def respond(
        source: RadarReevaluationReviewHandoffResult,
        *,
        responses: Mapping[
            str,
            RadarReviewResponseValue,
        ],
    ) -> RadarReevaluationReviewResponseResult:
        if not isinstance(
            source,
            RadarReevaluationReviewHandoffResult,
        ):
            raise TypeError(
                "source must be "
                "RadarReevaluationReviewHandoffResult."
            )

        if not isinstance(
            responses,
            Mapping,
        ):
            raise TypeError(
                "responses must be a mapping."
            )

        if source.handoff is None:
            if responses:
                raise (
                    RadarReevaluationReviewResponseInvariantError(
                        "No ReviewHandoff exists; "
                        "responses must be empty."
                    )
                )

            return (
                RadarReevaluationReviewResponseResult(
                    source=source,
                    response=None,
                    entries=(),
                    review_response_created=False,
                )
            )

        response = (
            GovernedRadarReviewResponse
            .build(
                source.handoff,
                responses=responses,
            )
        )

        entries = tuple(
            RadarReevaluationReviewResponseEntry(
                source_entry=source_entry,
                response_entry=response_entry,
                response_value=response_entry.response,
            )
            for source_entry, response_entry
            in zip(
                source.entries,
                response.entries,
                strict=True,
            )
        )

        return (
            RadarReevaluationReviewResponseResult(
                source=source,
                response=response,
                entries=entries,
                review_response_created=True,
            )
        )


__all__ = [
    "GovernedRadarReevaluationReviewResponse",
    "RadarReevaluationReviewResponseEntry",
    "RadarReevaluationReviewResponseInvariantError",
    "RadarReevaluationReviewResponseResult",
]
