from __future__ import annotations

import ast
import unittest

from dataclasses import (
    FrozenInstanceError,
    replace,
)
from pathlib import Path

from maestro.research.governed_radar_capability_evolution import (
    CapabilityGapAbsentError,
    EvolutionProposalKind,
    GovernedRadarCapabilityEvolution,
    ObservationSourceKind,
    RadarCapabilityEvolutionInvariantError,
    ResearchEvidenceIncompleteError,
    ResearchVerificationState,
)


SOURCE = Path(
    "src/maestro/research/"
    "governed_radar_capability_evolution.py"
)

DOC = Path(
    "docs/"
    "GOVERNED_RADAR_CAPABILITY_EVOLUTION_CONSTITUTION.md"
)


def observation(
    subject="ExampleRuntime",
):
    return (
        GovernedRadarCapabilityEvolution
        .record_observation(
            subject=subject,
            source_kind=(
                ObservationSourceKind
                .HUMAN_DISCOVERY
            ),
            source_ref=(
                "https://example.invalid/runtime"
            ),
            claims=(
                "May reduce memory pressure.",
                "May support local inference.",
            ),
            capability_terms=(
                "LOCAL_INFERENCE_RUNTIME",
                "MEMORY_CONSTRAINED_INFERENCE",
            ),
        )
    )


def verified_research(
    subject="ExampleRuntime",
):
    obs = observation(subject)

    evidence = (
        GovernedRadarCapabilityEvolution
        .admit_research(
            obs,
            verification_state=(
                ResearchVerificationState
                .VERIFIED
            ),
            findings=(
                "Runtime behavior requires "
                "independent validation.",
                "Candidate exposes a local "
                "inference capability.",
            ),
            evidence_refs=(
                "evidence://source-review",
                "evidence://sandbox-plan",
            ),
        )
    )

    return obs, evidence


class GovernedRadarCapabilityEvolutionTests(
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
                f"RCE-{number:02d}",
                text,
            )

        for invariant in (
            "DISCOVER != TRUST",
            "DISCOVER != INSTALL",
            "DISCOVER != ACTIVATE",
            "DISCOVER != AUTHORIZE",
            "CAPABILITY CANDIDATE != INSTALLED CAPABILITY",
            "PROPOSAL != INSTALLATION",
            "ARCHITECTURE PROPOSAL != ONTOLOGY MUTATION",
            "NEW TECHNOLOGY != NEW CONSTITUTIONAL IDENTITY",
            "TECHNOLOGY NAME != CORE IDENTITY",
            "DISCOVER != TRUST != INSTALL != ACTIVATE != AUTHORIZE",
        ):
            self.assertIn(
                invariant,
                text,
            )

    def test_02_human_observation_is_deterministic_and_authority_neutral(self):
        first = observation()
        second = observation()

        self.assertEqual(
            first.observation_id,
            second.observation_id,
        )

        for field_name in (
            "trust_asserted",
            "installation_requested",
            "installation_authorized",
            "activation_requested",
            "activation_authorized",
            "execution_requested",
            "execution_authorized",
            "learning_authorized",
            "promotion_authorized",
            "constitutional_dependency",
        ):
            self.assertFalse(
                getattr(
                    first,
                    field_name,
                )
            )

        with self.assertRaises(
            FrozenInstanceError
        ):
            first.subject = "Changed"

    def test_03_research_binds_origin_and_cannot_silently_add_capability(self):
        obs = observation()

        evidence = (
            GovernedRadarCapabilityEvolution
            .admit_research(
                obs,
                verification_state=(
                    ResearchVerificationState
                    .VERIFIED
                ),
                findings=(
                    "Independent finding.",
                ),
                evidence_refs=(
                    "evidence://1",
                ),
            )
        )

        self.assertEqual(
            evidence.observation_id,
            obs.observation_id,
        )

        with self.assertRaises(
            RadarCapabilityEvolutionInvariantError
        ):
            GovernedRadarCapabilityEvolution.admit_research(
                obs,
                verification_state=(
                    ResearchVerificationState
                    .VERIFIED
                ),
                findings=(
                    "Bad capability injection.",
                ),
                evidence_refs=(
                    "evidence://2",
                ),
                capability_terms=(
                    "UNRELATED_NEW_CAPABILITY",
                ),
            )

    def test_04_unknown_and_rejected_research_fail_closed(self):
        obs = observation()

        for state in (
            ResearchVerificationState.UNKNOWN,
            ResearchVerificationState.REJECTED,
        ):
            with self.subTest(
                state=state.value
            ):
                evidence = (
                    GovernedRadarCapabilityEvolution
                    .admit_research(
                        obs,
                        verification_state=state,
                        findings=(
                            "Unresolved finding.",
                        ),
                        evidence_refs=(
                            "evidence://unknown",
                        ),
                    )
                )

                with self.assertRaises(
                    ResearchEvidenceIncompleteError
                ):
                    GovernedRadarCapabilityEvolution.derive_candidate(
                        evidence,
                        existing_capabilities=(),
                    )

    def test_05_candidate_contains_only_missing_capabilities(self):
        _, evidence = verified_research()

        candidate = (
            GovernedRadarCapabilityEvolution
            .derive_candidate(
                evidence,
                existing_capabilities=(
                    "LOCAL_INFERENCE_RUNTIME",
                ),
            )
        )

        self.assertEqual(
            candidate.missing_capabilities,
            (
                "MEMORY_CONSTRAINED_INFERENCE",
            ),
        )

        self.assertEqual(
            candidate.existing_capabilities,
            (
                "LOCAL_INFERENCE_RUNTIME",
            ),
        )

    def test_06_no_capability_gap_produces_no_evolution_candidate(self):
        _, evidence = verified_research()

        with self.assertRaises(
            CapabilityGapAbsentError
        ):
            GovernedRadarCapabilityEvolution.derive_candidate(
                evidence,
                existing_capabilities=(
                    "LOCAL_INFERENCE_RUNTIME",
                    "MEMORY_CONSTRAINED_INFERENCE",
                ),
            )

    def test_07_missing_capability_can_produce_adapter_integration_or_architecture_proposal(self):
        _, evidence = verified_research()

        candidate = (
            GovernedRadarCapabilityEvolution
            .derive_candidate(
                evidence,
                existing_capabilities=(),
            )
        )

        for kind in (
            EvolutionProposalKind.ADAPTER,
            EvolutionProposalKind.INTEGRATION,
            EvolutionProposalKind.ARCHITECTURE,
        ):
            with self.subTest(
                kind=kind.value
            ):
                proposal = (
                    GovernedRadarCapabilityEvolution
                    .propose_evolution(
                        candidate,
                        kind=kind,
                        requirements=(
                            "sandbox validation",
                            "supply-chain review",
                        ),
                        evidence_refs=(
                            "evidence://research",
                        ),
                    )
                )

                self.assertIs(
                    proposal.kind,
                    kind,
                )

                self.assertEqual(
                    proposal.missing_capabilities,
                    candidate.missing_capabilities,
                )

    def test_08_airllm_human_discovery_remains_data_not_core_identity(self):
        obs = (
            GovernedRadarCapabilityEvolution
            .record_observation(
                subject="AirLLM",
                source_kind=(
                    ObservationSourceKind
                    .HUMAN_DISCOVERY
                ),
                source_ref=(
                    "https://github.com/"
                    "lyogavin/airllm#macos"
                ),
                claims=(
                    "Candidate local inference runtime.",
                    "Candidate memory-constrained inference.",
                    "Candidate model-streaming runtime.",
                ),
                capability_terms=(
                    "LOCAL_INFERENCE_RUNTIME",
                    "MEMORY_CONSTRAINED_INFERENCE",
                    "MODEL_STREAMING_RUNTIME",
                ),
            )
        )

        research = (
            GovernedRadarCapabilityEvolution
            .admit_research(
                obs,
                verification_state=(
                    ResearchVerificationState
                    .VERIFIED
                ),
                findings=(
                    "Requires sandbox validation.",
                    "Requires supply-chain validation.",
                    "Requires capability benchmarking.",
                ),
                evidence_refs=(
                    "human://discovery",
                    "research://repository-review",
                ),
            )
        )

        candidate = (
            GovernedRadarCapabilityEvolution
            .derive_candidate(
                research,
                existing_capabilities=(
                    "LOCAL_INFERENCE_RUNTIME",
                ),
            )
        )

        proposal = (
            GovernedRadarCapabilityEvolution
            .propose_evolution(
                candidate,
                kind=(
                    EvolutionProposalKind
                    .INTEGRATION
                ),
                requirements=(
                    "sandbox",
                    "supply-chain",
                    "benchmark",
                    "AY validation",
                    "EX authorization",
                ),
                evidence_refs=(
                    research.research_evidence_id,
                ),
            )
        )

        self.assertEqual(
            obs.subject,
            "AirLLM",
        )

        self.assertFalse(
            obs.constitutional_dependency
        )

        self.assertFalse(
            candidate.trusted
        )

        self.assertFalse(
            proposal.installation_authorized
        )

        self.assertFalse(
            proposal.activation_authorized
        )

        self.assertFalse(
            proposal.execution_authorized
        )

    def test_09_evolution_proposal_cannot_mutate_ontology_identity_or_core(self):
        _, evidence = verified_research()

        candidate = (
            GovernedRadarCapabilityEvolution
            .derive_candidate(
                evidence,
                existing_capabilities=(),
            )
        )

        proposal = (
            GovernedRadarCapabilityEvolution
            .propose_evolution(
                candidate,
                kind=(
                    EvolutionProposalKind
                    .ARCHITECTURE
                ),
                requirements=(
                    "architecture review",
                ),
                evidence_refs=(
                    "evidence://architecture",
                ),
            )
        )

        for field_name in (
            "trust_granted",
            "installation_requested",
            "installation_authorized",
            "activation_requested",
            "activation_authorized",
            "authorization_asserted",
            "execution_requested",
            "execution_authorized",
            "ontology_mutation_requested",
            "constitutional_identity_change_requested",
            "core_mutation_requested",
        ):
            self.assertFalse(
                getattr(
                    proposal,
                    field_name,
                )
            )

            with self.assertRaises(
                RadarCapabilityEvolutionInvariantError
            ):
                replace(
                    proposal,
                    **{
                        field_name: True
                    },
                )

    def test_10_module_is_passive_and_existing_radar_remains_downstream(self):
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
            "pip",
            "maestro.runtime.kernel",
            "maestro.governed_activation",
            "maestro.state_machine",
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
            "install",
            "activate",
            "execute",
            "download",
            "request",
            "urlopen",
            "promote",
            "transition",
            "commit",
            "write_text",
            "write_bytes",
        }

        self.assertEqual(
            calls & forbidden_calls,
            set(),
        )

        for required in (
            Path(
                "src/maestro/research/"
                "radar_decision_envelope.py"
            ),
            Path(
                "src/maestro/research/"
                "governed_capability_candidate.py"
            ),
            Path(
                "src/maestro/research/"
                "capability_integration.py"
            ),
            Path(
                "src/maestro/research/"
                "governed_integration_adapter_candidate.py"
            ),
            Path(
                "src/maestro/research/"
                "governed_architecture_evolution.py"
            ),
        ):
            self.assertTrue(
                required.is_file(),
                required,
            )


if __name__ == "__main__":
    unittest.main()
