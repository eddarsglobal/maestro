import unittest

from maestro.autonomous.executor import CouncilExecutor, ExecutionRequest, ExecutionResult
from maestro.enums import CouncilId


class FakeIT:
    council = CouncilId.IT
    def execute(self, request):
        return ExecutionResult(request.task_id, request.council, True, {"ok": True})


class ExecutorTests(unittest.TestCase):
    def test_adapter_execution(self):
        ex = CouncilExecutor()
        ex.register(FakeIT())
        result = ex.execute(ExecutionRequest("T1", CouncilId.IT, "CODE", {}))
        self.assertTrue(result.success)
        self.assertTrue(result.output["ok"])


if __name__ == "__main__":
    unittest.main()
