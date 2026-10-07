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


class NoveltyRelevanceInvariantError(
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


def _jaccard(
    left: frozenset[str],
    right: frozenset[str],
) -> float:
    if not left and not right:
        return 1.0

    union = left | right

    if not union:
        return 0.0

    return len(left & right) / len(union)


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
class NoveltyRelevanceEvaluation:
    evidence_id: str
    novelty: float
    relevance_to_maestro: float | None
    exact_match: bool
    max_known_similarity: float
    matched_relevance_terms: tuple[str, ...]
    verification_status: str = "UNVERIFIED_EXTERNAL"
    system_truth_asserted: bool = False

    def __post_init__(
        self,
    ) -> None:
        object.__setattr__(
            self,
            "novelty",
            _bounded(
                self.novelty,
                "novelty",
            ),
        )

        object.__setattr__(
            self,
            "max_known_similarity",
            _bounded(
                self.max_known_similarity,
                "max_known_similarity",
            ),
        )

        if self.relevance_to_maestro is not None:
            object.__setattr__(
                self,
                "relevance_to_maestro",
                _bounded(
                    self.relevance_to_maestro,
                    "relevance_to_maestro",
                ),
            )

        if (
            self.verification_status
            != "UNVERIFIED_EXTERNAL"
        ):
            raise NoveltyRelevanceInvariantError(
                "ADEL0.3 may evaluate "
                "UNVERIFIED_EXTERNAL evidence only."
            )

        if self.system_truth_asserted is not False:
            raise NoveltyRelevanceInvariantError(
                "ADEL0.3 cannot assert system truth."
            )

    @property
    def relevance_known(
        self,
    ) -> bool:
        return (
            self.relevance_to_maestro
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

        if self.relevance_to_maestro is None:
            raise NoveltyRelevanceInvariantError(
                "Unknown relevance cannot be "
                "silently converted into a "
                "RadarFactors relevance value."
            )

        return replace(
            factors,
            novelty=self.novelty,
            relevance_to_maestro=(
                self.relevance_to_maestro
            ),
        )


class NoveltyRelevanceEvaluator:
    """
    Pure ADEL0.3 evaluator.

    It derives novelty and MAESTRO relevance
    from already-existing governed RX evidence
    plus explicit caller-supplied comparison
    context.

    It performs no network access, learning,
    persistence, truth promotion, activation,
    skill creation, or authority escalation.
    """

    @staticmethod
    def evaluate(
        evidence: Evidence,
        *,
        known_claims: Iterable[str] = (),
        relevance_terms: Iterable[str] = (),
    ) -> NoveltyRelevanceEvaluation:
        TechnologyRadar._validate_evidence(
            evidence
        )

        if isinstance(
            known_claims,
            (str, bytes),
        ):
            raise TypeError(
                "known_claims must be an "
                "iterable of strings."
            )

        if isinstance(
            relevance_terms,
            (str, bytes),
        ):
            raise TypeError(
                "relevance_terms must be an "
                "iterable of strings."
            )

        known = tuple(
            known_claims
        )
        terms = tuple(
            relevance_terms
        )

        for claim in known:
            if not isinstance(
                claim,
                str,
            ):
                raise TypeError(
                    "known_claims must contain "
                    "strings only."
                )

        for term in terms:
            if not isinstance(
                term,
                str,
            ):
                raise TypeError(
                    "relevance_terms must contain "
                    "strings only."
                )

        claim_tokens = _tokens(
            evidence.claim
        )

        similarities = tuple(
            _jaccard(
                claim_tokens,
                _tokens(claim),
            )
            for claim in known
        )

        max_similarity = (
            max(similarities)
            if similarities
            else 0.0
        )

        novelty = 1.0 - max_similarity

        exact_match = any(
            claim_tokens == _tokens(claim)
            for claim in known
        )

        normalized_terms = tuple(
            sorted(
                {
                    token
                    for term in terms
                    for token in _tokens(term)
                }
            )
        )

        if not normalized_terms:
            relevance = None
            matched_terms: tuple[str, ...] = ()
        else:
            matched_terms = tuple(
                token
                for token in normalized_terms
                if token in claim_tokens
            )

            relevance = (
                len(matched_terms)
                / len(normalized_terms)
            )

        return NoveltyRelevanceEvaluation(
            evidence_id=evidence.evidence_id,
            novelty=novelty,
            relevance_to_maestro=relevance,
            exact_match=exact_match,
            max_known_similarity=max_similarity,
            matched_relevance_terms=matched_terms,
            verification_status=(
                "UNVERIFIED_EXTERNAL"
            ),
            system_truth_asserted=False,
        )


__all__ = [
    "NoveltyRelevanceEvaluation",
    "NoveltyRelevanceEvaluator",
    "NoveltyRelevanceInvariantError",
]
