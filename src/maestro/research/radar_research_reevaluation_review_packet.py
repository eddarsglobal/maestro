from __future__ import annotations

from dataclasses import dataclass

from .radar_decision_envelope import (
    RadarDecisionPolicy,
    RadarDisposition,
)
from .radar_review_packet import (
    RadarFactorSnapshot,
    RadarReviewEntry,
    RadarReviewPacket,
)
from .radar_research_reevaluation_decision import (
    RadarReevaluationDecisionEntry,
    RadarReevaluationDecisionResult,
)


class RadarReevaluationReviewPacketInvariantError(
    ValueError
):
    pass


def _review_rationale(
    score: float,
    policy: RadarDecisionPolicy,
) -> str:
    return (
        "Priority score "
        f"{score!r} meets or exceeds "
        "review threshold "
        f"{policy.review_min_priority!r}."
    )


@dataclass(
    frozen=True,
    slots=True,
)
class RadarReevaluationReviewPacketEntry:
    source_entry: RadarReevaluationDecisionEntry

    packet_entry: RadarReviewEntry

    policy: RadarDecisionPolicy

    review_packet_created: bool = True

    review_handoff_created: bool = False
    review_response_created: bool = False
    human_approval_asserted: bool = False

    followup_created: bool = False
    new_research_request_created: bool = False

    second_radar_evaluation: bool = False
    second_ranking_created: bool = False
    second_decision_created: bool = False

    network_requested: bool = False
    tool_execution_requested: bool = False
    persistence_requested: bool = False
    mission_transition_requested: bool = False

    verification_status: str = (
        "UNVERIFIED_EXTERNAL"
    )

    system_truth_asserted: bool = False

    ay_validation_asserted: bool = False
    ex_authorization_asserted: bool = False

    learning_asserted: bool = False
    promotion_asserted: bool = False
    activation_asserted: bool = False
    execution_asserted: bool = False

    def __post_init__(
        self,
    ) -> None:
        if not isinstance(
            self.source_entry,
            RadarReevaluationDecisionEntry,
        ):
            raise TypeError(
                "source_entry must be "
                "RadarReevaluationDecisionEntry."
            )

        if not isinstance(
            self.packet_entry,
            RadarReviewEntry,
        ):
            raise TypeError(
                "packet_entry must be "
                "RadarReviewEntry."
            )

        if not isinstance(
            self.policy,
            RadarDecisionPolicy,
        ):
            raise TypeError(
                "policy must be "
                "RadarDecisionPolicy."
            )

        source = self.source_entry
        packet = self.packet_entry

        if source.policy is not self.policy:
            raise (
                RadarReevaluationReviewPacketInvariantError(
                    "Packet entry must preserve "
                    "exact ADEL0.27 policy identity."
                )
            )

        if source.review_recommended is not True:
            raise (
                RadarReevaluationReviewPacketInvariantError(
                    "Only REVIEW recommendations "
                    "may become review packets."
                )
            )

        if (
            source.disposition
            is not RadarDisposition.REVIEW
        ):
            raise (
                RadarReevaluationReviewPacketInvariantError(
                    "Source disposition must be "
                    "REVIEW."
                )
            )

        if (
            packet.disposition
            is not RadarDisposition.REVIEW
        ):
            raise (
                RadarReevaluationReviewPacketInvariantError(
                    "Packet disposition must be "
                    "REVIEW."
                )
            )

        if (
            packet.evidence_id
            != source.evidence_id
        ):
            raise (
                RadarReevaluationReviewPacketInvariantError(
                    "Packet Evidence identity "
                    "mismatch."
                )
            )

        if (
            packet.priority_score
            != source.priority_score
        ):
            raise (
                RadarReevaluationReviewPacketInvariantError(
                    "Packet priority score must "
                    "preserve ADEL0.27 score."
                )
            )

        if (
            source.priority_score
            < self.policy.review_min_priority
        ):
            raise (
                RadarReevaluationReviewPacketInvariantError(
                    "REVIEW packet score must meet "
                    "review threshold."
                )
            )

        observation = (
            source.source_entry
            .ranked_observation
        )

        if (
            packet.source_ref
            != observation.source_ref
        ):
            raise (
                RadarReevaluationReviewPacketInvariantError(
                    "Packet source_ref mismatch."
                )
            )

        if packet.claim != observation.claim:
            raise (
                RadarReevaluationReviewPacketInvariantError(
                    "Packet claim mismatch."
                )
            )

        factors = observation.factors
        snapshot = packet.factors

        factor_pairs = (
            (
                snapshot.novelty,
                factors.novelty,
            ),
            (
                snapshot.source_quality,
                factors.source_quality,
            ),
            (
                snapshot.relevance_to_maestro,
                factors.relevance_to_maestro,
            ),
            (
                snapshot.expected_capability_gain,
                factors.expected_capability_gain,
            ),
            (
                snapshot.reproducibility,
                factors.reproducibility,
            ),
            (
                snapshot.integration_cost,
                factors.integration_cost,
            ),
            (
                snapshot.security_risk,
                factors.security_risk,
            ),
        )

        if any(
            before != after
            for before, after in factor_pairs
        ):
            raise (
                RadarReevaluationReviewPacketInvariantError(
                    "Packet factor snapshot must "
                    "preserve ADEL0.27 factors."
                )
            )

        expected_rationale = _review_rationale(
            source.priority_score,
            self.policy,
        )

        if packet.rationale != expected_rationale:
            raise (
                RadarReevaluationReviewPacketInvariantError(
                    "Packet rationale mismatch."
                )
            )

        if (
            packet.verification_status
            != "UNVERIFIED_EXTERNAL"
        ):
            raise (
                RadarReevaluationReviewPacketInvariantError(
                    "Review packet must remain "
                    "UNVERIFIED_EXTERNAL."
                )
            )

        if (
            packet.system_truth_asserted
            is not False
        ):
            raise (
                RadarReevaluationReviewPacketInvariantError(
                    "Review packet cannot assert "
                    "system truth."
                )
            )

        if (
            self.verification_status
            != "UNVERIFIED_EXTERNAL"
        ):
            raise (
                RadarReevaluationReviewPacketInvariantError(
                    "Review boundary must remain "
                    "UNVERIFIED_EXTERNAL."
                )
            )

        if self.system_truth_asserted is not False:
            raise (
                RadarReevaluationReviewPacketInvariantError(
                    "Review boundary cannot assert "
                    "system truth."
                )
            )

        if self.review_packet_created is not True:
            raise (
                RadarReevaluationReviewPacketInvariantError(
                    "review_packet_created must be "
                    "True for a packet entry."
                )
            )

        required_false = (
            "review_handoff_created",
            "review_response_created",
            "human_approval_asserted",
            "followup_created",
            "new_research_request_created",
            "second_radar_evaluation",
            "second_ranking_created",
            "second_decision_created",
            "network_requested",
            "tool_execution_requested",
            "persistence_requested",
            "mission_transition_requested",
            "ay_validation_asserted",
            "ex_authorization_asserted",
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
                    RadarReevaluationReviewPacketInvariantError(
                        "Review packet boundary "
                        f"cannot assert {name}."
                    )
                )

    @property
    def packet_rank(
        self,
    ) -> int:
        return self.packet_entry.rank

    @property
    def source_rank(
        self,
    ) -> int:
        return self.source_entry.rank

    @property
    def evidence_id(
        self,
    ) -> str:
        return self.packet_entry.evidence_id

    @property
    def priority_score(
        self,
    ) -> float:
        return self.packet_entry.priority_score

    @property
    def disposition(
        self,
    ) -> RadarDisposition:
        return self.packet_entry.disposition

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
class RadarReevaluationReviewPacketResult:
    source: RadarReevaluationDecisionResult

    packet: RadarReviewPacket | None

    entries: tuple[
        RadarReevaluationReviewPacketEntry,
        ...
    ]

    review_selection_applied: bool = True
    review_packet_created: bool = False

    review_handoff_created: bool = False
    review_response_created: bool = False
    human_approval_asserted: bool = False

    followup_created: bool = False
    new_research_request_created: bool = False

    second_radar_evaluation: bool = False
    second_ranking_created: bool = False
    second_decision_created: bool = False

    network_requested: bool = False
    tool_execution_requested: bool = False
    persistence_requested: bool = False
    mission_transition_requested: bool = False

    system_truth_asserted: bool = False

    ay_validation_asserted: bool = False
    ex_authorization_asserted: bool = False

    learning_asserted: bool = False
    promotion_asserted: bool = False
    activation_asserted: bool = False
    execution_asserted: bool = False

    def __post_init__(
        self,
    ) -> None:
        if not isinstance(
            self.source,
            RadarReevaluationDecisionResult,
        ):
            raise TypeError(
                "source must be "
                "RadarReevaluationDecisionResult."
            )

        expected_ids = (
            self.source
            .review_recommended_evidence_ids
        )

        if not expected_ids:
            if self.packet is not None:
                raise (
                    RadarReevaluationReviewPacketInvariantError(
                        "No REVIEW recommendation "
                        "may create a packet."
                    )
                )

            if self.entries:
                raise (
                    RadarReevaluationReviewPacketInvariantError(
                        "No REVIEW recommendation "
                        "may create packet entries."
                    )
                )

            if self.review_packet_created is not False:
                raise (
                    RadarReevaluationReviewPacketInvariantError(
                        "review_packet_created must "
                        "be False without REVIEW."
                    )
                )

        else:
            if not isinstance(
                self.packet,
                RadarReviewPacket,
            ):
                raise TypeError(
                    "packet must be "
                    "RadarReviewPacket when REVIEW "
                    "recommendations exist."
                )

            if self.review_packet_created is not True:
                raise (
                    RadarReevaluationReviewPacketInvariantError(
                        "review_packet_created must "
                        "be True when packet exists."
                    )
                )

            if self.packet.policy is not self.source.policy:
                raise (
                    RadarReevaluationReviewPacketInvariantError(
                        "Packet must preserve exact "
                        "ADEL0.27 policy identity."
                    )
                )

            if (
                self.packet.evidence_ids
                != expected_ids
            ):
                raise (
                    RadarReevaluationReviewPacketInvariantError(
                        "Packet must contain exactly "
                        "REVIEW-recommended Evidence "
                        "IDs in source order."
                    )
                )

            entry_ids = tuple(
                entry.evidence_id
                for entry in self.entries
            )

            if entry_ids != expected_ids:
                raise (
                    RadarReevaluationReviewPacketInvariantError(
                        "Result entries must contain "
                        "exactly REVIEW Evidence IDs."
                    )
                )

            if (
                len(self.entries)
                != self.packet.size
            ):
                raise (
                    RadarReevaluationReviewPacketInvariantError(
                        "Result entry count must "
                        "match packet size."
                    )
                )

            packet_ranks = tuple(
                entry.packet_rank
                for entry in self.entries
            )

            if packet_ranks != tuple(
                range(
                    1,
                    len(self.entries) + 1,
                )
            ):
                raise (
                    RadarReevaluationReviewPacketInvariantError(
                        "Packet-local ranks must be "
                        "contiguous and one-based."
                    )
                )

            source_by_id = {
                entry.evidence_id: entry
                for entry in self.source.entries
                if entry.review_recommended
            }

            for index, entry in enumerate(
                self.entries
            ):
                if not isinstance(
                    entry,
                    RadarReevaluationReviewPacketEntry,
                ):
                    raise TypeError(
                        "entries must contain "
                        "RadarReevaluationReviewPacketEntry."
                    )

                packet_entry = (
                    self.packet.entries[index]
                )

                if (
                    entry.packet_entry
                    is not packet_entry
                ):
                    raise (
                        RadarReevaluationReviewPacketInvariantError(
                            "Result must preserve "
                            "exact packet-entry "
                            "identity."
                        )
                    )

                source_entry = source_by_id[
                    entry.evidence_id
                ]

                if (
                    entry.source_entry
                    is not source_entry
                ):
                    raise (
                        RadarReevaluationReviewPacketInvariantError(
                            "Result must preserve "
                            "exact ADEL0.27 source "
                            "identity."
                        )
                    )

        if self.review_selection_applied is not True:
            raise (
                RadarReevaluationReviewPacketInvariantError(
                    "review_selection_applied must "
                    "be True."
                )
            )

        required_false = (
            "review_handoff_created",
            "review_response_created",
            "human_approval_asserted",
            "followup_created",
            "new_research_request_created",
            "second_radar_evaluation",
            "second_ranking_created",
            "second_decision_created",
            "network_requested",
            "tool_execution_requested",
            "persistence_requested",
            "mission_transition_requested",
            "system_truth_asserted",
            "ay_validation_asserted",
            "ex_authorization_asserted",
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
                    RadarReevaluationReviewPacketInvariantError(
                        "Review packet result cannot "
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
    def source_ranks(
        self,
    ) -> tuple[int, ...]:
        return tuple(
            entry.source_rank
            for entry in self.entries
        )

    @property
    def packet_ranks(
        self,
    ) -> tuple[int, ...]:
        return tuple(
            entry.packet_rank
            for entry in self.entries
        )


class GovernedRadarReevaluationReviewPacketMaterializer:
    """
    ADEL0.28 REVIEW-only packet materialization.

    ADEL0.11's generic packet builder explains
    OBSERVE, INVESTIGATE and REVIEW alike.

    This stricter re-evaluation boundary therefore
    performs explicit REVIEW-only selection.

    OBSERVE and INVESTIGATE decisions are excluded.

    When no REVIEW recommendation exists, no
    RadarReviewPacket is created.

    When REVIEW recommendations exist, this
    boundary snapshots only already-computed
    observation factors and creates explanatory
    RadarReviewEntry values.

    It performs no Radar evaluation, ranking,
    decision recomputation, ReviewHandoff,
    ReviewResponse, human approval, follow-up,
    ResearchRequest creation, network access,
    tool execution, persistence, mission
    transition, AY validation, EX authorization,
    truth assertion, learning, promotion,
    activation, execution authority or skill
    creation.

    REVIEW RECOMMENDED != REVIEW PACKET CREATED.
    REVIEW PACKET CREATED != REVIEW HANDOFF.
    REVIEW PACKET CREATED != HUMAN APPROVAL.
    REVIEW PACKET CREATED != REVIEW RESPONSE.
    REVIEW PACKET CREATED != AY VALIDATION.
    REVIEW PACKET CREATED != EX AUTHORIZATION.
    REVIEW PACKET CREATED != FOLLOW-UP.
    REVIEW PACKET CREATED != NEW RESEARCH.
    REVIEW PACKET CREATED != TRUTH.
    """

    @staticmethod
    def materialize(
        source: RadarReevaluationDecisionResult,
    ) -> RadarReevaluationReviewPacketResult:
        if not isinstance(
            source,
            RadarReevaluationDecisionResult,
        ):
            raise TypeError(
                "source must be "
                "RadarReevaluationDecisionResult."
            )

        selected = tuple(
            entry
            for entry in source.entries
            if entry.review_recommended
        )

        if not selected:
            return (
                RadarReevaluationReviewPacketResult(
                    source=source,
                    packet=None,
                    entries=(),
                    review_packet_created=False,
                )
            )

        packet_entries = []

        for packet_rank, source_entry in enumerate(
            selected,
            start=1,
        ):
            observation = (
                source_entry
                .source_entry
                .ranked_observation
            )

            packet_entries.append(
                RadarReviewEntry(
                    rank=packet_rank,
                    evidence_id=(
                        source_entry.evidence_id
                    ),
                    source_ref=(
                        observation.source_ref
                    ),
                    claim=observation.claim,
                    disposition=(
                        RadarDisposition.REVIEW
                    ),
                    priority_score=(
                        source_entry
                        .priority_score
                    ),
                    factors=(
                        RadarFactorSnapshot
                        .from_factors(
                            observation.factors
                        )
                    ),
                    rationale=(
                        _review_rationale(
                            source_entry
                            .priority_score,
                            source.policy,
                        )
                    ),
                )
            )

        packet = RadarReviewPacket(
            policy=source.policy,
            entries=tuple(
                packet_entries
            ),
        )

        entries = tuple(
            RadarReevaluationReviewPacketEntry(
                source_entry=source_entry,
                packet_entry=packet_entry,
                policy=source.policy,
            )
            for source_entry, packet_entry
            in zip(
                selected,
                packet.entries,
                strict=True,
            )
        )

        return (
            RadarReevaluationReviewPacketResult(
                source=source,
                packet=packet,
                entries=entries,
                review_packet_created=True,
            )
        )


__all__ = [
    "GovernedRadarReevaluationReviewPacketMaterializer",
    "RadarReevaluationReviewPacketEntry",
    "RadarReevaluationReviewPacketInvariantError",
    "RadarReevaluationReviewPacketResult",
]
