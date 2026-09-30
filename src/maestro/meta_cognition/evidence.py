from __future__ import annotations


class EvidenceSufficiencyEvaluator:
    """
    Evaluates whether acceptance criteria have supporting evidence.
    """

    def score(
        self,
        *,
        required_criteria: list[str],
        evidence_by_criterion: dict[str, list[str]],
        blocked_criteria: set[str] | None = None,
    ) -> float:
        if not required_criteria:
            return 1.0

        blocked = blocked_criteria or set()
        satisfied = 0.0

        for criterion in required_criteria:
            if criterion in blocked:
                continue
            refs = evidence_by_criterion.get(criterion, [])
            if refs:
                satisfied += 1.0

        return satisfied / len(required_criteria)
