from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from maestro.models import Evidence

from .radar_evaluation_pipeline import (
    GovernedRadarEvaluationPipeline,
    RadarEvaluationContext,
    RadarEvaluationResult,
)
from .technology_radar import (
    RadarObservation,
    TechnologyRadar,
)


class RadarPortfolioInvariantError(
    ValueError
):
    pass


@dataclass(
    frozen=True,
    slots=True,
)
class RadarPortfolioEntry:
    evidence: Evidence
    context: RadarEvaluationContext

    def __post_init__(
        self,
    ) -> None:
        if not isinstance(
            self.evidence,
            Evidence,
        ):
            raise TypeError(
                "evidence must be Evidence."
            )

        if not isinstance(
            self.context,
            RadarEvaluationContext,
        ):
            raise TypeError(
                "context must be "
                "RadarEvaluationContext."
            )


@dataclass(
    frozen=True,
    slots=True,
)
class RadarPortfolioResult:
    evaluations: tuple[
        RadarEvaluationResult,
        ...
    ]
    ranked_observations: tuple[
        RadarObservation,
        ...
    ]

    def __post_init__(
        self,
    ) -> None:
        evaluation_ids = tuple(
            result.evidence_id
            for result in self.evaluations
        )

        ranked_ids = tuple(
            row.evidence_id
            for row in self.ranked_observations
        )

        if len(
            evaluation_ids
        ) != len(
            set(evaluation_ids)
        ):
            raise RadarPortfolioInvariantError(
                "Portfolio evaluations require "
                "unique evidence IDs."
            )

        if len(
            ranked_ids
        ) != len(
            set(ranked_ids)
        ):
            raise RadarPortfolioInvariantError(
                "Ranked observations require "
                "unique evidence IDs."
            )

        if set(
            evaluation_ids
        ) != set(
            ranked_ids
        ):
            raise RadarPortfolioInvariantError(
                "Ranked observations must cover "
                "exactly the evaluated evidence IDs."
            )

        for result in self.evaluations:
            if (
                result.observation
                .verification_status
                != "UNVERIFIED_EXTERNAL"
            ):
                raise RadarPortfolioInvariantError(
                    "Portfolio must preserve "
                    "UNVERIFIED_EXTERNAL."
                )

            if (
                result.observation
                .system_truth_asserted
                is not False
            ):
                raise RadarPortfolioInvariantError(
                    "Portfolio cannot assert "
                    "system truth."
                )

    @property
    def size(
        self,
    ) -> int:
        return len(
            self.evaluations
        )

    @property
    def ranked_evidence_ids(
        self,
    ) -> tuple[str, ...]:
        return tuple(
            row.evidence_id
            for row in self.ranked_observations
        )


class GovernedRadarPortfolio:
    """
    Pure ADEL0.9 portfolio orchestration.

    It evaluates multiple already-governed
    Evidence objects through the ADEL0.8
    pipeline and ranks their resulting
    RadarObservation objects through the
    existing TechnologyRadar.rank method.

    It introduces no scoring formula,
    verification authority, authorization,
    activation, learning, promotion,
    persistence, network access, tool
    execution, security scanning, or
    skill creation.
    """

    def __init__(
        self,
        *,
        pipeline: (
            GovernedRadarEvaluationPipeline
            | None
        ) = None,
        radar: TechnologyRadar | None = None,
    ) -> None:
        self._radar = (
            radar
            if radar is not None
            else TechnologyRadar()
        )

        if not isinstance(
            self._radar,
            TechnologyRadar,
        ):
            raise TypeError(
                "radar must be TechnologyRadar."
            )

        self._pipeline = (
            pipeline
            if pipeline is not None
            else GovernedRadarEvaluationPipeline(
                radar=self._radar
            )
        )

        if not isinstance(
            self._pipeline,
            GovernedRadarEvaluationPipeline,
        ):
            raise TypeError(
                "pipeline must be "
                "GovernedRadarEvaluationPipeline."
            )

    def evaluate(
        self,
        entries: Iterable[
            RadarPortfolioEntry
        ],
    ) -> RadarPortfolioResult:
        if isinstance(
            entries,
            (str, bytes),
        ):
            raise TypeError(
                "entries must be an iterable "
                "of RadarPortfolioEntry objects."
            )

        rows = tuple(
            entries
        )

        for entry in rows:
            if not isinstance(
                entry,
                RadarPortfolioEntry,
            ):
                raise TypeError(
                    "entries must contain "
                    "RadarPortfolioEntry objects."
                )

        ids = tuple(
            entry.evidence.evidence_id
            for entry in rows
        )

        if len(ids) != len(set(ids)):
            raise RadarPortfolioInvariantError(
                "Portfolio requires unique "
                "evidence IDs before evaluation."
            )

        evaluations = tuple(
            self._pipeline.evaluate(
                entry.evidence,
                context=entry.context,
            )
            for entry in rows
        )

        observations = tuple(
            result.observation
            for result in evaluations
        )

        ranked = tuple(
            self._radar.rank(
                observations
            )
        )

        return RadarPortfolioResult(
            evaluations=evaluations,
            ranked_observations=ranked,
        )


__all__ = [
    "GovernedRadarPortfolio",
    "RadarPortfolioEntry",
    "RadarPortfolioInvariantError",
    "RadarPortfolioResult",
]
