from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, Any


@dataclass(slots=True)
class ModelRequest:
    purpose: str
    instructions: str
    context: dict[str, Any]


@dataclass(slots=True)
class ModelResponse:
    provider: str
    model: str
    output: str
    metadata: dict[str, Any]


class ModelProvider(Protocol):
    """
    Provider-neutral interface.

    OpenAI, Microsoft-hosted models, local models, or future providers
    must adapt to MAESTRO. MAESTRO never adapts its constitution to them.
    """

    def generate(self, request: ModelRequest) -> ModelResponse:
        ...
