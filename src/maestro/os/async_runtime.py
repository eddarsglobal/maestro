from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Iterable

from maestro.autonomous.executor import CouncilExecutor, ExecutionRequest, ExecutionResult


@dataclass(slots=True)
class AsyncExecutionEnvelope:
    request: ExecutionRequest
    result: ExecutionResult | None = None
    error: str | None = None


class AsyncCouncilRunner:
    """
    Runs independent Council execution requests concurrently.

    It wraps synchronous Council adapters using asyncio.to_thread so the
    v0.6 adapter contract remains valid.
    """

    def __init__(self, executor: CouncilExecutor, max_concurrency: int = 8):
        if max_concurrency < 1:
            raise ValueError("max_concurrency must be >= 1")
        self.executor = executor
        self._sem = asyncio.Semaphore(max_concurrency)

    async def _run_one(self, request: ExecutionRequest) -> AsyncExecutionEnvelope:
        async with self._sem:
            try:
                result = await asyncio.to_thread(self.executor.execute, request)
                return AsyncExecutionEnvelope(request=request, result=result)
            except Exception as exc:
                return AsyncExecutionEnvelope(request=request, error=str(exc))

    async def run_many(self, requests: Iterable[ExecutionRequest]) -> list[AsyncExecutionEnvelope]:
        tasks = [asyncio.create_task(self._run_one(req)) for req in requests]
        return await asyncio.gather(*tasks)
