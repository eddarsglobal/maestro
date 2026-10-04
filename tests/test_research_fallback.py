import threading
import unittest

from maestro.enums import (
    CouncilId,
    SideEffectLevel,
    ToolExecutionStatus,
)
from maestro.research import (
    MAX_RESEARCH_FALLBACK_ATTEMPTS,
    GovernedResearchRuntime,
    ResearchAttemptStatus,
    ResearchCapability,
    ResearchFallbackPolicy,
    ResearchProviderDescriptor,
    ResearchProviderRegistry,
    ResearchProviderStatus,
    ResearchProvidersExhaustedError,
    ResearchRequest,
    ResearchRuntimeConfigurationError,
)
from maestro.tools.registry import (
    ToolRegistry,
    ToolSpec,
)


def provider(
    provider_id,
    *,
    quality=0.5,
):
    return ResearchProviderDescriptor(
        provider_id=provider_id,
        capabilities=frozenset(
            {
                ResearchCapability.SEARCH,
            }
        ),
        tool_names={
            ResearchCapability.SEARCH: (
                f"{provider_id}.search"
            )
        },
        quality_score=quality,
    )


def register_tool(
    tools,
    provider_id,
    handler,
    *,
    binding=None,
):
    actual_binding = (
        provider_id
        if binding is None
        else binding
    )

    tools.register(
        ToolSpec(
            name=f"{provider_id}.search",
            description="Fake governed search",
            capabilities=(
                "research.search",
                (
                    "research.provider:"
                    f"{actual_binding}"
                ),
            ),
            allowed_councils=frozenset(
                {CouncilId.RX}
            ),
            side_effect_level=(
                SideEffectLevel.A0_READ_ONLY
            ),
        ),
        handler,
    )


class DenyFirewall:
    def authorize(self, request):
        raise PermissionError(
            "synthetic firewall denial"
        )


class ResearchFallbackTests(
    unittest.TestCase
):
    def test_policy_rejects_out_of_bounds(self):
        with self.assertRaises(
            ValueError
        ):
            ResearchFallbackPolicy(
                max_attempts=0
            )

        with self.assertRaises(
            ValueError
        ):
            ResearchFallbackPolicy(
                max_attempts=(
                    MAX_RESEARCH_FALLBACK_ATTEMPTS
                    + 1
                )
            )

    def test_policy_rejects_boolean(self):
        with self.assertRaises(
            TypeError
        ):
            ResearchFallbackPolicy(
                max_attempts=True
            )

    def test_success_records_single_attempt(self):
        providers = (
            ResearchProviderRegistry()
        )
        providers.register(
            provider("alpha")
        )

        tools = ToolRegistry()

        register_tool(
            tools,
            "alpha",
            lambda query: {
                "query": query,
            },
        )

        result = GovernedResearchRuntime(
            providers,
            tools,
        ).execute(
            ResearchRequest(
                "TASK-FB-1",
                ResearchCapability.SEARCH,
                arguments={
                    "query": "maestro"
                },
            )
        )

        self.assertEqual(
            result.provider_id,
            "alpha",
        )

        self.assertEqual(
            len(result.attempts),
            1,
        )

        self.assertEqual(
            result.attempts[0].status,
            ResearchAttemptStatus.SUCCEEDED,
        )

    def test_failure_falls_back_without_global_degrade(self):
        providers = (
            ResearchProviderRegistry()
        )

        providers.register(
            provider(
                "alpha",
                quality=1.0,
            )
        )

        providers.register(
            provider(
                "beta",
                quality=0.5,
            )
        )

        tools = ToolRegistry()

        def fail(**kwargs):
            raise ValueError(
                "do-not-copy-this-message"
            )

        register_tool(
            tools,
            "alpha",
            fail,
        )

        register_tool(
            tools,
            "beta",
            lambda **kwargs: {
                "provider": "beta"
            },
        )

        result = GovernedResearchRuntime(
            providers,
            tools,
        ).execute(
            ResearchRequest(
                "TASK-FB-2",
                ResearchCapability.SEARCH,
            )
        )

        self.assertEqual(
            result.provider_id,
            "beta",
        )

        self.assertEqual(
            [
                row.provider_id
                for row in result.attempts
            ],
            [
                "alpha",
                "beta",
            ],
        )

        self.assertEqual(
            result.attempts[0].status,
            (
                ResearchAttemptStatus
                .EXECUTION_FAILED
            ),
        )

        self.assertEqual(
            result.attempts[0].error_type,
            "ValueError",
        )

        self.assertIs(
            providers.descriptor(
                "alpha"
            ).status,
            ResearchProviderStatus.AVAILABLE,
        )

    def test_failed_provider_is_not_retried(self):
        providers = (
            ResearchProviderRegistry()
        )
        tools = ToolRegistry()

        calls = []

        for provider_id in (
            "alpha",
            "beta",
            "gamma",
        ):
            providers.register(
                provider(provider_id)
            )

            def fail(
                _provider=provider_id,
                **kwargs,
            ):
                calls.append(_provider)
                raise RuntimeError(
                    "synthetic failure"
                )

            register_tool(
                tools,
                provider_id,
                fail,
            )

        runtime = GovernedResearchRuntime(
            providers,
            tools,
            ResearchFallbackPolicy(
                max_attempts=3
            ),
        )

        with self.assertRaises(
            ResearchProvidersExhaustedError
        ) as caught:
            runtime.execute(
                ResearchRequest(
                    "TASK-FB-3",
                    ResearchCapability.SEARCH,
                )
            )

        self.assertEqual(
            calls,
            [
                "alpha",
                "beta",
                "gamma",
            ],
        )

        self.assertEqual(
            len(caught.exception.attempts),
            3,
        )

    def test_max_attempts_stops_with_providers_remaining(self):
        providers = (
            ResearchProviderRegistry()
        )
        tools = ToolRegistry()

        calls = []

        for provider_id in (
            "alpha",
            "beta",
            "gamma",
        ):
            providers.register(
                provider(provider_id)
            )

            register_tool(
                tools,
                provider_id,
                lambda _id=provider_id, **kwargs: (
                    calls.append(_id),
                    (_ for _ in ()).throw(
                        RuntimeError("failure")
                    ),
                )[1],
            )

        runtime = GovernedResearchRuntime(
            providers,
            tools,
            ResearchFallbackPolicy(
                max_attempts=2
            ),
        )

        with self.assertRaises(
            ResearchProvidersExhaustedError
        ) as caught:
            runtime.execute(
                ResearchRequest(
                    "TASK-FB-4",
                    ResearchCapability.SEARCH,
                )
            )

        self.assertEqual(
            calls,
            [
                "alpha",
                "beta",
            ],
        )

        self.assertEqual(
            len(caught.exception.attempts),
            2,
        )

    def test_provider_exhaustion_before_limit(self):
        providers = (
            ResearchProviderRegistry()
        )

        providers.register(
            provider("alpha")
        )

        tools = ToolRegistry()

        register_tool(
            tools,
            "alpha",
            lambda **kwargs: (
                (_ for _ in ()).throw(
                    RuntimeError("failure")
                )
            ),
        )

        runtime = GovernedResearchRuntime(
            providers,
            tools,
            ResearchFallbackPolicy(
                max_attempts=5
            ),
        )

        with self.assertRaises(
            ResearchProvidersExhaustedError
        ) as caught:
            runtime.execute(
                ResearchRequest(
                    "TASK-FB-5",
                    ResearchCapability.SEARCH,
                )
            )

        self.assertEqual(
            len(caught.exception.attempts),
            1,
        )

    def test_configuration_violation_does_not_fallback(self):
        providers = (
            ResearchProviderRegistry()
        )

        providers.register(
            provider(
                "alpha",
                quality=1.0,
            )
        )

        providers.register(
            provider(
                "beta",
                quality=0.5,
            )
        )

        tools = ToolRegistry()

        register_tool(
            tools,
            "alpha",
            lambda **kwargs: "alpha",
            binding="wrong-provider",
        )

        beta_calls = []

        register_tool(
            tools,
            "beta",
            lambda **kwargs: (
                beta_calls.append(True)
            ),
        )

        runtime = GovernedResearchRuntime(
            providers,
            tools,
        )

        with self.assertRaises(
            ResearchRuntimeConfigurationError
        ):
            runtime.execute(
                ResearchRequest(
                    "TASK-FB-6",
                    ResearchCapability.SEARCH,
                )
            )

        self.assertEqual(
            beta_calls,
            [],
        )

        self.assertEqual(
            tools.history,
            [],
        )

    def test_firewall_denial_does_not_fallback(self):
        providers = (
            ResearchProviderRegistry()
        )

        providers.register(
            provider(
                "alpha",
                quality=1.0,
            )
        )

        providers.register(
            provider(
                "beta",
                quality=0.5,
            )
        )

        tools = ToolRegistry(
            firewall=DenyFirewall()
        )

        register_tool(
            tools,
            "alpha",
            lambda **kwargs: "alpha",
        )

        beta_calls = []

        register_tool(
            tools,
            "beta",
            lambda **kwargs: (
                beta_calls.append(True)
            ),
        )

        runtime = GovernedResearchRuntime(
            providers,
            tools,
        )

        with self.assertRaisesRegex(
            PermissionError,
            "synthetic firewall denial",
        ):
            runtime.execute(
                ResearchRequest(
                    "TASK-FB-7",
                    ResearchCapability.SEARCH,
                )
            )

        self.assertEqual(
            beta_calls,
            [],
        )

        self.assertEqual(
            len(tools.history),
            1,
        )

        self.assertEqual(
            tools.history[0].status,
            ToolExecutionStatus.DENIED,
        )

    def test_existing_forbidden_provider_is_preserved(self):
        providers = (
            ResearchProviderRegistry()
        )

        providers.register(
            provider(
                "alpha",
                quality=1.0,
            )
        )

        providers.register(
            provider(
                "beta",
                quality=0.8,
            )
        )

        providers.register(
            provider(
                "gamma",
                quality=0.5,
            )
        )

        tools = ToolRegistry()

        register_tool(
            tools,
            "alpha",
            lambda **kwargs: "alpha",
        )

        register_tool(
            tools,
            "beta",
            lambda **kwargs: (
                (_ for _ in ()).throw(
                    RuntimeError("failure")
                )
            ),
        )

        register_tool(
            tools,
            "gamma",
            lambda **kwargs: "gamma",
        )

        result = GovernedResearchRuntime(
            providers,
            tools,
        ).execute(
            ResearchRequest(
                "TASK-FB-8",
                ResearchCapability.SEARCH,
                forbidden_provider_ids={
                    "alpha"
                },
            )
        )

        self.assertEqual(
            result.provider_id,
            "gamma",
        )

        self.assertEqual(
            [
                row.provider_id
                for row in result.attempts
            ],
            [
                "beta",
                "gamma",
            ],
        )

    def test_fallback_respects_deterministic_ranking(self):
        providers = (
            ResearchProviderRegistry()
        )

        providers.register(
            provider(
                "alpha",
                quality=1.0,
            )
        )

        providers.register(
            provider(
                "beta",
                quality=0.9,
            )
        )

        providers.register(
            provider(
                "gamma",
                quality=0.8,
            )
        )

        tools = ToolRegistry()

        register_tool(
            tools,
            "alpha",
            lambda **kwargs: (
                (_ for _ in ()).throw(
                    RuntimeError("failure")
                )
            ),
        )

        register_tool(
            tools,
            "beta",
            lambda **kwargs: "beta",
        )

        register_tool(
            tools,
            "gamma",
            lambda **kwargs: "gamma",
        )

        result = GovernedResearchRuntime(
            providers,
            tools,
        ).execute(
            ResearchRequest(
                "TASK-FB-9",
                ResearchCapability.SEARCH,
            )
        )

        self.assertEqual(
            result.provider_id,
            "beta",
        )

        self.assertEqual(
            [
                row.provider_id
                for row in result.attempts
            ],
            [
                "alpha",
                "beta",
            ],
        )

    def test_concurrent_same_task_and_tool_classify_independently(self):
        providers = (
            ResearchProviderRegistry()
        )

        providers.register(
            provider("alpha")
        )

        tools = ToolRegistry()
        barrier = threading.Barrier(2)

        def fail(**kwargs):
            barrier.wait(timeout=5)
            raise RuntimeError(
                "synthetic concurrent failure"
            )

        register_tool(
            tools,
            "alpha",
            fail,
        )

        runtime = GovernedResearchRuntime(
            providers,
            tools,
        )

        errors = []
        lock = threading.Lock()

        def worker():
            try:
                runtime.execute(
                    ResearchRequest(
                        "TASK-CONCURRENT-SAME",
                        ResearchCapability.SEARCH,
                    )
                )
            except Exception as exc:
                with lock:
                    errors.append(exc)

        threads = [
            threading.Thread(
                target=worker
            )
            for _ in range(2)
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
            len(errors),
            2,
        )

        self.assertTrue(
            all(
                isinstance(
                    exc,
                    ResearchProvidersExhaustedError,
                )
                for exc in errors
            )
        )

        for exc in errors:
            self.assertEqual(
                len(exc.attempts),
                1,
            )

            self.assertEqual(
                exc.attempts[
                    0
                ].provider_id,
                "alpha",
            )

            self.assertEqual(
                exc.attempts[
                    0
                ].status,
                (
                    ResearchAttemptStatus
                    .EXECUTION_FAILED
                ),
            )

            self.assertIsInstance(
                exc.__cause__,
                RuntimeError,
            )

        self.assertEqual(
            [
                invocation.status
                for invocation
                in tools.history
            ].count(
                ToolExecutionStatus.FAILED
            ),
            2,
        )


if __name__ == "__main__":
    unittest.main()
