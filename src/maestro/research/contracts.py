from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any
from urllib.parse import urlsplit
from uuid import uuid4


_SHA256_RE = re.compile(r"^[0-9a-fA-F]{64}$")
_ID_RE = re.compile(r"^(SRC|ART|CLM)-[A-F0-9]{12}$")


def _new_id(prefix: str) -> str:
    return f"{prefix}-{uuid4().hex[:12].upper()}"


def _require_nonempty(value: str, name: str) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{name} must be a string.")

    normalized = value.strip()

    if not normalized:
        raise ValueError(f"{name} must not be empty.")

    if "\x00" in normalized:
        raise ValueError(f"{name} must not contain NUL.")

    return normalized


def _require_identifier(value: str, prefix: str) -> str:
    normalized = _require_nonempty(value, f"{prefix} identifier")

    if not _ID_RE.fullmatch(normalized):
        raise ValueError(f"Invalid {prefix} identifier: {normalized!r}")

    if not normalized.startswith(prefix + "-"):
        raise ValueError(f"Identifier must use {prefix}- prefix.")

    return normalized


def _require_external_uri(value: str) -> str:
    uri = _require_nonempty(value, "source URI")
    parsed = urlsplit(uri)

    if parsed.scheme.lower() not in {"http", "https"}:
        raise ValueError(
            "RX0.1A external source URI must use http or https."
        )

    if not parsed.netloc:
        raise ValueError(
            "External source URI must contain a network authority."
        )

    return uri


def _require_aware_iso8601(value: str, name: str) -> str:
    normalized = _require_nonempty(value, name)

    candidate = normalized
    if candidate.endswith("Z"):
        candidate = candidate[:-1] + "+00:00"

    try:
        parsed = datetime.fromisoformat(candidate)
    except ValueError as exc:
        raise ValueError(
            f"{name} must be an ISO-8601 timestamp."
        ) from exc

    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(
            f"{name} must include an explicit timezone."
        )

    return normalized


class TrustState(StrEnum):
    UNTRUSTED = "UNTRUSTED"
    QUARANTINED = "QUARANTINED"
    INSPECTED = "INSPECTED"
    REJECTED = "REJECTED"


@dataclass(frozen=True, slots=True)
class ContentDigest:
    hex_digest: str
    algorithm: str = "sha256"

    def __post_init__(self) -> None:
        algorithm = _require_nonempty(
            self.algorithm,
            "digest algorithm",
        ).lower()

        if algorithm != "sha256":
            raise ValueError(
                "RX0.1A supports SHA-256 digests only."
            )

        digest = _require_nonempty(
            self.hex_digest,
            "hex digest",
        ).lower()

        if not _SHA256_RE.fullmatch(digest):
            raise ValueError(
                "SHA-256 digest must contain exactly 64 hex characters."
            )

        object.__setattr__(self, "algorithm", algorithm)
        object.__setattr__(self, "hex_digest", digest)

    @classmethod
    def from_bytes(cls, payload: bytes) -> "ContentDigest":
        if not isinstance(payload, bytes):
            raise TypeError("payload must be bytes.")

        return cls(
            hashlib.sha256(payload).hexdigest()
        )

    def to_dict(self) -> dict[str, str]:
        return {
            "algorithm": self.algorithm,
            "hex_digest": self.hex_digest,
        }


@dataclass(frozen=True, slots=True)
class ResearchSource:
    uri: str
    label: str = ""
    source_id: str = field(
        default_factory=lambda: _new_id("SRC")
    )

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "uri",
            _require_external_uri(self.uri),
        )

        if not isinstance(self.label, str):
            raise TypeError("source label must be a string.")

        label = self.label.strip()

        if "\x00" in label:
            raise ValueError(
                "source label must not contain NUL."
            )

        object.__setattr__(
            self,
            "label",
            label,
        )

        _require_identifier(
            self.source_id,
            "SRC",
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_id": self.source_id,
            "uri": self.uri,
            "label": self.label,
        }


@dataclass(frozen=True, slots=True)
class SourceProvenance:
    source_id: str
    retrieved_at: str
    digest: ContentDigest
    author: str | None = None
    license: str | None = None
    version: str | None = None

    def __post_init__(self) -> None:
        _require_identifier(
            self.source_id,
            "SRC",
        )

        object.__setattr__(
            self,
            "retrieved_at",
            _require_aware_iso8601(
                self.retrieved_at,
                "retrieved_at",
            ),
        )

        if not isinstance(self.digest, ContentDigest):
            raise TypeError(
                "digest must be a ContentDigest."
            )

        for name in (
            "author",
            "license",
            "version",
        ):
            value = getattr(self, name)

            if value is not None:
                object.__setattr__(
                    self,
                    name,
                    _require_nonempty(
                        value,
                        name,
                    ),
                )

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_id": self.source_id,
            "retrieved_at": self.retrieved_at,
            "digest": self.digest.to_dict(),
            "author": self.author,
            "license": self.license,
            "version": self.version,
        }


@dataclass(frozen=True, slots=True)
class ExternalArtifact:
    source: ResearchSource
    provenance: SourceProvenance
    artifact_kind: str
    media_type: str
    trust_state: TrustState = TrustState.UNTRUSTED
    artifact_id: str = field(
        default_factory=lambda: _new_id("ART")
    )

    def __post_init__(self) -> None:
        if not isinstance(self.source, ResearchSource):
            raise TypeError(
                "source must be a ResearchSource."
            )

        if not isinstance(
            self.provenance,
            SourceProvenance,
        ):
            raise TypeError(
                "provenance must be a SourceProvenance."
            )

        if (
            self.source.source_id
            != self.provenance.source_id
        ):
            raise ValueError(
                "Artifact source and provenance source_id must match."
            )

        object.__setattr__(
            self,
            "artifact_kind",
            _require_nonempty(
                self.artifact_kind,
                "artifact_kind",
            ),
        )

        object.__setattr__(
            self,
            "media_type",
            _require_nonempty(
                self.media_type,
                "media_type",
            ),
        )

        if not isinstance(
            self.trust_state,
            TrustState,
        ):
            raise TypeError(
                "trust_state must be a TrustState."
            )

        _require_identifier(
            self.artifact_id,
            "ART",
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "artifact_id": self.artifact_id,
            "source": self.source.to_dict(),
            "provenance": self.provenance.to_dict(),
            "artifact_kind": self.artifact_kind,
            "media_type": self.media_type,
            "trust_state": self.trust_state.value,
        }


@dataclass(frozen=True, slots=True)
class ResearchClaim:
    statement: str
    artifact_ids: tuple[str, ...]
    created_at: str
    trust_state: TrustState = TrustState.UNTRUSTED
    claim_id: str = field(
        default_factory=lambda: _new_id("CLM")
    )

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "statement",
            _require_nonempty(
                self.statement,
                "claim statement",
            ),
        )

        artifact_ids = tuple(
            self.artifact_ids
        )

        if not artifact_ids:
            raise ValueError(
                "ResearchClaim requires at least one external artifact."
            )

        for artifact_id in artifact_ids:
            _require_identifier(
                artifact_id,
                "ART",
            )

        if len(set(artifact_ids)) != len(
            artifact_ids
        ):
            raise ValueError(
                "ResearchClaim artifact_ids must be unique."
            )

        object.__setattr__(
            self,
            "artifact_ids",
            artifact_ids,
        )

        object.__setattr__(
            self,
            "created_at",
            _require_aware_iso8601(
                self.created_at,
                "created_at",
            ),
        )

        if not isinstance(
            self.trust_state,
            TrustState,
        ):
            raise TypeError(
                "trust_state must be a TrustState."
            )

        _require_identifier(
            self.claim_id,
            "CLM",
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "claim_id": self.claim_id,
            "statement": self.statement,
            "artifact_ids": list(self.artifact_ids),
            "created_at": self.created_at,
            "trust_state": self.trust_state.value,
        }
