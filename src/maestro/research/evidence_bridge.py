from __future__ import annotations

from collections.abc import Iterable

from maestro.enums import (
    CouncilId,
    EvidenceKind,
)
from maestro.models import Evidence

from .contracts import (
    ExternalArtifact,
    ResearchClaim,
)


def _require_task_id(value: str) -> str:
    if not isinstance(value, str):
        raise TypeError(
            "task_id must be a string."
        )

    normalized = value.strip()

    if not normalized:
        raise ValueError(
            "task_id must not be empty."
        )

    if "\x00" in normalized:
        raise ValueError(
            "task_id must not contain NUL."
        )

    return normalized


class ResearchEvidenceBridge:
    """
    Convert governed RX research contracts into ordinary MAESTRO Evidence.

    This bridge performs no network access, truth validation, learning,
    promotion, execution, or Council authorization.

    Evidence.source_ref points to the internal ResearchClaim identifier.
    External source URIs and provenance remain inside the evidence payload.

    WEB_SOURCE evidence means that RX observed and recorded an external
    claim. It does not mean that AY validated the claim as true.
    """

    @staticmethod
    def to_evidence(
        *,
        task_id: str,
        claim: ResearchClaim,
        artifacts: Iterable[ExternalArtifact],
    ) -> Evidence:
        task_id = _require_task_id(
            task_id
        )

        if not isinstance(
            claim,
            ResearchClaim,
        ):
            raise TypeError(
                "claim must be a ResearchClaim."
            )

        supplied = tuple(
            artifacts
        )

        if not supplied:
            raise ValueError(
                "Research evidence requires external artifacts."
            )

        for artifact in supplied:
            if not isinstance(
                artifact,
                ExternalArtifact,
            ):
                raise TypeError(
                    "artifacts must contain "
                    "ExternalArtifact objects only."
                )

        supplied_ids = tuple(
            artifact.artifact_id
            for artifact in supplied
        )

        if len(set(supplied_ids)) != len(
            supplied_ids
        ):
            raise ValueError(
                "Duplicate external artifacts are not allowed."
            )

        expected_ids = set(
            claim.artifact_ids
        )
        actual_ids = set(
            supplied_ids
        )

        if actual_ids != expected_ids:
            missing = sorted(
                expected_ids - actual_ids
            )
            extra = sorted(
                actual_ids - expected_ids
            )

            raise ValueError(
                "Research evidence artifact set mismatch; "
                f"missing={missing}, extra={extra}"
            )

        by_id = {
            artifact.artifact_id: artifact
            for artifact in supplied
        }

        ordered_artifacts = [
            by_id[artifact_id]
            for artifact_id
            in claim.artifact_ids
        ]

        payload = {
            "research_claim": (
                claim.to_dict()
            ),
            "artifacts": [
                artifact.to_dict()
                for artifact
                in ordered_artifacts
            ],
            "verification": {
                "status": (
                    "UNVERIFIED_EXTERNAL"
                ),
                "required_authority": (
                    CouncilId.AY.value
                ),
                "system_truth_asserted": (
                    False
                ),
            },
        }

        return Evidence(
            task_id=task_id,
            council=CouncilId.RX,
            kind=EvidenceKind.WEB_SOURCE,
            claim=claim.statement,
            payload=payload,
            source_ref=claim.claim_id,
        )
