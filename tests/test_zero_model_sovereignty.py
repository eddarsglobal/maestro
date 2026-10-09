from __future__ import annotations

import ast
import http.client
import inspect
import socket
import subprocess
import tempfile
import unittest
import urllib.request
from pathlib import Path
from unittest.mock import patch

from maestro import ProductionGenesisSystem


CONSTITUTION = Path("docs/ZERO_MODEL_SOVEREIGNTY_CONSTITUTION.md")
GENESIS_SYSTEM = Path("src/maestro/genesis/system.py")


class ForbiddenExternalEffect(RuntimeError):
    pass


def forbidden(*args, **kwargs):
    raise ForbiddenExternalEffect(
        "External effect attempted during zero-model sovereign boot."
    )


def boot_zero_model():
    with tempfile.TemporaryDirectory() as td:
        runtime = Path(td) / "runtime"

        with (
            patch("socket.create_connection", forbidden),
            patch.object(socket.socket, "connect", forbidden),
            patch("urllib.request.urlopen", forbidden),
            patch.object(http.client.HTTPConnection, "connect", forbidden),
            patch.object(http.client.HTTPSConnection, "connect", forbidden),
            patch("subprocess.Popen", forbidden),
            patch("subprocess.run", forbidden),
        ):
            system = ProductionGenesisSystem(runtime)
            return system.start()


class ZeroModelSovereigntyTests(unittest.TestCase):
    def test_01_constitution_contains_all_ten_zms_laws(self):
        text = CONSTITUTION.read_text(encoding="utf-8")
        for number in range(1, 11):
            self.assertIn(f"ZMS-{number:02d}", text)

    def test_02_constitution_separates_bmf005_from_bmf006(self):
        text = CONSTITUTION.read_text(encoding="utf-8")
        self.assertIn("BMF-005 = Zero-resource sovereign boot", text)
        self.assertIn(
            "BMF-006 = Explicit degraded intelligence capability state",
            text,
        )

    def test_03_genesis_has_no_direct_provider_or_network_import(self):
        tree = ast.parse(
            GENESIS_SYSTEM.read_text(encoding="utf-8")
        )

        imports = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imports.add(node.module)

        forbidden_imports = {
            "socket",
            "requests",
            "httpx",
            "urllib.request",
        }

        self.assertTrue(imports.isdisjoint(forbidden_imports))
        self.assertFalse(
            any(name.startswith("maestro.providers") for name in imports)
        )

    def test_04_genesis_constructor_requires_no_provider_identity(self):
        signature = inspect.signature(ProductionGenesisSystem)
        parameter_names = {
            name.lower()
            for name in signature.parameters
        }

        forbidden_names = {
            "provider",
            "provider_id",
            "model",
            "model_id",
            "runtime_provider",
            "inference_provider",
        }

        self.assertTrue(parameter_names.isdisjoint(forbidden_names))

    def test_05_zero_model_boot_reports_ready(self):
        result = boot_zero_model()
        self.assertEqual(result.get("status"), "READY")

    def test_06_zero_model_boot_preserves_kernel_ok(self):
        result = boot_zero_model()
        self.assertEqual(result["boot"]["kernel"], "OK")

    def test_07_zero_model_boot_preserves_registry_ok(self):
        result = boot_zero_model()
        self.assertEqual(result["boot"]["registry"], "OK")

    def test_08_zero_model_boot_preserves_unique_variables(self):
        result = boot_zero_model()
        self.assertIs(result["boot"]["unique_variables"], True)

    def test_09_zero_model_boot_performs_no_external_recovery_work(self):
        result = boot_zero_model()
        recovery = result["runtime_recovery"]
        self.assertEqual(recovery["processed"], 0)
        self.assertEqual(recovery["committed"], 0)
        self.assertEqual(recovery["aborted"], 0)
        self.assertEqual(recovery["blocked"], 0)

    def test_10_zero_model_boot_does_not_expand_authority(self):
        result = boot_zero_model()

        forbidden_authority_keys = {
            "authorized",
            "authorization",
            "authority",
            "promotion_authorized",
            "activation_authorized",
            "execution_authorized",
            "truth",
        }

        def walk(value):
            if isinstance(value, dict):
                for key, child in value.items():
                    yield str(key).lower()
                    yield from walk(child)
            elif isinstance(value, (list, tuple)):
                for child in value:
                    yield from walk(child)

        observed_keys = set(walk(result))
        self.assertTrue(
            observed_keys.isdisjoint(forbidden_authority_keys)
        )


if __name__ == "__main__":
    unittest.main()
