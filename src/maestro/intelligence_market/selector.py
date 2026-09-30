from __future__ import annotations

from .ledger import IntelligenceMarketLedger
from .models import MarketSelection, MarketPolicy
from .scorecards import ScoreCardEngine
from .exploration import ExplorationController


class IntelligenceMarketSelector:
    def __init__(
        self,
        ledger: IntelligenceMarketLedger,
        policy: MarketPolicy | None = None,
    ):
        self.ledger = ledger
        self.policy = policy or MarketPolicy()
        self.scorecards = ScoreCardEngine(self.policy)
        self.exploration = ExplorationController(self.policy.min_samples_for_confidence)

    def _evidence_confidence(
        self,
        *,
        resource_id: str,
        task_family: str,
        council_id: str | None,
        reliability: float | None = None,
    ) -> tuple[float, dict]:
        """
        Estimate confidence in an observed market score.

        Market score answers:
            "How well has this resource performed?"

        Evidence confidence answers:
            "How much evidence justifies trusting that score?"

        Confidence requires both sufficient observation volume and
        sufficient scenario diversity. Reliability additionally penalizes
        contradictory outcomes.
        """
        rows = self.ledger.query(
            resource_id=resource_id,
            task_family=task_family,
            council_id=council_id,
        )

        samples = len(rows)

        scenario_ids = {
            str(o.metadata.get("scenario_id"))
            for o in rows
            if isinstance(o.metadata, dict)
            and o.metadata.get("scenario_id") is not None
        }

        scenarios = len(scenario_ids)

        full_samples = max(
            1,
            int(self.policy.full_confidence_samples),
        )

        full_scenarios = max(
            1,
            int(self.policy.full_confidence_scenarios),
        )

        sample_factor = min(
            1.0,
            samples / full_samples,
        )

        # Legacy observations may not contain scenario_id.
        # They remain usable, but cannot fabricate extra diversity.
        scenario_factor = (
            min(1.0, scenarios / full_scenarios)
            if scenarios > 0
            else sample_factor
        )

        if reliability is None:
            reliability_factor = 1.0
        else:
            bounded_reliability = max(
                0.0,
                min(1.0, float(reliability)),
            )

            # Reliability can reduce confidence but does not erase
            # otherwise valid evidence completely.
            reliability_factor = (
                0.5 + 0.5 * bounded_reliability
            )

        confidence = (
            min(sample_factor, scenario_factor)
            * reliability_factor
        )

        confidence = max(
            0.0,
            min(1.0, confidence),
        )

        return confidence, {
            "evidence_samples": samples,
            "distinct_scenarios": scenarios,
            "sample_factor": sample_factor,
            "scenario_factor": scenario_factor,
            "reliability_factor": reliability_factor,
            "full_confidence_samples": full_samples,
            "full_confidence_scenarios": full_scenarios,
        }

    def select(
        self,
        *,
        eligible_resource_ids: list[str],
        task_family: str,
        council_id: str | None,
        allow_exploration: bool = True,
    ) -> MarketSelection:
        if not eligible_resource_ids:
            raise LookupError("No eligible intelligence resources.")

        sample_counts = {}
        cards = {}

        for rid in eligible_resource_ids:
            rows = self.ledger.query(resource_id=rid, task_family=task_family, council_id=council_id)
            sample_counts[rid] = len(rows)
            if rows:
                cards[rid] = self.scorecards.build(
                    self.ledger.all(),
                    resource_id=rid,
                    task_family=task_family,
                    council_id=council_id,
                )

        if allow_exploration:
            decision = self.exploration.should_explore(sample_counts)
            if decision.explore:
                rid = self.exploration.choose_under_tested(sample_counts)
                card = cards.get(rid)

                confidence, confidence_meta = self._evidence_confidence(
                    resource_id=rid,
                    task_family=task_family,
                    council_id=council_id,
                    reliability=card.reliability if card else None,
                )

                score = card.market_score if card else 0.5
                return MarketSelection(
                    rid, task_family, council_id, score, confidence, True,
                    {
                        "reason": decision.reason,
                        "samples": sample_counts[rid],
                        **confidence_meta,
                    },
                )

        if not cards:
            rid = sorted(eligible_resource_ids)[0]
            return MarketSelection(
                rid, task_family, council_id, 0.5, 0.0, False,
                {"reason": "bootstrap deterministic fallback"},
            )

        best = max(
            cards.values(),
            key=lambda c: (c.market_score, c.success_rate, c.mean_quality, c.resource_id),
        )
        confidence, confidence_meta = self._evidence_confidence(
            resource_id=best.resource_id,
            task_family=task_family,
            council_id=council_id,
            reliability=best.reliability,
        )

        return MarketSelection(
            best.resource_id,
            task_family,
            council_id,
            best.market_score,
            confidence,
            False,
            {
                "samples": best.samples,
                "success_rate": best.success_rate,
                "mean_quality": best.mean_quality,
                "reliability": best.reliability,
            **confidence_meta,
            },
        )
