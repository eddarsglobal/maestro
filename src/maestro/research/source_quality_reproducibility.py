from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, replace
from math import isfinite

from maestro.models import Evidence

from .technology_radar import (
    RadarFactors,
    TechnologyRadar,
)


class SourceQualityReproducibilityInvariantError(
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


def _string_set(
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
class SourceQualityReproducibilityEvaluation:
    evidence_id: str
    source_quality: float | None
    reproducibility: float | None
    artifact_count: int
    digest_coverage: float
    metadata_coverage: float
    independent_source_count: int
    reproduction_requirement_count: int
    reproduction_support_count: int
    unsupported_reproduction_requirements: tuple[str, ...]
    verification_status: str = "UNVERIFIED_EXTERNAL"
    system_truth_asserted: bool = False

    def __post_init__(
        self,
    ) -> None:
        if self.source_quality is not None:
            object.__setattr__(
                self,
                "source_quality",
                _bounded(
                    self.source_quality,
                    "source_quality",
                ),
            )

        if self.reproducibility is not None:
            object.__setattr__(
                self,
                "reproducibility",
                _bounded(
                    self.reproducibility,
                    "reproducibility",
                ),
            )

        object.__setattr__(
            self,
            "digest_coverage",
            _bounded(
                self.digest_coverage,
                "digest_coverage",
            ),
        )

        object.__setattr__(
            self,
            "metadata_coverage",
            _bounded(
                self.metadata_coverage,
                "metadata_coverage",
            ),
        )

        if self.artifact_count < 1:
            raise SourceQualityReproducibilityInvariantError(
                "ADEL0.5 requires at least "
                "one artifact."
            )

        if self.independent_source_count < 1:
            raise SourceQualityReproducibilityInvariantError(
                "ADEL0.5 requires at least "
                "one source."
            )

        if (
            self.verification_status
            != "UNVERIFIED_EXTERNAL"
        ):
            raise SourceQualityReproducibilityInvariantError(
                "ADEL0.5 may evaluate "
                "UNVERIFIED_EXTERNAL evidence only."
            )

        if self.system_truth_asserted is not False:
            raise SourceQualityReproducibilityInvariantError(
                "ADEL0.5 cannot assert system truth."
            )

    @property
    def source_quality_known(
        self,
    ) -> bool:
        return (
            self.source_quality
            is not None
        )

    @property
    def reproducibility_known(
        self,
    ) -> bool:
        return (
            self.reproducibility
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

        if self.source_quality is None:
            raise SourceQualityReproducibilityInvariantError(
                "Unknown source quality cannot "
                "be silently converted into a "
                "RadarFactors value."
            )

        if self.reproducibility is None:
            raise SourceQualityReproducibilityInvariantError(
                "Unknown reproducibility cannot "
                "be silently converted into a "
                "RadarFactors value."
            )

        return replace(
            factors,
            source_quality=self.source_quality,
            reproducibility=self.reproducibility,
        )


class SourceQualityReproducibilityEvaluator:
    """
    Pure ADEL0.5 evaluator.

    Source quality is derived only from
    observable evidence/provenance structure
    plus explicit caller-supplied source
    independence context.

    Reproducibility is derived only from
    explicit requirements and explicit
    available reproduction support.

    Neither score verifies truth.

    The evaluator performs no network access,
    persistence, learning, promotion,
    activation, execution, skill creation,
    or authority escalation.
    """

    @staticmethod
    def evaluate(
        evidence: Evidence,
        *,
        independent_sources: Iterable[str] = (),
        reproduction_requirements: Iterable[str] = (),
        reproduction_support: Iterable[str] = (),
    ) -> SourceQualityReproducibilityEvaluation:
        TechnologyRadar._validate_evidence(
            evidence
        )

        payload = evidence.payload
        artifacts = payload["artifacts"]

        source_ids: set[str] = set()
        digest_count = 0
        metadata_points = 0
        metadata_total = 0

        for artifact in artifacts:
            if not isinstance(
                artifact,
                dict,
            ):
                raise SourceQualityReproducibilityInvariantError(
                    "Artifact payload entries "
                    "must be dictionaries."
                )

            source = artifact.get(
                "source"
            )
            provenance = artifact.get(
                "provenance"
            )

            if not isinstance(
                source,
                dict,
            ):
                raise SourceQualityReproducibilityInvariantError(
                    "Artifact source metadata "
                    "must be a dictionary."
                )

            if not isinstance(
                provenance,
                dict,
            ):
                raise SourceQualityReproducibilityInvariantError(
                    "Artifact provenance metadata "
                    "must be a dictionary."
                )

            source_id = source.get(
                "source_id"
            )

            if isinstance(
                source_id,
                str,
            ) and source_id:
                source_ids.add(
                    source_id
                )

            digest = provenance.get(
                "digest"
            )

            if (
                isinstance(digest, dict)
                and digest.get("algorithm") == "sha256"
                and isinstance(
                    digest.get("hex_digest"),
                    str,
                )
                and len(
                    digest["hex_digest"]
                ) == 64
            ):
                digest_count += 1

            for field in (
                "author",
                "license",
                "version",
            ):
                metadata_total += 1

                value = provenance.get(
                    field
                )

                if isinstance(
                    value,
                    str,
                ) and value.strip():
                    metadata_points += 1

        artifact_count = len(
            artifacts
        )

        digest_coverage = (
            digest_count
            / artifact_count
        )

        metadata_coverage = (
            metadata_points
            / metadata_total
            if metadata_total
            else 0.0
        )

        explicit_independent = _string_set(
            independent_sources,
            "independent_sources",
        )

        independent_count = max(
            len(source_ids),
            len(explicit_independent),
        )

        source_quality = (
            0.50 * digest_coverage
            + 0.25 * metadata_coverage
            + 0.25 * min(
                independent_count / 2.0,
                1.0,
            )
        )

        requirements = _string_set(
            reproduction_requirements,
            "reproduction_requirements",
        )

        support = _string_set(
            reproduction_support,
            "reproduction_support",
        )

        unsupported = (
            requirements
            - support
        )

        if not requirements:
            reproducibility = None
        else:
            reproducibility = (
                len(
                    requirements
                    & support
                )
                / len(requirements)
            )

        return SourceQualityReproducibilityEvaluation(
            evidence_id=evidence.evidence_id,
            source_quality=source_quality,
            reproducibility=reproducibility,
            artifact_count=artifact_count,
            digest_coverage=digest_coverage,
            metadata_coverage=metadata_coverage,
            independent_source_count=(
                independent_count
            ),
            reproduction_requirement_count=(
                len(requirements)
            ),
            reproduction_support_count=(
                len(
                    requirements
                    & support
                )
            ),
            unsupported_reproduction_requirements=tuple(
                sorted(unsupported)
            ),
            verification_status=(
                "UNVERIFIED_EXTERNAL"
            ),
            system_truth_asserted=False,
        )


__all__ = [
    "SourceQualityReproducibilityEvaluation",
    "SourceQualityReproducibilityEvaluator",
    "SourceQualityReproducibilityInvariantError",
]
