from __future__ import annotations

import ast
import unittest

from dataclasses import replace
from pathlib import Path

from maestro.intelligence_market.governed_capability_resource_market import (
    ResourceLocality,
)
from maestro.intelligence_market.governed_cost_performance_privacy_locality import (
    CostPerformancePrivacyLocalityInvariantError,
    GovernedCostPerformancePrivacyLocality,
    MissionConstraintUnsatisfiedError,
    MissionExecutionOptimizationPolicy,
    MissionResourcePerformanceEvidence,
)


SOURCE = Path(
    "src/maestro/intelligence_market/"
    "governed_cost_performance_privacy_locality.py"
)

DOC = Path(
    "docs/"
    "GOVERNED_COST_PERFORMANCE_PRIVACY_LOCALITY_CONSTITUTION.md"
)


def evidence(
    resource_id: str,
    *,
    locality: ResourceLocality,
    offline: bool,
    private: bool,
    privacy: float,
    reliability: float,
    outcome: float,
    cost: int,
    latency: int,
    energy: float,
    mission_contract_id: str = "MC-CPL",
):
    return MissionResourcePerformanceEvidence(
        mission_contract_id=mission_contract_id,
        resource_id=resource_id,
        capability_id="GENERAL_REASONING",
        cost_units=cost,
        latency_ms=latency,
        energy_millijoules=energy,
        locality=locality,
        reliability=reliability,
        outcome_score=outcome,
        privacy_score=privacy,
        offline_capable=offline,
        private_execution=private,
        cost_evidence_ref=(
            f"metric://{resource_id}/cost"
        ),
        latency_evidence_ref=(
            f"metric://{resource_id}/latency"
        ),
        energy_evidence_ref=(
            f"metric://{resource_id}/energy"
        ),
        locality_evidence_ref=(
            f"metric://{resource_id}/locality"
        ),
        reliability_evidence_ref=(
            f"metric://{resource_id}/reliability"
        ),
        outcome_evidence_ref=(
            f"metric://{resource_id}/outcome"
        ),
        privacy_evidence_ref=(
            f"metric://{resource_id}/privacy"
        ),
    )


def local_private(
    resource_id="LOCAL-A",
):
    return evidence(
        resource_id,
        locality=ResourceLocality.LOCAL,
        offline=True,
        private=True,
        privacy=0.97,
        reliability=0.95,
        outcome=0.90,
        cost=30,
        latency=220,
        energy=480.0,
    )


def remote_fast(
    resource_id="REMOTE-B",
):
    return evidence(
        resource_id,
        locality=ResourceLocality.REMOTE,
        offline=False,
        private=False,
        privacy=0.60,
        reliability=0.99,
        outcome=0.98,
        cost=10,
        latency=80,
        energy=120.0,
    )


def policy(
    **overrides,
):
    values = {
        "mission_contract_id": "MC-CPL",
        "constraint_refs": (
            "mission://constraints",
        ),
        "prefer_local": False,
        "prefer_offline": False,
        "prefer_private": False,
        "require_local": False,
        "require_offline": False,
        "require_private": False,
        "min_privacy_score": 0.0,
        "min_reliability": 0.0,
        "max_cost_units": 1000,
        "max_latency_ms": 10000,
        "max_energy_millijoules": 100000.0,
    }

    values.update(
        overrides
    )

    return MissionExecutionOptimizationPolicy(
        **values
    )


class GovernedCostPerformancePrivacyLocalityTests(
    unittest.TestCase
):
    def test_01_constitution_contains_laws_and_separations(self):
        text = DOC.read_text(
            encoding="utf-8"
        )

        for number in range(
            1,
            11,
        ):
            self.assertIn(
                f"CPL-{number:02d}",
                text,
            )

        for invariant in (
            "OPTIMIZATION METRIC != AUTHORITY",
            "LOW COST != LOW ENERGY",
            "PREFERENCE != REQUIREMENT",
            "LOCAL != OFFLINE",
            "LOCAL != PRIVATE",
            "SUFFICIENCY != OPTIMIZATION",
            "SELECTED != AUTHORIZED",
            "OPTIMIZATION != AUTHORIZATION",
            "RESOURCE SELECTED != RESOURCE EXECUTED",
        ):
            self.assertIn(
                invariant,
                text,
            )

    def test_02_performance_evidence_exposes_all_bm2_metrics_deterministically(self):
        first = local_private()
        second = local_private()

        self.assertEqual(
            first.evidence_id,
            second.evidence_id,
        )

        self.assertEqual(
            first.cost_units,
            30,
        )

        self.assertEqual(
            first.latency_ms,
            220,
        )

        self.assertEqual(
            first.energy_millijoules,
            480.0,
        )

        self.assertIs(
            first.locality,
            ResourceLocality.LOCAL,
        )

        self.assertEqual(
            first.reliability,
            0.95,
        )

        self.assertEqual(
            first.outcome_score,
            0.90,
        )

        for ref_name in (
            "cost_evidence_ref",
            "latency_evidence_ref",
            "energy_evidence_ref",
            "locality_evidence_ref",
            "reliability_evidence_ref",
            "outcome_evidence_ref",
            "privacy_evidence_ref",
        ):
            self.assertTrue(
                getattr(
                    first,
                    ref_name,
                )
            )

    def test_03_performance_and_optimization_evidence_never_become_authority(self):
        item = local_private()

        for field_name in (
            "optimization_authority_granted",
            "trust_granted",
            "activation_authorized",
            "execution_authorized",
            "effect_authorized",
            "network_authorized",
            "mission_authority_transferred",
            "system_truth_asserted",
        ):
            self.assertFalse(
                getattr(
                    item,
                    field_name,
                )
            )

            with self.assertRaises(
                CostPerformancePrivacyLocalityInvariantError
            ):
                replace(
                    item,
                    **{
                        field_name: True
                    },
                )

        selection = (
            GovernedCostPerformancePrivacyLocality
            .select(
                capability_id=(
                    "GENERAL_REASONING"
                ),
                policy=policy(),
                evidence=(
                    item,
                ),
            )
        )

        for field_name in (
            "optimization_authority_granted",
            "trust_granted",
            "activation_authorized",
            "execution_authorized",
            "effect_authorized",
            "network_authorized",
            "mission_authority_transferred",
            "system_truth_asserted",
        ):
            self.assertFalse(
                getattr(
                    selection,
                    field_name,
                )
            )

    def test_04_explicit_local_offline_private_preferences_affect_ranking(self):
        local = local_private()
        remote = remote_fast()

        selection = (
            GovernedCostPerformancePrivacyLocality
            .select(
                capability_id=(
                    "GENERAL_REASONING"
                ),
                policy=policy(
                    prefer_local=True,
                    prefer_offline=True,
                    prefer_private=True,
                ),
                evidence=(
                    remote,
                    local,
                ),
            )
        )

        self.assertEqual(
            selection.selected_resource_id,
            "LOCAL-A",
        )

        self.assertFalse(
            selection.execution_authorized
        )

    def test_05_required_local_execution_fails_closed(self):
        with self.assertRaises(
            MissionConstraintUnsatisfiedError
        ):
            GovernedCostPerformancePrivacyLocality.select(
                capability_id=(
                    "GENERAL_REASONING"
                ),
                policy=policy(
                    require_local=True,
                ),
                evidence=(
                    remote_fast(),
                ),
            )

    def test_06_required_offline_execution_fails_closed(self):
        local_online = replace(
            local_private(),
            offline_capable=False,
        )

        with self.assertRaises(
            MissionConstraintUnsatisfiedError
        ):
            GovernedCostPerformancePrivacyLocality.select(
                capability_id=(
                    "GENERAL_REASONING"
                ),
                policy=policy(
                    require_offline=True,
                ),
                evidence=(
                    local_online,
                ),
            )

    def test_07_private_and_privacy_constraints_fail_closed(self):
        not_private = replace(
            local_private(),
            private_execution=False,
        )

        with self.assertRaises(
            MissionConstraintUnsatisfiedError
        ):
            GovernedCostPerformancePrivacyLocality.select(
                capability_id=(
                    "GENERAL_REASONING"
                ),
                policy=policy(
                    require_private=True,
                ),
                evidence=(
                    not_private,
                ),
            )

        low_privacy = replace(
            local_private(),
            privacy_score=0.70,
        )

        with self.assertRaises(
            MissionConstraintUnsatisfiedError
        ):
            GovernedCostPerformancePrivacyLocality.select(
                capability_id=(
                    "GENERAL_REASONING"
                ),
                policy=policy(
                    min_privacy_score=0.95,
                ),
                evidence=(
                    low_privacy,
                ),
            )

    def test_08_cost_latency_energy_and_reliability_limits_fail_closed(self):
        item = local_private()

        cases = (
            {
                "max_cost_units": 20,
            },
            {
                "max_latency_ms": 100,
            },
            {
                "max_energy_millijoules": 300.0,
            },
            {
                "min_reliability": 0.99,
            },
        )

        for overrides in cases:
            with self.subTest(
                overrides=overrides
            ):
                with self.assertRaises(
                    MissionConstraintUnsatisfiedError
                ):
                    GovernedCostPerformancePrivacyLocality.select(
                        capability_id=(
                            "GENERAL_REASONING"
                        ),
                        policy=policy(
                            **overrides
                        ),
                        evidence=(
                            item,
                        ),
                    )

    def test_09_selection_is_mission_bound_deterministic_and_order_independent(self):
        a = local_private(
            "LOCAL-A"
        )

        b = evidence(
            "LOCAL-B",
            locality=ResourceLocality.LOCAL,
            offline=True,
            private=True,
            privacy=0.96,
            reliability=0.94,
            outcome=0.89,
            cost=25,
            latency=180,
            energy=400.0,
        )

        first = (
            GovernedCostPerformancePrivacyLocality
            .select(
                capability_id=(
                    "GENERAL_REASONING"
                ),
                policy=policy(),
                evidence=(
                    a,
                    b,
                ),
            )
        )

        second = (
            GovernedCostPerformancePrivacyLocality
            .select(
                capability_id=(
                    "GENERAL_REASONING"
                ),
                policy=policy(),
                evidence=(
                    b,
                    a,
                ),
            )
        )

        self.assertEqual(
            first.selection_id,
            second.selection_id,
        )

        self.assertEqual(
            first.selected_resource_id,
            "LOCAL-A",
        )

        wrong_mission = replace(
            b,
            mission_contract_id=(
                "MC-OTHER"
            ),
        )

        with self.assertRaises(
            CostPerformancePrivacyLocalityInvariantError
        ):
            GovernedCostPerformancePrivacyLocality.select(
                capability_id=(
                    "GENERAL_REASONING"
                ),
                policy=policy(),
                evidence=(
                    a,
                    wrong_mission,
                ),
            )

    def test_10_module_is_passive_and_execution_remains_downstream(self):
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
            "subprocess",
            "socket",
            "requests",
            "urllib",
            "httpx",
            "maestro.runtime.kernel",
            "maestro.state_machine",
            "maestro.providers",
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
            "activate",
            "authorize",
            "dispatch",
            "transition",
            "commit",
            "download",
            "request",
            "urlopen",
            "write_text",
            "write_bytes",
        }

        self.assertEqual(
            calls & forbidden_calls,
            set(),
        )


if __name__ == "__main__":
    unittest.main()
