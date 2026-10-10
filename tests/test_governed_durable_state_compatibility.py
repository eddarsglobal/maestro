from __future__ import annotations

import ast
import unittest

from dataclasses import replace
from pathlib import Path

from maestro.governance.governed_durable_state_compatibility import (
    CompatibilityEvidenceState as E,
    DirectionalCompatibilityState,
    DurableCompatibilityEvidence,
    DurableCompatibilityState,
    DurableStateDescriptor,
    GovernedDurableCompatibilityInvariantError,
    GovernedDurableStateCompatibility,
    MigrationPlanStep,
    PreservationEvidence,
)


DOC = Path(
    "docs/"
    "GOVERNED_DURABLE_STATE_COMPATIBILITY_CONSTITUTION.md"
)

SOURCE = Path(
    "src/maestro/governance/"
    "governed_durable_state_compatibility.py"
)


def descriptor(
    state_id="STATE-001",
    generation="GEN-A",
    *,
    application_version=None,
    schema_version=None,
    format_version=None,
    requirements=("identity",),
):
    return DurableStateDescriptor(
        durable_state_id=state_id,
        state_type="USER_DATA",
        generation_id=generation,
        application_version=(
            application_version
            if application_version is not None
            else generation
        ),
        schema_id="USER-DATA",
        schema_version=(
            schema_version
            if schema_version is not None
            else generation
        ),
        format_id="JSON",
        format_version=(
            format_version
            if format_version is not None
            else generation
        ),
        preservation_requirements=tuple(
            requirements
        ),
    )


def evidence(
    source,
    target,
    *,
    target_read=E.PASS,
    target_write=E.PASS,
    source_read=E.UNKNOWN,
    source_write=E.UNKNOWN,
    migration_path=E.UNKNOWN,
    rollback_path=E.UNKNOWN,
    direct_preservation=E.PASS,
    migration_preservation=E.UNKNOWN,
    requirements=None,
    source_ref="test://evidence",
):
    required = (
        tuple(requirements)
        if requirements is not None
        else tuple(
            sorted(
                set(
                    source.preservation_requirements
                )
                | set(
                    target.preservation_requirements
                )
            )
        )
    )

    return DurableCompatibilityEvidence(
        source_descriptor_id=(
            source.descriptor_id
        ),
        target_descriptor_id=(
            target.descriptor_id
        ),
        target_reads_source=target_read,
        target_writes_source=target_write,
        source_reads_target=source_read,
        source_writes_target=source_write,
        migration_path_available=(
            migration_path
        ),
        rollback_path_available=(
            rollback_path
        ),
        preservation=tuple(
            PreservationEvidence(
                requirement_id=item,
                direct_state=direct_preservation,
                migration_state=(
                    migration_preservation
                ),
            )
            for item in required
        ),
        evidence_source_ref=source_ref,
    )


def assess(
    source,
    target,
    **kwargs,
):
    return (
        GovernedDurableStateCompatibility
        .assess(
            source,
            target,
            evidence(
                source,
                target,
                **kwargs,
            ),
        )
    )


class GovernedDurableStateCompatibilityTests(
    unittest.TestCase
):
    def test_01_constitution_contains_laws_and_separations(self):
        text = DOC.read_text(
            encoding="utf-8"
        )

        for number in range(1, 11):
            self.assertIn(
                f"DCM-{number:02d}",
                text,
            )

        for invariant in (
            "VERSION CHANGE != MIGRATION REQUIRED",
            "COMPATIBLE != IDENTICAL",
            "READABLE != WRITABLE",
            "MIGRATION POSSIBLE != MIGRATION AUTHORIZED",
            "MIGRATION PLAN != MIGRATION EXECUTION",
            "USER STATE != CORE STATE",
            "STATE TRANSFORMATION != STATE LOSS",
            "UNKNOWN COMPATIBILITY != COMPATIBLE",
            "FORWARD COMPATIBLE != BACKWARD COMPATIBLE",
            "MIGRATION SUCCESS != ACTIVATION AUTHORIZED",
            "SCHEMA VERSION != APPLICATION VERSION",
            "ROLLBACK POSSIBLE != ROLLBACK AUTHORIZED",
        ):
            self.assertIn(
                invariant,
                text,
            )

        self.assertIn(
            "BMF-027 != BMF-028",
            text,
        )

    def test_02_version_changes_do_not_require_migration(self):
        source = descriptor(
            generation="GEN-A",
            application_version="9999",
            schema_version="900",
            format_version="700",
        )

        target = descriptor(
            generation="GEN-B",
            application_version="1",
            schema_version="1",
            format_version="1",
        )

        result = assess(
            source,
            target,
            target_read=E.PASS,
            target_write=E.PASS,
            source_read=E.FAIL,
            source_write=E.FAIL,
        )

        self.assertIs(
            result.state,
            DurableCompatibilityState.COMPATIBLE,
        )

        self.assertIs(
            result.backward_state,
            DirectionalCompatibilityState.COMPATIBLE,
        )

        self.assertIs(
            result.forward_state,
            DirectionalCompatibilityState.INCOMPATIBLE,
        )

        self.assertNotEqual(
            source.application_version,
            target.application_version,
        )

        self.assertNotEqual(
            source.schema_version,
            target.schema_version,
        )

    def test_03_read_write_direction_and_migration_required_are_distinct(self):
        source = descriptor(
            state_id="STATE-M",
            generation="A",
        )

        target = descriptor(
            state_id="STATE-M",
            generation="B",
        )

        result = assess(
            source,
            target,
            target_read=E.PASS,
            target_write=E.FAIL,
            source_read=E.FAIL,
            source_write=E.FAIL,
            migration_path=E.PASS,
            rollback_path=E.PASS,
            direct_preservation=E.PASS,
            migration_preservation=E.PASS,
        )

        self.assertIs(
            result.backward_state,
            DirectionalCompatibilityState.INCOMPATIBLE,
        )

        self.assertIs(
            result.state,
            DurableCompatibilityState.MIGRATION_REQUIRED,
        )

        self.assertFalse(
            result.migration_authorized
        )

        self.assertFalse(
            result.migration_executed
        )

    def test_04_unknown_direct_compatibility_remains_unknown(self):
        source = descriptor(
            state_id="STATE-U",
            generation="A",
        )

        target = descriptor(
            state_id="STATE-U",
            generation="B",
        )

        result = assess(
            source,
            target,
            target_read=E.UNKNOWN,
            target_write=E.PASS,
            migration_path=E.PASS,
            rollback_path=E.PASS,
            direct_preservation=E.PASS,
            migration_preservation=E.PASS,
        )

        self.assertIs(
            result.state,
            DurableCompatibilityState.UNKNOWN,
        )

        self.assertNotEqual(
            result.state,
            DurableCompatibilityState.MIGRATION_REQUIRED,
        )

    def test_05_migration_preservation_fail_and_unknown_fail_closed(self):
        source = descriptor(
            state_id="STATE-P",
            generation="A",
        )

        target = descriptor(
            state_id="STATE-P",
            generation="B",
        )

        failed = assess(
            source,
            target,
            target_read=E.FAIL,
            target_write=E.FAIL,
            migration_path=E.PASS,
            direct_preservation=E.FAIL,
            migration_preservation=E.FAIL,
        )

        unknown = assess(
            source,
            target,
            target_read=E.FAIL,
            target_write=E.FAIL,
            migration_path=E.PASS,
            direct_preservation=E.FAIL,
            migration_preservation=E.UNKNOWN,
        )

        self.assertIs(
            failed.state,
            DurableCompatibilityState.INCOMPATIBLE,
        )

        self.assertIn(
            "migration preservation failed",
            failed.reasons,
        )

        self.assertIs(
            unknown.state,
            DurableCompatibilityState.UNKNOWN,
        )

        self.assertIn(
            "migration preservation unknown",
            unknown.reasons,
        )

    def test_06_lineage_and_preservation_coverage_fail_closed(self):
        source = descriptor(
            state_id="STATE-L",
            generation="A",
        )

        target = descriptor(
            state_id="STATE-L",
            generation="B",
        )

        row = evidence(
            source,
            target,
        )

        other_source = descriptor(
            state_id="STATE-L",
            generation="X",
        )

        with self.assertRaises(
            GovernedDurableCompatibilityInvariantError
        ):
            GovernedDurableStateCompatibility.assess(
                other_source,
                target,
                row,
            )

        expanded_target = descriptor(
            state_id="STATE-L",
            generation="B",
            requirements=(
                "identity",
                "history",
            ),
        )

        incomplete = DurableCompatibilityEvidence(
            source_descriptor_id=(
                source.descriptor_id
            ),
            target_descriptor_id=(
                expanded_target.descriptor_id
            ),
            target_reads_source=E.PASS,
            target_writes_source=E.PASS,
            source_reads_target=E.UNKNOWN,
            source_writes_target=E.UNKNOWN,
            migration_path_available=E.UNKNOWN,
            rollback_path_available=E.UNKNOWN,
            preservation=(
                PreservationEvidence(
                    "identity",
                    E.PASS,
                    E.UNKNOWN,
                ),
            ),
            evidence_source_ref=(
                "test://incomplete"
            ),
        )

        with self.assertRaises(
            GovernedDurableCompatibilityInvariantError
        ):
            GovernedDurableStateCompatibility.assess(
                source,
                expanded_target,
                incomplete,
            )

    def test_07_migration_plan_requires_migration_required_and_valid_steps(self):
        source = descriptor(
            state_id="STATE-PLAN",
            generation="A",
        )

        target = descriptor(
            state_id="STATE-PLAN",
            generation="B",
        )

        compatible = assess(
            source,
            target,
        )

        migration = assess(
            source,
            target,
            target_read=E.PASS,
            target_write=E.FAIL,
            migration_path=E.PASS,
            rollback_path=E.PASS,
            direct_preservation=E.PASS,
            migration_preservation=E.PASS,
        )

        with self.assertRaises(
            GovernedDurableCompatibilityInvariantError
        ):
            GovernedDurableStateCompatibility.plan(
                compatible,
                (
                    MigrationPlanStep(
                        1,
                        "STEP-1",
                        "No migration needed.",
                    ),
                ),
            )

        with self.assertRaises(
            GovernedDurableCompatibilityInvariantError
        ):
            GovernedDurableStateCompatibility.plan(
                migration,
                (
                    MigrationPlanStep(
                        2,
                        "STEP-2",
                        "Invalid first ordinal.",
                    ),
                ),
            )

        with self.assertRaises(
            GovernedDurableCompatibilityInvariantError
        ):
            GovernedDurableStateCompatibility.plan(
                migration,
                (
                    MigrationPlanStep(
                        1,
                        "STEP-DUP",
                        "First.",
                    ),
                    MigrationPlanStep(
                        2,
                        "STEP-DUP",
                        "Second.",
                    ),
                ),
            )

        plan = (
            GovernedDurableStateCompatibility
            .plan(
                migration,
                (
                    MigrationPlanStep(
                        1,
                        "STEP-1",
                        "Create transformed copy.",
                    ),
                    MigrationPlanStep(
                        2,
                        "STEP-2",
                        "Validate preservation.",
                    ),
                ),
                rollback_reference=(
                    "ROLLBACK-EVIDENCE"
                ),
            )
        )

        self.assertFalse(
            plan.migration_authorized
        )
        self.assertFalse(
            plan.migration_executed
        )
        self.assertFalse(
            plan.rollback_authorized
        )

    def test_08_content_lineage_is_deterministic(self):
        source_a = descriptor(
            state_id="STATE-D",
            generation="A",
            requirements=(
                "history",
                "identity",
            ),
        )

        source_b = descriptor(
            state_id="STATE-D",
            generation="A",
            requirements=(
                "identity",
                "history",
            ),
        )

        target = descriptor(
            state_id="STATE-D",
            generation="B",
            requirements=(
                "identity",
                "history",
            ),
        )

        self.assertEqual(
            source_a.descriptor_id,
            source_b.descriptor_id,
        )

        evidence_a = DurableCompatibilityEvidence(
            source_a.descriptor_id,
            target.descriptor_id,
            E.PASS,
            E.PASS,
            E.FAIL,
            E.FAIL,
            E.UNKNOWN,
            E.PASS,
            (
                PreservationEvidence(
                    "history",
                    E.PASS,
                    E.UNKNOWN,
                ),
                PreservationEvidence(
                    "identity",
                    E.PASS,
                    E.UNKNOWN,
                ),
            ),
            "test://determinism",
        )

        evidence_b = DurableCompatibilityEvidence(
            source_b.descriptor_id,
            target.descriptor_id,
            E.PASS,
            E.PASS,
            E.FAIL,
            E.FAIL,
            E.UNKNOWN,
            E.PASS,
            (
                PreservationEvidence(
                    "identity",
                    E.PASS,
                    E.UNKNOWN,
                ),
                PreservationEvidence(
                    "history",
                    E.PASS,
                    E.UNKNOWN,
                ),
            ),
            "test://determinism",
        )

        a = (
            GovernedDurableStateCompatibility
            .assess(
                source_a,
                target,
                evidence_a,
            )
        )

        b = (
            GovernedDurableStateCompatibility
            .assess(
                source_b,
                target,
                evidence_b,
            )
        )

        self.assertEqual(
            evidence_a.evidence_id,
            evidence_b.evidence_id,
        )

        self.assertEqual(
            a.assessment_id,
            b.assessment_id,
        )

        self.assertEqual(
            a.to_dict(),
            b.to_dict(),
        )

    def test_09_authority_escalation_fails_closed(self):
        source = descriptor(
            state_id="STATE-AUTH",
            generation="A",
        )

        target = descriptor(
            state_id="STATE-AUTH",
            generation="B",
        )

        assessment = assess(
            source,
            target,
            target_read=E.PASS,
            target_write=E.FAIL,
            migration_path=E.PASS,
            rollback_path=E.PASS,
            direct_preservation=E.PASS,
            migration_preservation=E.PASS,
        )

        plan = (
            GovernedDurableStateCompatibility
            .plan(
                assessment,
                (
                    MigrationPlanStep(
                        1,
                        "STEP-1",
                        "Prepare transformed copy.",
                    ),
                ),
            )
        )

        fields = (
            "migration_authorized",
            "migration_executed",
            "activation_authorized",
            "rollback_authorized",
            "source_state_mutation_requested",
            "source_state_deletion_requested",
            "core_mutation_requested",
            "state_loss_accepted",
            "system_truth_asserted",
        )

        for target_object in (
            assessment,
            plan,
        ):
            for field_name in fields:
                with self.subTest(
                    object=type(
                        target_object
                    ).__name__,
                    field=field_name,
                ):
                    with self.assertRaises(
                        GovernedDurableCompatibilityInvariantError
                    ):
                        replace(
                            target_object,
                            **{
                                field_name: True
                            },
                        )

    def test_10_module_is_passive_and_bmf027_is_separate_from_recovery(self):
        text = SOURCE.read_text(
            encoding="utf-8"
        )

        tree = ast.parse(text)

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

        forbidden_import_roots = (
            "subprocess",
            "socket",
            "requests",
            "httpx",
            "aiohttp",
            "urllib",
            "sqlite3",
        )

        bad_imports = {
            name
            for name in imports
            if any(
                name == root
                or name.startswith(
                    root + "."
                )
                for root
                in forbidden_import_roots
            )
        }

        forbidden_calls = {
            "execute",
            "executemany",
            "commit",
            "rollback",
            "restore",
            "activate",
            "authorize",
            "install",
            "unlink",
            "remove",
            "rename",
            "replace",
            "write_text",
            "write_bytes",
        }

        self.assertEqual(
            bad_imports,
            set(),
        )

        self.assertEqual(
            calls & forbidden_calls,
            set(),
        )

        constitution = DOC.read_text(
            encoding="utf-8"
        )

        self.assertIn(
            "BMF-027 != BMF-028",
            constitution,
        )

        self.assertIn(
            "MIGRATION PLAN != RECOVERY EXECUTION",
            constitution,
        )


if __name__ == "__main__":
    unittest.main()
