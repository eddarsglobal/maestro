from __future__ import annotations

import hmac
import secrets

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
    """
    Safe retained metadata for one tool call.

    Raw arguments, raw results, and raw exception
    messages are execution data. They must not be
    retained in history or context receipts.
    """

    task_ref: str
    actor: CouncilId
    tool_ref: str
    status: ToolExecutionStatus
    args_summary: dict[str, Any]
    result_summary: Any = None
    error: str | None = None


TOOL_RETENTION_VERSION = "RX0.3C"

_MAX_RETAINED_ARGUMENT_KINDS = 16


def _retained_value_kind(
    value: Any,
) -> str:
    """
    Return only a coarse structural category.

    This deliberately avoids repr(), str(), custom
    type names, mapping keys, nested traversal, and
    scalar values.
    """

    value_type = type(value)

    if value is None:
        return "none"

    if value_type is bool:
        return "bool"

    if value_type is int:
        return "int"

    if value_type is float:
        return "float"

    if value_type is str:
        return "text"

    if value_type in (
        bytes,
        bytearray,
        memoryview,
    ):
        return "binary"

    if value_type is dict:
        return "mapping"

    if value_type in (
        list,
        tuple,
    ):
        return "sequence"

    if value_type in (
        set,
        frozenset,
    ):
        return "set"

    return "object"


def _summarize_arguments(
    args: dict[str, Any],
) -> dict[str, Any]:
    kinds: list[str] = []

    for index, value in enumerate(
        args.values()
    ):
        if (
            index
            >= _MAX_RETAINED_ARGUMENT_KINDS
        ):
            break

        kinds.append(
            _retained_value_kind(
                value
            )
        )

    return {
        "version": TOOL_RETENTION_VERSION,
        "argument_count": len(args),
        "argument_kinds": tuple(kinds),
        "truncated": (
            len(args)
            > _MAX_RETAINED_ARGUMENT_KINDS
        ),
    }


def _summarize_result(
    result: Any,
) -> dict[str, str]:
    return {
        "version": TOOL_RETENTION_VERSION,
        "kind": _retained_value_kind(
            result
        ),
    }


def _summarize_exception(
    exc: Exception,
) -> str:
    """
    Retain an exception category, never its message.

    Only stable built-in categories are retained.
    Custom exception class names are intentionally
    collapsed to "Exception".
    """

    categories = (
        PermissionError,
        TimeoutError,
        ConnectionError,
        OSError,
        KeyError,
        ValueError,
        TypeError,
        RuntimeError,
    )

    for category in categories:
        if isinstance(
            exc,
            category,
        ):
            return category.__name__

    return "Exception"


class ToolRegistry:
    def __init__(self, firewall: ActionFirewall | None = None):
        self.firewall = firewall or ActionFirewall()

        # Raw task IDs may contain caller-controlled
        # text. They are never retained in
        # ToolInvocation. A per-registry keyed
        # reference preserves correlation without
        # retaining the original identifier.
        self._retention_reference_key = (
            secrets.token_bytes(32)
        )

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

    def _opaque_reference(
        self,
        namespace: str,
        value: str,
    ) -> str:
        """
        Create a registry-local opaque reference.

        Namespace separation prevents an identical
        raw task ID and tool name from producing
        the same retained reference.
        """

        if type(value) is not str:
            raise TypeError(
                "reference value must be "
                "a string."
            )

        message = (
            namespace.encode("ascii")
            + b"\x00"
            + value.encode("utf-8")
        )

        digest = hmac.new(
            self._retention_reference_key,
            message,
            digestmod="sha256",
        ).hexdigest()

        return (
            f"{namespace}ref:{digest}"
        )

    def task_reference(
        self,
        task_id: str,
    ) -> str:
        return self._opaque_reference(
            "task",
            task_id,
        )

    def tool_reference(
        self,
        tool_name: str,
    ) -> str:
        return self._opaque_reference(
            "tool",
            tool_name,
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
        task_ref = self.task_reference(
            task_id
        )
        tool_ref = self.tool_reference(
            tool_name
        )
        args = dict(arguments or {})

        # Execution receives raw arguments.
        # Retention receives only structural
        # metadata with no argument names/values.
        args_summary = (
            _summarize_arguments(
                args
            )
        )

        if actor not in spec.allowed_councils:
            self._record_invocation(
                ToolInvocation(
                    task_ref, actor, tool_ref, ToolExecutionStatus.DENIED, args_summary,
                    error="PermissionError",
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
                    task_ref, actor, tool_ref, ToolExecutionStatus.DENIED, args_summary,
                    error=_summarize_exception(
                        exc
                    ),
                )
            )
            raise

        try:
            result = self._handlers[tool_name](**args)
        except Exception as exc:
            self._record_invocation(
                ToolInvocation(
                    task_ref, actor, tool_ref, ToolExecutionStatus.FAILED, args_summary,
                    error=_summarize_exception(
                        exc
                    ),
                )
            )
            raise

        self._record_invocation(
            ToolInvocation(
                task_ref, actor, tool_ref, ToolExecutionStatus.EXECUTED, args_summary,
                result_summary=(
                    _summarize_result(
                        result
                    )
                ),
            )
        )
        return result
