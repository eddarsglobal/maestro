import unittest

from maestro.autonomous.sandbox import SandboxedToolRunner, SandboxPolicy, SandboxViolation
from maestro.enums import CouncilId, SideEffectLevel
from maestro.tools.registry import ToolRegistry, ToolSpec


class SandboxTests(unittest.TestCase):
    def test_allowlist_enforced(self):
        reg = ToolRegistry()
        reg.register(
            ToolSpec("read_repo", "r", ("repo.read",), frozenset({CouncilId.IT}), SideEffectLevel.A0_READ_ONLY),
            lambda: "ok",
        )
        runner = SandboxedToolRunner(reg, SandboxPolicy(frozenset({"read_repo"}), max_calls=1))
        self.assertEqual(runner.invoke(task_id="T1", actor=CouncilId.IT, tool_name="read_repo"), "ok")
        with self.assertRaises(SandboxViolation):
            runner.invoke(task_id="T1", actor=CouncilId.IT, tool_name="other")


if __name__ == "__main__":
    unittest.main()
