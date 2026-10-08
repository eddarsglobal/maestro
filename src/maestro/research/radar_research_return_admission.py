from __future__ import annotations

from dataclasses import dataclass

from .contracts import (
    ResearchSource,
    SourceProvenance,
)
from .radar_research_draft_admission import (
    RadarResearchDraftAdmissionStatus,
)
from .radar_research_exact_execution import (
    RadarResearchExactExecutionResult,
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


RADAR_RESEARCH_PROVIDER_RETURN_SCHEMA = (
    "MAESTRO-RX-RETURN-1"
)


class RadarResearchProviderReturnAdmissionError(
    ValueError
):
    pass


@dataclass(
    frozen=True,
    slots=True,
)
class RadarResearchProviderReturnPacket:
    """
    Canonical external-provider return contract.

    This packet is still UNTRUSTED external input.

    It contains enough explicit provenance for a
    later governed evidence-construction boundary,
    but it is NOT itself a ResearchClaim,
    ExternalArtifact, Evidence, verification, or
    truth assertion.
    """

    provider_id: str
    tool_name: str

    source: ResearchSource
    provenance: SourceProvenance

    claim_statement: str
    artifact_kind: str
    media_type: str

    schema: str = (
        RADAR_RESEARCH_PROVIDER_RETURN_SCHEMA
    )

    def __post_init__(
        self,
    ) -> None:
        for name in (
            "provider_id",
            "tool_name",
            "claim_statement",
            "artifact_kind",
            "media_type",
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
                    RadarResearchProviderReturnAdmissionError(
                        f"{name} must be non-empty."
                    )
                )

        if not isinstance(
            self.source,
            ResearchSource,
        ):
            raise TypeError(
                "source must be ResearchSource."
            )

        if not isinstance(
            self.provenance,
            SourceProvenance,
        ):
            raise TypeError(
                "provenance must be "
                "SourceProvenance."
            )

        if (
            self.source.source_id
            != self.provenance.source_id
        ):
            raise (
                RadarResearchProviderReturnAdmissionError(
                    "Provider return source and "
                    "provenance source_id must match."
                )
            )

        if (
            self.schema
            != RADAR_RESEARCH_PROVIDER_RETURN_SCHEMA
        ):
            raise (
                RadarResearchProviderReturnAdmissionError(
                    "Unsupported provider return "
                    "schema."
                )
            )


@dataclass(
    frozen=True,
    slots=True,
)
class RadarResearchProviderReturnAdmissionEntry:
    rank: int
    evidence_id: str
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

    verification_status: str = (
        "UNVERIFIED_EXTERNAL"
    )

    network_access_status: str = "UNKNOWN"

    system_truth_asserted: bool = False

    task_id_bound: bool = True
    research_request_created: bool = True
    provider_selected: bool = True
    routing_decision_created: bool = True
    tool_validated: bool = True
    execution_handoff_created: bool = True
    tool_execution_requested: bool = True
    tool_invoked: bool = True
    action_firewall_crossed: bool = True
    execution_completed: bool = True
    execution_result_created: bool = True
    execution_asserted: bool = True

    provider_return_received: bool = True
    provider_return_admitted: bool = True

    research_claim_created: bool = False
    external_artifact_created: bool = False
    evidence_created: bool = False
    evidence_reintegrated: bool = False

    mission_transition_requested: bool = False
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
                RadarResearchProviderReturnAdmissionError(
                    "rank must be a positive integer."
                )
            )

        for name in (
            "evidence_id",
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
                    RadarResearchProviderReturnAdmissionError(
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
                RadarResearchProviderReturnAdmissionError(
                    "Provider return requires "
                    "ADMISSIBLE research lineage."
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

        if (
            self.result.task_id
            != self.request.task_id
        ):
            raise (
                RadarResearchProviderReturnAdmissionError(
                    "Execution task_id lineage "
                    "mismatch."
                )
            )

        if (
            self.result.provider_id
            != self.decision.provider_id
        ):
            raise (
                RadarResearchProviderReturnAdmissionError(
                    "Execution provider lineage "
                    "mismatch."
                )
            )

        if (
            self.result.tool_name
            != self.decision.tool_name
        ):
            raise (
                RadarResearchProviderReturnAdmissionError(
                    "Execution tool lineage mismatch."
                )
            )

        if (
            self.return_packet.provider_id
            != self.result.provider_id
        ):
            raise (
                RadarResearchProviderReturnAdmissionError(
                    "Provider return packet "
                    "provider_id mismatch."
                )
            )

        if (
            self.return_packet.tool_name
            != self.result.tool_name
        ):
            raise (
                RadarResearchProviderReturnAdmissionError(
                    "Provider return packet "
                    "tool_name mismatch."
                )
            )

        if (
            self.verification_status
            != "UNVERIFIED_EXTERNAL"
        ):
            raise (
                RadarResearchProviderReturnAdmissionError(
                    "Admitted return must remain "
                    "UNVERIFIED_EXTERNAL."
                )
            )

        if self.network_access_status != "UNKNOWN":
            raise (
                RadarResearchProviderReturnAdmissionError(
                    "Network status remains UNKNOWN "
                    "without telemetry."
                )
            )

        if self.system_truth_asserted is not False:
            raise (
                RadarResearchProviderReturnAdmissionError(
                    "Return admission cannot "
                    "assert truth."
                )
            )

        required_true = (
            "task_id_bound",
            "research_request_created",
            "provider_selected",
            "routing_decision_created",
            "tool_validated",
            "execution_handoff_created",
            "tool_execution_requested",
            "tool_invoked",
            "action_firewall_crossed",
            "execution_completed",
            "execution_result_created",
            "execution_asserted",
            "provider_return_received",
            "provider_return_admitted",
        )

        for name in required_true:
            if getattr(
                self,
                name,
            ) is not True:
                raise (
                    RadarResearchProviderReturnAdmissionError(
                        "Return admission requires "
                        f"{name}=True."
                    )
                )

        required_false = (
            "research_claim_created",
            "external_artifact_created",
            "evidence_created",
            "evidence_reintegrated",
            "mission_transition_requested",
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
                    RadarResearchProviderReturnAdmissionError(
                        "Return admission cannot "
                        f"assert {name}."
                    )
                )

    @property
    def task_id(
        self,
    ) -> str:
        return self.result.task_id

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


@dataclass(
    frozen=True,
    slots=True,
)
class RadarResearchProviderReturnAdmissionResult:
    entries: tuple[
        RadarResearchProviderReturnAdmissionEntry,
        ...
    ]

    def __post_init__(
        self,
    ) -> None:
        for entry in self.entries:
            if not isinstance(
                entry,
                RadarResearchProviderReturnAdmissionEntry,
            ):
                raise TypeError(
                    "entries must contain "
                    "RadarResearchProviderReturnAdmissionEntry."
                )

        ids = tuple(
            entry.evidence_id
            for entry in self.entries
        )

        if len(ids) != len(set(ids)):
            raise (
                RadarResearchProviderReturnAdmissionError(
                    "Return admission requires "
                    "unique evidence IDs."
                )
            )

        ranks = tuple(
            entry.rank
            for entry in self.entries
        )

        if ranks != tuple(sorted(ranks)):
            raise (
                RadarResearchProviderReturnAdmissionError(
                    "Return admission must preserve "
                    "execution rank order."
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
    def evidence_ids(
        self,
    ) -> tuple[str, ...]:
        return tuple(
            entry.evidence_id
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


class GovernedRadarResearchProviderReturnAdmission:
    """
    ADEL0.22B strict provider-return admission.

    Execution output is untrusted.

    Only the canonical, versioned
    RadarResearchProviderReturnPacket is admitted.

    No coercion via str(), repr(), JSON guessing,
    duck typing, or capability-specific heuristics
    occurs here.

    RETURNED != ADMISSIBLE.
    ADMISSIBLE != RESEARCH CLAIM.
    ADMISSIBLE != EXTERNAL ARTIFACT.
    ADMISSIBLE != EVIDENCE.
    ADMISSIBLE != VERIFIED.
    ADMISSIBLE != TRUTH.
    ADMISSIBLE != LEARNING.
    ADMISSIBLE != PROMOTION.
    ADMISSIBLE != ACTIVATION.
    """

    @staticmethod
    def admit(
        execution: RadarResearchExactExecutionResult,
    ) -> RadarResearchProviderReturnAdmissionResult:
        if not isinstance(
            execution,
            RadarResearchExactExecutionResult,
        ):
            raise TypeError(
                "execution must be "
                "RadarResearchExactExecutionResult."
            )

        entries = []

        for executed in execution.entries:
            output = executed.result.output

            if type(
                output
            ) is not RadarResearchProviderReturnPacket:
                raise (
                    RadarResearchProviderReturnAdmissionError(
                        "Provider output is not an "
                        "admissible canonical return "
                        "packet."
                    )
                )

            entries.append(
                RadarResearchProviderReturnAdmissionEntry(
                    rank=executed.rank,
                    evidence_id=(
                        executed.evidence_id
                    ),
                    source_ref=(
                        executed.source_ref
                    ),
                    claim=executed.claim,
                    priority_score=(
                        executed.priority_score
                    ),
                    factors=executed.factors,
                    rationale=(
                        executed.rationale
                    ),
                    target=executed.target,
                    admission_status=(
                        executed.admission_status
                    ),
                    admission_reason=(
                        executed.admission_reason
                    ),
                    request=executed.request,
                    decision=executed.decision,
                    result=executed.result,
                    return_packet=output,
                )
            )

        return (
            RadarResearchProviderReturnAdmissionResult(
                entries=tuple(entries)
            )
        )


__all__ = [
    "RADAR_RESEARCH_PROVIDER_RETURN_SCHEMA",
    "GovernedRadarResearchProviderReturnAdmission",
    "RadarResearchProviderReturnAdmissionEntry",
    "RadarResearchProviderReturnAdmissionError",
    "RadarResearchProviderReturnAdmissionResult",
    "RadarResearchProviderReturnPacket",
]
