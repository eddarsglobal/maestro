from __future__ import annotations

import ast
import hashlib
import unittest
from pathlib import Path

from maestro.enums import (
    CouncilId,
    SideEffectLevel,
)
from maestro.research.provider_contracts import (
    ResearchCapability,
)
from maestro.research.provider_registry import (
    ResearchProviderRegistry,
)
from maestro.research.redirects import (
    GovernedRedirectResponse,
    GovernedRedirectTransport,
    SourceRedirectHop,
)
from maestro.research.runtime import (
    GovernedResearchRuntime,
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
    GOVERNED_WEB_FETCH_CAPABILITY,
    GOVERNED_WEB_FETCH_PROVIDER_BINDING,
    GOVERNED_WEB_FETCH_PROVIDER_ID,
    GOVERNED_WEB_FETCH_TOOL_NAME,
    GOVERNED_WEB_FETCH_VERSION,
    GovernedWebFetchResult,
    GovernedWebFetchTool,
    build_governed_web_fetch_binding,
)
from maestro.tools.registry import (
    ToolRegistry,
)


_POLICY = SourceAccessPolicy()


def response(
    url: str,
    *,
    body: bytes = b"BODY",
    status: int = 200,
    content_type: (
        str | None
    ) = "text/plain",
    method: str = "GET",
) -> SourceHTTPResponse:
    return SourceHTTPResponse(
        target=_POLICY.prepare_url(
            url
        ),
        method=method,
        status=status,
        content_type=content_type,
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
        *,
        result: (
            GovernedRedirectResponse
            | None
        ) = None,
        error: Exception | None = None,
    ):
        self.result = result
        self.error = error
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

        if self.error is not None:
            raise self.error

        if self.result is None:
            raise AssertionError(
                "Synthetic result missing."
            )

        return self.result


class GovernedWebFetchTests(
    unittest.TestCase
):
    def test_binding_contract_is_fetch_only_rx_a0(
        self,
    ):
        binding = (
            build_governed_web_fetch_binding(
                transport=(
                    FakeRedirectTransport(
                        result=(
                            GovernedRedirectResponse(
                                response=response(
                                    "https://example.com/"
                                ),
                                redirects=(),
                            )
                        )
                    )
                )
            )
        )

        self.assertEqual(
            binding.provider.provider_id,
            GOVERNED_WEB_FETCH_PROVIDER_ID,
        )

        self.assertEqual(
            binding.provider.capabilities,
            frozenset(
                {
                    ResearchCapability.FETCH,
                }
            ),
        )

        self.assertEqual(
            binding.provider.tool_name_for(
                ResearchCapability.FETCH
            ),
            GOVERNED_WEB_FETCH_TOOL_NAME,
        )

        self.assertEqual(
            binding.tool_spec.name,
            GOVERNED_WEB_FETCH_TOOL_NAME,
        )

        self.assertEqual(
            binding.tool_spec.capabilities,
            (
                GOVERNED_WEB_FETCH_CAPABILITY,
                GOVERNED_WEB_FETCH_PROVIDER_BINDING,
            ),
        )

        self.assertEqual(
            binding.tool_spec.allowed_councils,
            frozenset(
                {
                    CouncilId.RX,
                }
            ),
        )

        self.assertIs(
            binding.tool_spec.side_effect_level,
            SideEffectLevel.A0_READ_ONLY,
        )

        self.assertFalse(
            binding.tool_spec
            .requires_policy_approval
        )

        self.assertFalse(
            binding.tool_spec
            .requires_human_approval
        )

        self.assertEqual(
            binding.provider.metadata[
                "version"
            ],
            GOVERNED_WEB_FETCH_VERSION,
        )

    def test_default_tool_uses_governed_redirect_transport(
        self,
    ):
        tool = GovernedWebFetchTool()

        self.assertIsInstance(
            tool.transport,
            GovernedRedirectTransport,
        )

    def test_non_governed_transport_is_rejected(
        self,
    ):
        with self.assertRaises(
            TypeError
        ):
            GovernedWebFetchTool(
                transport=object()  # type: ignore[arg-type]
            )

    def test_fetch_calls_only_get_once(
        self,
    ):
        final = GovernedRedirectResponse(
            response=response(
                "https://example.com/"
            ),
            redirects=(),
        )

        transport = FakeRedirectTransport(
            result=final
        )

        tool = GovernedWebFetchTool(
            transport
        )

        tool(
            "https://example.com/"
        )

        self.assertEqual(
            transport.calls,
            [
                (
                    "GET",
                    "https://example.com/",
                )
            ],
        )

    def test_fetch_preserves_response_contract(
        self,
    ):
        body = b"HELLO"

        final = GovernedRedirectResponse(
            response=response(
                "https://example.com/final",
                body=body,
                status=203,
                content_type="text/plain",
            ),
            redirects=(),
        )

        result = GovernedWebFetchTool(
            FakeRedirectTransport(
                result=final
            )
        )(
            "https://example.com/final"
        )

        self.assertIsInstance(
            result,
            GovernedWebFetchResult,
        )

        self.assertEqual(
            result.final_url,
            "https://example.com/final",
        )

        self.assertEqual(
            result.method,
            "GET",
        )

        self.assertEqual(
            result.status,
            203,
        )

        self.assertEqual(
            result.content_type,
            "text/plain",
        )

        self.assertEqual(
            result.body,
            body,
        )

        self.assertEqual(
            result.body_size,
            len(body),
        )

        self.assertEqual(
            result.body_sha256,
            hashlib.sha256(
                body
            ).hexdigest(),
        )

    def test_redirect_provenance_is_preserved(
        self,
    ):
        hop = SourceRedirectHop(
            status=302,
            source_url=(
                "https://example.com/a"
            ),
            target_url=(
                "https://example.com/b"
            ),
        )

        final = GovernedRedirectResponse(
            response=response(
                "https://example.com/b"
            ),
            redirects=(
                hop,
            ),
        )

        result = GovernedWebFetchTool(
            FakeRedirectTransport(
                result=final
            )
        )(
            "https://example.com/a"
        )

        self.assertEqual(
            result.redirects,
            (
                hop,
            ),
        )

        self.assertIs(
            result.redirects[0],
            hop,
        )

    def test_non_string_url_rejected_before_transport(
        self,
    ):
        transport = FakeRedirectTransport(
            result=(
                GovernedRedirectResponse(
                    response=response(
                        "https://example.com/"
                    ),
                    redirects=(),
                )
            )
        )

        tool = GovernedWebFetchTool(
            transport
        )

        with self.assertRaises(
            TypeError
        ):
            tool(123)  # type: ignore[arg-type]

        self.assertEqual(
            transport.calls,
            [],
        )

    def test_runtime_fetch_uses_governed_binding(
        self,
    ):
        body = b"RUNTIME BODY"

        transport = FakeRedirectTransport(
            result=(
                GovernedRedirectResponse(
                    response=response(
                        "https://example.com/final",
                        body=body,
                    ),
                    redirects=(
                        SourceRedirectHop(
                            301,
                            "https://example.com/start",
                            "https://example.com/final",
                        ),
                    ),
                )
            )
        )

        binding = (
            build_governed_web_fetch_binding(
                transport=transport
            )
        )

        providers = (
            ResearchProviderRegistry()
        )

        tools = ToolRegistry()

        providers.register(
            binding.provider
        )

        tools.register(
            binding.tool_spec,
            binding.handler,
        )

        runtime = GovernedResearchRuntime(
            providers,
            tools,
        )

        result = runtime.execute(
            ResearchRequest(
                task_id="TASK-WEB-FETCH",
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
            result.output.final_url,
            "https://example.com/final",
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

    def test_tool_history_does_not_retain_url_or_body(
        self,
    ):
        secret_url = (
            "https://example.com/"
            "?token=RX03D_URL_SECRET"
        )

        body = (
            b"RX03D_BODY_SECRET"
        )

        binding = (
            build_governed_web_fetch_binding(
                transport=(
                    FakeRedirectTransport(
                        result=(
                            GovernedRedirectResponse(
                                response=response(
                                    secret_url,
                                    body=body,
                                ),
                                redirects=(),
                            )
                        )
                    )
                )
            )
        )

        tools = ToolRegistry()

        tools.register(
            binding.tool_spec,
            binding.handler,
        )

        result = tools.invoke(
            task_id=(
                "TASK-RX03D-PRIVACY"
            ),
            actor=CouncilId.RX,
            tool_name=(
                binding.tool_spec.name
            ),
            arguments={
                "url": secret_url,
            },
        )

        self.assertEqual(
            result.body,
            body,
        )

        retained = repr(
            (
                tools.history,
                tools.last_invocation_receipt(),
            )
        )

        self.assertNotIn(
            secret_url,
            retained,
        )

        self.assertNotIn(
            "RX03D_URL_SECRET",
            retained,
        )

        self.assertNotIn(
            "RX03D_BODY_SECRET",
            retained,
        )

    def test_module_has_no_direct_network_or_promotion_imports(
        self,
    ):
        path = Path(
            "src/maestro/research/web_fetch.py"
        )

        tree = ast.parse(
            path.read_text(
                encoding="utf-8"
            )
        )

        forbidden_roots = {
            "socket",
            "ssl",
            "http",
            "urllib",
            "requests",
            "httpx",
            "aiohttp",
        }

        forbidden_maestro_prefixes = (
            "maestro.evidence",
            "maestro.academy",
            "maestro.adaptive",
            "maestro.governed_activation",
            "maestro.outcome_governed_adaptation",
        )

        for node in ast.walk(tree):
            if isinstance(
                node,
                ast.Import,
            ):
                for alias in node.names:
                    root = (
                        alias.name.split(
                            ".",
                            1,
                        )[0]
                    )

                    self.assertNotIn(
                        root,
                        forbidden_roots,
                    )

            if isinstance(
                node,
                ast.ImportFrom,
            ):
                module = (
                    node.module or ""
                )

                root = module.split(
                    ".",
                    1,
                )[0]

                self.assertNotIn(
                    root,
                    forbidden_roots,
                )

                self.assertFalse(
                    any(
                        module.startswith(
                            prefix
                        )
                        for prefix
                        in forbidden_maestro_prefixes
                    )
                )


if __name__ == "__main__":
    unittest.main()
