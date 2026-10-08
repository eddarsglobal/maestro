from __future__ import annotations

import hashlib
import json

from dataclasses import dataclass

from maestro.enums import (
    CouncilId,
    EvidenceKind,
)
from maestro.models import (
    Evidence,
)

from .contracts import (
    ExternalArtifact,
    ResearchClaim,
    TrustState,
)
from .evidence_bridge import (
    ResearchEvidenceBridge,
)
from .radar_research_draft_admission import (
    RadarResearchDraftAdmissionStatus,
)
from .radar_research_return_admission import (
    RadarResearchProviderReturnAdmissionResult,
    RadarResearchProviderReturnPacket,
)
from .radar_review_handoff import (
    RadarReviewTarget,
)
from .radar_review_packet import (
    RadarFactorSnapshot,
)
from .runtime_contracts import (
    ResearchExecutionResult,
    ResearchRequest,
    ResearchRoutingDecision,
)


class RadarResearchEvidenceReintegrationError(
    ValueError
):
    pass


def _stable_identifier(
    prefix: str,
    *parts: str,
) -> str:
    if prefix not in {
        "ART",
        "CLM",
        "EVD",
    }:
        raise ValueError(
            "Unsupported stable identifier prefix."
        )

    for part in parts:
        if not isinstance(
            part,
            str,
        ):
            raise TypeError(
                "Stable identifier parts "
                "must be strings."
            )

    canonical = json.dumps(
        parts,
        ensure_ascii=False,
        separators=(",", ":"),
        allow_nan=False,
    ).encode(
        "utf-8"
    )

    digest = hashlib.sha256(
        canonical
    ).hexdigest()[
        :12
    ].upper()

    return (
        f"{prefix}-{digest}"
    )


@dataclass(
    frozen=True,
    slots=True,
)
class RadarResearchEvidenceReintegrationEntry:
    rank: int

    origin_evidence_id: str
    source_ref: str
    claim: str

    priority_score: float
    factors: RadarFactorSnapshot
    rationale: str
    target: RadarReviewTarget

    admission_status: (
        RadarResearchDraftAdmissionStatus
    )
    admission_reason: str

    request: ResearchRequest
    decision: ResearchRoutingDecision
    result: ResearchExecutionResult

    return_packet: (
        RadarResearchProviderReturnPacket
    )

    artifact: ExternalArtifact
    research_claim: ResearchClaim
    evidence: Evidence

    verification_status: str = (
        "UNVERIFIED_EXTERNAL"
    )

    network_access_status: str = "UNKNOWN"

    system_truth_asserted: bool = False

    task_id_bound: bool = True
    provider_return_admitted: bool = True

    external_artifact_created: bool = True
    research_claim_created: bool = True
    evidence_created: bool = True
    evidence_model_reintegrated: bool = True

    evidence_persisted: bool = False
    radar_evaluated: bool = False
    followup_authorized: bool = False

    mission_transition_requested: bool = False
    new_network_requested: bool = False
    persistence_requested: bool = False

    learning_asserted: bool = False
    authorization_asserted: bool = False
    promotion_asserted: bool = False
    activation_asserted: bool = False

    def __post_init__(
        self,
    ) -> None:
        if (
            not isinstance(
                self.rank,
                int,
            )
            or isinstance(
                self.rank,
                bool,
            )
            or self.rank < 1
        ):
            raise (
                RadarResearchEvidenceReintegrationError(
                    "rank must be a positive integer."
                )
            )

        for name in (
            "origin_evidence_id",
            "source_ref",
            "claim",
            "rationale",
            "admission_reason",
        ):
            value = getattr(
                self,
                name,
            )

            if (
                not isinstance(
                    value,
                    str,
                )
                or not value.strip()
            ):
                raise (
                    RadarResearchEvidenceReintegrationError(
                        f"{name} must be non-empty."
                    )
                )

        if not isinstance(
            self.factors,
            RadarFactorSnapshot,
        ):
            raise TypeError(
                "factors must be "
                "RadarFactorSnapshot."
            )

        if not isinstance(
            self.target,
            RadarReviewTarget,
        ):
            raise TypeError(
                "target must be "
                "RadarReviewTarget."
            )

        if (
            self.admission_status
            is not RadarResearchDraftAdmissionStatus
            .ADMISSIBLE
        ):
            raise (
                RadarResearchEvidenceReintegrationError(
                    "Evidence reintegration "
                    "requires ADMISSIBLE lineage."
                )
            )

        if not isinstance(
            self.request,
            ResearchRequest,
        ):
            raise TypeError(
                "request must be ResearchRequest."
            )

        if not isinstance(
            self.decision,
            ResearchRoutingDecision,
        ):
            raise TypeError(
                "decision must be "
                "ResearchRoutingDecision."
            )

        if not isinstance(
            self.result,
            ResearchExecutionResult,
        ):
            raise TypeError(
                "result must be "
                "ResearchExecutionResult."
            )

        if type(
            self.return_packet
        ) is not RadarResearchProviderReturnPacket:
            raise TypeError(
                "return_packet must be exactly "
                "RadarResearchProviderReturnPacket."
            )

        if not isinstance(
            self.artifact,
            ExternalArtifact,
        ):
            raise TypeError(
                "artifact must be "
                "ExternalArtifact."
            )

        if not isinstance(
            self.research_claim,
            ResearchClaim,
        ):
            raise TypeError(
                "research_claim must be "
                "ResearchClaim."
            )

        if not isinstance(
            self.evidence,
            Evidence,
        ):
            raise TypeError(
                "evidence must be Evidence."
            )

        packet = self.return_packet

        if (
            self.artifact.source
            is not packet.source
        ):
            raise (
                RadarResearchEvidenceReintegrationError(
                    "Artifact must preserve the "
                    "admitted ResearchSource object."
                )
            )

        if (
            self.artifact.provenance
            is not packet.provenance
        ):
            raise (
                RadarResearchEvidenceReintegrationError(
                    "Artifact must preserve the "
                    "admitted SourceProvenance object."
                )
            )

        if (
            self.artifact.artifact_kind
            != packet.artifact_kind
        ):
            raise (
                RadarResearchEvidenceReintegrationError(
                    "Artifact kind mismatch."
                )
            )

        if (
            self.artifact.media_type
            != packet.media_type
        ):
            raise (
                RadarResearchEvidenceReintegrationError(
                    "Artifact media type mismatch."
                )
            )

        if (
            self.artifact.trust_state
            is not TrustState.UNTRUSTED
        ):
            raise (
                RadarResearchEvidenceReintegrationError(
                    "External artifact must remain "
                    "UNTRUSTED."
                )
            )

        expected_artifact_id = (
            _stable_identifier(
                "ART",
                self.request.task_id,
                packet.provider_id,
                packet.tool_name,
                packet.source.source_id,
                packet.source.uri,
                packet.provenance.retrieved_at,
                packet.provenance.digest.hex_digest,
                packet.artifact_kind,
                packet.media_type,
            )
        )

        if (
            self.artifact.artifact_id
            != expected_artifact_id
        ):
            raise (
                RadarResearchEvidenceReintegrationError(
                    "Artifact identity is not "
                    "deterministic."
                )
            )

        if (
            self.research_claim.statement
            != packet.claim_statement
        ):
            raise (
                RadarResearchEvidenceReintegrationError(
                    "Research claim statement "
                    "must match admitted return."
                )
            )

        if (
            self.research_claim.artifact_ids
            != (
                self.artifact.artifact_id,
            )
        ):
            raise (
                RadarResearchEvidenceReintegrationError(
                    "Research claim must bind "
                    "exactly one constructed "
                    "artifact."
                )
            )

        if (
            self.research_claim.created_at
            != packet.provenance.retrieved_at
        ):
            raise (
                RadarResearchEvidenceReintegrationError(
                    "Claim timestamp must derive "
                    "from admitted provenance."
                )
            )

        if (
            self.research_claim.trust_state
            is not TrustState.UNTRUSTED
        ):
            raise (
                RadarResearchEvidenceReintegrationError(
                    "Research claim must remain "
                    "UNTRUSTED."
                )
            )

        expected_claim_id = (
            _stable_identifier(
                "CLM",
                self.request.task_id,
                self.artifact.artifact_id,
                packet.provider_id,
                packet.tool_name,
                packet.claim_statement,
                packet.provenance.retrieved_at,
                packet.provenance.digest.hex_digest,
            )
        )

        if (
            self.research_claim.claim_id
            != expected_claim_id
        ):
            raise (
                RadarResearchEvidenceReintegrationError(
                    "Claim identity is not "
                    "deterministic."
                )
            )

        if (
            self.evidence.task_id
            != self.request.task_id
        ):
            raise (
                RadarResearchEvidenceReintegrationError(
                    "Evidence task_id mismatch."
                )
            )

        if (
            self.evidence.council
            is not CouncilId.RX
        ):
            raise (
                RadarResearchEvidenceReintegrationError(
                    "Evidence must remain RX."
                )
            )

        if (
            self.evidence.kind
            is not EvidenceKind.WEB_SOURCE
        ):
            raise (
                RadarResearchEvidenceReintegrationError(
                    "Evidence must be WEB_SOURCE."
                )
            )

        if (
            self.evidence.claim
            != self.research_claim.statement
        ):
            raise (
                RadarResearchEvidenceReintegrationError(
                    "Evidence claim mismatch."
                )
            )

        if (
            self.evidence.source_ref
            != self.research_claim.claim_id
        ):
            raise (
                RadarResearchEvidenceReintegrationError(
                    "Evidence source_ref must "
                    "equal ResearchClaim.claim_id."
                )
            )

        if (
            self.evidence.created_at
            != packet.provenance.retrieved_at
        ):
            raise (
                RadarResearchEvidenceReintegrationError(
                    "Evidence timestamp must derive "
                    "from admitted provenance."
                )
            )

        expected_evidence_id = (
            _stable_identifier(
                "EVD",
                self.request.task_id,
                self.research_claim.claim_id,
                self.artifact.artifact_id,
                packet.provenance.digest.hex_digest,
            )
        )

        if (
            self.evidence.evidence_id
            != expected_evidence_id
        ):
            raise (
                RadarResearchEvidenceReintegrationError(
                    "Evidence identity is not "
                    "deterministic."
                )
            )

        if not isinstance(
            self.evidence.payload,
            dict,
        ):
            raise (
                RadarResearchEvidenceReintegrationError(
                    "Research evidence payload "
                    "must remain a dictionary."
                )
            )

        verification = (
            self.evidence.payload.get(
                "verification"
            )
        )

        if not isinstance(
            verification,
            dict,
        ):
            raise (
                RadarResearchEvidenceReintegrationError(
                    "Research evidence requires "
                    "verification metadata."
                )
            )

        if (
            verification.get("status")
            != "UNVERIFIED_EXTERNAL"
        ):
            raise (
                RadarResearchEvidenceReintegrationError(
                    "Evidence must remain "
                    "UNVERIFIED_EXTERNAL."
                )
            )

        if (
            verification.get(
                "required_authority"
            )
            != CouncilId.AY.value
        ):
            raise (
                RadarResearchEvidenceReintegrationError(
                    "AY must remain the required "
                    "verification authority."
                )
            )

        if (
            verification.get(
                "system_truth_asserted"
            )
            is not False
        ):
            raise (
                RadarResearchEvidenceReintegrationError(
                    "Evidence cannot assert truth."
                )
            )

        if (
            self.verification_status
            != "UNVERIFIED_EXTERNAL"
        ):
            raise (
                RadarResearchEvidenceReintegrationError(
                    "Reintegrated evidence must "
                    "remain UNVERIFIED_EXTERNAL."
                )
            )

        if self.network_access_status != "UNKNOWN":
            raise (
                RadarResearchEvidenceReintegrationError(
                    "Prior network access remains "
                    "UNKNOWN without telemetry."
                )
            )

        if self.system_truth_asserted is not False:
            raise (
                RadarResearchEvidenceReintegrationError(
                    "Evidence construction cannot "
                    "assert system truth."
                )
            )

        required_true = (
            "task_id_bound",
            "provider_return_admitted",
            "external_artifact_created",
            "research_claim_created",
            "evidence_created",
            "evidence_model_reintegrated",
        )

        for name in required_true:
            if getattr(
                self,
                name,
            ) is not True:
                raise (
                    RadarResearchEvidenceReintegrationError(
                        "Evidence reintegration "
                        f"requires {name}=True."
                    )
                )

        required_false = (
            "evidence_persisted",
            "radar_evaluated",
            "followup_authorized",
            "mission_transition_requested",
            "new_network_requested",
            "persistence_requested",
            "learning_asserted",
            "authorization_asserted",
            "promotion_asserted",
            "activation_asserted",
        )

        for name in required_false:
            if getattr(
                self,
                name,
            ) is not False:
                raise (
                    RadarResearchEvidenceReintegrationError(
                        "Evidence reintegration "
                        f"cannot assert {name}."
                    )
                )

    @property
    def task_id(
        self,
    ) -> str:
        return self.request.task_id

    @property
    def provider_id(
        self,
    ) -> str:
        return self.result.provider_id

    @property
    def tool_name(
        self,
    ) -> str:
        return self.result.tool_name

    @property
    def returned_evidence_id(
        self,
    ) -> str:
        return self.evidence.evidence_id


@dataclass(
    frozen=True,
    slots=True,
)
class RadarResearchEvidenceReintegrationResult:
    entries: tuple[
        RadarResearchEvidenceReintegrationEntry,
        ...
    ]

    def __post_init__(
        self,
    ) -> None:
        for entry in self.entries:
            if not isinstance(
                entry,
                RadarResearchEvidenceReintegrationEntry,
            ):
                raise TypeError(
                    "entries must contain "
                    "RadarResearchEvidenceReintegrationEntry."
                )

        origin_ids = tuple(
            entry.origin_evidence_id
            for entry in self.entries
        )

        if (
            len(origin_ids)
            != len(set(origin_ids))
        ):
            raise (
                RadarResearchEvidenceReintegrationError(
                    "Origin evidence IDs must "
                    "remain unique."
                )
            )

        returned_ids = tuple(
            entry.returned_evidence_id
            for entry in self.entries
        )

        if (
            len(returned_ids)
            != len(set(returned_ids))
        ):
            raise (
                RadarResearchEvidenceReintegrationError(
                    "Returned evidence IDs must "
                    "be unique."
                )
            )

        ranks = tuple(
            entry.rank
            for entry in self.entries
        )

        if ranks != tuple(sorted(ranks)):
            raise (
                RadarResearchEvidenceReintegrationError(
                    "Evidence reintegration must "
                    "preserve rank order."
                )
            )

    @property
    def size(
        self,
    ) -> int:
        return len(
            self.entries
        )

    @property
    def origin_evidence_ids(
        self,
    ) -> tuple[str, ...]:
        return tuple(
            entry.origin_evidence_id
            for entry in self.entries
        )

    @property
    def evidence_ids(
        self,
    ) -> tuple[str, ...]:
        return tuple(
            entry.returned_evidence_id
            for entry in self.entries
        )

    @property
    def task_ids(
        self,
    ) -> tuple[str, ...]:
        return tuple(
            entry.task_id
            for entry in self.entries
        )

    @property
    def provider_ids(
        self,
    ) -> tuple[str, ...]:
        return tuple(
            entry.provider_id
            for entry in self.entries
        )

    @property
    def tool_names(
        self,
    ) -> tuple[str, ...]:
        return tuple(
            entry.tool_name
            for entry in self.entries
        )


class GovernedRadarResearchEvidenceReintegrator:
    """
    ADEL0.22C evidence-model reintegration.

    Consumes only ADEL0.22B admitted provider
    returns.

    It constructs one UNTRUSTED ExternalArtifact,
    one UNTRUSTED ResearchClaim, and one RX
    WEB_SOURCE Evidence through ResearchEvidenceBridge.

    This is model reintegration only.

    It does NOT persist evidence.
    It does NOT evaluate Technology Radar.
    It does NOT authorize another follow-up cycle.
    It does NOT perform network access.
    It does NOT verify truth.
    It does NOT learn, promote, or activate.

    RETURN ADMITTED != EVIDENCE.

    EVIDENCE CREATED != VERIFIED.
    EVIDENCE CREATED != PERSISTED.
    EVIDENCE CREATED != RADAR EVALUATED.
    EVIDENCE CREATED != FOLLOW-UP AUTHORIZED.
    EVIDENCE CREATED != TRUTH.
    EVIDENCE CREATED != LEARNING.
    EVIDENCE CREATED != PROMOTION.
    EVIDENCE CREATED != ACTIVATION.
    """

    @staticmethod
    def reintegrate(
        admission: (
            RadarResearchProviderReturnAdmissionResult
        ),
    ) -> RadarResearchEvidenceReintegrationResult:
        if not isinstance(
            admission,
            RadarResearchProviderReturnAdmissionResult,
        ):
            raise TypeError(
                "admission must be "
                "RadarResearchProviderReturnAdmissionResult."
            )

        entries = []

        for admitted in admission.entries:
            packet = (
                admitted.return_packet
            )

            artifact_id = (
                _stable_identifier(
                    "ART",
                    admitted.request.task_id,
                    packet.provider_id,
                    packet.tool_name,
                    packet.source.source_id,
                    packet.source.uri,
                    packet.provenance.retrieved_at,
                    packet.provenance.digest.hex_digest,
                    packet.artifact_kind,
                    packet.media_type,
                )
            )

            artifact = ExternalArtifact(
                source=packet.source,
                provenance=packet.provenance,
                artifact_kind=(
                    packet.artifact_kind
                ),
                media_type=(
                    packet.media_type
                ),
                trust_state=(
                    TrustState.UNTRUSTED
                ),
                artifact_id=artifact_id,
            )

            claim_id = (
                _stable_identifier(
                    "CLM",
                    admitted.request.task_id,
                    artifact.artifact_id,
                    packet.provider_id,
                    packet.tool_name,
                    packet.claim_statement,
                    packet.provenance.retrieved_at,
                    packet.provenance.digest.hex_digest,
                )
            )

            research_claim = (
                ResearchClaim(
                    statement=(
                        packet.claim_statement
                    ),
                    artifact_ids=(
                        artifact.artifact_id,
                    ),
                    created_at=(
                        packet.provenance
                        .retrieved_at
                    ),
                    trust_state=(
                        TrustState.UNTRUSTED
                    ),
                    claim_id=claim_id,
                )
            )

            bridged = (
                ResearchEvidenceBridge
                .to_evidence(
                    task_id=(
                        admitted.request.task_id
                    ),
                    claim=research_claim,
                    artifacts=(
                        artifact,
                    ),
                )
            )

            evidence_id = (
                _stable_identifier(
                    "EVD",
                    admitted.request.task_id,
                    research_claim.claim_id,
                    artifact.artifact_id,
                    packet.provenance.digest.hex_digest,
                )
            )

            evidence = Evidence(
                task_id=bridged.task_id,
                council=bridged.council,
                kind=bridged.kind,
                claim=bridged.claim,
                payload=bridged.payload,
                source_ref=(
                    bridged.source_ref
                ),
                created_at=(
                    packet.provenance
                    .retrieved_at
                ),
                evidence_id=(
                    evidence_id
                ),
            )

            entries.append(
                RadarResearchEvidenceReintegrationEntry(
                    rank=admitted.rank,
                    origin_evidence_id=(
                        admitted.evidence_id
                    ),
                    source_ref=(
                        admitted.source_ref
                    ),
                    claim=admitted.claim,
                    priority_score=(
                        admitted.priority_score
                    ),
                    factors=(
                        admitted.factors
                    ),
                    rationale=(
                        admitted.rationale
                    ),
                    target=(
                        admitted.target
                    ),
                    admission_status=(
                        admitted.admission_status
                    ),
                    admission_reason=(
                        admitted.admission_reason
                    ),
                    request=(
                        admitted.request
                    ),
                    decision=(
                        admitted.decision
                    ),
                    result=(
                        admitted.result
                    ),
                    return_packet=packet,
                    artifact=artifact,
                    research_claim=(
                        research_claim
                    ),
                    evidence=evidence,
                )
            )

        return (
            RadarResearchEvidenceReintegrationResult(
                entries=tuple(entries)
            )
        )


__all__ = [
    "GovernedRadarResearchEvidenceReintegrator",
    "RadarResearchEvidenceReintegrationEntry",
    "RadarResearchEvidenceReintegrationError",
    "RadarResearchEvidenceReintegrationResult",
]
