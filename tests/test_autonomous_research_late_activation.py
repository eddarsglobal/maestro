from __future__ import annotations

import tempfile
import unittest

from pathlib import Path

from maestro.autonomous.runtime import (
    AutonomousRuntime,
)
from maestro.research.web_fetch import (
    GOVERNED_WEB_FETCH_TOOL_NAME,
    build_governed_web_fetch_binding,
)


class AutonomousResearchLateActivationTests(
    unittest.TestCase
):
    def test_default_runtime_remains_web_off(
        self,
    ):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)

            runtime = AutonomousRuntime(
                root
            )

            self.assertIsNone(
                runtime.research
            )

            self.assertIsNone(
                runtime.research_evidence
            )

            self.assertFalse(
                (
                    root
                    / "research_evidence.sqlite3"
                ).exists()
            )

            with self.assertRaises(
                KeyError
            ):
                runtime.kernel.tools.spec(
                    GOVERNED_WEB_FETCH_TOOL_NAME
                )

    def test_explicit_late_activation_uses_kernel_authority(
        self,
    ):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)

            runtime = AutonomousRuntime(
                root
            )

            binding = (
                build_governed_web_fetch_binding()
            )

            runtime.activate_web_research(
                binding
            )

            self.assertIsNotNone(
                runtime.research
            )

            self.assertIsNotNone(
                runtime.research_evidence
            )

            self.assertIs(
                runtime.research.tools,
                runtime.kernel.tools,
            )

            self.assertIs(
                runtime.kernel.tools.firewall,
                runtime.kernel.firewall,
            )

            self.assertIs(
                runtime.kernel.tools.spec(
                    GOVERNED_WEB_FETCH_TOOL_NAME
                ),
                binding.tool_spec,
            )

            self.assertTrue(
                (
                    root
                    / "research_evidence.sqlite3"
                ).exists()
            )

    def test_invalid_late_activation_fails_closed(
        self,
    ):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)

            runtime = AutonomousRuntime(
                root
            )

            with self.assertRaises(
                TypeError
            ):
                runtime.activate_web_research(
                    object()
                )

            self.assertIsNone(
                runtime.research
            )

            self.assertIsNone(
                runtime.research_evidence
            )

            self.assertFalse(
                (
                    root
                    / "research_evidence.sqlite3"
                ).exists()
            )

    def test_second_activation_is_rejected(
        self,
    ):
        with tempfile.TemporaryDirectory() as td:
            runtime = AutonomousRuntime(
                td
            )

            first = (
                build_governed_web_fetch_binding()
            )

            runtime.activate_web_research(
                first
            )

            original_research = (
                runtime.research
            )

            original_store = (
                runtime.research_evidence
            )

            with self.assertRaises(
                RuntimeError
            ):
                runtime.activate_web_research(
                    build_governed_web_fetch_binding()
                )

            self.assertIs(
                runtime.research,
                original_research,
            )

            self.assertIs(
                runtime.research_evidence,
                original_store,
            )

            self.assertIs(
                runtime.kernel.tools.spec(
                    GOVERNED_WEB_FETCH_TOOL_NAME
                ),
                first.tool_spec,
            )


if __name__ == "__main__":
    unittest.main()
