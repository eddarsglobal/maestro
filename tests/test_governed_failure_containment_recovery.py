from __future__ import annotations

import ast
import unittest

from dataclasses import replace
from pathlib import Path

from maestro.governance.governed_failure_containment_recovery import (
    ContainmentState,
    EvidenceState as E,
    FailureRecoveryEvidence,
    FailureState,
    GovernedFailureContainment,
    GovernedRecoveryInvariantError,
    RecoveryAssessmentState,
    RecoveryPlanAction,
    RecoveryPlanStep,
    RecoveryPreservationEvidence,
    UpdateRecoveryContext,
)


SOURCE = Path(
    "src/maestro/governance/"
    "governed_failure_containment_recovery.py"
)

DOC = Path(
    "docs/"
    "GOVERNED_FAILURE_CONTAINMENT_RECOVERY_CONSTITUTION.md"
)


def context(
    *,
    subject="UPDATE-001",
    generation="GEN-2",
    current="STATE-CURRENT",
    baseline="STATE-LKG",
    requirements=("identity",),
):
    return UpdateRecoveryContext(
        subject_id=subject,
        update_generation_id=generation,
        current_state_id=current,
        last_known_good_state_id=baseline,
        preservation_requirements=tuple(
            requirements
        ),
    )


def evidence(
    ctx,
    *,
    failure=FailureState.DETECTED,
    integrity=E.PASS,
    containment_capability=E.PASS,
    containment_state=ContainmentState.CONTAINED,
    rollback_path=E.PASS,
    recovery_path=E.PASS,
    rollback_preservation=E.PASS,
    recovery_preservation=E.PASS,
    requirements=None,
):
    rows = (
        tuple(requirements)
        if requirements is not None
        else ctx.preservation_requirements
    )

    return FailureRecoveryEvidence(
        context_id=ctx.context_id,
        failure_state=failure,
        current_state_integrity=integrity,
        containment_capability=containment_capability,
        containment_state=containment_state,
        rollback_path_available=rollback_path,
        recovery_path_available=recovery_path,
        preservation=tuple(
            RecoveryPreservationEvidence(
                requirement_id=item,
                rollback_state=rollback_preservation,
                recovery_state=recovery_preservation,
            )
            for item in rows
        ),
        evidence_source_ref="test://fcr",
    )


def assess(
    ctx,
    **kwargs,
):
    return GovernedFailureContainment.assess(
        ctx,
        evidence(
            ctx,
            **kwargs,
        ),
    )


class GovernedFailureContainmentRecoveryTests(
    unittest.TestCase
):
    def test_01_constitution_contains_laws_and_separations(self):
        text = DOC.read_text(
            encoding="utf-8"
        )

        for number in range(1, 11):
            self.assertIn(
                f"FCR-{number:02d}",
                text,
            )

        for invariant in (
            "FAILURE DETECTED != RECOVERY AUTHORIZED",
            "RECOVERY POSSIBLE != RECOVERY AUTHORIZED",
            "ROLLBACK POSSIBLE != ROLLBACK AUTHORIZED",
            "ROLLBACK PLAN != ROLLBACK EXECUTION",
            "RECOVERY PLAN != RECOVERY EXECUTION",
            "CONTAINMENT != DELETION",
            "FAILED UPDATE != CORRUPTED USER STATE",
            "RECOVERY SUCCESS != ACTIVATION AUTHORIZED",
            "ROLLBACK SUCCESS != RELEASE AUTHORIZED",
            "RECOVERY EVIDENCE != SYSTEM TRUTH",
            "SOURCE STATE != RECOVERY COPY",
            "BMF-028 != BMF-027",
        ):
            self.assertIn(
                invariant,
                text,
            )

    def test_02_healthy_requires_no_failure_and_integrity_pass(self):
        ctx = context()

        result = assess(
            ctx,
            failure=FailureState.NOT_DETECTED,
            integrity=E.PASS,
            containment_state=(
                ContainmentState.NOT_CONTAINED
            ),
            rollback_path=E.UNKNOWN,
            recovery_path=E.UNKNOWN,
        )

        self.assertIs(
            result.state,
            RecoveryAssessmentState.HEALTHY,
        )

        unknown = assess(
            ctx,
            failure=FailureState.UNKNOWN,
            integrity=E.PASS,
            containment_state=(
                ContainmentState.UNKNOWN
            ),
        )

        self.assertIs(
            unknown.state,
            RecoveryAssessmentState.UNKNOWN,
        )

    def test_03_detected_uncontained_failure_requires_containment(self):
        ctx = context()

        result = assess(
            ctx,
            containment_capability=E.PASS,
            containment_state=(
                ContainmentState.NOT_CONTAINED
            ),
        )

        self.assertIs(
            result.state,
            RecoveryAssessmentState.CONTAINMENT_REQUIRED,
        )

        plan = (
            GovernedFailureContainment
            .plan_containment(
                result,
                (
                    RecoveryPlanStep(
                        1,
                        "CONTAIN-1",
                        "Isolate the failed update.",
                    ),
                ),
            )
        )

        self.assertIs(
            plan.action,
            RecoveryPlanAction.CONTAINMENT,
        )

        self.assertFalse(
            plan.containment_executed
        )

    def test_04_contained_failure_with_intact_state_requires_rollback(self):
        ctx = context()

        result = assess(
            ctx,
            integrity=E.PASS,
            containment_state=(
                ContainmentState.CONTAINED
            ),
            rollback_path=E.PASS,
            rollback_preservation=E.PASS,
        )

        self.assertIs(
            result.state,
            RecoveryAssessmentState.ROLLBACK_REQUIRED,
        )

        plan = (
            GovernedFailureContainment
            .plan_rollback(
                result,
                (
                    RecoveryPlanStep(
                        1,
                        "ROLLBACK-1",
                        "Prepare governed rollback.",
                    ),
                ),
            )
        )

        self.assertEqual(
            plan.baseline_state_id,
            ctx.last_known_good_state_id,
        )

        self.assertFalse(
            plan.rollback_authorized
        )
        self.assertFalse(
            plan.rollback_executed
        )

    def test_05_explicit_state_integrity_failure_requires_recovery(self):
        ctx = context()

        result = assess(
            ctx,
            integrity=E.FAIL,
            containment_state=(
                ContainmentState.CONTAINED
            ),
            recovery_path=E.PASS,
            recovery_preservation=E.PASS,
        )

        self.assertIs(
            result.state,
            RecoveryAssessmentState.RECOVERY_REQUIRED,
        )

        plan = (
            GovernedFailureContainment
            .plan_recovery(
                result,
                (
                    RecoveryPlanStep(
                        1,
                        "RECOVERY-1",
                        "Prepare recovery copy.",
                    ),
                ),
            )
        )

        self.assertEqual(
            plan.baseline_state_id,
            ctx.last_known_good_state_id,
        )

        self.assertFalse(
            plan.recovery_authorized
        )
        self.assertFalse(
            plan.recovery_executed
        )

    def test_06_unknown_and_unrecoverable_fail_closed(self):
        ctx = context()

        unknown = assess(
            ctx,
            containment_state=(
                ContainmentState.CONTAINED
            ),
            rollback_path=E.UNKNOWN,
        )

        self.assertIs(
            unknown.state,
            RecoveryAssessmentState.UNKNOWN,
        )

        unrecoverable = assess(
            ctx,
            integrity=E.FAIL,
            containment_state=(
                ContainmentState.CONTAINED
            ),
            recovery_path=E.FAIL,
            recovery_preservation=E.FAIL,
        )

        self.assertIs(
            unrecoverable.state,
            RecoveryAssessmentState.UNRECOVERABLE,
        )

    def test_07_context_binding_and_preservation_coverage_fail_closed(self):
        ctx = context(
            requirements=(
                "history",
                "identity",
            ),
        )

        row = evidence(
            ctx,
        )

        other = context(
            subject="UPDATE-OTHER",
            requirements=(
                "history",
                "identity",
            ),
        )

        with self.assertRaises(
            GovernedRecoveryInvariantError
        ):
            GovernedFailureContainment.assess(
                other,
                row,
            )

        incomplete = evidence(
            ctx,
            requirements=("identity",),
        )

        with self.assertRaises(
            GovernedRecoveryInvariantError
        ):
            GovernedFailureContainment.assess(
                ctx,
                incomplete,
            )

    def test_08_plans_require_matching_state_and_valid_steps(self):
        ctx = context()

        healthy = assess(
            ctx,
            failure=FailureState.NOT_DETECTED,
            integrity=E.PASS,
            containment_state=(
                ContainmentState.NOT_CONTAINED
            ),
        )

        step = RecoveryPlanStep(
            1,
            "STEP-1",
            "Passive plan step.",
        )

        with self.assertRaises(
            GovernedRecoveryInvariantError
        ):
            GovernedFailureContainment.plan_rollback(
                healthy,
                (step,),
            )

        rollback = assess(
            ctx,
            containment_state=(
                ContainmentState.CONTAINED
            ),
            rollback_path=E.PASS,
            rollback_preservation=E.PASS,
        )

        with self.assertRaises(
            GovernedRecoveryInvariantError
        ):
            GovernedFailureContainment.plan_rollback(
                rollback,
                (
                    RecoveryPlanStep(
                        2,
                        "STEP-2",
                        "Invalid order.",
                    ),
                ),
            )

        with self.assertRaises(
            GovernedRecoveryInvariantError
        ):
            GovernedFailureContainment.plan_rollback(
                rollback,
                (
                    RecoveryPlanStep(
                        1,
                        "DUP",
                        "First.",
                    ),
                    RecoveryPlanStep(
                        2,
                        "DUP",
                        "Second.",
                    ),
                ),
            )

    def test_09_determinism_and_authority_escalation_fail_closed(self):
        ctx_a = context(
            requirements=(
                "history",
                "identity",
            ),
        )

        ctx_b = context(
            requirements=(
                "identity",
                "history",
            ),
        )

        self.assertEqual(
            ctx_a.context_id,
            ctx_b.context_id,
        )

        evidence_a = evidence(
            ctx_a,
            requirements=(
                "history",
                "identity",
            ),
        )

        evidence_b = evidence(
            ctx_b,
            requirements=(
                "identity",
                "history",
            ),
        )

        a = GovernedFailureContainment.assess(
            ctx_a,
            evidence_a,
        )

        b = GovernedFailureContainment.assess(
            ctx_b,
            evidence_b,
        )

        self.assertEqual(
            evidence_a.evidence_id,
            evidence_b.evidence_id,
        )

        self.assertEqual(
            a.assessment_id,
            b.assessment_id,
        )

        plan = (
            GovernedFailureContainment
            .plan_rollback(
                a,
                (
                    RecoveryPlanStep(
                        1,
                        "ROLLBACK-1",
                        "Passive rollback plan.",
                    ),
                ),
            )
        )

        fields = (
            "containment_authorized",
            "containment_executed",
            "rollback_authorized",
            "rollback_executed",
            "recovery_authorized",
            "recovery_executed",
            "activation_authorized",
            "release_authorized",
            "source_state_mutation_requested",
            "source_state_deletion_requested",
            "system_truth_asserted",
        )

        for value in (
            a,
            plan,
        ):
            for field_name in fields:
                with self.subTest(
                    object=type(value).__name__,
                    field=field_name,
                ):
                    with self.assertRaises(
                        GovernedRecoveryInvariantError
                    ):
                        replace(
                            value,
                            **{
                                field_name: True
                            },
                        )

    def test_10_module_is_passive_and_existing_execution_is_not_dependency(self):
        tree = ast.parse(
            SOURCE.read_text(
                encoding="utf-8"
            )
        )

        imports = set()
        calls = set()

        for node in ast.walk(tree):
            if isinstance(
                node,
                ast.Import,
            ):
                imports.update(
                    alias.name
                    for alias in node.names
                )

            elif isinstance(
                node,
                ast.ImportFrom,
            ):
                if node.module:
                    imports.add(
                        node.module
                    )

            elif isinstance(
                node,
                ast.Call,
            ):
                if isinstance(
                    node.func,
                    ast.Name,
                ):
                    calls.add(
                        node.func.id
                    )

                elif isinstance(
                    node.func,
                    ast.Attribute,
                ):
                    calls.add(
                        node.func.attr
                    )

        forbidden_imports = {
            name
            for name in imports
            if (
                name.startswith(
                    "maestro.governed_activation"
                )
                or name.startswith(
                    "maestro.autonomous.recovery"
                )
                or name.startswith(
                    "maestro.fabric.recovery"
                )
                or name.startswith(
                    "subprocess"
                )
                or name.startswith(
                    "socket"
                )
                or name.startswith(
                    "sqlite3"
                )
                or name.startswith(
                    "requests"
                )
                or name.startswith(
                    "httpx"
                )
            )
        }

        self.assertEqual(
            forbidden_imports,
            set(),
        )

        forbidden_calls = {
            "execute",
            "executemany",
            "commit",
            "rollback",
            "recover",
            "restore",
            "activate",
            "authorize",
            "install",
            "unlink",
            "remove",
            "rename",
            "write_text",
            "write_bytes",
        }

        self.assertEqual(
            calls & forbidden_calls,
            set(),
        )

        constitution = DOC.read_text(
            encoding="utf-8"
        )

        self.assertIn(
            "BMF-028 != BMF-027",
            constitution,
        )


if __name__ == "__main__":
    unittest.main()
