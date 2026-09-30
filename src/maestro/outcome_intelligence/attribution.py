from __future__ import annotations

from .models import (
    AttributionEffect,
    AttributionFinding,
    AttributionTarget,
    OutcomeDimension,
    VerifiedOutcome,
)


def _passed(outcome: VerifiedOutcome, dimension: OutcomeDimension) -> bool | None:
    row = outcome.dimension(dimension)
    return row.passed if row else None


class OutcomeAttributor:
    """
    Conservative attribution engine.

    It explains what the evidence supports; it does not infer causation from
    temporal order alone.
    """

    def attribute(self, outcome: VerifiedOutcome) -> tuple[AttributionFinding, ...]:
        if not outcome.ay_verified:
            raise ValueError("Outcome must be AY-verified before attribution.")

        semantic = _passed(outcome, OutcomeDimension.SEMANTIC_CORRECTNESS)
        format_ok = _passed(outcome, OutcomeDimension.FORMAT_COMPLIANCE)
        resource_ok = _passed(outcome, OutcomeDimension.RESOURCE_EXECUTION)
        validator_ok = _passed(outcome, OutcomeDimension.VALIDATOR_INTEGRITY)

        findings: list[AttributionFinding] = []

        if validator_ok is False:
            findings.append(AttributionFinding(
                AttributionTarget.VALIDATOR,
                AttributionEffect.BLAME,
                0.95,
                "Validator integrity failed; downstream outcome attribution is unsafe.",
            ))
            findings.append(AttributionFinding(
                AttributionTarget.RESOURCE,
                AttributionEffect.INSUFFICIENT,
                0.05,
                "Resource cannot be judged reliably while validator integrity is false.",
                ("validator_failure",),
            ))
            return tuple(findings)

        if resource_ok is False:
            findings.append(AttributionFinding(
                AttributionTarget.RESOURCE,
                AttributionEffect.BLAME,
                0.95,
                "Resource execution itself failed.",
            ))
            return tuple(findings)

        if semantic is True and format_ok is False:
            findings.append(AttributionFinding(
                AttributionTarget.FORMAT,
                AttributionEffect.BLAME,
                0.95,
                "Semantic content passed while strict format compliance failed.",
            ))
            findings.append(AttributionFinding(
                AttributionTarget.RESOURCE,
                AttributionEffect.INSUFFICIENT,
                0.20,
                "Format-only failure does not establish general resource weakness.",
                ("prompt_contract", "normalization_policy"),
            ))
            return tuple(findings)

        if outcome.system_success and semantic is True:
            findings.append(AttributionFinding(
                AttributionTarget.RESOURCE,
                AttributionEffect.CREDIT,
                0.60,
                "Verified semantic success supports limited resource credit, not universal superiority.",
            ))
            return tuple(findings)

        if semantic is False:
            findings.append(AttributionFinding(
                AttributionTarget.RESOURCE,
                AttributionEffect.INSUFFICIENT,
                0.35,
                "Semantic failure is observed, but resource causation is not isolated from prompt/context/strategy confounders.",
                ("prompt", "context", "strategy"),
            ))
            return tuple(findings)

        findings.append(AttributionFinding(
            AttributionTarget.UNKNOWN,
            AttributionEffect.INSUFFICIENT,
            0.10,
            "Available outcome dimensions do not support causal attribution.",
        ))
        return tuple(findings)
