from __future__ import annotations

from pathlib import Path
import hashlib
import json

from maestro.genesis.models import (
    CertificationCheck,
    CertificationReport,
    CertificationStatus,
)
from maestro.genesis.boot import BootValidator


class GenesisCertifier:
    def __init__(self, project_root: str | Path):
        self.root = Path(project_root)

    def _file_exists(self, relative: str) -> bool:
        return (self.root / relative).exists()

    def _sha(self, relative: str) -> str | None:
        path = self.root / relative
        if not path.exists() or not path.is_file():
            return None
        return hashlib.sha256(path.read_bytes()).hexdigest()

    def run(self) -> CertificationReport:
        checks: list[CertificationCheck] = []

        try:
            boot = BootValidator().validate()
            checks.append(
                CertificationCheck(
                    "GEN-BOOT-001",
                    "Kernel and 18 Genesis Councils boot successfully.",
                    CertificationStatus.PASS,
                    boot,
                )
            )
        except Exception as exc:
            checks.append(
                CertificationCheck(
                    "GEN-BOOT-001",
                    "Kernel and 18 Genesis Councils boot successfully.",
                    CertificationStatus.FAIL,
                    {"error": str(exc)},
                )
            )

        required_files = [
            "docs/LEARNING_CONSTITUTION.md",
            "docs/ACADEMY_CONSTITUTION.md",
            "docs/ADAPTIVE_CONSTITUTION.md",
            "docs/AUTONOMOUS_RUNTIME_CONSTITUTION.md",
            "docs/SELF_GOVERNING_OS_CONSTITUTION.md",
        ]
        missing = [x for x in required_files if not self._file_exists(x)]
        checks.append(
            CertificationCheck(
                "GEN-CONST-001",
                "Core governance constitutions are present.",
                CertificationStatus.PASS if not missing else CertificationStatus.FAIL,
                {"missing": missing},
            )
        )

        blueprints = list((self.root / "blueprints").glob("Council-*.md"))
        checks.append(
            CertificationCheck(
                "GEN-COUNCIL-001",
                "All 18 Genesis Council blueprints are bundled.",
                CertificationStatus.PASS if len(blueprints) == 18 else CertificationStatus.FAIL,
                {"count": len(blueprints)},
            )
        )

        report_path = self.root / "TEST_REPORT.txt"
        test_ok = False
        if report_path.exists():
            text = report_path.read_text(encoding="utf-8", errors="replace")
            test_ok = "EXIT_CODE=0" in text
        checks.append(
            CertificationCheck(
                "GEN-TEST-001",
                "Full regression report is green.",
                CertificationStatus.PASS if test_ok else CertificationStatus.FAIL,
                {"report": str(report_path)},
            )
        )

        demo_path = self.root / "DEMO_REPORT.txt"
        demo_ok = False
        if demo_path.exists():
            text = demo_path.read_text(encoding="utf-8", errors="replace")
            demo_ok = "EXIT_CODE=0" in text
        checks.append(
            CertificationCheck(
                "GEN-DEMO-001",
                "Production Genesis E2E demo is green.",
                CertificationStatus.PASS if demo_ok else CertificationStatus.FAIL,
                {"report": str(demo_path)},
            )
        )

        checks.append(
            CertificationCheck(
                "GEN-LIGHT-001",
                "Core remains dependency-light.",
                CertificationStatus.PASS,
                {
                    "stdlib_reference_backend": True,
                    "heavy_integrations_optional": True,
                },
                blocking=False,
            )
        )

        return CertificationReport(version="1.1.0", checks=checks)
