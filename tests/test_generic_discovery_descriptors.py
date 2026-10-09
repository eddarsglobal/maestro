from __future__ import annotations

import ast
import http.client
import socket
import subprocess
import unittest
import urllib.request
from dataclasses import FrozenInstanceError, fields
from pathlib import Path
from unittest.mock import patch

from maestro.sovereign.generic_descriptors import (
    CapabilityDescriptor,
    GenericResourceDescriptor,
    HostDescriptor,
)
from maestro.sovereign.generic_discovery import (
    CapabilityObservation,
    GenericHostDiscoveryProjector,
    HostDiscoveryObservation,
    ResourceObservation,
)


CONSTITUTION = Path(
    "docs/GENERIC_DISCOVERY_DESCRIPTORS_CONSTITUTION.md"
)

DESCRIPTOR_SOURCE = Path(
    "src/maestro/sovereign/generic_descriptors.py"
)

DISCOVERY_SOURCE = Path(
    "src/maestro/sovereign/generic_discovery.py"
)


def observation() -> HostDiscoveryObservation:
    return HostDiscoveryObservation(
        host_id="future-host",
        host_kind="unknown-future-host",
        locality="LOCAL",
        capabilities=(
            CapabilityObservation(
                capability_id="future.compute.beta",
                domain="future-domain",
            ),
            CapabilityObservation(
                capability_id="future.semantic.alpha",
                domain="future-domain",
            ),
        ),
        resources=(
            ResourceObservation(
                resource_id="resource-z",
                resource_kind="unknown-resource",
                capability_ids=frozenset({
                    "future.semantic.alpha",
                }),
            ),
            ResourceObservation(
                resource_id="resource-a",
                resource_kind="unknown-resource",
                capability_ids=frozenset({
                    "future.compute.beta",
                }),
            ),
        ),
    )


class GenericDiscoveryDescriptorTests(unittest.TestCase):
    def test_01_constitution_contains_all_ten_gdr_laws(self):
        text = CONSTITUTION.read_text(encoding="utf-8")

        for number in range(1, 11):
            self.assertIn(
                f"GDR-{number:02d}",
                text,
            )

    def test_02_generic_resource_requires_no_provider_model_or_runtime(self):
        names = {
            field.name
            for field in fields(
                GenericResourceDescriptor
            )
        }

        self.assertNotIn("provider_id", names)
        self.assertNotIn("model_id", names)
        self.assertNotIn("runtime_id", names)

    def test_03_unknown_future_capability_is_representable(self):
        capability = CapabilityDescriptor(
            capability_id="technology.unknown.2099",
            domain="future-domain",
        )

        self.assertEqual(
            capability.capability_id,
            "technology.unknown.2099",
        )

    def test_04_host_observation_produces_all_generic_descriptors(self):
        projection = (
            GenericHostDiscoveryProjector.project(
                observation()
            )
        )

        self.assertIsInstance(
            projection.host,
            HostDescriptor,
        )

        self.assertTrue(
            all(
                isinstance(
                    item,
                    CapabilityDescriptor,
                )
                for item in projection.capabilities
            )
        )

        self.assertTrue(
            all(
                isinstance(
                    item,
                    GenericResourceDescriptor,
                )
                for item in projection.resources
            )
        )

    def test_05_projection_order_is_deterministic(self):
        first = GenericHostDiscoveryProjector.project(
            observation()
        )
        second = GenericHostDiscoveryProjector.project(
            observation()
        )

        self.assertEqual(
            first.to_dict(),
            second.to_dict(),
        )

        self.assertEqual(
            [
                item.resource_id
                for item in first.resources
            ],
            ["resource-a", "resource-z"],
        )

    def test_06_duplicate_capability_fails_closed(self):
        row = HostDiscoveryObservation(
            host_id="duplicate-capability",
            capabilities=(
                CapabilityObservation(
                    capability_id="future.alpha",
                ),
                CapabilityObservation(
                    capability_id="future.alpha",
                ),
            ),
        )

        with self.assertRaises(ValueError):
            GenericHostDiscoveryProjector.project(row)

    def test_07_duplicate_resource_fails_closed(self):
        row = HostDiscoveryObservation(
            host_id="duplicate-resource",
            capabilities=(
                CapabilityObservation(
                    capability_id="future.alpha",
                ),
            ),
            resources=(
                ResourceObservation(
                    resource_id="resource-x",
                    capability_ids=frozenset({
                        "future.alpha",
                    }),
                ),
                ResourceObservation(
                    resource_id="resource-x",
                    capability_ids=frozenset({
                        "future.alpha",
                    }),
                ),
            ),
        )

        with self.assertRaises(ValueError):
            GenericHostDiscoveryProjector.project(row)

    def test_08_undeclared_resource_capability_fails_closed(self):
        row = HostDiscoveryObservation(
            host_id="undeclared-capability",
            resources=(
                ResourceObservation(
                    resource_id="resource-x",
                    capability_ids=frozenset({
                        "future.missing",
                    }),
                ),
            ),
        )

        with self.assertRaises(ValueError):
            GenericHostDiscoveryProjector.project(row)

    def test_09_projection_has_no_external_side_effect_requirement(self):
        def forbidden(*args, **kwargs):
            raise AssertionError(
                "external side effect attempted"
            )

        with (
            patch("socket.create_connection", forbidden),
            patch.object(
                socket.socket,
                "connect",
                forbidden,
            ),
            patch("urllib.request.urlopen", forbidden),
            patch.object(
                http.client.HTTPConnection,
                "connect",
                forbidden,
            ),
            patch.object(
                http.client.HTTPSConnection,
                "connect",
                forbidden,
            ),
            patch("subprocess.Popen", forbidden),
            patch("subprocess.run", forbidden),
        ):
            projection = (
                GenericHostDiscoveryProjector.project(
                    observation()
                )
            )

        self.assertEqual(
            projection.host.host_id,
            "future-host",
        )

    def test_10_generic_discovery_is_passive_and_non_authoritative(self):
        forbidden_imports = {
            "socket",
            "subprocess",
            "requests",
            "httpx",
            "urllib",
            "urllib.request",
            "aiohttp",
        }

        for path in (
            DESCRIPTOR_SOURCE,
            DISCOVERY_SOURCE,
        ):
            tree = ast.parse(
                path.read_text(encoding="utf-8")
            )

            imports = set()

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    imports.update(
                        alias.name
                        for alias in node.names
                    )
                elif isinstance(
                    node,
                    ast.ImportFrom,
                ):
                    if node.module:
                        imports.add(node.module)

            bad = {
                name
                for name in imports
                if any(
                    name == forbidden
                    or name.startswith(
                        forbidden + "."
                    )
                    for forbidden
                    in forbidden_imports
                )
            }

            self.assertFalse(bad)

        projection = (
            GenericHostDiscoveryProjector.project(
                observation()
            )
        )

        authority_keys = {
            "authorized",
            "authorization",
            "authority",
            "ay_verdict",
            "ex_authorization",
            "activation_authority",
            "execution_authority",
            "promotion_authority",
            "system_truth",
        }

        def keys(value):
            if isinstance(value, dict):
                for key, child in value.items():
                    yield str(key).lower()
                    yield from keys(child)
            elif isinstance(value, list):
                for child in value:
                    yield from keys(child)

        observed = set(
            keys(projection.to_dict())
        )

        self.assertTrue(
            observed.isdisjoint(
                authority_keys
            )
        )


if __name__ == "__main__":
    unittest.main()
