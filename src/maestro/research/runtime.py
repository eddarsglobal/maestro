from __future__ import annotations

from maestro.enums import (
    CouncilId,
    SideEffectLevel,
)
from maestro.tools.registry import (
    ToolRegistry,
)

from .provider_contracts import (
    ResearchCapability,
    ResearchProviderDescriptor,
    ResearchProviderStatus,
)
from .provider_registry import (
    ResearchProviderRegistry,
)
from .runtime_contracts import (
    ResearchExecutionResult,
    ResearchRequest,
    ResearchRoutingDecision,
    _thaw_research_json,
)


class ResearchRuntimeConfigurationError(
    RuntimeError
):
    pass


_TOOL_CAPABILITY = {
    ResearchCapability.SEARCH: (
        "research.search"
    ),
    ResearchCapability.FETCH: (
        "research.fetch"
    ),
}


class GovernedResearchRuntime:
    """
    Governed provider-neutral RX source runtime.

    Provider descriptors own routing metadata only.
    All actual source access must cross ToolRegistry
    and ActionFirewall with actor=RX.
    """

    def __init__(
        self,
        providers: ResearchProviderRegistry,
        tools: ToolRegistry,
    ):
        if not isinstance(
            providers,
            ResearchProviderRegistry,
        ):
            raise TypeError(
                "providers must be a "
                "ResearchProviderRegistry."
            )

        if not isinstance(
            tools,
            ToolRegistry,
        ):
            raise TypeError(
                "tools must be a ToolRegistry."
            )

        self.providers = providers
        self.tools = tools

    @staticmethod
    def _score(
        descriptor: ResearchProviderDescriptor,
        request: ResearchRequest,
    ) -> tuple:
        degraded_penalty = (
            1
            if descriptor.status
            is ResearchProviderStatus.DEGRADED
            else 0
        )

        local_penalty = (
            0
            if (
                not request.preferred_local
                or descriptor.local
            )
            else 1
        )

        return (
            degraded_penalty,
            local_penalty,
            -descriptor.quality_score,
            descriptor.cost_score,
            descriptor.latency_score,
            descriptor.provider_id,
        )

    def route(
        self,
        request: ResearchRequest,
    ) -> ResearchRoutingDecision:
        if not isinstance(
            request,
            ResearchRequest,
        ):
            raise TypeError(
                "request must be a "
                "ResearchRequest."
            )

        candidates = self.providers.eligible(
            request.capability,
            forbidden_provider_ids=(
                request.forbidden_provider_ids
            ),
        )

        if not candidates:
            raise LookupError(
                "No eligible research provider "
                f"for {request.capability.value}."
            )

        chosen = min(
            candidates,
            key=lambda descriptor: (
                self._score(
                    descriptor,
                    request,
                )
            ),
        )

        return ResearchRoutingDecision(
            provider_id=chosen.provider_id,
            tool_name=chosen.tool_name_for(
                request.capability
            ),
            candidates=tuple(
                descriptor.provider_id
                for descriptor
                in sorted(
                    candidates,
                    key=lambda item: (
                        self._score(
                            item,
                            request,
                        )
                    ),
                )
            ),
            reason=(
                "eligible capability + governed "
                "research provider ranking"
            ),
        )

    def _validate_tool(
        self,
        request: ResearchRequest,
        decision: ResearchRoutingDecision,
    ) -> None:
        try:
            spec = self.tools.spec(
                decision.tool_name
            )
        except KeyError as exc:
            raise (
                ResearchRuntimeConfigurationError(
                    "Research provider references "
                    "an unknown governed tool."
                )
            ) from exc

        if (
            CouncilId.RX
            not in spec.allowed_councils
        ):
            raise (
                ResearchRuntimeConfigurationError(
                    "Research provider tool does "
                    "not allow Council RX."
                )
            )

        if (
            spec.side_effect_level
            is not SideEffectLevel.A0_READ_ONLY
        ):
            raise (
                ResearchRuntimeConfigurationError(
                    "RX source access must be "
                    "A0_READ_ONLY."
                )
            )

        expected_capability = (
            _TOOL_CAPABILITY[
                request.capability
            ]
        )

        if (
            expected_capability
            not in spec.capabilities
        ):
            raise (
                ResearchRuntimeConfigurationError(
                    "Research provider tool lacks "
                    f"{expected_capability}."
                )
            )

        provider_binding = (
            "research.provider:"
            f"{decision.provider_id}"
        )

        if (
            provider_binding
            not in spec.capabilities
        ):
            raise (
                ResearchRuntimeConfigurationError(
                    "Research provider/tool "
                    "binding mismatch."
                )
            )

        if (
            spec.requires_policy_approval
            or spec.requires_human_approval
        ):
            raise (
                ResearchRuntimeConfigurationError(
                    "RX0.2B accepts only "
                    "approval-free A0 research "
                    "tools."
                )
            )

    def execute(
        self,
        request: ResearchRequest,
    ) -> ResearchExecutionResult:
        decision = self.route(
            request
        )

        self._validate_tool(
            request,
            decision,
        )

        output = self.tools.invoke(
            task_id=request.task_id,
            actor=CouncilId.RX,
            tool_name=decision.tool_name,
            arguments=(
                _thaw_research_json(
                    request.arguments
                )
            ),
        )

        return ResearchExecutionResult(
            task_id=request.task_id,
            capability=request.capability,
            provider_id=decision.provider_id,
            tool_name=decision.tool_name,
            output=output,
        )
