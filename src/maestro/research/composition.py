from __future__ import annotations

from dataclasses import dataclass

from maestro.tools.registry import (
    ToolRegistry,
)

from .provider_registry import (
    ResearchProviderRegistry,
)
from .runtime import (
    GovernedResearchRuntime,
)
from .runtime_contracts import (
    ResearchFallbackPolicy,
)
from .web_fetch import (
    GovernedWebFetchBinding,
)


GOVERNED_RESEARCH_COMPOSITION_VERSION = (
    "RX0.3D2A"
)


@dataclass(
    frozen=True,
    slots=True,
)
class GovernedResearchComposition:
    """
    Explicitly composed RX runtime.

    The composition owns the provider catalog,
    but deliberately reuses the caller-owned
    governed ToolRegistry.

    It performs no automatic provider discovery
    and creates no network authority by itself.
    """

    providers: ResearchProviderRegistry
    tools: ToolRegistry
    runtime: GovernedResearchRuntime


def compose_governed_web_research(
    *,
    tools: ToolRegistry,
    binding: GovernedWebFetchBinding,
    fallback_policy: (
        ResearchFallbackPolicy | None
    ) = None,
) -> GovernedResearchComposition:
    """
    Explicitly install one governed Web FETCH
    binding into an existing ToolRegistry and
    compose the corresponding RX runtime.

    Calling this function is the activation act.
    Importing this module has no activation side
    effect.

    The caller must already own the ToolRegistry,
    normally the same registry protected by the
    MAESTRO kernel ActionFirewall.
    """

    if not isinstance(
        tools,
        ToolRegistry,
    ):
        raise TypeError(
            "tools must be a ToolRegistry."
        )

    if not isinstance(
        binding,
        GovernedWebFetchBinding,
    ):
        raise TypeError(
            "binding must be a "
            "GovernedWebFetchBinding."
        )

    if (
        fallback_policy is not None
        and not isinstance(
            fallback_policy,
            ResearchFallbackPolicy,
        )
    ):
        raise TypeError(
            "fallback_policy must be a "
            "ResearchFallbackPolicy."
        )

    providers = (
        ResearchProviderRegistry()
    )

    providers.register(
        binding.provider
    )

    runtime = GovernedResearchRuntime(
        providers,
        tools,
        fallback_policy,
    )

    # This is intentionally the only mutation of
    # the caller-owned execution control plane.
    # ToolRegistry.register() remains the authority
    # for duplicate/conflicting tool identities.
    tools.register(
        binding.tool_spec,
        binding.handler,
    )

    return GovernedResearchComposition(
        providers=providers,
        tools=tools,
        runtime=runtime,
    )


__all__ = [
    "GOVERNED_RESEARCH_COMPOSITION_VERSION",
    "GovernedResearchComposition",
    "compose_governed_web_research",
]
