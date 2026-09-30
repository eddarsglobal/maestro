from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from maestro.intelligence_market import IntelligenceMarket, MarketObservation

from .models import MarketLearningDirective, VerifiedOutcome


@dataclass(slots=True, frozen=True)
class OutcomeMarketApplyResult:
    applied: bool
    duplicate: bool
    reason: str
    outcome_id: str
    resource_id: str | None
    task_family: str
    observations_before: int
    observations_after: int


class OutcomeMarketBridge:
    """
    Governed bridge from verified Outcome Intelligence to Intelligence Market.

    An eligible directive is necessary but not sufficient. The bridge also
    requires traceable AY evidence, explicit market-observation facts, and
    idempotence. It never fabricates missing cost/context/tool/locality data.
    """

    REQUIRED_CONTEXT_KEYS = (
        "council_id",
        "scenario_id",
        "cost_score",
        "context_fit",
        "tool_fit",
        "local",
    )

    def apply(
        self,
        *,
        market: IntelligenceMarket,
        outcome: VerifiedOutcome,
        directive: MarketLearningDirective,
    ) -> OutcomeMarketApplyResult:
        before = len(market.ledger.all())

        def result(applied: bool, duplicate: bool, reason: str) -> OutcomeMarketApplyResult:
            return OutcomeMarketApplyResult(
                applied=applied,
                duplicate=duplicate,
                reason=reason,
                outcome_id=outcome.outcome_id,
                resource_id=outcome.resource_id,
                task_family=outcome.task_family,
                observations_before=before,
                observations_after=len(market.ledger.all()),
            )

        if not directive.eligible:
            return result(False, False, f"directive ineligible: {directive.reason}")

        if not outcome.ay_verified:
            return result(False, False, "outcome is not AY-verified")

        if not outcome.evidence_ids:
            return result(False, False, "AY-verified outcome has no evidence ids")

        if directive.resource_id is None or outcome.resource_id is None:
            return result(False, False, "resource id missing")

        if directive.resource_id != outcome.resource_id:
            return result(False, False, "directive/outcome resource mismatch")

        if directive.task_family != outcome.task_family:
            return result(False, False, "directive/outcome task-family mismatch")

        if directive.success is None or directive.quality is None:
            return result(False, False, "eligible directive lacks success/quality")

        for row in market.ledger.all():
            meta = row.metadata if isinstance(row.metadata, dict) else {}
            if meta.get("outcome_id") == outcome.outcome_id:
                return result(False, True, "outcome already applied to market")

        context = outcome.metadata.get("market_observation")
        if not isinstance(context, dict):
            return result(False, False, "market_observation evidence missing")

        missing = [key for key in self.REQUIRED_CONTEXT_KEYS if key not in context]
        if missing:
            return result(False, False, "market_observation missing: " + ", ".join(missing))

        scenario_id = context["scenario_id"]
        if not isinstance(scenario_id, str) or not scenario_id.strip():
            return result(False, False, "scenario_id must be a non-empty string")

        local = context["local"]
        if not isinstance(local, bool):
            return result(False, False, "local must be an explicit boolean")

        council_id = context["council_id"]
        if council_id is not None and not isinstance(council_id, str):
            return result(False, False, "council_id must be string or None")

        def bounded_number(name: str) -> float:
            value = context[name]
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise ValueError(f"{name} must be numeric")
            value = float(value)
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{name} must be within [0, 1]")
            return value

        try:
            cost_score = bounded_number("cost_score")
            context_fit = bounded_number("context_fit")
            tool_fit = bounded_number("tool_fit")
        except ValueError as exc:
            return result(False, False, str(exc))

        latency_ms = context.get("latency_ms")
        if latency_ms is not None:
            if isinstance(latency_ms, bool) or not isinstance(latency_ms, (int, float)):
                return result(False, False, "latency_ms must be numeric or None")
            latency_ms = float(latency_ms)
            if latency_ms < 0.0:
                return result(False, False, "latency_ms cannot be negative")

        quality = float(directive.quality)
        if not 0.0 <= quality <= 1.0:
            return result(False, False, "directive quality must be within [0, 1]")

        observation = MarketObservation(
            resource_id=directive.resource_id,
            task_family=directive.task_family,
            council_id=council_id,
            success=bool(directive.success),
            quality=quality,
            latency_ms=latency_ms,
            cost_score=cost_score,
            context_fit=context_fit,
            tool_fit=tool_fit,
            local=local,
            evidence_ref=outcome.evidence_ids[0],
            metadata={
                "scenario_id": scenario_id,
                "outcome_id": outcome.outcome_id,
                "source": "OUTCOME_INTELLIGENCE",
                "system_verdict": outcome.system_verdict,
                "attribution_confidence": float(directive.confidence),
                "attribution_reason": directive.reason,
                "evidence_ids": list(outcome.evidence_ids),
            },
        )

        market.observe(observation)
        return result(True, False, "verified outcome applied to market")
