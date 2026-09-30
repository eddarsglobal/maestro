from __future__ import annotations

from .models import AdaptationCandidate, CandidateEligibility


class AdaptationEligibilityGate:
    def __init__(
        self,
        *,
        min_support: int = 3,
        min_confidence: float = 0.60,
        max_counter_ratio: float = 0.25,
    ):
        self.min_support = max(2, int(min_support))
        self.min_confidence = float(min_confidence)
        self.max_counter_ratio = float(max_counter_ratio)

    def evaluate(self, candidate: AdaptationCandidate) -> CandidateEligibility:
        total = candidate.support_count + candidate.counter_count
        counter_ratio = candidate.counter_count / total if total else 0.0

        if candidate.support_count < self.min_support:
            return CandidateEligibility(False, "insufficient repeated support", candidate.support_count, candidate.counter_count, candidate.confidence)
        if candidate.confidence < self.min_confidence:
            return CandidateEligibility(False, "attribution confidence below adaptation threshold", candidate.support_count, candidate.counter_count, candidate.confidence)
        if counter_ratio > self.max_counter_ratio:
            return CandidateEligibility(False, "counter-evidence ratio exceeds threshold", candidate.support_count, candidate.counter_count, candidate.confidence)
        if candidate.proposed_change.get("authority_change") is not False:
            return CandidateEligibility(False, "adaptation may not claim new authority", candidate.support_count, candidate.counter_count, candidate.confidence)

        return CandidateEligibility(True, "repeated attributable outcome pattern is eligible for shadow evaluation", candidate.support_count, candidate.counter_count, candidate.confidence)
