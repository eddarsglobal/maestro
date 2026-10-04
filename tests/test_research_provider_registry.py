import unittest

from maestro.research import (
    ResearchCapability,
    ResearchProviderDescriptor,
    ResearchProviderRegistry,
    ResearchProviderStatus,
)


def descriptor(
    provider_id="alpha",
    *,
    capabilities=None,
    tool_names=None,
    status=ResearchProviderStatus.AVAILABLE,
    quality_score=0.5,
    cost_score=0.0,
    latency_score=0.0,
):
    capabilities = (
        frozenset(
            {
                ResearchCapability.SEARCH,
                ResearchCapability.FETCH,
            }
        )
        if capabilities is None
        else capabilities
    )

    tool_names = (
        {
            ResearchCapability.SEARCH: (
                f"{provider_id}.search"
            ),
            ResearchCapability.FETCH: (
                f"{provider_id}.fetch"
            ),
        }
        if tool_names is None
        else tool_names
    )

    return ResearchProviderDescriptor(
        provider_id=provider_id,
        capabilities=capabilities,
        tool_names=tool_names,
        status=status,
        quality_score=quality_score,
        cost_score=cost_score,
        latency_score=latency_score,
    )


class ResearchProviderRegistryTests(
    unittest.TestCase
):
    def test_descriptor_serializes(self):
        row = descriptor(
            "example"
        )

        data = row.to_dict()

        self.assertEqual(
            data["provider_id"],
            "example",
        )
        self.assertEqual(
            data["capabilities"],
            ["FETCH", "SEARCH"],
        )
        self.assertEqual(
            data["tool_names"]["SEARCH"],
            "example.search",
        )

    def test_empty_provider_id_rejected(self):
        with self.assertRaises(
            ValueError
        ):
            descriptor(
                "   "
            )

    def test_empty_capabilities_rejected(self):
        with self.assertRaises(
            ValueError
        ):
            descriptor(
                capabilities=frozenset(),
                tool_names={},
            )

    def test_tool_mapping_must_cover_capabilities(self):
        with self.assertRaises(
            ValueError
        ):
            descriptor(
                capabilities=frozenset(
                    {
                        ResearchCapability.SEARCH,
                        ResearchCapability.FETCH,
                    }
                ),
                tool_names={
                    ResearchCapability.SEARCH: (
                        "example.search"
                    ),
                },
            )

    def test_tool_name_rejects_nul(self):
        with self.assertRaises(
            ValueError
        ):
            descriptor(
                capabilities=frozenset(
                    {
                        ResearchCapability.SEARCH,
                    }
                ),
                tool_names={
                    ResearchCapability.SEARCH: (
                        "bad\x00tool"
                    ),
                },
            )

    def test_invalid_scores_rejected(self):
        cases = (
            {
                "quality_score": 1.1,
            },
            {
                "quality_score": -0.1,
            },
            {
                "cost_score": -1.0,
            },
            {
                "latency_score": -1.0,
            },
            {
                "quality_score": float("nan"),
            },
        )

        for kwargs in cases:
            with self.subTest(
                kwargs=kwargs
            ):
                with self.assertRaises(
                    ValueError
                ):
                    descriptor(
                        **kwargs
                    )

    def test_registry_register_and_lookup(self):
        registry = (
            ResearchProviderRegistry()
        )

        row = descriptor(
            "example"
        )

        registry.register(row)

        self.assertIs(
            registry.descriptor("example"),
            row,
        )

        self.assertEqual(
            registry.eligible(
                ResearchCapability.SEARCH
            ),
            [row],
        )

    def test_duplicate_provider_rejected(self):
        registry = (
            ResearchProviderRegistry()
        )

        registry.register(
            descriptor("example")
        )

        with self.assertRaises(
            ValueError
        ):
            registry.register(
                descriptor("example")
            )

    def test_unavailable_is_not_eligible(self):
        registry = (
            ResearchProviderRegistry()
        )

        registry.register(
            descriptor("example")
        )

        registry.set_status(
            "example",
            ResearchProviderStatus.DEGRADED,
        )

        self.assertEqual(
            len(
                registry.eligible(
                    ResearchCapability.SEARCH
                )
            ),
            1,
        )

        registry.set_status(
            "example",
            ResearchProviderStatus.UNAVAILABLE,
        )

        self.assertEqual(
            registry.eligible(
                ResearchCapability.SEARCH
            ),
            [],
        )

    def test_forbidden_and_order_are_deterministic(self):
        registry = (
            ResearchProviderRegistry()
        )

        registry.register(
            descriptor("zeta")
        )
        registry.register(
            descriptor("alpha")
        )
        registry.register(
            descriptor("middle")
        )

        rows = registry.eligible(
            ResearchCapability.SEARCH,
            forbidden_provider_ids=(
                frozenset(
                    {"middle"}
                )
            ),
        )

        self.assertEqual(
            [
                row.provider_id
                for row in rows
            ],
            [
                "alpha",
                "zeta",
            ],
        )


if __name__ == "__main__":
    unittest.main()
