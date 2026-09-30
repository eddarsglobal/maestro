from __future__ import annotations

from dataclasses import replace
from typing import Iterable

from .models import (
    AdaptivePolicy,
    ActivationRecord,
    PolicyKind,
    PolicyStatus,
    PromotionEvidence,
)


class PolicyActivationDenied(RuntimeError):
    pass


class AdaptivePolicyManager:
    """
    Versioned policy control plane.

    Learning/Academy may REGISTER and SHADOW policies.
    Only the governed activation path may make a policy ACTIVE.
    """

    def __init__(self):
        self._policies: dict[str, AdaptivePolicy] = {}
        self._active: dict[PolicyKind, str] = {}
        self._history: list[ActivationRecord] = []

    def register(self, policy: AdaptivePolicy) -> None:
        if policy.policy_id in self._policies:
            raise ValueError(f"Duplicate policy: {policy.policy_id}")

        active = self.active(policy.kind)
        if active is not None and policy.version <= active.version:
            raise ValueError("Candidate policy version must be newer than active version.")

        self._policies[policy.policy_id] = policy

    def policy(self, policy_id: str) -> AdaptivePolicy:
        return self._policies[policy_id]

    def active(self, kind: PolicyKind) -> AdaptivePolicy | None:
        policy_id = self._active.get(kind)
        return self._policies.get(policy_id) if policy_id else None

    def set_shadow(self, policy_id: str) -> None:
        policy = self.policy(policy_id)
        if policy.status is not PolicyStatus.CANDIDATE:
            raise PolicyActivationDenied("Only CANDIDATE policies may enter SHADOW.")
        policy.status = PolicyStatus.SHADOW

    def activate(
        self,
        policy_id: str,
        *,
        evidence: PromotionEvidence,
        ay_validated: bool,
        ex_authorized: bool,
        max_regressions: int = 0,
        min_samples: int = 10,
        min_shadow_success: float = 0.90,
        require_positive_delta: bool = True,
        reason: str = "governed promotion",
    ) -> ActivationRecord:
        policy = self.policy(policy_id)

        if policy.status is not PolicyStatus.SHADOW:
            raise PolicyActivationDenied("Policy must complete SHADOW before activation.")
        if not ay_validated:
            raise PolicyActivationDenied("AY validation required.")
        if not ex_authorized:
            raise PolicyActivationDenied("EX authorization required.")
        if evidence.regression_count > max_regressions:
            raise PolicyActivationDenied("Regression budget exceeded.")
        if evidence.evaluation_samples < min_samples:
            raise PolicyActivationDenied("Insufficient evaluation sample size.")
        if evidence.shadow_success_rate < min_shadow_success:
            raise PolicyActivationDenied("Shadow success rate below threshold.")
        if not evidence.academy_recommended:
            raise PolicyActivationDenied("Academy recommendation/evaluation required.")
        if require_positive_delta and evidence.delta <= 0:
            raise PolicyActivationDenied("Candidate does not improve baseline score.")

        previous = self.active(policy.kind)
        if previous is not None:
            previous.status = PolicyStatus.RETIRED

        policy.status = PolicyStatus.ACTIVE
        self._active[policy.kind] = policy.policy_id

        record = ActivationRecord(
            policy_id=policy.policy_id,
            kind=policy.kind,
            previous_policy_id=previous.policy_id if previous else None,
            action="ACTIVATE",
            reason=reason,
        )
        self._history.append(record)
        return record

    def bootstrap_active(self, policy: AdaptivePolicy) -> None:
        """
        Used only for a known-safe genesis/default policy during bootstrap.
        """
        if self.active(policy.kind) is not None:
            raise PolicyActivationDenied("Active policy already exists for this kind.")
        if policy.policy_id not in self._policies:
            self.register(policy)
        policy.status = PolicyStatus.ACTIVE
        self._active[policy.kind] = policy.policy_id
        self._history.append(
            ActivationRecord(
                policy_id=policy.policy_id,
                kind=policy.kind,
                previous_policy_id=None,
                action="BOOTSTRAP",
                reason="known-safe genesis policy",
            )
        )

    def rollback(
        self,
        kind: PolicyKind,
        *,
        ex_authorized: bool,
        ay_acknowledged: bool,
        reason: str,
    ) -> ActivationRecord:
        if not ex_authorized:
            raise PolicyActivationDenied("EX authorization required for rollback.")
        if not ay_acknowledged:
            raise PolicyActivationDenied("AY acknowledgement required for governed rollback.")

        current = self.active(kind)
        if current is None:
            raise PolicyActivationDenied("No active policy to rollback.")

        prior_ids = [
            r.previous_policy_id
            for r in reversed(self._history)
            if r.kind is kind and r.policy_id == current.policy_id and r.previous_policy_id
        ]
        if not prior_ids:
            raise PolicyActivationDenied("No previous policy available for rollback.")

        previous = self.policy(prior_ids[0])
        current.status = PolicyStatus.RETIRED
        previous.status = PolicyStatus.ACTIVE
        self._active[kind] = previous.policy_id

        record = ActivationRecord(
            policy_id=previous.policy_id,
            kind=kind,
            previous_policy_id=current.policy_id,
            action="ROLLBACK",
            reason=reason,
        )
        self._history.append(record)
        return record

    def history(self) -> list[ActivationRecord]:
        return list(self._history)

    def all_for_kind(self, kind: PolicyKind) -> list[AdaptivePolicy]:
        return sorted(
            [p for p in self._policies.values() if p.kind is kind],
            key=lambda p: p.version,
        )
