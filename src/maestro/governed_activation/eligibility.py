from __future__ import annotations


class ActivationEligibilityGate:
    @staticmethod
    def _status_value(candidate) -> str:
        value = getattr(candidate, "status", None)
        if hasattr(value, "value"):
            value = value.value
        return str(value or "")

    @staticmethod
    def _candidate_id(candidate) -> str:
        return str(getattr(candidate, "candidate_id", "") or "")

    @staticmethod
    def _task_family(candidate) -> str:
        return str(getattr(candidate, "task_family", "") or "")

    @staticmethod
    def _proposed_change(candidate) -> dict:
        return dict(getattr(candidate, "proposed_change", {}) or {})

    def _assert_persisted_provenance(self, candidate, candidate_ledger) -> None:
        candidate_id = self._candidate_id(candidate)

        matches = [
            row
            for row in candidate_ledger.all()
            if self._candidate_id(row) == candidate_id
        ]

        if len(matches) != 1:
            raise PermissionError(
                "Activation candidate is not uniquely present in the trusted "
                "Outcome-Governed Adaptation ledger."
            )

        persisted = matches[0]

        if self._status_value(persisted) != "PROMOTION_READY":
            raise PermissionError(
                "Trusted OGA candidate is not PROMOTION_READY."
            )

        persisted_metadata = dict(
            getattr(persisted, "metadata", {}) or {}
        )

        if persisted_metadata.get("evaluation_learning_eligible") is not True:
            raise PermissionError(
                "Trusted OGA candidate lacks learning-grade evaluation provenance."
            )

        if not persisted_metadata.get("evaluation_profile_id"):
            raise PermissionError(
                "Trusted OGA candidate lacks deterministic evaluation profile ID."
            )

        if self._task_family(persisted) != self._task_family(candidate):
            raise PermissionError(
                "Activation candidate task_family does not match trusted OGA state."
            )

        if self._proposed_change(persisted) != self._proposed_change(candidate):
            raise PermissionError(
                "Activation candidate proposed_change does not match trusted OGA state."
            )

        incoming_key = getattr(candidate, "key", None)
        persisted_key = getattr(persisted, "key", None)

        if (
            incoming_key is not None
            and persisted_key is not None
            and str(incoming_key) != str(persisted_key)
        ):
            raise PermissionError(
                "Activation candidate key does not match trusted OGA state."
            )

    def assert_eligible(self, candidate, *, candidate_ledger=None) -> None:
        if self._status_value(candidate) != "PROMOTION_READY":
            raise PermissionError(
                "Activation requires a PROMOTION_READY adaptation candidate."
            )

        candidate_id = self._candidate_id(candidate)
        if not candidate_id:
            raise ValueError("candidate_id is required")

        proposed_change = self._proposed_change(candidate)
        if bool(proposed_change.get("authority_change", False)):
            raise PermissionError(
                "Activation cannot expand constitutional authority."
            )

        if candidate_ledger is not None:
            self._assert_persisted_provenance(
                candidate,
                candidate_ledger,
            )
