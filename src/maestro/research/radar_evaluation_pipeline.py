from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from maestro.models import Evidence

from .capability_integration import (
    CapabilityIntegrationEvaluation,
    CapabilityIntegrationEvaluator,
)
from .novelty_relevance import (
    NoveltyRelevanceEvaluation,
    NoveltyRelevanceEvaluator,
)
from .radar_factor_composition import (
    RadarFactorComposer,
)
from .security_risk import (
    SecurityRiskEvaluation,
    SecurityRiskEvaluator,
)
from .source_quality_reproducibility import (
    SourceQualityReproducibilityEvaluation,
    SourceQualityReproducibilityEvaluator,
)
from .technology_radar import (
    RadarFactors,
    RadarObservation,
    TechnologyRadar,
)


@dataclass(
    frozen=True,
    slots=True,
)
class RadarEvaluationContext:
    known_claims: tuple[str, ...] = ()
    relevance_terms: tuple[str, ...] = ()
    capability_terms: tuple[str, ...] = ()
    existing_capabilities: tuple[str, ...] = ()
    integration_requirements: tuple[str, ...] = ()
    available_integration_support: tuple[str, ...] = ()
    independent_sources: tuple[str, ...] = ()
    reproduction_requirements: tuple[str, ...] = ()
    reproduction_support: tuple[str, ...] = ()
    risk_signals: tuple[str, ...] = ()
    mitigations: tuple[str, ...] = ()

    def __post_init__(
        self,
    ) -> None:
        for name in (
            "known_claims",
            "relevance_terms",
            "capability_terms",
            "existing_capabilities",
            "integration_requirements",
            "available_integration_support",
            "independent_sources",
            "reproduction_requirements",
            "reproduction_support",
            "risk_signals",
            "mitigations",
        ):
            values = getattr(
                self,
                name,
            )

            if not isinstance(
                values,
                tuple,
            ):
                raise TypeError(
                    f"{name} must be a tuple."
                )

            for value in values:
                if not isinstance(
                    value,
                    str,
                ):
                    raise TypeError(
                        f"{name} must contain "
                        "strings only."
                    )


@dataclass(
    frozen=True,
    slots=True,
)
class RadarEvaluationResult:
    evidence_id: str
    novelty_relevance: NoveltyRelevanceEvaluation
    capability_integration: CapabilityIntegrationEvaluation
    source_quality_reproducibility: (
        SourceQualityReproducibilityEvaluation
    )
    security_risk: SecurityRiskEvaluation
    factors: RadarFactors
    observation: RadarObservation

    def __post_init__(
        self,
    ) -> None:
        ids = {
            self.evidence_id,
            self.novelty_relevance.evidence_id,
            self.capability_integration.evidence_id,
            (
                self.source_quality_reproducibility
                .evidence_id
            ),
            self.security_risk.evidence_id,
            self.observation.evidence_id,
        }

        if len(ids) != 1:
            raise ValueError(
                "RadarEvaluationResult requires "
                "one shared evidence_id."
            )

        if (
            self.observation.verification_status
            != "UNVERIFIED_EXTERNAL"
        ):
            raise ValueError(
                "Radar pipeline must preserve "
                "UNVERIFIED_EXTERNAL."
            )

        if (
            self.observation.system_truth_asserted
            is not False
        ):
            raise ValueError(
                "Radar pipeline cannot assert "
                "system truth."
            )


class GovernedRadarEvaluationPipeline:
    """
    Pure ADEL0.8 orchestration layer.

    Flow:

    Evidence
      -> ADEL0.3 evaluation
      -> ADEL0.4 evaluation
      -> ADEL0.5 evaluation
      -> ADEL0.6 evaluation
      -> ADEL0.7 composition
      -> TechnologyRadar.assess
      -> RadarObservation

    The pipeline introduces no new scoring
    algorithms and no new authority.

    It performs no network access, persistence,
    learning, verification, promotion,
    activation, security scanning, tool
    execution, skill creation, or authority
    escalation.
    """

    def __init__(
        self,
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

    @staticmethod
    def context(
        *,
        known_claims: Iterable[str] = (),
        relevance_terms: Iterable[str] = (),
        capability_terms: Iterable[str] = (),
        existing_capabilities: Iterable[str] = (),
        integration_requirements: Iterable[str] = (),
        available_integration_support: Iterable[str] = (),
        independent_sources: Iterable[str] = (),
        reproduction_requirements: Iterable[str] = (),
        reproduction_support: Iterable[str] = (),
        risk_signals: Iterable[str] = (),
        mitigations: Iterable[str] = (),
    ) -> RadarEvaluationContext:
        def materialize(
            values: Iterable[str],
            name: str,
        ) -> tuple[str, ...]:
            if isinstance(
                values,
                (str, bytes),
            ):
                raise TypeError(
                    f"{name} must be an iterable "
                    "of strings."
                )

            result = tuple(
                values
            )

            for value in result:
                if not isinstance(
                    value,
                    str,
                ):
                    raise TypeError(
                        f"{name} must contain "
                        "strings only."
                    )

            return result

        return RadarEvaluationContext(
            known_claims=materialize(
                known_claims,
                "known_claims",
            ),
            relevance_terms=materialize(
                relevance_terms,
                "relevance_terms",
            ),
            capability_terms=materialize(
                capability_terms,
                "capability_terms",
            ),
            existing_capabilities=materialize(
                existing_capabilities,
                "existing_capabilities",
            ),
            integration_requirements=materialize(
                integration_requirements,
                "integration_requirements",
            ),
            available_integration_support=materialize(
                available_integration_support,
                "available_integration_support",
            ),
            independent_sources=materialize(
                independent_sources,
                "independent_sources",
            ),
            reproduction_requirements=materialize(
                reproduction_requirements,
                "reproduction_requirements",
            ),
            reproduction_support=materialize(
                reproduction_support,
                "reproduction_support",
            ),
            risk_signals=materialize(
                risk_signals,
                "risk_signals",
            ),
            mitigations=materialize(
                mitigations,
                "mitigations",
            ),
        )

    def evaluate(
        self,
        evidence: Evidence,
        *,
        context: RadarEvaluationContext,
    ) -> RadarEvaluationResult:
        if not isinstance(
            evidence,
            Evidence,
        ):
            raise TypeError(
                "evidence must be Evidence."
            )

        if not isinstance(
            context,
            RadarEvaluationContext,
        ):
            raise TypeError(
                "context must be "
                "RadarEvaluationContext."
            )

        TechnologyRadar._validate_evidence(
            evidence
        )

        novelty_relevance = (
            NoveltyRelevanceEvaluator.evaluate(
                evidence,
                known_claims=(
                    context.known_claims
                ),
                relevance_terms=(
                    context.relevance_terms
                ),
            )
        )

        capability_integration = (
            CapabilityIntegrationEvaluator
            .evaluate(
                evidence,
                capability_terms=(
                    context.capability_terms
                ),
                existing_capabilities=(
                    context.existing_capabilities
                ),
                integration_requirements=(
                    context.integration_requirements
                ),
                available_integration_support=(
                    context
                    .available_integration_support
                ),
            )
        )

        source_quality_reproducibility = (
            SourceQualityReproducibilityEvaluator
            .evaluate(
                evidence,
                independent_sources=(
                    context.independent_sources
                ),
                reproduction_requirements=(
                    context
                    .reproduction_requirements
                ),
                reproduction_support=(
                    context.reproduction_support
                ),
            )
        )

        security_risk = (
            SecurityRiskEvaluator.evaluate(
                evidence,
                risk_signals=(
                    context.risk_signals
                ),
                mitigations=(
                    context.mitigations
                ),
            )
        )

        factors = RadarFactorComposer.compose(
            novelty_relevance=(
                novelty_relevance
            ),
            capability_integration=(
                capability_integration
            ),
            source_quality_reproducibility=(
                source_quality_reproducibility
            ),
            security_risk=security_risk,
        )

        observation = self._radar.assess(
            evidence,
            factors,
        )

        return RadarEvaluationResult(
            evidence_id=evidence.evidence_id,
            novelty_relevance=(
                novelty_relevance
            ),
            capability_integration=(
                capability_integration
            ),
            source_quality_reproducibility=(
                source_quality_reproducibility
            ),
            security_risk=security_risk,
            factors=factors,
            observation=observation,
        )


__all__ = [
    "GovernedRadarEvaluationPipeline",
    "RadarEvaluationContext",
    "RadarEvaluationResult",
]
