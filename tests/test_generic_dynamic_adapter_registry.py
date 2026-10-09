from __future__ import annotations

import ast
import unittest
from dataclasses import dataclass, fields
from pathlib import Path

from maestro.sovereign.generic_adapters import (
    DynamicAdapterRegistry,
    GenericAdapterDescriptor,
)
from maestro.sovereign.generic_descriptors import (
    GenericResourceDescriptor,
)


CONSTITUTION = Path(
    "docs/GENERIC_DYNAMIC_ADAPTER_REGISTRY_CONSTITUTION.md"
)

ADAPTER_SOURCE = Path(
    "src/maestro/sovereign/generic_adapters.py"
)


@dataclass(frozen=True)
class FutureAdapter:
    adapter_id: str
    resource_id: str
    capability_ids: frozenset[str]


def resource(
    resource_id: str = "future-resource",
    capabilities: frozenset[str] = frozenset({
        "future.compute.alpha",
        "future.semantic.beta",
    }),
) -> GenericResourceDescriptor:
    return GenericResourceDescriptor(
        resource_id=resource_id,
        resource_kind="technology-not-invented-yet",
        host_id="future-host",
        capability_ids=capabilities,
        status="OBSERVED",
        locality="UNKNOWN",
    )


def adapter_pair(
    resource_id: str,
    adapter_id: str,
    capabilities: frozenset[str],
) -> tuple[
    GenericAdapterDescriptor,
    FutureAdapter,
]:
    descriptor = GenericAdapterDescriptor(
        adapter_id=adapter_id,
        resource_id=resource_id,
        adapter_kind="future-adapter-class",
        capability_ids=capabilities,
    )

    adapter = FutureAdapter(
        adapter_id=adapter_id,
        resource_id=resource_id,
        capability_ids=capabilities,
    )

    return descriptor, adapter


class GenericDynamicAdapterRegistryTests(unittest.TestCase):
    def test_01_constitution_contains_all_ten_gar_laws(self):
        text = CONSTITUTION.read_text(encoding="utf-8")

        for number in range(1, 11):
            self.assertIn(
                f"GAR-{number:02d}",
                text,
            )

        self.assertIn("BMF-010", text)

    def test_02_generic_adapter_descriptor_has_no_provider_model_runtime_requirement(self):
        names = {
            field.name
            for field in fields(
                GenericAdapterDescriptor
            )
        }

        self.assertNotIn("provider_id", names)
        self.assertNotIn("model_id", names)
        self.assertNotIn("runtime_id", names)

    def test_03_unknown_future_resource_can_register(self):
        row = resource()
        descriptor, adapter = adapter_pair(
            row.resource_id,
            "future-adapter",
            frozenset({
                "future.compute.alpha",
            }),
        )

        registry = DynamicAdapterRegistry()
        binding = registry.register(
            row,
            descriptor,
            adapter,
        )

        self.assertEqual(len(registry), 1)
        self.assertIs(
            registry.adapter(row.resource_id),
            adapter,
        )
        self.assertIs(
            registry.binding(row.resource_id),
            binding,
        )

    def test_04_duplicate_resource_binding_fails_closed(self):
        row = resource()
        descriptor, adapter = adapter_pair(
            row.resource_id,
            "adapter-a",
            frozenset({
                "future.compute.alpha",
            }),
        )

        registry = DynamicAdapterRegistry()
        registry.register(row, descriptor, adapter)

        with self.assertRaises(ValueError):
            registry.register(
                row,
                descriptor,
                adapter,
            )

    def test_05_duplicate_adapter_identity_across_resources_fails_closed(self):
        first = resource("resource-a")
        second = resource("resource-b")

        first_descriptor, first_adapter = adapter_pair(
            first.resource_id,
            "shared-adapter",
            frozenset({
                "future.compute.alpha",
            }),
        )

        second_descriptor, second_adapter = adapter_pair(
            second.resource_id,
            "shared-adapter",
            frozenset({
                "future.compute.alpha",
            }),
        )

        registry = DynamicAdapterRegistry()
        registry.register(
            first,
            first_descriptor,
            first_adapter,
        )

        with self.assertRaises(ValueError):
            registry.register(
                second,
                second_descriptor,
                second_adapter,
            )

    def test_06_identity_and_capability_mismatches_fail_closed(self):
        row = resource()
        registry = DynamicAdapterRegistry()

        wrong_resource_descriptor, wrong_resource_adapter = (
            adapter_pair(
                "other-resource",
                "adapter-resource-mismatch",
                frozenset({
                    "future.compute.alpha",
                }),
            )
        )

        with self.assertRaises(ValueError):
            registry.register(
                row,
                wrong_resource_descriptor,
                wrong_resource_adapter,
            )

        bad_descriptor, bad_adapter = adapter_pair(
            row.resource_id,
            "adapter-capability-mismatch",
            frozenset({
                "future.capability.not-declared",
            }),
        )

        with self.assertRaises(ValueError):
            registry.register(
                row,
                bad_descriptor,
                bad_adapter,
            )

    def test_07_replacement_is_explicit_and_observable(self):
        row = resource()

        first_descriptor, first_adapter = adapter_pair(
            row.resource_id,
            "adapter-generation-a",
            frozenset({
                "future.compute.alpha",
            }),
        )

        second_descriptor, second_adapter = adapter_pair(
            row.resource_id,
            "adapter-generation-b",
            frozenset({
                "future.semantic.beta",
            }),
        )

        registry = DynamicAdapterRegistry()
        first = registry.register(
            row,
            first_descriptor,
            first_adapter,
        )

        old, new = registry.replace(
            row,
            second_descriptor,
            second_adapter,
        )

        self.assertIs(old, first)
        self.assertEqual(
            old.descriptor.adapter_id,
            "adapter-generation-a",
        )
        self.assertEqual(
            new.descriptor.adapter_id,
            "adapter-generation-b",
        )
        self.assertIs(
            registry.adapter(row.resource_id),
            second_adapter,
        )

    def test_08_unregister_removes_binding_and_releases_adapter_identity(self):
        first = resource("resource-a")
        second = resource("resource-b")

        descriptor, adapter = adapter_pair(
            first.resource_id,
            "reusable-adapter-id",
            frozenset({
                "future.compute.alpha",
            }),
        )

        registry = DynamicAdapterRegistry()
        original = registry.register(
            first,
            descriptor,
            adapter,
        )

        removed = registry.unregister(
            first.resource_id
        )

        self.assertIs(removed, original)
        self.assertEqual(len(registry), 0)

        second_descriptor, second_adapter = adapter_pair(
            second.resource_id,
            "reusable-adapter-id",
            frozenset({
                "future.compute.alpha",
            }),
        )

        registry.register(
            second,
            second_descriptor,
            second_adapter,
        )

        self.assertEqual(len(registry), 1)

    def test_09_inventory_is_deterministic(self):
        registry = DynamicAdapterRegistry()

        for resource_id in (
            "resource-z",
            "resource-a",
            "resource-m",
        ):
            row = resource(resource_id)
            descriptor, adapter = adapter_pair(
                resource_id,
                f"adapter-{resource_id}",
                frozenset({
                    "future.compute.alpha",
                }),
            )
            registry.register(
                row,
                descriptor,
                adapter,
            )

        observed = [
            item.resource.resource_id
            for item in registry.all()
        ]

        self.assertEqual(
            observed,
            [
                "resource-a",
                "resource-m",
                "resource-z",
            ],
        )

    def test_10_registry_is_passive_and_non_authoritative(self):
        tree = ast.parse(
            ADAPTER_SOURCE.read_text(encoding="utf-8")
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

        row = resource()
        descriptor, adapter = adapter_pair(
            row.resource_id,
            "adapter-passive",
            frozenset({
                "future.compute.alpha",
            }),
        )

        registry = DynamicAdapterRegistry()
        registry.register(
            row,
            descriptor,
            adapter,
        )

        inventory = registry.inventory()

        forbidden_keys = {
            "trusted",
            "authorized",
            "authorization",
            "authority",
            "activated",
            "installed",
            "executed",
            "ay_verdict",
            "ex_authorization",
            "system_truth",
        }

        def keys(value):
            if isinstance(value, dict):
                for key, child in value.items():
                    yield str(key).lower()
                    yield from keys(child)
            elif isinstance(value, (list, tuple)):
                for child in value:
                    yield from keys(child)

        self.assertTrue(
            set(keys(inventory)).isdisjoint(
                forbidden_keys
            )
        )


if __name__ == "__main__":
    unittest.main()
