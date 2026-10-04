import unittest

from maestro.enums import (
    CouncilId,
    SideEffectLevel,
    ToolExecutionStatus,
)
from maestro.research import (
    GovernedResearchRuntime,
    ResearchCapability,
    ResearchProviderDescriptor,
    ResearchProviderRegistry,
    ResearchProviderStatus,
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
    local=False,
    status=ResearchProviderStatus.AVAILABLE,
    quality=0.5,
    cost=0.0,
    latency=0.0,
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
            ),
        },
        local=local,
        status=status,
        quality_score=quality,
        cost_score=cost,
        latency_score=latency,
    )


def register_search_tool(
    tools,
    provider_id,
    handler=lambda **kwargs: kwargs,
    *,
    councils=frozenset(
        {CouncilId.RX}
    ),
    level=SideEffectLevel.A0_READ_ONLY,
    capabilities=None,
    provider_binding=None,
    policy=False,
    human=False,
):
    if capabilities is None:
        binding = (
            provider_id
            if provider_binding is None
            else provider_binding
        )

        capabilities = (
            "research.search",
            f"research.provider:{binding}",
        )

    tools.register(
        ToolSpec(
            name=f"{provider_id}.search",
            description="Fake search",
            capabilities=capabilities,
            allowed_councils=councils,
            side_effect_level=level,
            requires_policy_approval=policy,
            requires_human_approval=human,
        ),
        handler,
    )


class GovernedResearchRuntimeTests(
    unittest.TestCase
):
    def test_request_freezes_arguments_and_forbidden(self):
        request = ResearchRequest(
            task_id="TASK-RX-RUNTIME",
            capability=(
                ResearchCapability.SEARCH
            ),
            arguments={
                "query": "maestro"
            },
            forbidden_provider_ids={
                "blocked"
            },
        )

        with self.assertRaises(
            TypeError
        ):
            request.arguments[
                "query"
            ] = "changed"

        self.assertEqual(
            request.forbidden_provider_ids,
            frozenset(
                {"blocked"}
            ),
        )

    def test_route_prefers_available_over_degraded(self):
        providers = (
            ResearchProviderRegistry()
        )

        providers.register(
            provider(
                "degraded-local",
                local=True,
                status=(
                    ResearchProviderStatus.DEGRADED
                ),
                quality=1.0,
            )
        )

        providers.register(
            provider(
                "available-remote",
                local=False,
                quality=0.1,
            )
        )

        runtime = GovernedResearchRuntime(
            providers,
            ToolRegistry(),
        )

        decision = runtime.route(
            ResearchRequest(
                "TASK-1",
                ResearchCapability.SEARCH,
            )
        )

        self.assertEqual(
            decision.provider_id,
            "available-remote",
        )

    def test_route_prefers_local_when_requested(self):
        providers = (
            ResearchProviderRegistry()
        )

        providers.register(
            provider(
                "remote",
                quality=1.0,
            )
        )

        providers.register(
            provider(
                "local",
                local=True,
                quality=0.1,
            )
        )

        decision = GovernedResearchRuntime(
            providers,
            ToolRegistry(),
        ).route(
            ResearchRequest(
                "TASK-2",
                ResearchCapability.SEARCH,
                preferred_local=True,
            )
        )

        self.assertEqual(
            decision.provider_id,
            "local",
        )

    def test_route_uses_quality_cost_latency_and_id(self):
        providers = (
            ResearchProviderRegistry()
        )

        providers.register(
            provider(
                "zeta",
                quality=0.8,
                cost=1.0,
                latency=1.0,
            )
        )

        providers.register(
            provider(
                "beta",
                quality=0.9,
                cost=5.0,
                latency=5.0,
            )
        )

        providers.register(
            provider(
                "alpha",
                quality=0.9,
                cost=1.0,
                latency=1.0,
            )
        )

        decision = GovernedResearchRuntime(
            providers,
            ToolRegistry(),
        ).route(
            ResearchRequest(
                "TASK-3",
                ResearchCapability.SEARCH,
                preferred_local=False,
            )
        )

        self.assertEqual(
            decision.provider_id,
            "alpha",
        )

    def test_no_eligible_provider_raises(self):
        runtime = GovernedResearchRuntime(
            ResearchProviderRegistry(),
            ToolRegistry(),
        )

        with self.assertRaises(
            LookupError
        ):
            runtime.route(
                ResearchRequest(
                    "TASK-4",
                    ResearchCapability.SEARCH,
                )
            )

    def test_forbidden_provider_is_excluded(self):
        providers = (
            ResearchProviderRegistry()
        )

        providers.register(
            provider(
                "best",
                quality=1.0,
            )
        )

        providers.register(
            provider(
                "second",
                quality=0.5,
            )
        )

        decision = GovernedResearchRuntime(
            providers,
            ToolRegistry(),
        ).route(
            ResearchRequest(
                "TASK-5",
                ResearchCapability.SEARCH,
                forbidden_provider_ids=(
                    frozenset(
                        {"best"}
                    )
                ),
            )
        )

        self.assertEqual(
            decision.provider_id,
            "second",
        )

    def test_missing_tool_fails_closed(self):
        providers = (
            ResearchProviderRegistry()
        )
        providers.register(
            provider("alpha")
        )

        runtime = GovernedResearchRuntime(
            providers,
            ToolRegistry(),
        )

        with self.assertRaises(
            ResearchRuntimeConfigurationError
        ):
            runtime.execute(
                ResearchRequest(
                    "TASK-6",
                    ResearchCapability.SEARCH,
                )
            )

    def test_tool_must_allow_rx(self):
        providers = (
            ResearchProviderRegistry()
        )
        providers.register(
            provider("alpha")
        )

        tools = ToolRegistry()

        register_search_tool(
            tools,
            "alpha",
            councils=frozenset(
                {CouncilId.IT}
            ),
        )

        with self.assertRaises(
            ResearchRuntimeConfigurationError
        ):
            GovernedResearchRuntime(
                providers,
                tools,
            ).execute(
                ResearchRequest(
                    "TASK-7",
                    ResearchCapability.SEARCH,
                )
            )

    def test_tool_must_be_a0_read_only(self):
        providers = (
            ResearchProviderRegistry()
        )
        providers.register(
            provider("alpha")
        )

        tools = ToolRegistry()

        register_search_tool(
            tools,
            "alpha",
            level=(
                SideEffectLevel
                .A1_REVERSIBLE_LOCAL
            ),
        )

        with self.assertRaises(
            ResearchRuntimeConfigurationError
        ):
            GovernedResearchRuntime(
                providers,
                tools,
            ).execute(
                ResearchRequest(
                    "TASK-8",
                    ResearchCapability.SEARCH,
                )
            )

    def test_tool_must_advertise_research_capability(self):
        providers = (
            ResearchProviderRegistry()
        )
        providers.register(
            provider("alpha")
        )

        tools = ToolRegistry()

        register_search_tool(
            tools,
            "alpha",
            capabilities=(
                "repository.read",
            ),
        )

        with self.assertRaises(
            ResearchRuntimeConfigurationError
        ):
            GovernedResearchRuntime(
                providers,
                tools,
            ).execute(
                ResearchRequest(
                    "TASK-9",
                    ResearchCapability.SEARCH,
                )
            )

    def test_a0_tool_must_not_hide_approval_requirement(self):
        providers = (
            ResearchProviderRegistry()
        )
        providers.register(
            provider("alpha")
        )

        tools = ToolRegistry()

        register_search_tool(
            tools,
            "alpha",
            human=True,
        )

        with self.assertRaises(
            ResearchRuntimeConfigurationError
        ):
            GovernedResearchRuntime(
                providers,
                tools,
            ).execute(
                ResearchRequest(
                    "TASK-10",
                    ResearchCapability.SEARCH,
                )
            )

    def test_execute_crosses_tool_registry_as_rx(self):
        providers = (
            ResearchProviderRegistry()
        )
        providers.register(
            provider("alpha")
        )

        tools = ToolRegistry()

        register_search_tool(
            tools,
            "alpha",
            handler=lambda query: {
                "query": query,
                "results": ["one"],
            },
        )

        runtime = GovernedResearchRuntime(
            providers,
            tools,
        )

        result = runtime.execute(
            ResearchRequest(
                "TASK-11",
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
            result.output["query"],
            "maestro",
        )

        invocation = tools.history[-1]

        self.assertEqual(
            invocation.actor,
            CouncilId.RX,
        )
        self.assertEqual(
            invocation.tool_name,
            "alpha.search",
        )
        self.assertEqual(
            invocation.status,
            ToolExecutionStatus.EXECUTED,
        )

    def test_handler_failure_is_recorded_and_propagated(self):
        providers = (
            ResearchProviderRegistry()
        )
        providers.register(
            provider("alpha")
        )

        tools = ToolRegistry()

        def fail(**kwargs):
            raise ValueError(
                "provider failure"
            )

        register_search_tool(
            tools,
            "alpha",
            handler=fail,
        )

        runtime = GovernedResearchRuntime(
            providers,
            tools,
        )

        with self.assertRaisesRegex(
            ValueError,
            "provider failure",
        ):
            runtime.execute(
                ResearchRequest(
                    "TASK-12",
                    ResearchCapability.SEARCH,
                )
            )

        self.assertEqual(
            tools.history[-1].status,
            ToolExecutionStatus.FAILED,
        )

    def test_request_deep_freezes_nested_arguments(self):
        source = {
            "filters": {
                "domains": [
                    "example.com"
                ]
            }
        }

        request = ResearchRequest(
            "TASK-13",
            ResearchCapability.SEARCH,
            arguments=source,
        )

        source["filters"]["domains"].append(
            "mutated.example"
        )

        self.assertEqual(
            request.arguments[
                "filters"
            ][
                "domains"
            ],
            ("example.com",),
        )

        with self.assertRaises(
            TypeError
        ):
            request.arguments[
                "filters"
            ][
                "extra"
            ] = True

        with self.assertRaises(
            AttributeError
        ):
            request.arguments[
                "filters"
            ][
                "domains"
            ].append(
                "x"
            )

    def test_request_rejects_non_json_arguments(self):
        with self.assertRaises(
            TypeError
        ):
            ResearchRequest(
                "TASK-14",
                ResearchCapability.SEARCH,
                arguments={
                    "bad": object()
                },
            )

        with self.assertRaises(
            ValueError
        ):
            ResearchRequest(
                "TASK-14B",
                ResearchCapability.SEARCH,
                arguments={
                    "bad": float("nan")
                },
            )

    def test_forbidden_provider_ids_are_canonicalized(self):
        request = ResearchRequest(
            "TASK-15",
            ResearchCapability.SEARCH,
            forbidden_provider_ids={
                " alpha "
            },
        )

        self.assertEqual(
            request.forbidden_provider_ids,
            frozenset(
                {"alpha"}
            ),
        )

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
                quality=0.1,
            )
        )

        decision = GovernedResearchRuntime(
            providers,
            ToolRegistry(),
        ).route(request)

        self.assertEqual(
            decision.provider_id,
            "beta",
        )

    def test_provider_tool_binding_must_match(self):
        providers = (
            ResearchProviderRegistry()
        )
        providers.register(
            provider("alpha")
        )

        tools = ToolRegistry()

        register_search_tool(
            tools,
            "alpha",
            provider_binding="beta",
        )

        with self.assertRaisesRegex(
            ResearchRuntimeConfigurationError,
            "binding mismatch",
        ):
            GovernedResearchRuntime(
                providers,
                tools,
            ).execute(
                ResearchRequest(
                    "TASK-16",
                    ResearchCapability.SEARCH,
                )
            )

    def test_fetch_uses_governed_fetch_tool(self):
        providers = (
            ResearchProviderRegistry()
        )

        providers.register(
            ResearchProviderDescriptor(
                provider_id="fetcher",
                capabilities=frozenset(
                    {
                        ResearchCapability.FETCH,
                    }
                ),
                tool_names={
                    ResearchCapability.FETCH: (
                        "fetcher.fetch"
                    )
                },
            )
        )

        tools = ToolRegistry()

        tools.register(
            ToolSpec(
                name="fetcher.fetch",
                description="Fake fetch",
                capabilities=(
                    "research.fetch",
                    "research.provider:fetcher",
                ),
                allowed_councils=frozenset(
                    {CouncilId.RX}
                ),
                side_effect_level=(
                    SideEffectLevel.A0_READ_ONLY
                ),
            ),
            lambda url: {
                "url": url,
                "body": "fake",
            },
        )

        result = GovernedResearchRuntime(
            providers,
            tools,
        ).execute(
            ResearchRequest(
                "TASK-17",
                ResearchCapability.FETCH,
                arguments={
                    "url": (
                        "https://example.com/doc"
                    )
                },
            )
        )

        self.assertEqual(
            result.provider_id,
            "fetcher",
        )

        self.assertEqual(
            result.tool_name,
            "fetcher.fetch",
        )

        self.assertEqual(
            result.output["body"],
            "fake",
        )

        self.assertEqual(
            tools.history[-1].actor,
            CouncilId.RX,
        )

    def test_execute_thaws_nested_arguments_for_tool(self):
        providers = (
            ResearchProviderRegistry()
        )
        providers.register(
            provider("alpha")
        )

        tools = ToolRegistry()

        observed = {}

        def handler(filters):
            observed["filters"] = filters
            return {
                "ok": True
            }

        register_search_tool(
            tools,
            "alpha",
            handler=handler,
        )

        request = ResearchRequest(
            "TASK-18",
            ResearchCapability.SEARCH,
            arguments={
                "filters": {
                    "domains": [
                        "example.com",
                        "example.org",
                    ]
                }
            },
        )

        result = GovernedResearchRuntime(
            providers,
            tools,
        ).execute(request)

        self.assertTrue(
            result.output["ok"]
        )

        self.assertIsInstance(
            observed["filters"],
            dict,
        )

        self.assertIsInstance(
            observed["filters"]["domains"],
            list,
        )

        self.assertEqual(
            observed["filters"]["domains"],
            [
                "example.com",
                "example.org",
            ],
        )

        observed["filters"]["domains"].append(
            "handler-local.example"
        )

        self.assertEqual(
            request.arguments[
                "filters"
            ][
                "domains"
            ],
            (
                "example.com",
                "example.org",
            ),
        )


if __name__ == "__main__":
    unittest.main()
