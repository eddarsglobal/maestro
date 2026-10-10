from __future__ import annotations

import ast
import unittest
from dataclasses import replace
from pathlib import Path

from maestro.research.capability_integration import (
    CapabilityIntegrationEvaluation,
)
from maestro.research.governed_capability_candidate import (
    CapabilityCandidateSet,
    GovernedCapabilityCandidate,
    GovernedCapabilityCandidateDeriver,
    GovernedCapabilityCandidateInvariantError,
)
from maestro.research.technology_landscape_change import (
    LandscapeChangeState,
    TechnologyLandscapeChangeDetector,
    TechnologyLandscapeObservation,
    TechnologyLandscapeSnapshot,
)


DOC = Path(
    "docs/GOVERNED_CAPABILITY_CANDIDATE_CONSTITUTION.md"
)

SOURCE = Path(
    "src/maestro/research/"
    "governed_capability_candidate.py"
)


def observation(
    subject_id: str,
    evidence_id: str,
    *,
    version: str,
    claim: str | None = None,
) -> TechnologyLandscapeObservation:
    return TechnologyLandscapeObservation(
        subject_id=subject_id,
        evidence_id=evidence_id,
        source_ref=f"CLAIM-{evidence_id}",
        claim=claim or f"{subject_id} observed.",
        state={
            "version": version,
        },
    )


def evaluation(
    evidence_id: str,
    capability: str = "vision",
) -> CapabilityIntegrationEvaluation:
    return CapabilityIntegrationEvaluation(
        evidence_id=evidence_id,
        expected_capability_gain=1.0,
        integration_cost=0.25,
        target_capability_terms=(
            capability,
        ),
        novel_capability_terms=(
            capability,
        ),
        matched_novel_capability_terms=(
            capability,
        ),
        integration_requirements=(),
        unsupported_integration_requirements=(),
    )


class GovernedCapabilityCandidateTests(
    unittest.TestCase
):
    def test_01_constitution_contains_ten_laws(self):
        text = DOC.read_text(
            encoding="utf-8"
        )

        for number in range(1, 11):
            self.assertIn(
                f"GCD-{number:02d}",
                text,
            )

        self.assertIn(
            "CAPABILITY CANDIDATE != INTEGRATION CANDIDATE",
            text,
        )

        self.assertIn(
            "CAPABILITY DERIVATION != INTEGRATION PROPOSAL",
            text,
        )

    def test_02_modified_subject_derives_candidate(self):
        previous = TechnologyLandscapeSnapshot(
            scope_id="scope",
            observations=(
                observation(
                    "runtime.alpha",
                    "E0",
                    version="1",
                ),
            ),
            complete=True,
        )

        current = TechnologyLandscapeSnapshot(
            scope_id="scope",
            observations=(
                observation(
                    "runtime.alpha",
                    "E1",
                    version="2",
                    claim=(
                        "Runtime supports vision."
                    ),
                ),
            ),
            complete=True,
        )

        change = (
            TechnologyLandscapeChangeDetector
            .compare(
                previous,
                current,
            )
        )

        result = (
            GovernedCapabilityCandidateDeriver
            .derive(
                change,
                current_snapshot=current,
                evaluations=(
                    evaluation("E1"),
                ),
            )
        )

        self.assertEqual(
            result.size,
            1,
        )

        candidate = result.candidates[0]

        self.assertEqual(
            candidate.subject_id,
            "runtime.alpha",
        )

        self.assertEqual(
            candidate.capability_term,
            "vision",
        )

        self.assertEqual(
            candidate.evidence_id,
            "E1",
        )

        self.assertEqual(
            candidate.landscape_change_id,
            change.change_id,
        )

        self.assertEqual(
            candidate.current_snapshot_id,
            current.snapshot_id,
        )

    def test_03_added_subject_derives_candidate(self):
        previous = TechnologyLandscapeSnapshot(
            scope_id="scope",
            observations=(),
            complete=True,
        )

        current = TechnologyLandscapeSnapshot(
            scope_id="scope",
            observations=(
                observation(
                    "runtime.new",
                    "E1",
                    version="1",
                ),
            ),
            complete=True,
        )

        change = (
            TechnologyLandscapeChangeDetector
            .compare(
                previous,
                current,
            )
        )

        self.assertEqual(
            change.added_subject_ids,
            ("runtime.new",),
        )

        result = (
            GovernedCapabilityCandidateDeriver
            .derive(
                change,
                current_snapshot=current,
                evaluations=(
                    evaluation("E1"),
                ),
            )
        )

        self.assertEqual(
            result.size,
            1,
        )

    def test_04_unknown_unchanged_and_removed_produce_zero(self):
        row = observation(
            "runtime.alpha",
            "E1",
            version="1",
        )

        snapshot = TechnologyLandscapeSnapshot(
            scope_id="scope",
            observations=(row,),
            complete=True,
        )

        unknown = (
            TechnologyLandscapeChangeDetector
            .compare(
                None,
                snapshot,
            )
        )

        unchanged = (
            TechnologyLandscapeChangeDetector
            .compare(
                snapshot,
                snapshot,
            )
        )

        removed_current = (
            TechnologyLandscapeSnapshot(
                scope_id="scope",
                observations=(),
                complete=True,
            )
        )

        removed = (
            TechnologyLandscapeChangeDetector
            .compare(
                snapshot,
                removed_current,
            )
        )

        self.assertIs(
            unknown.state,
            LandscapeChangeState.UNKNOWN,
        )

        self.assertIs(
            unchanged.state,
            LandscapeChangeState.UNCHANGED,
        )

        self.assertEqual(
            GovernedCapabilityCandidateDeriver
            .derive(
                unknown,
                current_snapshot=snapshot,
            ).size,
            0,
        )

        self.assertEqual(
            GovernedCapabilityCandidateDeriver
            .derive(
                unchanged,
                current_snapshot=snapshot,
            ).size,
            0,
        )

        self.assertEqual(
            GovernedCapabilityCandidateDeriver
            .derive(
                removed,
                current_snapshot=removed_current,
            ).size,
            0,
        )

    def test_05_foreign_evidence_lineage_fails_closed(self):
        previous = TechnologyLandscapeSnapshot(
            scope_id="scope",
            observations=(
                observation(
                    "runtime.alpha",
                    "E0",
                    version="1",
                ),
            ),
            complete=True,
        )

        current = TechnologyLandscapeSnapshot(
            scope_id="scope",
            observations=(
                observation(
                    "runtime.alpha",
                    "E1",
                    version="2",
                ),
            ),
            complete=True,
        )

        change = (
            TechnologyLandscapeChangeDetector
            .compare(
                previous,
                current,
            )
        )

        with self.assertRaises(
            GovernedCapabilityCandidateInvariantError
        ):
            GovernedCapabilityCandidateDeriver.derive(
                change,
                current_snapshot=current,
                evaluations=(
                    evaluation(
                        "FOREIGN-EVIDENCE"
                    ),
                ),
            )

    def test_06_snapshot_identity_mismatch_fails_closed(self):
        previous = TechnologyLandscapeSnapshot(
            scope_id="scope",
            observations=(
                observation(
                    "runtime.alpha",
                    "E0",
                    version="1",
                ),
            ),
            complete=True,
        )

        current = TechnologyLandscapeSnapshot(
            scope_id="scope",
            observations=(
                observation(
                    "runtime.alpha",
                    "E1",
                    version="2",
                ),
            ),
            complete=True,
        )

        different_current = TechnologyLandscapeSnapshot(
            scope_id="scope",
            observations=(
                observation(
                    "runtime.alpha",
                    "E2",
                    version="3",
                ),
            ),
            complete=True,
        )

        change = (
            TechnologyLandscapeChangeDetector
            .compare(
                previous,
                current,
            )
        )

        with self.assertRaises(
            GovernedCapabilityCandidateInvariantError
        ):
            GovernedCapabilityCandidateDeriver.derive(
                change,
                current_snapshot=different_current,
                evaluations=(),
            )

    def test_07_candidate_identity_is_deterministic(self):
        previous = TechnologyLandscapeSnapshot(
            scope_id="scope",
            observations=(
                observation(
                    "runtime.alpha",
                    "E0",
                    version="1",
                ),
            ),
            complete=True,
        )

        current = TechnologyLandscapeSnapshot(
            scope_id="scope",
            observations=(
                observation(
                    "runtime.alpha",
                    "E1",
                    version="2",
                ),
            ),
            complete=True,
        )

        change = (
            TechnologyLandscapeChangeDetector
            .compare(
                previous,
                current,
            )
        )

        item = evaluation("E1")

        first = (
            GovernedCapabilityCandidateDeriver
            .derive(
                change,
                current_snapshot=current,
                evaluations=(item,),
            )
        )

        second = (
            GovernedCapabilityCandidateDeriver
            .derive(
                change,
                current_snapshot=current,
                evaluations=(item,),
            )
        )

        self.assertEqual(
            first.to_dict(),
            second.to_dict(),
        )

        self.assertEqual(
            first.candidates[0].candidate_id,
            second.candidates[0].candidate_id,
        )

    def test_08_authority_escalation_fails_closed(self):
        candidate = GovernedCapabilityCandidate(
            candidate_id="GCC-test",
            landscape_change_id="TLC-test",
            current_snapshot_id="TLS-test",
            scope_id="scope",
            subject_id="runtime.alpha",
            capability_term="vision",
            evidence_id="E1",
            source_ref="C1",
            landscape_evidence_ids=("E1",),
        )

        fields = (
            "trust_asserted",
            "integration_candidate_created",
            "adapter_candidate_created",
            "installation_requested",
            "activation_requested",
            "authorization_asserted",
            "execution_requested",
            "core_mutation_requested",
            "system_truth_asserted",
        )

        for field_name in fields:
            with self.subTest(
                field=field_name
            ):
                with self.assertRaises(
                    GovernedCapabilityCandidateInvariantError
                ):
                    replace(
                        candidate,
                        **{
                            field_name: True
                        },
                    )

    def test_09_candidate_set_is_deterministically_ordered(self):
        a = GovernedCapabilityCandidate(
            candidate_id="GCC-a",
            landscape_change_id="TLC-1",
            current_snapshot_id="TLS-1",
            scope_id="scope",
            subject_id="runtime.b",
            capability_term="vision",
            evidence_id="E2",
            source_ref="C2",
            landscape_evidence_ids=(
                "E1",
                "E2",
            ),
        )

        b = GovernedCapabilityCandidate(
            candidate_id="GCC-b",
            landscape_change_id="TLC-1",
            current_snapshot_id="TLS-1",
            scope_id="scope",
            subject_id="runtime.a",
            capability_term="audio",
            evidence_id="E1",
            source_ref="C1",
            landscape_evidence_ids=(
                "E2",
                "E1",
            ),
        )

        first = CapabilityCandidateSet(
            candidates=(a, b)
        )

        second = CapabilityCandidateSet(
            candidates=(b, a)
        )

        self.assertEqual(
            first.to_dict(),
            second.to_dict(),
        )

        self.assertEqual(
            tuple(
                item.subject_id
                for item in first.candidates
            ),
            (
                "runtime.a",
                "runtime.b",
            ),
        )

    def test_10_module_is_passive_and_bmf020_separate(self):
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

        forbidden_roots = (
            "subprocess",
            "socket",
            "requests",
            "httpx",
            "aiohttp",
            "urllib",
        )

        forbidden_calls = {
            "install",
            "activate",
            "promote",
            "execute",
            "dispatch",
            "download",
            "connect",
            "urlopen",
            "Popen",
        }

        bad_imports = {
            name
            for name in imports
            if any(
                name == root
                or name.startswith(
                    root + "."
                )
                for root in forbidden_roots
            )
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
            "PlatformExecutionHandoff",
            "register_bindings",
        ):
            self.assertNotIn(
                forbidden_symbol,
                text,
            )


if __name__ == "__main__":
    unittest.main()
