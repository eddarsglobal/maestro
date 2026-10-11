from __future__ import annotations

import hashlib
import json

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Iterable

from maestro.orchestration.governed_adaptive_mission_closure import (
    GovernedMissionVerdict,
    MissionVerdictState,
)
from maestro.orchestration.governed_durable_mission_recovery import (
    GovernedDurableMissionCheckpoint,
)


GOVERNED_EXPERIENCE_LEARNING_PROMOTION_VERSION = 1


class ExperienceLearningPromotionInvariantError(
    ValueError
):
    pass


class ExperienceCaptureIncompleteError(
    ExperienceLearningPromotionInvariantError
):
    pass


class LearningCandidateIncompleteError(
    ExperienceLearningPromotionInvariantError
):
    pass


class PromotionEvaluationIncompleteError(
    ExperienceLearningPromotionInvariantError
):
    pass


class ExperienceOutcome(StrEnum):
    SUCCESS = "SUCCESS"
    PARTIAL = "PARTIAL"
    FAILURE = "FAILURE"
    ABORTED = "ABORTED"


class EvidenceState(StrEnum):
    PASS = "PASS"
    FAIL = "FAIL"
    UNKNOWN = "UNKNOWN"


class LearningCandidateKind(StrEnum):
    SUCCESS_PATTERN = "SUCCESS_PATTERN"
    FAILURE_PATTERN = "FAILURE_PATTERN"
    ROUTING_POLICY = "ROUTING_POLICY"
    RESOURCE_POLICY = "RESOURCE_POLICY"
    RETRY_POLICY = "RETRY_POLICY"
    TOOL_POLICY = "TOOL_POLICY"
    CONTEXT_POLICY = "CONTEXT_POLICY"
    STRATEGY_POLICY = "STRATEGY_POLICY"


class PromotionDecisionState(StrEnum):
    PROMOTION_ELIGIBLE = "PROMOTION_ELIGIBLE"
    REJECTED = "REJECTED"
    UNKNOWN = "UNKNOWN"


def _required_text(
    value: str,
    name: str,
) -> str:
    if not isinstance(value, str):
        raise TypeError(
            f"{name} must be a string."
        )

    value = value.strip()

    if not value:
        raise ExperienceLearningPromotionInvariantError(
            f"{name} must not be empty."
        )

    if "\x00" in value:
        raise ExperienceLearningPromotionInvariantError(
            f"{name} must not contain NUL."
        )

    return value


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


def _normalized_tuple(
    values: Iterable[str],
    name: str,
    *,
    require_nonempty: bool = True,
) -> tuple[str, ...]:
    rows = tuple(
        sorted(
            _required_text(
                item,
                name,
            )
            for item in values
        )
    )

    if require_nonempty and not rows:
        raise ExperienceLearningPromotionInvariantError(
            f"{name} must not be empty."
        )

    if len(rows) != len(set(rows)):
        raise ExperienceLearningPromotionInvariantError(
            f"{name} values must be unique."
        )

    return rows


def _score(
    value: float,
    name: str,
) -> float:
    if (
        not isinstance(
            value,
            (int, float),
        )
        or isinstance(
            value,
            bool,
        )
    ):
        raise TypeError(
            f"{name} must be numeric."
        )

    value = float(value)

    if not 0.0 <= value <= 1.0:
        raise ExperienceLearningPromotionInvariantError(
            f"{name} must be between 0 and 1."
        )

    return value


def _nonnegative_int(
    value: int,
    name: str,
) -> int:
    if (
        not isinstance(value, int)
        or isinstance(value, bool)
        or value < 0
    ):
        raise ExperienceLearningPromotionInvariantError(
            f"{name} must be >= 0."
        )

    return value


def _positive_int(
    value: int,
    name: str,
) -> int:
    value = _nonnegative_int(
        value,
        name,
    )

    if value < 1:
        raise ExperienceLearningPromotionInvariantError(
            f"{name} must be >= 1."
        )

    return value


def _canonical_json(
    value: Any,
) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    )


def _stable_id(
    prefix: str,
    payload: Any,
) -> str:
    return (
        prefix
        + "-"
        + hashlib.sha256(
            _canonical_json(
                payload
            ).encode("utf-8")
        ).hexdigest()[:24]
    )


@dataclass(
    frozen=True,
    slots=True,
)
class ResourcePerformanceEvidence:
    resource_id: str
    capability_id: str

    success_state: EvidenceState

    quality_score: float
    reliability_score: float

    cost_units: int
    latency_ms: int

    evidence_refs: tuple[str, ...]

    performance_id: str = field(
        init=False
    )

    def __post_init__(self) -> None:
        for name in (
            "resource_id",
            "capability_id",
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
            self.success_state,
            EvidenceState,
        ):
            raise TypeError(
                "success_state must be "
                "EvidenceState."
            )

        for name in (
            "quality_score",
            "reliability_score",
        ):
            object.__setattr__(
                self,
                name,
                _score(
                    getattr(self, name),
                    name,
                ),
            )

        for name in (
            "cost_units",
            "latency_ms",
        ):
            object.__setattr__(
                self,
                name,
                _nonnegative_int(
                    getattr(self, name),
                    name,
                ),
            )

        object.__setattr__(
            self,
            "evidence_refs",
            _normalized_tuple(
                self.evidence_refs,
                "evidence_ref",
            ),
        )

        object.__setattr__(
            self,
            "performance_id",
            _stable_id(
                "RPE",
                {
                    "resource_id": (
                        self.resource_id
                    ),
                    "capability_id": (
                        self.capability_id
                    ),
                    "success_state": (
                        self.success_state.value
                    ),
                    "quality_score": (
                        self.quality_score
                    ),
                    "reliability_score": (
                        self.reliability_score
                    ),
                    "cost_units": (
                        self.cost_units
                    ),
                    "latency_ms": (
                        self.latency_ms
                    ),
                    "evidence_refs": list(
                        self.evidence_refs
                    ),
                },
            ),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "performance_id": (
                self.performance_id
            ),
            "resource_id": self.resource_id,
            "capability_id": (
                self.capability_id
            ),
            "success_state": (
                self.success_state.value
            ),
            "quality_score": (
                self.quality_score
            ),
            "reliability_score": (
                self.reliability_score
            ),
            "cost_units": (
                self.cost_units
            ),
            "latency_ms": (
                self.latency_ms
            ),
            "evidence_refs": list(
                self.evidence_refs
            ),
        }


@dataclass(
    frozen=True,
    slots=True,
)
class ImmutableExperienceEvidence:
    checkpoint_id: str
    checkpoint_payload_sha256: str

    mission_contract_id: str
    plan_id: str
    routing_plan_id: str

    mission_verdict_id: str
    mission_verdict_state: MissionVerdictState

    outcome: ExperienceOutcome

    verified_result_ref: str | None

    failure_refs: tuple[str, ...]
    retry_evidence_refs: tuple[str, ...]

    routing_quality_score: float

    resource_performance: tuple[
        ResourcePerformanceEvidence,
        ...,
    ]

    human_correction_refs: tuple[str, ...]

    evidence_refs: tuple[str, ...]

    cost_units: int
    latency_ms: int

    experience_id: str = field(
        init=False
    )

    experience_sha256: str = field(
        init=False
    )

    learning_authorized: bool = False
    policy_mutation_authorized: bool = False
    memory_authority_granted: bool = False
    routing_authority_granted: bool = False
    council_authority_granted: bool = False
    core_mutation_authorized: bool = False
    promotion_authorized: bool = False

    def __post_init__(self) -> None:
        for name in (
            "checkpoint_id",
            "checkpoint_payload_sha256",
            "mission_contract_id",
            "plan_id",
            "routing_plan_id",
            "mission_verdict_id",
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
            self.mission_verdict_state,
            MissionVerdictState,
        ):
            raise TypeError(
                "mission_verdict_state must "
                "be MissionVerdictState."
            )

        if not isinstance(
            self.outcome,
            ExperienceOutcome,
        ):
            raise TypeError(
                "outcome must be "
                "ExperienceOutcome."
            )

        object.__setattr__(
            self,
            "verified_result_ref",
            _optional_text(
                self.verified_result_ref,
                "verified_result_ref",
            ),
        )

        for name in (
            "failure_refs",
            "retry_evidence_refs",
            "human_correction_refs",
        ):
            object.__setattr__(
                self,
                name,
                _normalized_tuple(
                    getattr(self, name),
                    name,
                    require_nonempty=False,
                ),
            )

        object.__setattr__(
            self,
            "evidence_refs",
            _normalized_tuple(
                self.evidence_refs,
                "evidence_ref",
            ),
        )

        object.__setattr__(
            self,
            "routing_quality_score",
            _score(
                self.routing_quality_score,
                "routing_quality_score",
            ),
        )

        for name in (
            "cost_units",
            "latency_ms",
        ):
            object.__setattr__(
                self,
                name,
                _nonnegative_int(
                    getattr(self, name),
                    name,
                ),
            )

        rows = tuple(
            sorted(
                self.resource_performance,
                key=lambda item: (
                    item.resource_id,
                    item.capability_id,
                ),
            )
        )

        if not rows:
            raise ExperienceCaptureIncompleteError(
                "Experience must contain "
                "resource performance evidence."
            )

        if not all(
            isinstance(
                item,
                ResourcePerformanceEvidence,
            )
            for item in rows
        ):
            raise TypeError(
                "resource_performance must "
                "contain "
                "ResourcePerformanceEvidence."
            )

        performance_ids = [
            item.performance_id
            for item in rows
        ]

        if len(performance_ids) != len(
            set(performance_ids)
        ):
            raise ExperienceLearningPromotionInvariantError(
                "Resource performance evidence "
                "must be unique."
            )

        object.__setattr__(
            self,
            "resource_performance",
            rows,
        )

        if (
            self.mission_verdict_state
            is MissionVerdictState.UNKNOWN
        ):
            raise ExperienceCaptureIncompleteError(
                "UNKNOWN mission verdict "
                "cannot become experience evidence."
            )

        if (
            self.outcome
            is ExperienceOutcome.SUCCESS
        ):
            if (
                self.mission_verdict_state
                is not MissionVerdictState.ACCEPTED
            ):
                raise ExperienceCaptureIncompleteError(
                    "SUCCESS requires ACCEPTED "
                    "mission verdict."
                )

            if self.verified_result_ref is None:
                raise ExperienceCaptureIncompleteError(
                    "SUCCESS requires a "
                    "verified result reference."
                )

        if (
            self.outcome
            is ExperienceOutcome.FAILURE
            and not self.failure_refs
        ):
            raise ExperienceCaptureIncompleteError(
                "FAILURE requires "
                "failure evidence."
            )

        for name in (
            "learning_authorized",
            "policy_mutation_authorized",
            "memory_authority_granted",
            "routing_authority_granted",
            "council_authority_granted",
            "core_mutation_authorized",
            "promotion_authorized",
        ):
            if getattr(self, name) is not False:
                raise ExperienceLearningPromotionInvariantError(
                    "Experience evidence cannot "
                    f"assert {name}."
                )

        payload = self.to_payload()

        digest = hashlib.sha256(
            _canonical_json(
                payload
            ).encode("utf-8")
        ).hexdigest()

        object.__setattr__(
            self,
            "experience_sha256",
            digest,
        )

        object.__setattr__(
            self,
            "experience_id",
            "EXP2-" + digest[:24],
        )

    def to_payload(self) -> dict[str, Any]:
        return {
            "checkpoint_id": self.checkpoint_id,
            "checkpoint_payload_sha256": (
                self.checkpoint_payload_sha256
            ),
            "mission_contract_id": (
                self.mission_contract_id
            ),
            "plan_id": self.plan_id,
            "routing_plan_id": (
                self.routing_plan_id
            ),
            "mission_verdict_id": (
                self.mission_verdict_id
            ),
            "mission_verdict_state": (
                self.mission_verdict_state.value
            ),
            "outcome": self.outcome.value,
            "verified_result_ref": (
                self.verified_result_ref
            ),
            "failure_refs": list(
                self.failure_refs
            ),
            "retry_evidence_refs": list(
                self.retry_evidence_refs
            ),
            "routing_quality_score": (
                self.routing_quality_score
            ),
            "resource_performance": [
                item.to_dict()
                for item
                in self.resource_performance
            ],
            "human_correction_refs": list(
                self.human_correction_refs
            ),
            "evidence_refs": list(
                self.evidence_refs
            ),
            "cost_units": self.cost_units,
            "latency_ms": self.latency_ms,
        }


@dataclass(
    frozen=True,
    slots=True,
)
class GovernedLearningCandidate:
    kind: LearningCandidateKind

    key: str
    statement: str

    support_experience_ids: tuple[
        str,
        ...,
    ]

    counter_experience_ids: tuple[
        str,
        ...,
    ]

    source_experience_sha256: tuple[
        str,
        ...,
    ]

    candidate_id: str = field(
        init=False
    )

    policy_mutation_authorized: bool = False
    memory_authority_granted: bool = False
    routing_authority_granted: bool = False
    council_authority_granted: bool = False
    core_mutation_authorized: bool = False
    production_behavior_changed: bool = False
    promotion_authorized: bool = False

    def __post_init__(self) -> None:
        if not isinstance(
            self.kind,
            LearningCandidateKind,
        ):
            raise TypeError(
                "kind must be "
                "LearningCandidateKind."
            )

        for name in (
            "key",
            "statement",
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
            "support_experience_ids",
            _normalized_tuple(
                self.support_experience_ids,
                "support_experience_id",
            ),
        )

        object.__setattr__(
            self,
            "counter_experience_ids",
            _normalized_tuple(
                self.counter_experience_ids,
                "counter_experience_id",
                require_nonempty=False,
            ),
        )

        object.__setattr__(
            self,
            "source_experience_sha256",
            _normalized_tuple(
                self.source_experience_sha256,
                "source_experience_sha256",
            ),
        )

        overlap = (
            set(self.support_experience_ids)
            & set(self.counter_experience_ids)
        )

        if overlap:
            raise ExperienceLearningPromotionInvariantError(
                "Support and counter "
                "experience sets must not overlap."
            )

        if len(
            self.support_experience_ids
        ) < 2:
            raise LearningCandidateIncompleteError(
                "Governed learning candidate "
                "requires at least two "
                "supporting experiences."
            )

        for name in (
            "policy_mutation_authorized",
            "memory_authority_granted",
            "routing_authority_granted",
            "council_authority_granted",
            "core_mutation_authorized",
            "production_behavior_changed",
            "promotion_authorized",
        ):
            if getattr(self, name) is not False:
                raise ExperienceLearningPromotionInvariantError(
                    "Learning candidate cannot "
                    f"assert {name}."
                )

        object.__setattr__(
            self,
            "candidate_id",
            _stable_id(
                "GLC",
                {
                    "kind": self.kind.value,
                    "key": self.key,
                    "statement": (
                        self.statement
                    ),
                    "support_experience_ids": list(
                        self
                        .support_experience_ids
                    ),
                    "counter_experience_ids": list(
                        self
                        .counter_experience_ids
                    ),
                    "source_experience_sha256": list(
                        self
                        .source_experience_sha256
                    ),
                },
            ),
        )


@dataclass(
    frozen=True,
    slots=True,
)
class PromotionPolicy:
    min_support: int
    min_samples: int

    min_replay_score: float
    min_shadow_success_rate: float
    min_improvement: float

    max_regressions: int

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "min_support",
            _positive_int(
                self.min_support,
                "min_support",
            ),
        )

        object.__setattr__(
            self,
            "min_samples",
            _positive_int(
                self.min_samples,
                "min_samples",
            ),
        )

        for name in (
            "min_replay_score",
            "min_shadow_success_rate",
            "min_improvement",
        ):
            object.__setattr__(
                self,
                name,
                _score(
                    getattr(self, name),
                    name,
                ),
            )

        object.__setattr__(
            self,
            "max_regressions",
            _nonnegative_int(
                self.max_regressions,
                "max_regressions",
            ),
        )


@dataclass(
    frozen=True,
    slots=True,
)
class PromotionEvaluationEvidence:
    candidate_id: str

    samples: int

    baseline_score: float
    candidate_score: float
    replay_score: float
    shadow_success_rate: float

    regression_count: int

    comparison_ref: str
    rollback_ref: str

    ay_validation: EvidenceState
    ex_authorization: EvidenceState

    evidence_refs: tuple[str, ...]

    evaluation_id: str = field(
        init=False
    )

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "candidate_id",
            _required_text(
                self.candidate_id,
                "candidate_id",
            ),
        )

        object.__setattr__(
            self,
            "samples",
            _positive_int(
                self.samples,
                "samples",
            ),
        )

        for name in (
            "baseline_score",
            "candidate_score",
            "replay_score",
            "shadow_success_rate",
        ):
            object.__setattr__(
                self,
                name,
                _score(
                    getattr(self, name),
                    name,
                ),
            )

        object.__setattr__(
            self,
            "regression_count",
            _nonnegative_int(
                self.regression_count,
                "regression_count",
            ),
        )

        for name in (
            "comparison_ref",
            "rollback_ref",
        ):
            object.__setattr__(
                self,
                name,
                _required_text(
                    getattr(self, name),
                    name,
                ),
            )

        for name in (
            "ay_validation",
            "ex_authorization",
        ):
            if not isinstance(
                getattr(self, name),
                EvidenceState,
            ):
                raise TypeError(
                    f"{name} must be "
                    "EvidenceState."
                )

        object.__setattr__(
            self,
            "evidence_refs",
            _normalized_tuple(
                self.evidence_refs,
                "evidence_ref",
            ),
        )

        object.__setattr__(
            self,
            "evaluation_id",
            _stable_id(
                "PEV",
                {
                    "candidate_id": (
                        self.candidate_id
                    ),
                    "samples": self.samples,
                    "baseline_score": (
                        self.baseline_score
                    ),
                    "candidate_score": (
                        self.candidate_score
                    ),
                    "replay_score": (
                        self.replay_score
                    ),
                    "shadow_success_rate": (
                        self
                        .shadow_success_rate
                    ),
                    "regression_count": (
                        self.regression_count
                    ),
                    "comparison_ref": (
                        self.comparison_ref
                    ),
                    "rollback_ref": (
                        self.rollback_ref
                    ),
                    "ay_validation": (
                        self.ay_validation.value
                    ),
                    "ex_authorization": (
                        self.ex_authorization.value
                    ),
                    "evidence_refs": list(
                        self.evidence_refs
                    ),
                },
            ),
        )


@dataclass(
    frozen=True,
    slots=True,
)
class GovernedPromotionDecision:
    candidate_id: str
    evaluation_id: str

    state: PromotionDecisionState

    reasons: tuple[str, ...]

    comparison_ref: str
    rollback_ref: str

    decision_id: str = field(
        init=False
    )

    policy_mutation_authorized: bool = False
    memory_mutation_authorized: bool = False
    routing_mutation_authorized: bool = False
    council_mutation_authorized: bool = False
    core_mutation_authorized: bool = False

    production_activation_authorized: bool = False
    execution_authorized: bool = False
    system_truth_asserted: bool = False

    def __post_init__(self) -> None:
        for name in (
            "candidate_id",
            "evaluation_id",
            "comparison_ref",
            "rollback_ref",
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
            self.state,
            PromotionDecisionState,
        ):
            raise TypeError(
                "state must be "
                "PromotionDecisionState."
            )

        object.__setattr__(
            self,
            "reasons",
            _normalized_tuple(
                self.reasons,
                "reason",
            ),
        )

        for name in (
            "policy_mutation_authorized",
            "memory_mutation_authorized",
            "routing_mutation_authorized",
            "council_mutation_authorized",
            "core_mutation_authorized",
            "production_activation_authorized",
            "execution_authorized",
            "system_truth_asserted",
        ):
            if getattr(self, name) is not False:
                raise ExperienceLearningPromotionInvariantError(
                    "Promotion decision cannot "
                    f"assert {name}."
                )

        object.__setattr__(
            self,
            "decision_id",
            _stable_id(
                "GPD",
                {
                    "candidate_id": (
                        self.candidate_id
                    ),
                    "evaluation_id": (
                        self.evaluation_id
                    ),
                    "state": self.state.value,
                    "reasons": list(
                        self.reasons
                    ),
                    "comparison_ref": (
                        self.comparison_ref
                    ),
                    "rollback_ref": (
                        self.rollback_ref
                    ),
                },
            ),
        )

    @property
    def promotion_eligible(self) -> bool:
        return (
            self.state
            is PromotionDecisionState
            .PROMOTION_ELIGIBLE
        )


class GovernedExperienceLearningPromotion:
    @staticmethod
    def capture(
        checkpoint: GovernedDurableMissionCheckpoint,
        verdict: GovernedMissionVerdict,
        *,
        outcome: ExperienceOutcome,
        verified_result_ref: str | None,
        failure_refs: Iterable[str],
        retry_evidence_refs: Iterable[str],
        routing_quality_score: float,
        resource_performance: Iterable[
            ResourcePerformanceEvidence
        ],
        human_correction_refs: Iterable[str],
        evidence_refs: Iterable[str],
        cost_units: int,
        latency_ms: int,
    ) -> ImmutableExperienceEvidence:
        if not isinstance(
            checkpoint,
            GovernedDurableMissionCheckpoint,
        ):
            raise TypeError(
                "checkpoint must be "
                "GovernedDurableMissionCheckpoint."
            )

        if not isinstance(
            verdict,
            GovernedMissionVerdict,
        ):
            raise TypeError(
                "verdict must be "
                "GovernedMissionVerdict."
            )

        if verdict.plan_id != checkpoint.plan_id:
            raise ExperienceLearningPromotionInvariantError(
                "Mission verdict is not bound "
                "to checkpoint plan."
            )

        payload = checkpoint.payload

        durable_verdict = payload.get(
            "mission_verdict"
        )

        if not isinstance(
            durable_verdict,
            dict,
        ):
            raise ExperienceCaptureIncompleteError(
                "Durable mission checkpoint "
                "does not contain mission verdict."
            )

        if (
            durable_verdict.get(
                "verdict_id"
            )
            != verdict.verdict_id
        ):
            raise ExperienceLearningPromotionInvariantError(
                "Mission verdict does not match "
                "durable checkpoint verdict."
            )

        return ImmutableExperienceEvidence(
            checkpoint_id=(
                checkpoint.checkpoint_id
            ),
            checkpoint_payload_sha256=(
                checkpoint.payload_sha256
            ),
            mission_contract_id=(
                checkpoint.mission_contract_id
            ),
            plan_id=checkpoint.plan_id,
            routing_plan_id=(
                checkpoint.routing_plan_id
            ),
            mission_verdict_id=(
                verdict.verdict_id
            ),
            mission_verdict_state=(
                verdict.state
            ),
            outcome=outcome,
            verified_result_ref=(
                verified_result_ref
            ),
            failure_refs=tuple(
                failure_refs
            ),
            retry_evidence_refs=tuple(
                retry_evidence_refs
            ),
            routing_quality_score=(
                routing_quality_score
            ),
            resource_performance=tuple(
                resource_performance
            ),
            human_correction_refs=tuple(
                human_correction_refs
            ),
            evidence_refs=tuple(
                evidence_refs
            ),
            cost_units=cost_units,
            latency_ms=latency_ms,
        )

    @staticmethod
    def propose_learning(
        support: Iterable[
            ImmutableExperienceEvidence
        ],
        *,
        kind: LearningCandidateKind,
        key: str,
        statement: str,
        counter: Iterable[
            ImmutableExperienceEvidence
        ] = (),
    ) -> GovernedLearningCandidate:
        support_rows = tuple(
            support
        )

        counter_rows = tuple(
            counter
        )

        if not all(
            isinstance(
                item,
                ImmutableExperienceEvidence,
            )
            for item in (
                *support_rows,
                *counter_rows,
            )
        ):
            raise TypeError(
                "Learning support/counter rows "
                "must contain "
                "ImmutableExperienceEvidence."
            )

        if len(support_rows) < 2:
            raise LearningCandidateIncompleteError(
                "At least two immutable "
                "experiences are required."
            )

        support_ids = tuple(
            item.experience_id
            for item in support_rows
        )

        counter_ids = tuple(
            item.experience_id
            for item in counter_rows
        )

        if len(support_ids) != len(
            set(support_ids)
        ):
            raise LearningCandidateIncompleteError(
                "Supporting experiences "
                "must be distinct."
            )

        if len(counter_ids) != len(
            set(counter_ids)
        ):
            raise LearningCandidateIncompleteError(
                "Counter experiences "
                "must be distinct."
            )

        digests = tuple(
            item.experience_sha256
            for item in (
                *support_rows,
                *counter_rows,
            )
        )

        return GovernedLearningCandidate(
            kind=kind,
            key=key,
            statement=statement,
            support_experience_ids=(
                support_ids
            ),
            counter_experience_ids=(
                counter_ids
            ),
            source_experience_sha256=(
                digests
            ),
        )

    @staticmethod
    def evaluate_promotion(
        candidate: GovernedLearningCandidate,
        evidence: PromotionEvaluationEvidence,
        policy: PromotionPolicy,
    ) -> GovernedPromotionDecision:
        if not isinstance(
            candidate,
            GovernedLearningCandidate,
        ):
            raise TypeError(
                "candidate must be "
                "GovernedLearningCandidate."
            )

        if not isinstance(
            evidence,
            PromotionEvaluationEvidence,
        ):
            raise TypeError(
                "evidence must be "
                "PromotionEvaluationEvidence."
            )

        if not isinstance(
            policy,
            PromotionPolicy,
        ):
            raise TypeError(
                "policy must be "
                "PromotionPolicy."
            )

        if (
            evidence.candidate_id
            != candidate.candidate_id
        ):
            raise ExperienceLearningPromotionInvariantError(
                "Promotion evidence is not "
                "bound to learning candidate."
            )

        reasons: list[str] = []

        if (
            evidence.ay_validation
            is EvidenceState.FAIL
            or evidence.ex_authorization
            is EvidenceState.FAIL
        ):
            state = (
                PromotionDecisionState
                .REJECTED
            )

            reasons.append(
                "Explicit AY or EX promotion "
                "gate failure."
            )

        elif (
            evidence.ay_validation
            is EvidenceState.UNKNOWN
            or evidence.ex_authorization
            is EvidenceState.UNKNOWN
        ):
            state = (
                PromotionDecisionState.UNKNOWN
            )

            reasons.append(
                "AY or EX promotion evidence "
                "is unknown."
            )

        elif (
            len(
                candidate
                .support_experience_ids
            )
            < policy.min_support
        ):
            state = (
                PromotionDecisionState.REJECTED
            )

            reasons.append(
                "Insufficient immutable "
                "experience support."
            )

        elif (
            evidence.samples
            < policy.min_samples
        ):
            state = (
                PromotionDecisionState.REJECTED
            )

            reasons.append(
                "Insufficient evaluation samples."
            )

        elif (
            evidence.replay_score
            < policy.min_replay_score
        ):
            state = (
                PromotionDecisionState.REJECTED
            )

            reasons.append(
                "Replay score below threshold."
            )

        elif (
            evidence.shadow_success_rate
            < policy.min_shadow_success_rate
        ):
            state = (
                PromotionDecisionState.REJECTED
            )

            reasons.append(
                "Shadow success rate "
                "below threshold."
            )

        elif (
            evidence.regression_count
            > policy.max_regressions
        ):
            state = (
                PromotionDecisionState.REJECTED
            )

            reasons.append(
                "Regression count exceeds "
                "promotion policy."
            )

        elif (
            evidence.candidate_score
            - evidence.baseline_score
            < policy.min_improvement
        ):
            state = (
                PromotionDecisionState.REJECTED
            )

            reasons.append(
                "Candidate does not improve "
                "over explicit baseline."
            )

        else:
            state = (
                PromotionDecisionState
                .PROMOTION_ELIGIBLE
            )

            reasons.append(
                "Candidate passed support, "
                "comparison, replay, shadow, "
                "regression, rollback, AY and "
                "EX promotion evidence."
            )

        return GovernedPromotionDecision(
            candidate_id=(
                candidate.candidate_id
            ),
            evaluation_id=(
                evidence.evaluation_id
            ),
            state=state,
            reasons=tuple(reasons),
            comparison_ref=(
                evidence.comparison_ref
            ),
            rollback_ref=(
                evidence.rollback_ref
            ),
        )


__all__ = [
    "GOVERNED_EXPERIENCE_LEARNING_PROMOTION_VERSION",
    "ExperienceLearningPromotionInvariantError",
    "ExperienceCaptureIncompleteError",
    "LearningCandidateIncompleteError",
    "PromotionEvaluationIncompleteError",
    "ExperienceOutcome",
    "EvidenceState",
    "LearningCandidateKind",
    "PromotionDecisionState",
    "ResourcePerformanceEvidence",
    "ImmutableExperienceEvidence",
    "GovernedLearningCandidate",
    "PromotionPolicy",
    "PromotionEvaluationEvidence",
    "GovernedPromotionDecision",
    "GovernedExperienceLearningPromotion",
]
