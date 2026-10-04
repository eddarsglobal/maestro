import threading
import unittest

from maestro.enums import (
    CouncilId,
    SideEffectLevel,
    ToolExecutionStatus,
)
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

    def test_executed_invocation_has_context_receipt(self):
        registry = ToolRegistry()

        registry.register(
            ToolSpec(
                name="receipt.read",
                description="receipt",
                capabilities=("receipt.read",),
                allowed_councils=frozenset(
                    {CouncilId.IT}
                ),
                side_effect_level=(
                    SideEffectLevel.A0_READ_ONLY
                ),
            ),
            lambda value: value,
        )

        registry.invoke(
            task_id="TASK-RECEIPT-1",
            actor=CouncilId.IT,
            tool_name="receipt.read",
            arguments={
                "value": "ok"
            },
        )

        receipt = (
            registry.last_invocation_receipt()
        )

        self.assertIsNotNone(receipt)
        self.assertEqual(
            receipt.status,
            ToolExecutionStatus.EXECUTED,
        )
        self.assertEqual(
            receipt.args_summary["value"],
            "ok",
        )

    def test_failed_invocation_has_context_receipt(self):
        registry = ToolRegistry()

        def fail():
            raise RuntimeError(
                "synthetic failure"
            )

        registry.register(
            ToolSpec(
                name="receipt.fail",
                description="receipt",
                capabilities=("receipt.read",),
                allowed_councils=frozenset(
                    {CouncilId.IT}
                ),
                side_effect_level=(
                    SideEffectLevel.A0_READ_ONLY
                ),
            ),
            fail,
        )

        with self.assertRaises(
            RuntimeError
        ):
            registry.invoke(
                task_id="TASK-RECEIPT-2",
                actor=CouncilId.IT,
                tool_name="receipt.fail",
            )

        receipt = (
            registry.last_invocation_receipt()
        )

        self.assertIsNotNone(receipt)
        self.assertEqual(
            receipt.status,
            ToolExecutionStatus.FAILED,
        )

    def test_denied_invocation_has_context_receipt(self):
        registry = ToolRegistry()

        registry.register(
            ToolSpec(
                name="receipt.denied",
                description="receipt",
                capabilities=("receipt.write",),
                allowed_councils=frozenset(
                    {CouncilId.IT}
                ),
                side_effect_level=(
                    SideEffectLevel
                    .A1_REVERSIBLE_LOCAL
                ),
            ),
            lambda: True,
        )

        with self.assertRaises(
            PermissionError
        ):
            registry.invoke(
                task_id="TASK-RECEIPT-3",
                actor=CouncilId.CM,
                tool_name="receipt.denied",
            )

        receipt = (
            registry.last_invocation_receipt()
        )

        self.assertIsNotNone(receipt)
        self.assertEqual(
            receipt.status,
            ToolExecutionStatus.DENIED,
        )

    def test_unknown_tool_clears_stale_receipt(self):
        registry = ToolRegistry()

        registry.register(
            ToolSpec(
                name="receipt.good",
                description="receipt",
                capabilities=("receipt.read",),
                allowed_councils=frozenset(
                    {CouncilId.IT}
                ),
                side_effect_level=(
                    SideEffectLevel.A0_READ_ONLY
                ),
            ),
            lambda: True,
        )

        registry.invoke(
            task_id="TASK-RECEIPT-4",
            actor=CouncilId.IT,
            tool_name="receipt.good",
        )

        self.assertIsNotNone(
            registry.last_invocation_receipt()
        )

        with self.assertRaises(
            KeyError
        ):
            registry.invoke(
                task_id="TASK-RECEIPT-4",
                actor=CouncilId.IT,
                tool_name="missing.tool",
            )

        self.assertIsNone(
            registry.last_invocation_receipt()
        )

    def test_receipt_is_context_local_under_concurrency(self):
        registry = ToolRegistry()
        barrier = threading.Barrier(2)

        def fail(marker):
            barrier.wait(timeout=5)
            raise RuntimeError(marker)

        registry.register(
            ToolSpec(
                name="receipt.concurrent",
                description="receipt",
                capabilities=("receipt.read",),
                allowed_councils=frozenset(
                    {CouncilId.IT}
                ),
                side_effect_level=(
                    SideEffectLevel.A0_READ_ONLY
                ),
            ),
            fail,
        )

        observed = {}
        observed_lock = threading.Lock()

        def worker(marker):
            try:
                registry.invoke(
                    task_id="TASK-SAME",
                    actor=CouncilId.IT,
                    tool_name=(
                        "receipt.concurrent"
                    ),
                    arguments={
                        "marker": marker
                    },
                )
            except RuntimeError:
                receipt = (
                    registry
                    .last_invocation_receipt()
                )

                with observed_lock:
                    observed[marker] = (
                        receipt
                    )

        threads = [
            threading.Thread(
                target=worker,
                args=(marker,),
            )
            for marker in ("A", "B")
        ]

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join(timeout=10)

        self.assertFalse(
            any(
                thread.is_alive()
                for thread in threads
            )
        )

        self.assertEqual(
            set(observed),
            {"A", "B"},
        )

        for marker in ("A", "B"):
            receipt = observed[marker]

            self.assertIsNotNone(
                receipt
            )

            self.assertEqual(
                receipt.status,
                ToolExecutionStatus.FAILED,
            )

            self.assertEqual(
                receipt.args_summary[
                    "marker"
                ],
                marker,
            )

        self.assertIsNot(
            observed["A"],
            observed["B"],
        )


if __name__ == "__main__":
    unittest.main()
