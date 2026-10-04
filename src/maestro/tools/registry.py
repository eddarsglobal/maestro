from __future__ import annotations

from contextvars import ContextVar
from dataclasses import dataclass, field
from typing import Any, Callable

from maestro.enums import CouncilId, SideEffectLevel, ToolExecutionStatus
from maestro.governance.action_firewall import ActionFirewall, ActionRequest


ToolHandler = Callable[..., Any]


@dataclass(frozen=True, slots=True)
class ToolSpec:
    name: str
    description: str
    capabilities: tuple[str, ...]
    allowed_councils: frozenset[CouncilId]
    side_effect_level: SideEffectLevel
    requires_policy_approval: bool = False
    requires_human_approval: bool = False


@dataclass(slots=True)
class ToolInvocation:
    task_id: str
    actor: CouncilId
    tool_name: str
    status: ToolExecutionStatus
    args_summary: dict[str, Any]
    result_summary: Any = None
    error: str | None = None


class ToolRegistry:
    def __init__(self, firewall: ActionFirewall | None = None):
        self.firewall = firewall or ActionFirewall()
        self._specs: dict[str, ToolSpec] = {}
        self._handlers: dict[str, ToolHandler] = {}
        self.history: list[ToolInvocation] = []

        self._invocation_receipt: ContextVar[
            ToolInvocation | None
        ] = ContextVar(
            (
                "maestro_tool_invocation_receipt_"
                f"{id(self)}"
            ),
            default=None,
        )

    def register(self, spec: ToolSpec, handler: ToolHandler) -> None:
        if spec.name in self._specs:
            raise ValueError(f"Duplicate tool: {spec.name}")
        self._specs[spec.name] = spec
        self._handlers[spec.name] = handler

    def spec(self, name: str) -> ToolSpec:
        return self._specs[name]

    def last_invocation_receipt(
        self,
    ) -> ToolInvocation | None:
        """
        Return the last ToolInvocation produced
        in the current execution context.

        The global history remains observational.
        This receipt is the correlation primitive
        for one synchronous/thread/async context.
        """
        return self._invocation_receipt.get()

    def _record_invocation(
        self,
        invocation: ToolInvocation,
    ) -> None:
        self.history.append(invocation)
        self._invocation_receipt.set(
            invocation
        )

    def allowed_tools(self, council: CouncilId) -> list[ToolSpec]:
        return [
            spec for spec in self._specs.values()
            if council in spec.allowed_councils
        ]

    def invoke(
        self,
        *,
        task_id: str,
        actor: CouncilId,
        tool_name: str,
        arguments: dict[str, Any] | None = None,
        policy_approved: bool = False,
        human_approved: bool = False,
    ) -> Any:
        # Prevent a previous invocation in this
        # execution context from being mistaken
        # for the current one if this call fails
        # before a ToolInvocation is recorded.
        self._invocation_receipt.set(None)

        if tool_name not in self._specs:
            raise KeyError(f"Unknown tool: {tool_name}")

        spec = self._specs[tool_name]
        args = dict(arguments or {})

        if actor not in spec.allowed_councils:
            self._record_invocation(
                ToolInvocation(
                    task_id, actor, tool_name, ToolExecutionStatus.DENIED, args,
                    error="Council not permitted to use tool.",
                )
            )
            raise PermissionError(f"{actor.value} cannot use {tool_name}.")

        effective_policy = policy_approved or not spec.requires_policy_approval
        effective_human = human_approved or not spec.requires_human_approval

        try:
            self.firewall.authorize(
                ActionRequest(
                    actor=actor,
                    action=tool_name,
                    level=spec.side_effect_level,
                    policy_approved=effective_policy,
                    human_approved=effective_human,
                )
            )
        except Exception as exc:
            self._record_invocation(
                ToolInvocation(
                    task_id, actor, tool_name, ToolExecutionStatus.DENIED, args,
                    error=str(exc),
                )
            )
            raise

        try:
            result = self._handlers[tool_name](**args)
        except Exception as exc:
            self._record_invocation(
                ToolInvocation(
                    task_id, actor, tool_name, ToolExecutionStatus.FAILED, args,
                    error=str(exc),
                )
            )
            raise

        self._record_invocation(
            ToolInvocation(
                task_id, actor, tool_name, ToolExecutionStatus.EXECUTED, args,
                result_summary=result,
            )
        )
        return result
