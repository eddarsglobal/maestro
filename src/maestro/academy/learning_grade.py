from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any, Callable

from maestro.sovereign import (
    IntelligenceCapability,
    IntelligenceRequest,
)

from .models import AcademyScenario, PolicyVariant, ScenarioResult


ResourceResolver = Callable[[PolicyVariant], str]


def _integer_tokens(text: str) -> list[int]:
    return [
        int(value)
        for value in re.findall(
            r"(?<![\w.])-?\d+(?![\w.])",
            text,
        )
    ]


def semantic_accepts(
    output: str,
    expected: str,
    scenario: AcademyScenario,
) -> bool:
    text = output.strip()
    validator = str(
        scenario.metadata.get("validator") or "exact"
    )

    if validator == "exact":
        return text == expected

    if validator == "contains":
        return expected in text

    if validator == "integer":
        try:
            target = int(expected)
        except ValueError:
            return False
        return target in _integer_tokens(text)

    if validator == "ordered_integers":
        try:
            target = [
                int(value)
                for value in expected.split(",")
            ]
        except ValueError:
            return False

        actual = _integer_tokens(text)
        width = len(target)

        return any(
            actual[index:index + width] == target
            for index in range(
                0,
                max(0, len(actual) - width + 1),
            )
        )

    if validator == "json_object":
        value = text

        if value.startswith("```") and value.endswith("```"):
            lines = value.splitlines()
            if len(lines) >= 3:
                value = "\n".join(lines[1:-1]).strip()

        try:
            return json.loads(value) == json.loads(expected)
        except Exception:
            return False

    if validator == "binary_token":
        wanted = expected.upper()
        opposite = "NON" if wanted == "OUI" else "OUI"
        tokens = re.findall(
            r"\b(?:OUI|NON)\b",
            text.upper(),
        )
        return wanted in tokens and opposite not in tokens

    if validator == "endswith_word":
        return bool(
            re.search(
                rf"\b{re.escape(expected)}\b"
                r"[\s.!?`'\"\)]*$",
                text,
                flags=re.IGNORECASE,
            )
        )

    raise ValueError(
        f"Unsupported semantic validator: {validator}"
    )


def format_accepts(
    output: str,
    expected: str,
    scenario: AcademyScenario,
) -> bool:
    mode = str(
        scenario.metadata.get("format_mode") or "exact"
    )

    if mode == "exact":
        return output.strip() == expected

    raise ValueError(
        f"Unsupported format mode: {mode}"
    )


@dataclass(frozen=True)
class LearningGradeExecution:
    scenario_id: str
    policy_id: str
    resource_id: str
    expected: str
    output: str
    semantic_pass: bool
    format_pass: bool
    execution_profile_ref: str | None
    profile_ref_verified: bool
    deterministic_execution: bool
    latency_ms: float
    error: str | None = None

    @property
    def success(self) -> bool:
        return bool(
            self.semantic_pass
            and self.format_pass
            and self.profile_ref_verified
            and self.deterministic_execution
            and self.error is None
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "scenario_id": self.scenario_id,
            "policy_id": self.policy_id,
            "resource_id": self.resource_id,
            "expected": self.expected,
            "output": self.output,
            "semantic_pass": self.semantic_pass,
            "format_pass": self.format_pass,
            "execution_profile_ref": self.execution_profile_ref,
            "profile_ref_verified": self.profile_ref_verified,
            "deterministic_execution": self.deterministic_execution,
            "latency_ms": self.latency_ms,
            "error": self.error,
            "success": self.success,
        }


class LearningGradeAcademyRunner:
    """
    Native Academy runner for learning-grade model evaluation.

    The runner:
    - binds the OGA evaluation profile to the actual sovereign request;
    - verifies the execution profile returned by the adapter;
    - measures semantic correctness separately from format compliance;
    - exposes a normal Academy ScenarioResult;
    - caches identical resource/scenario/profile executions.
    """

    def __init__(
        self,
        registry,
        evaluation_profile,
        resource_resolver: ResourceResolver,
        *,
        capability: IntelligenceCapability = (
            IntelligenceCapability.DIRECT
        ),
    ):
        if not getattr(
            evaluation_profile,
            "learning_eligible",
            False,
        ):
            raise ValueError(
                "LearningGradeAcademyRunner requires a "
                "learning-eligible evaluation profile."
            )

        self.registry = registry
        self.evaluation_profile = evaluation_profile
        self.resource_resolver = resource_resolver
        self.capability = capability
        self.execution_profile = (
            evaluation_profile.to_execution_profile()
        )
        self._cache: dict[
            tuple[str, str, str],
            LearningGradeExecution,
        ] = {}

    @property
    def profile_id(self) -> str:
        return str(self.evaluation_profile.profile_id)

    def evidence(
        self,
        resource_id: str,
        scenario_id: str,
    ) -> LearningGradeExecution | None:
        return self._cache.get(
            (
                resource_id,
                scenario_id,
                self.profile_id,
            )
        )

    def all_evidence(self) -> list[LearningGradeExecution]:
        return list(self._cache.values())

    def _scenario_result(
        self,
        policy_id: str,
        evidence: LearningGradeExecution,
        *,
        cached: bool,
    ) -> ScenarioResult:
        gates = set()

        if (
            evidence.profile_ref_verified
            and evidence.deterministic_execution
        ):
            gates.add("DETERMINISTIC_EXECUTION")

        if evidence.semantic_pass:
            gates.add("SEMANTIC_VALIDATION")

        if evidence.format_pass:
            gates.add("FORMAT_VALIDATION")

        if evidence.success:
            gates.add("LEARNING_GRADE_EVIDENCE")

        notes = [
            (
                "profile_ref_verified="
                + ("PASS" if evidence.profile_ref_verified else "FAIL")
            ),
            (
                "deterministic_execution="
                + ("PASS" if evidence.deterministic_execution else "FAIL")
            ),
            (
                "semantic="
                + ("PASS" if evidence.semantic_pass else "FAIL")
            ),
            (
                "format="
                + ("PASS" if evidence.format_pass else "FAIL")
            ),
        ]

        if evidence.error:
            notes.append(evidence.error)

        if not evidence.success:
            notes.append(
                f"expected={evidence.expected!r} "
                f"actual={evidence.output!r}"
            )

        if cached:
            notes.append(
                "reused identical resource/scenario/profile execution"
            )

        return ScenarioResult(
            scenario_id=evidence.scenario_id,
            policy_id=policy_id,
            success=evidence.success,
            selected_councils={"AI"},
            gates_observed=gates,
            human_approval_requested=False,
            retries=0,
            latency_ms=evidence.latency_ms,
            cost_units=0.0,
            evidence_score=1.0 if evidence.success else 0.0,
            notes=notes,
        )

    def __call__(
        self,
        policy: PolicyVariant,
        scenario: AcademyScenario,
    ) -> ScenarioResult:
        resource_id = str(
            self.resource_resolver(policy)
        )

        key = (
            resource_id,
            scenario.scenario_id,
            self.profile_id,
        )

        cached = self._cache.get(key)

        if cached is not None:
            return self._scenario_result(
                policy.policy_id,
                cached,
                cached=True,
            )

        expected = str(
            scenario.metadata.get("expected") or ""
        )

        output = ""
        latency_ms = 0.0
        error = None
        semantic_pass = False
        format_pass = False
        profile_ref = None
        profile_ref_verified = False
        deterministic_execution = False

        try:
            request = IntelligenceRequest(
                task_id=(
                    "ACADEMY-LG-"
                    + scenario.scenario_id
                ),
                capability=self.capability,
                instruction=scenario.objective,
                max_tokens=int(
                    self.evaluation_profile.num_predict
                ),
                requires_tools=False,
                preferred_local=True,
                metadata={
                    "academy_learning_grade": True,
                    "scenario_id": scenario.scenario_id,
                    "evaluation_profile_id": self.profile_id,
                },
                execution_profile=self.execution_profile,
            )

            adapter = self.registry.adapter(resource_id)
            response = adapter.execute(request)

            output = response.output.strip()
            latency_ms = float(
                response.metadata.get("total_ms") or 0.0
            )

            profile_ref = response.metadata.get(
                "execution_profile_ref"
            )

            profile_ref_verified = (
                profile_ref == self.profile_id
            )

            deterministic_execution = bool(
                response.metadata.get(
                    "deterministic_execution"
                )
            )

            semantic_pass = bool(response.success) and (
                semantic_accepts(
                    output,
                    expected,
                    scenario,
                )
            )

            format_pass = bool(response.success) and (
                format_accepts(
                    output,
                    expected,
                    scenario,
                )
            )

        except Exception as exc:
            error = (
                f"{type(exc).__name__}: {exc}"
            )

        evidence = LearningGradeExecution(
            scenario_id=scenario.scenario_id,
            policy_id=policy.policy_id,
            resource_id=resource_id,
            expected=expected,
            output=output,
            semantic_pass=semantic_pass,
            format_pass=format_pass,
            execution_profile_ref=profile_ref,
            profile_ref_verified=profile_ref_verified,
            deterministic_execution=deterministic_execution,
            latency_ms=latency_ms,
            error=error,
        )

        self._cache[key] = evidence

        return self._scenario_result(
            policy.policy_id,
            evidence,
            cached=False,
        )
