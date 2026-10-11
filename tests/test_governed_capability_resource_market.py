from __future__ import annotations

import ast
import unittest

from dataclasses import replace
from pathlib import Path

from maestro.intelligence_market.governed_capability_resource_market import (
    CapabilityResourceMarketInvariantError,
    GovernedCapabilityResourceMarket,
    IntelligenceResourceCandidate,
    ResourceEvidenceState as E,
    ResourceLocality,
    ResourceSelectionIncompleteError,
    ResourceSelectionPolicy,
)
from maestro.orchestration.governed_mission_foundation import (
    CapabilityRule,
    GovernedMissionFoundation,
    MissionContract,
)


SOURCE = Path(
    "src/maestro/intelligence_market/"
    "governed_capability_resource_market.py"
)

DOC = Path(
    "docs/"
    "GOVERNED_CAPABILITY_RESOURCE_MARKET_CONSTITUTION.md"
)


def mission():
    contract = MissionContract(
        objective=(
            "Analyze software locally "
            "with strong privacy"
        ),
        scope=(
            "Reasoning and software analysis"
        ),
        requested_output=(
            "Verified technical analysis"
        ),
        constraints=(
            "Local execution required",
            "High privacy required",
        ),
        acceptance_criteria=(
            "Reasoning evidence passes",
        ),
        authority_requirements=(
            "EX routing",
            "AY acceptance",
        ),
        evidence_obligations=(
            "Resource evidence",
        ),
    )

    demand = (
        GovernedMissionFoundation
        .analyze(
            contract,
            (
                CapabilityRule(
                    "RULE-R",
                    "GENERAL_REASONING",
                    (
                        "analyze",
                        "reasoning",
                    ),
                    "Reasoning capability required.",
                ),
            ),
        )
    )

    graph = (
        GovernedCapabilityResourceMarket
        .synthesize_capability_graph(
            demand
        )
    )

    return contract, demand, graph


def policy(contract):
    return ResourceSelectionPolicy(
        mission_contract_id=(
            contract.contract_id
        ),
        constraint_refs=(
            "High privacy required",
            "Local execution required",
        ),
        min_evidence_quality=0.80,
        min_reliability=0.80,
        min_privacy_score=0.90,
        max_cost_units=100,
        max_latency_ms=1000,
        require_local=True,
    )


def candidate(
    resource_id,
    *,
    evidence=0.95,
    reliability=0.95,
    privacy=0.95,
    cost=20,
    latency=100,
    locality=ResourceLocality.LOCAL,
    availability=E.PASS,
    provider=None,
    model=None,
    runtime=None,
):
    return IntelligenceResourceCandidate(
        resource_id=resource_id,
        capabilities=(
            "GENERAL_REASONING",
        ),
        availability=availability,
        evidence_quality=evidence,
        reliability=reliability,
        privacy_score=privacy,
        cost_units=cost,
        latency_ms=latency,
        locality=locality,
        provider_ref=provider,
        model_ref=model,
        runtime_ref=runtime,
    )


class GovernedCapabilityResourceMarketTests(
    unittest.TestCase
):
    def test_01_constitution_contains_laws(self):
        text = DOC.read_text(
            encoding="utf-8"
        )

        for number in range(
            1,
            11,
        ):
            self.assertIn(
                f"CIM-{number:02d}",
                text,
            )

        for invariant in (
            "CAPABILITY != PROVIDER",
            "CAPABILITY != MODEL",
            "CAPABILITY != RUNTIME",
            "TECHNOLOGY IDENTITY != MISSION SEMANTICS",
            "RESOURCE AVAILABLE != RESOURCE ELIGIBLE",
            "RESOURCE ELIGIBLE != RESOURCE AUTHORIZED",
            "UNKNOWN != AVAILABLE",
            "RESOURCE SELECTED != RESOURCE ACTIVATED",
            "RESOURCE SELECTED != EXECUTION AUTHORIZED",
            "MODEL SELECTED != MODEL AUTHORITY",
            "PROVIDER SELECTED != PROVIDER AUTHORITY",
            "MODEL SWITCH != MISSION CHANGE",
            "PROVIDER SWITCH != AUTHORITY CHANGE",
            "RUNTIME SWITCH != CORE MUTATION",
        ):
            self.assertIn(
                invariant,
                text,
            )

    def test_02_capability_graph_is_generic_and_deterministic(self):
        _, demand, a = mission()

        b = (
            GovernedCapabilityResourceMarket
            .synthesize_capability_graph(
                demand
            )
        )

        self.assertEqual(
            a.graph_id,
            b.graph_id,
        )

        self.assertEqual(
            a.capability_ids,
            (
                "GENERAL_REASONING",
            ),
        )

        payload = a.to_dict()

        encoded = repr(
            payload
        ).casefold()

        self.assertNotIn(
            "provider_ref",
            encoded,
        )
        self.assertNotIn(
            "model_ref",
            encoded,
        )
        self.assertNotIn(
            "runtime_ref",
            encoded,
        )

        self.assertFalse(
            a.provider_bound
        )
        self.assertFalse(
            a.model_bound
        )
        self.assertFalse(
            a.runtime_bound
        )

    def test_03_selection_uses_evidence_reliability_privacy_cost_and_latency(self):
        contract, _, graph = mission()

        selected = (
            GovernedCapabilityResourceMarket
            .select(
                graph,
                (
                    candidate(
                        "R-A",
                        evidence=0.90,
                        reliability=0.90,
                        privacy=0.95,
                        cost=50,
                        latency=300,
                    ),
                    candidate(
                        "R-B",
                        evidence=0.95,
                        reliability=0.95,
                        privacy=0.99,
                        cost=30,
                        latency=200,
                    ),
                ),
                policy(
                    contract
                ),
            )
        )

        self.assertEqual(
            selected.selected_resource_ids,
            (
                "R-B",
            ),
        )

    def test_04_ranking_is_deterministic_and_order_independent(self):
        contract, _, graph = mission()

        a = candidate(
            "A-RESOURCE"
        )

        b = candidate(
            "B-RESOURCE"
        )

        first = (
            GovernedCapabilityResourceMarket
            .select(
                graph,
                (
                    b,
                    a,
                ),
                policy(
                    contract
                ),
            )
        )

        second = (
            GovernedCapabilityResourceMarket
            .select(
                graph,
                (
                    a,
                    b,
                ),
                policy(
                    contract
                ),
            )
        )

        self.assertEqual(
            first.selection_id,
            second.selection_id,
        )

        self.assertEqual(
            first.selected_resource_ids,
            (
                "A-RESOURCE",
            ),
        )

    def test_05_unknown_or_failed_availability_fails_closed(self):
        contract, _, graph = mission()

        for state in (
            E.UNKNOWN,
            E.FAIL,
        ):
            with self.subTest(
                state=state.value
            ):
                with self.assertRaises(
                    ResourceSelectionIncompleteError
                ):
                    GovernedCapabilityResourceMarket.select(
                        graph,
                        (
                            candidate(
                                "UNAVAILABLE",
                                availability=state,
                            ),
                        ),
                        policy(
                            contract
                        ),
                    )

    def test_06_locality_privacy_and_limits_fail_closed(self):
        contract, _, graph = mission()

        bad = (
            candidate(
                "REMOTE",
                locality=(
                    ResourceLocality.REMOTE
                ),
            ),
            candidate(
                "LOW-PRIVACY",
                privacy=0.50,
            ),
            candidate(
                "EXPENSIVE",
                cost=1000,
            ),
            candidate(
                "SLOW",
                latency=5000,
            ),
        )

        for item in bad:
            with self.subTest(
                resource=item.resource_id
            ):
                with self.assertRaises(
                    ResourceSelectionIncompleteError
                ):
                    GovernedCapabilityResourceMarket.select(
                        graph,
                        (
                            item,
                        ),
                        policy(
                            contract
                        ),
                    )

    def test_07_policy_must_bind_exact_mission_contract(self):
        _, _, graph = mission()

        wrong = ResourceSelectionPolicy(
            mission_contract_id=(
                "MC-WRONG"
            ),
            constraint_refs=(
                "Local execution required",
            ),
            min_evidence_quality=0.0,
            min_reliability=0.0,
            min_privacy_score=0.0,
            max_cost_units=1000,
            max_latency_ms=10000,
            require_local=False,
        )

        with self.assertRaises(
            CapabilityResourceMarketInvariantError
        ):
            GovernedCapabilityResourceMarket.select(
                graph,
                (
                    candidate(
                        "R"
                    ),
                ),
                wrong,
            )

    def test_08_provider_model_runtime_switch_preserves_capability_graph(self):
        contract, _, graph = mission()

        local_a = candidate(
            "RESOURCE-A",
            provider="PROVIDER-A",
            model="MODEL-A",
            runtime="RUNTIME-A",
        )

        local_b = candidate(
            "RESOURCE-B",
            provider="PROVIDER-B",
            model="MODEL-B",
            runtime="RUNTIME-B",
        )

        selection_a = (
            GovernedCapabilityResourceMarket
            .select(
                graph,
                (
                    local_a,
                ),
                policy(
                    contract
                ),
            )
        )

        selection_b = (
            GovernedCapabilityResourceMarket
            .select(
                graph,
                (
                    local_b,
                ),
                policy(
                    contract
                ),
            )
        )

        self.assertEqual(
            graph.capability_ids,
            (
                "GENERAL_REASONING",
            ),
        )

        self.assertEqual(
            selection_a.capability_graph_id,
            selection_b.capability_graph_id,
        )

        self.assertNotEqual(
            selection_a.selected_resource_ids,
            selection_b.selected_resource_ids,
        )

    def test_09_selection_never_transfers_authority(self):
        contract, _, graph = mission()

        result = (
            GovernedCapabilityResourceMarket
            .select(
                graph,
                (
                    candidate(
                        "RESOURCE",
                        provider="P",
                        model="M",
                        runtime="R",
                    ),
                ),
                policy(
                    contract
                ),
            )
        )

        fields = (
            "activation_authorized",
            "execution_authorized",
            "provider_authority_granted",
            "model_authority_granted",
            "runtime_authority_granted",
            "mission_authority_transferred",
            "system_truth_asserted",
        )

        for field_name in fields:
            self.assertFalse(
                getattr(
                    result,
                    field_name,
                )
            )

            with self.assertRaises(
                CapabilityResourceMarketInvariantError
            ):
                replace(
                    result,
                    **{
                        field_name: True
                    },
                )

    def test_10_module_is_passive_and_provider_independent(self):
        tree = ast.parse(
            SOURCE.read_text(
                encoding="utf-8"
            )
        )

        imports = set()
        calls = set()

        for node in ast.walk(tree):
            if isinstance(
                node,
                ast.Import,
            ):
                imports.update(
                    alias.name
                    for alias in node.names
                )

            elif isinstance(
                node,
                ast.ImportFrom,
            ):
                if node.module:
                    imports.add(
                        node.module
                    )

            elif isinstance(
                node,
                ast.Call,
            ):
                if isinstance(
                    node.func,
                    ast.Name,
                ):
                    calls.add(
                        node.func.id
                    )

                elif isinstance(
                    node.func,
                    ast.Attribute,
                ):
                    calls.add(
                        node.func.attr
                    )

        forbidden_import_roots = (
            "maestro.providers",
            "maestro.sovereign.router",
            "maestro.autonomous.provider_adapters",
            "subprocess",
            "socket",
            "requests",
            "httpx",
            "aiohttp",
            "sqlite3",
        )

        bad_imports = {
            name
            for name in imports
            if any(
                name == root
                or name.startswith(
                    root + "."
                )
                for root
                in forbidden_import_roots
            )
        }

        self.assertEqual(
            bad_imports,
            set(),
        )

        forbidden_calls = {
            "execute",
            "generate",
            "activate",
            "authorize",
            "install",
            "route",
            "dispatch",
            "commit",
            "write_text",
            "write_bytes",
        }

        self.assertEqual(
            calls & forbidden_calls,
            set(),
        )


if __name__ == "__main__":
    unittest.main()
