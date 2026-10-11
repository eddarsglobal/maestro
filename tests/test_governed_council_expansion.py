from __future__ import annotations

import ast
import unittest

from dataclasses import replace
from pathlib import Path

from maestro.councils.capsules import (
    CapsuleStatus,
)
from maestro.councils.governed_council_expansion import (
    CouncilExpansionInvariantError,
    CouncilGapAbsentError,
    CouncilLifecycleEvidence,
    CouncilLifecycleEvidenceState as E,
    CouncilLifecycleState,
    GovernedCouncilExpansion,
)
from maestro.orchestration.governed_mission_foundation import (
    CapabilityRule,
    GovernedMissionFoundation,
    MissionContract,
)


SOURCE = Path(
    "src/maestro/councils/"
    "governed_council_expansion.py"
)

DOC = Path(
    "docs/"
    "GOVERNED_COUNCIL_EXPANSION_CONSTITUTION.md"
)


def demand():
    contract = MissionContract(
        objective=(
            "Develop a quantum "
            "verification capability"
        ),
        scope=(
            "Advanced verification"
        ),
        requested_output=(
            "Verified capability design"
        ),
        constraints=(
            "Preserve sovereignty",
        ),
        acceptance_criteria=(
            "Verification passes",
        ),
        authority_requirements=(
            "AY acceptance",
            "EX routing",
        ),
        evidence_obligations=(
            "Verification evidence",
        ),
    )

    result = (
        GovernedMissionFoundation
        .analyze(
            contract,
            (
                CapabilityRule(
                    "RULE-QV",
                    "QUANTUM_VERIFICATION",
                    (
                        "quantum",
                        "verification",
                    ),
                    "Mission requires "
                    "quantum verification.",
                ),
            ),
        )
    )

    return contract, result


def proposal():
    _, mission_demand = demand()

    gap = (
        GovernedCouncilExpansion
        .assess_gap(
            mission_demand,
            (),
        )
    )

    value = (
        GovernedCouncilExpansion
        .propose(
            gap,
            council_id="QV",
            name=(
                "Quantum Verification Council"
            ),
            primary_authority=(
                "quantum verification analysis"
            ),
            triggers=(
                "quantum verification",
            ),
            cannot_own=(
                "EX routing authority",
                "AY acceptance authority",
            ),
        )
    )

    return gap, value


class GovernedCouncilExpansionTests(
    unittest.TestCase
):
    def test_01_constitution_contains_laws(self):
        text = DOC.read_text(
            encoding="utf-8"
        )

        for number in range(
            1,
            11,
        ):
            self.assertIn(
                f"CEX-{number:02d}",
                text,
            )

        for invariant in (
            "MISSING CAPABILITY != COUNCIL AUTHORIZED",
            "GAP DETECTED != COUNCIL INSTALLED",
            "PROPOSAL != APPROVAL",
            "PROPOSAL != INSTALLATION",
            "PROPOSAL != ACTIVATION",
            "GENESIS COUNCIL != DYNAMIC COUNCIL",
            "CAPSULE CREATED != CAPSULE INSTALLED",
            "SHADOW != APPROVED",
            "EVALUATED != AUTHORIZED",
            "AY VALIDATED != EX AUTHORIZED",
            "EX AUTHORIZED != INSTALLED",
            "AUTONOMY != SELF-INSTALLATION",
            "INSTALL_ELIGIBLE != INSTALLED",
            "INSTALLED != ACTIVATED",
            "ACTIVATED != EXECUTION AUTHORIZED",
        ):
            self.assertIn(
                invariant,
                text,
            )

    def test_02_gap_is_exact_and_deterministic(self):
        _, mission_demand = demand()

        a = (
            GovernedCouncilExpansion
            .assess_gap(
                mission_demand,
                (),
            )
        )

        b = (
            GovernedCouncilExpansion
            .assess_gap(
                mission_demand,
                (),
            )
        )

        self.assertTrue(
            a.gap_present
        )

        self.assertEqual(
            a.missing_capabilities,
            (
                "QUANTUM_VERIFICATION",
            ),
        )

        self.assertEqual(
            a.gap_id,
            b.gap_id,
        )

    def test_03_complete_coverage_produces_no_gap_and_no_proposal(self):
        _, mission_demand = demand()

        gap = (
            GovernedCouncilExpansion
            .assess_gap(
                mission_demand,
                (
                    "QUANTUM_VERIFICATION",
                ),
            )
        )

        self.assertFalse(
            gap.gap_present
        )

        with self.assertRaises(
            CouncilGapAbsentError
        ):
            GovernedCouncilExpansion.propose(
                gap,
                council_id="QV",
                name="QV",
                primary_authority="verification",
                triggers=("quantum",),
                cannot_own=(
                    "EX routing authority",
                ),
            )

    def test_04_proposal_binds_gap_and_missing_capability(self):
        gap, value = proposal()

        self.assertEqual(
            value.gap_id,
            gap.gap_id,
        )

        self.assertEqual(
            value.demand_id,
            gap.demand_id,
        )

        self.assertEqual(
            value.capabilities,
            gap.missing_capabilities,
        )

        self.assertFalse(
            value.approved
        )
        self.assertFalse(
            value.installed
        )
        self.assertFalse(
            value.activated
        )

    def test_05_genesis_council_replacement_fails_closed(self):
        _, mission_demand = demand()

        gap = (
            GovernedCouncilExpansion
            .assess_gap(
                mission_demand,
                (),
            )
        )

        with self.assertRaises(
            CouncilExpansionInvariantError
        ):
            GovernedCouncilExpansion.propose(
                gap,
                council_id="EX",
                name="Fake EX",
                primary_authority="forbidden",
                triggers=("forbidden",),
                cannot_own=(
                    "system truth",
                ),
            )

    def test_06_proposal_projects_to_existing_capsule_format(self):
        _, value = proposal()

        manifest = value.to_manifest()

        self.assertEqual(
            manifest.council_id,
            "QV",
        )

        self.assertEqual(
            manifest.system_variable,
            "$conseil-qv",
        )

        self.assertEqual(
            manifest.status,
            CapsuleStatus.PROPOSED,
        )

        self.assertFalse(
            manifest.genesis
        )

        self.assertEqual(
            manifest.metadata[
                "proposal_id"
            ],
            value.proposal_id,
        )

    def test_07_lifecycle_progresses_through_governance_gates(self):
        _, value = proposal()

        cases = (
            (
                CapsuleStatus.PROPOSED,
                E.UNKNOWN,
                E.UNKNOWN,
                E.UNKNOWN,
                E.UNKNOWN,
                CouncilLifecycleState
                .SHADOW_REQUIRED,
            ),
            (
                CapsuleStatus.SHADOW,
                E.PASS,
                E.UNKNOWN,
                E.UNKNOWN,
                E.UNKNOWN,
                CouncilLifecycleState
                .AY_REQUIRED,
            ),
            (
                CapsuleStatus.SHADOW,
                E.PASS,
                E.PASS,
                E.UNKNOWN,
                E.UNKNOWN,
                CouncilLifecycleState
                .EX_REQUIRED,
            ),
            (
                CapsuleStatus.SHADOW,
                E.PASS,
                E.PASS,
                E.PASS,
                E.UNKNOWN,
                CouncilLifecycleState
                .HUMAN_APPROVAL_REQUIRED,
            ),
            (
                CapsuleStatus.SHADOW,
                E.PASS,
                E.PASS,
                E.PASS,
                E.PASS,
                CouncilLifecycleState
                .INSTALL_ELIGIBLE,
            ),
        )

        for (
            status,
            evaluation,
            ay,
            ex,
            human,
            expected,
        ) in cases:
            with self.subTest(
                expected=expected.value
            ):
                result = (
                    GovernedCouncilExpansion
                    .assess_lifecycle(
                        value,
                        CouncilLifecycleEvidence(
                            proposal_id=(
                                value.proposal_id
                            ),
                            capsule_status=status,
                            evaluation=evaluation,
                            ay_validation=ay,
                            ex_authorization=ex,
                            human_approval=human,
                            evidence_source_ref=(
                                "test://lifecycle"
                            ),
                        ),
                    )
                )

                self.assertIs(
                    result.state,
                    expected,
                )

    def test_08_failed_and_unknown_evidence_fail_closed(self):
        _, value = proposal()

        failed = (
            GovernedCouncilExpansion
            .assess_lifecycle(
                value,
                CouncilLifecycleEvidence(
                    value.proposal_id,
                    CapsuleStatus.SHADOW,
                    E.FAIL,
                    E.PASS,
                    E.PASS,
                    E.PASS,
                    "test://failed",
                ),
            )
        )

        unknown = (
            GovernedCouncilExpansion
            .assess_lifecycle(
                value,
                CouncilLifecycleEvidence(
                    value.proposal_id,
                    CapsuleStatus.SHADOW,
                    E.UNKNOWN,
                    E.PASS,
                    E.PASS,
                    E.PASS,
                    "test://unknown",
                ),
            )
        )

        self.assertIs(
            failed.state,
            CouncilLifecycleState.REJECTED,
        )

        self.assertIs(
            unknown.state,
            CouncilLifecycleState.UNKNOWN,
        )

        self.assertFalse(
            failed.install_eligible
        )
        self.assertFalse(
            unknown.install_eligible
        )

    def test_09_eligibility_never_asserts_installation_or_activation(self):
        _, value = proposal()

        assessment = (
            GovernedCouncilExpansion
            .assess_lifecycle(
                value,
                CouncilLifecycleEvidence(
                    value.proposal_id,
                    CapsuleStatus.SHADOW,
                    E.PASS,
                    E.PASS,
                    E.PASS,
                    E.PASS,
                    "test://eligible",
                ),
            )
        )

        self.assertTrue(
            assessment.install_eligible
        )

        for field_name in (
            "installation_authorized",
            "installation_executed",
            "activation_authorized",
            "activation_executed",
            "execution_authorized",
            "system_truth_asserted",
        ):
            with self.assertRaises(
                CouncilExpansionInvariantError
            ):
                replace(
                    assessment,
                    **{
                        field_name: True
                    },
                )

    def test_10_module_is_passive_and_registry_is_downstream(self):
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
                    "maestro.councils.dynamic_registry"
                )
                or name.startswith(
                    "maestro.providers"
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
            )
        }

        self.assertEqual(
            forbidden_imports,
            set(),
        )

        forbidden_calls = {
            "install",
            "activate",
            "execute",
            "authorize",
            "store",
            "commit",
            "write_text",
            "write_bytes",
            "unlink",
            "remove",
        }

        self.assertEqual(
            calls & forbidden_calls,
            set(),
        )


if __name__ == "__main__":
    unittest.main()
