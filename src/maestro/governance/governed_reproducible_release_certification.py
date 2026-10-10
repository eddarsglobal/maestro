from __future__ import annotations

import hashlib
import json
import re

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


GOVERNED_REPRODUCIBLE_RELEASE_CERTIFICATION_VERSION = 1

_SHA256_RE = re.compile(
    r"^[0-9a-f]{64}$"
)


class GovernedReleaseInvariantError(
    ValueError
):
    pass


class GateEvidenceState(StrEnum):
    PASS = "PASS"
    FAIL = "FAIL"
    UNKNOWN = "UNKNOWN"


class PlatformCertificationState(StrEnum):
    PASS = "PASS"
    FAILED = "FAILED"
    INCOMPLETE = "INCOMPLETE"


class ReleaseCertificationState(StrEnum):
    PASS = "PASS"
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
        raise GovernedReleaseInvariantError(
            f"{name} must not be empty."
        )

    if "\x00" in normalized:
        raise GovernedReleaseInvariantError(
            f"{name} must not contain NUL."
        )

    return normalized


def _optional_sha256(
    value: str | None,
    name: str,
) -> str | None:
    if value is None:
        return None

    normalized = _required_text(
        value,
        name,
    ).lower()

    if not _SHA256_RE.fullmatch(
        normalized
    ):
        raise GovernedReleaseInvariantError(
            f"{name} must be a "
            "64-character SHA-256 hex digest."
        )

    return normalized


def _required_sha256(
    value: str,
    name: str,
) -> str:
    normalized = _optional_sha256(
        value,
        name,
    )

    if normalized is None:
        raise GovernedReleaseInvariantError(
            f"{name} is required."
        )

    return normalized


def _sha256(
    payload: bytes,
) -> str:
    return hashlib.sha256(
        payload
    ).hexdigest()


def _stable_id(
    prefix: str,
    payload: dict[str, Any],
) -> str:
    canonical = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    )

    return (
        prefix
        + "-"
        + _sha256(
            canonical.encode("utf-8")
        )[:24]
    )


def _assert_passive(
    *,
    trusted: bool,
    release_authorized: bool,
    publish_authorized: bool,
    deploy_authorized: bool,
    tag_mutation_authorized: bool,
    core_mutation_requested: bool,
    universal_support_asserted: bool,
    system_truth_asserted: bool,
) -> None:
    flags = {
        "trusted": trusted,
        "release_authorized": (
            release_authorized
        ),
        "publish_authorized": (
            publish_authorized
        ),
        "deploy_authorized": (
            deploy_authorized
        ),
        "tag_mutation_authorized": (
            tag_mutation_authorized
        ),
        "core_mutation_requested": (
            core_mutation_requested
        ),
        "universal_support_asserted": (
            universal_support_asserted
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
        raise GovernedReleaseInvariantError(
            "Release certification evidence "
            "cannot assert downstream authority: "
            + ", ".join(asserted)
        )


@dataclass(
    frozen=True,
    slots=True,
)
class ReproducibleReleaseManifest:
    release_id: str
    release_version: str

    core_source_digest: str
    constitutional_fingerprint: str

    supported_platform_ids: tuple[
        str,
        ...,
    ]

    build_recipe_id: str

    manifest_id: str = field(
        init=False
    )

    def __post_init__(
        self,
    ) -> None:
        for name in (
            "release_id",
            "release_version",
            "build_recipe_id",
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
            "core_source_digest",
            _required_sha256(
                self.core_source_digest,
                "core_source_digest",
            ),
        )

        object.__setattr__(
            self,
            "constitutional_fingerprint",
            _required_sha256(
                self.constitutional_fingerprint,
                "constitutional_fingerprint",
            ),
        )

        platforms = tuple(
            sorted(
                _required_text(
                    item,
                    "supported_platform_id",
                )
                for item
                in self.supported_platform_ids
            )
        )

        if not platforms:
            raise GovernedReleaseInvariantError(
                "Release manifest requires at "
                "least one supported platform."
            )

        if len(platforms) != len(
            set(platforms)
        ):
            raise GovernedReleaseInvariantError(
                "Supported platform IDs "
                "must be unique."
            )

        object.__setattr__(
            self,
            "supported_platform_ids",
            platforms,
        )

        payload = {
            "version": (
                GOVERNED_REPRODUCIBLE_RELEASE_CERTIFICATION_VERSION
            ),
            "release_id": self.release_id,
            "release_version": (
                self.release_version
            ),
            "core_source_digest": (
                self.core_source_digest
            ),
            "constitutional_fingerprint": (
                self.constitutional_fingerprint
            ),
            "supported_platform_ids": (
                list(platforms)
            ),
            "build_recipe_id": (
                self.build_recipe_id
            ),
        }

        object.__setattr__(
            self,
            "manifest_id",
            _stable_id(
                "RRM",
                payload,
            ),
        )

    def to_dict(
        self,
    ) -> dict[str, Any]:
        return {
            "version": (
                GOVERNED_REPRODUCIBLE_RELEASE_CERTIFICATION_VERSION
            ),
            "manifest_id": self.manifest_id,
            "release_id": self.release_id,
            "release_version": (
                self.release_version
            ),
            "core_source_digest": (
                self.core_source_digest
            ),
            "constitutional_fingerprint": (
                self.constitutional_fingerprint
            ),
            "supported_platform_ids": list(
                self.supported_platform_ids
            ),
            "build_recipe_id": (
                self.build_recipe_id
            ),
        }


@dataclass(
    frozen=True,
    slots=True,
)
class PlatformGateEvidence:
    platform_id: str

    build_state: GateEvidenceState
    test_state: GateEvidenceState

    artifact_id: str

    artifact_digest: str | None
    reproduced_artifact_digest: (
        str | None
    )

    core_source_digest: str | None
    constitutional_fingerprint: (
        str | None
    )

    source_ref: str

    evidence_id: str = field(
        init=False
    )

    def __post_init__(
        self,
    ) -> None:
        for name in (
            "platform_id",
            "artifact_id",
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
            self.build_state,
            GateEvidenceState,
        ):
            raise TypeError(
                "build_state must be "
                "GateEvidenceState."
            )

        if not isinstance(
            self.test_state,
            GateEvidenceState,
        ):
            raise TypeError(
                "test_state must be "
                "GateEvidenceState."
            )

        for name in (
            "artifact_digest",
            "reproduced_artifact_digest",
            "core_source_digest",
            "constitutional_fingerprint",
        ):
            object.__setattr__(
                self,
                name,
                _optional_sha256(
                    getattr(self, name),
                    name,
                ),
            )

        payload = {
            "platform_id": self.platform_id,
            "build_state": (
                self.build_state.value
            ),
            "test_state": (
                self.test_state.value
            ),
            "artifact_id": (
                self.artifact_id
            ),
            "artifact_digest": (
                self.artifact_digest
            ),
            "reproduced_artifact_digest": (
                self.reproduced_artifact_digest
            ),
            "core_source_digest": (
                self.core_source_digest
            ),
            "constitutional_fingerprint": (
                self.constitutional_fingerprint
            ),
            "source_ref": self.source_ref,
        }

        object.__setattr__(
            self,
            "evidence_id",
            _stable_id(
                "RPE",
                payload,
            ),
        )

    def to_dict(
        self,
    ) -> dict[str, Any]:
        return {
            "evidence_id": (
                self.evidence_id
            ),
            "platform_id": (
                self.platform_id
            ),
            "build_state": (
                self.build_state.value
            ),
            "test_state": (
                self.test_state.value
            ),
            "artifact_id": (
                self.artifact_id
            ),
            "artifact_digest": (
                self.artifact_digest
            ),
            "reproduced_artifact_digest": (
                self.reproduced_artifact_digest
            ),
            "core_source_digest": (
                self.core_source_digest
            ),
            "constitutional_fingerprint": (
                self.constitutional_fingerprint
            ),
            "source_ref": (
                self.source_ref
            ),
        }


def _derive_platform_state(
    *,
    manifest: ReproducibleReleaseManifest,
    evidence: PlatformGateEvidence,
) -> tuple[
    PlatformCertificationState,
    tuple[str, ...],
]:
    failed: list[str] = []
    incomplete: list[str] = []

    if (
        evidence.build_state
        is GateEvidenceState.FAIL
    ):
        failed.append(
            "build gate failed"
        )

    elif (
        evidence.build_state
        is GateEvidenceState.UNKNOWN
    ):
        incomplete.append(
            "build gate unknown"
        )

    if (
        evidence.test_state
        is GateEvidenceState.FAIL
    ):
        failed.append(
            "test gate failed"
        )

    elif (
        evidence.test_state
        is GateEvidenceState.UNKNOWN
    ):
        incomplete.append(
            "test gate unknown"
        )

    if (
        evidence.core_source_digest
        is None
    ):
        incomplete.append(
            "core source digest missing"
        )

    elif (
        evidence.core_source_digest
        != manifest.core_source_digest
    ):
        failed.append(
            "core source digest mismatch"
        )

    if (
        evidence.constitutional_fingerprint
        is None
    ):
        incomplete.append(
            "constitutional fingerprint missing"
        )

    elif (
        evidence.constitutional_fingerprint
        != manifest.constitutional_fingerprint
    ):
        failed.append(
            "constitutional fingerprint mismatch"
        )

    if evidence.artifact_digest is None:
        incomplete.append(
            "artifact digest missing"
        )

    if (
        evidence.reproduced_artifact_digest
        is None
    ):
        incomplete.append(
            "reproduced artifact digest missing"
        )

    if (
        evidence.artifact_digest
        is not None
        and
        evidence.reproduced_artifact_digest
        is not None
        and
        evidence.artifact_digest
        != evidence.reproduced_artifact_digest
    ):
        failed.append(
            "artifact reproducibility mismatch"
        )

    if failed:
        return (
            PlatformCertificationState.FAILED,
            tuple(
                failed
                + incomplete
            ),
        )

    if incomplete:
        return (
            PlatformCertificationState.INCOMPLETE,
            tuple(incomplete),
        )

    return (
        PlatformCertificationState.PASS,
        (),
    )


@dataclass(
    frozen=True,
    slots=True,
)
class GovernedPlatformCertification:
    manifest: ReproducibleReleaseManifest
    evidence: PlatformGateEvidence

    certification_id: str = field(
        init=False
    )

    state: PlatformCertificationState = (
        field(
            init=False
        )
    )

    reasons: tuple[
        str,
        ...,
    ] = field(
        init=False
    )

    trusted: bool = False
    release_authorized: bool = False
    publish_authorized: bool = False
    deploy_authorized: bool = False
    tag_mutation_authorized: bool = False
    core_mutation_requested: bool = False
    universal_support_asserted: bool = False
    system_truth_asserted: bool = False

    def __post_init__(
        self,
    ) -> None:
        if not isinstance(
            self.manifest,
            ReproducibleReleaseManifest,
        ):
            raise TypeError(
                "manifest must be "
                "ReproducibleReleaseManifest."
            )

        if not isinstance(
            self.evidence,
            PlatformGateEvidence,
        ):
            raise TypeError(
                "evidence must be "
                "PlatformGateEvidence."
            )

        if (
            self.evidence.platform_id
            not in
            self.manifest.supported_platform_ids
        ):
            raise GovernedReleaseInvariantError(
                "Platform evidence is not "
                "declared in the supported "
                "platform set."
            )

        state, reasons = (
            _derive_platform_state(
                manifest=self.manifest,
                evidence=self.evidence,
            )
        )

        object.__setattr__(
            self,
            "state",
            state,
        )

        object.__setattr__(
            self,
            "reasons",
            reasons,
        )

        payload = {
            "manifest_id": (
                self.manifest.manifest_id
            ),
            "evidence_id": (
                self.evidence.evidence_id
            ),
            "platform_id": (
                self.evidence.platform_id
            ),
            "state": state.value,
            "reasons": list(reasons),
        }

        object.__setattr__(
            self,
            "certification_id",
            _stable_id(
                "RPC",
                payload,
            ),
        )

        _assert_passive(
            trusted=self.trusted,
            release_authorized=(
                self.release_authorized
            ),
            publish_authorized=(
                self.publish_authorized
            ),
            deploy_authorized=(
                self.deploy_authorized
            ),
            tag_mutation_authorized=(
                self.tag_mutation_authorized
            ),
            core_mutation_requested=(
                self.core_mutation_requested
            ),
            universal_support_asserted=(
                self.universal_support_asserted
            ),
            system_truth_asserted=(
                self.system_truth_asserted
            ),
        )

    @property
    def platform_id(
        self,
    ) -> str:
        return self.evidence.platform_id

    def to_dict(
        self,
    ) -> dict[str, Any]:
        return {
            "certification_id": (
                self.certification_id
            ),
            "manifest_id": (
                self.manifest.manifest_id
            ),
            "platform_id": (
                self.platform_id
            ),
            "state": self.state.value,
            "reasons": list(
                self.reasons
            ),
            "evidence": (
                self.evidence.to_dict()
            ),
            "trusted": False,
            "release_authorized": False,
            "publish_authorized": False,
            "deploy_authorized": False,
            "tag_mutation_authorized": False,
            "core_mutation_requested": False,
            "universal_support_asserted": False,
            "system_truth_asserted": False,
        }


@dataclass(
    frozen=True,
    slots=True,
)
class GovernedReleaseCertificationResult:
    manifest: ReproducibleReleaseManifest

    platform_certifications: tuple[
        GovernedPlatformCertification,
        ...,
    ]

    certification_id: str = field(
        init=False
    )

    state: ReleaseCertificationState = (
        field(
            init=False
        )
    )

    passed_platform_ids: tuple[
        str,
        ...,
    ] = field(
        init=False
    )

    missing_platform_ids: tuple[
        str,
        ...,
    ] = field(
        init=False
    )

    trusted: bool = False
    release_authorized: bool = False
    publish_authorized: bool = False
    deploy_authorized: bool = False
    tag_mutation_authorized: bool = False
    core_mutation_requested: bool = False
    universal_support_asserted: bool = False
    system_truth_asserted: bool = False

    def __post_init__(
        self,
    ) -> None:
        if not isinstance(
            self.manifest,
            ReproducibleReleaseManifest,
        ):
            raise TypeError(
                "manifest must be "
                "ReproducibleReleaseManifest."
            )

        rows = tuple(
            self.platform_certifications
        )

        if not all(
            isinstance(
                row,
                GovernedPlatformCertification,
            )
            for row in rows
        ):
            raise TypeError(
                "platform_certifications must "
                "contain governed platform "
                "certifications only."
            )

        for row in rows:
            if (
                row.manifest.manifest_id
                != self.manifest.manifest_id
            ):
                raise GovernedReleaseInvariantError(
                    "Platform certification "
                    "belongs to a different "
                    "release manifest."
                )

        ids = [
            row.platform_id
            for row in rows
        ]

        if len(ids) != len(set(ids)):
            raise GovernedReleaseInvariantError(
                "Platform certifications "
                "must be unique per platform."
            )

        unsupported = sorted(
            set(ids)
            - set(
                self.manifest
                .supported_platform_ids
            )
        )

        if unsupported:
            raise GovernedReleaseInvariantError(
                "Release certification contains "
                "undeclared platform evidence."
            )

        ordered = tuple(
            sorted(
                rows,
                key=lambda row: (
                    row.platform_id,
                    row.certification_id,
                ),
            )
        )

        passed = tuple(
            row.platform_id
            for row in ordered
            if (
                row.state
                is PlatformCertificationState.PASS
            )
        )

        missing = tuple(
            platform_id
            for platform_id
            in self.manifest
            .supported_platform_ids
            if platform_id not in set(ids)
        )

        if any(
            row.state
            is PlatformCertificationState.FAILED
            for row in ordered
        ):
            state = (
                ReleaseCertificationState.FAILED
            )

        elif (
            missing
            or any(
                row.state
                is PlatformCertificationState.INCOMPLETE
                for row in ordered
            )
        ):
            state = (
                ReleaseCertificationState.INCOMPLETE
            )

        elif (
            set(passed)
            == set(
                self.manifest
                .supported_platform_ids
            )
        ):
            state = (
                ReleaseCertificationState.PASS
            )

        else:
            state = (
                ReleaseCertificationState.INCOMPLETE
            )

        object.__setattr__(
            self,
            "platform_certifications",
            ordered,
        )

        object.__setattr__(
            self,
            "passed_platform_ids",
            passed,
        )

        object.__setattr__(
            self,
            "missing_platform_ids",
            missing,
        )

        object.__setattr__(
            self,
            "state",
            state,
        )

        payload = {
            "manifest_id": (
                self.manifest.manifest_id
            ),
            "state": state.value,
            "passed_platform_ids": (
                list(passed)
            ),
            "missing_platform_ids": (
                list(missing)
            ),
            "platform_certifications": [
                row.to_dict()
                for row in ordered
            ],
        }

        object.__setattr__(
            self,
            "certification_id",
            _stable_id(
                "RRC",
                payload,
            ),
        )

        _assert_passive(
            trusted=self.trusted,
            release_authorized=(
                self.release_authorized
            ),
            publish_authorized=(
                self.publish_authorized
            ),
            deploy_authorized=(
                self.deploy_authorized
            ),
            tag_mutation_authorized=(
                self.tag_mutation_authorized
            ),
            core_mutation_requested=(
                self.core_mutation_requested
            ),
            universal_support_asserted=(
                self.universal_support_asserted
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
                GOVERNED_REPRODUCIBLE_RELEASE_CERTIFICATION_VERSION
            ),
            "certification_id": (
                self.certification_id
            ),
            "manifest": (
                self.manifest.to_dict()
            ),
            "state": self.state.value,
            "passed_platform_ids": list(
                self.passed_platform_ids
            ),
            "missing_platform_ids": list(
                self.missing_platform_ids
            ),
            "platform_certifications": [
                row.to_dict()
                for row
                in self.platform_certifications
            ],
            "trusted": False,
            "release_authorized": False,
            "publish_authorized": False,
            "deploy_authorized": False,
            "tag_mutation_authorized": False,
            "core_mutation_requested": False,
            "universal_support_asserted": False,
            "system_truth_asserted": False,
        }


class GovernedReproducibleReleaseCertification:
    @classmethod
    def certify_platform(
        cls,
        manifest: ReproducibleReleaseManifest,
        evidence: PlatformGateEvidence,
    ) -> GovernedPlatformCertification:
        return GovernedPlatformCertification(
            manifest=manifest,
            evidence=evidence,
        )

    @classmethod
    def certify_release(
        cls,
        manifest: ReproducibleReleaseManifest,
        platform_certifications: tuple[
            GovernedPlatformCertification,
            ...,
        ],
    ) -> GovernedReleaseCertificationResult:
        return GovernedReleaseCertificationResult(
            manifest=manifest,
            platform_certifications=(
                tuple(
                    platform_certifications
                )
            ),
        )


__all__ = [
    "GOVERNED_REPRODUCIBLE_RELEASE_CERTIFICATION_VERSION",
    "GovernedReleaseInvariantError",
    "GateEvidenceState",
    "PlatformCertificationState",
    "ReleaseCertificationState",
    "ReproducibleReleaseManifest",
    "PlatformGateEvidence",
    "GovernedPlatformCertification",
    "GovernedReleaseCertificationResult",
    "GovernedReproducibleReleaseCertification",
]
