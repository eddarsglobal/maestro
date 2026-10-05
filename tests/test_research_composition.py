from __future__ import annotations

import ast
import hashlib
import unittest
from pathlib import Path

from maestro.enums import (
    CouncilId,
)
from maestro.research.composition import (
    GOVERNED_RESEARCH_COMPOSITION_VERSION,
    GovernedResearchComposition,
    compose_governed_web_research,
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
from maestro.tools.registry import (
    ToolRegistry,
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


def binding(
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

    return (
        build_governed_web_fetch_binding(
            transport=transport
        ),
        transport,
    )


class GovernedResearchCompositionTests(
    unittest.TestCase
):
    def test_registry_has_no_web_tool_before_explicit_composition(
        self,
    ):
        tools = ToolRegistry()

        with self.assertRaises(
            KeyError
        ):
            tools.spec(
                GOVERNED_WEB_FETCH_TOOL_NAME
            )

    def test_composition_reuses_exact_tool_registry(
        self,
    ):
        tools = ToolRegistry()

        web_binding, _ = binding()

        composition = (
            compose_governed_web_research(
                tools=tools,
                binding=web_binding,
            )
        )

        self.assertIsInstance(
            composition,
            GovernedResearchComposition,
        )

        self.assertIs(
            composition.tools,
            tools,
        )

        self.assertIs(
            composition.runtime.tools,
            tools,
        )

        self.assertIs(
            composition.tools.firewall,
            tools.firewall,
        )

    def test_composition_registers_exact_provider_and_tool(
        self,
    ):
        tools = ToolRegistry()

        web_binding, _ = binding()

        composition = (
            compose_governed_web_research(
                tools=tools,
                binding=web_binding,
            )
        )

        descriptor = (
            composition.providers.descriptor(
                GOVERNED_WEB_FETCH_PROVIDER_ID
            )
        )

        self.assertIs(
            descriptor,
            web_binding.provider,
        )

        self.assertIs(
            tools.spec(
                GOVERNED_WEB_FETCH_TOOL_NAME
            ),
            web_binding.tool_spec,
        )

        self.assertEqual(
            descriptor.tool_name_for(
                ResearchCapability.FETCH
            ),
            GOVERNED_WEB_FETCH_TOOL_NAME,
        )

    def test_composed_runtime_executes_fetch(
        self,
    ):
        body = b"COMPOSED-RUNTIME"

        tools = ToolRegistry()

        web_binding, transport = (
            binding(
                body=body
            )
        )

        composition = (
            compose_governed_web_research(
                tools=tools,
                binding=web_binding,
            )
        )

        result = (
            composition.runtime.execute(
                ResearchRequest(
                    task_id=(
                        "TASK-RX03D2A"
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

    def test_non_tool_registry_is_rejected_before_activation(
        self,
    ):
        web_binding, _ = binding()

        with self.assertRaises(
            TypeError
        ):
            compose_governed_web_research(
                tools=object(),  # type: ignore[arg-type]
                binding=web_binding,
            )

    def test_non_binding_is_rejected_before_activation(
        self,
    ):
        tools = ToolRegistry()

        with self.assertRaises(
            TypeError
        ):
            compose_governed_web_research(
                tools=tools,
                binding=object(),  # type: ignore[arg-type]
            )

        with self.assertRaises(
            KeyError
        ):
            tools.spec(
                GOVERNED_WEB_FETCH_TOOL_NAME
            )

    def test_duplicate_tool_fails_closed_without_replacement(
        self,
    ):
        tools = ToolRegistry()

        web_binding, _ = binding()

        tools.register(
            web_binding.tool_spec,
            lambda url: {
                "existing": url,
            },
        )

        with self.assertRaises(
            ValueError
        ):
            compose_governed_web_research(
                tools=tools,
                binding=web_binding,
            )

        output = tools.invoke(
            task_id="TASK-EXISTING",
            actor=CouncilId.RX,
            tool_name=(
                GOVERNED_WEB_FETCH_TOOL_NAME
            ),
            arguments={
                "url": (
                    "https://example.com/"
                ),
            },
        )

        self.assertEqual(
            output,
            {
                "existing": (
                    "https://example.com/"
                )
            },
        )

    def test_composition_module_contains_no_hidden_activation_path(
        self,
    ):
        path = Path(
            "src/maestro/research/composition.py"
        )

        source = path.read_text(
            encoding="utf-8"
        )

        tree = ast.parse(
            source
        )

        forbidden_imports = (
            "maestro.runtime.kernel",
            "maestro.autonomous",
            "maestro_gateway",
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
                    self.assertFalse(
                        alias.name.startswith(
                            forbidden_imports
                        )
                    )

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

                self.assertFalse(
                    module.startswith(
                        forbidden_imports
                    )
                )

                self.assertNotIn(
                    module.split(
                        ".",
                        1,
                    )[0],
                    forbidden_network_roots,
                )

        self.assertNotIn(
            "build_governed_web_fetch_binding",
            source,
        )

        self.assertNotIn(
            "GovernedRedirectTransport",
            source,
        )

        self.assertEqual(
            GOVERNED_RESEARCH_COMPOSITION_VERSION,
            "RX0.3D2A",
        )


if __name__ == "__main__":
    unittest.main()
