from __future__ import annotations

from dataclasses import dataclass

from .radar_portfolio import (
    RadarPortfolioResult,
)
from .radar_research_reevaluation_start import (
    RadarReevaluationStartEntry,
    RadarReevaluationStartResult,
)
from .technology_radar import (
    RadarObservation,
    TechnologyRadar,
)


class RadarReevaluationPortfolioReintegrationInvariantError(
    ValueError
):
    pass


@dataclass(
    frozen=True,
    slots=True,
)
class RadarReevaluationPortfolioEntry:
    source_entry: RadarReevaluationStartEntry

    ranked_observation: RadarObservation

    portfolio_rank: int

    portfolio_reintegrated: bool = True
    ranking_created: bool = True

    second_radar_evaluation: bool = False

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
            RadarReevaluationStartEntry,
        ):
            raise TypeError(
                "source_entry must be "
                "RadarReevaluationStartEntry."
            )

        if not isinstance(
            self.ranked_observation,
            RadarObservation,
        ):
            raise TypeError(
                "ranked_observation must be "
                "RadarObservation."
            )

        if (
            not isinstance(
                self.portfolio_rank,
                int,
            )
            or isinstance(
                self.portfolio_rank,
                bool,
            )
            or self.portfolio_rank < 1
        ):
            raise (
                RadarReevaluationPortfolioReintegrationInvariantError(
                    "portfolio_rank must be a "
                    "positive integer."
                )
            )

        source = self.source_entry

        if (
            source.reevaluation_authorized
            is not True
        ):
            raise (
                RadarReevaluationPortfolioReintegrationInvariantError(
                    "Portfolio reintegration "
                    "requires authorized "
                    "re-evaluation."
                )
            )

        if source.cycle_started is not True:
            raise (
                RadarReevaluationPortfolioReintegrationInvariantError(
                    "Portfolio reintegration "
                    "requires a started cycle."
                )
            )

        if source.radar_evaluated is not True:
            raise (
                RadarReevaluationPortfolioReintegrationInvariantError(
                    "Portfolio reintegration "
                    "requires Radar evaluation."
                )
            )

        if source.portfolio_created is not False:
            raise (
                RadarReevaluationPortfolioReintegrationInvariantError(
                    "ADEL0.25 source must not "
                    "already contain a portfolio."
                )
            )

        if (
            self.ranked_observation
            is not source.evaluation.observation
        ):
            raise (
                RadarReevaluationPortfolioReintegrationInvariantError(
                    "Ranking must reuse the exact "
                    "ADEL0.25 RadarObservation."
                )
            )

        evidence = source.evidence

        if (
            self.ranked_observation.evidence_id
            != evidence.evidence_id
        ):
            raise (
                RadarReevaluationPortfolioReintegrationInvariantError(
                    "Ranked Evidence identity "
                    "mismatch."
                )
            )

        if (
            self.ranked_observation.task_id
            != evidence.task_id
        ):
            raise (
                RadarReevaluationPortfolioReintegrationInvariantError(
                    "Ranked task lineage mismatch."
                )
            )

        if (
            self.ranked_observation.source_ref
            != evidence.source_ref
        ):
            raise (
                RadarReevaluationPortfolioReintegrationInvariantError(
                    "Ranked source lineage "
                    "mismatch."
                )
            )

        if (
            self.ranked_observation.claim
            != evidence.claim
        ):
            raise (
                RadarReevaluationPortfolioReintegrationInvariantError(
                    "Ranked claim lineage mismatch."
                )
            )

        if (
            self.ranked_observation
            .verification_status
            != "UNVERIFIED_EXTERNAL"
        ):
            raise (
                RadarReevaluationPortfolioReintegrationInvariantError(
                    "Portfolio ranking must remain "
                    "UNVERIFIED_EXTERNAL."
                )
            )

        if (
            self.ranked_observation
            .system_truth_asserted
            is not False
        ):
            raise (
                RadarReevaluationPortfolioReintegrationInvariantError(
                    "Portfolio ranking cannot "
                    "assert system truth."
                )
            )

        if (
            self.verification_status
            != "UNVERIFIED_EXTERNAL"
        ):
            raise (
                RadarReevaluationPortfolioReintegrationInvariantError(
                    "Portfolio boundary must remain "
                    "UNVERIFIED_EXTERNAL."
                )
            )

        if self.system_truth_asserted is not False:
            raise (
                RadarReevaluationPortfolioReintegrationInvariantError(
                    "Portfolio boundary cannot "
                    "assert system truth."
                )
            )

        if self.portfolio_reintegrated is not True:
            raise (
                RadarReevaluationPortfolioReintegrationInvariantError(
                    "portfolio_reintegrated must "
                    "be True."
                )
            )

        if self.ranking_created is not True:
            raise (
                RadarReevaluationPortfolioReintegrationInvariantError(
                    "ranking_created must be True."
                )
            )

        required_false = (
            "second_radar_evaluation",
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
                    RadarReevaluationPortfolioReintegrationInvariantError(
                        "Portfolio reintegration "
                        f"cannot assert {name}."
                    )
                )

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
    def cycle_number(
        self,
    ) -> int:
        return self.source_entry.cycle_number

    @property
    def evaluation(
        self,
    ):
        return self.source_entry.evaluation

    @property
    def evidence(
        self,
    ):
        return self.source_entry.evidence

    @property
    def priority_score(
        self,
    ) -> float:
        return (
            self.ranked_observation
            .priority_score
        )


@dataclass(
    frozen=True,
    slots=True,
)
class RadarReevaluationPortfolioReintegrationResult:
    source: RadarReevaluationStartResult

    portfolio: RadarPortfolioResult

    entries: tuple[
        RadarReevaluationPortfolioEntry,
        ...
    ]

    portfolio_reintegrated: bool = True
    ranking_created: bool = True

    second_radar_evaluation: bool = False

    decision_envelope_created: bool = False
    review_packet_created: bool = False
    followup_created: bool = False
    new_research_request_created: bool = False

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
            RadarReevaluationStartResult,
        ):
            raise TypeError(
                "source must be "
                "RadarReevaluationStartResult."
            )

        if not isinstance(
            self.portfolio,
            RadarPortfolioResult,
        ):
            raise TypeError(
                "portfolio must be "
                "RadarPortfolioResult."
            )

        for entry in self.entries:
            if not isinstance(
                entry,
                RadarReevaluationPortfolioEntry,
            ):
                raise TypeError(
                    "entries must contain "
                    "RadarReevaluationPortfolioEntry."
                )

        source_evaluations = tuple(
            entry.evaluation
            for entry in self.source.entries
        )

        if (
            len(source_evaluations)
            != len(self.portfolio.evaluations)
        ):
            raise (
                RadarReevaluationPortfolioReintegrationInvariantError(
                    "Portfolio evaluation count "
                    "must match ADEL0.25."
                )
            )

        for source_evaluation, portfolio_evaluation in zip(
            source_evaluations,
            self.portfolio.evaluations,
            strict=True,
        ):
            if (
                portfolio_evaluation
                is not source_evaluation
            ):
                raise (
                    RadarReevaluationPortfolioReintegrationInvariantError(
                        "Portfolio must reuse exact "
                        "ADEL0.25 evaluation objects."
                    )
                )

        source_by_id = {
            entry.evidence_id: entry
            for entry in self.source.entries
        }

        ranked_ids = (
            self.portfolio
            .ranked_evidence_ids
        )

        if (
            set(ranked_ids)
            != set(source_by_id)
        ):
            raise (
                RadarReevaluationPortfolioReintegrationInvariantError(
                    "Portfolio ranking must cover "
                    "exactly ADEL0.25 Evidence IDs."
                )
            )

        entry_ids = tuple(
            entry.evidence_id
            for entry in self.entries
        )

        if entry_ids != ranked_ids:
            raise (
                RadarReevaluationPortfolioReintegrationInvariantError(
                    "Reintegration entries must "
                    "follow exact portfolio rank."
                )
            )

        ranks = tuple(
            entry.portfolio_rank
            for entry in self.entries
        )

        if ranks != tuple(
            range(
                1,
                len(self.entries) + 1,
            )
        ):
            raise (
                RadarReevaluationPortfolioReintegrationInvariantError(
                    "Portfolio ranks must be "
                    "contiguous and one-based."
                )
            )

        for index, entry in enumerate(
            self.entries
        ):
            ranked = (
                self.portfolio
                .ranked_observations[index]
            )

            if (
                entry.ranked_observation
                is not ranked
            ):
                raise (
                    RadarReevaluationPortfolioReintegrationInvariantError(
                        "Entry must preserve exact "
                        "ranked observation identity."
                    )
                )

            source_entry = source_by_id[
                ranked.evidence_id
            ]

            if entry.source_entry is not source_entry:
                raise (
                    RadarReevaluationPortfolioReintegrationInvariantError(
                        "Entry must preserve exact "
                        "ADEL0.25 source identity."
                    )
                )

            if (
                ranked
                is not source_entry
                .evaluation
                .observation
            ):
                raise (
                    RadarReevaluationPortfolioReintegrationInvariantError(
                        "Ranking must reuse exact "
                        "ADEL0.25 observations."
                    )
                )

        if self.portfolio_reintegrated is not True:
            raise (
                RadarReevaluationPortfolioReintegrationInvariantError(
                    "portfolio_reintegrated must "
                    "be True."
                )
            )

        if self.ranking_created is not True:
            raise (
                RadarReevaluationPortfolioReintegrationInvariantError(
                    "ranking_created must be True."
                )
            )

        required_false = (
            "second_radar_evaluation",
            "decision_envelope_created",
            "review_packet_created",
            "followup_created",
            "new_research_request_created",
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
                    RadarReevaluationPortfolioReintegrationInvariantError(
                        "Portfolio result cannot "
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
    def ranked_evidence_ids(
        self,
    ) -> tuple[str, ...]:
        return tuple(
            entry.evidence_id
            for entry in self.entries
        )

    @property
    def portfolio_ranks(
        self,
    ) -> tuple[int, ...]:
        return tuple(
            entry.portfolio_rank
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
    ):
        return self.portfolio.evaluations

    @property
    def ranked_observations(
        self,
    ):
        return (
            self.portfolio
            .ranked_observations
        )


class GovernedRadarReevaluationPortfolioReintegrator:
    """
    ADEL0.26 governed portfolio reintegration.

    This boundary consumes ADEL0.25 Radar
    evaluations that have already occurred.

    It MUST NOT re-run the ADEL0.8 evaluation
    pipeline.

    It reuses the exact RadarEvaluationResult
    objects and their exact RadarObservation
    objects, ranks those existing observations
    once through TechnologyRadar.rank(), and
    constructs RadarPortfolioResult directly.

    It performs no second Radar evaluation,
    decision-envelope creation, review,
    follow-up, ResearchRequest creation,
    network access, tool execution,
    persistence, mission transition, truth
    assertion, AY validation, EX authorization,
    learning, promotion, activation, execution
    authority, or skill creation.

    PORTFOLIO REINTEGRATED != DECISION CREATED.
    RANKED != DECIDED.
    RANKED != REVIEWED.
    RANKED != FOLLOW-UP.
    RANKED != NEW RESEARCH.
    RANKED != TRUTH.
    """

    @staticmethod
    def reintegrate(
        start: RadarReevaluationStartResult,
    ) -> RadarReevaluationPortfolioReintegrationResult:
        if not isinstance(
            start,
            RadarReevaluationStartResult,
        ):
            raise TypeError(
                "start must be "
                "RadarReevaluationStartResult."
            )

        evaluations = tuple(
            entry.evaluation
            for entry in start.entries
        )

        observations = tuple(
            evaluation.observation
            for evaluation in evaluations
        )

        radar = TechnologyRadar()

        ranked = tuple(
            radar.rank(
                observations
            )
        )

        portfolio = RadarPortfolioResult(
            evaluations=evaluations,
            ranked_observations=ranked,
        )

        source_by_id = {
            entry.evidence_id: entry
            for entry in start.entries
        }

        entries = tuple(
            RadarReevaluationPortfolioEntry(
                source_entry=source_by_id[
                    observation.evidence_id
                ],
                ranked_observation=observation,
                portfolio_rank=index,
            )
            for index, observation
            in enumerate(
                ranked,
                start=1,
            )
        )

        return (
            RadarReevaluationPortfolioReintegrationResult(
                source=start,
                portfolio=portfolio,
                entries=entries,
            )
        )


__all__ = [
    "GovernedRadarReevaluationPortfolioReintegrator",
    "RadarReevaluationPortfolioEntry",
    "RadarReevaluationPortfolioReintegrationInvariantError",
    "RadarReevaluationPortfolioReintegrationResult",
]
