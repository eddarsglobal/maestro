from __future__ import annotations

from dataclasses import dataclass

from .radar_decision_envelope import (
    GovernedRadarDecisionEnvelope,
    RadarDecisionEntry,
    RadarDecisionEnvelope,
    RadarDecisionPolicy,
    RadarDisposition,
)
from .radar_research_portfolio_reintegration import (
    RadarReevaluationPortfolioEntry,
    RadarReevaluationPortfolioReintegrationResult,
)


class RadarReevaluationDecisionInvariantError(
    ValueError
):
    pass


def _expected_disposition(
    score: float,
    policy: RadarDecisionPolicy,
) -> RadarDisposition:
    if score >= policy.review_min_priority:
        return RadarDisposition.REVIEW

    if score >= policy.investigate_min_priority:
        return RadarDisposition.INVESTIGATE

    return RadarDisposition.OBSERVE


@dataclass(
    frozen=True,
    slots=True,
)
class RadarReevaluationDecisionEntry:
    source_entry: RadarReevaluationPortfolioEntry

    decision_entry: RadarDecisionEntry

    policy: RadarDecisionPolicy

    decision_created: bool = True

    review_packet_created: bool = False
    review_handoff_created: bool = False
    review_response_created: bool = False

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
            RadarReevaluationPortfolioEntry,
        ):
            raise TypeError(
                "source_entry must be "
                "RadarReevaluationPortfolioEntry."
            )

        if not isinstance(
            self.decision_entry,
            RadarDecisionEntry,
        ):
            raise TypeError(
                "decision_entry must be "
                "RadarDecisionEntry."
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
        decision = self.decision_entry

        if (
            source.portfolio_reintegrated
            is not True
        ):
            raise (
                RadarReevaluationDecisionInvariantError(
                    "Decision requires a "
                    "reintegrated portfolio."
                )
            )

        if source.ranking_created is not True:
            raise (
                RadarReevaluationDecisionInvariantError(
                    "Decision requires an existing "
                    "portfolio ranking."
                )
            )

        if source.second_radar_evaluation is not False:
            raise (
                RadarReevaluationDecisionInvariantError(
                    "ADEL0.27 cannot consume a "
                    "second Radar evaluation."
                )
            )

        if (
            source.decision_envelope_created
            is not False
        ):
            raise (
                RadarReevaluationDecisionInvariantError(
                    "ADEL0.26 source must not "
                    "already contain a decision."
                )
            )

        if (
            decision.rank
            != source.portfolio_rank
        ):
            raise (
                RadarReevaluationDecisionInvariantError(
                    "Decision rank must preserve "
                    "portfolio rank."
                )
            )

        if (
            decision.evidence_id
            != source.evidence_id
        ):
            raise (
                RadarReevaluationDecisionInvariantError(
                    "Decision Evidence identity "
                    "mismatch."
                )
            )

        if (
            decision.priority_score
            != source.priority_score
        ):
            raise (
                RadarReevaluationDecisionInvariantError(
                    "Decision priority score must "
                    "preserve portfolio score."
                )
            )

        expected = _expected_disposition(
            source.priority_score,
            self.policy,
        )

        if decision.disposition is not expected:
            raise (
                RadarReevaluationDecisionInvariantError(
                    "Decision disposition does not "
                    "match explicit policy."
                )
            )

        if (
            decision.verification_status
            != "UNVERIFIED_EXTERNAL"
        ):
            raise (
                RadarReevaluationDecisionInvariantError(
                    "Decision must remain "
                    "UNVERIFIED_EXTERNAL."
                )
            )

        if (
            decision.system_truth_asserted
            is not False
        ):
            raise (
                RadarReevaluationDecisionInvariantError(
                    "Decision cannot assert "
                    "system truth."
                )
            )

        if (
            self.verification_status
            != "UNVERIFIED_EXTERNAL"
        ):
            raise (
                RadarReevaluationDecisionInvariantError(
                    "Decision boundary must remain "
                    "UNVERIFIED_EXTERNAL."
                )
            )

        if self.system_truth_asserted is not False:
            raise (
                RadarReevaluationDecisionInvariantError(
                    "Decision boundary cannot "
                    "assert system truth."
                )
            )

        if self.decision_created is not True:
            raise (
                RadarReevaluationDecisionInvariantError(
                    "decision_created must be True."
                )
            )

        required_false = (
            "review_packet_created",
            "review_handoff_created",
            "review_response_created",
            "followup_created",
            "new_research_request_created",
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
                    RadarReevaluationDecisionInvariantError(
                        "Decision boundary cannot "
                        f"assert {name}."
                    )
                )

    @property
    def rank(
        self,
    ) -> int:
        return self.decision_entry.rank

    @property
    def evidence_id(
        self,
    ) -> str:
        return self.decision_entry.evidence_id

    @property
    def priority_score(
        self,
    ) -> float:
        return (
            self.decision_entry
            .priority_score
        )

    @property
    def disposition(
        self,
    ) -> RadarDisposition:
        return (
            self.decision_entry
            .disposition
        )

    @property
    def review_recommended(
        self,
    ) -> bool:
        return (
            self.disposition
            is RadarDisposition.REVIEW
        )

    @property
    def investigate_recommended(
        self,
    ) -> bool:
        return (
            self.disposition
            is RadarDisposition.INVESTIGATE
        )

    @property
    def observe_recommended(
        self,
    ) -> bool:
        return (
            self.disposition
            is RadarDisposition.OBSERVE
        )

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
class RadarReevaluationDecisionResult:
    source: (
        RadarReevaluationPortfolioReintegrationResult
    )

    policy: RadarDecisionPolicy

    envelope: RadarDecisionEnvelope

    entries: tuple[
        RadarReevaluationDecisionEntry,
        ...
    ]

    decision_envelope_created: bool = True

    review_packet_created: bool = False
    review_handoff_created: bool = False
    review_response_created: bool = False

    followup_created: bool = False
    new_research_request_created: bool = False

    second_radar_evaluation: bool = False
    second_ranking_created: bool = False

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
            RadarReevaluationPortfolioReintegrationResult,
        ):
            raise TypeError(
                "source must be "
                "RadarReevaluationPortfolioReintegrationResult."
            )

        if not isinstance(
            self.policy,
            RadarDecisionPolicy,
        ):
            raise TypeError(
                "policy must be "
                "RadarDecisionPolicy."
            )

        if not isinstance(
            self.envelope,
            RadarDecisionEnvelope,
        ):
            raise TypeError(
                "envelope must be "
                "RadarDecisionEnvelope."
            )

        if (
            self.source.portfolio_reintegrated
            is not True
        ):
            raise (
                RadarReevaluationDecisionInvariantError(
                    "Decision requires ADEL0.26 "
                    "portfolio reintegration."
                )
            )

        if self.source.ranking_created is not True:
            raise (
                RadarReevaluationDecisionInvariantError(
                    "Decision requires ADEL0.26 "
                    "ranking."
                )
            )

        if (
            self.source.second_radar_evaluation
            is not False
        ):
            raise (
                RadarReevaluationDecisionInvariantError(
                    "ADEL0.27 cannot follow a "
                    "second Radar evaluation."
                )
            )

        if (
            self.source
            .decision_envelope_created
            is not False
        ):
            raise (
                RadarReevaluationDecisionInvariantError(
                    "ADEL0.26 must not already "
                    "contain a decision envelope."
                )
            )

        if (
            self.envelope.evidence_ids
            != self.source.ranked_evidence_ids
        ):
            raise (
                RadarReevaluationDecisionInvariantError(
                    "Decision envelope must cover "
                    "the exact ranked portfolio "
                    "in the exact order."
                )
            )

        if (
            self.envelope.size
            != self.source.size
        ):
            raise (
                RadarReevaluationDecisionInvariantError(
                    "Decision envelope size must "
                    "match portfolio size."
                )
            )

        if (
            len(self.entries)
            != self.envelope.size
        ):
            raise (
                RadarReevaluationDecisionInvariantError(
                    "Decision result entry count "
                    "must match envelope size."
                )
            )

        for index, entry in enumerate(
            self.entries
        ):
            if not isinstance(
                entry,
                RadarReevaluationDecisionEntry,
            ):
                raise TypeError(
                    "entries must contain "
                    "RadarReevaluationDecisionEntry."
                )

            source_entry = (
                self.source.entries[index]
            )

            decision_entry = (
                self.envelope.entries[index]
            )

            if (
                entry.source_entry
                is not source_entry
            ):
                raise (
                    RadarReevaluationDecisionInvariantError(
                        "Decision result must "
                        "preserve exact ADEL0.26 "
                        "source-entry identity."
                    )
                )

            if (
                entry.decision_entry
                is not decision_entry
            ):
                raise (
                    RadarReevaluationDecisionInvariantError(
                        "Decision result must "
                        "preserve exact envelope "
                        "entry identity."
                    )
                )

            if entry.policy is not self.policy:
                raise (
                    RadarReevaluationDecisionInvariantError(
                        "Every decision entry must "
                        "preserve exact policy "
                        "identity."
                    )
                )

        if (
            self.decision_envelope_created
            is not True
        ):
            raise (
                RadarReevaluationDecisionInvariantError(
                    "decision_envelope_created "
                    "must be True."
                )
            )

        required_false = (
            "review_packet_created",
            "review_handoff_created",
            "review_response_created",
            "followup_created",
            "new_research_request_created",
            "second_radar_evaluation",
            "second_ranking_created",
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
                    RadarReevaluationDecisionInvariantError(
                        "Decision result cannot "
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
    def dispositions(
        self,
    ) -> tuple[
        RadarDisposition,
        ...
    ]:
        return tuple(
            entry.disposition
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

    @property
    def review_recommended_evidence_ids(
        self,
    ) -> tuple[str, ...]:
        return tuple(
            entry.evidence_id
            for entry in self.entries
            if entry.review_recommended
        )


class GovernedRadarReevaluationDecisionMaker:
    """
    ADEL0.27 governed re-evaluation decision
    envelope.

    It consumes exactly the ADEL0.26 ranked
    RadarPortfolioResult and an explicit
    RadarDecisionPolicy.

    It delegates disposition calculation to the
    existing pure ADEL0.10
    GovernedRadarDecisionEnvelope.evaluate()
    boundary.

    OBSERVE, INVESTIGATE and REVIEW remain
    passive research recommendations only.

    REVIEW disposition does NOT create a
    ReviewPacket, ReviewHandoff or ReviewResponse.

    This boundary performs no second Radar
    evaluation, no second ranking, no follow-up,
    no ResearchRequest creation, no network
    access, no tool execution, no persistence,
    no mission transition, no AY validation,
    no EX authorization, no truth assertion,
    no learning, no promotion, no activation,
    no execution authority and no skill
    creation.

    PORTFOLIO RANKED != DECISION.
    DECISION CREATED != REVIEW CREATED.
    REVIEW RECOMMENDED != REVIEW CREATED.
    DECISION CREATED != FOLLOW-UP.
    DECISION CREATED != NEW RESEARCH.
    DECISION CREATED != AUTHORIZATION.
    DECISION CREATED != TRUTH.
    """

    @staticmethod
    def decide(
        source: (
            RadarReevaluationPortfolioReintegrationResult
        ),
        *,
        policy: RadarDecisionPolicy,
    ) -> RadarReevaluationDecisionResult:
        if not isinstance(
            source,
            RadarReevaluationPortfolioReintegrationResult,
        ):
            raise TypeError(
                "source must be "
                "RadarReevaluationPortfolioReintegrationResult."
            )

        if not isinstance(
            policy,
            RadarDecisionPolicy,
        ):
            raise TypeError(
                "policy must be "
                "RadarDecisionPolicy."
            )

        envelope = (
            GovernedRadarDecisionEnvelope
            .evaluate(
                source.portfolio,
                policy=policy,
            )
        )

        entries = tuple(
            RadarReevaluationDecisionEntry(
                source_entry=source_entry,
                decision_entry=decision_entry,
                policy=policy,
            )
            for source_entry, decision_entry
            in zip(
                source.entries,
                envelope.entries,
                strict=True,
            )
        )

        return RadarReevaluationDecisionResult(
            source=source,
            policy=policy,
            envelope=envelope,
            entries=entries,
        )


__all__ = [
    "GovernedRadarReevaluationDecisionMaker",
    "RadarReevaluationDecisionEntry",
    "RadarReevaluationDecisionInvariantError",
    "RadarReevaluationDecisionResult",
]
