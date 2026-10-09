from __future__ import annotations

from dataclasses import dataclass

from .provider_contracts import (
    ResearchCapability,
)
from .radar_followup_candidate import (
    GovernedRadarFollowUpCandidateBuilder,
    RadarFollowUpCandidate,
    RadarFollowUpCandidateSet,
)
from .radar_review_handoff import (
    RadarReviewTarget,
)
from .radar_research_reevaluation_evidence_followup import (
    RadarReevaluationEvidenceFollowUpEntry,
    RadarReevaluationEvidenceFollowUpResult,
)


class RadarReevaluationFollowUpCandidateInvariantError(
    ValueError
):
    pass


@dataclass(
    frozen=True,
    slots=True,
)
class RadarReevaluationFollowUpCandidateEntry:
    source_entry: RadarReevaluationEvidenceFollowUpEntry
    candidate: RadarFollowUpCandidate

    followup_candidate_created: bool = True
    query_prepared: bool = True

    research_request_draft_created: bool = False
    new_task_id_bound: bool = False
    research_request_created: bool = False
    provider_selected: bool = False
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

    skill_creation_requested: bool = False

    def __post_init__(
        self,
    ) -> None:
        if not isinstance(
            self.source_entry,
            RadarReevaluationEvidenceFollowUpEntry,
        ):
            raise TypeError(
                "source_entry must be "
                "RadarReevaluationEvidenceFollowUpEntry."
            )

        if not isinstance(
            self.candidate,
            RadarFollowUpCandidate,
        ):
            raise TypeError(
                "candidate must be "
                "RadarFollowUpCandidate."
            )

        source = self.source_entry
        candidate = self.candidate
        need = source.need

        if source.followup_need_created is not True:
            raise (
                RadarReevaluationFollowUpCandidateInvariantError(
                    "Follow-up candidate requires "
                    "an existing ADEL0.31 need."
                )
            )

        if candidate.rank != need.rank:
            raise (
                RadarReevaluationFollowUpCandidateInvariantError(
                    "Candidate rank must preserve "
                    "follow-up rank."
                )
            )

        if candidate.evidence_id != need.evidence_id:
            raise (
                RadarReevaluationFollowUpCandidateInvariantError(
                    "Candidate Evidence identity "
                    "mismatch."
                )
            )

        if candidate.source_ref != need.source_ref:
            raise (
                RadarReevaluationFollowUpCandidateInvariantError(
                    "Candidate source_ref mismatch."
                )
            )

        if candidate.claim != need.claim:
            raise (
                RadarReevaluationFollowUpCandidateInvariantError(
                    "Candidate claim mismatch."
                )
            )

        if (
            candidate.priority_score
            != need.priority_score
        ):
            raise (
                RadarReevaluationFollowUpCandidateInvariantError(
                    "Candidate priority score "
                    "mismatch."
                )
            )

        if candidate.factors is not need.factors:
            raise (
                RadarReevaluationFollowUpCandidateInvariantError(
                    "Candidate must preserve exact "
                    "factor snapshot identity."
                )
            )

        if candidate.rationale != need.rationale:
            raise (
                RadarReevaluationFollowUpCandidateInvariantError(
                    "Candidate rationale mismatch."
                )
            )

        if candidate.target is not need.target:
            raise (
                RadarReevaluationFollowUpCandidateInvariantError(
                    "Candidate target mismatch."
                )
            )

        if (
            candidate.capability
            is not ResearchCapability.SEARCH
        ):
            raise (
                RadarReevaluationFollowUpCandidateInvariantError(
                    "Candidate capability must "
                    "remain SEARCH."
                )
            )

        if (
            not isinstance(
                candidate.query,
                str,
            )
            or not candidate.query.strip()
        ):
            raise (
                RadarReevaluationFollowUpCandidateInvariantError(
                    "Candidate query must be "
                    "non-empty."
                )
            )

        if need.claim not in candidate.query:
            raise (
                RadarReevaluationFollowUpCandidateInvariantError(
                    "Candidate query must preserve "
                    "the source claim."
                )
            )

        if candidate.preferred_local is not True:
            raise (
                RadarReevaluationFollowUpCandidateInvariantError(
                    "Candidate must preserve "
                    "preferred_local=True."
                )
            )

        if (
            candidate.verification_status
            != "UNVERIFIED_EXTERNAL"
        ):
            raise (
                RadarReevaluationFollowUpCandidateInvariantError(
                    "Candidate must remain "
                    "UNVERIFIED_EXTERNAL."
                )
            )

        if candidate.system_truth_asserted is not False:
            raise (
                RadarReevaluationFollowUpCandidateInvariantError(
                    "Candidate cannot assert "
                    "system truth."
                )
            )

        passive_candidate_flags = (
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

        for name in passive_candidate_flags:
            if getattr(
                candidate,
                name,
            ) is not False:
                raise (
                    RadarReevaluationFollowUpCandidateInvariantError(
                        "ADEL0.15 candidate crossed "
                        f"forbidden boundary {name}."
                    )
                )

        if self.followup_candidate_created is not True:
            raise (
                RadarReevaluationFollowUpCandidateInvariantError(
                    "followup_candidate_created "
                    "must be True."
                )
            )

        if self.query_prepared is not True:
            raise (
                RadarReevaluationFollowUpCandidateInvariantError(
                    "query_prepared must be True."
                )
            )

        if (
            self.verification_status
            != "UNVERIFIED_EXTERNAL"
        ):
            raise (
                RadarReevaluationFollowUpCandidateInvariantError(
                    "ADEL0.32 must remain "
                    "UNVERIFIED_EXTERNAL."
                )
            )

        required_false = (
            "research_request_draft_created",
            "new_task_id_bound",
            "research_request_created",
            "provider_selected",
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
            "skill_creation_requested",
        )

        for name in required_false:
            if getattr(
                self,
                name,
            ) is not False:
                raise (
                    RadarReevaluationFollowUpCandidateInvariantError(
                        "Candidate boundary cannot "
                        f"assert {name}."
                    )
                )

    @property
    def evidence_id(
        self,
    ) -> str:
        return self.candidate.evidence_id

    @property
    def query(
        self,
    ) -> str:
        return self.candidate.query

    @property
    def capability(
        self,
    ) -> ResearchCapability:
        return self.candidate.capability

    @property
    def preferred_local(
        self,
    ) -> bool:
        return self.candidate.preferred_local

    @property
    def target(
        self,
    ) -> RadarReviewTarget:
        return self.candidate.target

    @property
    def followup_rank(
        self,
    ) -> int:
        return self.candidate.rank

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
    def origin_task_id(
        self,
    ) -> str:
        return self.source_entry.task_id


@dataclass(
    frozen=True,
    slots=True,
)
class RadarReevaluationFollowUpCandidateResult:
    source: RadarReevaluationEvidenceFollowUpResult

    candidates: RadarFollowUpCandidateSet | None

    entries: tuple[
        RadarReevaluationFollowUpCandidateEntry,
        ...
    ]

    candidate_set_materialized: bool = False
    followup_candidate_created: bool = False
    query_preparation_performed: bool = False

    research_request_draft_created: bool = False
    new_task_id_bound: bool = False
    research_request_created: bool = False
    provider_selected: bool = False
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

    skill_creation_requested: bool = False

    def __post_init__(
        self,
    ) -> None:
        if not isinstance(
            self.source,
            RadarReevaluationEvidenceFollowUpResult,
        ):
            raise TypeError(
                "source must be "
                "RadarReevaluationEvidenceFollowUpResult."
            )

        if self.source.followup is None:
            if self.candidates is not None:
                raise (
                    RadarReevaluationFollowUpCandidateInvariantError(
                        "No follow-up may materialize "
                        "a candidate set."
                    )
                )

            if self.entries:
                raise (
                    RadarReevaluationFollowUpCandidateInvariantError(
                        "No follow-up may create "
                        "candidate entries."
                    )
                )

            if self.candidate_set_materialized is not False:
                raise (
                    RadarReevaluationFollowUpCandidateInvariantError(
                        "No follow-up requires "
                        "candidate_set_materialized=False."
                    )
                )

            if self.followup_candidate_created is not False:
                raise (
                    RadarReevaluationFollowUpCandidateInvariantError(
                        "No follow-up requires "
                        "followup_candidate_created=False."
                    )
                )

            if self.query_preparation_performed is not False:
                raise (
                    RadarReevaluationFollowUpCandidateInvariantError(
                        "No follow-up may prepare "
                        "candidate queries."
                    )
                )

        else:
            if not isinstance(
                self.candidates,
                RadarFollowUpCandidateSet,
            ):
                raise TypeError(
                    "candidates must be "
                    "RadarFollowUpCandidateSet."
                )

            if self.candidate_set_materialized is not True:
                raise (
                    RadarReevaluationFollowUpCandidateInvariantError(
                        "Existing follow-up requires "
                        "candidate_set_materialized=True."
                    )
                )

            expected_ids = self.source.evidence_ids

            if (
                self.candidates.evidence_ids
                != expected_ids
            ):
                raise (
                    RadarReevaluationFollowUpCandidateInvariantError(
                        "Candidate set must preserve "
                        "exact ADEL0.31 evidence IDs."
                    )
                )

            if self.evidence_ids != expected_ids:
                raise (
                    RadarReevaluationFollowUpCandidateInvariantError(
                        "Wrapper entries must "
                        "preserve exact evidence IDs."
                    )
                )

            if (
                len(self.entries)
                != len(self.source.entries)
            ):
                raise (
                    RadarReevaluationFollowUpCandidateInvariantError(
                        "Candidate wrapper entry "
                        "count mismatch."
                    )
                )

            expected_created = bool(
                expected_ids
            )

            if (
                self.followup_candidate_created
                is not expected_created
            ):
                raise (
                    RadarReevaluationFollowUpCandidateInvariantError(
                        "followup_candidate_created "
                        "must match candidate count."
                    )
                )

            if (
                self.query_preparation_performed
                is not expected_created
            ):
                raise (
                    RadarReevaluationFollowUpCandidateInvariantError(
                        "query preparation flag must "
                        "match candidate count."
                    )
                )

            for index, entry in enumerate(
                self.entries
            ):
                if not isinstance(
                    entry,
                    RadarReevaluationFollowUpCandidateEntry,
                ):
                    raise TypeError(
                        "entries must contain "
                        "RadarReevaluationFollowUpCandidateEntry."
                    )

                if (
                    entry.source_entry
                    is not self.source.entries[index]
                ):
                    raise (
                        RadarReevaluationFollowUpCandidateInvariantError(
                            "Exact ADEL0.31 source "
                            "identity must be "
                            "preserved."
                        )
                    )

                if (
                    entry.candidate
                    is not self.candidates.entries[index]
                ):
                    raise (
                        RadarReevaluationFollowUpCandidateInvariantError(
                            "Exact ADEL0.15 candidate "
                            "identity must be "
                            "preserved."
                        )
                    )

        if (
            self.verification_status
            != "UNVERIFIED_EXTERNAL"
        ):
            raise (
                RadarReevaluationFollowUpCandidateInvariantError(
                    "ADEL0.32 result must remain "
                    "UNVERIFIED_EXTERNAL."
                )
            )

        required_false = (
            "research_request_draft_created",
            "new_task_id_bound",
            "research_request_created",
            "provider_selected",
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
            "skill_creation_requested",
        )

        for name in required_false:
            if getattr(
                self,
                name,
            ) is not False:
                raise (
                    RadarReevaluationFollowUpCandidateInvariantError(
                        "Candidate result cannot "
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
    def queries(
        self,
    ) -> tuple[str, ...]:
        return tuple(
            entry.query
            for entry in self.entries
        )

    @property
    def capabilities(
        self,
    ) -> tuple[
        ResearchCapability,
        ...
    ]:
        return tuple(
            entry.capability
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


class GovernedRadarReevaluationFollowUpCandidate:
    """
    ADEL0.32 governed re-evaluation follow-up
    candidate boundary.

    It reuses the passive ADEL0.15
    GovernedRadarFollowUpCandidateBuilder.build()
    primitive.

    A candidate describes what external evidence
    could be searched for. Its SEARCH query is
    data only.

    QUERY PREPARED != RESEARCH REQUEST.

    CANDIDATE != RESEARCH REQUEST DRAFT.
    CANDIDATE != NEW TASK ID BINDING.
    CANDIDATE != RESEARCH REQUEST.
    CANDIDATE != PROVIDER SELECTION.
    CANDIDATE != ROUTING.
    CANDIDATE != TOOL EXECUTION.
    CANDIDATE != NETWORK.
    CANDIDATE != MISSION TRANSITION.
    CANDIDATE != RX_ACTIVE.
    CANDIDATE != PERSISTENCE.
    CANDIDATE != AUTHORIZATION.
    CANDIDATE != TRUTH.

    Existing origin task lineage may be observed
    through the wrapper but no new task identity
    is bound at this boundary.
    """

    @staticmethod
    def build(
        source: RadarReevaluationEvidenceFollowUpResult,
    ) -> RadarReevaluationFollowUpCandidateResult:
        if not isinstance(
            source,
            RadarReevaluationEvidenceFollowUpResult,
        ):
            raise TypeError(
                "source must be "
                "RadarReevaluationEvidenceFollowUpResult."
            )

        if source.followup is None:
            return (
                RadarReevaluationFollowUpCandidateResult(
                    source=source,
                    candidates=None,
                    entries=(),
                    candidate_set_materialized=False,
                    followup_candidate_created=False,
                    query_preparation_performed=False,
                )
            )

        candidates = (
            GovernedRadarFollowUpCandidateBuilder
            .build(
                source.followup
            )
        )

        entries = tuple(
            RadarReevaluationFollowUpCandidateEntry(
                source_entry=source_entry,
                candidate=candidate,
            )
            for source_entry, candidate
            in zip(
                source.entries,
                candidates.entries,
                strict=True,
            )
        )

        return (
            RadarReevaluationFollowUpCandidateResult(
                source=source,
                candidates=candidates,
                entries=entries,
                candidate_set_materialized=True,
                followup_candidate_created=bool(
                    entries
                ),
                query_preparation_performed=bool(
                    entries
                ),
            )
        )


__all__ = [
    "GovernedRadarReevaluationFollowUpCandidate",
    "RadarReevaluationFollowUpCandidateEntry",
    "RadarReevaluationFollowUpCandidateInvariantError",
    "RadarReevaluationFollowUpCandidateResult",
]
