from __future__ import annotations


class CognitiveQualityGate:
    """
    Fabric quality gate is advisory and structural.
    AY remains the SYSTEM validation authority.
    """

    def stage_quality(self, artifact) -> float:
        if not artifact.success:
            return 0.0
        output = artifact.output.strip()
        if not output:
            return 0.0
        # Lightweight structural baseline only.
        return min(1.0, 0.5 + min(len(output), 1000) / 2000.0)

    def report_complete(self, report) -> bool:
        return report.completed and not report.failed_stage_ids
