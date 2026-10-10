from __future__ import annotations

import ast
import unittest

from dataclasses import replace
from pathlib import Path

from maestro.orchestration.governed_mission_foundation import (
    CapabilityRule,
    CouncilCapabilityBinding,
    CouncilGraphIncompleteError,
    GovernedMissionFoundation,
    MissionAnalysisIncompleteError,
    MissionContract,
    MissionFoundationInvariantError,
)


SOURCE = Path(
    "src/maestro/orchestration/"
    "governed_mission_foundation.py"
)

DOC = Path(
    "docs/"
    "GOVERNED_MISSION_FOUNDATION_CONSTITUTION.md"
)


def contract():
    return MissionContract(
        objective=(
            "Build and secure "
            "a local application"
        ),
        scope=(
            "Application architecture "
            "and security"
        ),
        requested_output=(
            "A verified implementation plan"
        ),
        constraints=(
            "No cloud dependency",
            "Preserve mission objective",
        ),
        acceptance_criteria=(
            "Architecture is complete",
            "Security review passes",
        ),
        authority_requirements=(
            "AY acceptance",
            "EX routing",
        ),
        evidence_obligations=(
            "Architecture evidence",
            "Security evidence",
        ),
    )


def rules():
    return (
        CapabilityRule(
            "RULE-IT",
            "SOFTWARE_IMPLEMENTATION",
            (
                "application",
                "architecture",
            ),
            "Mission requires "
            "software architecture.",
        ),
        CapabilityRule(
            "RULE-SC",
            "SECURITY_REVIEW",
            (
                "secure",
                "security",
            ),
            "Mission requires "
            "security evaluation.",
        ),
    )


class GovernedMissionFoundationTests(
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
                f"MCF-{number:02d}",
                text,
            )

        for invariant in (
            "MISSION CREATED != MISSION AUTHORIZED",
            "MISSION CONTRACT != CAPABILITY DEMAND",
            "CAPABILITY != PROVIDER",
            "CAPABILITY DEMAND != RESOURCE SELECTION",
            "COUNCIL != MODEL",
            "COUNCIL REQUIRED != COUNCIL ACTIVATED",
            "MISSING COUNCIL CAPABILITY != DYNAMIC COUNCIL AUTHORIZED",
            "PLAN FOUNDATION != EXECUTION AUTHORIZATION",
            "GRAPH READY != NODE EXECUTED",
            "MISSION FOUNDATION != MISSION EXECUTION",
        ):
            self.assertIn(
                invariant,
                text,
            )

    def test_02_contract_is_complete_and_deterministic(self):
        a = contract()

        b = MissionContract(
            objective=a.objective,
            scope=a.scope,
            requested_output=(
                a.requested_output
            ),
            constraints=tuple(
                reversed(
                    a.constraints
                )
            ),
            acceptance_criteria=tuple(
                reversed(
                    a.acceptance_criteria
                )
            ),
            authority_requirements=tuple(
                reversed(
                    a.authority_requirements
                )
            ),
            evidence_obligations=tuple(
                reversed(
                    a.evidence_obligations
                )
            ),
        )

        self.assertEqual(
            a.contract_id,
            b.contract_id,
        )

        self.assertEqual(
            a.to_dict(),
            b.to_dict(),
        )

    def test_03_incomplete_contract_fails_closed(self):
        with self.assertRaises(
            MissionFoundationInvariantError
        ):
            MissionContract(
                objective="",
                scope="scope",
                requested_output="output",
                constraints=("constraint",),
                acceptance_criteria=("criterion",),
                authority_requirements=("EX",),
                evidence_obligations=("evidence",),
            )

        with self.assertRaises(
            MissionFoundationInvariantError
        ):
            MissionContract(
                objective="objective",
                scope="scope",
                requested_output="output",
                constraints=(),
                acceptance_criteria=("criterion",),
                authority_requirements=("EX",),
                evidence_obligations=("evidence",),
            )

    def test_04_analysis_derives_generic_capabilities(self):
        mission = contract()

        result = (
            GovernedMissionFoundation
            .analyze(
                mission,
                rules(),
            )
        )

        self.assertEqual(
            result.contract_id,
            mission.contract_id,
        )

        self.assertEqual(
            {
                item.capability_id
                for item in result.demands
            },
            {
                "SOFTWARE_IMPLEMENTATION",
                "SECURITY_REVIEW",
            },
        )

        self.assertFalse(
            result.resource_selected
        )
        self.assertFalse(
            result.provider_selected
        )
        self.assertFalse(
            result.model_selected
        )
        self.assertFalse(
            result.execution_authorized
        )

    def test_05_analysis_without_capability_match_fails_closed(self):
        mission = contract()

        with self.assertRaises(
            MissionAnalysisIncompleteError
        ):
            GovernedMissionFoundation.analyze(
                mission,
                (
                    CapabilityRule(
                        "RULE-FN",
                        "FINANCIAL_ANALYSIS",
                        ("tax-only-token",),
                        "Unmatched rule.",
                    ),
                ),
            )

    def test_06_duplicate_rules_and_authority_escalation_fail_closed(self):
        mission = contract()

        duplicate = CapabilityRule(
            "RULE-X",
            "SOFTWARE_IMPLEMENTATION",
            ("application",),
            "Rule.",
        )

        with self.assertRaises(
            MissionFoundationInvariantError
        ):
            GovernedMissionFoundation.analyze(
                mission,
                (
                    duplicate,
                    duplicate,
                ),
            )

        result = (
            GovernedMissionFoundation
            .analyze(
                mission,
                rules(),
            )
        )

        for field_name in (
            "resource_selected",
            "provider_selected",
            "model_selected",
            "execution_authorized",
            "system_truth_asserted",
        ):
            with self.assertRaises(
                MissionFoundationInvariantError
            ):
                replace(
                    result,
                    **{
                        field_name: True
                    },
                )

    def test_07_council_graph_uses_minimum_capability_cover(self):
        mission = contract()

        demand = (
            GovernedMissionFoundation
            .analyze(
                mission,
                rules(),
            )
        )

        graph = (
            GovernedMissionFoundation
            .synthesize_council_graph(
                mission,
                demand,
                (
                    CouncilCapabilityBinding(
                        "IT",
                        (
                            "SOFTWARE_IMPLEMENTATION",
                        ),
                    ),
                    CouncilCapabilityBinding(
                        "SC",
                        (
                            "SECURITY_REVIEW",
                        ),
                    ),
                    CouncilCapabilityBinding(
                        "AI",
                        (
                            "SOFTWARE_IMPLEMENTATION",
                            "SECURITY_REVIEW",
                        ),
                    ),
                ),
            )
        )

        ids = {
            node.council_id
            for node in graph.nodes
        }

        self.assertEqual(
            ids,
            {
                "EX",
                "AY",
                "AI",
            },
        )

        self.assertEqual(
            {
                owner
                for _, owner
                in graph.capability_owners
            },
            {
                "AI",
            },
        )

        self.assertFalse(
            graph.council_activated
        )
        self.assertFalse(
            graph.execution_requested
        )
        self.assertFalse(
            graph.execution_authorized
        )

    def test_08_equal_minimum_graphs_use_deterministic_tie_break(self):
        mission = contract()

        demand = (
            GovernedMissionFoundation
            .analyze(
                mission,
                rules(),
            )
        )

        bindings_a = (
            CouncilCapabilityBinding(
                "SC",
                (
                    "SOFTWARE_IMPLEMENTATION",
                    "SECURITY_REVIEW",
                ),
            ),
            CouncilCapabilityBinding(
                "IT",
                (
                    "SOFTWARE_IMPLEMENTATION",
                    "SECURITY_REVIEW",
                ),
            ),
        )

        bindings_b = tuple(
            reversed(
                bindings_a
            )
        )

        a = (
            GovernedMissionFoundation
            .synthesize_council_graph(
                mission,
                demand,
                bindings_a,
            )
        )

        b = (
            GovernedMissionFoundation
            .synthesize_council_graph(
                mission,
                demand,
                bindings_b,
            )
        )

        self.assertEqual(
            a.graph_id,
            b.graph_id,
        )

        self.assertEqual(
            {
                owner
                for _, owner
                in a.capability_owners
            },
            {
                "IT",
            },
        )

    def test_09_missing_council_coverage_and_rebinding_fail_closed(self):
        mission = contract()

        demand = (
            GovernedMissionFoundation
            .analyze(
                mission,
                rules(),
            )
        )

        with self.assertRaises(
            CouncilGraphIncompleteError
        ):
            GovernedMissionFoundation.synthesize_council_graph(
                mission,
                demand,
                (
                    CouncilCapabilityBinding(
                        "IT",
                        (
                            "SOFTWARE_IMPLEMENTATION",
                        ),
                    ),
                ),
            )

        other = MissionContract(
            objective="Different mission",
            scope="Different scope",
            requested_output="Different output",
            constraints=("Different constraint",),
            acceptance_criteria=("Different criterion",),
            authority_requirements=("EX routing",),
            evidence_obligations=("Different evidence",),
        )

        with self.assertRaises(
            MissionFoundationInvariantError
        ):
            GovernedMissionFoundation.synthesize_council_graph(
                other,
                demand,
                (
                    CouncilCapabilityBinding(
                        "AI",
                        (
                            "SOFTWARE_IMPLEMENTATION",
                            "SECURITY_REVIEW",
                        ),
                    ),
                ),
            )

    def test_10_module_is_passive_and_resource_independent(self):
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

        forbidden_import_roots = (
            "maestro.providers",
            "maestro.sovereign.router",
            "maestro.intelligence_market",
            "maestro.tools",
            "maestro.autonomous.executor",
            "subprocess",
            "socket",
            "requests",
            "httpx",
            "aiohttp",
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

        self.assertEqual(
            bad_imports,
            set(),
        )

        forbidden_calls = {
            "execute",
            "activate",
            "authorize",
            "install",
            "dispatch",
            "route",
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
