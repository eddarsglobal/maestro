from __future__ import annotations

import ast
import unittest
from dataclasses import fields, replace
from pathlib import Path

from maestro.cognitive_economy.minimum_sufficient import (
    GovernedResourceEconomyProfile,
    MinimumSufficientResourceInvariantError,
    MinimumSufficientResourcePolicy,
    MinimumSufficientResourceSelector,
)
from maestro.sovereign.generic_descriptors import (
    GenericResourceDescriptor,
)


CONSTITUTION = Path(
    "docs/MINIMUM_SUFFICIENT_RESOURCE_CONSTITUTION.md"
)

SOURCE = Path(
    "src/maestro/cognitive_economy/minimum_sufficient.py"
)


def resource(
    resource_id: str,
    capabilities: set[str] | frozenset[str],
    *,
    kind: str = "GENERIC",
) -> GenericResourceDescriptor:
    return GenericResourceDescriptor(
        resource_id=resource_id,
        resource_kind=kind,
        host_id="host-a",
        capability_ids=frozenset(capabilities),
        status="AVAILABLE",
    )


def economy(
    resource_id: str,
    *,
    quality: float = 0.8,
    cost: float = 0.2,
    latency: float = 0.2,
    mass: float = 0.2,
) -> GovernedResourceEconomyProfile:
    return GovernedResourceEconomyProfile(
        resource_id=resource_id,
        quality_score=quality,
        cost_score=cost,
        latency_score=latency,
        resource_mass_score=mass,
        evidence_refs=(
            f"EVD-{resource_id}",
        ),
    )


class MinimumSufficientResourceTests(unittest.TestCase):
    def test_01_constitution_contains_all_ten_msr_laws(self):
        text = CONSTITUTION.read_text(encoding="utf-8")

        for number in range(1, 11):
            self.assertIn(
                f"MSR-{number:02d}",
                text,
            )

        self.assertIn("BMF-013", text)
        self.assertIn(
            "ECONOMICALLY SELECTED",
            text,
        )

    def test_02_minimum_capability_mass_defeats_overprovisioning(self):
        small = resource(
            "small",
            {"reasoning.general"},
        )

        large = resource(
            "large",
            {
                "reasoning.general",
                "reasoning.heavy",
                "code",
                "tool.use",
                "embedding",
            },
        )

        decision = MinimumSufficientResourceSelector.select(
            (large, small),
            (
                economy(
                    "large",
                    quality=0.99,
                    cost=0.01,
                    latency=0.01,
                    mass=0.8,
                ),
                economy(
                    "small",
                    quality=0.70,
                    cost=0.50,
                    latency=0.50,
                    mass=0.2,
                ),
            ),
            MinimumSufficientResourcePolicy(
                required_capability_ids=frozenset({
                    "reasoning.general",
                }),
                min_quality_score=0.70,
            ),
        )

        self.assertEqual(
            decision.selected_resource_id,
            "small",
        )
        self.assertEqual(
            decision.selected.excess_capability_count,
            0,
        )

    def test_03_hard_sufficiency_envelope_is_enforced(self):
        rows = (
            resource("under", {"cap.a"}),
            resource("quality", {"cap.a", "cap.b"}),
            resource("cost", {"cap.a", "cap.b"}),
            resource("latency", {"cap.a", "cap.b"}),
            resource("mass", {"cap.a", "cap.b"}),
            resource("good", {"cap.a", "cap.b"}),
        )

        profiles = (
            economy("under"),
            economy("quality", quality=0.59),
            economy("cost", cost=0.61),
            economy("latency", latency=0.61),
            economy("mass", mass=0.61),
            economy(
                "good",
                quality=0.60,
                cost=0.60,
                latency=0.60,
                mass=0.60,
            ),
        )

        decision = MinimumSufficientResourceSelector.select(
            rows,
            profiles,
            MinimumSufficientResourcePolicy(
                required_capability_ids=frozenset({
                    "cap.a",
                    "cap.b",
                }),
                min_quality_score=0.60,
                max_cost_score=0.60,
                max_latency_score=0.60,
                max_resource_mass_score=0.60,
            ),
        )

        self.assertEqual(
            decision.selected_resource_id,
            "good",
        )
        self.assertEqual(
            set(decision.rejected_resource_ids),
            {
                "under",
                "quality",
                "cost",
                "latency",
                "mass",
            },
        )

    def test_04_lower_resource_mass_wins_after_equal_capability_mass(self):
        heavy = resource("heavy", {"cap.a"})
        light = resource("light", {"cap.a"})

        decision = MinimumSufficientResourceSelector.select(
            (heavy, light),
            (
                economy(
                    "heavy",
                    quality=1.0,
                    cost=0.0,
                    latency=0.0,
                    mass=0.8,
                ),
                economy(
                    "light",
                    quality=0.7,
                    cost=0.8,
                    latency=0.8,
                    mass=0.1,
                ),
            ),
            MinimumSufficientResourcePolicy(
                required_capability_ids=frozenset({
                    "cap.a",
                }),
                min_quality_score=0.7,
            ),
        )

        self.assertEqual(
            decision.selected_resource_id,
            "light",
        )

    def test_05_cost_latency_quality_and_id_form_deterministic_tail_rank(self):
        resources = tuple(
            resource(name, {"cap.a"})
            for name in (
                "z-quality",
                "y-latency",
                "x-cost",
            )
        )

        profiles = (
            economy(
                "z-quality",
                quality=1.0,
                cost=0.3,
                latency=0.1,
                mass=0.2,
            ),
            economy(
                "y-latency",
                quality=0.8,
                cost=0.2,
                latency=0.05,
                mass=0.2,
            ),
            economy(
                "x-cost",
                quality=0.7,
                cost=0.1,
                latency=0.9,
                mass=0.2,
            ),
        )

        policy = MinimumSufficientResourcePolicy(
            required_capability_ids=frozenset({
                "cap.a",
            }),
        )

        first = MinimumSufficientResourceSelector.select(
            resources,
            profiles,
            policy,
        )
        second = MinimumSufficientResourceSelector.select(
            tuple(reversed(resources)),
            tuple(reversed(profiles)),
            policy,
        )

        self.assertEqual(
            first.selected_resource_id,
            "x-cost",
        )
        self.assertEqual(
            first.to_dict(),
            second.to_dict(),
        )

        identical_resources = (
            resource("resource-z", {"cap.a"}),
            resource("resource-a", {"cap.a"}),
        )
        identical_profiles = (
            economy("resource-z"),
            economy("resource-a"),
        )

        tied = MinimumSufficientResourceSelector.select(
            identical_resources,
            identical_profiles,
            policy,
        )

        self.assertEqual(
            tied.selected_resource_id,
            "resource-a",
        )

    def test_06_generic_intelligence_compute_and_future_resources_need_no_provider_model(self):
        field_names = {
            field.name
            for field in fields(
                MinimumSufficientResourcePolicy
            )
        }

        self.assertNotIn("provider_id", field_names)
        self.assertNotIn("model_id", field_names)

        cases = (
            (
                "future-intelligence",
                "INTELLIGENCE-NOT-INVENTED",
                "future.reasoning.alpha",
            ),
            (
                "future-compute",
                "COMPUTE-NOT-INVENTED",
                "future.compute.alpha",
            ),
        )

        for resource_id, kind, capability in cases:
            with self.subTest(resource_id=resource_id):
                row = resource(
                    resource_id,
                    {capability},
                    kind=kind,
                )
                decision = (
                    MinimumSufficientResourceSelector
                    .select(
                        (row,),
                        (economy(resource_id),),
                        MinimumSufficientResourcePolicy(
                            required_capability_ids=
                            frozenset({capability}),
                        ),
                    )
                )
                self.assertEqual(
                    decision.selected_resource_id,
                    resource_id,
                )

    def test_07_resource_profile_integrity_fails_closed(self):
        row = resource("resource-a", {"cap.a"})
        profile = economy("resource-a")
        policy = MinimumSufficientResourcePolicy(
            required_capability_ids=frozenset({
                "cap.a",
            }),
        )

        with self.assertRaises(
            MinimumSufficientResourceInvariantError
        ):
            MinimumSufficientResourceSelector.select(
                (row,),
                (),
                policy,
            )

        with self.assertRaises(
            MinimumSufficientResourceInvariantError
        ):
            MinimumSufficientResourceSelector.select(
                (row, row),
                (profile,),
                policy,
            )

        with self.assertRaises(
            MinimumSufficientResourceInvariantError
        ):
            MinimumSufficientResourceSelector.select(
                (row,),
                (profile, profile),
                policy,
            )

    def test_08_forbidden_and_no_sufficient_resource_fail_closed(self):
        row = resource("resource-a", {"cap.a"})
        profile = economy("resource-a")

        with self.assertRaises(LookupError):
            MinimumSufficientResourceSelector.select(
                (row,),
                (profile,),
                MinimumSufficientResourcePolicy(
                    required_capability_ids=frozenset({
                        "cap.a",
                    }),
                    forbidden_resource_ids=frozenset({
                        "resource-a",
                    }),
                ),
            )

        with self.assertRaises(LookupError):
            MinimumSufficientResourceSelector.select(
                (row,),
                (profile,),
                MinimumSufficientResourcePolicy(
                    required_capability_ids=frozenset({
                        "cap.missing",
                    }),
                ),
            )

    def test_09_selection_decision_cannot_assert_authority(self):
        row = resource("resource-a", {"cap.a"})
        decision = MinimumSufficientResourceSelector.select(
            (row,),
            (economy("resource-a"),),
            MinimumSufficientResourcePolicy(
                required_capability_ids=frozenset({
                    "cap.a",
                }),
            ),
        )

        forbidden = (
            "execution_authorized",
            "activation_authorized",
            "trust_asserted",
            "system_truth_asserted",
        )

        for name in forbidden:
            with self.subTest(name=name):
                with self.assertRaises(
                    MinimumSufficientResourceInvariantError
                ):
                    replace(
                        decision,
                        **{name: True},
                    )

        with self.assertRaises(
            MinimumSufficientResourceInvariantError
        ):
            replace(
                decision,
                selection_only=False,
            )

    def test_10_selector_is_passive_and_non_executing(self):
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
                "execute",
                "activate",
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
