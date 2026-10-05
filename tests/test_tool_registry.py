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
            receipt.args_summary,
            {
                "version": "RX0.3C",
                "argument_count": 1,
                "argument_kinds": (
                    "text",
                ),
                "truncated": False,
            },
        )

        self.assertNotIn(
            "ok",
            repr(
                receipt.args_summary
            ),
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
                    task_id=f"TASK-{marker}",
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
                receipt.task_ref,
                registry.task_reference(
                    f"TASK-{marker}"
                ),
            )

            self.assertNotIn(
                marker,
                repr(
                    receipt.args_summary
                ),
            )

        self.assertIsNot(
            observed["A"],
            observed["B"],
        )


    def test_raw_arguments_and_result_are_not_retained(self):
        registry = ToolRegistry()

        secret = (
            "RX03C_SUPER_SECRET_TOKEN"
        )

        observed = {}

        def handler(
            token,
            payload,
        ):
            observed["token"] = token
            observed["payload"] = payload

            return {
                "body": token,
                "nested": payload,
            }

        registry.register(
            ToolSpec(
                name="privacy.success",
                description="privacy",
                capabilities=(
                    "privacy.read",
                ),
                allowed_councils=frozenset(
                    {
                        CouncilId.IT,
                    }
                ),
                side_effect_level=(
                    SideEffectLevel.A0_READ_ONLY
                ),
            ),
            handler,
        )

        payload = {
            "credential": secret,
        }

        result = registry.invoke(
            task_id="TASK-PRIVACY-1",
            actor=CouncilId.IT,
            tool_name="privacy.success",
            arguments={
                "token": secret,
                "payload": payload,
            },
        )

        self.assertEqual(
            observed["token"],
            secret,
        )

        self.assertIs(
            observed["payload"],
            payload,
        )

        self.assertEqual(
            result["body"],
            secret,
        )

        receipt = (
            registry.last_invocation_receipt()
        )

        self.assertIsNotNone(
            receipt
        )

        self.assertEqual(
            receipt.args_summary[
                "argument_kinds"
            ],
            (
                "text",
                "mapping",
            ),
        )

        self.assertEqual(
            receipt.result_summary,
            {
                "version": "RX0.3C",
                "kind": "mapping",
            },
        )

        self.assertNotIn(
            secret,
            repr(
                receipt.args_summary
            ),
        )

        self.assertNotIn(
            secret,
            repr(
                receipt.result_summary
            ),
        )

        self.assertIs(
            registry.history[-1],
            receipt,
        )

    def test_handler_error_message_is_not_retained(self):
        registry = ToolRegistry()

        secret = (
            "RX03C_HANDLER_SECRET"
        )

        def fail(token):
            raise RuntimeError(
                "handler failed with "
                + token
            )

        registry.register(
            ToolSpec(
                name="privacy.fail",
                description="privacy",
                capabilities=(
                    "privacy.read",
                ),
                allowed_councils=frozenset(
                    {
                        CouncilId.IT,
                    }
                ),
                side_effect_level=(
                    SideEffectLevel.A0_READ_ONLY
                ),
            ),
            fail,
        )

        with self.assertRaises(
            RuntimeError
        ) as caught:
            registry.invoke(
                task_id="TASK-PRIVACY-2",
                actor=CouncilId.IT,
                tool_name="privacy.fail",
                arguments={
                    "token": secret,
                },
            )

        self.assertIn(
            secret,
            str(
                caught.exception
            ),
        )

        receipt = (
            registry.last_invocation_receipt()
        )

        self.assertEqual(
            receipt.status,
            ToolExecutionStatus.FAILED,
        )

        self.assertEqual(
            receipt.error,
            "RuntimeError",
        )

        self.assertNotIn(
            secret,
            repr(receipt),
        )

    def test_council_denial_does_not_retain_arguments(self):
        registry = ToolRegistry()

        secret = (
            "RX03C_DENIED_SECRET"
        )

        registry.register(
            ToolSpec(
                name="privacy.denied",
                description="privacy",
                capabilities=(
                    "privacy.read",
                ),
                allowed_councils=frozenset(
                    {
                        CouncilId.IT,
                    }
                ),
                side_effect_level=(
                    SideEffectLevel.A0_READ_ONLY
                ),
            ),
            lambda token: token,
        )

        with self.assertRaises(
            PermissionError
        ):
            registry.invoke(
                task_id="TASK-PRIVACY-3",
                actor=CouncilId.CM,
                tool_name="privacy.denied",
                arguments={
                    "token": secret,
                },
            )

        receipt = (
            registry.last_invocation_receipt()
        )

        self.assertEqual(
            receipt.status,
            ToolExecutionStatus.DENIED,
        )

        self.assertEqual(
            receipt.error,
            "PermissionError",
        )

        self.assertNotIn(
            secret,
            repr(receipt),
        )

    def test_firewall_error_message_is_not_retained(self):
        secret = (
            "RX03C_FIREWALL_SECRET"
        )

        class DenyingFirewall:
            def authorize(
                self,
                request,
            ):
                raise RuntimeError(
                    "firewall denied "
                    + secret
                )

        registry = ToolRegistry(
            DenyingFirewall()
        )

        registry.register(
            ToolSpec(
                name="privacy.firewall",
                description="privacy",
                capabilities=(
                    "privacy.read",
                ),
                allowed_councils=frozenset(
                    {
                        CouncilId.IT,
                    }
                ),
                side_effect_level=(
                    SideEffectLevel.A0_READ_ONLY
                ),
            ),
            lambda: True,
        )

        with self.assertRaises(
            RuntimeError
        ) as caught:
            registry.invoke(
                task_id="TASK-PRIVACY-4",
                actor=CouncilId.IT,
                tool_name=(
                    "privacy.firewall"
                ),
            )

        self.assertIn(
            secret,
            str(
                caught.exception
            ),
        )

        receipt = (
            registry.last_invocation_receipt()
        )

        self.assertEqual(
            receipt.status,
            ToolExecutionStatus.DENIED,
        )

        self.assertEqual(
            receipt.error,
            "RuntimeError",
        )

        self.assertNotIn(
            secret,
            repr(receipt),
        )

    def test_summary_never_calls_user_repr(self):
        registry = ToolRegistry()

        class Hostile:
            def __repr__(self):
                raise AssertionError(
                    "repr must not run"
                )

            def __str__(self):
                raise AssertionError(
                    "str must not run"
                )

        hostile = Hostile()

        registry.register(
            ToolSpec(
                name="privacy.object",
                description="privacy",
                capabilities=(
                    "privacy.read",
                ),
                allowed_councils=frozenset(
                    {
                        CouncilId.IT,
                    }
                ),
                side_effect_level=(
                    SideEffectLevel.A0_READ_ONLY
                ),
            ),
            lambda value: value,
        )

        result = registry.invoke(
            task_id="TASK-PRIVACY-5",
            actor=CouncilId.IT,
            tool_name="privacy.object",
            arguments={
                "value": hostile,
            },
        )

        self.assertIs(
            result,
            hostile,
        )

        receipt = (
            registry.last_invocation_receipt()
        )

        self.assertEqual(
            receipt.args_summary[
                "argument_kinds"
            ],
            (
                "object",
            ),
        )

        self.assertEqual(
            receipt.result_summary[
                "kind"
            ],
            "object",
        )

    def test_argument_summary_is_bounded(self):
        registry = ToolRegistry()

        registry.register(
            ToolSpec(
                name="privacy.bounded",
                description="privacy",
                capabilities=(
                    "privacy.read",
                ),
                allowed_councils=frozenset(
                    {
                        CouncilId.IT,
                    }
                ),
                side_effect_level=(
                    SideEffectLevel.A0_READ_ONLY
                ),
            ),
            lambda **kwargs: True,
        )

        arguments = {
            f"arg_{index}": (
                "SECRET_VALUE"
            )
            for index in range(100)
        }

        registry.invoke(
            task_id="TASK-PRIVACY-6",
            actor=CouncilId.IT,
            tool_name="privacy.bounded",
            arguments=arguments,
        )

        receipt = (
            registry.last_invocation_receipt()
        )

        self.assertEqual(
            receipt.args_summary[
                "argument_count"
            ],
            100,
        )

        self.assertEqual(
            len(
                receipt.args_summary[
                    "argument_kinds"
                ]
            ),
            16,
        )

        self.assertTrue(
            receipt.args_summary[
                "truncated"
            ]
        )

        self.assertNotIn(
            "SECRET_VALUE",
            repr(
                receipt.args_summary
            ),
        )


    def test_task_id_is_retained_only_as_opaque_reference(self):
        registry = ToolRegistry()

        sensitive_task_id = (
            "https://example.com/"
            "?token=RX03C_TASK_SECRET"
        )

        registry.register(
            ToolSpec(
                name="privacy.taskref",
                description="privacy",
                capabilities=(
                    "privacy.read",
                ),
                allowed_councils=frozenset(
                    {
                        CouncilId.IT,
                    }
                ),
                side_effect_level=(
                    SideEffectLevel.A0_READ_ONLY
                ),
            ),
            lambda: True,
        )

        result = registry.invoke(
            task_id=sensitive_task_id,
            actor=CouncilId.IT,
            tool_name="privacy.taskref",
        )

        self.assertTrue(
            result
        )

        receipt = (
            registry.last_invocation_receipt()
        )

        self.assertIsNotNone(
            receipt
        )

        self.assertFalse(
            hasattr(
                receipt,
                "task_id",
            )
        )

        self.assertEqual(
            receipt.task_ref,
            registry.task_reference(
                sensitive_task_id
            ),
        )

        self.assertTrue(
            receipt.task_ref.startswith(
                "taskref:"
            )
        )

        retained = repr(
            (
                receipt,
                registry.history,
            )
        )

        self.assertNotIn(
            sensitive_task_id,
            retained,
        )

        self.assertNotIn(
            "RX03C_TASK_SECRET",
            retained,
        )

        other_registry = ToolRegistry()

        self.assertNotEqual(
            receipt.task_ref,
            other_registry.task_reference(
                sensitive_task_id
            ),
        )


    def test_tool_name_is_retained_only_as_opaque_reference(self):
        registry = ToolRegistry()

        sensitive_tool_name = (
            "https://example.com/"
            "?token=RX03C_TOOL_SECRET"
        )

        registry.register(
            ToolSpec(
                name=sensitive_tool_name,
                description="privacy",
                capabilities=(
                    "privacy.read",
                ),
                allowed_councils=frozenset(
                    {
                        CouncilId.IT,
                    }
                ),
                side_effect_level=(
                    SideEffectLevel.A0_READ_ONLY
                ),
            ),
            lambda: True,
        )

        result = registry.invoke(
            task_id="TASK-TOOL-REF",
            actor=CouncilId.IT,
            tool_name=sensitive_tool_name,
        )

        self.assertTrue(
            result
        )

        receipt = (
            registry.last_invocation_receipt()
        )

        self.assertIsNotNone(
            receipt
        )

        self.assertFalse(
            hasattr(
                receipt,
                "tool_name",
            )
        )

        self.assertEqual(
            receipt.tool_ref,
            registry.tool_reference(
                sensitive_tool_name
            ),
        )

        self.assertTrue(
            receipt.tool_ref.startswith(
                "toolref:"
            )
        )

        retained = repr(
            (
                receipt,
                registry.history,
            )
        )

        self.assertNotIn(
            sensitive_tool_name,
            retained,
        )

        self.assertNotIn(
            "RX03C_TOOL_SECRET",
            retained,
        )

        self.assertNotEqual(
            registry.task_reference(
                sensitive_tool_name
            ),
            registry.tool_reference(
                sensitive_tool_name
            ),
        )

        other_registry = ToolRegistry()

        self.assertNotEqual(
            receipt.tool_ref,
            other_registry.tool_reference(
                sensitive_tool_name
            ),
        )


if __name__ == "__main__":
    unittest.main()
