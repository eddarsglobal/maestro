from __future__ import annotations

import re

from collections.abc import Iterable
from dataclasses import dataclass, replace
from math import isfinite

from maestro.models import Evidence

from .technology_radar import (
    RadarFactors,
    TechnologyRadar,
)


_TOKEN_RE = re.compile(r"[a-z0-9]+")


class CapabilityIntegrationInvariantError(
    ValueError
):
    pass


def _tokens(
    value: str,
) -> frozenset[str]:
    if not isinstance(
        value,
        str,
    ):
        raise TypeError(
            "text values must be strings."
        )

    return frozenset(
        _TOKEN_RE.findall(
            value.casefold()
        )
    )


def _normalized_terms(
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

    normalized: set[str] = set()

    for value in values:
        if not isinstance(
            value,
            str,
        ):
            raise TypeError(
                f"{name} must contain "
                "strings only."
            )

        normalized.update(
            _tokens(value)
        )

    return frozenset(
        normalized
    )


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


@dataclass(
    frozen=True,
    slots=True,
)
class CapabilityIntegrationEvaluation:
    evidence_id: str
    expected_capability_gain: float | None
    integration_cost: float | None
    target_capability_terms: tuple[str, ...]
    novel_capability_terms: tuple[str, ...]
    matched_novel_capability_terms: tuple[str, ...]
    integration_requirements: tuple[str, ...]
    unsupported_integration_requirements: tuple[str, ...]
    verification_status: str = "UNVERIFIED_EXTERNAL"
    system_truth_asserted: bool = False

    def __post_init__(
        self,
    ) -> None:
        if self.expected_capability_gain is not None:
            object.__setattr__(
                self,
                "expected_capability_gain",
                _bounded(
                    self.expected_capability_gain,
                    "expected_capability_gain",
                ),
            )

        if self.integration_cost is not None:
            object.__setattr__(
                self,
                "integration_cost",
                _bounded(
                    self.integration_cost,
                    "integration_cost",
                ),
            )

        if (
            self.verification_status
            != "UNVERIFIED_EXTERNAL"
        ):
            raise CapabilityIntegrationInvariantError(
                "ADEL0.4 may evaluate "
                "UNVERIFIED_EXTERNAL evidence only."
            )

        if self.system_truth_asserted is not False:
            raise CapabilityIntegrationInvariantError(
                "ADEL0.4 cannot assert system truth."
            )

    @property
    def capability_gain_known(
        self,
    ) -> bool:
        return (
            self.expected_capability_gain
            is not None
        )

    @property
    def integration_cost_known(
        self,
    ) -> bool:
        return (
            self.integration_cost
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

        if self.expected_capability_gain is None:
            raise CapabilityIntegrationInvariantError(
                "Unknown capability gain cannot "
                "be silently converted into a "
                "RadarFactors value."
            )

        if self.integration_cost is None:
            raise CapabilityIntegrationInvariantError(
                "Unknown integration cost cannot "
                "be silently converted into a "
                "RadarFactors value."
            )

        return replace(
            factors,
            expected_capability_gain=(
                self.expected_capability_gain
            ),
            integration_cost=(
                self.integration_cost
            ),
        )


class CapabilityIntegrationEvaluator:
    """
    Pure ADEL0.4 evaluator.

    It derives expected capability gain and
    integration cost from existing governed
    RX evidence plus explicit caller-supplied
    context.

    Capability gain is not truth, learning,
    promotion, installation, or activation.

    Integration cost is an interest factor,
    not authorization to integrate anything.

    The evaluator performs no network access,
    persistence, learning, promotion,
    activation, skill creation, execution,
    or authority escalation.
    """

    @staticmethod
    def evaluate(
        evidence: Evidence,
        *,
        capability_terms: Iterable[str] = (),
        existing_capabilities: Iterable[str] = (),
        integration_requirements: Iterable[str] = (),
        available_integration_support: Iterable[str] = (),
    ) -> CapabilityIntegrationEvaluation:
        TechnologyRadar._validate_evidence(
            evidence
        )

        target_terms = _normalized_terms(
            capability_terms,
            "capability_terms",
        )

        existing_terms = _normalized_terms(
            existing_capabilities,
            "existing_capabilities",
        )

        requirement_terms = _normalized_terms(
            integration_requirements,
            "integration_requirements",
        )

        support_terms = _normalized_terms(
            available_integration_support,
            "available_integration_support",
        )

        claim_terms = _tokens(
            evidence.claim
        )

        novel_terms = (
            target_terms
            - existing_terms
        )

        matched_novel_terms = (
            novel_terms
            & claim_terms
        )

        if not target_terms:
            capability_gain = None
        elif not novel_terms:
            capability_gain = 0.0
        else:
            capability_gain = (
                len(matched_novel_terms)
                / len(novel_terms)
            )

        unsupported_requirements = (
            requirement_terms
            - support_terms
        )

        if not requirement_terms:
            integration_cost = None
        else:
            integration_cost = (
                len(unsupported_requirements)
                / len(requirement_terms)
            )

        return CapabilityIntegrationEvaluation(
            evidence_id=evidence.evidence_id,
            expected_capability_gain=(
                capability_gain
            ),
            integration_cost=(
                integration_cost
            ),
            target_capability_terms=tuple(
                sorted(target_terms)
            ),
            novel_capability_terms=tuple(
                sorted(novel_terms)
            ),
            matched_novel_capability_terms=tuple(
                sorted(matched_novel_terms)
            ),
            integration_requirements=tuple(
                sorted(requirement_terms)
            ),
            unsupported_integration_requirements=tuple(
                sorted(
                    unsupported_requirements
                )
            ),
            verification_status=(
                "UNVERIFIED_EXTERNAL"
            ),
            system_truth_asserted=False,
        )


__all__ = [
    "CapabilityIntegrationEvaluation",
    "CapabilityIntegrationEvaluator",
    "CapabilityIntegrationInvariantError",
]
