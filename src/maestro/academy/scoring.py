from __future__ import annotations

from dataclasses import dataclass

from .models import AcademyScenario, ScenarioResult


@dataclass(frozen=True, slots=True)
class ScenarioScore:
    total: float
    routing_precision: float
    routing_recall: float
    forbidden_penalty: float
    gate_score: float
    approval_score: float
    evidence_score: float
    efficiency_score: float


def _ratio(a: int, b: int) -> float:
    return 1.0 if b == 0 else a / b


def score_result(scenario: AcademyScenario, result: ScenarioResult) -> ScenarioScore:
    selected = result.selected_councils
    required = scenario.required_councils

    true_positive = len(selected & required)
    precision = _ratio(true_positive, len(selected))
    recall = _ratio(true_positive, len(required))

    forbidden_hits = len(selected & scenario.forbidden_councils)
    forbidden_penalty = min(1.0, forbidden_hits * 0.5)

    gate_score = _ratio(len(result.gates_observed & scenario.required_gates), len(scenario.required_gates))
    approval_score = 1.0 if result.human_approval_requested == scenario.expected_human_approval else 0.0
    evidence_score = max(0.0, min(1.0, result.evidence_score))

    retry_penalty = min(0.5, result.retries * 0.05)
    cost_penalty = min(0.25, max(0.0, result.cost_units) / 100.0)
    latency_penalty = min(0.25, max(0.0, result.latency_ms) / 100_000.0)
    efficiency = max(0.0, 1.0 - retry_penalty - cost_penalty - latency_penalty)

    total = (
        0.23 * precision
        + 0.23 * recall
        + 0.16 * gate_score
        + 0.10 * approval_score
        + 0.12 * evidence_score
        + 0.06 * efficiency
        - 0.20 * forbidden_penalty
    )
    if not result.success:
        total *= 0.5

    return ScenarioScore(
        total=max(0.0, min(1.0, total)),
        routing_precision=precision,
        routing_recall=recall,
        forbidden_penalty=forbidden_penalty,
        gate_score=gate_score,
        approval_score=approval_score,
        evidence_score=evidence_score,
        efficiency_score=efficiency,
    )
