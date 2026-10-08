from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum

from maestro.enums import (
    CouncilId,
    EvidenceKind,
)
from maestro.models import Evidence

from .radar_research_evidence_reintegration import (
    RadarResearchEvidenceReintegrationEntry,
    RadarResearchEvidenceReintegrationResult,
)


class RadarFollowUpCycleGateInvariantError(
    ValueError
):
    pass


class RadarFollowUpCycleDisposition(
    StrEnum
):
    ELIGIBLE_FOR_REEVALUATION = (
        "ELIGIBLE_FOR_REEVALUATION"
    )

    STOP_CYCLE = "STOP_CYCLE"


@dataclass(
    frozen=True,
    slots=True,
)
class RadarFollowUpCycleGateEntry:
    source_entry: (
        RadarResearchEvidenceReintegrationEntry
    )

    disposition: RadarFollowUpCycleDisposition

    verification_status: str = (
        "UNVERIFIED_EXTERNAL"
    )

    system_truth_asserted: bool = False

    cycle_decision_created: bool = True

    cycle_started: bool = False
    radar_evaluated: bool = False
    reevaluation_authorized: bool = False

    new_research_request_created: bool = False
    network_requested: bool = False
    tool_execution_requested: bool = False

    mission_transition_requested: bool = False
    persistence_requested: bool = False

    learning_asserted: bool = False
    authorization_asserted: bool = False
    promotion_asserted: bool = False
    activation_asserted: bool = False
    execution_asserted: bool = False

    def __post_init__(
        self,
    ) -> None:
        if not isinstance(
            self.source_entry,
            RadarResearchEvidenceReintegrationEntry,
        ):
            raise TypeError(
                "source_entry must be "
                "RadarResearchEvidenceReintegrationEntry."
            )

        if not isinstance(
            self.disposition,
            RadarFollowUpCycleDisposition,
        ):
            raise TypeError(
                "disposition must be "
                "RadarFollowUpCycleDisposition."
            )

        source = self.source_entry
        evidence = source.evidence

        if not isinstance(
            evidence,
            Evidence,
        ):
            raise TypeError(
                "source evidence must be Evidence."
            )

        if (
            source.evidence_model_reintegrated
            is not True
        ):
            raise (
                RadarFollowUpCycleGateInvariantError(
                    "Cycle gate requires "
                    "reintegrated Evidence."
                )
            )

        if source.evidence_persisted is not False:
            raise (
                RadarFollowUpCycleGateInvariantError(
                    "Cycle gate cannot consume an "
                    "entry asserting persistence."
                )
            )

        if source.radar_evaluated is not False:
            raise (
                RadarFollowUpCycleGateInvariantError(
                    "Cycle gate requires Evidence "
                    "that has not been Radar-evaluated."
                )
            )

        if source.followup_authorized is not False:
            raise (
                RadarFollowUpCycleGateInvariantError(
                    "Cycle gate cannot inherit a "
                    "prior follow-up authorization."
                )
            )

        if (
            evidence.evidence_id
            != source.returned_evidence_id
        ):
            raise (
                RadarFollowUpCycleGateInvariantError(
                    "Returned Evidence identity "
                    "mismatch."
                )
            )

        if (
            evidence.task_id
            != source.task_id
        ):
            raise (
                RadarFollowUpCycleGateInvariantError(
                    "Returned Evidence task "
                    "lineage mismatch."
                )
            )

        if evidence.council is not CouncilId.RX:
            raise (
                RadarFollowUpCycleGateInvariantError(
                    "Cycle gate accepts RX "
                    "Evidence only."
                )
            )

        if (
            evidence.kind
            is not EvidenceKind.WEB_SOURCE
        ):
            raise (
                RadarFollowUpCycleGateInvariantError(
                    "Cycle gate accepts WEB_SOURCE "
                    "Evidence only."
                )
            )

        if (
            evidence.source_ref
            != source.research_claim.claim_id
        ):
            raise (
                RadarFollowUpCycleGateInvariantError(
                    "Evidence source_ref lineage "
                    "mismatch."
                )
            )

        if (
            evidence.claim
            != source.research_claim.statement
        ):
            raise (
                RadarFollowUpCycleGateInvariantError(
                    "Evidence claim lineage "
                    "mismatch."
                )
            )

        if not isinstance(
            evidence.payload,
            dict,
        ):
            raise (
                RadarFollowUpCycleGateInvariantError(
                    "Research Evidence payload "
                    "must be a dictionary."
                )
            )

        verification = evidence.payload.get(
            "verification"
        )

        if not isinstance(
            verification,
            dict,
        ):
            raise (
                RadarFollowUpCycleGateInvariantError(
                    "Research Evidence requires "
                    "verification metadata."
                )
            )

        if (
            verification.get("status")
            != "UNVERIFIED_EXTERNAL"
        ):
            raise (
                RadarFollowUpCycleGateInvariantError(
                    "Cycle gate accepts only "
                    "UNVERIFIED_EXTERNAL Evidence."
                )
            )

        if (
            verification.get(
                "required_authority"
            )
            != CouncilId.AY.value
        ):
            raise (
                RadarFollowUpCycleGateInvariantError(
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
                RadarFollowUpCycleGateInvariantError(
                    "Cycle gate cannot accept "
                    "system-truth Evidence."
                )
            )

        if (
            self.verification_status
            != "UNVERIFIED_EXTERNAL"
        ):
            raise (
                RadarFollowUpCycleGateInvariantError(
                    "Cycle decision must remain "
                    "UNVERIFIED_EXTERNAL."
                )
            )

        if self.system_truth_asserted is not False:
            raise (
                RadarFollowUpCycleGateInvariantError(
                    "Cycle decision cannot assert "
                    "system truth."
                )
            )

        if self.cycle_decision_created is not True:
            raise (
                RadarFollowUpCycleGateInvariantError(
                    "Cycle decision must be "
                    "explicitly created."
                )
            )

        passive_flags = (
            "cycle_started",
            "radar_evaluated",
            "reevaluation_authorized",
            "new_research_request_created",
            "network_requested",
            "tool_execution_requested",
            "mission_transition_requested",
            "persistence_requested",
            "learning_asserted",
            "authorization_asserted",
            "promotion_asserted",
            "activation_asserted",
            "execution_asserted",
        )

        for name in passive_flags:
            if getattr(
                self,
                name,
            ) is not False:
                raise (
                    RadarFollowUpCycleGateInvariantError(
                        "Cycle gate cannot assert "
                        f"{name}."
                    )
                )

    @property
    def rank(
        self,
    ) -> int:
        return self.source_entry.rank

    @property
    def origin_evidence_id(
        self,
    ) -> str:
        return (
            self.source_entry
            .origin_evidence_id
        )

    @property
    def evidence_id(
        self,
    ) -> str:
        return (
            self.source_entry
            .returned_evidence_id
        )

    @property
    def task_id(
        self,
    ) -> str:
        return self.source_entry.task_id

    @property
    def source_ref(
        self,
    ) -> str:
        return self.source_entry.evidence.source_ref

    @property
    def claim(
        self,
    ) -> str:
        return self.source_entry.evidence.claim

    @property
    def provider_id(
        self,
    ) -> str:
        return self.source_entry.provider_id

    @property
    def tool_name(
        self,
    ) -> str:
        return self.source_entry.tool_name

    @property
    def evidence(
        self,
    ) -> Evidence:
        return self.source_entry.evidence

    @property
    def eligible_for_reevaluation(
        self,
    ) -> bool:
        return (
            self.disposition
            is RadarFollowUpCycleDisposition
            .ELIGIBLE_FOR_REEVALUATION
        )

    @property
    def stop_cycle(
        self,
    ) -> bool:
        return (
            self.disposition
            is RadarFollowUpCycleDisposition
            .STOP_CYCLE
        )


@dataclass(
    frozen=True,
    slots=True,
)
class RadarFollowUpCycleGateResult:
    entries: tuple[
        RadarFollowUpCycleGateEntry,
        ...
    ]

    def __post_init__(
        self,
    ) -> None:
        for entry in self.entries:
            if not isinstance(
                entry,
                RadarFollowUpCycleGateEntry,
            ):
                raise TypeError(
                    "entries must contain "
                    "RadarFollowUpCycleGateEntry."
                )

        evidence_ids = tuple(
            entry.evidence_id
            for entry in self.entries
        )

        if (
            len(evidence_ids)
            != len(set(evidence_ids))
        ):
            raise (
                RadarFollowUpCycleGateInvariantError(
                    "Cycle gate requires unique "
                    "returned Evidence IDs."
                )
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
                RadarFollowUpCycleGateInvariantError(
                    "Cycle gate requires unique "
                    "origin Evidence IDs."
                )
            )

        ranks = tuple(
            entry.rank
            for entry in self.entries
        )

        if ranks != tuple(sorted(ranks)):
            raise (
                RadarFollowUpCycleGateInvariantError(
                    "Cycle gate must preserve "
                    "reintegration rank order."
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
    def origin_evidence_ids(
        self,
    ) -> tuple[str, ...]:
        return tuple(
            entry.origin_evidence_id
            for entry in self.entries
        )

    @property
    def eligible_evidence_ids(
        self,
    ) -> tuple[str, ...]:
        return tuple(
            entry.evidence_id
            for entry in self.entries
            if entry.eligible_for_reevaluation
        )

    @property
    def stopped_evidence_ids(
        self,
    ) -> tuple[str, ...]:
        return tuple(
            entry.evidence_id
            for entry in self.entries
            if entry.stop_cycle
        )


class GovernedRadarFollowUpCycleGate:
    """
    ADEL0.23 explicit follow-up cycle gate.

    This boundary consumes ADEL0.22C Evidence
    reintegration output and records exactly one
    explicit disposition per returned Evidence:

      ELIGIBLE_FOR_REEVALUATION
      STOP_CYCLE

    Eligibility is NOT authorization and does not
    start another Radar/research cycle.

    This gate performs no Radar evaluation,
    research request creation, provider routing,
    network access, tool execution, persistence,
    mission transition, truth verification,
    learning, promotion, or activation.

    CYCLE ELIGIBLE != CYCLE STARTED.
    CYCLE ELIGIBLE != RADAR EVALUATED.
    CYCLE ELIGIBLE != REEVALUATION AUTHORIZED.
    CYCLE ELIGIBLE != NEW RESEARCH REQUEST.
    CYCLE ELIGIBLE != NETWORK REQUEST.
    CYCLE ELIGIBLE != EXECUTION.
    CYCLE ELIGIBLE != TRUTH.
    """

    @staticmethod
    def decide(
        reintegration: (
            RadarResearchEvidenceReintegrationResult
        ),
        *,
        decisions: Mapping[
            str,
            RadarFollowUpCycleDisposition,
        ],
    ) -> RadarFollowUpCycleGateResult:
        if not isinstance(
            reintegration,
            RadarResearchEvidenceReintegrationResult,
        ):
            raise TypeError(
                "reintegration must be "
                "RadarResearchEvidenceReintegrationResult."
            )

        if not isinstance(
            decisions,
            Mapping,
        ):
            raise TypeError(
                "decisions must be a mapping."
            )

        normalized: dict[
            str,
            RadarFollowUpCycleDisposition,
        ] = {}

        for evidence_id, disposition in (
            decisions.items()
        ):
            if (
                not isinstance(
                    evidence_id,
                    str,
                )
                or not evidence_id.strip()
            ):
                raise (
                    RadarFollowUpCycleGateInvariantError(
                        "Decision Evidence IDs must "
                        "be non-empty strings."
                    )
                )

            if not isinstance(
                disposition,
                RadarFollowUpCycleDisposition,
            ):
                raise TypeError(
                    "Cycle dispositions must be "
                    "RadarFollowUpCycleDisposition."
                )

            normalized[evidence_id] = (
                disposition
            )

        expected_ids = set(
            reintegration.evidence_ids
        )

        supplied_ids = set(
            normalized
        )

        if supplied_ids != expected_ids:
            missing = sorted(
                expected_ids - supplied_ids
            )

            extra = sorted(
                supplied_ids - expected_ids
            )

            raise (
                RadarFollowUpCycleGateInvariantError(
                    "Cycle decisions must cover "
                    "exactly the returned Evidence "
                    "IDs; "
                    f"missing={missing}, "
                    f"extra={extra}."
                )
            )

        entries = tuple(
            RadarFollowUpCycleGateEntry(
                source_entry=entry,
                disposition=normalized[
                    entry.returned_evidence_id
                ],
            )
            for entry in reintegration.entries
        )

        return RadarFollowUpCycleGateResult(
            entries=entries
        )


__all__ = [
    "GovernedRadarFollowUpCycleGate",
    "RadarFollowUpCycleDisposition",
    "RadarFollowUpCycleGateEntry",
    "RadarFollowUpCycleGateInvariantError",
    "RadarFollowUpCycleGateResult",
]
