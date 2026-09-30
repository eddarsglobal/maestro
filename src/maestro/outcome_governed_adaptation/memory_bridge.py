from __future__ import annotations

from pathlib import Path

from maestro.outcome_intelligence import OutcomeIntelligence, OutcomeLedger, VerifiedOutcome

from .models import AdaptationCandidate


class OutcomeMemoryBridge:
    """
    Read-only bridge from durable verified Outcome Intelligence memory into
    Outcome-Governed Adaptation.

    It does not activate policy and does not manufacture outcomes.
    """

    def collect(
        self,
        outcome_intelligence: OutcomeIntelligence,
        *,
        task_family: str | None = None,
        resource_id: str | None = None,
    ) -> list[VerifiedOutcome]:
        return outcome_intelligence.ledger.query(
            task_family=task_family,
            resource_id=resource_id,
        )

    def propose(
        self,
        adaptation_engine,
        outcome_intelligence: OutcomeIntelligence,
        *,
        task_family: str | None = None,
        resource_id: str | None = None,
    ) -> list[AdaptationCandidate]:
        outcomes = self.collect(
            outcome_intelligence,
            task_family=task_family,
            resource_id=resource_id,
        )
        return adaptation_engine.propose_from_outcomes(outcomes)

    def import_verified_history(
        self,
        source_path: str | Path,
        destination: OutcomeLedger,
    ) -> dict[str, int]:
        """
        Import prior verified outcome memory while preserving outcome IDs.
        Duplicate IDs are ignored. No unverified row may be imported.
        """
        source = OutcomeLedger(source_path)
        source.load()

        existing_ids = {row.outcome_id for row in destination.all()}
        imported = 0
        duplicates = 0

        for outcome in source.all():
            if not outcome.ay_verified:
                raise ValueError(
                    "Historical outcome import contains an unverified outcome."
                )

            if outcome.outcome_id in existing_ids:
                duplicates += 1
                continue

            destination.record(outcome)
            existing_ids.add(outcome.outcome_id)
            imported += 1

        return {
            "source_rows": len(source.all()),
            "imported": imported,
            "duplicates": duplicates,
            "destination_rows": len(destination.all()),
        }
