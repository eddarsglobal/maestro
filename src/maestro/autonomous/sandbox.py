from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

from maestro.enums import CouncilId
from maestro.tools.registry import ToolRegistry


class SandboxViolation(PermissionError):
    pass


@dataclass(frozen=True, slots=True)
class SandboxPolicy:
    allowed_tools: frozenset[str]
    max_calls: int = 32
    deny_network: bool = False
    deny_process_spawn: bool = False


class SandboxedToolRunner:
    """
    Logical sandbox boundary over the Tool Registry.

    v0.6 does not pretend to be an OS-level sandbox. It enforces the runtime
    capability contract and is intentionally replaceable by stronger adapters.
    """

    def __init__(self, registry: ToolRegistry, policy: SandboxPolicy):
        self.registry = registry
        self.policy = policy
        self.calls = 0

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
        if tool_name not in self.policy.allowed_tools:
            raise SandboxViolation(f"Tool outside sandbox allowlist: {tool_name}")
        if self.calls >= self.policy.max_calls:
            raise SandboxViolation("Sandbox tool-call budget exhausted.")

        self.calls += 1
        return self.registry.invoke(
            task_id=task_id,
            actor=actor,
            tool_name=tool_name,
            arguments=arguments,
            policy_approved=policy_approved,
            human_approved=human_approved,
        )
