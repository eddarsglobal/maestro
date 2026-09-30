from __future__ import annotations

from dataclasses import dataclass

from .models import ResourceScoreCard


@dataclass(slots=True)
class PortfolioEntry:
    resource_id: str
    market_score: float
    role: str


class IntelligencePortfolio:
    """
    Keeps multiple viable resources rather than optimizing toward one monopoly.
    """

    def build(self, scorecards: list[ResourceScoreCard], limit: int = 3) -> list[PortfolioEntry]:
        if limit < 1:
            raise ValueError("limit must be >= 1")
        ordered = sorted(
            scorecards,
            key=lambda c: (c.market_score, c.reliability, c.success_rate),
            reverse=True,
        )[:limit]
        roles = ["PRIMARY", "SECONDARY", "RESERVE"]
        return [
            PortfolioEntry(c.resource_id, c.market_score, roles[min(i, len(roles)-1)])
            for i, c in enumerate(ordered)
        ]
