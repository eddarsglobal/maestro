from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from .radar_evaluation_pipeline import (
    GovernedRadarEvaluationPipeline,
    RadarEvaluationContext,
    RadarEvaluationResult,
)
from .radar_research_cycle_governance import (
    MAX_RADAR_FOLLOWUP_CYCLES,
    RadarFollowUpCycleGovernanceDisposition,
    RadarFollowUpCycleGovernanceEntry,
    RadarFollowUpCycleGovernanceResult,
)


class RadarReevaluationStartInvariantError(
    ValueError
):
    pass


@dataclass(
    frozen=True,
    slots=True,
)
class RadarReevaluationStartEntry:
    source_entry: (
        RadarFollowUpCycleGovernanceEntry
    )

    evaluation_context: RadarEvaluationContext

    evaluation: RadarEvaluationResult

    cycle_number: int

    reevaluation_authorized: bool = True
    cycle_started: bool = True
    radar_evaluated: bool = True

    portfolio_created: bool = False
    decision_envelope_created: bool = False
    review_packet_created: bool = False
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
            RadarFollowUpCycleGovernanceEntry,
        ):
            raise TypeError(
                "source_entry must be "
                "RadarFollowUpCycleGovernanceEntry."
            )

        if (
            self.source_entry.disposition
            is not RadarFollowUpCycleGovernanceDisposition
            .ADMIT_REEVALUATION
        ):
            raise (
                RadarReevaluationStartInvariantError(
                    "Re-evaluation start requires "
                    "ADMIT_REEVALUATION."
                )
            )

        if (
            self.source_entry
            .reevaluation_authorized
            is not True
        ):
            raise (
                RadarReevaluationStartInvariantError(
                    "Re-evaluation start requires "
                    "reevaluation_authorized=True."
                )
            )

        if (
            self.source_entry.context
            is None
        ):
            raise (
                RadarReevaluationStartInvariantError(
                    "Authorized re-evaluation "
                    "requires cycle context."
                )
            )

        if (
            self.source_entry.cycle_started
            is not False
        ):
            raise (
                RadarReevaluationStartInvariantError(
                    "Source cycle must not already "
                    "be started."
                )
            )

        if (
            self.source_entry.radar_evaluated
            is not False
        ):
            raise (
                RadarReevaluationStartInvariantError(
                    "Source must not already be "
                    "Radar-evaluated."
                )
            )

        if (
            type(self.evaluation_context)
            is not RadarEvaluationContext
        ):
            raise TypeError(
                "evaluation_context must be "
                "exactly RadarEvaluationContext."
            )

        if not isinstance(
            self.evaluation,
            RadarEvaluationResult,
        ):
            raise TypeError(
                "evaluation must be "
                "RadarEvaluationResult."
            )

        expected_cycle_number = (
            self.source_entry
            .context
            .completed_cycles
            + 1
        )

        if (
            self.cycle_number
            != expected_cycle_number
        ):
            raise (
                RadarReevaluationStartInvariantError(
                    "cycle_number must equal "
                    "completed_cycles + 1."
                )
            )

        if not (
            1
            <= self.cycle_number
            <= self.source_entry
            .policy
            .max_cycles
            <= MAX_RADAR_FOLLOWUP_CYCLES
        ):
            raise (
                RadarReevaluationStartInvariantError(
                    "Cycle number violates bounded "
                    "cycle governance."
                )
            )

        if (
            self.evaluation_context
            .known_claims
            != self.source_entry
            .context
            .known_claims
        ):
            raise (
                RadarReevaluationStartInvariantError(
                    "Re-evaluation known_claims "
                    "must exactly preserve the "
                    "ADEL0.24 convergence context."
                )
            )

        evidence = (
            self.source_entry.evidence
        )

        if (
            self.evaluation.evidence_id
            != evidence.evidence_id
        ):
            raise (
                RadarReevaluationStartInvariantError(
                    "Evaluation Evidence identity "
                    "mismatch."
                )
            )

        if (
            self.evaluation
            .observation
            .evidence_id
            != evidence.evidence_id
        ):
            raise (
                RadarReevaluationStartInvariantError(
                    "Observation Evidence identity "
                    "mismatch."
                )
            )

        if (
            self.evaluation
            .observation
            .task_id
            != evidence.task_id
        ):
            raise (
                RadarReevaluationStartInvariantError(
                    "Observation task lineage "
                    "mismatch."
                )
            )

        if (
            self.evaluation
            .observation
            .source_ref
            != evidence.source_ref
        ):
            raise (
                RadarReevaluationStartInvariantError(
                    "Observation source lineage "
                    "mismatch."
                )
            )

        if (
            self.evaluation
            .observation
            .claim
            != evidence.claim
        ):
            raise (
                RadarReevaluationStartInvariantError(
                    "Observation claim lineage "
                    "mismatch."
                )
            )

        if (
            self.source_entry.novelty
            is None
        ):
            raise (
                RadarReevaluationStartInvariantError(
                    "ADMIT_REEVALUATION requires "
                    "governance novelty."
                )
            )

        if (
            self.evaluation
            .novelty_relevance
            .novelty
            != self.source_entry.novelty
        ):
            raise (
                RadarReevaluationStartInvariantError(
                    "Radar novelty must match the "
                    "ADEL0.24 convergence novelty."
                )
            )

        if (
            self.evaluation
            .observation
            .verification_status
            != "UNVERIFIED_EXTERNAL"
        ):
            raise (
                RadarReevaluationStartInvariantError(
                    "Re-evaluation must remain "
                    "UNVERIFIED_EXTERNAL."
                )
            )

        if (
            self.evaluation
            .observation
            .system_truth_asserted
            is not False
        ):
            raise (
                RadarReevaluationStartInvariantError(
                    "Re-evaluation cannot assert "
                    "system truth."
                )
            )

        if (
            self.verification_status
            != "UNVERIFIED_EXTERNAL"
        ):
            raise (
                RadarReevaluationStartInvariantError(
                    "Start boundary must remain "
                    "UNVERIFIED_EXTERNAL."
                )
            )

        if self.system_truth_asserted is not False:
            raise (
                RadarReevaluationStartInvariantError(
                    "Start boundary cannot assert "
                    "system truth."
                )
            )

        required_true = (
            "reevaluation_authorized",
            "cycle_started",
            "radar_evaluated",
        )

        for name in required_true:
            if getattr(
                self,
                name,
            ) is not True:
                raise (
                    RadarReevaluationStartInvariantError(
                        "Re-evaluation start "
                        f"requires {name}=True."
                    )
                )

        required_false = (
            "portfolio_created",
            "decision_envelope_created",
            "review_packet_created",
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
                    RadarReevaluationStartInvariantError(
                        "Re-evaluation start cannot "
                        f"assert {name}."
                    )
                )

    @property
    def rank(
        self,
    ) -> int:
        return self.source_entry.rank

    @property
    def evidence_id(
        self,
    ) -> str:
        return self.source_entry.evidence_id

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
    def evidence(
        self,
    ):
        return self.source_entry.evidence


@dataclass(
    frozen=True,
    slots=True,
)
class RadarReevaluationStartResult:
    entries: tuple[
        RadarReevaluationStartEntry,
        ...
    ]

    def __post_init__(
        self,
    ) -> None:
        for entry in self.entries:
            if not isinstance(
                entry,
                RadarReevaluationStartEntry,
            ):
                raise TypeError(
                    "entries must contain "
                    "RadarReevaluationStartEntry."
                )

        ids = tuple(
            entry.evidence_id
            for entry in self.entries
        )

        if (
            len(ids)
            != len(set(ids))
        ):
            raise (
                RadarReevaluationStartInvariantError(
                    "Re-evaluation start requires "
                    "unique Evidence IDs."
                )
            )

        ranks = tuple(
            entry.rank
            for entry in self.entries
        )

        if ranks != tuple(sorted(ranks)):
            raise (
                RadarReevaluationStartInvariantError(
                    "Re-evaluation start must "
                    "preserve governance order."
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
    def cycle_numbers(
        self,
    ) -> tuple[int, ...]:
        return tuple(
            entry.cycle_number
            for entry in self.entries
        )

    @property
    def evaluations(
        self,
    ) -> tuple[
        RadarEvaluationResult,
        ...
    ]:
        return tuple(
            entry.evaluation
            for entry in self.entries
        )


class GovernedRadarReevaluationStarter:
    """
    ADEL0.25 governed Radar re-evaluation start.

    This boundary consumes only ADEL0.24 entries
    explicitly authorized with ADMIT_REEVALUATION.

    For every admitted Evidence it performs
    exactly one local governed ADEL0.8 Radar
    evaluation using an explicit
    RadarEvaluationContext.

    The caller must preserve the same
    known_claims already used by ADEL0.24 for
    semantic convergence.

    This boundary stops immediately after
    RadarEvaluationResult.

    It does NOT create a portfolio.
    It does NOT rank a portfolio.
    It does NOT create a DecisionEnvelope.
    It does NOT create Review packets.
    It does NOT request more evidence.
    It does NOT create ResearchRequest.
    It does NOT perform network access.
    It does NOT invoke tools.
    It does NOT persist.
    It does NOT transition mission state.
    It does NOT assert truth, AY validation,
    EX authorization, learning, promotion,
    activation, or execution authority.

    REEVALUATION AUTHORIZED != CYCLE STARTED.
    CYCLE STARTED != PORTFOLIO CREATED.
    RADAR EVALUATED != DECISION CREATED.
    RADAR EVALUATED != NEW RESEARCH.
    RADAR EVALUATED != TRUTH.
    """

    @staticmethod
    def start(
        governance: (
            RadarFollowUpCycleGovernanceResult
        ),
        *,
        contexts: Mapping[
            str,
            RadarEvaluationContext,
        ],
    ) -> RadarReevaluationStartResult:
        if not isinstance(
            governance,
            RadarFollowUpCycleGovernanceResult,
        ):
            raise TypeError(
                "governance must be "
                "RadarFollowUpCycleGovernanceResult."
            )

        if not isinstance(
            contexts,
            Mapping,
        ):
            raise TypeError(
                "contexts must be a mapping."
            )

        normalized: dict[
            str,
            RadarEvaluationContext,
        ] = {}

        for evidence_id, context in (
            contexts.items()
        ):
            if (
                not isinstance(
                    evidence_id,
                    str,
                )
                or not evidence_id.strip()
            ):
                raise (
                    RadarReevaluationStartInvariantError(
                        "Context Evidence IDs must "
                        "be non-empty strings."
                    )
                )

            if (
                type(context)
                is not RadarEvaluationContext
            ):
                raise TypeError(
                    "Re-evaluation contexts must "
                    "be exactly "
                    "RadarEvaluationContext."
                )

            normalized[
                evidence_id
            ] = context

        expected_ids = set(
            governance.admitted_evidence_ids
        )

        supplied_ids = set(
            normalized
        )

        if supplied_ids != expected_ids:
            missing = sorted(
                expected_ids
                - supplied_ids
            )

            extra = sorted(
                supplied_ids
                - expected_ids
            )

            raise (
                RadarReevaluationStartInvariantError(
                    "Re-evaluation contexts must "
                    "cover exactly "
                    "ADMIT_REEVALUATION Evidence "
                    "IDs; "
                    f"missing={missing}, "
                    f"extra={extra}."
                )
            )

        pipeline = (
            GovernedRadarEvaluationPipeline()
        )

        entries = []

        for source_entry in governance.entries:
            if (
                source_entry.disposition
                is not RadarFollowUpCycleGovernanceDisposition
                .ADMIT_REEVALUATION
            ):
                continue

            context = normalized[
                source_entry.evidence_id
            ]

            if (
                source_entry.context
                is None
            ):
                raise (
                    RadarReevaluationStartInvariantError(
                        "Admitted Evidence requires "
                        "cycle context."
                    )
                )

            if (
                context.known_claims
                != source_entry
                .context
                .known_claims
            ):
                raise (
                    RadarReevaluationStartInvariantError(
                        "Radar known_claims must "
                        "match ADEL0.24 context."
                    )
                )

            evaluation = (
                pipeline.evaluate(
                    source_entry.evidence,
                    context=context,
                )
            )

            entries.append(
                RadarReevaluationStartEntry(
                    source_entry=source_entry,
                    evaluation_context=context,
                    evaluation=evaluation,
                    cycle_number=(
                        source_entry
                        .context
                        .completed_cycles
                        + 1
                    ),
                )
            )

        return (
            RadarReevaluationStartResult(
                entries=tuple(entries)
            )
        )


__all__ = [
    "GovernedRadarReevaluationStarter",
    "RadarReevaluationStartEntry",
    "RadarReevaluationStartInvariantError",
    "RadarReevaluationStartResult",
]
