from __future__ import annotations

from dataclasses import dataclass

from .radar_decision_envelope import (
    RadarDecisionEnvelope,
    RadarDecisionPolicy,
    RadarDisposition,
)
from .radar_portfolio import (
    RadarPortfolioResult,
)
from .technology_radar import (
    RadarFactors,
)


class RadarReviewPacketInvariantError(
    ValueError
):
    pass


@dataclass(
    frozen=True,
    slots=True,
)
class RadarFactorSnapshot:
    novelty: float
    source_quality: float
    relevance_to_maestro: float
    expected_capability_gain: float
    reproducibility: float
    integration_cost: float
    security_risk: float

    @classmethod
    def from_factors(
        cls,
        factors: RadarFactors,
    ) -> "RadarFactorSnapshot":
        if not isinstance(
            factors,
            RadarFactors,
        ):
            raise TypeError(
                "factors must be RadarFactors."
            )

        return cls(
            novelty=factors.novelty,
            source_quality=(
                factors.source_quality
            ),
            relevance_to_maestro=(
                factors.relevance_to_maestro
            ),
            expected_capability_gain=(
                factors.expected_capability_gain
            ),
            reproducibility=(
                factors.reproducibility
            ),
            integration_cost=(
                factors.integration_cost
            ),
            security_risk=(
                factors.security_risk
            ),
        )


@dataclass(
    frozen=True,
    slots=True,
)
class RadarReviewEntry:
    rank: int
    evidence_id: str
    source_ref: str
    claim: str
    disposition: RadarDisposition
    priority_score: float
    factors: RadarFactorSnapshot
    rationale: str
    verification_status: str = (
        "UNVERIFIED_EXTERNAL"
    )
    system_truth_asserted: bool = False

    def __post_init__(
        self,
    ) -> None:
        if (
            not isinstance(
                self.rank,
                int,
            )
            or isinstance(
                self.rank,
                bool,
            )
            or self.rank < 1
        ):
            raise RadarReviewPacketInvariantError(
                "rank must be a positive integer."
            )

        for name in (
            "evidence_id",
            "source_ref",
            "claim",
            "rationale",
        ):
            value = getattr(
                self,
                name,
            )

            if (
                not isinstance(
                    value,
                    str,
                )
                or not value
            ):
                raise RadarReviewPacketInvariantError(
                    f"{name} must be non-empty."
                )

        if not isinstance(
            self.disposition,
            RadarDisposition,
        ):
            raise TypeError(
                "disposition must be "
                "RadarDisposition."
            )

        if not isinstance(
            self.factors,
            RadarFactorSnapshot,
        ):
            raise TypeError(
                "factors must be "
                "RadarFactorSnapshot."
            )

        if (
            self.verification_status
            != "UNVERIFIED_EXTERNAL"
        ):
            raise RadarReviewPacketInvariantError(
                "Review packet must remain "
                "UNVERIFIED_EXTERNAL."
            )

        if (
            self.system_truth_asserted
            is not False
        ):
            raise RadarReviewPacketInvariantError(
                "Review packet cannot assert "
                "system truth."
            )


@dataclass(
    frozen=True,
    slots=True,
)
class RadarReviewPacket:
    policy: RadarDecisionPolicy
    entries: tuple[
        RadarReviewEntry,
        ...
    ]

    def __post_init__(
        self,
    ) -> None:
        if not isinstance(
            self.policy,
            RadarDecisionPolicy,
        ):
            raise TypeError(
                "policy must be "
                "RadarDecisionPolicy."
            )

        ids = tuple(
            entry.evidence_id
            for entry in self.entries
        )

        if len(ids) != len(set(ids)):
            raise RadarReviewPacketInvariantError(
                "Review packet requires "
                "unique evidence IDs."
            )

        expected_ranks = tuple(
            range(
                1,
                len(self.entries) + 1,
            )
        )

        actual_ranks = tuple(
            entry.rank
            for entry in self.entries
        )

        if actual_ranks != expected_ranks:
            raise RadarReviewPacketInvariantError(
                "Review packet ranks must be "
                "contiguous and ordered."
            )

        for entry in self.entries:
            if not isinstance(
                entry,
                RadarReviewEntry,
            ):
                raise TypeError(
                    "entries must contain "
                    "RadarReviewEntry objects."
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


class GovernedRadarReviewPacket:
    """
    Pure ADEL0.11 explanation layer.

    It joins:
      ADEL0.9 portfolio evaluations,
      ADEL0.10 decision envelope,
      ADEL0.10 explicit decision policy.

    It exposes the seven already-computed radar
    factors and a deterministic explanation for
    each passive research disposition.

    It computes no new priority score.

    It performs no network access, verification,
    learning, promotion, authorization,
    activation, execution, persistence, security
    scanning, skill creation, or truth assertion.
    """

    @staticmethod
    def _expected_disposition(
        score: float,
        policy: RadarDecisionPolicy,
    ) -> RadarDisposition:
        if (
            score
            >= policy.review_min_priority
        ):
            return RadarDisposition.REVIEW

        if (
            score
            >= policy.investigate_min_priority
        ):
            return RadarDisposition.INVESTIGATE

        return RadarDisposition.OBSERVE

    @staticmethod
    def _rationale(
        score: float,
        disposition: RadarDisposition,
        policy: RadarDecisionPolicy,
    ) -> str:
        if (
            disposition
            is RadarDisposition.REVIEW
        ):
            return (
                "Priority score "
                f"{score!r} meets or exceeds "
                "review threshold "
                f"{policy.review_min_priority!r}."
            )

        if (
            disposition
            is RadarDisposition.INVESTIGATE
        ):
            return (
                "Priority score "
                f"{score!r} meets or exceeds "
                "investigate threshold "
                f"{policy.investigate_min_priority!r} "
                "and remains below review threshold "
                f"{policy.review_min_priority!r}."
            )

        return (
            "Priority score "
            f"{score!r} remains below "
            "investigate threshold "
            f"{policy.investigate_min_priority!r}."
        )

    @classmethod
    def build(
        cls,
        portfolio: RadarPortfolioResult,
        envelope: RadarDecisionEnvelope,
        *,
        policy: RadarDecisionPolicy,
    ) -> RadarReviewPacket:
        if not isinstance(
            portfolio,
            RadarPortfolioResult,
        ):
            raise TypeError(
                "portfolio must be "
                "RadarPortfolioResult."
            )

        if not isinstance(
            envelope,
            RadarDecisionEnvelope,
        ):
            raise TypeError(
                "envelope must be "
                "RadarDecisionEnvelope."
            )

        if not isinstance(
            policy,
            RadarDecisionPolicy,
        ):
            raise TypeError(
                "policy must be "
                "RadarDecisionPolicy."
            )

        ranked_ids = tuple(
            observation.evidence_id
            for observation
            in portfolio.ranked_observations
        )

        if (
            envelope.evidence_ids
            != ranked_ids
        ):
            raise RadarReviewPacketInvariantError(
                "Decision envelope must match "
                "portfolio ranking exactly."
            )

        evaluations = {
            evaluation.evidence_id: evaluation
            for evaluation
            in portfolio.evaluations
        }

        entries: list[
            RadarReviewEntry
        ] = []

        for decision in envelope.entries:
            evaluation = evaluations.get(
                decision.evidence_id
            )

            if evaluation is None:
                raise RadarReviewPacketInvariantError(
                    "Missing evaluation for "
                    "decision evidence ID."
                )

            observation = (
                evaluation.observation
            )

            if (
                decision.priority_score
                != observation.priority_score
            ):
                raise RadarReviewPacketInvariantError(
                    "Decision priority score "
                    "does not match observation."
                )

            expected = (
                cls._expected_disposition(
                    observation.priority_score,
                    policy,
                )
            )

            if (
                decision.disposition
                is not expected
            ):
                raise RadarReviewPacketInvariantError(
                    "Decision disposition does "
                    "not match supplied policy."
                )

            if (
                observation.verification_status
                != "UNVERIFIED_EXTERNAL"
            ):
                raise RadarReviewPacketInvariantError(
                    "Review packet accepts "
                    "UNVERIFIED_EXTERNAL "
                    "observations only."
                )

            if (
                observation.system_truth_asserted
                is not False
            ):
                raise RadarReviewPacketInvariantError(
                    "Review packet cannot consume "
                    "system-truth observations."
                )

            entries.append(
                RadarReviewEntry(
                    rank=decision.rank,
                    evidence_id=(
                        observation.evidence_id
                    ),
                    source_ref=(
                        observation.source_ref
                    ),
                    claim=observation.claim,
                    disposition=(
                        decision.disposition
                    ),
                    priority_score=(
                        observation.priority_score
                    ),
                    factors=(
                        RadarFactorSnapshot
                        .from_factors(
                            observation.factors
                        )
                    ),
                    rationale=cls._rationale(
                        observation.priority_score,
                        decision.disposition,
                        policy,
                    ),
                )
            )

        return RadarReviewPacket(
            policy=policy,
            entries=tuple(entries),
        )


__all__ = [
    "GovernedRadarReviewPacket",
    "RadarFactorSnapshot",
    "RadarReviewEntry",
    "RadarReviewPacket",
    "RadarReviewPacketInvariantError",
]
