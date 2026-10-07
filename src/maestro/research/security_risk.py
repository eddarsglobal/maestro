from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, replace
from math import isfinite

from maestro.models import Evidence

from .technology_radar import (
    RadarFactors,
    TechnologyRadar,
)


class SecurityRiskInvariantError(
    ValueError
):
    pass


def _bounded(
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


def _normalized_set(
    values: Iterable[str],
    name: str,
) -> frozenset[str]:
    if isinstance(
        values,
        (str, bytes),
    ):
        raise TypeError(
            f"{name} must be an iterable "
            "of strings."
        )

    result: set[str] = set()

    for value in values:
        if not isinstance(
            value,
            str,
        ):
            raise TypeError(
                f"{name} must contain "
                "strings only."
            )

        normalized = value.strip().casefold()

        if normalized:
            result.add(
                normalized
            )

    return frozenset(
        result
    )


@dataclass(
    frozen=True,
    slots=True,
)
class SecurityRiskEvaluation:
    evidence_id: str
    security_risk: float | None
    risk_signals: tuple[str, ...]
    mitigated_risk_signals: tuple[str, ...]
    unmitigated_risk_signals: tuple[str, ...]
    mitigation_count: int
    residual_risk_ratio: float | None
    verification_status: str = "UNVERIFIED_EXTERNAL"
    system_truth_asserted: bool = False

    def __post_init__(
        self,
    ) -> None:
        if self.security_risk is not None:
            object.__setattr__(
                self,
                "security_risk",
                _bounded(
                    self.security_risk,
                    "security_risk",
                ),
            )

        if self.residual_risk_ratio is not None:
            object.__setattr__(
                self,
                "residual_risk_ratio",
                _bounded(
                    self.residual_risk_ratio,
                    "residual_risk_ratio",
                ),
            )

        if self.mitigation_count < 0:
            raise SecurityRiskInvariantError(
                "mitigation_count cannot "
                "be negative."
            )

        if (
            self.verification_status
            != "UNVERIFIED_EXTERNAL"
        ):
            raise SecurityRiskInvariantError(
                "ADEL0.6 may evaluate "
                "UNVERIFIED_EXTERNAL evidence only."
            )

        if self.system_truth_asserted is not False:
            raise SecurityRiskInvariantError(
                "ADEL0.6 cannot assert system truth."
            )

    @property
    def security_risk_known(
        self,
    ) -> bool:
        return (
            self.security_risk
            is not None
        )

    def apply_to_factors(
        self,
        factors: RadarFactors,
    ) -> RadarFactors:
        if not isinstance(
            factors,
            RadarFactors,
        ):
            raise TypeError(
                "factors must be RadarFactors."
            )

        if self.security_risk is None:
            raise SecurityRiskInvariantError(
                "Unknown security risk cannot "
                "be silently converted into a "
                "RadarFactors value."
            )

        return replace(
            factors,
            security_risk=self.security_risk,
        )


class SecurityRiskEvaluator:
    """
    Pure ADEL0.6 security-risk evaluator.

    It derives residual security risk only
    from explicit caller-supplied risk signals
    and explicit mitigations.

    It does not perform security scanning,
    network access, sandbox execution,
    authority validation, activation,
    installation, learning, promotion,
    persistence, or tool execution.

    security_risk is a Radar interest penalty.
    It is not an authorization decision,
    security verdict, truth assertion,
    or Council authority.
    """

    @staticmethod
    def evaluate(
        evidence: Evidence,
        *,
        risk_signals: Iterable[str] = (),
        mitigations: Iterable[str] = (),
    ) -> SecurityRiskEvaluation:
        TechnologyRadar._validate_evidence(
            evidence
        )

        signals = _normalized_set(
            risk_signals,
            "risk_signals",
        )

        mitigation_set = _normalized_set(
            mitigations,
            "mitigations",
        )

        if not signals:
            risk = None
            residual_ratio = None
            mitigated: frozenset[str] = (
                frozenset()
            )
            unmitigated: frozenset[str] = (
                frozenset()
            )
        else:
            mitigated = (
                signals
                & mitigation_set
            )

            unmitigated = (
                signals
                - mitigation_set
            )

            residual_ratio = (
                len(unmitigated)
                / len(signals)
            )

            risk = residual_ratio

        return SecurityRiskEvaluation(
            evidence_id=evidence.evidence_id,
            security_risk=risk,
            risk_signals=tuple(
                sorted(signals)
            ),
            mitigated_risk_signals=tuple(
                sorted(mitigated)
            ),
            unmitigated_risk_signals=tuple(
                sorted(unmitigated)
            ),
            mitigation_count=len(
                mitigation_set
            ),
            residual_risk_ratio=(
                residual_ratio
            ),
            verification_status=(
                "UNVERIFIED_EXTERNAL"
            ),
            system_truth_asserted=False,
        )


__all__ = [
    "SecurityRiskEvaluation",
    "SecurityRiskEvaluator",
    "SecurityRiskInvariantError",
]
