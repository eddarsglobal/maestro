from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol

from maestro.enums import CouncilId


@dataclass(slots=True)
class ExecutionRequest:
    task_id: str
    council: CouncilId
    action: str
    context: dict[str, Any]
    tools: list[str] = field(default_factory=list)


@dataclass(slots=True)
class ExecutionResult:
    task_id: str
    council: CouncilId
    success: bool
    output: dict[str, Any] = field(default_factory=dict)
    evidence: list[dict[str, Any]] = field(default_factory=list)
    error: str | None = None


class CouncilExecutionAdapter(Protocol):
    council: CouncilId

    def execute(self, request: ExecutionRequest) -> ExecutionResult:
        ...


class CouncilExecutor:
    def __init__(self):
        self._adapters: dict[CouncilId, CouncilExecutionAdapter] = {}

    def register(self, adapter: CouncilExecutionAdapter) -> None:
        if adapter.council in self._adapters:
            raise ValueError(f"Adapter already registered for {adapter.council.value}.")
        self._adapters[adapter.council] = adapter

    def execute(self, request: ExecutionRequest) -> ExecutionResult:
        if request.council not in self._adapters:
            raise KeyError(f"No execution adapter for {request.council.value}")
        return self._adapters[request.council].execute(request)
