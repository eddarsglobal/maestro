import asyncio
import unittest

from maestro.autonomous.executor import CouncilExecutor, ExecutionRequest, ExecutionResult
from maestro.enums import CouncilId
from maestro.os.async_runtime import AsyncCouncilRunner


class FakeIT:
    council = CouncilId.IT
    def execute(self, request):
        return ExecutionResult(request.task_id, request.council, True, {"ok": request.action})


class AsyncRuntimeTests(unittest.TestCase):
    def test_parallel_runner(self):
        async def run():
            ex = CouncilExecutor()
            ex.register(FakeIT())
            runner = AsyncCouncilRunner(ex, max_concurrency=2)
            reqs = [
                ExecutionRequest("T1", CouncilId.IT, "A", {}),
                ExecutionRequest("T2", CouncilId.IT, "B", {}),
            ]
            return await runner.run_many(reqs)

        out = asyncio.run(run())
        self.assertEqual(len(out), 2)
        self.assertTrue(all(x.result and x.result.success for x in out))


if __name__ == "__main__":
    unittest.main()
