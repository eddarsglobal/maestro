from __future__ import annotations

import ast
import unittest
from dataclasses import replace
from pathlib import Path

from maestro.research.provider_contracts import (
    ResearchCapability,
)
from maestro.research.unknown_technology_ingress import (
    GovernedUnknownTechnologyResearchIngress,
    UnknownTechnologyResearchIngressInvariantError,
)
from maestro.sovereign.generic_descriptors import (
    CapabilityDescriptor,
    GenericResourceDescriptor,
    HostDescriptor,
)
from maestro.sovereign.generic_discovery import (
    CapabilityObservation,
    GenericDiscoveryProjection,
    GenericHostDiscoveryProjector,
    HostDiscoveryObservation,
    ResourceObservation,
)


CONSTITUTION = Path(
    "docs/UNKNOWN_TECHNOLOGY_RESEARCH_INGRESS_CONSTITUTION.md"
)

INGRESS_SOURCE = Path(
    "src/maestro/research/unknown_technology_ingress.py"
)


def projection() -> GenericDiscoveryProjection:
    return GenericHostDiscoveryProjector.project(
        HostDiscoveryObservation(
            host_id="future-host",
            host_kind="unknown-future-host",
            locality="UNKNOWN",
            capabilities=(
                CapabilityObservation(
                    capability_id="future.compute.alpha",
                    domain="future-domain",
                    attributes={
                        "evidence_ref": "EVD-CAP-A",
                    },
                ),
                CapabilityObservation(
                    capability_id="future.semantic.beta",
                    domain="future-domain",
                    attributes={
                        "evidence_ref": "EVD-CAP-B",
                    },
                ),
            ),
            resources=(
                ResourceObservation(
                    resource_id="resource-z",
                    resource_kind="future-resource",
                    capability_ids=frozenset({
                        "future.semantic.beta",
                    }),
                    attributes={
                        "evidence_ref": "EVD-RES-Z",
                    },
                ),
                ResourceObservation(
                    resource_id="resource-a",
                    resource_kind="future-resource",
                    capability_ids=frozenset({
                        "future.compute.alpha",
                    }),
                    attributes={
                        "evidence_ref": "EVD-RES-A",
                    },
                ),
            ),
            attributes={
                "evidence_ref": "EVD-HOST",
            },
        )
    )


class UnknownTechnologyResearchIngressTests(
    unittest.TestCase
):
    def test_01_constitution_contains_all_ten_utr_laws(self):
        text = CONSTITUTION.read_text(encoding="utf-8")

        for number in range(1, 11):
            self.assertIn(
                f"UTR-{number:02d}",
                text,
            )

        self.assertIn("BMF-011", text)

    def test_02_generic_projection_enters_rx_adel_path(self):
        result = (
            GovernedUnknownTechnologyResearchIngress
            .build(projection())
        )

        self.assertEqual(result.size, 2)

        self.assertTrue(
            all(
                candidate.path == ("RX", "ADEL")
                for candidate in result.candidates
            )
        )

        self.assertTrue(
            all(
                candidate.research_capability
                is ResearchCapability.SEARCH
                for candidate in result.candidates
            )
        )

    def test_03_candidates_are_capability_first_and_deterministically_ordered(self):
        result = (
            GovernedUnknownTechnologyResearchIngress
            .build(projection())
        )

        observed = [
            (
                candidate.capability.capability_id,
                candidate.resource.resource_id,
            )
            for candidate in result.candidates
        ]

        self.assertEqual(
            observed,
            [
                (
                    "future.compute.alpha",
                    "resource-a",
                ),
                (
                    "future.semantic.beta",
                    "resource-z",
                ),
            ],
        )

        self.assertTrue(
            result.candidates[0].query.startswith(
                "Research capability "
            )
        )

    def test_04_descriptor_evidence_is_preserved(self):
        result = (
            GovernedUnknownTechnologyResearchIngress
            .build(projection())
        )

        payload = result.to_dict()["candidates"][0]

        self.assertEqual(
            payload["host"]["attributes"][
                "evidence_ref"
            ],
            "EVD-HOST",
        )
        self.assertEqual(
            payload["resource"]["attributes"][
                "evidence_ref"
            ],
            "EVD-RES-A",
        )
        self.assertEqual(
            payload["capability"]["attributes"][
                "evidence_ref"
            ],
            "EVD-CAP-A",
        )

    def test_05_candidate_identity_is_deterministic(self):
        first = (
            GovernedUnknownTechnologyResearchIngress
            .build(projection())
        )
        second = (
            GovernedUnknownTechnologyResearchIngress
            .build(projection())
        )

        self.assertEqual(
            first.to_dict(),
            second.to_dict(),
        )
        self.assertEqual(
            [
                item.candidate_id
                for item in first.candidates
            ],
            [
                item.candidate_id
                for item in second.candidates
            ],
        )

    def test_06_ingress_does_not_import_or_construct_research_request(self):
        tree = ast.parse(
            INGRESS_SOURCE.read_text(encoding="utf-8")
        )

        imported_names = set()
        called_names = set()

        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                imported_names.update(
                    alias.name
                    for alias in node.names
                )
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    called_names.add(node.func.id)

        self.assertNotIn(
            "ResearchRequest",
            imported_names,
        )
        self.assertNotIn(
            "ResearchRequest",
            called_names,
        )

    def test_07_all_authority_escalations_fail_closed(self):
        candidate = (
            GovernedUnknownTechnologyResearchIngress
            .build(projection())
            .candidates[0]
        )

        forbidden = (
            "research_request_materialized",
            "network_requested",
            "trust_asserted",
            "installation_requested",
            "activation_requested",
            "authorization_asserted",
            "execution_requested",
            "system_truth_asserted",
        )

        for field_name in forbidden:
            with self.subTest(field_name=field_name):
                with self.assertRaises(
                    UnknownTechnologyResearchIngressInvariantError
                ):
                    replace(
                        candidate,
                        **{field_name: True},
                    )

    def test_08_non_search_and_path_escalation_fail_closed(self):
        candidate = (
            GovernedUnknownTechnologyResearchIngress
            .build(projection())
            .candidates[0]
        )

        with self.assertRaises(
            UnknownTechnologyResearchIngressInvariantError
        ):
            replace(
                candidate,
                research_capability=
                ResearchCapability.FETCH,
            )

        with self.assertRaises(
            UnknownTechnologyResearchIngressInvariantError
        ):
            replace(
                candidate,
                path=("RX", "EXECUTION"),
            )

    def test_09_projection_integrity_mismatches_fail_closed(self):
        valid = projection()

        wrong_host_resource = GenericResourceDescriptor(
            resource_id="wrong-host-resource",
            resource_kind="future-resource",
            host_id="different-host",
            capability_ids=frozenset({
                "future.compute.alpha",
            }),
        )

        wrong_host_projection = GenericDiscoveryProjection(
            host=valid.host,
            capabilities=valid.capabilities,
            resources=(wrong_host_resource,),
        )

        with self.assertRaises(
            UnknownTechnologyResearchIngressInvariantError
        ):
            (
                GovernedUnknownTechnologyResearchIngress
                .build(wrong_host_projection)
            )

        missing_capability = GenericResourceDescriptor(
            resource_id="missing-capability-resource",
            resource_kind="future-resource",
            host_id=valid.host.host_id,
            capability_ids=frozenset({
                "future.not-declared",
            }),
        )

        missing_projection = GenericDiscoveryProjection(
            host=valid.host,
            capabilities=valid.capabilities,
            resources=(missing_capability,),
        )

        with self.assertRaises(
            UnknownTechnologyResearchIngressInvariantError
        ):
            (
                GovernedUnknownTechnologyResearchIngress
                .build(missing_projection)
            )

    def test_10_ingress_is_passive_and_non_authoritative(self):
        tree = ast.parse(
            INGRESS_SOURCE.read_text(encoding="utf-8")
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

        result = (
            GovernedUnknownTechnologyResearchIngress
            .build(projection())
        )

        for candidate in result.candidates:
            self.assertFalse(
                candidate.research_request_materialized
            )
            self.assertFalse(candidate.network_requested)
            self.assertFalse(candidate.trust_asserted)
            self.assertFalse(
                candidate.installation_requested
            )
            self.assertFalse(
                candidate.activation_requested
            )
            self.assertFalse(
                candidate.authorization_asserted
            )
            self.assertFalse(
                candidate.execution_requested
            )
            self.assertFalse(
                candidate.system_truth_asserted
            )


if __name__ == "__main__":
    unittest.main()
