from __future__ import annotations

import ast
import unittest
from dataclasses import replace
from pathlib import Path

from maestro.orchestration.cost_avoidance import (
    GovernedOrchestrationPathSelector,
    OrchestrationCostInvariantError,
    OrchestrationCostPolicy,
    OrchestrationPath,
    WorkRequirements,
)


CONSTITUTION = Path(
    "docs/ORCHESTRATION_COST_AVOIDANCE_CONSTITUTION.md"
)

SOURCE = Path(
    "src/maestro/orchestration/cost_avoidance.py"
)


class OrchestrationCostAvoidanceTests(unittest.TestCase):
    def test_01_constitution_contains_all_ten_oca_laws(self):
        text = CONSTITUTION.read_text(encoding="utf-8")

        for number in range(1, 11):
            self.assertIn(
                f"OCA-{number:02d}",
                text,
            )

        self.assertIn("BMF-014", text)
        self.assertIn(
            "LEAST ORCHESTRATION SUFFICIENT",
            text,
        )

    def test_02_atomic_is_zero_orchestration_baseline(self):
        decision = (
            GovernedOrchestrationPathSelector
            .select(
                WorkRequirements(
                    work_id="atomic",
                )
            )
        )

        self.assertIs(
            decision.selected_path,
            OrchestrationPath.ATOMIC,
        )
        self.assertEqual(decision.path_cost_rank, 0)
        self.assertEqual(decision.required_council_ids, ())
        self.assertEqual(decision.required_resource_calls, 0)
        self.assertEqual(decision.required_cognitive_depth, 0)
        self.assertFalse(decision.cognition_required)
        self.assertFalse(decision.fabric_required)

    def test_03_cognitive_path_preserves_exact_requirements_without_fabric(self):
        decision = (
            GovernedOrchestrationPathSelector
            .select(
                WorkRequirements(
                    work_id="cognitive",
                    requires_cognition=True,
                    required_council_ids=frozenset({
                        "SC",
                        "IT",
                    }),
                    required_resource_calls=1,
                    required_cognitive_depth=2,
                )
            )
        )

        self.assertIs(
            decision.selected_path,
            OrchestrationPath.COGNITIVE,
        )
        self.assertEqual(decision.path_cost_rank, 1)
        self.assertEqual(
            decision.required_council_ids,
            ("IT", "SC"),
        )
        self.assertEqual(decision.required_resource_calls, 1)
        self.assertEqual(decision.required_cognitive_depth, 2)
        self.assertTrue(decision.cognition_required)
        self.assertFalse(decision.fabric_required)

    def test_04_cognitive_path_can_be_inferred_from_declared_cognitive_work(self):
        cases = (
            WorkRequirements(
                work_id="council",
                required_council_ids=frozenset({"IT"}),
            ),
            WorkRequirements(
                work_id="resource",
                required_resource_calls=1,
            ),
            WorkRequirements(
                work_id="depth",
                required_cognitive_depth=1,
            ),
        )

        for requirements in cases:
            with self.subTest(work=requirements.work_id):
                decision = (
                    GovernedOrchestrationPathSelector
                    .select(requirements)
                )
                self.assertIs(
                    decision.selected_path,
                    OrchestrationPath.COGNITIVE,
                )
                self.assertFalse(decision.fabric_required)

    def test_05_fabric_requires_distribution_remote_capacity_or_cross_node_state(self):
        cases = (
            WorkRequirements(
                work_id="distribution",
                requires_distribution=True,
            ),
            WorkRequirements(
                work_id="remote",
                requires_remote_capacity=True,
            ),
            WorkRequirements(
                work_id="cross-node",
                requires_cross_node_state=True,
            ),
            WorkRequirements(
                work_id="cognitive-distributed",
                requires_cognition=True,
                required_resource_calls=1,
                requires_distribution=True,
            ),
        )

        for requirements in cases:
            with self.subTest(work=requirements.work_id):
                decision = (
                    GovernedOrchestrationPathSelector
                    .select(requirements)
                )
                self.assertIs(
                    decision.selected_path,
                    OrchestrationPath.FABRIC,
                )
                self.assertEqual(decision.path_cost_rank, 2)
                self.assertTrue(decision.fabric_required)

    def test_06_policy_ceilings_fail_closed(self):
        cases = (
            (
                WorkRequirements(
                    work_id="cognitive",
                    requires_cognition=True,
                ),
                OrchestrationCostPolicy(
                    allow_cognitive=False,
                ),
            ),
            (
                WorkRequirements(
                    work_id="fabric",
                    requires_distribution=True,
                ),
                OrchestrationCostPolicy(
                    allow_fabric=False,
                ),
            ),
            (
                WorkRequirements(
                    work_id="councils",
                    required_council_ids=frozenset({
                        "IT",
                        "SC",
                    }),
                ),
                OrchestrationCostPolicy(
                    max_council_count=1,
                ),
            ),
            (
                WorkRequirements(
                    work_id="resources",
                    required_resource_calls=2,
                ),
                OrchestrationCostPolicy(
                    max_resource_calls=1,
                ),
            ),
            (
                WorkRequirements(
                    work_id="depth",
                    required_cognitive_depth=3,
                ),
                OrchestrationCostPolicy(
                    max_cognitive_depth=2,
                ),
            ),
        )

        for requirements, policy in cases:
            with self.subTest(work=requirements.work_id):
                with self.assertRaises(LookupError):
                    (
                        GovernedOrchestrationPathSelector
                        .select(requirements, policy)
                    )

    def test_07_decision_is_deterministic_and_has_no_council_fanout(self):
        first = (
            GovernedOrchestrationPathSelector
            .select(
                WorkRequirements(
                    work_id="deterministic",
                    required_council_ids=frozenset({
                        "SC",
                        "IT",
                        "AY",
                    }),
                    required_resource_calls=1,
                    required_cognitive_depth=2,
                )
            )
        )

        second = (
            GovernedOrchestrationPathSelector
            .select(
                WorkRequirements(
                    work_id="deterministic",
                    required_council_ids=frozenset({
                        "AY",
                        "IT",
                        "SC",
                    }),
                    required_resource_calls=1,
                    required_cognitive_depth=2,
                )
            )
        )

        self.assertEqual(first.to_dict(), second.to_dict())
        self.assertEqual(
            first.required_council_ids,
            ("AY", "IT", "SC"),
        )
        self.assertEqual(len(first.required_council_ids), 3)

    def test_08_unnecessary_escalation_and_authority_fail_closed(self):
        decision = (
            GovernedOrchestrationPathSelector
            .select(
                WorkRequirements(
                    work_id="atomic",
                )
            )
        )

        authority_fields = (
            "council_activation_authorized",
            "intelligence_execution_authorized",
            "fabric_dispatch_authorized",
            "network_authorized",
            "system_truth_asserted",
        )

        for field_name in authority_fields:
            with self.subTest(field=field_name):
                with self.assertRaises(
                    OrchestrationCostInvariantError
                ):
                    replace(
                        decision,
                        **{field_name: True},
                    )

        with self.assertRaises(
            OrchestrationCostInvariantError
        ):
            replace(
                decision,
                selection_only=False,
            )

        with self.assertRaises(
            OrchestrationCostInvariantError
        ):
            replace(
                decision,
                selected_path=OrchestrationPath.COGNITIVE,
                path_cost_rank=1,
            )

    def test_09_payload_is_selection_only_and_non_authoritative(self):
        payload = (
            GovernedOrchestrationPathSelector
            .select(
                WorkRequirements(
                    work_id="payload",
                    required_resource_calls=1,
                )
            )
            .to_dict()
        )

        self.assertEqual(
            payload["selected_path"],
            "COGNITIVE",
        )
        self.assertTrue(payload["selection_only"])
        self.assertFalse(
            payload["council_activation_authorized"]
        )
        self.assertFalse(
            payload["intelligence_execution_authorized"]
        )
        self.assertFalse(
            payload["fabric_dispatch_authorized"]
        )
        self.assertFalse(payload["network_authorized"])
        self.assertFalse(payload["system_truth_asserted"])

    def test_10_selector_is_passive_and_imports_no_heavy_runtime(self):
        tree = ast.parse(
            SOURCE.read_text(encoding="utf-8")
        )

        imports = set()
        calls = set()

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.update(
                    alias.name
                    for alias in node.names
                )
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.add(node.module)
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute):
                    calls.add(node.func.attr)
                elif isinstance(node.func, ast.Name):
                    calls.add(node.func.id)

        forbidden_roots = {
            "socket",
            "subprocess",
            "urllib",
            "requests",
            "httpx",
            "aiohttp",
            "maestro.councils",
            "maestro.cognitive_fabric",
            "maestro.fabric",
            "maestro.intelligence_market",
            "maestro.providers",
        }

        bad_imports = {
            name
            for name in imports
            if any(
                name == root
                or name.startswith(root + ".")
                for root in forbidden_roots
            )
        }

        self.assertFalse(bad_imports)
        self.assertTrue(
            calls.isdisjoint({
                "activate",
                "execute",
                "dispatch",
                "install",
                "download",
                "connect",
                "urlopen",
                "Popen",
                "run",
            })
        )


if __name__ == "__main__":
    unittest.main()
