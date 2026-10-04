from __future__ import annotations

import socket
import time
from collections.abc import Callable
from dataclasses import dataclass
from ipaddress import ip_address
from typing import Any

from .resolver import (
    GovernedSourceResolver,
    NumericSourceEndpoint,
    SourceResolution,
)
from .source_access import (
    SourceAccessPolicy,
    SourceAccessTarget,
)


BOUND_SOURCE_CONNECTOR_VERSION = "RX0.3B2A"


class SourceConnectionInvariantError(
    ValueError
):
    """
    A resolver/connector contract invariant
    was violated before network connection.
    """


@dataclass(
    frozen=True,
    slots=True,
)
class SourceConnectionAttempt:
    endpoint: NumericSourceEndpoint
    error_type: str


class SourceConnectionError(
    ConnectionError
):
    def __init__(
        self,
        message: str,
        attempts: tuple[
            SourceConnectionAttempt,
            ...,
        ] = (),
    ):
        super().__init__(message)
        self.attempts = tuple(attempts)


@dataclass(
    frozen=True,
    slots=True,
)
class BoundSourceConnection:
    """
    Successful TCP connection bound to one
    previously validated numeric endpoint.

    The socket remains owned by the caller.
    """

    target: SourceAccessTarget
    endpoint: NumericSourceEndpoint
    socket: Any

    def close(self) -> None:
        self.socket.close()


SocketFactory = Callable[
    [int, int, int],
    Any,
]


class BoundSourceConnector:
    """
    DNS-to-TCP boundary for external research.

    Public connection entry points always invoke a
    GovernedSourceResolver first. SourceResolution
    is an internal data contract, never an authority
    token accepted directly from an external caller.

    The TCP connect phase receives numeric sockaddrs
    only and performs no hostname resolution.

    SourceAccessPolicy.timeout_seconds is enforced
    here as one total TCP-connect budget across all
    validated endpoints. It still does NOT bound the
    preceding blocking system DNS resolution.
    """

    def __init__(
        self,
        resolver: (
            GovernedSourceResolver | None
        ) = None,
        *,
        socket_factory: (
            SocketFactory | None
        ) = None,
        monotonic: (
            Callable[[], float] | None
        ) = None,
    ):
        self.resolver = (
            resolver
            if resolver is not None
            else GovernedSourceResolver()
        )

        if not isinstance(
            self.resolver,
            GovernedSourceResolver,
        ):
            raise TypeError(
                "resolver must be a "
                "GovernedSourceResolver."
            )

        self.policy = self.resolver.policy

        if not isinstance(
            self.policy,
            SourceAccessPolicy,
        ):
            raise TypeError(
                "resolver policy must be a "
                "SourceAccessPolicy."
            )

        self._socket_factory = (
            socket_factory
            if socket_factory is not None
            else socket.socket
        )

        if not callable(
            self._socket_factory
        ):
            raise TypeError(
                "socket_factory must be "
                "callable."
            )

        self._monotonic = (
            monotonic
            if monotonic is not None
            else time.monotonic
        )

        if not callable(
            self._monotonic
        ):
            raise TypeError(
                "monotonic must be callable."
            )

    @staticmethod
    def _target_identity(
        target: SourceAccessTarget,
    ) -> tuple[Any, ...]:
        return (
            target.request_url,
            target.scheme,
            target.hostname,
            target.port,
            target.literal_ip,
        )

    @staticmethod
    def _safe_close(
        sock: Any,
    ) -> None:
        if sock is None:
            return

        try:
            sock.close()
        except Exception:
            pass

    def _revalidate_resolution(
        self,
        resolution: SourceResolution,
    ) -> tuple[
        SourceAccessTarget,
        tuple[NumericSourceEndpoint, ...],
    ]:
        if not isinstance(
            resolution,
            SourceResolution,
        ):
            raise TypeError(
                "resolution must be a "
                "SourceResolution."
            )

        target = resolution.target

        canonical = (
            self.policy.prepare_url(
                target.request_url
            )
        )

        if (
            self._target_identity(
                canonical
            )
            != self._target_identity(
                target
            )
        ):
            raise SourceConnectionInvariantError(
                "Resolution target does not "
                "match canonical source policy."
            )

        if (
            self._target_identity(
                resolution.resolved.target
            )
            != self._target_identity(
                target
            )
        ):
            raise SourceConnectionInvariantError(
                "Resolved target identity "
                "mismatch."
            )

        expected_query = (
            None
            if canonical.literal_ip
            is not None
            else canonical.hostname + "."
        )

        if (
            resolution.query_host
            != expected_query
        ):
            raise SourceConnectionInvariantError(
                "Resolution DNS query identity "
                "mismatch."
            )

        endpoints = tuple(
            resolution.endpoints
        )

        if not endpoints:
            raise SourceConnectionInvariantError(
                "Resolution contains no "
                "numeric endpoints."
            )

        addresses: list[str] = []

        for endpoint in endpoints:
            if not isinstance(
                endpoint,
                NumericSourceEndpoint,
            ):
                raise SourceConnectionInvariantError(
                    "Resolution contains an "
                    "invalid endpoint object."
                )

            if (
                endpoint.port
                != canonical.port
            ):
                raise SourceConnectionInvariantError(
                    "Endpoint port does not "
                    "match source target."
                )

            parsed = ip_address(
                endpoint.address
            )

            expected_family = (
                int(socket.AF_INET)
                if parsed.version == 4
                else int(socket.AF_INET6)
            )

            if (
                int(endpoint.family)
                != expected_family
            ):
                raise SourceConnectionInvariantError(
                    "Endpoint family/address "
                    "mismatch."
                )

            addresses.append(
                parsed.compressed
            )

        validated = (
            self.policy
            .validate_resolution(
                canonical,
                addresses,
            )
        )

        endpoint_addresses = tuple(
            endpoint.address
            for endpoint in endpoints
        )

        if (
            validated.addresses
            != endpoint_addresses
        ):
            raise SourceConnectionInvariantError(
                "Endpoint inventory changed "
                "during policy validation."
            )

        if (
            resolution.resolved.addresses
            != endpoint_addresses
        ):
            raise SourceConnectionInvariantError(
                "Resolved address inventory "
                "does not match endpoints."
            )

        return canonical, endpoints

    def _connect_resolution(
        self,
        resolution: SourceResolution,
    ) -> BoundSourceConnection:
        target, endpoints = (
            self._revalidate_resolution(
                resolution
            )
        )

        deadline = (
            float(self._monotonic())
            + self.policy.timeout_seconds
        )

        attempts: list[
            SourceConnectionAttempt
        ] = []

        last_error: Exception | None = None

        for endpoint in endpoints:
            # Revalidate each endpoint immediately
            # before a connect attempt.
            single = (
                self.policy
                .validate_resolution(
                    target,
                    (endpoint.address,),
                )
            )

            if single.addresses != (
                endpoint.address,
            ):
                raise SourceConnectionInvariantError(
                    "Endpoint failed immediate "
                    "pre-connect validation."
                )

            remaining = (
                deadline
                - float(
                    self._monotonic()
                )
            )

            if remaining <= 0.0:
                raise SourceConnectionError(
                    "TCP connection budget "
                    "exhausted.",
                    tuple(attempts),
                ) from last_error

            sock = None

            try:
                sock = self._socket_factory(
                    int(endpoint.family),
                    int(socket.SOCK_STREAM),
                    int(socket.IPPROTO_TCP),
                )

                sock.settimeout(
                    remaining
                )

                # Numeric sockaddr only.
                # No hostname reaches connect().
                sock.connect(
                    endpoint.sockaddr
                )

            except OSError as exc:
                last_error = exc

                attempts.append(
                    SourceConnectionAttempt(
                        endpoint=endpoint,
                        error_type=(
                            type(exc).__name__
                        ),
                    )
                )

                self._safe_close(sock)
                continue

            except Exception:
                # Programming/invariant failures
                # are terminal. They must never
                # masquerade as endpoint failure
                # and trigger network fallback.
                self._safe_close(sock)
                raise

            completed_at = float(
                self._monotonic()
            )

            if completed_at >= deadline:
                self._safe_close(sock)

                timeout_error = TimeoutError(
                    "TCP connection completed "
                    "after budget deadline."
                )

                attempts.append(
                    SourceConnectionAttempt(
                        endpoint=endpoint,
                        error_type=(
                            type(
                                timeout_error
                            ).__name__
                        ),
                    )
                )

                raise SourceConnectionError(
                    "TCP connection budget "
                    "exhausted.",
                    tuple(attempts),
                ) from timeout_error

            return BoundSourceConnection(
                target=target,
                endpoint=endpoint,
                socket=sock,
            )

        raise SourceConnectionError(
            "Unable to connect to any "
            "validated source endpoint.",
            tuple(attempts),
        ) from last_error

    def connect_url(
        self,
        url: str,
    ) -> BoundSourceConnection:
        resolution = (
            self.resolver.resolve_url(
                url
            )
        )

        return self._connect_resolution(
            resolution
        )

    def connect_target(
        self,
        target: SourceAccessTarget,
    ) -> BoundSourceConnection:
        resolution = (
            self.resolver.resolve_target(
                target
            )
        )

        return self._connect_resolution(
            resolution
        )


__all__ = [
    "BOUND_SOURCE_CONNECTOR_VERSION",
    "BoundSourceConnection",
    "BoundSourceConnector",
    "SourceConnectionAttempt",
    "SourceConnectionError",
    "SourceConnectionInvariantError",
]
