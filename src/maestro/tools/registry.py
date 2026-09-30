from __future__ import annotations

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

    def register(self, spec: ToolSpec, handler: ToolHandler) -> None:
        if spec.name in self._specs:
            raise ValueError(f"Duplicate tool: {spec.name}")
        self._specs[spec.name] = spec
        self._handlers[spec.name] = handler

    def spec(self, name: str) -> ToolSpec:
        return self._specs[name]

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
        if tool_name not in self._specs:
            raise KeyError(f"Unknown tool: {tool_name}")

        spec = self._specs[tool_name]
        args = dict(arguments or {})

        if actor not in spec.allowed_councils:
            self.history.append(
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
            self.history.append(
                ToolInvocation(
                    task_id, actor, tool_name, ToolExecutionStatus.DENIED, args,
                    error=str(exc),
                )
            )
            raise

        try:
            result = self._handlers[tool_name](**args)
        except Exception as exc:
            self.history.append(
                ToolInvocation(
                    task_id, actor, tool_name, ToolExecutionStatus.FAILED, args,
                    error=str(exc),
                )
            )
            raise

        self.history.append(
            ToolInvocation(
                task_id, actor, tool_name, ToolExecutionStatus.EXECUTED, args,
                result_summary=result,
            )
        )
        return result
