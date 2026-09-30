from __future__ import annotations

from dataclasses import dataclass

from maestro.genesis.models import CertificationReport


class ReleaseDenied(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class ReleaseEvidence:
    certification_passed: bool
    test_exit_code: int
    demo_exit_code: int
    constitution_hash_present: bool
    manifest_present: bool
    rollback_supported: bool


class ProductionReleaseGate:
    """
    Final software-release gate for MAESTRO itself.

    This is distinct from AY task-level SYSTEM verdicts.
    """

    def authorize(self, evidence: ReleaseEvidence) -> bool:
        if not evidence.certification_passed:
            raise ReleaseDenied("Genesis certification failed.")
        if evidence.test_exit_code != 0:
            raise ReleaseDenied("Regression suite failed.")
        if evidence.demo_exit_code != 0:
            raise ReleaseDenied("E2E demonstration failed.")
        if not evidence.constitution_hash_present:
            raise ReleaseDenied("Constitution fingerprint missing.")
        if not evidence.manifest_present:
            raise ReleaseDenied("Release manifest missing.")
        if not evidence.rollback_supported:
            raise ReleaseDenied("Rollback capability required.")
        return True
