from __future__ import annotations

import ast
import unittest
from pathlib import Path

from maestro.governance.bording_map_agent import (
    BordingMapAssessment,
    BordingMapAssessmentState,
    BordingMapControlAgent,
    BordingMapDefinition,
    BordingMapGate,
    BordingMapInvariantError,
    BordingMapPoint,
)


def mini_definition() -> BordingMapDefinition:
    return BordingMapDefinition(
        schema_version=1,
        name="test",
        points=(
            BordingMapPoint(
                point_id="BMF-001",
                gate=BordingMapGate.EVERGREEN,
                category="constitution",
                title="Preserve sovereignty.",
            ),
            BordingMapPoint(
                point_id="BMF-002",
                gate=BordingMapGate.PROJECT,
                category="future",
                title="Complete future capability.",
            ),
        ),
    )


def pass_row(evidence: str = "test:evidence") -> dict[str, object]:
    return {
        "state": "PASS",
        "evidence": [evidence],
    }


class BordingMapControlAgentTests(unittest.TestCase):
    def test_01_actual_map_parses_with_28_points(self):
        definition = BordingMapControlAgent.load("docs/BordingMapFile.md")
        self.assertEqual(len(definition.points), 28)
        self.assertEqual(definition.point_ids[0], "BMF-001")
        self.assertEqual(definition.point_ids[-1], "BMF-028")

    def test_02_actual_map_ids_are_unique(self):
        definition = BordingMapControlAgent.load("docs/BordingMapFile.md")
        self.assertEqual(len(definition.point_ids), len(set(definition.point_ids)))

    def test_03_missing_machine_markers_fail_closed(self):
        with self.assertRaises(BordingMapInvariantError):
            BordingMapControlAgent.parse_text("# no machine map")

    def test_04_duplicate_id_fails_closed(self):
        with self.assertRaises(BordingMapInvariantError):
            BordingMapDefinition(
                schema_version=1,
                name="duplicate",
                points=(
                    BordingMapPoint(
                        "BMF-001",
                        BordingMapGate.EVERGREEN,
                        "x",
                        "one",
                    ),
                    BordingMapPoint(
                        "BMF-001",
                        BordingMapGate.PROJECT,
                        "x",
                        "two",
                    ),
                ),
            )

    def test_05_invalid_point_id_fails_closed(self):
        with self.assertRaises(BordingMapInvariantError):
            BordingMapPoint(
                "NOT-BMF",
                BordingMapGate.PROJECT,
                "x",
                "bad",
            )

    def test_06_pass_requires_evidence(self):
        with self.assertRaises(BordingMapInvariantError):
            BordingMapAssessment(
                point_id="BMF-001",
                state=BordingMapAssessmentState.PASS,
            )

    def test_07_deferred_requires_note(self):
        with self.assertRaises(BordingMapInvariantError):
            BordingMapAssessment(
                point_id="BMF-001",
                state=BordingMapAssessmentState.DEFERRED,
            )

    def test_08_not_applicable_requires_note(self):
        with self.assertRaises(BordingMapInvariantError):
            BordingMapAssessment(
                point_id="BMF-001",
                state=BordingMapAssessmentState.NOT_APPLICABLE,
            )

    def test_09_blocked_requires_note(self):
        with self.assertRaises(BordingMapInvariantError):
            BordingMapAssessment(
                point_id="BMF-001",
                state=BordingMapAssessmentState.BLOCKED,
            )

    def test_10_unknown_assessment_id_fails_closed(self):
        with self.assertRaises(BordingMapInvariantError):
            BordingMapControlAgent.audit(
                mini_definition(),
                version="V1",
                assessments={"BMF-999": pass_row()},
            )

    def test_11_missing_assessment_blocks_release(self):
        audit = BordingMapControlAgent.audit(
            mini_definition(),
            version="V1",
            assessments={"BMF-001": pass_row()},
        )
        self.assertFalse(audit.release_ready)
        self.assertEqual(audit.missing_assessment_ids, ("BMF-002",))

    def test_12_evergreen_deferred_blocks_release(self):
        audit = BordingMapControlAgent.audit(
            mini_definition(),
            version="V1",
            assessments={
                "BMF-001": {"state": "DEFERRED", "note": "not yet"},
                "BMF-002": {"state": "DEFERRED", "note": "future"},
            },
        )
        self.assertFalse(audit.release_ready)
        self.assertEqual(audit.evergreen_violation_ids, ("BMF-001",))

    def test_13_project_deferred_allows_interim_release(self):
        audit = BordingMapControlAgent.audit(
            mini_definition(),
            version="V1",
            assessments={
                "BMF-001": pass_row(),
                "BMF-002": {"state": "DEFERRED", "note": "future milestone"},
            },
        )
        self.assertTrue(audit.release_ready)
        self.assertFalse(audit.project_complete)

    def test_14_blocked_project_blocks_release(self):
        audit = BordingMapControlAgent.audit(
            mini_definition(),
            version="V1",
            assessments={
                "BMF-001": pass_row(),
                "BMF-002": {"state": "BLOCKED", "note": "hard blocker"},
            },
        )
        self.assertFalse(audit.release_ready)
        self.assertEqual(audit.blocked_point_ids, ("BMF-002",))

    def test_15_all_pass_is_project_complete(self):
        audit = BordingMapControlAgent.audit(
            mini_definition(),
            version="V1",
            assessments={
                "BMF-001": pass_row("e1"),
                "BMF-002": pass_row("e2"),
            },
        )
        self.assertTrue(audit.release_ready)
        self.assertTrue(audit.project_complete)
        self.assertEqual(audit.progress_basis_points, 10_000)

    def test_16_progress_and_next_point_are_deterministic(self):
        audit = BordingMapControlAgent.audit(
            mini_definition(),
            version="V1",
            assessments={
                "BMF-001": pass_row(),
                "BMF-002": {"state": "DEFERRED", "note": "next"},
            },
        )
        self.assertEqual(audit.progress_basis_points, 5_000)
        self.assertEqual(audit.progress_percent, 50.0)
        self.assertEqual(audit.next_point_id, "BMF-002")

    def test_17_fingerprint_is_deterministic(self):
        first = mini_definition()
        second = mini_definition()
        self.assertEqual(first.fingerprint, second.fingerprint)
        self.assertEqual(len(first.fingerprint), 64)

    def test_18_agent_is_passive_and_asserts_no_authority(self):
        path = Path("src/maestro/governance/bording_map_agent.py")
        tree = ast.parse(path.read_text(encoding="utf-8"))

        imported = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imported.add(alias.name)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module)

        forbidden = {
            "subprocess",
            "socket",
            "requests",
            "httpx",
            "urllib.request",
            "maestro.runtime",
            "maestro.governed_activation",
            "maestro.tools",
        }
        self.assertTrue(imported.isdisjoint(forbidden))

        audit = BordingMapControlAgent.audit(
            mini_definition(),
            version="V1",
            assessments={
                "BMF-001": pass_row(),
                "BMF-002": {"state": "DEFERRED", "note": "future"},
            },
        )

        self.assertFalse(audit.authority_asserted)
        self.assertFalse(audit.ay_verdict_asserted)
        self.assertFalse(audit.ex_authorization_asserted)
        self.assertFalse(audit.promotion_authority)
        self.assertFalse(audit.activation_authority)
        self.assertFalse(audit.installation_authority)
        self.assertFalse(audit.execution_authority)
        self.assertFalse(audit.system_truth_asserted)


if __name__ == "__main__":
    unittest.main()
