from __future__ import annotations

import ast
import unittest
from dataclasses import replace
from pathlib import Path

from maestro.research.governed_architecture_evolution import (
    GovernedArchitectureEvolutionInvariantError,
    GovernedArchitectureEvolutionProposal,
    GovernedArchitectureEvolutionProposer,
    GovernedCapabilityOntologyAssessor,
    OntologySufficiencyState,
)
from maestro.research.governed_capability_candidate import (
    GovernedCapabilityCandidate,
)


DOC = Path(
    "docs/GOVERNED_ARCHITECTURE_EVOLUTION_CONSTITUTION.md"
)

SOURCE = Path(
    "src/maestro/research/"
    "governed_architecture_evolution.py"
)


def capability() -> GovernedCapabilityCandidate:
    return GovernedCapabilityCandidate(
        candidate_id="GCC-test",
        landscape_change_id="TLC-test",
        current_snapshot_id="TLS-test",
        scope_id="future-runtime",
        subject_id="runtime.future",
        capability_term="temporal-multimodal",
        evidence_id="E1",
        source_ref="CLAIM-1",
        landscape_evidence_ids=("E1", "E2"),
    )


def insufficient():
    return GovernedCapabilityOntologyAssessor.assess(
        capability(),
        ontology_id="ontology-v1",
        required_concepts=(
            "multimodal-stream",
            "temporal-alignment",
        ),
        represented_concepts=(
            "multimodal-stream",
        ),
        ontology_complete=True,
    )


class GovernedArchitectureEvolutionTests(
    unittest.TestCase
):
    def test_01_constitution_contains_ten_laws(self):
        text = DOC.read_text(encoding="utf-8")

        for number in range(1, 11):
            self.assertIn(
                f"AOE-{number:02d}",
                text,
            )

        self.assertIn(
            "CAPABILITY GAP != ONTOLOGY GAP",
            text,
        )

        self.assertIn(
            "MISSING ADAPTER != ONTOLOGY GAP",
            text,
        )

        self.assertIn(
            "ARCHITECTURE PROPOSAL != SUPPLY-CHAIN ARTIFACT",
            text,
        )

    def test_02_sufficient_ontology_produces_zero(self):
        assessment = GovernedCapabilityOntologyAssessor.assess(
            capability(),
            ontology_id="ontology-v1",
            required_concepts=(
                "vision",
                "stream",
            ),
            represented_concepts=(
                "vision",
                "stream",
                "audio",
            ),
            ontology_complete=True,
        )

        self.assertIs(
            assessment.state,
            OntologySufficiencyState.SUFFICIENT,
        )

        self.assertEqual(
            assessment.missing_concepts,
            (),
        )

        result = GovernedArchitectureEvolutionProposer.propose(
            assessment,
            rationale="No extension required.",
        )

        self.assertEqual(result.size, 0)

    def test_03_unknown_is_not_insufficient(self):
        assessment = GovernedCapabilityOntologyAssessor.assess(
            capability(),
            ontology_id="ontology-v1",
            required_concepts=("future-concept",),
            represented_concepts=(),
            ontology_complete=False,
        )

        self.assertIs(
            assessment.state,
            OntologySufficiencyState.UNKNOWN,
        )

        self.assertEqual(
            assessment.missing_concepts,
            (),
        )

        result = GovernedArchitectureEvolutionProposer.propose(
            assessment,
            rationale="Ontology knowledge incomplete.",
        )

        self.assertEqual(result.size, 0)

    def test_04_insufficient_ontology_produces_proposal(self):
        assessment = insufficient()

        self.assertIs(
            assessment.state,
            OntologySufficiencyState.INSUFFICIENT,
        )

        self.assertEqual(
            assessment.missing_concepts,
            ("temporal-alignment",),
        )

        result = GovernedArchitectureEvolutionProposer.propose(
            assessment,
            proposed_concepts=(
                "temporal-alignment",
            ),
            rationale=(
                "Current ontology cannot represent "
                "temporal alignment."
            ),
        )

        self.assertEqual(result.size, 1)

        proposal = result.proposals[0]

        self.assertEqual(
            proposal.assessment_id,
            assessment.assessment_id,
        )

        self.assertEqual(
            proposal.missing_concepts,
            ("temporal-alignment",),
        )

        self.assertEqual(
            proposal.proposed_concepts,
            ("temporal-alignment",),
        )

    def test_05_assessment_and_proposal_are_deterministic(self):
        source = capability()

        a = GovernedCapabilityOntologyAssessor.assess(
            source,
            ontology_id="ontology-v1",
            required_concepts=(
                "temporal-alignment",
                "multimodal-stream",
            ),
            represented_concepts=(
                "multimodal-stream",
            ),
            ontology_complete=True,
        )

        b = GovernedCapabilityOntologyAssessor.assess(
            source,
            ontology_id="ontology-v1",
            required_concepts=(
                "multimodal-stream",
                "temporal-alignment",
            ),
            represented_concepts=(
                "multimodal-stream",
            ),
            ontology_complete=True,
        )

        self.assertEqual(
            a.to_dict(),
            b.to_dict(),
        )

        self.assertEqual(
            a.assessment_id,
            b.assessment_id,
        )

        pa = GovernedArchitectureEvolutionProposer.propose(
            a,
            proposed_concepts=(
                "temporal-alignment",
            ),
            rationale="Extend ontology.",
        )

        pb = GovernedArchitectureEvolutionProposer.propose(
            b,
            proposed_concepts=(
                "temporal-alignment",
            ),
            rationale="Extend ontology.",
        )

        self.assertEqual(
            pa.to_dict(),
            pb.to_dict(),
        )

        self.assertEqual(
            pa.proposals[0].proposal_id,
            pb.proposals[0].proposal_id,
        )

    def test_06_incomplete_proposal_fails_closed(self):
        assessment = insufficient()

        cases = (
            (),
            ("unrelated-concept",),
        )

        for proposed in cases:
            with self.subTest(proposed=proposed):
                with self.assertRaises(
                    GovernedArchitectureEvolutionInvariantError
                ):
                    GovernedArchitectureEvolutionProposer.propose(
                        assessment,
                        proposed_concepts=proposed,
                        rationale="Evolution proposal.",
                    )

    def test_07_evidence_and_reason_lineage_preserved(self):
        source = capability()

        assessment = GovernedCapabilityOntologyAssessor.assess(
            source,
            ontology_id="ontology-v1",
            required_concepts=(
                "temporal-alignment",
            ),
            represented_concepts=(),
            ontology_complete=True,
        )

        self.assertEqual(
            assessment.capability_candidate_id,
            source.candidate_id,
        )

        self.assertEqual(
            assessment.landscape_change_id,
            source.landscape_change_id,
        )

        self.assertEqual(
            assessment.current_snapshot_id,
            source.current_snapshot_id,
        )

        self.assertEqual(
            assessment.evidence_id,
            source.evidence_id,
        )

        self.assertEqual(
            assessment.source_ref,
            source.source_ref,
        )

        self.assertEqual(
            assessment.landscape_evidence_ids,
            source.landscape_evidence_ids,
        )

        self.assertEqual(
            assessment.verification_status,
            "UNVERIFIED_EXTERNAL",
        )

        result = GovernedArchitectureEvolutionProposer.propose(
            assessment,
            proposed_concepts=(
                "temporal-alignment",
            ),
            rationale=(
                "Ontology cannot represent "
                "temporal alignment."
            ),
        )

        proposal = result.proposals[0]

        self.assertEqual(
            proposal.assessment_id,
            assessment.assessment_id,
        )

        self.assertEqual(
            proposal.evidence_id,
            assessment.evidence_id,
        )

        self.assertEqual(
            proposal.landscape_evidence_ids,
            assessment.landscape_evidence_ids,
        )

        self.assertEqual(
            proposal.verification_status,
            "UNVERIFIED_EXTERNAL",
        )

        self.assertFalse(
            proposal.system_truth_asserted
        )

    def test_08_authority_escalation_fails_closed(self):
        assessment = insufficient()

        assessment_flags = (
            "architecture_evolution_proposal_created",
            "proposal_approved",
            "schema_mutation_requested",
            "migration_requested",
            "registry_mutation_requested",
            "installation_requested",
            "activation_requested",
            "authorization_asserted",
            "execution_requested",
            "core_mutation_requested",
            "supply_chain_artifact_created",
            "system_truth_asserted",
        )

        for field_name in assessment_flags:
            with self.subTest(
                object="assessment",
                field=field_name,
            ):
                with self.assertRaises(
                    GovernedArchitectureEvolutionInvariantError
                ):
                    replace(
                        assessment,
                        **{field_name: True},
                    )

        proposal = GovernedArchitectureEvolutionProposal(
            proposal_id="AEP-test",
            assessment_id=assessment.assessment_id,
            capability_candidate_id=(
                assessment.capability_candidate_id
            ),
            landscape_change_id=(
                assessment.landscape_change_id
            ),
            current_snapshot_id=(
                assessment.current_snapshot_id
            ),
            scope_id=assessment.scope_id,
            subject_id=assessment.subject_id,
            capability_term=(
                assessment.capability_term
            ),
            evidence_id=assessment.evidence_id,
            source_ref=assessment.source_ref,
            landscape_evidence_ids=(
                assessment.landscape_evidence_ids
            ),
            ontology_id=assessment.ontology_id,
            missing_concepts=(
                "temporal-alignment",
            ),
            proposed_concepts=(
                "temporal-alignment",
            ),
            rationale="Extend ontology.",
        )

        proposal_flags = (
            "proposal_approved",
            "schema_mutation_requested",
            "migration_requested",
            "registry_mutation_requested",
            "installation_requested",
            "activation_requested",
            "authorization_asserted",
            "execution_requested",
            "core_mutation_requested",
            "supply_chain_artifact_created",
            "system_truth_asserted",
        )

        for field_name in proposal_flags:
            with self.subTest(
                object="proposal",
                field=field_name,
            ):
                with self.assertRaises(
                    GovernedArchitectureEvolutionInvariantError
                ):
                    replace(
                        proposal,
                        **{field_name: True},
                    )

    def test_09_missing_adapter_is_not_ontology_gap(self):
        text = SOURCE.read_text(
            encoding="utf-8"
        )

        self.assertNotIn(
            "CapabilityGapDetector",
            text,
        )

        self.assertNotIn(
            "DynamicAdapterRegistry",
            text,
        )

        self.assertNotIn(
            "AdapterBinding",
            text,
        )

        self.assertNotIn(
            "ProviderRegistry",
            text,
        )

        assessment = GovernedCapabilityOntologyAssessor.assess(
            capability(),
            ontology_id="ontology-v1",
            required_concepts=("vision",),
            represented_concepts=("vision",),
            ontology_complete=True,
        )

        self.assertIs(
            assessment.state,
            OntologySufficiencyState.SUFFICIENT,
        )

    def test_10_module_is_passive_and_bmf022_separate(self):
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

            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.add(node.module)

            elif isinstance(node, ast.Call):
                if isinstance(
                    node.func,
                    ast.Name,
                ):
                    calls.add(node.func.id)

                elif isinstance(
                    node.func,
                    ast.Attribute,
                ):
                    calls.add(node.func.attr)

        forbidden_import_fragments = (
            "dynamic_registry",
            "generic_adapters",
            "platform_boundary",
            "governed_activation",
            "strategic_adaptation",
            "outcome_governed_adaptation",
        )

        bad_imports = {
            name
            for name in imports
            if any(
                fragment in name
                for fragment in forbidden_import_fragments
            )
        }

        forbidden_calls = {
            "register",
            "install",
            "activate",
            "authorize",
            "execute",
            "dispatch",
            "migrate",
            "apply",
            "promote",
            "download",
            "verify",
            "sign",
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
            "CouncilCapsuleManifest",
            "DynamicAdapterRegistry",
            "AdapterBinding",
            "PlatformExecutionHandoff",
            "SupplyChainArtifact",
            "ArtifactSignature",
        ):
            self.assertNotIn(
                forbidden_symbol,
                text,
            )


if __name__ == "__main__":
    unittest.main()
