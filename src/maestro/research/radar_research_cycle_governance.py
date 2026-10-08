from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum
from math import isfinite

from .novelty_relevance import (
    NoveltyRelevanceEvaluator,
)
from .radar_research_followup_cycle_gate import (
    RadarFollowUpCycleDisposition,
    RadarFollowUpCycleGateEntry,
    RadarFollowUpCycleGateResult,
)


MAX_RADAR_FOLLOWUP_CYCLES = 8


class RadarFollowUpCycleGovernanceInvariantError(
    ValueError
):
    pass


class RadarFollowUpCycleGovernanceDisposition(
    StrEnum
):
    ADMIT_REEVALUATION = (
        "ADMIT_REEVALUATION"
    )

    STOP_NOT_ELIGIBLE = (
        "STOP_NOT_ELIGIBLE"
    )

    STOP_BUDGET = "STOP_BUDGET"

    STOP_DUPLICATE = "STOP_DUPLICATE"

    STOP_CONVERGED = "STOP_CONVERGED"


def _require_real_unit(
    value: float,
    name: str,
) -> float:
    if isinstance(
        value,
        bool,
    ) or not isinstance(
        value,
        (int, float),
    ):
        raise TypeError(
            f"{name} must be a real number."
        )

    normalized = float(
        value
    )

    if not isfinite(
        normalized
    ):
        raise (
            RadarFollowUpCycleGovernanceInvariantError(
                f"{name} must be finite."
            )
        )

    if not (
        0.0
        <= normalized
        <= 1.0
    ):
        raise (
            RadarFollowUpCycleGovernanceInvariantError(
                f"{name} must be within [0, 1]."
            )
        )

    return normalized


def _require_nonempty_strings(
    values: tuple[str, ...],
    name: str,
) -> tuple[str, ...]:
    if not isinstance(
        values,
        tuple,
    ):
        raise TypeError(
            f"{name} must be a tuple."
        )

    normalized = []

    for value in values:
        if (
            not isinstance(
                value,
                str,
            )
            or not value.strip()
        ):
            raise (
                RadarFollowUpCycleGovernanceInvariantError(
                    f"{name} must contain "
                    "non-empty strings only."
                )
            )

        normalized.append(
            value.strip()
        )

    if (
        len(normalized)
        != len(set(normalized))
    ):
        raise (
            RadarFollowUpCycleGovernanceInvariantError(
                f"{name} must not contain "
                "duplicates."
            )
        )

    return tuple(
        sorted(normalized)
    )


def _require_digest(
    value: str,
) -> str:
    if not isinstance(
        value,
        str,
    ):
        raise TypeError(
            "content digests must be strings."
        )

    normalized = (
        value.strip().lower()
    )

    if (
        len(normalized) != 64
        or any(
            char not in "0123456789abcdef"
            for char in normalized
        )
    ):
        raise (
            RadarFollowUpCycleGovernanceInvariantError(
                "Content digests must be "
                "64-character SHA-256 hex."
            )
        )

    return normalized


@dataclass(
    frozen=True,
    slots=True,
)
class RadarFollowUpCyclePolicy:
    max_cycles: int = 3

    minimum_novelty: float = 0.05

    def __post_init__(
        self,
    ) -> None:
        if (
            not isinstance(
                self.max_cycles,
                int,
            )
            or isinstance(
                self.max_cycles,
                bool,
            )
        ):
            raise TypeError(
                "max_cycles must be an integer."
            )

        if not (
            1
            <= self.max_cycles
            <= MAX_RADAR_FOLLOWUP_CYCLES
        ):
            raise (
                RadarFollowUpCycleGovernanceInvariantError(
                    "max_cycles must be between "
                    "1 and "
                    f"{MAX_RADAR_FOLLOWUP_CYCLES}."
                )
            )

        object.__setattr__(
            self,
            "minimum_novelty",
            _require_real_unit(
                self.minimum_novelty,
                "minimum_novelty",
            ),
        )


@dataclass(
    frozen=True,
    slots=True,
)
class RadarFollowUpCycleContext:
    completed_cycles: int

    seen_evidence_ids: tuple[
        str,
        ...
    ] = ()

    seen_content_digests: tuple[
        str,
        ...
    ] = ()

    known_claims: tuple[
        str,
        ...
    ] = ()

    def __post_init__(
        self,
    ) -> None:
        if (
            not isinstance(
                self.completed_cycles,
                int,
            )
            or isinstance(
                self.completed_cycles,
                bool,
            )
        ):
            raise TypeError(
                "completed_cycles must be "
                "an integer."
            )

        if self.completed_cycles < 0:
            raise (
                RadarFollowUpCycleGovernanceInvariantError(
                    "completed_cycles cannot "
                    "be negative."
                )
            )

        object.__setattr__(
            self,
            "seen_evidence_ids",
            _require_nonempty_strings(
                self.seen_evidence_ids,
                "seen_evidence_ids",
            ),
        )

        if not isinstance(
            self.seen_content_digests,
            tuple,
        ):
            raise TypeError(
                "seen_content_digests must "
                "be a tuple."
            )

        digests = tuple(
            _require_digest(
                value
            )
            for value
            in self.seen_content_digests
        )

        if (
            len(digests)
            != len(set(digests))
        ):
            raise (
                RadarFollowUpCycleGovernanceInvariantError(
                    "seen_content_digests must "
                    "not contain duplicates."
                )
            )

        object.__setattr__(
            self,
            "seen_content_digests",
            tuple(
                sorted(digests)
            ),
        )

        object.__setattr__(
            self,
            "known_claims",
            _require_nonempty_strings(
                self.known_claims,
                "known_claims",
            ),
        )


def _current_digest(
    source_entry: RadarFollowUpCycleGateEntry,
) -> str:
    return _require_digest(
        source_entry
        .source_entry
        .return_packet
        .provenance
        .digest
        .hex_digest
    )


def _derive(
    source_entry: RadarFollowUpCycleGateEntry,
    *,
    context: (
        RadarFollowUpCycleContext
        | None
    ),
    policy: RadarFollowUpCyclePolicy,
) -> tuple[
    RadarFollowUpCycleGovernanceDisposition,
    float | None,
    str,
]:
    if not isinstance(
        source_entry,
        RadarFollowUpCycleGateEntry,
    ):
        raise TypeError(
            "source_entry must be "
            "RadarFollowUpCycleGateEntry."
        )

    if not isinstance(
        policy,
        RadarFollowUpCyclePolicy,
    ):
        raise TypeError(
            "policy must be "
            "RadarFollowUpCyclePolicy."
        )

    if (
        source_entry.disposition
        is RadarFollowUpCycleDisposition
        .STOP_CYCLE
    ):
        if context is not None:
            raise (
                RadarFollowUpCycleGovernanceInvariantError(
                    "STOP_CYCLE entries must not "
                    "receive cycle contexts."
                )
            )

        return (
            RadarFollowUpCycleGovernanceDisposition
            .STOP_NOT_ELIGIBLE,
            None,
            "Upstream cycle gate stopped "
            "this Evidence.",
        )

    if (
        source_entry.disposition
        is not RadarFollowUpCycleDisposition
        .ELIGIBLE_FOR_REEVALUATION
    ):
        raise (
            RadarFollowUpCycleGovernanceInvariantError(
                "Unsupported upstream cycle "
                "disposition."
            )
        )

    if not isinstance(
        context,
        RadarFollowUpCycleContext,
    ):
        raise TypeError(
            "Eligible Evidence requires "
            "RadarFollowUpCycleContext."
        )

    if (
        context.completed_cycles
        >= policy.max_cycles
    ):
        return (
            RadarFollowUpCycleGovernanceDisposition
            .STOP_BUDGET,
            None,
            "Follow-up cycle budget exhausted.",
        )

    digest = _current_digest(
        source_entry
    )

    if (
        source_entry.evidence_id
        in context.seen_evidence_ids
        or digest
        in context.seen_content_digests
    ):
        return (
            RadarFollowUpCycleGovernanceDisposition
            .STOP_DUPLICATE,
            None,
            "Evidence identity or content digest "
            "was already seen.",
        )

    novelty = (
        NoveltyRelevanceEvaluator
        .evaluate(
            source_entry.evidence,
            known_claims=(
                context.known_claims
            ),
        )
        .novelty
    )

    if (
        novelty
        <= policy.minimum_novelty
    ):
        return (
            RadarFollowUpCycleGovernanceDisposition
            .STOP_CONVERGED,
            novelty,
            "Evidence novelty is at or below "
            "the convergence threshold.",
        )

    return (
        RadarFollowUpCycleGovernanceDisposition
        .ADMIT_REEVALUATION,
        novelty,
        "Budget, deduplication and "
        "convergence gates passed.",
    )


@dataclass(
    frozen=True,
    slots=True,
)
class RadarFollowUpCycleGovernanceEntry:
    source_entry: (
        RadarFollowUpCycleGateEntry
    )

    policy: RadarFollowUpCyclePolicy

    context: (
        RadarFollowUpCycleContext
        | None
    )

    disposition: (
        RadarFollowUpCycleGovernanceDisposition
    )

    novelty: float | None

    reason: str

    reevaluation_authorized: bool

    cycle_started: bool = False
    radar_evaluated: bool = False

    new_research_request_created: bool = False
    network_requested: bool = False
    tool_execution_requested: bool = False

    mission_transition_requested: bool = False
    persistence_requested: bool = False

    verification_status: str = (
        "UNVERIFIED_EXTERNAL"
    )

    system_truth_asserted: bool = False

    ay_validation_asserted: bool = False
    ex_authorization_asserted: bool = False

    learning_asserted: bool = False
    promotion_asserted: bool = False
    activation_asserted: bool = False
    execution_asserted: bool = False

    def __post_init__(
        self,
    ) -> None:
        if not isinstance(
            self.source_entry,
            RadarFollowUpCycleGateEntry,
        ):
            raise TypeError(
                "source_entry must be "
                "RadarFollowUpCycleGateEntry."
            )

        if not isinstance(
            self.policy,
            RadarFollowUpCyclePolicy,
        ):
            raise TypeError(
                "policy must be "
                "RadarFollowUpCyclePolicy."
            )

        if (
            self.context is not None
            and not isinstance(
                self.context,
                RadarFollowUpCycleContext,
            )
        ):
            raise TypeError(
                "context must be "
                "RadarFollowUpCycleContext "
                "or None."
            )

        if not isinstance(
            self.disposition,
            RadarFollowUpCycleGovernanceDisposition,
        ):
            raise TypeError(
                "disposition must be "
                "RadarFollowUpCycleGovernanceDisposition."
            )

        if (
            not isinstance(
                self.reason,
                str,
            )
            or not self.reason.strip()
        ):
            raise (
                RadarFollowUpCycleGovernanceInvariantError(
                    "reason must be non-empty."
                )
            )

        (
            expected_disposition,
            expected_novelty,
            expected_reason,
        ) = _derive(
            self.source_entry,
            context=self.context,
            policy=self.policy,
        )

        if (
            self.disposition
            is not expected_disposition
        ):
            raise (
                RadarFollowUpCycleGovernanceInvariantError(
                    "Cycle governance disposition "
                    "does not match policy."
                )
            )

        if self.novelty != expected_novelty:
            raise (
                RadarFollowUpCycleGovernanceInvariantError(
                    "Cycle governance novelty "
                    "does not match policy."
                )
            )

        if self.reason != expected_reason:
            raise (
                RadarFollowUpCycleGovernanceInvariantError(
                    "Cycle governance reason "
                    "does not match policy."
                )
            )

        should_authorize = (
            self.disposition
            is RadarFollowUpCycleGovernanceDisposition
            .ADMIT_REEVALUATION
        )

        if (
            self.reevaluation_authorized
            is not should_authorize
        ):
            raise (
                RadarFollowUpCycleGovernanceInvariantError(
                    "reevaluation_authorized "
                    "must match disposition."
                )
            )

        if (
            self.verification_status
            != "UNVERIFIED_EXTERNAL"
        ):
            raise (
                RadarFollowUpCycleGovernanceInvariantError(
                    "Cycle governance must remain "
                    "UNVERIFIED_EXTERNAL."
                )
            )

        if self.system_truth_asserted is not False:
            raise (
                RadarFollowUpCycleGovernanceInvariantError(
                    "Cycle governance cannot "
                    "assert system truth."
                )
            )

        passive_flags = (
            "cycle_started",
            "radar_evaluated",
            "new_research_request_created",
            "network_requested",
            "tool_execution_requested",
            "mission_transition_requested",
            "persistence_requested",
            "ay_validation_asserted",
            "ex_authorization_asserted",
            "learning_asserted",
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
                    RadarFollowUpCycleGovernanceInvariantError(
                        "Cycle governance cannot "
                        f"assert {name}."
                    )
                )

    @property
    def rank(
        self,
    ) -> int:
        return self.source_entry.rank

    @property
    def evidence_id(
        self,
    ) -> str:
        return self.source_entry.evidence_id

    @property
    def origin_evidence_id(
        self,
    ) -> str:
        return (
            self.source_entry
            .origin_evidence_id
        )

    @property
    def task_id(
        self,
    ) -> str:
        return self.source_entry.task_id

    @property
    def evidence(
        self,
    ):
        return self.source_entry.evidence

    @property
    def content_digest(
        self,
    ) -> str:
        return _current_digest(
            self.source_entry
        )

    @property
    def admitted(
        self,
    ) -> bool:
        return (
            self.disposition
            is RadarFollowUpCycleGovernanceDisposition
            .ADMIT_REEVALUATION
        )


@dataclass(
    frozen=True,
    slots=True,
)
class RadarFollowUpCycleGovernanceResult:
    entries: tuple[
        RadarFollowUpCycleGovernanceEntry,
        ...
    ]

    def __post_init__(
        self,
    ) -> None:
        for entry in self.entries:
            if not isinstance(
                entry,
                RadarFollowUpCycleGovernanceEntry,
            ):
                raise TypeError(
                    "entries must contain "
                    "RadarFollowUpCycleGovernanceEntry."
                )

        ids = tuple(
            entry.evidence_id
            for entry in self.entries
        )

        if len(ids) != len(set(ids)):
            raise (
                RadarFollowUpCycleGovernanceInvariantError(
                    "Cycle governance requires "
                    "unique Evidence IDs."
                )
            )

        ranks = tuple(
            entry.rank
            for entry in self.entries
        )

        if ranks != tuple(sorted(ranks)):
            raise (
                RadarFollowUpCycleGovernanceInvariantError(
                    "Cycle governance must preserve "
                    "cycle-gate rank order."
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
    def admitted_evidence_ids(
        self,
    ) -> tuple[str, ...]:
        return tuple(
            entry.evidence_id
            for entry in self.entries
            if entry.admitted
        )

    @property
    def stopped_evidence_ids(
        self,
    ) -> tuple[str, ...]:
        return tuple(
            entry.evidence_id
            for entry in self.entries
            if not entry.admitted
        )


class GovernedRadarFollowUpCycleGovernor:
    """
    ADEL0.24 pure bounded-cycle governance.

    It consumes ADEL0.23 cycle-gate decisions and
    explicit immutable caller-supplied history.

    It enforces:
      - a hard bounded cycle budget,
      - exact Evidence-ID deduplication,
      - SHA-256 content deduplication,
      - semantic convergence using the existing
        pure novelty evaluator.

    It contains no hidden counters, singleton
    state, mutable history, durable-store lookup,
    Radar execution, network activity or tool
    invocation.

    ADMIT_REEVALUATION is a narrow permission to
    cross a later reevaluation-start boundary.

    ADMIT_REEVALUATION != CYCLE STARTED.
    ADMIT_REEVALUATION != RADAR EVALUATED.
    ADMIT_REEVALUATION != RESEARCH REQUEST.
    ADMIT_REEVALUATION != NETWORK.
    ADMIT_REEVALUATION != EXECUTION.
    ADMIT_REEVALUATION != TRUTH.
    """

    @staticmethod
    def govern(
        gate: RadarFollowUpCycleGateResult,
        *,
        contexts: Mapping[
            str,
            RadarFollowUpCycleContext,
        ],
        policy: RadarFollowUpCyclePolicy,
    ) -> RadarFollowUpCycleGovernanceResult:
        if not isinstance(
            gate,
            RadarFollowUpCycleGateResult,
        ):
            raise TypeError(
                "gate must be "
                "RadarFollowUpCycleGateResult."
            )

        if not isinstance(
            contexts,
            Mapping,
        ):
            raise TypeError(
                "contexts must be a mapping."
            )

        if not isinstance(
            policy,
            RadarFollowUpCyclePolicy,
        ):
            raise TypeError(
                "policy must be "
                "RadarFollowUpCyclePolicy."
            )

        normalized: dict[
            str,
            RadarFollowUpCycleContext,
        ] = {}

        for evidence_id, context in (
            contexts.items()
        ):
            if (
                not isinstance(
                    evidence_id,
                    str,
                )
                or not evidence_id.strip()
            ):
                raise (
                    RadarFollowUpCycleGovernanceInvariantError(
                        "Context Evidence IDs must "
                        "be non-empty strings."
                    )
                )

            if not isinstance(
                context,
                RadarFollowUpCycleContext,
            ):
                raise TypeError(
                    "Cycle contexts must be "
                    "RadarFollowUpCycleContext."
                )

            normalized[
                evidence_id
            ] = context

        expected_context_ids = set(
            gate.eligible_evidence_ids
        )

        supplied_context_ids = set(
            normalized
        )

        if (
            supplied_context_ids
            != expected_context_ids
        ):
            missing = sorted(
                expected_context_ids
                - supplied_context_ids
            )

            extra = sorted(
                supplied_context_ids
                - expected_context_ids
            )

            raise (
                RadarFollowUpCycleGovernanceInvariantError(
                    "Cycle contexts must cover "
                    "exactly ELIGIBLE_FOR_REEVALUATION "
                    "Evidence IDs; "
                    f"missing={missing}, "
                    f"extra={extra}."
                )
            )

        entries = []

        for source_entry in gate.entries:
            context = (
                normalized[
                    source_entry.evidence_id
                ]
                if (
                    source_entry
                    .eligible_for_reevaluation
                )
                else None
            )

            (
                disposition,
                novelty,
                reason,
            ) = _derive(
                source_entry,
                context=context,
                policy=policy,
            )

            entries.append(
                RadarFollowUpCycleGovernanceEntry(
                    source_entry=source_entry,
                    policy=policy,
                    context=context,
                    disposition=disposition,
                    novelty=novelty,
                    reason=reason,
                    reevaluation_authorized=(
                        disposition
                        is RadarFollowUpCycleGovernanceDisposition
                        .ADMIT_REEVALUATION
                    ),
                )
            )

        return (
            RadarFollowUpCycleGovernanceResult(
                entries=tuple(entries)
            )
        )


__all__ = [
    "MAX_RADAR_FOLLOWUP_CYCLES",
    "GovernedRadarFollowUpCycleGovernor",
    "RadarFollowUpCycleContext",
    "RadarFollowUpCycleGovernanceDisposition",
    "RadarFollowUpCycleGovernanceEntry",
    "RadarFollowUpCycleGovernanceInvariantError",
    "RadarFollowUpCycleGovernanceResult",
    "RadarFollowUpCyclePolicy",
]
