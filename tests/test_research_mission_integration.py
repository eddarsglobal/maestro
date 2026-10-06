from __future__ import annotations

import hashlib
import tempfile
import unittest

from pathlib import Path
from unittest.mock import patch

from maestro.autonomous.runtime import (
    AutonomousRuntime,
)
from maestro.models import Mission
from maestro.research.web_fetch import (
    GovernedWebFetchResult,
    GovernedWebFetchTool,
    build_governed_web_fetch_binding,
)


BODY = (
    b"RX0.4C-MISSION-INTEGRATION-"
    b"RAW-WEB-BODY"
)


def fetch_result() -> GovernedWebFetchResult:
    return GovernedWebFetchResult(
        final_url=(
            "https://example.com/final"
        ),
        method="GET",
        status=200,
        content_type="text/plain",
        body=BODY,
        body_sha256=(
            hashlib.sha256(
                BODY
            ).hexdigest()
        ),
        redirects=(),
    )


class ResearchMissionIntegrationTests(
    unittest.TestCase
):
    def test_default_runtime_keeps_durable_research_off(
        self,
    ):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)

            runtime = AutonomousRuntime(
                root
            )

            mission = (
                runtime.create_mission(
                    "default-off"
                )
            )

            self.assertIsNone(
                runtime.research
            )

            self.assertIsNone(
                runtime.research_evidence
            )

            self.assertFalse(
                (
                    root
                    / "research_evidence.sqlite3"
                ).exists()
            )

            with self.assertRaises(
                RuntimeError
            ):
                runtime.research_fetch(
                    mission,
                    "https://example.com/",
                )

    def test_mission_fetch_is_visible_and_durable(
        self,
    ):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)

            binding = (
                build_governed_web_fetch_binding()
            )

            with patch.object(
                GovernedWebFetchTool,
                "__call__",
                return_value=fetch_result(),
            ):
                runtime = AutonomousRuntime(
                    root,
                    web_research_binding=binding,
                )

                mission = (
                    runtime.create_mission(
                        "mission research"
                    )
                )

                evidence = (
                    runtime.research_fetch(
                        mission,
                        "https://example.com/",
                    )
                )

            self.assertEqual(
                runtime.kernel.evidence
                .for_task(
                    mission.task_id
                ),
                [
                    evidence
                ],
            )

            self.assertIsNotNone(
                runtime.research_evidence
            )

            durable = (
                runtime.research_evidence
                .for_task(
                    mission.task_id
                )
            )

            self.assertEqual(
                [
                    item.evidence_id
                    for item in durable
                ],
                [
                    evidence.evidence_id
                ],
            )

            verification = (
                evidence.payload[
                    "verification"
                ]
            )

            self.assertEqual(
                verification["status"],
                "UNVERIFIED_EXTERNAL",
            )

            self.assertFalse(
                verification[
                    "system_truth_asserted"
                ]
            )

            persisted = b"".join(
                item.read_bytes()
                for item in root.rglob("*")
                if item.is_file()
            )

            self.assertNotIn(
                BODY,
                persisted,
            )

    def test_restart_hydrates_durable_research_into_kernel(
        self,
    ):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)

            with patch.object(
                GovernedWebFetchTool,
                "__call__",
                return_value=fetch_result(),
            ):
                first = AutonomousRuntime(
                    root,
                    web_research_binding=(
                        build_governed_web_fetch_binding()
                    ),
                )

                mission = (
                    first.create_mission(
                        "restart research"
                    )
                )

                evidence = (
                    first.research_fetch(
                        mission,
                        "https://example.com/",
                    )
                )

            second = AutonomousRuntime(
                root,
                web_research_binding=(
                    build_governed_web_fetch_binding()
                ),
            )

            loaded = (
                second.kernel.evidence.get(
                    evidence.evidence_id
                )
            )

            self.assertEqual(
                loaded.to_dict(),
                evidence.to_dict(),
            )

            self.assertEqual(
                [
                    item.evidence_id
                    for item
                    in second.kernel.evidence
                    .for_task(
                        mission.task_id
                    )
                ],
                [
                    evidence.evidence_id
                ],
            )

    def test_foreign_mission_fails_before_fetch(
        self,
    ):
        with tempfile.TemporaryDirectory() as td:
            runtime = AutonomousRuntime(
                td,
                web_research_binding=(
                    build_governed_web_fetch_binding()
                ),
            )

            foreign = Mission(
                objective="foreign"
            )

            with patch.object(
                GovernedWebFetchTool,
                "__call__",
                return_value=fetch_result(),
            ) as call:
                with self.assertRaises(
                    ValueError
                ):
                    runtime.research_fetch(
                        foreign,
                        "https://example.com/",
                    )

                call.assert_not_called()


if __name__ == "__main__":
    unittest.main()
