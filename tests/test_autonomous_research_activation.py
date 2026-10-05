from __future__ import annotations

import ast
import hashlib
import inspect
import tempfile
import unittest
from pathlib import Path

from maestro.autonomous.runtime import (
    AutonomousRuntime,
)
from maestro.os.operating_system import (
    MaestroOperatingSystem,
)
from maestro.research.composition import (
    GovernedResearchComposition,
)
from maestro.research.provider_contracts import (
    ResearchCapability,
)
from maestro.research.redirects import (
    GovernedRedirectResponse,
    GovernedRedirectTransport,
)
from maestro.research.runtime_contracts import (
    ResearchRequest,
)
from maestro.research.source_access import (
    SourceAccessPolicy,
)
from maestro.research.transport import (
    SourceHTTPResponse,
)
from maestro.research.web_fetch import (
    GOVERNED_WEB_FETCH_PROVIDER_ID,
    GOVERNED_WEB_FETCH_TOOL_NAME,
    GovernedWebFetchBinding,
    build_governed_web_fetch_binding,
)


_POLICY = SourceAccessPolicy()


def response(
    url: str,
    *,
    body: bytes = b"OK",
) -> SourceHTTPResponse:
    return SourceHTTPResponse(
        target=_POLICY.prepare_url(
            url
        ),
        method="GET",
        status=200,
        content_type="text/plain",
        body=body,
        body_sha256=(
            hashlib.sha256(
                body
            ).hexdigest()
        ),
    )


class FakeRedirectTransport(
    GovernedRedirectTransport
):
    def __init__(
        self,
        result: GovernedRedirectResponse,
    ):
        self.result = result
        self.calls: list[
            tuple[str, str]
        ] = []

    def request(
        self,
        method: str,
        url: str,
    ) -> GovernedRedirectResponse:
        self.calls.append(
            (
                method,
                url,
            )
        )

        return self.result


def web_binding(
    *,
    body: bytes = b"OK",
) -> tuple[
    GovernedWebFetchBinding,
    FakeRedirectTransport,
]:
    transport = FakeRedirectTransport(
        GovernedRedirectResponse(
            response=response(
                "https://example.com/final",
                body=body,
            ),
            redirects=(),
        )
    )

    binding = (
        build_governed_web_fetch_binding(
            transport=transport
        )
    )

    return (
        binding,
        transport,
    )


class AutonomousResearchActivationTests(
    unittest.TestCase
):
    def test_default_runtime_keeps_web_research_off(
        self,
    ):
        with tempfile.TemporaryDirectory() as td:
            runtime = AutonomousRuntime(
                td
            )

            self.assertIsNone(
                runtime.research
            )

            with self.assertRaises(
                KeyError
            ):
                runtime.kernel.tools.spec(
                    GOVERNED_WEB_FETCH_TOOL_NAME
                )

    def test_binding_parameter_is_keyword_only(
        self,
    ):
        signature = inspect.signature(
            AutonomousRuntime
        )

        parameter = (
            signature.parameters[
                "web_research_binding"
            ]
        )

        self.assertIs(
            parameter.kind,
            inspect.Parameter.KEYWORD_ONLY,
        )

        self.assertIsNone(
            parameter.default
        )

        web, _ = web_binding()

        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(
                TypeError
            ):
                AutonomousRuntime(
                    td,
                    web,
                )

    def test_invalid_binding_fails_before_runtime_directory_creation(
        self,
    ):
        with tempfile.TemporaryDirectory() as td:
            runtime_dir = (
                Path(td)
                / "runtime"
            )

            self.assertFalse(
                runtime_dir.exists()
            )

            with self.assertRaises(
                TypeError
            ):
                AutonomousRuntime(
                    runtime_dir,
                    web_research_binding=(
                        object()
                    ),
                )

            self.assertFalse(
                runtime_dir.exists()
            )

    def test_explicit_binding_reuses_kernel_tools_and_firewall(
        self,
    ):
        web, transport = (
            web_binding()
        )

        with tempfile.TemporaryDirectory() as td:
            runtime = AutonomousRuntime(
                td,
                web_research_binding=web,
            )

            self.assertIsInstance(
                runtime.research,
                GovernedResearchComposition,
            )

            self.assertIs(
                runtime.research.tools,
                runtime.kernel.tools,
            )

            self.assertIs(
                runtime.research.runtime.tools,
                runtime.kernel.tools,
            )

            self.assertIs(
                runtime.kernel.tools.firewall,
                runtime.kernel.firewall,
            )

            self.assertIs(
                runtime.research.providers
                .descriptor(
                    GOVERNED_WEB_FETCH_PROVIDER_ID
                ),
                web.provider,
            )

            self.assertIs(
                runtime.kernel.tools.spec(
                    GOVERNED_WEB_FETCH_TOOL_NAME
                ),
                web.tool_spec,
            )

            self.assertEqual(
                transport.calls,
                [],
            )

    def test_explicit_runtime_research_executes_governed_fetch(
        self,
    ):
        body = (
            b"AUTONOMOUS-RX"
        )

        web, transport = (
            web_binding(
                body=body
            )
        )

        with tempfile.TemporaryDirectory() as td:
            runtime = AutonomousRuntime(
                td,
                web_research_binding=web,
            )

            result = (
                runtime.research
                .runtime
                .execute(
                    ResearchRequest(
                        task_id=(
                            "TASK-AUTONOMOUS-RX"
                        ),
                        capability=(
                            ResearchCapability.FETCH
                        ),
                        arguments={
                            "url": (
                                "https://example.com/start"
                            ),
                        },
                    )
                )
            )

            self.assertEqual(
                result.provider_id,
                GOVERNED_WEB_FETCH_PROVIDER_ID,
            )

            self.assertEqual(
                result.tool_name,
                GOVERNED_WEB_FETCH_TOOL_NAME,
            )

            self.assertEqual(
                result.output.body,
                body,
            )

            self.assertEqual(
                transport.calls,
                [
                    (
                        "GET",
                        "https://example.com/start",
                    )
                ],
            )

    def test_runtime_construction_does_not_perform_network_io(
        self,
    ):
        web, transport = (
            web_binding()
        )

        with tempfile.TemporaryDirectory() as td:
            runtime = AutonomousRuntime(
                td,
                web_research_binding=web,
            )

            self.assertIsNotNone(
                runtime.research
            )

            self.assertEqual(
                transport.calls,
                [],
            )

    def test_operating_system_default_remains_web_off(
        self,
    ):
        with tempfile.TemporaryDirectory() as td:
            operating_system = (
                MaestroOperatingSystem(
                    td
                )
            )

            self.assertIsNone(
                operating_system
                .runtime
                .research
            )

            with self.assertRaises(
                KeyError
            ):
                (
                    operating_system
                    .runtime
                    .kernel
                    .tools
                    .spec(
                        GOVERNED_WEB_FETCH_TOOL_NAME
                    )
                )

    def test_autonomous_runtime_has_no_hidden_web_authority(
        self,
    ):
        path = Path(
            "src/maestro/autonomous/runtime.py"
        )

        source = path.read_text(
            encoding="utf-8"
        )

        tree = ast.parse(
            source
        )

        forbidden_markers = (
            "enable_web",
            "build_governed_web_fetch_binding",
            "GovernedRedirectTransport",
            "GovernedHTTPTransport",
            "BoundSourceConnector",
            "GovernedSourceResolver",
        )

        for marker in forbidden_markers:
            self.assertNotIn(
                marker,
                source,
            )

        forbidden_network_roots = {
            "socket",
            "ssl",
            "http",
            "urllib",
            "requests",
            "httpx",
            "aiohttp",
        }

        for node in ast.walk(tree):
            if isinstance(
                node,
                ast.Import,
            ):
                for alias in node.names:
                    self.assertNotIn(
                        alias.name.split(
                            ".",
                            1,
                        )[0],
                        forbidden_network_roots,
                    )

            if isinstance(
                node,
                ast.ImportFrom,
            ):
                module = (
                    node.module or ""
                )

                self.assertNotIn(
                    module.split(
                        ".",
                        1,
                    )[0],
                    forbidden_network_roots,
                )


if __name__ == "__main__":
    unittest.main()
