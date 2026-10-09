from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from .radar_review_handoff import (
    GovernedRadarReviewHandoff,
    RadarReviewAssignment,
    RadarReviewHandoff,
    RadarReviewHandoffEntry,
    RadarReviewTarget,
)
from .radar_research_reevaluation_review_packet import (
    RadarReevaluationReviewPacketEntry,
    RadarReevaluationReviewPacketResult,
)


class RadarReevaluationReviewHandoffInvariantError(
    ValueError
):
    pass


@dataclass(
    frozen=True,
    slots=True,
)
class RadarReevaluationReviewHandoffEntry:
    source_entry: RadarReevaluationReviewPacketEntry
    handoff_entry: RadarReviewHandoffEntry
    assignment: RadarReviewAssignment

    review_handoff_created: bool = True

    review_response_created: bool = False
    human_approval_asserted: bool = False
    ay_validation_asserted: bool = False
    ex_authorization_asserted: bool = False

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
            RadarReevaluationReviewPacketEntry,
        ):
            raise TypeError(
                "source_entry must be "
                "RadarReevaluationReviewPacketEntry."
            )

        if not isinstance(
            self.handoff_entry,
            RadarReviewHandoffEntry,
        ):
            raise TypeError(
                "handoff_entry must be "
                "RadarReviewHandoffEntry."
            )

        if not isinstance(
            self.assignment,
            RadarReviewAssignment,
        ):
            raise TypeError(
                "assignment must be "
                "RadarReviewAssignment."
            )

        source = self.source_entry
        handoff = self.handoff_entry
        assignment = self.assignment

        if source.review_packet_created is not True:
            raise (
                RadarReevaluationReviewHandoffInvariantError(
                    "Review handoff requires an "
                    "existing ADEL0.28 packet entry."
                )
            )

        if (
            handoff.evidence_id
            != source.evidence_id
        ):
            raise (
                RadarReevaluationReviewHandoffInvariantError(
                    "Handoff Evidence identity "
                    "mismatch."
                )
            )

        if (
            assignment.evidence_id
            != source.evidence_id
        ):
            raise (
                RadarReevaluationReviewHandoffInvariantError(
                    "Assignment Evidence identity "
                    "mismatch."
                )
            )

        if handoff.target is not assignment.target:
            raise (
                RadarReevaluationReviewHandoffInvariantError(
                    "Handoff target must preserve "
                    "explicit assignment."
                )
            )

        if (
            handoff.rank
            != source.packet_rank
        ):
            raise (
                RadarReevaluationReviewHandoffInvariantError(
                    "Handoff rank must preserve "
                    "packet-local rank."
                )
            )

        packet = source.packet_entry

        if handoff.source_ref != packet.source_ref:
            raise (
                RadarReevaluationReviewHandoffInvariantError(
                    "Handoff source_ref mismatch."
                )
            )

        if handoff.claim != packet.claim:
            raise (
                RadarReevaluationReviewHandoffInvariantError(
                    "Handoff claim mismatch."
                )
            )

        if (
            handoff.priority_score
            != packet.priority_score
        ):
            raise (
                RadarReevaluationReviewHandoffInvariantError(
                    "Handoff priority score "
                    "mismatch."
                )
            )

        if handoff.factors is not packet.factors:
            raise (
                RadarReevaluationReviewHandoffInvariantError(
                    "Handoff must preserve exact "
                    "factor snapshot identity."
                )
            )

        if handoff.rationale != packet.rationale:
            raise (
                RadarReevaluationReviewHandoffInvariantError(
                    "Handoff rationale mismatch."
                )
            )

        if (
            handoff.verification_status
            != "UNVERIFIED_EXTERNAL"
        ):
            raise (
                RadarReevaluationReviewHandoffInvariantError(
                    "Handoff must remain "
                    "UNVERIFIED_EXTERNAL."
                )
            )

        if handoff.system_truth_asserted is not False:
            raise (
                RadarReevaluationReviewHandoffInvariantError(
                    "Handoff cannot assert "
                    "system truth."
                )
            )

        if handoff.authorization_asserted is not False:
            raise (
                RadarReevaluationReviewHandoffInvariantError(
                    "Handoff cannot assert "
                    "authorization."
                )
            )

        if handoff.activation_asserted is not False:
            raise (
                RadarReevaluationReviewHandoffInvariantError(
                    "Handoff cannot assert "
                    "activation."
                )
            )

        if handoff.execution_asserted is not False:
            raise (
                RadarReevaluationReviewHandoffInvariantError(
                    "Handoff cannot assert "
                    "execution."
                )
            )

        if (
            self.verification_status
            != "UNVERIFIED_EXTERNAL"
        ):
            raise (
                RadarReevaluationReviewHandoffInvariantError(
                    "ADEL0.29 must remain "
                    "UNVERIFIED_EXTERNAL."
                )
            )

        if self.review_handoff_created is not True:
            raise (
                RadarReevaluationReviewHandoffInvariantError(
                    "review_handoff_created must "
                    "be True."
                )
            )

        required_false = (
            "review_response_created",
            "human_approval_asserted",
            "ay_validation_asserted",
            "ex_authorization_asserted",
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
                    RadarReevaluationReviewHandoffInvariantError(
                        "Handoff boundary cannot "
                        f"assert {name}."
                    )
                )

    @property
    def evidence_id(
        self,
    ) -> str:
        return self.handoff_entry.evidence_id

    @property
    def target(
        self,
    ) -> RadarReviewTarget:
        return self.handoff_entry.target

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
class RadarReevaluationReviewHandoffResult:
    source: RadarReevaluationReviewPacketResult

    handoff: RadarReviewHandoff | None

    assignments: tuple[
        RadarReviewAssignment,
        ...
    ]

    entries: tuple[
        RadarReevaluationReviewHandoffEntry,
        ...
    ]

    review_handoff_created: bool = False

    review_response_created: bool = False
    human_approval_asserted: bool = False
    ay_validation_asserted: bool = False
    ex_authorization_asserted: bool = False

    followup_created: bool = False
    new_research_request_created: bool = False

    network_requested: bool = False
    tool_execution_requested: bool = False
    persistence_requested: bool = False
    mission_transition_requested: bool = False

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
            RadarReevaluationReviewPacketResult,
        ):
            raise TypeError(
                "source must be "
                "RadarReevaluationReviewPacketResult."
            )

        if self.source.packet is None:
            if self.source.review_packet_created is not False:
                raise (
                    RadarReevaluationReviewHandoffInvariantError(
                        "Missing packet requires "
                        "review_packet_created=False."
                    )
                )

            if self.handoff is not None:
                raise (
                    RadarReevaluationReviewHandoffInvariantError(
                        "No packet may create "
                        "a handoff."
                    )
                )

            if self.assignments:
                raise (
                    RadarReevaluationReviewHandoffInvariantError(
                        "No packet may retain "
                        "assignments."
                    )
                )

            if self.entries:
                raise (
                    RadarReevaluationReviewHandoffInvariantError(
                        "No packet may create "
                        "handoff entries."
                    )
                )

            if self.review_handoff_created is not False:
                raise (
                    RadarReevaluationReviewHandoffInvariantError(
                        "No packet requires "
                        "review_handoff_created=False."
                    )
                )

        else:
            if self.source.review_packet_created is not True:
                raise (
                    RadarReevaluationReviewHandoffInvariantError(
                        "Existing packet requires "
                        "review_packet_created=True."
                    )
                )

            if not isinstance(
                self.handoff,
                RadarReviewHandoff,
            ):
                raise TypeError(
                    "handoff must be "
                    "RadarReviewHandoff."
                )

            if self.review_handoff_created is not True:
                raise (
                    RadarReevaluationReviewHandoffInvariantError(
                        "Existing packet handoff "
                        "must be marked created."
                    )
                )

            expected_ids = self.source.evidence_ids

            if self.handoff.evidence_ids != expected_ids:
                raise (
                    RadarReevaluationReviewHandoffInvariantError(
                        "Handoff must cover exact "
                        "ADEL0.28 packet IDs."
                    )
                )

            assignment_ids = tuple(
                row.evidence_id
                for row in self.assignments
            )

            if assignment_ids != expected_ids:
                raise (
                    RadarReevaluationReviewHandoffInvariantError(
                        "Assignments must preserve "
                        "exact packet order and "
                        "coverage."
                    )
                )

            if len(set(assignment_ids)) != len(
                assignment_ids
            ):
                raise (
                    RadarReevaluationReviewHandoffInvariantError(
                        "Assignments require unique "
                        "Evidence IDs."
                    )
                )

            if (
                len(self.entries)
                != self.source.size
            ):
                raise (
                    RadarReevaluationReviewHandoffInvariantError(
                        "Handoff wrapper entry "
                        "count mismatch."
                    )
                )

            for index, entry in enumerate(
                self.entries
            ):
                if not isinstance(
                    entry,
                    RadarReevaluationReviewHandoffEntry,
                ):
                    raise TypeError(
                        "entries must contain "
                        "RadarReevaluationReviewHandoffEntry."
                    )

                if (
                    entry.source_entry
                    is not self.source.entries[index]
                ):
                    raise (
                        RadarReevaluationReviewHandoffInvariantError(
                            "Exact ADEL0.28 source "
                            "identity must be "
                            "preserved."
                        )
                    )

                if (
                    entry.handoff_entry
                    is not self.handoff.entries[index]
                ):
                    raise (
                        RadarReevaluationReviewHandoffInvariantError(
                            "Exact handoff entry "
                            "identity must be "
                            "preserved."
                        )
                    )

                if (
                    entry.assignment
                    is not self.assignments[index]
                ):
                    raise (
                        RadarReevaluationReviewHandoffInvariantError(
                            "Exact assignment "
                            "identity must be "
                            "preserved."
                        )
                    )

        required_false = (
            "review_response_created",
            "human_approval_asserted",
            "ay_validation_asserted",
            "ex_authorization_asserted",
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
                    RadarReevaluationReviewHandoffInvariantError(
                        "Handoff result cannot "
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
            row.evidence_id
            for row in self.entries
        )

    @property
    def targets(
        self,
    ) -> tuple[
        RadarReviewTarget,
        ...
    ]:
        return tuple(
            row.target
            for row in self.entries
        )

    @property
    def packet_ranks(
        self,
    ) -> tuple[int, ...]:
        return tuple(
            row.packet_rank
            for row in self.entries
        )

    @property
    def source_ranks(
        self,
    ) -> tuple[int, ...]:
        return tuple(
            row.source_rank
            for row in self.entries
        )

    @property
    def human_review_routed(
        self,
    ) -> bool:
        return any(
            target
            is RadarReviewTarget.HUMAN_REVIEW
            for target in self.targets
        )

    @property
    def ay_review_routed(
        self,
    ) -> bool:
        return any(
            target
            is RadarReviewTarget.AY_REVIEW
            for target in self.targets
        )

    @property
    def ex_review_routed(
        self,
    ) -> bool:
        return any(
            target
            is RadarReviewTarget.EX_REVIEW
            for target in self.targets
        )


class GovernedRadarReevaluationReviewHandoff:
    """
    ADEL0.29 governed re-evaluation review handoff.

    It reuses the already-governed passive ADEL0.12
    GovernedRadarReviewHandoff.build() primitive.

    Every REVIEW Evidence requires one explicit
    RadarReviewTarget assignment.

    Missing, extra or invalid assignments fail
    closed.

    HUMAN_REVIEW, AY_REVIEW and EX_REVIEW remain
    routing destinations only.

    HUMAN_REVIEW ROUTED != HUMAN APPROVED.
    AY_REVIEW ROUTED != AY VALIDATED.
    EX_REVIEW ROUTED != EX AUTHORIZED.

    No packet means no handoff and requires an
    empty assignment mapping.

    This boundary performs no ReviewResponse,
    human approval, AY validation, EX
    authorization, follow-up, ResearchRequest,
    network access, tool execution, persistence,
    mission transition, truth assertion,
    learning, promotion, activation, execution
    authority or skill creation.

    PACKET CREATED != HANDOFF CREATED.
    HANDOFF CREATED != REVIEW RESPONSE.
    HANDOFF CREATED != HUMAN APPROVAL.
    HANDOFF CREATED != AY VALIDATION.
    HANDOFF CREATED != EX AUTHORIZATION.
    HANDOFF CREATED != FOLLOW-UP.
    HANDOFF CREATED != NEW RESEARCH.
    HANDOFF CREATED != NETWORK.
    HANDOFF CREATED != EXECUTION.
    HANDOFF CREATED != TRUTH.
    """

    @staticmethod
    def handoff(
        source: RadarReevaluationReviewPacketResult,
        *,
        assignments: Mapping[
            str,
            RadarReviewTarget,
        ],
    ) -> RadarReevaluationReviewHandoffResult:
        if not isinstance(
            source,
            RadarReevaluationReviewPacketResult,
        ):
            raise TypeError(
                "source must be "
                "RadarReevaluationReviewPacketResult."
            )

        if not isinstance(
            assignments,
            Mapping,
        ):
            raise TypeError(
                "assignments must be a mapping."
            )

        if source.packet is None:
            if assignments:
                raise (
                    RadarReevaluationReviewHandoffInvariantError(
                        "No ReviewPacket exists; "
                        "assignments must be empty."
                    )
                )

            return (
                RadarReevaluationReviewHandoffResult(
                    source=source,
                    handoff=None,
                    assignments=(),
                    entries=(),
                    review_handoff_created=False,
                )
            )

        handoff = (
            GovernedRadarReviewHandoff
            .build(
                source.packet,
                assignments=assignments,
            )
        )

        assignment_rows = tuple(
            RadarReviewAssignment(
                evidence_id=handoff_entry.evidence_id,
                target=handoff_entry.target,
            )
            for handoff_entry
            in handoff.entries
        )

        entries = tuple(
            RadarReevaluationReviewHandoffEntry(
                source_entry=source_entry,
                handoff_entry=handoff_entry,
                assignment=assignment,
            )
            for (
                source_entry,
                handoff_entry,
                assignment,
            )
            in zip(
                source.entries,
                handoff.entries,
                assignment_rows,
                strict=True,
            )
        )

        return (
            RadarReevaluationReviewHandoffResult(
                source=source,
                handoff=handoff,
                assignments=assignment_rows,
                entries=entries,
                review_handoff_created=True,
            )
        )


__all__ = [
    "GovernedRadarReevaluationReviewHandoff",
    "RadarReevaluationReviewHandoffEntry",
    "RadarReevaluationReviewHandoffInvariantError",
    "RadarReevaluationReviewHandoffResult",
]
