from __future__ import annotations

import http.client
import socket
import subprocess
import tempfile
import unittest
import urllib.request
from pathlib import Path
from unittest.mock import patch

from maestro import ProductionGenesisSystem
from maestro.sovereign import IntelligenceCapability


CONSTITUTION = Path(
    "docs/SOVEREIGN_DEGRADED_INTELLIGENCE_CONSTITUTION.md"
)


class ForbiddenExternalEffect(RuntimeError):
    pass


def forbidden(*args, **kwargs):
    raise ForbiddenExternalEffect(
        "External effect attempted during sovereign degraded boot."
    )


def boot_zero_resource():
    with tempfile.TemporaryDirectory() as td:
        with (
            patch("socket.create_connection", forbidden),
            patch.object(socket.socket, "connect", forbidden),
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
            system = ProductionGenesisSystem(
                Path(td) / "runtime"
            )
            result = system.start()
            state = system.sovereign_intelligence.degraded.assess(
                system.sovereign_intelligence.registry
            )
            return result, state


class SovereignDegradedIntelligenceTests(unittest.TestCase):
    def test_01_constitution_contains_all_ten_sdi_laws(self):
        text = CONSTITUTION.read_text(encoding="utf-8")
        for number in range(1, 11):
            self.assertIn(f"SDI-{number:02d}", text)

    def test_02_constitution_preserves_bmf005_bmf006_boundary(self):
        text = CONSTITUTION.read_text(encoding="utf-8")
        self.assertIn("BMF-005", text)
        self.assertIn("BMF-006", text)
        self.assertIn("DEGRADED_INTELLIGENCE", text)
        self.assertIn("DEGRADED_CORE", text)

    def test_03_zero_resource_core_remains_ready(self):
        result, _ = boot_zero_resource()
        self.assertEqual(result["status"], "READY")

    def test_04_zero_resource_state_is_explicitly_sovereign_degraded(self):
        result, _ = boot_zero_resource()
        intelligence = result["intelligence"]
        self.assertEqual(
            intelligence["state"],
            "SOVEREIGN_DEGRADED",
        )
        self.assertEqual(
            intelligence["level"],
            "DETERMINISTIC_ONLY",
        )

    def test_05_zero_resource_counts_are_explicit(self):
        result, _ = boot_zero_resource()
        intelligence = result["intelligence"]
        self.assertEqual(
            intelligence["registered_resources"],
            0,
        )
        self.assertEqual(
            intelligence["available_resources"],
            0,
        )

    def test_06_zero_resource_capabilities_are_explicit(self):
        result, _ = boot_zero_resource()
        intelligence = result["intelligence"]
        expected = sorted(
            capability.value
            for capability in IntelligenceCapability
        )
        self.assertEqual(
            intelligence["available_capabilities"],
            [],
        )
        self.assertEqual(
            intelligence["unavailable_capabilities"],
            expected,
        )

    def test_07_genesis_reuses_sovereign_degraded_assessment(self):
        result, degraded = boot_zero_resource()
        intelligence = result["intelligence"]
        self.assertEqual(
            intelligence["level"],
            degraded.level.value,
        )
        self.assertEqual(
            intelligence["available_capabilities"],
            sorted(degraded.available_capabilities),
        )
        self.assertEqual(
            intelligence["reason"],
            degraded.reason,
        )

    def test_08_zero_resource_boot_needs_no_external_effect(self):
        result, _ = boot_zero_resource()
        self.assertEqual(result["status"], "READY")
        self.assertEqual(
            result["intelligence"]["available_resources"],
            0,
        )

    def test_09_reporting_does_not_assert_authority(self):
        result, _ = boot_zero_resource()

        forbidden_keys = {
            "authorized",
            "authorization",
            "authority",
            "ay_verdict",
            "ex_authorization",
            "promotion_authority",
            "activation_authority",
            "execution_authority",
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

        observed = set(keys(result))
        self.assertTrue(observed.isdisjoint(forbidden_keys))

    def test_10_zero_resource_intelligence_report_is_deterministic(self):
        first, _ = boot_zero_resource()
        second, _ = boot_zero_resource()
        self.assertEqual(
            first["intelligence"],
            second["intelligence"],
        )


if __name__ == "__main__":
    unittest.main()
