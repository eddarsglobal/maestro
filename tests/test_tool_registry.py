import unittest

from maestro.enums import CouncilId, SideEffectLevel
from maestro.governance.action_firewall import ActionDenied
from maestro.tools.registry import ToolRegistry, ToolSpec


class ToolRegistryTests(unittest.TestCase):
    def test_allowed_read_tool(self):
        registry = ToolRegistry()
        registry.register(
            ToolSpec(
                name="read_repo",
                description="Read repository",
                capabilities=("repository.read",),
                allowed_councils=frozenset({CouncilId.IT, CouncilId.SC}),
                side_effect_level=SideEffectLevel.A0_READ_ONLY,
            ),
            lambda path: f"read:{path}",
        )
        result = registry.invoke(
            task_id="TASK-X",
            actor=CouncilId.IT,
            tool_name="read_repo",
            arguments={"path": "src"},
        )
        self.assertEqual(result, "read:src")

    def test_disallowed_council(self):
        registry = ToolRegistry()
        registry.register(
            ToolSpec(
                name="edit_repo",
                description="Edit repository",
                capabilities=("repository.write",),
                allowed_councils=frozenset({CouncilId.IT}),
                side_effect_level=SideEffectLevel.A1_REVERSIBLE_LOCAL,
            ),
            lambda: True,
        )
        with self.assertRaises(PermissionError):
            registry.invoke(
                task_id="TASK-X",
                actor=CouncilId.CM,
                tool_name="edit_repo",
            )

    def test_material_external_requires_human_when_spec_requires_it(self):
        registry = ToolRegistry()
        registry.register(
            ToolSpec(
                name="deploy_prod",
                description="Deploy production",
                capabilities=("deployment.production",),
                allowed_councils=frozenset({CouncilId.OP}),
                side_effect_level=SideEffectLevel.A3_MATERIAL_EXTERNAL,
                requires_policy_approval=True,
                requires_human_approval=True,
            ),
            lambda: "deployed",
        )
        with self.assertRaises(ActionDenied):
            registry.invoke(
                task_id="TASK-X",
                actor=CouncilId.OP,
                tool_name="deploy_prod",
                policy_approved=True,
                human_approved=False,
            )

        result = registry.invoke(
            task_id="TASK-X",
            actor=CouncilId.OP,
            tool_name="deploy_prod",
            policy_approved=True,
            human_approved=True,
        )
        self.assertEqual(result, "deployed")


if __name__ == "__main__":
    unittest.main()
