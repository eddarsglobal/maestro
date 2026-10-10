from __future__ import annotations

import ast
import math
import unittest
from dataclasses import replace
from pathlib import Path

from maestro.research.technology_landscape_change import (
    LandscapeChangeState,
    TechnologyLandscapeChange,
    TechnologyLandscapeChangeDetector,
    TechnologyLandscapeChangeInvariantError,
    TechnologyLandscapeObservation,
    TechnologyLandscapeSnapshot,
)
from maestro.research.technology_radar import (
    RadarFactors,
    RadarObservation,
)


DOC = Path(
    "docs/TECHNOLOGY_LANDSCAPE_CHANGE_CONSTITUTION.md"
)

SOURCE = Path(
    "src/maestro/research/"
    "technology_landscape_change.py"
)


def observation(
    subject_id: str,
    evidence_id: str,
    state: dict,
) -> TechnologyLandscapeObservation:
    return TechnologyLandscapeObservation(
        subject_id=subject_id,
        evidence_id=evidence_id,
        source_ref=f"CLAIM-{evidence_id}",
        claim=f"{subject_id} observed.",
        state=state,
    )


class TechnologyLandscapeChangeTests(
    unittest.TestCase
):
    def test_01_constitution_contains_ten_laws(self):
        text = DOC.read_text(
            encoding="utf-8"
        )

        for number in range(1, 11):
            self.assertIn(
                f"TLC-{number:02d}",
                text,
            )

        self.assertIn(
            "UNKNOWN SHALL NEVER be treated as UNCHANGED",
            text,
        )

    def test_02_evidence_churn_does_not_change_snapshot(self):
        first = TechnologyLandscapeSnapshot(
            scope_id="scope",
            observations=(
                observation(
                    "runtime.a",
                    "E1",
                    {
                        "version": "1",
                        "capabilities": [
                            "compute",
                            "generate",
                        ],
                    },
                ),
            ),
            complete=True,
        )

        second = TechnologyLandscapeSnapshot(
            scope_id="scope",
            observations=(
                observation(
                    "runtime.a",
                    "E2",
                    {
                        "capabilities": [
                            "compute",
                            "generate",
                        ],
                        "version": "1",
                    },
                ),
            ),
            complete=True,
        )

        self.assertEqual(
            first.snapshot_id,
            second.snapshot_id,
        )

        result = (
            TechnologyLandscapeChangeDetector
            .compare(
                first,
                second,
            )
        )

        self.assertIs(
            result.state,
            LandscapeChangeState.UNCHANGED,
        )

    def test_03_add_remove_modify_are_explicit(self):
        previous = TechnologyLandscapeSnapshot(
            scope_id="scope",
            observations=(
                observation(
                    "removed",
                    "E1",
                    {"version": "1"},
                ),
                observation(
                    "modified",
                    "E2",
                    {"version": "1"},
                ),
            ),
            complete=True,
        )

        current = TechnologyLandscapeSnapshot(
            scope_id="scope",
            observations=(
                observation(
                    "modified",
                    "E3",
                    {"version": "2"},
                ),
                observation(
                    "added",
                    "E4",
                    {"version": "1"},
                ),
            ),
            complete=True,
        )

        result = (
            TechnologyLandscapeChangeDetector
            .compare(
                previous,
                current,
            )
        )

        self.assertIs(
            result.state,
            LandscapeChangeState.CHANGED,
        )

        self.assertEqual(
            result.added_subject_ids,
            ("added",),
        )

        self.assertEqual(
            result.removed_subject_ids,
            ("removed",),
        )

        self.assertEqual(
            result.modified_subject_ids,
            ("modified",),
        )

    def test_04_unknown_is_not_unchanged(self):
        row = observation(
            "runtime",
            "E1",
            {"version": "1"},
        )

        complete = TechnologyLandscapeSnapshot(
            scope_id="scope",
            observations=(row,),
            complete=True,
        )

        incomplete = TechnologyLandscapeSnapshot(
            scope_id="scope",
            observations=(row,),
            complete=False,
        )

        no_baseline = (
            TechnologyLandscapeChangeDetector
            .compare(
                None,
                complete,
            )
        )

        incomplete_current = (
            TechnologyLandscapeChangeDetector
            .compare(
                complete,
                incomplete,
            )
        )

        self.assertIs(
            no_baseline.state,
            LandscapeChangeState.UNKNOWN,
        )

        self.assertIs(
            incomplete_current.state,
            LandscapeChangeState.UNKNOWN,
        )

        self.assertIsNot(
            no_baseline.state,
            LandscapeChangeState.UNCHANGED,
        )

    def test_05_scope_mismatch_fails_closed(self):
        row = observation(
            "runtime",
            "E1",
            {"version": "1"},
        )

        previous = TechnologyLandscapeSnapshot(
            scope_id="scope-a",
            observations=(row,),
            complete=True,
        )

        current = TechnologyLandscapeSnapshot(
            scope_id="scope-b",
            observations=(row,),
            complete=True,
        )

        with self.assertRaises(
            TechnologyLandscapeChangeInvariantError
        ):
            TechnologyLandscapeChangeDetector.compare(
                previous,
                current,
            )

    def test_06_authority_escalation_fails_closed(self):
        change = TechnologyLandscapeChange(
            state=LandscapeChangeState.CHANGED,
            scope_id="scope",
            previous_snapshot_id="OLD",
            current_snapshot_id="NEW",
            modified_subject_ids=("runtime",),
            evidence_ids=("E1",),
            reason="LANDSCAPE_CHANGED",
        )

        for field_name in (
            "update_recommended",
            "capability_candidate_created",
            "trust_asserted",
            "installation_requested",
            "activation_requested",
            "authorization_asserted",
            "execution_requested",
            "core_mutation_requested",
            "system_truth_asserted",
        ):
            with self.subTest(
                field=field_name
            ):
                with self.assertRaises(
                    TechnologyLandscapeChangeInvariantError
                ):
                    replace(
                        change,
                        **{field_name: True},
                    )

    def test_07_radar_evidence_remains_unverified(self):
        factors = RadarFactors(
            novelty=0.5,
            source_quality=0.5,
            relevance_to_maestro=0.5,
            expected_capability_gain=0.5,
            reproducibility=0.5,
            integration_cost=0.5,
            security_risk=0.5,
        )

        radar = RadarObservation(
            task_id="TASK-A",
            evidence_id="E-A",
            source_ref="CLAIM-A",
            claim="External runtime observed.",
            verification_status=(
                "UNVERIFIED_EXTERNAL"
            ),
            system_truth_asserted=False,
            factors=factors,
            priority_score=(
                factors.priority_score
            ),
        )

        row = (
            TechnologyLandscapeObservation
            .from_radar(
                subject_id="runtime.a",
                observation=radar,
                state={"version": "future"},
            )
        )

        self.assertEqual(
            row.verification_status,
            "UNVERIFIED_EXTERNAL",
        )

        self.assertFalse(
            row.system_truth_asserted
        )

    def test_08_state_must_be_canonical_json_safe(self):
        with self.assertRaises(ValueError):
            observation(
                "runtime",
                "E1",
                {"score": math.inf},
            )

        with self.assertRaises(TypeError):
            observation(
                "runtime",
                "E2",
                {"unsupported": object()},
            )

    def test_09_bmf018_does_not_implement_bmf019(self):
        text = SOURCE.read_text(
            encoding="utf-8"
        )

        forbidden = (
            "GovernedUnknownTechnologyResearchIngress",
            "UnknownTechnologyResearchCandidate",
            "CapabilityIntegrationEvaluator",
            "RadarFollowUpCandidate",
            "ResearchRequest",
        )

        for symbol in forbidden:
            with self.subTest(
                symbol=symbol
            ):
                self.assertNotIn(
                    symbol,
                    text,
                )

    def test_10_module_is_passive(self):
        tree = ast.parse(
            SOURCE.read_text(
                encoding="utf-8"
            )
        )

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

        self.assertEqual(
            bad_imports,
            set(),
        )

        self.assertEqual(
            calls & forbidden_calls,
            set(),
        )


if __name__ == "__main__":
    unittest.main()
