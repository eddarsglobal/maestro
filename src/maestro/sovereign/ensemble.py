from __future__ import annotations

from dataclasses import dataclass

from .contracts import IntelligenceResponse


@dataclass(slots=True)
class SynthesisInput:
    responses: list[IntelligenceResponse]


class MultiResourceSynthesizer:
    """
    Deterministic evidence-preserving merge helper.
    It does not ask one model to become authority over the others.
    """

    def select_successes(self, responses: list[IntelligenceResponse]) -> list[IntelligenceResponse]:
        return [r for r in responses if r.success]

    def agreement_ratio(self, responses: list[IntelligenceResponse]) -> float:
        ok = self.select_successes(responses)
        if not ok:
            return 0.0
        normalized = [r.output.strip() for r in ok]
        winner = max(set(normalized), key=normalized.count)
        return normalized.count(winner) / len(normalized)
