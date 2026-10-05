from __future__ import annotations

from maestro.enums import (
    CouncilId,
    SideEffectLevel,
    ToolExecutionStatus,
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
    ResearchAttemptStatus,
    ResearchExecutionAttempt,
    ResearchExecutionResult,
    ResearchFallbackPolicy,
    ResearchRequest,
    ResearchRoutingDecision,
    _thaw_research_json,
)


class ResearchRuntimeConfigurationError(
    RuntimeError
):
    pass


class ResearchProvidersExhaustedError(
    RuntimeError
):
    def __init__(
        self,
        message: str,
        attempts: tuple[
            ResearchExecutionAttempt,
            ...
        ],
    ):
        super().__init__(message)
        self.attempts = attempts


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
        fallback_policy: (
            ResearchFallbackPolicy | None
        ) = None,
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

        self.providers = providers
        self.tools = tools
        self.fallback_policy = (
            fallback_policy
            or ResearchFallbackPolicy()
        )

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

    @staticmethod
    def _with_forbidden_provider_ids(
        request: ResearchRequest,
        forbidden_provider_ids: set[str],
    ) -> ResearchRequest:
        return ResearchRequest(
            task_id=request.task_id,
            capability=request.capability,
            arguments=request.arguments,
            preferred_local=(
                request.preferred_local
            ),
            forbidden_provider_ids=(
                frozenset(
                    forbidden_provider_ids
                )
            ),
        )

    def _recorded_handler_failure(
        self,
        *,
        task_id: str,
        tool_name: str,
    ) -> bool:
        invocation = (
            self.tools
            .last_invocation_receipt()
        )

        if invocation is None:
            return False

        return (
            invocation.task_ref
            == self.tools.task_reference(
                task_id
            )
            and invocation.actor
            is CouncilId.RX
            and invocation.tool_ref
            == self.tools.tool_reference(
                tool_name
            )
            and invocation.status
            is ToolExecutionStatus.FAILED
        )

    def execute(
        self,
        request: ResearchRequest,
    ) -> ResearchExecutionResult:
        if not isinstance(
            request,
            ResearchRequest,
        ):
            raise TypeError(
                "request must be a "
                "ResearchRequest."
            )

        attempts: list[
            ResearchExecutionAttempt
        ] = []

        forbidden_provider_ids = set(
            request.forbidden_provider_ids
        )

        last_execution_error: (
            Exception | None
        ) = None

        for attempt_number in range(
            1,
            self.fallback_policy.max_attempts
            + 1,
        ):
            attempt_request = (
                self._with_forbidden_provider_ids(
                    request,
                    forbidden_provider_ids,
                )
            )

            try:
                decision = self.route(
                    attempt_request
                )
            except LookupError as exc:
                if attempts:
                    raise (
                        ResearchProvidersExhaustedError(
                            "No eligible research "
                            "provider remains after "
                            "execution failure.",
                            tuple(attempts),
                        )
                    ) from (
                        last_execution_error
                        or exc
                    )

                raise

            # Configuration/governance violations
            # are terminal and MUST NOT trigger
            # provider fallback.
            self._validate_tool(
                attempt_request,
                decision,
            )

            try:
                output = self.tools.invoke(
                    task_id=(
                        attempt_request.task_id
                    ),
                    actor=CouncilId.RX,
                    tool_name=(
                        decision.tool_name
                    ),
                    arguments=(
                        _thaw_research_json(
                            attempt_request.arguments
                        )
                    ),
                )
            except Exception as exc:
                # Only a ToolRegistry-recorded
                # handler FAILED event qualifies
                # for RX provider fallback.
                #
                # DENIED/firewall/governance
                # failures propagate fail-closed.
                if not (
                    self._recorded_handler_failure(
                        task_id=(
                            attempt_request.task_id
                        ),
                        tool_name=(
                            decision.tool_name
                        ),
                    )
                ):
                    raise

                attempts.append(
                    ResearchExecutionAttempt(
                        attempt_number=(
                            attempt_number
                        ),
                        provider_id=(
                            decision.provider_id
                        ),
                        tool_name=(
                            decision.tool_name
                        ),
                        status=(
                            ResearchAttemptStatus
                            .EXECUTION_FAILED
                        ),
                        error_type=(
                            type(exc).__name__
                        ),
                    )
                )

                last_execution_error = exc

                # Mission-local exclusion only.
                # Never mutate provider status
                # globally from a single request.
                forbidden_provider_ids.add(
                    decision.provider_id
                )

                if (
                    attempt_number
                    >= self.fallback_policy
                    .max_attempts
                ):
                    raise (
                        ResearchProvidersExhaustedError(
                            "Research provider "
                            "fallback attempt limit "
                            "exhausted.",
                            tuple(attempts),
                        )
                    ) from exc

                continue

            attempts.append(
                ResearchExecutionAttempt(
                    attempt_number=(
                        attempt_number
                    ),
                    provider_id=(
                        decision.provider_id
                    ),
                    tool_name=(
                        decision.tool_name
                    ),
                    status=(
                        ResearchAttemptStatus
                        .SUCCEEDED
                    ),
                )
            )

            return ResearchExecutionResult(
                task_id=(
                    attempt_request.task_id
                ),
                capability=(
                    attempt_request.capability
                ),
                provider_id=(
                    decision.provider_id
                ),
                tool_name=(
                    decision.tool_name
                ),
                output=output,
                attempts=tuple(attempts),
            )

        raise AssertionError(
            "Unreachable bounded research "
            "fallback state."
        )
