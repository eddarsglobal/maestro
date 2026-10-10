from __future__ import annotations

import ast
import json
import os
import subprocess
import sys
import tempfile
import unittest
from dataclasses import MISSING, dataclass, fields, replace
from pathlib import Path
from typing import Any

from maestro.genesis.system import ProductionGenesisSystem
from maestro.sovereign.generic_adapters import (
    GenericAdapterDescriptor,
)
from maestro.sovereign.generic_discovery import (
    CapabilityObservation,
    GenericDiscoveryProjection,
    GenericHostDiscoveryProjector,
    HostDiscoveryObservation,
    ResourceObservation,
)
from maestro.sovereign.platform_boundary import (
    GovernedPlatformBoundary,
    PlatformBoundaryInvariantError,
    PlatformIdentity,
)


CONSTITUTION = Path(
    "docs/PLATFORM_ABSTRACTION_BOUNDARY_CONSTITUTION.md"
)

PAB_SOURCE = Path(
    "src/maestro/sovereign/platform_boundary.py"
)

EDGE_SOURCE = Path(
    "src/maestro/providers/ollama/"
    "sovereign_discovery_bridge.py"
)

GENERIC_BRIDGE_SOURCE = Path(
    "src/maestro/sovereign/discovery.py"
)

ROOT_SOURCE = Path(
    "src/maestro/__init__.py"
)

GENESIS_SOURCE = Path(
    "src/maestro/genesis/system.py"
)


def construct(cls: type, values: dict[str, Any]):
    kwargs: dict[str, Any] = {}

    for item in fields(cls):
        if item.name in values:
            kwargs[item.name] = values[item.name]
            continue

        if (
            item.default is not MISSING
            or item.default_factory is not MISSING
        ):
            continue

        raise AssertionError(
            f"Missing test value for "
            f"{cls.__name__}.{item.name}"
        )

    return cls(**kwargs)


def generic_projection() -> GenericDiscoveryProjection:
    capability = construct(
        CapabilityObservation,
        {
            "capability_id": "future.capability.alpha",
            "domain": "FUTURE",
            "version": "1",
            "description": "Future capability.",
            "attributes": {
                "source": "test-edge",
            },
        },
    )

    resource = construct(
        ResourceObservation,
        {
            "resource_id": "future-resource-a",
            "resource_kind": "FUTURE_RESOURCE",
            "capability_ids": frozenset({
                "future.capability.alpha",
            }),
            "status": "AVAILABLE",
            "locality": "LOCAL",
            "attributes": {
                "source": "test-edge",
            },
        },
    )

    observation = construct(
        HostDiscoveryObservation,
        {
            "host_id": "future-host-a",
            "host_kind": "FUTURE_HOST",
            "locality": "LOCAL",
            "capabilities": (capability,),
            "resources": (resource,),
            "attributes": {
                "source": "test-edge",
            },
        },
    )

    return GenericHostDiscoveryProjector.project(
        observation
    )


@dataclass(frozen=True, slots=True)
class MetadataAdapter:
    adapter_id: str
    resource_id: str
    capability_ids: frozenset[str]


class PlatformAbstractionBoundaryTests(unittest.TestCase):
    def test_01_constitution_contains_all_ten_pab_laws(self):
        text = CONSTITUTION.read_text(
            encoding="utf-8"
        )

        for number in range(1, 11):
            self.assertIn(
                f"PAB-{number:02d}",
                text,
            )

        self.assertIn("BMF-015", text)
        self.assertIn(
            "PLATFORM IDENTITY = ADAPTER DATA",
            text,
        )
        self.assertIn(
            "DISCOVERY != TRUST",
            text,
        )
        self.assertIn(
            "HANDOFF != AUTHORIZATION",
            text,
        )

    def test_02_generic_core_imports_load_zero_provider_modules(self):
        modules = (
            "maestro",
            "maestro.sovereign",
            "maestro.sovereign.generic_descriptors",
            "maestro.sovereign.generic_discovery",
            "maestro.sovereign.generic_adapters",
            "maestro.sovereign.platform_boundary",
            "maestro.cognitive_economy.minimum_sufficient",
            "maestro.orchestration.cost_avoidance",
            "maestro.genesis.system",
        )

        probe = r'''
import importlib
import json
import sys

importlib.import_module(sys.argv[1])

providers = sorted(
    name
    for name in sys.modules
    if name == "maestro.providers"
    or name.startswith("maestro.providers.")
)

print(json.dumps(providers))
'''

        env = dict(os.environ)
        env["PYTHONPATH"] = "src"

        for module in modules:
            with self.subTest(module=module):
                output = subprocess.check_output(
                    [
                        sys.executable,
                        "-c",
                        probe,
                        module,
                    ],
                    env=env,
                    text=True,
                )

                self.assertEqual(
                    json.loads(output),
                    [],
                )

    def test_03_raw_discovery_is_rejected_and_generic_projection_is_accepted(self):
        platform = PlatformIdentity(
            platform_id="future-platform-x",
            platform_kind="NOT-YET-INVENTED",
            attributes={
                "edge": "test",
            },
        )

        with self.assertRaises(TypeError):
            GovernedPlatformBoundary.accept_discovery(
                platform,
                object(),
            )

        projection = generic_projection()

        result = (
            GovernedPlatformBoundary
            .accept_discovery(
                platform,
                projection,
            )
        )

        self.assertIs(
            result.projection,
            projection,
        )
        self.assertTrue(result.selection_only)
        self.assertFalse(result.trust_asserted)
        self.assertFalse(
            result.execution_authorized
        )
        self.assertFalse(
            result.network_authorized
        )

    def test_04_generic_adapter_validation_and_handoff_are_non_authoritative(self):
        projection = generic_projection()

        resource = projection.resources[0]

        platform = PlatformIdentity(
            platform_id="future-platform-y",
            platform_kind="UNKNOWN_FUTURE_PLATFORM",
        )

        adapter_id = "future-adapter-a"

        descriptor = GenericAdapterDescriptor(
            adapter_id=adapter_id,
            resource_id=resource.resource_id,
            adapter_kind="FUTURE_ADAPTER",
            capability_ids=frozenset(
                resource.capability_ids
            ),
            attributes={
                "edge": "test",
            },
        )

        adapter = MetadataAdapter(
            adapter_id=adapter_id,
            resource_id=resource.resource_id,
            capability_ids=frozenset(
                resource.capability_ids
            ),
        )

        validated = (
            GovernedPlatformBoundary
            .validate_adapter(
                platform,
                resource,
                descriptor,
                adapter,
            )
        )

        capability_id = next(
            iter(resource.capability_ids)
        )

        handoff = (
            GovernedPlatformBoundary
            .build_execution_handoff(
                platform,
                validated.binding,
                capability_id,
            )
        )

        self.assertTrue(handoff.handoff_only)
        self.assertFalse(
            handoff.execution_authorized
        )
        self.assertFalse(
            handoff.activation_authorized
        )
        self.assertFalse(
            handoff.network_authorized
        )
        self.assertFalse(
            handoff.system_truth_asserted
        )

        payload = handoff.to_dict()

        self.assertNotIn(
            "adapter",
            payload,
        )

    def test_05_authority_escalation_fails_closed(self):
        platform = PlatformIdentity(
            platform_id="future-platform-z",
        )

        result = (
            GovernedPlatformBoundary
            .accept_discovery(
                platform,
                generic_projection(),
            )
        )

        fields_to_escalate = (
            "trust_asserted",
            "installation_authorized",
            "activation_authorized",
            "execution_authorized",
            "network_authorized",
            "system_truth_asserted",
        )

        for field_name in fields_to_escalate:
            with self.subTest(field=field_name):
                with self.assertRaises(
                    PlatformBoundaryInvariantError
                ):
                    replace(
                        result,
                        **{field_name: True},
                    )

        with self.assertRaises(
            PlatformBoundaryInvariantError
        ):
            replace(
                result,
                selection_only=False,
            )

    def test_06_core_static_provider_dependency_direction_is_clean(self):
        violations = []

        for path in Path(
            "src/maestro"
        ).rglob("*.py"):
            relative = path.as_posix()

            if relative.startswith(
                "src/maestro/providers/"
            ):
                continue

            if relative == (
                "src/maestro/local_intelligence.py"
            ):
                continue

            tree = ast.parse(
                path.read_text(
                    encoding="utf-8"
                )
            )

            bad = set()

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name.startswith(
                            "maestro.providers"
                        ):
                            bad.add(alias.name)

                elif isinstance(
                    node,
                    ast.ImportFrom,
                ):
                    module = node.module or ""

                    if module.startswith(
                        "maestro.providers"
                    ):
                        bad.add(module)

            if bad:
                violations.append(
                    (
                        relative,
                        sorted(bad),
                    )
                )

        self.assertEqual(
            violations,
            [],
        )

    def test_07_genesis_is_zero_platform_by_default(self):
        with tempfile.TemporaryDirectory() as td:
            system = ProductionGenesisSystem(td)

            self.assertIsNone(
                system.local_intelligence
            )

        self.assertNotIn(
            "LocalIntelligence.ollama()",
            GENESIS_SOURCE.read_text(
                encoding="utf-8"
            ),
        )

    def test_08_legacy_sovereign_bridge_is_provider_neutral(self):
        source = (
            GENERIC_BRIDGE_SOURCE
            .read_text(
                encoding="utf-8"
            )
        )

        tree = ast.parse(source)

        provider_imports = set()

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.startswith(
                        "maestro.providers"
                    ):
                        provider_imports.add(
                            alias.name
                        )

            elif isinstance(
                node,
                ast.ImportFrom,
            ):
                module = node.module or ""

                if module.startswith(
                    "maestro.providers"
                ):
                    provider_imports.add(
                        module
                    )

        self.assertEqual(
            provider_imports,
            set(),
        )

        self.assertNotIn(
            "import_ollama",
            source,
        )

        self.assertIn(
            "register_bindings",
            source,
        )

    def test_09_provider_edge_crosses_pab_before_legacy_registration(self):
        source = EDGE_SOURCE.read_text(
            encoding="utf-8"
        )

        required = (
            "PlatformIdentity",
            "GenericDiscoveryProjection",
            "GenericHostDiscoveryProjector",
            "GenericResourceDescriptor",
            "GenericAdapterDescriptor",
            "GovernedPlatformBoundary",
            "accept_discovery",
            "validate_adapter",
            "build_execution_handoff",
            "register_bindings",
        )

        for symbol in required:
            self.assertIn(
                symbol,
                source,
            )

        tree = ast.parse(source)

        method = next(
            node
            for node in ast.walk(tree)
            if isinstance(
                node,
                ast.FunctionDef,
            )
            and node.name == "import_ollama"
        )

        calls = []

        for node in ast.walk(method):
            if not isinstance(
                node,
                ast.Call,
            ):
                continue

            if isinstance(
                node.func,
                ast.Attribute,
            ):
                calls.append(
                    (
                        node.lineno,
                        node.func.attr,
                    )
                )

            elif isinstance(
                node.func,
                ast.Name,
            ):
                calls.append(
                    (
                        node.lineno,
                        node.func.id,
                    )
                )

        accept_lines = [
            line
            for line, name in calls
            if name == "accept_discovery"
        ]

        validation_lines = [
            line
            for line, name in calls
            if name == "_validate_generic_adapter"
        ]

        registration_lines = [
            line
            for line, name in calls
            if name == "register_bindings"
        ]

        self.assertTrue(accept_lines)
        self.assertTrue(validation_lines)
        self.assertTrue(registration_lines)

        self.assertLess(
            max(accept_lines),
            min(registration_lines),
        )

        self.assertLess(
            max(validation_lines),
            min(registration_lines),
        )

    def test_10_provider_edge_keeps_platform_identity_outside_core_identity(self):
        edge = EDGE_SOURCE.read_text(
            encoding="utf-8"
        )

        pab = PAB_SOURCE.read_text(
            encoding="utf-8"
        )

        root = ROOT_SOURCE.read_text(
            encoding="utf-8"
        )

        self.assertIn(
            "class PlatformIdentity",
            pab,
        )

        self.assertIn(
            "PlatformIdentity",
            edge,
        )

        self.assertIn(
            "__getattr__",
            root,
        )

        generic_core_files = (
            Path(
                "src/maestro/sovereign/"
                "generic_descriptors.py"
            ),
            Path(
                "src/maestro/sovereign/"
                "generic_discovery.py"
            ),
            Path(
                "src/maestro/sovereign/"
                "generic_adapters.py"
            ),
            PAB_SOURCE,
        )

        for path in generic_core_files:
            with self.subTest(path=str(path)):
                lowered = path.read_text(
                    encoding="utf-8"
                ).lower()

                self.assertNotIn(
                    "ollama",
                    lowered,
                )


if __name__ == "__main__":
    unittest.main()
