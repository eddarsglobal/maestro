from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from math import isfinite

from maestro.enums import (
    CouncilId,
    EvidenceKind,
)
from maestro.models import Evidence


class TechnologyRadarInvariantError(
    ValueError
):
    pass


def _factor(
    value: float,
    name: str,
) -> float:
    if isinstance(value, bool):
        raise TypeError(
            f"{name} must be a real number."
        )

    if not isinstance(
        value,
        (int, float),
    ):
        raise TypeError(
            f"{name} must be a real number."
        )

    normalized = float(value)

    if not isfinite(normalized):
        raise ValueError(
            f"{name} must be finite."
        )

    if not 0.0 <= normalized <= 1.0:
        raise ValueError(
            f"{name} must be in [0, 1]."
        )

    return normalized


@dataclass(
    frozen=True,
    slots=True,
)
class RadarFactors:
    novelty: float
    source_quality: float
    relevance_to_maestro: float
    expected_capability_gain: float
    reproducibility: float
    integration_cost: float
    security_risk: float

    def __post_init__(
        self,
    ) -> None:
        for name in (
            "novelty",
            "source_quality",
            "relevance_to_maestro",
            "expected_capability_gain",
            "reproducibility",
            "integration_cost",
            "security_risk",
        ):
            object.__setattr__(
                self,
                name,
                _factor(
                    getattr(self, name),
                    name,
                ),
            )

    @property
    def priority_score(
        self,
    ) -> float:
        positive = (
            self.novelty
            * self.source_quality
            * self.relevance_to_maestro
            * self.expected_capability_gain
            * self.reproducibility
        )

        penalty = (
            (1.0 + self.integration_cost)
            * (1.0 + self.security_risk)
        )

        return positive / penalty


@dataclass(
    frozen=True,
    slots=True,
)
class RadarObservation:
    task_id: str
    evidence_id: str
    source_ref: str
    claim: str
    verification_status: str
    system_truth_asserted: bool
    factors: RadarFactors
    priority_score: float


class TechnologyRadar:
    """
    Pure RX discovery-priority evaluator.

    It consumes existing RX WEB_SOURCE Evidence
    and produces rank-only observations.

    It performs no network access, truth
    verification, learning, promotion,
    installation, activation, or execution.
    """

    @staticmethod
    def _validate_evidence(
        evidence: Evidence,
    ) -> None:
        if not isinstance(
            evidence,
            Evidence,
        ):
            raise TypeError(
                "evidence must be an Evidence."
            )

        if evidence.council is not CouncilId.RX:
            raise TechnologyRadarInvariantError(
                "Technology Radar accepts "
                "RX evidence only."
            )

        if (
            evidence.kind
            is not EvidenceKind.WEB_SOURCE
        ):
            raise TechnologyRadarInvariantError(
                "Technology Radar accepts "
                "WEB_SOURCE evidence only."
            )

        if not isinstance(
            evidence.source_ref,
            str,
        ) or not evidence.source_ref:
            raise TechnologyRadarInvariantError(
                "Technology Radar requires "
                "an internal source_ref."
            )

        if not isinstance(
            evidence.payload,
            dict,
        ):
            raise TechnologyRadarInvariantError(
                "Research evidence payload "
                "must be a dictionary."
            )

        verification = (
            evidence.payload.get(
                "verification"
            )
        )

        if not isinstance(
            verification,
            dict,
        ):
            raise TechnologyRadarInvariantError(
                "Research evidence requires "
                "verification metadata."
            )

        if (
            verification.get("status")
            != "UNVERIFIED_EXTERNAL"
        ):
            raise TechnologyRadarInvariantError(
                "Technology Radar may rank "
                "UNVERIFIED_EXTERNAL evidence "
                "only."
            )

        if (
            verification.get(
                "required_authority"
            )
            != CouncilId.AY.value
        ):
            raise TechnologyRadarInvariantError(
                "External research must retain "
                "AY as verification authority."
            )

        if (
            verification.get(
                "system_truth_asserted"
            )
            is not False
        ):
            raise TechnologyRadarInvariantError(
                "Technology Radar rejects "
                "evidence asserting system truth."
            )

        research_claim = (
            evidence.payload.get(
                "research_claim"
            )
        )

        if not isinstance(
            research_claim,
            dict,
        ):
            raise TechnologyRadarInvariantError(
                "Research evidence requires "
                "research_claim metadata."
            )

        if (
            research_claim.get("claim_id")
            != evidence.source_ref
        ):
            raise TechnologyRadarInvariantError(
                "Research claim identity "
                "does not match source_ref."
            )

        if (
            research_claim.get("statement")
            != evidence.claim
        ):
            raise TechnologyRadarInvariantError(
                "Research claim statement "
                "does not match Evidence."
            )

        artifacts = evidence.payload.get(
            "artifacts"
        )

        if (
            not isinstance(
                artifacts,
                list,
            )
            or not artifacts
        ):
            raise TechnologyRadarInvariantError(
                "Research evidence requires "
                "at least one external artifact."
            )

    def assess(
        self,
        evidence: Evidence,
        factors: RadarFactors,
    ) -> RadarObservation:
        self._validate_evidence(
            evidence
        )

        if not isinstance(
            factors,
            RadarFactors,
        ):
            raise TypeError(
                "factors must be RadarFactors."
            )

        return RadarObservation(
            task_id=evidence.task_id,
            evidence_id=evidence.evidence_id,
            source_ref=evidence.source_ref,
            claim=evidence.claim,
            verification_status=(
                "UNVERIFIED_EXTERNAL"
            ),
            system_truth_asserted=False,
            factors=factors,
            priority_score=(
                factors.priority_score
            ),
        )

    def rank(
        self,
        observations: Iterable[
            RadarObservation
        ],
    ) -> list[RadarObservation]:
        rows = tuple(
            observations
        )

        for row in rows:
            if not isinstance(
                row,
                RadarObservation,
            ):
                raise TypeError(
                    "observations must contain "
                    "RadarObservation objects."
                )

        ids = [
            row.evidence_id
            for row in rows
        ]

        if len(ids) != len(set(ids)):
            raise TechnologyRadarInvariantError(
                "Technology Radar ranking "
                "requires unique evidence IDs."
            )

        return sorted(
            rows,
            key=lambda row: (
                -row.priority_score,
                row.evidence_id,
            ),
        )


__all__ = [
    "RadarFactors",
    "RadarObservation",
    "TechnologyRadar",
    "TechnologyRadarInvariantError",
]
