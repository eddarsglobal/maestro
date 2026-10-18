"""Request-local cancellation token shared by research transport and connector.

The token does not grant network access. It is deliberately not process-global
mutable state: nested and concurrent missions retain separate context values.
"""
from contextvars import ContextVar

ACTIVE_HTTP_CANCELLATION: ContextVar = ContextVar(
    "maestro_governed_http_mission_cancellation", default=None
)
