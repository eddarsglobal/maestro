from __future__ import annotations

from dataclasses import dataclass

from .capability_integration import (
    CapabilityIntegrationEvaluation,
)
from .novelty_relevance import (
    NoveltyRelevanceEvaluation,
)
from .security_risk import (
    SecurityRiskEvaluation,
)
from .source_quality_reproducibility import (
    SourceQualityReproducibilityEvaluation,
)
from .technology_radar import (
    RadarFactors,
)


class RadarFactorCompositionInvariantError(
    ValueError
):
    pass


@dataclass(
    frozen=True,
    slots=True,
)
class RadarFactorComposition:
    novelty_relevance: NoveltyRelevanceEvaluation
    capability_integration: CapabilityIntegrationEvaluation
    source_quality_reproducibility: (
        SourceQualityReproducibilityEvaluation
    )
    security_risk: SecurityRiskEvaluation

    def __post_init__(
        self,
    ) -> None:
        evaluations = (
            self.novelty_relevance,
            self.capability_integration,
            self.source_quality_reproducibility,
            self.security_risk,
        )

        evidence_ids = {
            evaluation.evidence_id
            for evaluation in evaluations
        }

        if len(evidence_ids) != 1:
            raise RadarFactorCompositionInvariantError(
                "All composed evaluations must "
                "refer to the same evidence_id."
            )

        for evaluation in evaluations:
            if (
                evaluation.verification_status
                != "UNVERIFIED_EXTERNAL"
            ):
                raise RadarFactorCompositionInvariantError(
                    "ADEL0.7 accepts "
                    "UNVERIFIED_EXTERNAL evaluations only."
                )

            if evaluation.system_truth_asserted is not False:
                raise RadarFactorCompositionInvariantError(
                    "ADEL0.7 cannot compose an "
                    "evaluation asserting system truth."
                )

    @property
    def evidence_id(
        self,
    ) -> str:
        return (
            self.novelty_relevance.evidence_id
        )

    @property
    def complete(
        self,
    ) -> bool:
        return all(
            (
                self.novelty_relevance.relevance_to_maestro
                is not None,
                self.capability_integration
                .expected_capability_gain
                is not None,
                self.capability_integration
                .integration_cost
                is not None,
                self.source_quality_reproducibility
                .source_quality
                is not None,
                self.source_quality_reproducibility
                .reproducibility
                is not None,
                self.security_risk.security_risk
                is not None,
            )
        )

    def to_factors(
        self,
    ) -> RadarFactors:
        if not self.complete:
            raise RadarFactorCompositionInvariantError(
                "Incomplete evaluation set cannot "
                "be composed into RadarFactors."
            )

        relevance = (
            self.novelty_relevance
            .relevance_to_maestro
        )

        capability_gain = (
            self.capability_integration
            .expected_capability_gain
        )

        integration_cost = (
            self.capability_integration
            .integration_cost
        )

        source_quality = (
            self.source_quality_reproducibility
            .source_quality
        )

        reproducibility = (
            self.source_quality_reproducibility
            .reproducibility
        )

        security_risk = (
            self.security_risk
            .security_risk
        )

        if relevance is None:
            raise RadarFactorCompositionInvariantError(
                "relevance_to_maestro is unknown."
            )

        if capability_gain is None:
            raise RadarFactorCompositionInvariantError(
                "expected_capability_gain is unknown."
            )

        if integration_cost is None:
            raise RadarFactorCompositionInvariantError(
                "integration_cost is unknown."
            )

        if source_quality is None:
            raise RadarFactorCompositionInvariantError(
                "source_quality is unknown."
            )

        if reproducibility is None:
            raise RadarFactorCompositionInvariantError(
                "reproducibility is unknown."
            )

        if security_risk is None:
            raise RadarFactorCompositionInvariantError(
                "security_risk is unknown."
            )

        return RadarFactors(
            novelty=(
                self.novelty_relevance
                .novelty
            ),
            source_quality=source_quality,
            relevance_to_maestro=relevance,
            expected_capability_gain=(
                capability_gain
            ),
            reproducibility=reproducibility,
            integration_cost=integration_cost,
            security_risk=security_risk,
        )


class RadarFactorComposer:
    """
    Pure ADEL0.7 composition layer.

    It composes already-produced governed
    evaluation results into one RadarFactors
    value.

    It does not evaluate Evidence itself.

    It performs no network access, learning,
    persistence, promotion, activation,
    security scanning, verification,
    skill creation, execution, or authority
    escalation.
    """

    @staticmethod
    def compose(
        *,
        novelty_relevance: (
            NoveltyRelevanceEvaluation
        ),
        capability_integration: (
            CapabilityIntegrationEvaluation
        ),
        source_quality_reproducibility: (
            SourceQualityReproducibilityEvaluation
        ),
        security_risk: SecurityRiskEvaluation,
    ) -> RadarFactors:
        if not isinstance(
            novelty_relevance,
            NoveltyRelevanceEvaluation,
        ):
            raise TypeError(
                "novelty_relevance must be "
                "NoveltyRelevanceEvaluation."
            )

        if not isinstance(
            capability_integration,
            CapabilityIntegrationEvaluation,
        ):
            raise TypeError(
                "capability_integration must be "
                "CapabilityIntegrationEvaluation."
            )

        if not isinstance(
            source_quality_reproducibility,
            SourceQualityReproducibilityEvaluation,
        ):
            raise TypeError(
                "source_quality_reproducibility must be "
                "SourceQualityReproducibilityEvaluation."
            )

        if not isinstance(
            security_risk,
            SecurityRiskEvaluation,
        ):
            raise TypeError(
                "security_risk must be "
                "SecurityRiskEvaluation."
            )

        composition = RadarFactorComposition(
            novelty_relevance=novelty_relevance,
            capability_integration=(
                capability_integration
            ),
            source_quality_reproducibility=(
                source_quality_reproducibility
            ),
            security_risk=security_risk,
        )

        return composition.to_factors()


__all__ = [
    "RadarFactorComposition",
    "RadarFactorComposer",
    "RadarFactorCompositionInvariantError",
]
