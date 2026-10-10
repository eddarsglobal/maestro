from __future__ import annotations

import ast
import unittest
from dataclasses import replace
from pathlib import Path

from maestro.research.governed_capability_candidate import (
    GovernedCapabilityCandidate,
)
from maestro.research.governed_integration_adapter_candidate import (
    GovernedAdapterCandidate,
    GovernedIntegrationAdapterCandidateInvariantError,
    GovernedIntegrationAdapterCandidateProposer,
    GovernedIntegrationCandidate,
)


DOC = Path(
    "docs/"
    "GOVERNED_INTEGRATION_ADAPTER_CANDIDATE_CONSTITUTION.md"
)

SOURCE = Path(
    "src/maestro/research/"
    "governed_integration_adapter_candidate.py"
)


def capability() -> GovernedCapabilityCandidate:
    return GovernedCapabilityCandidate(
        candidate_id="GCC-test",
        landscape_change_id="TLC-test",
        current_snapshot_id="TLS-test",
        scope_id="future-runtime",
        subject_id="runtime.alpha",
        capability_term="vision",
        evidence_id="E1",
        source_ref="CLAIM-1",
        landscape_evidence_ids=(
            "E1",
            "E2",
        ),
    )


class GovernedIntegrationAdapterCandidateTests(
    unittest.TestCase
):
    def test_01_constitution_contains_ten_laws(self):
        text = DOC.read_text(
            encoding="utf-8"
        )

        for number in range(1, 11):
            self.assertIn(
                f"IAP-{number:02d}",
                text,
            )

        self.assertIn(
            "ADAPTER PROPOSAL != REGISTRATION",
            text,
        )

        self.assertIn(
            "INTEGRATION / ADAPTER PROPOSAL != "
            "ARCHITECTURE-EVOLUTION PROPOSAL",
            text,
        )

    def test_02_integration_only_proposal(self):
        source = capability()

        result = (
            GovernedIntegrationAdapterCandidateProposer
            .propose(
                source,
                interface_contract=(
                    "generic multimodal capability interface"
                ),
                integration_requirements=(
                    "sandbox",
                    "capability-contract",
                ),
            )
        )

        self.assertEqual(
            len(result.integration_candidates),
            1,
        )

        self.assertEqual(
            len(result.adapter_candidates),
            0,
        )

        proposal = result.integration_candidates[0]

        self.assertEqual(
            proposal.capability_candidate_id,
            source.candidate_id,
        )

        self.assertEqual(
            proposal.landscape_change_id,
            source.landscape_change_id,
        )

        self.assertEqual(
            proposal.evidence_id,
            source.evidence_id,
        )

        self.assertEqual(
            proposal.landscape_evidence_ids,
            source.landscape_evidence_ids,
        )

        self.assertEqual(
            proposal.verification_status,
            "UNVERIFIED_EXTERNAL",
        )

    def test_03_optional_adapter_proposal(self):
        source = capability()

        result = (
            GovernedIntegrationAdapterCandidateProposer
            .propose(
                source,
                interface_contract=(
                    "generic multimodal capability interface"
                ),
                adapter_kind=(
                    "GENERIC_CAPABILITY_ADAPTER"
                ),
                resource_contract=(
                    "replaceable intelligence resource"
                ),
            )
        )

        self.assertEqual(
            len(result.integration_candidates),
            1,
        )

        self.assertEqual(
            len(result.adapter_candidates),
            1,
        )

        integration = (
            result.integration_candidates[0]
        )

        adapter = result.adapter_candidates[0]

        self.assertEqual(
            adapter.integration_proposal_id,
            integration.proposal_id,
        )

        self.assertEqual(
            adapter.capability_candidate_id,
            source.candidate_id,
        )

        self.assertEqual(
            adapter.evidence_id,
            source.evidence_id,
        )

    def test_04_no_capability_candidate_produces_zero(self):
        result = (
            GovernedIntegrationAdapterCandidateProposer
            .propose(None)
        )

        self.assertEqual(
            result.size,
            0,
        )

        self.assertEqual(
            result.integration_candidates,
            (),
        )

        self.assertEqual(
            result.adapter_candidates,
            (),
        )

    def test_05_incomplete_adapter_contract_fails_closed(self):
        source = capability()

        cases = (
            {
                "adapter_kind": (
                    "GENERIC_ADAPTER"
                ),
                "resource_contract": None,
            },
            {
                "adapter_kind": None,
                "resource_contract": (
                    "generic resource"
                ),
            },
        )

        for case in cases:
            with self.subTest(case=case):
                with self.assertRaises(
                    GovernedIntegrationAdapterCandidateInvariantError
                ):
                    (
                        GovernedIntegrationAdapterCandidateProposer
                        .propose(
                            source,
                            interface_contract=(
                                "generic interface"
                            ),
                            adapter_kind=(
                                case["adapter_kind"]
                            ),
                            resource_contract=(
                                case["resource_contract"]
                            ),
                        )
                    )

    def test_06_proposal_identity_is_deterministic(self):
        source = capability()

        first = (
            GovernedIntegrationAdapterCandidateProposer
            .propose(
                source,
                interface_contract=(
                    "generic interface"
                ),
                integration_requirements=(
                    "sandbox",
                    "contract",
                ),
                adapter_kind=(
                    "GENERIC_ADAPTER"
                ),
                resource_contract=(
                    "replaceable resource"
                ),
            )
        )

        second = (
            GovernedIntegrationAdapterCandidateProposer
            .propose(
                source,
                interface_contract=(
                    "generic interface"
                ),
                integration_requirements=(
                    "contract",
                    "sandbox",
                ),
                adapter_kind=(
                    "GENERIC_ADAPTER"
                ),
                resource_contract=(
                    "replaceable resource"
                ),
            )
        )

        self.assertEqual(
            first.to_dict(),
            second.to_dict(),
        )

        self.assertEqual(
            first.integration_candidates[0].proposal_id,
            second.integration_candidates[0].proposal_id,
        )

        self.assertEqual(
            first.adapter_candidates[0].proposal_id,
            second.adapter_candidates[0].proposal_id,
        )

    def test_07_lineage_and_verification_are_preserved(self):
        source = capability()

        result = (
            GovernedIntegrationAdapterCandidateProposer
            .propose(
                source,
                interface_contract=(
                    "generic interface"
                ),
                adapter_kind=(
                    "GENERIC_ADAPTER"
                ),
                resource_contract=(
                    "generic resource"
                ),
            )
        )

        rows = (
            result.integration_candidates
            + result.adapter_candidates
        )

        for item in rows:
            with self.subTest(
                kind=type(item).__name__
            ):
                self.assertEqual(
                    item.capability_candidate_id,
                    source.candidate_id,
                )

                self.assertEqual(
                    item.landscape_change_id,
                    source.landscape_change_id,
                )

                self.assertEqual(
                    item.current_snapshot_id,
                    source.current_snapshot_id,
                )

                self.assertEqual(
                    item.scope_id,
                    source.scope_id,
                )

                self.assertEqual(
                    item.subject_id,
                    source.subject_id,
                )

                self.assertEqual(
                    item.capability_term,
                    source.capability_term,
                )

                self.assertEqual(
                    item.evidence_id,
                    source.evidence_id,
                )

                self.assertEqual(
                    item.source_ref,
                    source.source_ref,
                )

                self.assertEqual(
                    item.landscape_evidence_ids,
                    source.landscape_evidence_ids,
                )

                self.assertEqual(
                    item.verification_status,
                    "UNVERIFIED_EXTERNAL",
                )

                self.assertFalse(
                    item.system_truth_asserted
                )

    def test_08_authority_escalation_fails_closed(self):
        integration = GovernedIntegrationCandidate(
            proposal_id="GIC-test",
            capability_candidate_id="GCC-test",
            landscape_change_id="TLC-test",
            current_snapshot_id="TLS-test",
            scope_id="scope",
            subject_id="runtime.alpha",
            capability_term="vision",
            evidence_id="E1",
            source_ref="C1",
            landscape_evidence_ids=("E1",),
            interface_contract="generic interface",
        )

        adapter = GovernedAdapterCandidate(
            proposal_id="GAC-test",
            integration_proposal_id="GIC-test",
            capability_candidate_id="GCC-test",
            landscape_change_id="TLC-test",
            current_snapshot_id="TLS-test",
            scope_id="scope",
            subject_id="runtime.alpha",
            capability_term="vision",
            evidence_id="E1",
            source_ref="C1",
            landscape_evidence_ids=("E1",),
            interface_contract="generic interface",
            adapter_kind="GENERIC_ADAPTER",
            resource_contract="generic resource",
        )

        fields = (
            "registry_mutation_requested",
            "adapter_binding_created",
            "trust_asserted",
            "installation_requested",
            "activation_requested",
            "authorization_asserted",
            "execution_requested",
            "core_mutation_requested",
            "architecture_evolution_proposal_created",
            "system_truth_asserted",
        )

        for obj in (
            integration,
            adapter,
        ):
            for field_name in fields:
                with self.subTest(
                    kind=type(obj).__name__,
                    field=field_name,
                ):
                    with self.assertRaises(
                        GovernedIntegrationAdapterCandidateInvariantError
                    ):
                        replace(
                            obj,
                            **{
                                field_name: True
                            },
                        )

    def test_09_to_dict_asserts_no_registration_binding_or_activation(self):
        result = (
            GovernedIntegrationAdapterCandidateProposer
            .propose(
                capability(),
                interface_contract=(
                    "generic interface"
                ),
                adapter_kind=(
                    "GENERIC_ADAPTER"
                ),
                resource_contract=(
                    "generic resource"
                ),
            )
        )

        rows = (
            result.integration_candidates
            + result.adapter_candidates
        )

        false_fields = (
            "registry_mutation_requested",
            "adapter_binding_created",
            "trust_asserted",
            "installation_requested",
            "activation_requested",
            "authorization_asserted",
            "execution_requested",
            "core_mutation_requested",
            "architecture_evolution_proposal_created",
            "system_truth_asserted",
        )

        for item in rows:
            payload = item.to_dict()

            for field_name in false_fields:
                with self.subTest(
                    kind=type(item).__name__,
                    field=field_name,
                ):
                    self.assertIs(
                        payload[field_name],
                        False,
                    )

    def test_10_module_is_passive_and_bmf021_separate(self):
        text = SOURCE.read_text(
            encoding="utf-8"
        )

        tree = ast.parse(text)

        imports = set()
        calls = set()

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
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

            elif isinstance(node, ast.Call):
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

        forbidden_import_fragments = (
            "generic_adapters",
            "platform_boundary",
            "governed_activation",
            "provider_adapters",
        )

        bad_imports = {
            name
            for name in imports
            if any(
                fragment in name
                for fragment
                in forbidden_import_fragments
            )
        }

        forbidden_calls = {
            "register",
            "register_bindings",
            "bind",
            "install",
            "activate",
            "authorize",
            "execute",
            "dispatch",
            "promote",
            "download",
        }

        self.assertEqual(
            bad_imports,
            set(),
        )

        self.assertEqual(
            calls & forbidden_calls,
            set(),
        )

        for forbidden_symbol in (
            "DynamicAdapterRegistry",
            "AdapterBinding",
            "GovernedPlatformBoundary",
            "PlatformExecutionHandoff",
            "ArchitectureEvolutionProposal",
        ):
            self.assertNotIn(
                forbidden_symbol,
                text,
            )


if __name__ == "__main__":
    unittest.main()
