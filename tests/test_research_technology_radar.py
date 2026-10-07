from __future__ import annotations

import ast
import unittest

from datetime import (
    datetime,
    timezone,
)
from pathlib import Path

from maestro.enums import (
    CouncilId,
    EvidenceKind,
)
from maestro.research import (
    ContentDigest,
    ExternalArtifact,
    RadarFactors,
    ResearchClaim,
    ResearchEvidenceBridge,
    ResearchSource,
    SourceProvenance,
    TechnologyRadar,
    TechnologyRadarInvariantError,
)


class TechnologyRadarTests(
    unittest.TestCase
):
    def evidence(self):
        now = (
            datetime.now(
                timezone.utc
            ).isoformat()
        )

        source = ResearchSource(
            "https://example.com/"
            "technology-radar-source",
            label="External technology source",
        )

        provenance = SourceProvenance(
            source_id=source.source_id,
            retrieved_at=now,
            digest=ContentDigest.from_bytes(
                b"ADEL0.2B"
            ),
        )

        artifact = ExternalArtifact(
            source=source,
            provenance=provenance,
            artifact_kind="DOCUMENT",
            media_type="text/html",
        )

        claim = ResearchClaim(
            statement=(
                "External technology "
                "observation"
            ),
            artifact_ids=(
                artifact.artifact_id,
            ),
            created_at=now,
        )

        return (
            ResearchEvidenceBridge
            .to_evidence(
                task_id=(
                    "TASK-A1B2C3D4E5F6"
                ),
                claim=claim,
                artifacts=[artifact],
            )
        )

    def factors(
        self,
        **overrides,
    ):
        values = {
            "novelty": 0.90,
            "source_quality": 0.80,
            "relevance_to_maestro": 0.95,
            "expected_capability_gain": 0.85,
            "reproducibility": 0.75,
            "integration_cost": 0.20,
            "security_risk": 0.10,
        }

        values.update(
            overrides
        )

        return RadarFactors(
            **values
        )

    def test_assessment_preserves_unverified_boundary(
        self,
    ):
        evidence = self.evidence()

        observation = (
            TechnologyRadar().assess(
                evidence,
                self.factors(),
            )
        )

        self.assertEqual(
            observation.task_id,
            evidence.task_id,
        )

        self.assertEqual(
            observation.evidence_id,
            evidence.evidence_id,
        )

        self.assertEqual(
            observation.source_ref,
            evidence.source_ref,
        )

        self.assertEqual(
            observation.verification_status,
            "UNVERIFIED_EXTERNAL",
        )

        self.assertFalse(
            observation.system_truth_asserted
        )

    def test_priority_score_matches_normalized_formula(
        self,
    ):
        factors = RadarFactors(
            novelty=1.0,
            source_quality=0.8,
            relevance_to_maestro=0.9,
            expected_capability_gain=0.7,
            reproducibility=0.6,
            integration_cost=0.2,
            security_risk=0.3,
        )

        expected = (
            1.0
            * 0.8
            * 0.9
            * 0.7
            * 0.6
            / (
                (1.0 + 0.2)
                * (1.0 + 0.3)
            )
        )

        self.assertAlmostEqual(
            factors.priority_score,
            expected,
        )

    def test_cost_and_security_risk_reduce_priority(
        self,
    ):
        radar = TechnologyRadar()

        first = radar.assess(
            self.evidence(),
            self.factors(
                integration_cost=0.0,
                security_risk=0.0,
            ),
        )

        second_evidence = self.evidence()

        second = radar.assess(
            second_evidence,
            self.factors(
                integration_cost=1.0,
                security_risk=1.0,
            ),
        )

        self.assertGreater(
            first.priority_score,
            second.priority_score,
        )

    def test_invalid_factor_domain_fails_closed(
        self,
    ):
        with self.assertRaises(
            ValueError
        ):
            self.factors(
                novelty=1.01
            )

        with self.assertRaises(
            ValueError
        ):
            self.factors(
                security_risk=-0.01
            )

        with self.assertRaises(
            TypeError
        ):
            self.factors(
                integration_cost=True
            )

    def test_authority_or_truth_escalation_is_rejected(
        self,
    ):
        radar = TechnologyRadar()

        evidence = self.evidence()
        evidence.council = CouncilId.IT

        with self.assertRaises(
            TechnologyRadarInvariantError
        ):
            radar.assess(
                evidence,
                self.factors(),
            )

        evidence = self.evidence()
        evidence.kind = EvidenceKind.OTHER

        with self.assertRaises(
            TechnologyRadarInvariantError
        ):
            radar.assess(
                evidence,
                self.factors(),
            )

        evidence = self.evidence()
        evidence.payload[
            "verification"
        ]["status"] = "VERIFIED"

        with self.assertRaises(
            TechnologyRadarInvariantError
        ):
            radar.assess(
                evidence,
                self.factors(),
            )

        evidence = self.evidence()
        evidence.payload[
            "verification"
        ]["system_truth_asserted"] = True

        with self.assertRaises(
            TechnologyRadarInvariantError
        ):
            radar.assess(
                evidence,
                self.factors(),
            )

        evidence = self.evidence()
        evidence.payload[
            "verification"
        ]["required_authority"] = "EX"

        with self.assertRaises(
            TechnologyRadarInvariantError
        ):
            radar.assess(
                evidence,
                self.factors(),
            )

    def test_ranking_is_deterministic_and_unique(
        self,
    ):
        radar = TechnologyRadar()

        low = radar.assess(
            self.evidence(),
            self.factors(
                novelty=0.20
            ),
        )

        high = radar.assess(
            self.evidence(),
            self.factors(
                novelty=0.95
            ),
        )

        ranked = radar.rank(
            [low, high]
        )

        self.assertEqual(
            ranked,
            [high, low],
        )

        with self.assertRaises(
            TechnologyRadarInvariantError
        ):
            radar.rank(
                [high, high]
            )

    def test_module_has_no_network_or_authority_escalation_imports(
        self,
    ):
        path = Path(
            "src/maestro/research/"
            "technology_radar.py"
        )

        tree = ast.parse(
            path.read_text(
                encoding="utf-8"
            )
        )

        imported = set()

        for node in ast.walk(tree):
            if isinstance(
                node,
                ast.Import,
            ):
                for alias in node.names:
                    imported.add(
                        alias.name
                    )

            elif isinstance(
                node,
                ast.ImportFrom,
            ):
                if node.module:
                    imported.add(
                        node.module
                    )

        forbidden = (
            "socket",
            "http",
            "urllib",
            "requests",
            "subprocess",
            "maestro.learning",
            "maestro.adaptive",
            (
                "maestro."
                "outcome_governed_adaptation"
            ),
            (
                "maestro."
                "governed_activation"
            ),
            "maestro.tools",
            "maestro.autonomous",
        )

        violations = sorted(
            name
            for name in imported
            if any(
                name == prefix
                or name.startswith(
                    prefix + "."
                )
                for prefix in forbidden
            )
        )

        self.assertEqual(
            violations,
            [],
        )


if __name__ == "__main__":
    unittest.main()
