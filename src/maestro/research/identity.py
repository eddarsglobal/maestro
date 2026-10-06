from __future__ import annotations

import re


_DURABLE_RESEARCH_TASK_ID_RE = re.compile(
    r"TASK-[A-F0-9]{12}"
)


def require_durable_research_task_id(
    value: str,
) -> str:
    """
    Validate a task identity crossing the durable
    Research evidence boundary.

    Runtime task identifiers may be broader, but
    durable RX evidence accepts canonical MAESTRO
    mission identifiers only.

    The rejected value is intentionally never
    included in an exception message.
    """

    if not isinstance(value, str):
        raise TypeError(
            "durable research task_id "
            "must be a string."
        )

    if (
        _DURABLE_RESEARCH_TASK_ID_RE
        .fullmatch(value)
        is None
    ):
        raise ValueError(
            "durable research task_id must "
            "match TASK-[A-F0-9]{12}."
        )

    return value
