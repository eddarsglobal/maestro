from __future__ import annotations

import hashlib
import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any

from maestro.enums import CouncilId, EvidenceKind
from maestro.models import Evidence

from .contracts import TrustState
from .identity import (
    require_durable_research_task_id,
)


RESEARCH_EVIDENCE_SCHEMA = "maestro.research_evidence.v0.1"


_SQL_SCHEMA = """
CREATE TABLE IF NOT EXISTS research_evidence (
    evidence_id TEXT PRIMARY KEY,
    task_id TEXT NOT NULL,
    source_ref TEXT NOT NULL,
    schema_name TEXT NOT NULL,
    canonical_json TEXT NOT NULL,
    sha256 TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS
idx_research_evidence_task
ON research_evidence(task_id);

CREATE INDEX IF NOT EXISTS
idx_research_evidence_source
ON research_evidence(source_ref);
"""


class ResearchEvidenceStoreError(RuntimeError):
    pass


class ResearchEvidenceConflictError(
    ResearchEvidenceStoreError
):
    pass


class ResearchEvidenceCorruptionError(
    ResearchEvidenceStoreError
):
    pass


def _canonical_json(
    payload: dict[str, Any],
) -> str:
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )


def _sha256_text(value: str) -> str:
    return hashlib.sha256(
        value.encode("utf-8")
    ).hexdigest()


def _evidence_from_dict(
    raw: dict[str, Any],
) -> Evidence:
    return Evidence(
        task_id=str(raw["task_id"]),
        council=CouncilId(
            str(raw["council"])
        ),
        kind=EvidenceKind(
            str(raw["kind"])
        ),
        claim=str(raw["claim"]),
        payload=raw["payload"],
        source_ref=(
            str(raw["source_ref"])
            if raw.get("source_ref")
            is not None
            else None
        ),
        created_at=str(raw["created_at"]),
        evidence_id=str(
            raw["evidence_id"]
        ),
    )


def _validate_research_evidence(
    evidence: Evidence,
) -> None:
    if not isinstance(evidence, Evidence):
        raise TypeError(
            "evidence must be an Evidence."
        )

    require_durable_research_task_id(
        evidence.task_id
    )

    if evidence.council is not CouncilId.RX:
        raise ValueError(
            "ResearchEvidenceStore accepts RX evidence only."
        )

    if (
        evidence.kind
        is not EvidenceKind.WEB_SOURCE
    ):
        raise ValueError(
            "ResearchEvidenceStore accepts "
            "WEB_SOURCE evidence only."
        )

    if (
        not isinstance(
            evidence.source_ref,
            str,
        )
        or not evidence.source_ref.strip()
    ):
        raise ValueError(
            "Research evidence requires source_ref."
        )

    if not isinstance(
        evidence.payload,
        dict,
    ):
        raise ValueError(
            "Research evidence payload "
            "must be a dictionary."
        )

    claim = evidence.payload.get(
        "research_claim"
    )

    if not isinstance(claim, dict):
        raise ValueError(
            "Research evidence requires "
            "research_claim payload."
        )

    if (
        claim.get("claim_id")
        != evidence.source_ref
    ):
        raise ValueError(
            "Evidence source_ref must equal "
            "research claim_id."
        )

    if (
        claim.get("statement")
        != evidence.claim
    ):
        raise ValueError(
            "Evidence claim must equal "
            "research claim statement."
        )

    artifact_ids = claim.get(
        "artifact_ids"
    )

    if (
        not isinstance(
            artifact_ids,
            list,
        )
        or not artifact_ids
    ):
        raise ValueError(
            "Research claim requires "
            "artifact_ids."
        )

    artifacts = evidence.payload.get(
        "artifacts"
    )

    if (
        not isinstance(artifacts, list)
        or not artifacts
    ):
        raise ValueError(
            "Research evidence requires "
            "artifacts."
        )

    stored_ids = []

    for artifact in artifacts:
        if not isinstance(
            artifact,
            dict,
        ):
            raise ValueError(
                "Research artifact payload "
                "must be a dictionary."
            )

        artifact_id = artifact.get(
            "artifact_id"
        )

        if (
            not isinstance(
                artifact_id,
                str,
            )
            or not artifact_id
        ):
            raise ValueError(
                "Research artifact requires "
                "artifact_id."
            )

        stored_ids.append(
            artifact_id
        )

    if len(set(stored_ids)) != len(
        stored_ids
    ):
        raise ValueError(
            "Research evidence contains "
            "duplicate artifacts."
        )

    if stored_ids != artifact_ids:
        raise ValueError(
            "Research claim/artifact relation "
            "does not match."
        )

    verification = evidence.payload.get(
        "verification"
    )

    if not isinstance(
        verification,
        dict,
    ):
        raise ValueError(
            "Research evidence requires "
            "verification metadata."
        )

    if (
        verification.get("status")
        != "UNVERIFIED_EXTERNAL"
    ):
        raise ValueError(
            "External research must remain "
            "UNVERIFIED_EXTERNAL."
        )

    if (
        verification.get(
            "required_authority"
        )
        != CouncilId.AY.value
    ):
        raise ValueError(
            "AY must remain the required "
            "verification authority."
        )

    if (
        verification.get(
            "system_truth_asserted"
        )
        is not False
    ):
        raise ValueError(
            "Research evidence may not assert "
            "system truth."
        )

    allowed_trust = {
        state.value
        for state in TrustState
    }

    if (
        claim.get("trust_state")
        not in allowed_trust
    ):
        raise ValueError(
            "Invalid research claim trust state."
        )

    for artifact in artifacts:
        if (
            artifact.get("trust_state")
            not in allowed_trust
        ):
            raise ValueError(
                "Invalid research artifact "
                "trust state."
            )


class ResearchEvidenceStore:
    """
    Durable RX WEB_SOURCE evidence store.

    It persists external research observations.
    It does not perform truth validation, AY verdicts,
    learning, promotion, or execution.
    """

    def __init__(
        self,
        path: str | Path,
    ):
        self.path = Path(path)
        self.path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        con = self._connect()

        try:
            con.execute(
                "PRAGMA journal_mode=WAL"
            )
            con.executescript(
                _SQL_SCHEMA
            )
        finally:
            con.close()

    def _connect(self):
        con = sqlite3.connect(
            self.path,
            timeout=30.0,
            isolation_level=None,
        )

        con.row_factory = sqlite3.Row

        con.execute(
            "PRAGMA foreign_keys=ON"
        )
        con.execute(
            "PRAGMA busy_timeout=30000"
        )
        con.execute(
            "PRAGMA synchronous=FULL"
        )

        return con

    @contextmanager
    def _immediate(self):
        con = self._connect()

        try:
            con.execute(
                "BEGIN IMMEDIATE"
            )

            yield con

            con.execute(
                "COMMIT"
            )
        except Exception:
            if con.in_transaction:
                con.execute(
                    "ROLLBACK"
                )
            raise
        finally:
            con.close()

    @staticmethod
    def _serialize(
        evidence: Evidence,
    ) -> tuple[str, str]:
        _validate_research_evidence(
            evidence
        )

        envelope = {
            "schema": (
                RESEARCH_EVIDENCE_SCHEMA
            ),
            "evidence": (
                evidence.to_dict()
            ),
        }

        canonical = _canonical_json(
            envelope
        )

        return (
            canonical,
            _sha256_text(canonical),
        )

    def record(
        self,
        evidence: Evidence,
    ) -> str:
        canonical, digest = (
            self._serialize(evidence)
        )

        with self._immediate() as con:
            existing = con.execute(
                """
                SELECT
                    evidence_id,
                    task_id,
                    source_ref,
                    schema_name,
                    canonical_json,
                    sha256,
                    created_at
                FROM research_evidence
                WHERE evidence_id = ?
                """,
                (evidence.evidence_id,),
            ).fetchone()

            if existing is not None:
                if (
                    existing["canonical_json"]
                    != canonical
                    or existing["sha256"]
                    != digest
                ):
                    raise (
                        ResearchEvidenceConflictError(
                            "Evidence ID already "
                            "exists with different "
                            "content."
                        )
                    )

                expected_metadata = {
                    "evidence_id": evidence.evidence_id,
                    "task_id": evidence.task_id,
                    "source_ref": evidence.source_ref,
                    "schema_name": RESEARCH_EVIDENCE_SCHEMA,
                    "created_at": evidence.created_at,
                }

                actual_metadata = {
                    key: existing[key]
                    for key in expected_metadata
                }

                if actual_metadata != expected_metadata:
                    raise (
                        ResearchEvidenceCorruptionError(
                            "Existing research evidence "
                            "index/body metadata mismatch."
                        )
                    )

                return evidence.evidence_id

            con.execute(
                """
                INSERT INTO research_evidence (
                    evidence_id,
                    task_id,
                    source_ref,
                    schema_name,
                    canonical_json,
                    sha256,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    evidence.evidence_id,
                    evidence.task_id,
                    evidence.source_ref,
                    RESEARCH_EVIDENCE_SCHEMA,
                    canonical,
                    digest,
                    evidence.created_at,
                ),
            )

        return evidence.evidence_id

    def get(
        self,
        evidence_id: str,
    ) -> Evidence:
        con = self._connect()

        try:
            row = con.execute(
                """
                SELECT *
                FROM research_evidence
                WHERE evidence_id = ?
                """,
                (evidence_id,),
            ).fetchone()
        finally:
            con.close()

        if row is None:
            raise KeyError(evidence_id)

        canonical = str(
            row["canonical_json"]
        )

        if (
            _sha256_text(canonical)
            != row["sha256"]
        ):
            raise (
                ResearchEvidenceCorruptionError(
                    "Research evidence checksum "
                    "mismatch."
                )
            )

        try:
            envelope = json.loads(
                canonical
            )
        except Exception as exc:
            raise (
                ResearchEvidenceCorruptionError(
                    "Research evidence contains "
                    "invalid JSON."
                )
            ) from exc

        if not isinstance(
            envelope,
            dict,
        ):
            raise (
                ResearchEvidenceCorruptionError(
                    "Malformed research evidence "
                    "envelope."
                )
            )

        if (
            envelope.get("schema")
            != RESEARCH_EVIDENCE_SCHEMA
            or row["schema_name"]
            != RESEARCH_EVIDENCE_SCHEMA
        ):
            raise (
                ResearchEvidenceCorruptionError(
                    "Unsupported research evidence "
                    "schema."
                )
            )

        if (
            _canonical_json(envelope)
            != canonical
        ):
            raise (
                ResearchEvidenceCorruptionError(
                    "Research evidence is not "
                    "canonically encoded."
                )
            )

        try:
            raw = envelope["evidence"]

            if not isinstance(raw, dict):
                raise TypeError(
                    "evidence body is not a dict"
                )

            evidence = (
                _evidence_from_dict(raw)
            )

            _validate_research_evidence(
                evidence
            )
        except Exception as exc:
            raise (
                ResearchEvidenceCorruptionError(
                    "Stored research evidence "
                    "failed validation."
                )
            ) from exc

        if (
            evidence.evidence_id
            != row["evidence_id"]
            or evidence.task_id
            != row["task_id"]
            or evidence.source_ref
            != row["source_ref"]
            or evidence.created_at
            != row["created_at"]
        ):
            raise (
                ResearchEvidenceCorruptionError(
                    "Research evidence index/body "
                    "mismatch."
                )
            )

        return evidence

    def ids(self) -> list[str]:
        con = self._connect()

        try:
            rows = con.execute(
                """
                SELECT evidence_id
                FROM research_evidence
                ORDER BY evidence_id
                """
            ).fetchall()
        finally:
            con.close()

        return [
            str(row["evidence_id"])
            for row in rows
        ]

    def for_task(
        self,
        task_id: str,
    ) -> list[Evidence]:
        task_id = (
            require_durable_research_task_id(
                task_id
            )
        )

        con = self._connect()

        try:
            rows = con.execute(
                """
                SELECT evidence_id
                FROM research_evidence
                WHERE task_id = ?
                ORDER BY evidence_id
                """,
                (task_id,),
            ).fetchall()
        finally:
            con.close()

        return [
            self.get(
                str(row["evidence_id"])
            )
            for row in rows
        ]

    def count(self) -> int:
        con = self._connect()

        try:
            row = con.execute(
                """
                SELECT COUNT(*) AS n
                FROM research_evidence
                """
            ).fetchone()
        finally:
            con.close()

        return int(row["n"])
