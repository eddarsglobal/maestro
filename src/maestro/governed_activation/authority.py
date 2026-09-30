from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from enum import Enum

from .models import ActivationSnapshot, ActivationState


class GovernanceAction(str, Enum):
    AY_VALIDATE = "AY_VALIDATE"
    EX_AUTHORIZE = "EX_AUTHORIZE"
    ROLLBACK_AY_ACK = "ROLLBACK_AY_ACK"
    ROLLBACK_EX_AUTHORIZE = "ROLLBACK_EX_AUTHORIZE"


@dataclass(frozen=True)
class GovernanceAttestation:
    actor: str
    action: GovernanceAction
    contract_id: str
    decision: str
    evidence_refs: tuple[str, ...] = field(default_factory=tuple)
    authority_ref: str | None = None
    parent_attestation_id: str | None = None
    reason: str | None = None
    attestation_id: str = field(init=False)

    def __post_init__(self) -> None:
        actor = str(self.actor or "").strip().upper()
        contract_id = str(self.contract_id or "").strip()
        decision = str(self.decision or "").strip().upper()
        refs = tuple(
            str(value).strip()
            for value in self.evidence_refs
            if str(value).strip()
        )

        if actor not in {"AY", "EX"}:
            raise ValueError("Governance attestation actor must be AY or EX.")
        if not contract_id:
            raise ValueError("Governance attestation requires contract_id.")
        if not decision:
            raise ValueError("Governance attestation requires decision.")

        object.__setattr__(self, "actor", actor)
        object.__setattr__(self, "contract_id", contract_id)
        object.__setattr__(self, "decision", decision)
        object.__setattr__(self, "evidence_refs", refs)

        if self.authority_ref is not None:
            object.__setattr__(
                self,
                "authority_ref",
                str(self.authority_ref).strip(),
            )

        if self.parent_attestation_id is not None:
            object.__setattr__(
                self,
                "parent_attestation_id",
                str(self.parent_attestation_id).strip(),
            )

        if self.reason is not None:
            object.__setattr__(
                self,
                "reason",
                str(self.reason).strip(),
            )

        object.__setattr__(
            self,
            "attestation_id",
            self._expected_id(),
        )

    def _payload(self) -> dict:
        return {
            "actor": self.actor,
            "action": self.action.value,
            "contract_id": self.contract_id,
            "decision": self.decision,
            "evidence_refs": list(self.evidence_refs),
            "authority_ref": self.authority_ref,
            "parent_attestation_id": self.parent_attestation_id,
            "reason": self.reason,
        }

    def _expected_id(self) -> str:
        raw = json.dumps(
            self._payload(),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )
        digest = hashlib.sha256(
            raw.encode("utf-8")
        ).hexdigest()[:16].upper()
        return f"GAT-{digest}"

    def assert_integrity(self) -> None:
        if self.attestation_id != self._expected_id():
            raise ValueError(
                "Governance attestation integrity check failed."
            )

    def assert_bound(
        self,
        snapshot: ActivationSnapshot,
        *,
        actor: str,
        action: GovernanceAction,
        parent_attestation_id: str | None = None,
        reason: str | None = None,
        evidence_ref: str | None = None,
    ) -> None:
        self.assert_integrity()
        snapshot.contract.assert_integrity()

        if self.contract_id != snapshot.contract_id:
            raise PermissionError(
                "Governance attestation is bound to another contract."
            )

        if self.actor != str(actor).upper():
            raise PermissionError(
                "Governance attestation actor mismatch."
            )

        if self.action is not action:
            raise PermissionError(
                "Governance attestation action mismatch."
            )

        if (
            parent_attestation_id is not None
            and self.parent_attestation_id != parent_attestation_id
        ):
            raise PermissionError(
                "Governance attestation parent-chain mismatch."
            )

        if reason is not None and self.reason != str(reason):
            raise PermissionError(
                "Governance attestation reason mismatch."
            )

        if (
            evidence_ref is not None
            and str(evidence_ref) not in self.evidence_refs
        ):
            raise PermissionError(
                "Governance attestation lacks required evidence binding."
            )

    def to_dict(self) -> dict:
        self.assert_integrity()
        return {
            **self._payload(),
            "attestation_id": self.attestation_id,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "GovernanceAttestation":
        row = cls(
            actor=str(data["actor"]),
            action=GovernanceAction(str(data["action"])),
            contract_id=str(data["contract_id"]),
            decision=str(data["decision"]),
            evidence_refs=tuple(
                str(value)
                for value in data.get("evidence_refs", ())
            ),
            authority_ref=data.get("authority_ref"),
            parent_attestation_id=data.get("parent_attestation_id"),
            reason=data.get("reason"),
        )

        expected = data.get("attestation_id")
        if expected and row.attestation_id != expected:
            raise ValueError(
                "Governance attestation integrity check failed."
            )

        return row


class GovernanceAuthority:
    """
    Deterministic provenance factory for GPA governance decisions.

    IDs are content-addressed integrity references. They are not secret-key
    signatures and must not be represented as cryptographic identity proof.
    """

    def issue_ay_validation(
        self,
        snapshot: ActivationSnapshot,
        *,
        verdict: str,
        evidence_refs,
    ) -> GovernanceAttestation:
        snapshot.contract.assert_integrity()

        if snapshot.state is not ActivationState.PROPOSED:
            raise ValueError(
                "AY attestation requires PROPOSED state."
            )

        refs = tuple(
            str(value)
            for value in evidence_refs
            if str(value)
        )
        if not refs:
            raise ValueError(
                "AY attestation requires evidence."
            )

        return GovernanceAttestation(
            actor="AY",
            action=GovernanceAction.AY_VALIDATE,
            contract_id=snapshot.contract_id,
            decision=str(verdict).upper(),
            evidence_refs=refs,
        )

    def issue_ex_authorization(
        self,
        snapshot: ActivationSnapshot,
        *,
        authorized: bool,
        authority_ref: str,
        evidence_refs=(),
    ) -> GovernanceAttestation:
        snapshot.contract.assert_integrity()

        if snapshot.state is not ActivationState.AY_VALIDATED:
            raise PermissionError(
                "EX attestation requires AY_VALIDATED state."
            )

        parent = str(
            snapshot.metadata.get("ay_attestation_id") or ""
        )
        if not parent:
            raise PermissionError(
                "EX attestation requires AY attestation provenance."
            )

        if not authority_ref:
            raise ValueError("authority_ref is required")

        return GovernanceAttestation(
            actor="EX",
            action=GovernanceAction.EX_AUTHORIZE,
            contract_id=snapshot.contract_id,
            decision="AUTHORIZED" if authorized else "DENIED",
            evidence_refs=tuple(
                str(value)
                for value in evidence_refs
                if str(value)
            ),
            authority_ref=str(authority_ref),
            parent_attestation_id=parent,
        )

    def issue_rollback_ay_ack(
        self,
        snapshot: ActivationSnapshot,
        *,
        acknowledged: bool,
        reason: str,
        evidence_ref: str,
    ) -> GovernanceAttestation:
        snapshot.contract.assert_integrity()

        if snapshot.state is not ActivationState.ACTIVE:
            raise PermissionError(
                "Rollback AY attestation requires ACTIVE state."
            )

        if not reason or not evidence_ref:
            raise ValueError(
                "Rollback AY attestation requires reason and evidence."
            )

        return GovernanceAttestation(
            actor="AY",
            action=GovernanceAction.ROLLBACK_AY_ACK,
            contract_id=snapshot.contract_id,
            decision=(
                "ACKNOWLEDGED"
                if acknowledged
                else "DENIED"
            ),
            evidence_refs=(str(evidence_ref),),
            reason=str(reason),
        )

    def issue_rollback_ex_authorization(
        self,
        snapshot: ActivationSnapshot,
        *,
        authorized: bool,
        reason: str,
        evidence_ref: str,
        authority_ref: str,
        ay_attestation: GovernanceAttestation,
    ) -> GovernanceAttestation:
        snapshot.contract.assert_integrity()

        ay_attestation.assert_bound(
            snapshot,
            actor="AY",
            action=GovernanceAction.ROLLBACK_AY_ACK,
            reason=reason,
            evidence_ref=evidence_ref,
        )

        if not authority_ref:
            raise ValueError("authority_ref is required")

        return GovernanceAttestation(
            actor="EX",
            action=GovernanceAction.ROLLBACK_EX_AUTHORIZE,
            contract_id=snapshot.contract_id,
            decision="AUTHORIZED" if authorized else "DENIED",
            evidence_refs=(str(evidence_ref),),
            authority_ref=str(authority_ref),
            parent_attestation_id=ay_attestation.attestation_id,
            reason=str(reason),
        )
