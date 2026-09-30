from __future__ import annotations

from dataclasses import dataclass, field, asdict
from enum import StrEnum
from typing import Any
from datetime import datetime, timezone


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class CertificationStatus(StrEnum):
    PASS = "PASS"
    FAIL = "FAIL"
    WARN = "WARN"


class HealthStatus(StrEnum):
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    UNHEALTHY = "UNHEALTHY"


@dataclass(slots=True)
class CertificationCheck:
    check_id: str
    description: str
    status: CertificationStatus
    evidence: dict[str, Any] = field(default_factory=dict)
    blocking: bool = True


@dataclass(slots=True)
class CertificationReport:
    version: str
    checks: list[CertificationCheck]
    created_at: str = field(default_factory=utc_now)

    @property
    def passed(self) -> bool:
        return all(
            c.status is not CertificationStatus.FAIL
            for c in self.checks
            if c.blocking
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "created_at": self.created_at,
            "passed": self.passed,
            "checks": [
                {
                    **asdict(c),
                    "status": c.status.value,
                }
                for c in self.checks
            ],
        }


@dataclass(slots=True)
class HealthReport:
    status: HealthStatus
    components: dict[str, dict[str, Any]]
    created_at: str = field(default_factory=utc_now)

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status.value,
            "components": self.components,
            "created_at": self.created_at,
        }
