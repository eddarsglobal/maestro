from __future__ import annotations


class ContradictionDetector:
    """
    Lightweight contradiction detector over explicit claims/statuses.
    """

    def score(self, claims: list[dict]) -> float:
        if not claims:
            return 0.0

        by_key: dict[str, set[str]] = {}
        for c in claims:
            key = str(c.get("key", "")).strip()
            value = str(c.get("value", "")).strip().lower()
            if not key or not value:
                continue
            by_key.setdefault(key, set()).add(value)

        if not by_key:
            return 0.0

        contradicted = sum(1 for values in by_key.values() if len(values) > 1)
        return contradicted / len(by_key)
