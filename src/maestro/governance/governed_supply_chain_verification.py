from __future__ import annotations

import hashlib
import json
import re

from dataclasses import dataclass
from enum import StrEnum
from typing import Any


GOVERNED_SUPPLY_CHAIN_VERIFICATION_VERSION = 1

_SHA256_RE = re.compile(
    r"^[0-9a-fA-F]{64}$"
)


class GovernedSupplyChainInvariantError(
    ValueError
):
    pass


class ArtifactKind(StrEnum):
    ADAPTER = "ADAPTER"
    UPDATE = "UPDATE"


class IntegrityState(StrEnum):
    VERIFIED = "VERIFIED"
    FAILED = "FAILED"


class SignatureState(StrEnum):
    ABSENT = "ABSENT"
    UNKNOWN = "UNKNOWN"
    VALID = "VALID"
    INVALID = "INVALID"


class ProvenanceState(StrEnum):
    UNKNOWN = "UNKNOWN"
    VERIFIED = "VERIFIED"
    FAILED = "FAILED"


class ArtifactVerificationState(StrEnum):
    VERIFIED = "VERIFIED"
    FAILED = "FAILED"
    INCOMPLETE = "INCOMPLETE"


def _required_text(
    value: str,
    name: str,
) -> str:
    if not isinstance(value, str):
        raise TypeError(
            f"{name} must be a string."
        )

    normalized = value.strip()

    if not normalized:
        raise ValueError(
            f"{name} must not be empty."
        )

    if "\x00" in normalized:
        raise ValueError(
            f"{name} must not contain NUL."
        )

    return normalized


def _optional_text(
    value: str | None,
    name: str,
) -> str | None:
    if value is None:
        return None

    return _required_text(
        value,
        name,
    )


def _sha256(
    payload: bytes,
) -> str:
    if not isinstance(
        payload,
        bytes,
    ):
        raise TypeError(
            "artifact_bytes must be bytes."
        )

    return hashlib.sha256(
        payload
    ).hexdigest()


def _require_sha256(
    value: str,
    name: str,
) -> str:
    normalized = _required_text(
        value,
        name,
    ).lower()

    if not _SHA256_RE.fullmatch(
        normalized
    ):
        raise (
            GovernedSupplyChainInvariantError(
                f"{name} must be a "
                "64-character SHA-256 hex digest."
            )
        )

    return normalized


def _stable_id(
    prefix: str,
    payload: dict[str, Any],
) -> str:
    canonical = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )

    digest = hashlib.sha256(
        canonical.encode("utf-8")
    ).hexdigest()

    return f"{prefix}-{digest[:24]}"


def _assert_no_authority(
    *,
    trusted: bool,
    installation_authorized: bool,
    installed: bool,
    activation_authorized: bool,
    activated: bool,
    execution_authorized: bool,
    executed: bool,
    core_mutation_requested: bool,
    observability_system_created: bool,
    system_truth_asserted: bool,
) -> None:
    flags = {
        "trusted": trusted,
        "installation_authorized": (
            installation_authorized
        ),
        "installed": installed,
        "activation_authorized": (
            activation_authorized
        ),
        "activated": activated,
        "execution_authorized": (
            execution_authorized
        ),
        "executed": executed,
        "core_mutation_requested": (
            core_mutation_requested
        ),
        "observability_system_created": (
            observability_system_created
        ),
        "system_truth_asserted": (
            system_truth_asserted
        ),
    }

    asserted = sorted(
        name
        for name, value in flags.items()
        if value is not False
    )

    if asserted:
        raise (
            GovernedSupplyChainInvariantError(
                "Supply-chain verification "
                "cannot assert downstream authority: "
                + ", ".join(asserted)
            )
        )


@dataclass(
    frozen=True,
    slots=True,
)
class ArtifactManifest:
    artifact_id: str
    artifact_kind: ArtifactKind
    artifact_version: str

    origin_id: str
    source_ref: str

    digest_algorithm: str
    expected_digest: str

    signer_id: str | None = None
    signature_algorithm: str | None = None

    def __post_init__(
        self,
    ) -> None:
        for name in (
            "artifact_id",
            "artifact_version",
            "origin_id",
            "source_ref",
        ):
            object.__setattr__(
                self,
                name,
                _required_text(
                    getattr(self, name),
                    name,
                ),
            )

        if not isinstance(
            self.artifact_kind,
            ArtifactKind,
        ):
            raise TypeError(
                "artifact_kind must be "
                "ArtifactKind."
            )

        algorithm = _required_text(
            self.digest_algorithm,
            "digest_algorithm",
        ).lower()

        if algorithm != "sha256":
            raise (
                GovernedSupplyChainInvariantError(
                    "SCV0.1 supports SHA-256 "
                    "artifact integrity only."
                )
            )

        object.__setattr__(
            self,
            "digest_algorithm",
            algorithm,
        )

        object.__setattr__(
            self,
            "expected_digest",
            _require_sha256(
                self.expected_digest,
                "expected_digest",
            ),
        )

        signer = _optional_text(
            self.signer_id,
            "signer_id",
        )

        signature_algorithm = _optional_text(
            self.signature_algorithm,
            "signature_algorithm",
        )

        if (
            signer is None
        ) != (
            signature_algorithm is None
        ):
            raise (
                GovernedSupplyChainInvariantError(
                    "signer_id and "
                    "signature_algorithm must "
                    "both be present or absent."
                )
            )

        object.__setattr__(
            self,
            "signer_id",
            signer,
        )

        object.__setattr__(
            self,
            "signature_algorithm",
            signature_algorithm,
        )

    def to_dict(
        self,
    ) -> dict[str, Any]:
        return {
            "artifact_id": self.artifact_id,
            "artifact_kind": (
                self.artifact_kind.value
            ),
            "artifact_version": (
                self.artifact_version
            ),
            "origin_id": self.origin_id,
            "source_ref": self.source_ref,
            "digest_algorithm": (
                self.digest_algorithm
            ),
            "expected_digest": (
                self.expected_digest
            ),
            "signer_id": self.signer_id,
            "signature_algorithm": (
                self.signature_algorithm
            ),
        }


@dataclass(
    frozen=True,
    slots=True,
)
class ArtifactProvenanceClaim:
    artifact_id: str
    artifact_version: str

    origin_id: str
    source_ref: str

    digest_algorithm: str
    digest: str

    def __post_init__(
        self,
    ) -> None:
        for name in (
            "artifact_id",
            "artifact_version",
            "origin_id",
            "source_ref",
        ):
            object.__setattr__(
                self,
                name,
                _required_text(
                    getattr(self, name),
                    name,
                ),
            )

        algorithm = _required_text(
            self.digest_algorithm,
            "digest_algorithm",
        ).lower()

        if algorithm != "sha256":
            raise (
                GovernedSupplyChainInvariantError(
                    "SCV0.1 supports SHA-256 "
                    "provenance digests only."
                )
            )

        object.__setattr__(
            self,
            "digest_algorithm",
            algorithm,
        )

        object.__setattr__(
            self,
            "digest",
            _require_sha256(
                self.digest,
                "digest",
            ),
        )

    def to_dict(
        self,
    ) -> dict[str, Any]:
        return {
            "artifact_id": self.artifact_id,
            "artifact_version": (
                self.artifact_version
            ),
            "origin_id": self.origin_id,
            "source_ref": self.source_ref,
            "digest_algorithm": (
                self.digest_algorithm
            ),
            "digest": self.digest,
        }


@dataclass(
    frozen=True,
    slots=True,
)
class SignatureVerificationEvidence:
    evidence_id: str

    artifact_id: str
    artifact_digest: str

    signer_id: str
    signature_algorithm: str

    signature_present: bool
    cryptographically_verified: bool | None

    verifier_ref: str

    def __post_init__(
        self,
    ) -> None:
        for name in (
            "evidence_id",
            "artifact_id",
            "signer_id",
            "signature_algorithm",
            "verifier_ref",
        ):
            object.__setattr__(
                self,
                name,
                _required_text(
                    getattr(self, name),
                    name,
                ),
            )

        object.__setattr__(
            self,
            "artifact_digest",
            _require_sha256(
                self.artifact_digest,
                "artifact_digest",
            ),
        )

        if not isinstance(
            self.signature_present,
            bool,
        ):
            raise TypeError(
                "signature_present must be bool."
            )

        if (
            self.cryptographically_verified
            is not None
            and not isinstance(
                self.cryptographically_verified,
                bool,
            )
        ):
            raise TypeError(
                "cryptographically_verified "
                "must be bool or None."
            )

        if (
            not self.signature_present
            and self.cryptographically_verified
            is not None
        ):
            raise (
                GovernedSupplyChainInvariantError(
                    "Absent signature cannot have "
                    "cryptographic verification state."
                )
            )


@dataclass(
    frozen=True,
    slots=True,
)
class GovernedArtifactVerification:
    verification_id: str

    artifact_id: str
    artifact_kind: ArtifactKind
    artifact_version: str

    origin_id: str
    source_ref: str

    expected_digest: str
    observed_digest: str

    integrity_state: IntegrityState
    signature_state: SignatureState
    provenance_state: ProvenanceState
    verification_state: ArtifactVerificationState

    signature_evidence_id: str | None = None

    trusted: bool = False
    installation_authorized: bool = False
    installed: bool = False
    activation_authorized: bool = False
    activated: bool = False
    execution_authorized: bool = False
    executed: bool = False
    core_mutation_requested: bool = False
    observability_system_created: bool = False
    system_truth_asserted: bool = False

    def __post_init__(
        self,
    ) -> None:
        for name in (
            "verification_id",
            "artifact_id",
            "artifact_version",
            "origin_id",
            "source_ref",
        ):
            object.__setattr__(
                self,
                name,
                _required_text(
                    getattr(self, name),
                    name,
                ),
            )

        if not isinstance(
            self.artifact_kind,
            ArtifactKind,
        ):
            raise TypeError(
                "artifact_kind must be "
                "ArtifactKind."
            )

        object.__setattr__(
            self,
            "expected_digest",
            _require_sha256(
                self.expected_digest,
                "expected_digest",
            ),
        )

        object.__setattr__(
            self,
            "observed_digest",
            _require_sha256(
                self.observed_digest,
                "observed_digest",
            ),
        )

        if not isinstance(
            self.integrity_state,
            IntegrityState,
        ):
            raise TypeError(
                "integrity_state must be "
                "IntegrityState."
            )

        if not isinstance(
            self.signature_state,
            SignatureState,
        ):
            raise TypeError(
                "signature_state must be "
                "SignatureState."
            )

        if not isinstance(
            self.provenance_state,
            ProvenanceState,
        ):
            raise TypeError(
                "provenance_state must be "
                "ProvenanceState."
            )

        if not isinstance(
            self.verification_state,
            ArtifactVerificationState,
        ):
            raise TypeError(
                "verification_state must be "
                "ArtifactVerificationState."
            )

        evidence_id = _optional_text(
            self.signature_evidence_id,
            "signature_evidence_id",
        )

        object.__setattr__(
            self,
            "signature_evidence_id",
            evidence_id,
        )

        expected_integrity = (
            IntegrityState.VERIFIED
            if self.expected_digest
            == self.observed_digest
            else IntegrityState.FAILED
        )

        if (
            self.integrity_state
            is not expected_integrity
        ):
            raise (
                GovernedSupplyChainInvariantError(
                    "integrity_state does not "
                    "match artifact digest comparison."
                )
            )

        if (
            self.signature_state
            is SignatureState.VALID
            and evidence_id is None
        ):
            raise (
                GovernedSupplyChainInvariantError(
                    "VALID signature requires "
                    "signature evidence."
                )
            )

        if (
            self.provenance_state
            is ProvenanceState.VERIFIED
            and (
                self.signature_state
                is not SignatureState.VALID
                or evidence_id is None
            )
        ):
            raise (
                GovernedSupplyChainInvariantError(
                    "VERIFIED provenance requires "
                    "VALID signature evidence."
                )
            )

        if (
            self.signature_state
            is SignatureState.VALID
            and self.provenance_state
            is ProvenanceState.UNKNOWN
        ):
            raise (
                GovernedSupplyChainInvariantError(
                    "VALID signature evidence cannot "
                    "leave provenance UNKNOWN."
                )
            )

        if (
            self.verification_state
            is ArtifactVerificationState.VERIFIED
            and (
                self.integrity_state
                is not IntegrityState.VERIFIED
                or self.provenance_state
                is not ProvenanceState.VERIFIED
            )
        ):
            raise (
                GovernedSupplyChainInvariantError(
                    "VERIFIED artifact requires "
                    "verified integrity and provenance."
                )
            )

        if (
            self.integrity_state
            is IntegrityState.FAILED
            or self.provenance_state
            is ProvenanceState.FAILED
            or self.signature_state
            is SignatureState.INVALID
        ):
            expected_verification = (
                ArtifactVerificationState.FAILED
            )
        elif (
            self.integrity_state
            is IntegrityState.VERIFIED
            and self.provenance_state
            is ProvenanceState.VERIFIED
        ):
            expected_verification = (
                ArtifactVerificationState.VERIFIED
            )
        else:
            expected_verification = (
                ArtifactVerificationState.INCOMPLETE
            )

        if (
            self.verification_state
            is not expected_verification
        ):
            raise (
                GovernedSupplyChainInvariantError(
                    "verification_state does not "
                    "match integrity/provenance state."
                )
            )

        _assert_no_authority(
            trusted=self.trusted,
            installation_authorized=(
                self.installation_authorized
            ),
            installed=self.installed,
            activation_authorized=(
                self.activation_authorized
            ),
            activated=self.activated,
            execution_authorized=(
                self.execution_authorized
            ),
            executed=self.executed,
            core_mutation_requested=(
                self.core_mutation_requested
            ),
            observability_system_created=(
                self.observability_system_created
            ),
            system_truth_asserted=(
                self.system_truth_asserted
            ),
        )

    def to_dict(
        self,
    ) -> dict[str, Any]:
        return {
            "version": (
                GOVERNED_SUPPLY_CHAIN_VERIFICATION_VERSION
            ),
            "verification_id": (
                self.verification_id
            ),
            "artifact_id": self.artifact_id,
            "artifact_kind": (
                self.artifact_kind.value
            ),
            "artifact_version": (
                self.artifact_version
            ),
            "origin_id": self.origin_id,
            "source_ref": self.source_ref,
            "expected_digest": (
                self.expected_digest
            ),
            "observed_digest": (
                self.observed_digest
            ),
            "integrity_state": (
                self.integrity_state.value
            ),
            "signature_state": (
                self.signature_state.value
            ),
            "provenance_state": (
                self.provenance_state.value
            ),
            "verification_state": (
                self.verification_state.value
            ),
            "signature_evidence_id": (
                self.signature_evidence_id
            ),
            "trusted": False,
            "installation_authorized": False,
            "installed": False,
            "activation_authorized": False,
            "activated": False,
            "execution_authorized": False,
            "executed": False,
            "core_mutation_requested": False,
            "observability_system_created": False,
            "system_truth_asserted": False,
        }


class GovernedSupplyChainVerifier:
    @classmethod
    def verify(
        cls,
        manifest: ArtifactManifest,
        *,
        artifact_bytes: bytes,
        provenance: ArtifactProvenanceClaim,
        signature_evidence: (
            SignatureVerificationEvidence
            | None
        ) = None,
    ) -> GovernedArtifactVerification:
        if not isinstance(
            manifest,
            ArtifactManifest,
        ):
            raise TypeError(
                "manifest must be ArtifactManifest."
            )

        if not isinstance(
            provenance,
            ArtifactProvenanceClaim,
        ):
            raise TypeError(
                "provenance must be "
                "ArtifactProvenanceClaim."
            )

        observed_digest = _sha256(
            artifact_bytes
        )

        integrity_state = (
            IntegrityState.VERIFIED
            if observed_digest
            == manifest.expected_digest
            else IntegrityState.FAILED
        )

        provenance_matches = (
            provenance.artifact_id
            == manifest.artifact_id
            and provenance.artifact_version
            == manifest.artifact_version
            and provenance.origin_id
            == manifest.origin_id
            and provenance.source_ref
            == manifest.source_ref
            and provenance.digest_algorithm
            == manifest.digest_algorithm
            and provenance.digest
            == manifest.expected_digest
        )

        signature_state = (
            SignatureState.ABSENT
        )

        signature_evidence_id = None

        if signature_evidence is not None:
            if not isinstance(
                signature_evidence,
                SignatureVerificationEvidence,
            ):
                raise TypeError(
                    "signature_evidence must be "
                    "SignatureVerificationEvidence."
                )

            signature_evidence_id = (
                signature_evidence.evidence_id
            )

            signature_binding_matches = (
                signature_evidence.artifact_id
                == manifest.artifact_id
                and signature_evidence.artifact_digest
                == manifest.expected_digest
                and manifest.signer_id is not None
                and signature_evidence.signer_id
                == manifest.signer_id
                and manifest.signature_algorithm
                is not None
                and (
                    signature_evidence
                    .signature_algorithm
                    == manifest.signature_algorithm
                )
            )

            if (
                not signature_evidence
                .signature_present
            ):
                signature_state = (
                    SignatureState.ABSENT
                )

            elif not signature_binding_matches:
                signature_state = (
                    SignatureState.INVALID
                )

            elif (
                signature_evidence
                .cryptographically_verified
                is True
            ):
                signature_state = (
                    SignatureState.VALID
                )

            elif (
                signature_evidence
                .cryptographically_verified
                is False
            ):
                signature_state = (
                    SignatureState.INVALID
                )

            else:
                signature_state = (
                    SignatureState.UNKNOWN
                )

        if not provenance_matches:
            provenance_state = (
                ProvenanceState.FAILED
            )

        elif manifest.signer_id is None:
            provenance_state = (
                ProvenanceState.UNKNOWN
            )

        elif (
            signature_state
            is SignatureState.VALID
        ):
            provenance_state = (
                ProvenanceState.VERIFIED
            )

        elif (
            signature_state
            is SignatureState.INVALID
        ):
            provenance_state = (
                ProvenanceState.FAILED
            )

        else:
            provenance_state = (
                ProvenanceState.UNKNOWN
            )

        if (
            integrity_state
            is IntegrityState.FAILED
            or provenance_state
            is ProvenanceState.FAILED
            or signature_state
            is SignatureState.INVALID
        ):
            verification_state = (
                ArtifactVerificationState.FAILED
            )

        elif (
            integrity_state
            is IntegrityState.VERIFIED
            and provenance_state
            is ProvenanceState.VERIFIED
        ):
            verification_state = (
                ArtifactVerificationState.VERIFIED
            )

        else:
            verification_state = (
                ArtifactVerificationState.INCOMPLETE
            )

        payload = {
            "artifact_id": (
                manifest.artifact_id
            ),
            "artifact_kind": (
                manifest.artifact_kind.value
            ),
            "artifact_version": (
                manifest.artifact_version
            ),
            "expected_digest": (
                manifest.expected_digest
            ),
            "observed_digest": (
                observed_digest
            ),
            "integrity_state": (
                integrity_state.value
            ),
            "signature_state": (
                signature_state.value
            ),
            "provenance_state": (
                provenance_state.value
            ),
            "signature_evidence_id": (
                signature_evidence_id
            ),
        }

        return GovernedArtifactVerification(
            verification_id=_stable_id(
                "SCV",
                payload,
            ),
            artifact_id=(
                manifest.artifact_id
            ),
            artifact_kind=(
                manifest.artifact_kind
            ),
            artifact_version=(
                manifest.artifact_version
            ),
            origin_id=(
                manifest.origin_id
            ),
            source_ref=(
                manifest.source_ref
            ),
            expected_digest=(
                manifest.expected_digest
            ),
            observed_digest=(
                observed_digest
            ),
            integrity_state=(
                integrity_state
            ),
            signature_state=(
                signature_state
            ),
            provenance_state=(
                provenance_state
            ),
            verification_state=(
                verification_state
            ),
            signature_evidence_id=(
                signature_evidence_id
            ),
        )


__all__ = [
    "GOVERNED_SUPPLY_CHAIN_VERIFICATION_VERSION",
    "GovernedSupplyChainInvariantError",
    "ArtifactKind",
    "IntegrityState",
    "SignatureState",
    "ProvenanceState",
    "ArtifactVerificationState",
    "ArtifactManifest",
    "ArtifactProvenanceClaim",
    "SignatureVerificationEvidence",
    "GovernedArtifactVerification",
    "GovernedSupplyChainVerifier",
]
