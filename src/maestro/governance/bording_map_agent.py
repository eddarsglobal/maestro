from __future__ import annotations

import argparse
import hashlib
import json
import re

from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Mapping


_MACHINE_START = "<!-- BORDING_MAP_MACHINE_START -->"
_MACHINE_END = "<!-- BORDING_MAP_MACHINE_END -->"
_POINT_ID_RE = re.compile(r"BMF-\d{3}")


class BordingMapInvariantError(ValueError):
    """Raised when the governed BordingMap contract is malformed."""


class BordingMapGate(StrEnum):
    EVERGREEN = "EVERGREEN"
    PROJECT = "PROJECT"


class BordingMapAssessmentState(StrEnum):
    PASS = "PASS"
    DEFERRED = "DEFERRED"
    NOT_APPLICABLE = "NOT_APPLICABLE"
    BLOCKED = "BLOCKED"


@dataclass(frozen=True, slots=True)
class BordingMapPoint:
    point_id: str
    gate: BordingMapGate
    category: str
    title: str

    def __post_init__(self) -> None:
        if not _POINT_ID_RE.fullmatch(self.point_id):
            raise BordingMapInvariantError(
                f"Invalid BordingMap point ID: {self.point_id!r}."
            )

        if not isinstance(self.gate, BordingMapGate):
            raise TypeError("gate must be BordingMapGate.")

        if not isinstance(self.category, str) or not self.category.strip():
            raise BordingMapInvariantError(
                "Point category must be non-empty."
            )

        if not isinstance(self.title, str) or not self.title.strip():
            raise BordingMapInvariantError(
                "Point title must be non-empty."
            )


@dataclass(frozen=True, slots=True)
class BordingMapDefinition:
    schema_version: int
    name: str
    points: tuple[BordingMapPoint, ...]

    def __post_init__(self) -> None:
        if (
            not isinstance(self.schema_version, int)
            or isinstance(self.schema_version, bool)
            or self.schema_version < 1
        ):
            raise BordingMapInvariantError(
                "schema_version must be an integer >= 1."
            )

        if not isinstance(self.name, str) or not self.name.strip():
            raise BordingMapInvariantError(
                "Map name must be non-empty."
            )

        if not self.points:
            raise BordingMapInvariantError(
                "BordingMap must contain at least one point."
            )

        ids = tuple(point.point_id for point in self.points)

        if len(ids) != len(set(ids)):
            raise BordingMapInvariantError(
                "Duplicate BordingMap point IDs."
            )

    @property
    def point_ids(self) -> tuple[str, ...]:
        return tuple(point.point_id for point in self.points)

    @property
    def fingerprint(self) -> str:
        payload = {
            "schema_version": self.schema_version,
            "name": self.name,
            "points": [
                {
                    "id": point.point_id,
                    "gate": point.gate.value,
                    "category": point.category,
                    "title": point.title,
                }
                for point in self.points
            ],
        }

        encoded = json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")

        return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True, slots=True)
class BordingMapAssessment:
    point_id: str
    state: BordingMapAssessmentState
    evidence: tuple[str, ...] = ()
    note: str = ""

    def __post_init__(self) -> None:
        if not _POINT_ID_RE.fullmatch(self.point_id):
            raise BordingMapInvariantError(
                "Invalid assessment point ID."
            )

        if not isinstance(self.state, BordingMapAssessmentState):
            raise TypeError(
                "state must be BordingMapAssessmentState."
            )

        if not isinstance(self.evidence, tuple):
            raise TypeError("evidence must be tuple[str, ...].")

        for item in self.evidence:
            if not isinstance(item, str) or not item.strip():
                raise BordingMapInvariantError(
                    "Evidence entries must be non-empty strings."
                )

        if not isinstance(self.note, str):
            raise TypeError("note must be str.")

        if (
            self.state is BordingMapAssessmentState.PASS
            and not self.evidence
        ):
            raise BordingMapInvariantError(
                "PASS requires explicit evidence."
            )

        if (
            self.state is not BordingMapAssessmentState.PASS
            and not self.note.strip()
        ):
            raise BordingMapInvariantError(
                f"{self.state.value} requires an explicit note."
            )


@dataclass(frozen=True, slots=True)
class VersionBordingMapAudit:
    version: str
    map_fingerprint: str
    total_points: int
    pass_count: int
    deferred_count: int
    not_applicable_count: int
    blocked_count: int
    progress_basis_points: int
    completed_point_ids: tuple[str, ...]
    deferred_point_ids: tuple[str, ...]
    not_applicable_point_ids: tuple[str, ...]
    blocked_point_ids: tuple[str, ...]
    missing_assessment_ids: tuple[str, ...]
    evergreen_violation_ids: tuple[str, ...]
    next_point_id: str | None
    release_ready: bool
    project_complete: bool

    authority_asserted: bool = False
    ay_verdict_asserted: bool = False
    ex_authorization_asserted: bool = False
    promotion_authority: bool = False
    activation_authority: bool = False
    installation_authority: bool = False
    execution_authority: bool = False
    system_truth_asserted: bool = False

    @property
    def progress_percent(self) -> float:
        return self.progress_basis_points / 100

    def as_dict(self) -> dict[str, object]:
        return {
            "version": self.version,
            "map_fingerprint": self.map_fingerprint,
            "total_points": self.total_points,
            "pass_count": self.pass_count,
            "deferred_count": self.deferred_count,
            "not_applicable_count": self.not_applicable_count,
            "blocked_count": self.blocked_count,
            "progress_basis_points": self.progress_basis_points,
            "progress_percent": self.progress_percent,
            "completed_point_ids": list(self.completed_point_ids),
            "deferred_point_ids": list(self.deferred_point_ids),
            "not_applicable_point_ids": list(
                self.not_applicable_point_ids
            ),
            "blocked_point_ids": list(self.blocked_point_ids),
            "missing_assessment_ids": list(
                self.missing_assessment_ids
            ),
            "evergreen_violation_ids": list(
                self.evergreen_violation_ids
            ),
            "next_point_id": self.next_point_id,
            "release_ready": self.release_ready,
            "project_complete": self.project_complete,
            "authority_asserted": self.authority_asserted,
            "ay_verdict_asserted": self.ay_verdict_asserted,
            "ex_authorization_asserted": (
                self.ex_authorization_asserted
            ),
            "promotion_authority": self.promotion_authority,
            "activation_authority": self.activation_authority,
            "installation_authority": self.installation_authority,
            "execution_authority": self.execution_authority,
            "system_truth_asserted": self.system_truth_asserted,
        }


class BordingMapControlAgent:
    """
    Deterministic read-only development governance assistant.

    AUDIT != AUTHORIZATION
    REPORT != VERDICT
    RELEASE_READY != RELEASE AUTHORIZED
    """

    @staticmethod
    def parse_text(text: str) -> BordingMapDefinition:
        if not isinstance(text, str):
            raise TypeError("text must be str.")

        if (
            text.count(_MACHINE_START) != 1
            or text.count(_MACHINE_END) != 1
        ):
            raise BordingMapInvariantError(
                "BordingMap machine markers must exist exactly once."
            )

        start = text.index(_MACHINE_START) + len(_MACHINE_START)
        end = text.index(_MACHINE_END, start)

        block = text[start:end].strip()
        lines = block.splitlines()

        if lines and lines[0].strip().startswith("```"):
            lines = lines[1:]

        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        raw = "\n".join(lines).strip()

        try:
            payload = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise BordingMapInvariantError(
                "Invalid machine-readable BordingMap JSON."
            ) from exc

        if not isinstance(payload, dict):
            raise BordingMapInvariantError(
                "BordingMap payload must be an object."
            )

        rows = payload.get("points")

        if not isinstance(rows, list):
            raise BordingMapInvariantError(
                "BordingMap points must be a list."
            )

        points: list[BordingMapPoint] = []

        for row in rows:
            if not isinstance(row, dict):
                raise BordingMapInvariantError(
                    "Each BordingMap point must be an object."
                )

            try:
                point = BordingMapPoint(
                    point_id=row["id"],
                    gate=BordingMapGate(row["gate"]),
                    category=row["category"],
                    title=row["title"],
                )
            except (KeyError, ValueError) as exc:
                raise BordingMapInvariantError(
                    "Malformed BordingMap point."
                ) from exc

            points.append(point)

        return BordingMapDefinition(
            schema_version=payload.get("schema_version"),
            name=payload.get("name"),
            points=tuple(points),
        )

    @classmethod
    def load(
        cls,
        path: str | Path,
    ) -> BordingMapDefinition:
        return cls.parse_text(
            Path(path).read_text(encoding="utf-8")
        )

    @staticmethod
    def _assessment_from_raw(
        point_id: str,
        raw: object,
    ) -> BordingMapAssessment:
        if not isinstance(raw, Mapping):
            raise BordingMapInvariantError(
                "Assessment must be an object."
            )

        try:
            state = BordingMapAssessmentState(raw["state"])
        except (KeyError, ValueError) as exc:
            raise BordingMapInvariantError(
                "Invalid assessment state."
            ) from exc

        evidence_raw = raw.get("evidence", ())

        if not isinstance(evidence_raw, (list, tuple)):
            raise BordingMapInvariantError(
                "Assessment evidence must be a list."
            )

        if any(not isinstance(item, str) for item in evidence_raw):
            raise BordingMapInvariantError(
                "Assessment evidence entries must be strings."
            )

        note = raw.get("note", "")

        if not isinstance(note, str):
            raise BordingMapInvariantError(
                "Assessment note must be str."
            )

        return BordingMapAssessment(
            point_id=point_id,
            state=state,
            evidence=tuple(evidence_raw),
            note=note,
        )

    @classmethod
    def audit(
        cls,
        definition: BordingMapDefinition,
        *,
        version: str,
        assessments: Mapping[str, object],
    ) -> VersionBordingMapAudit:
        if not isinstance(definition, BordingMapDefinition):
            raise TypeError(
                "definition must be BordingMapDefinition."
            )

        if not isinstance(version, str) or not version.strip():
            raise BordingMapInvariantError(
                "Version must be non-empty."
            )

        if not isinstance(assessments, Mapping):
            raise TypeError(
                "assessments must be a Mapping."
            )

        known = set(definition.point_ids)
        supplied = set(assessments)

        unknown = supplied - known

        if unknown:
            raise BordingMapInvariantError(
                "Unknown assessment point IDs: "
                + ", ".join(sorted(unknown))
            )

        parsed = {
            point_id: cls._assessment_from_raw(
                point_id,
                raw,
            )
            for point_id, raw in assessments.items()
        }

        missing = tuple(
            point_id
            for point_id in definition.point_ids
            if point_id not in parsed
        )

        completed = tuple(
            point_id
            for point_id in definition.point_ids
            if (
                point_id in parsed
                and parsed[point_id].state
                is BordingMapAssessmentState.PASS
            )
        )

        deferred = tuple(
            point_id
            for point_id in definition.point_ids
            if (
                point_id in parsed
                and parsed[point_id].state
                is BordingMapAssessmentState.DEFERRED
            )
        )

        not_applicable = tuple(
            point_id
            for point_id in definition.point_ids
            if (
                point_id in parsed
                and parsed[point_id].state
                is BordingMapAssessmentState.NOT_APPLICABLE
            )
        )

        blocked = tuple(
            point_id
            for point_id in definition.point_ids
            if (
                point_id in parsed
                and parsed[point_id].state
                is BordingMapAssessmentState.BLOCKED
            )
        )

        evergreen_violations = tuple(
            point.point_id
            for point in definition.points
            if (
                point.gate is BordingMapGate.EVERGREEN
                and (
                    point.point_id not in parsed
                    or parsed[point.point_id].state
                    is not BordingMapAssessmentState.PASS
                )
            )
        )

        total = len(definition.points)

        progress_basis_points = (
            len(completed) * 10_000 // total
        )

        next_point = next(
            (
                point_id
                for point_id in definition.point_ids
                if point_id not in completed
            ),
            None,
        )

        release_ready = (
            not missing
            and not blocked
            and not evergreen_violations
        )

        project_complete = (
            not missing
            and len(completed) == total
        )

        return VersionBordingMapAudit(
            version=version.strip(),
            map_fingerprint=definition.fingerprint,
            total_points=total,
            pass_count=len(completed),
            deferred_count=len(deferred),
            not_applicable_count=len(not_applicable),
            blocked_count=len(blocked),
            progress_basis_points=progress_basis_points,
            completed_point_ids=completed,
            deferred_point_ids=deferred,
            not_applicable_point_ids=not_applicable,
            blocked_point_ids=blocked,
            missing_assessment_ids=missing,
            evergreen_violation_ids=evergreen_violations,
            next_point_id=next_point,
            release_ready=release_ready,
            project_complete=project_complete,
        )

    @classmethod
    def audit_payload(
        cls,
        definition: BordingMapDefinition,
        payload: object,
    ) -> VersionBordingMapAudit:
        if not isinstance(payload, Mapping):
            raise BordingMapInvariantError(
                "Version assessment payload must be an object."
            )

        version = payload.get("version")
        assessments = payload.get("assessments")

        if not isinstance(assessments, Mapping):
            raise BordingMapInvariantError(
                "Payload assessments must be an object."
            )

        return cls.audit(
            definition,
            version=version,
            assessments=assessments,
        )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "MAESTRO governed BordingMap version-control agent."
        )
    )

    parser.add_argument(
        "--map",
        default="docs/BordingMapFile.md",
    )

    parser.add_argument(
        "--assessment",
        required=True,
    )

    parser.add_argument(
        "--final",
        action="store_true",
        help=(
            "Require PROJECT_COMPLETE instead of "
            "intermediate RELEASE_READY."
        ),
    )

    args = parser.parse_args(argv)

    definition = BordingMapControlAgent.load(args.map)

    payload = json.loads(
        Path(args.assessment).read_text(
            encoding="utf-8"
        )
    )

    audit = BordingMapControlAgent.audit_payload(
        definition,
        payload,
    )

    print(
        json.dumps(
            audit.as_dict(),
            indent=2,
            sort_keys=True,
        )
    )

    if args.final:
        return 0 if audit.project_complete else 3

    return 0 if audit.release_ready else 2


if __name__ == "__main__":
    raise SystemExit(main())
