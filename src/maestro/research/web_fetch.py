from __future__ import annotations

from dataclasses import dataclass

from maestro.enums import (
    CouncilId,
    SideEffectLevel,
)
from maestro.tools.registry import (
    ToolSpec,
)

from .provider_contracts import (
    ResearchCapability,
    ResearchProviderDescriptor,
)
from .redirects import (
    GovernedRedirectTransport,
    SourceRedirectHop,
)


GOVERNED_WEB_FETCH_VERSION = "RX0.3D1"

GOVERNED_WEB_FETCH_PROVIDER_ID = (
    "governed_web"
)

GOVERNED_WEB_FETCH_TOOL_NAME = (
    "governed_web.fetch"
)

GOVERNED_WEB_FETCH_CAPABILITY = (
    "research.fetch"
)

GOVERNED_WEB_FETCH_PROVIDER_BINDING = (
    "research.provider:"
    + GOVERNED_WEB_FETCH_PROVIDER_ID
)


@dataclass(
    frozen=True,
    slots=True,
)
class GovernedWebFetchResult:
    """
    Result of one governed Web fetch.

    Body bytes remain execution/output data.
    ToolRegistry retention policy is responsible
    for not retaining their contents.
    """

    final_url: str
    method: str
    status: int
    content_type: str | None
    body: bytes
    body_sha256: str
    redirects: tuple[
        SourceRedirectHop,
        ...,
    ]

    @property
    def body_size(
        self,
    ) -> int:
        return len(
            self.body
        )


class GovernedWebFetchTool:
    """
    FETCH tool backed exclusively by the governed
    redirect transport stack.

    This class does not perform DNS, TCP, TLS,
    HTTP parsing, redirect interpretation, trust
    evaluation, evidence promotion, or learning.
    """

    def __init__(
        self,
        transport: (
            GovernedRedirectTransport
            | None
        ) = None,
    ):
        selected = (
            GovernedRedirectTransport()
            if transport is None
            else transport
        )

        if not isinstance(
            selected,
            GovernedRedirectTransport,
        ):
            raise TypeError(
                "transport must be a "
                "GovernedRedirectTransport."
            )

        self.transport = selected

    def __call__(
        self,
        url: str,
    ) -> GovernedWebFetchResult:
        if not isinstance(
            url,
            str,
        ):
            raise TypeError(
                "url must be a string."
            )

        governed = (
            self.transport.request(
                "GET",
                url,
            )
        )

        response = (
            governed.response
        )

        return GovernedWebFetchResult(
            final_url=(
                response.target
                .request_url
            ),
            method=response.method,
            status=response.status,
            content_type=(
                response.content_type
            ),
            body=response.body,
            body_sha256=(
                response.body_sha256
            ),
            redirects=(
                governed.redirects
            ),
        )


@dataclass(
    frozen=True,
    slots=True,
)
class GovernedWebFetchBinding:
    """
    Declarative binding only.

    Construction does not mutate a provider
    registry or ToolRegistry.
    """

    provider: ResearchProviderDescriptor
    tool_spec: ToolSpec
    handler: GovernedWebFetchTool


def build_governed_web_fetch_binding(
    *,
    transport: (
        GovernedRedirectTransport
        | None
    ) = None,
) -> GovernedWebFetchBinding:
    handler = GovernedWebFetchTool(
        transport=transport
    )

    provider = (
        ResearchProviderDescriptor(
            provider_id=(
                GOVERNED_WEB_FETCH_PROVIDER_ID
            ),
            capabilities=frozenset(
                {
                    ResearchCapability.FETCH,
                }
            ),
            tool_names={
                ResearchCapability.FETCH: (
                    GOVERNED_WEB_FETCH_TOOL_NAME
                ),
            },
            local=False,
            metadata={
                "version": (
                    GOVERNED_WEB_FETCH_VERSION
                ),
                "transport": (
                    "GovernedRedirectTransport"
                ),
            },
        )
    )

    tool_spec = ToolSpec(
        name=(
            GOVERNED_WEB_FETCH_TOOL_NAME
        ),
        description=(
            "Governed public HTTP/HTTPS "
            "FETCH through RX source-access "
            "transport."
        ),
        capabilities=(
            GOVERNED_WEB_FETCH_CAPABILITY,
            GOVERNED_WEB_FETCH_PROVIDER_BINDING,
        ),
        allowed_councils=frozenset(
            {
                CouncilId.RX,
            }
        ),
        side_effect_level=(
            SideEffectLevel.A0_READ_ONLY
        ),
        requires_policy_approval=False,
        requires_human_approval=False,
    )

    return GovernedWebFetchBinding(
        provider=provider,
        tool_spec=tool_spec,
        handler=handler,
    )


__all__ = [
    "GOVERNED_WEB_FETCH_VERSION",
    "GOVERNED_WEB_FETCH_PROVIDER_ID",
    "GOVERNED_WEB_FETCH_TOOL_NAME",
    "GOVERNED_WEB_FETCH_CAPABILITY",
    "GOVERNED_WEB_FETCH_PROVIDER_BINDING",
    "GovernedWebFetchResult",
    "GovernedWebFetchTool",
    "GovernedWebFetchBinding",
    "build_governed_web_fetch_binding",
]
