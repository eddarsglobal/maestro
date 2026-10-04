from __future__ import annotations

import socket
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from ipaddress import ip_address
from typing import Any

from .source_access import (
    ResolvedSourceTarget,
    SourceAccessPolicy,
    SourceAccessTarget,
)


GetAddrInfo = Callable[
    [
        str,
        int,
        int,
        int,
        int,
        int,
    ],
    Iterable[
        tuple[
            int,
            int,
            int,
            str,
            tuple[Any, ...],
        ]
    ],
]


class SourceResolutionError(
    RuntimeError
):
    pass


@dataclass(
    frozen=True,
    slots=True,
)
class NumericSourceEndpoint:
    family: int
    address: str
    port: int

    def __post_init__(self) -> None:
        if (
            isinstance(self.port, bool)
            or not isinstance(
                self.port,
                int,
            )
            or not 1
            <= self.port
            <= 65535
        ):
            raise ValueError(
                "Endpoint port is invalid."
            )

        try:
            parsed = ip_address(
                self.address
            )
        except ValueError as exc:
            raise ValueError(
                "Endpoint address is invalid."
            ) from exc

        expected_family = (
            int(socket.AF_INET)
            if parsed.version == 4
            else int(socket.AF_INET6)
        )

        if (
            int(self.family)
            != expected_family
        ):
            raise ValueError(
                "Endpoint family does not "
                "match its numeric address."
            )

        object.__setattr__(
            self,
            "family",
            expected_family,
        )

        object.__setattr__(
            self,
            "address",
            parsed.compressed,
        )

    @property
    def sockaddr(
        self,
    ) -> tuple[Any, ...]:
        if (
            self.family
            == int(socket.AF_INET)
        ):
            return (
                self.address,
                self.port,
            )

        return (
            self.address,
            self.port,
            0,
            0,
        )


@dataclass(
    frozen=True,
    slots=True,
)
class SourceResolution:
    # Data contract, not an authority token.
    # A future transport must consume resolutions
    # produced by GovernedSourceResolver and must
    # revalidate the numeric inventory before connect.
    target: SourceAccessTarget
    query_host: str | None
    resolved: ResolvedSourceTarget
    endpoints: tuple[
        NumericSourceEndpoint,
        ...,
    ]

    def __post_init__(self) -> None:
        if (
            self.resolved.target
            != self.target
        ):
            raise ValueError(
                "Resolution target mismatch."
            )

        if not self.endpoints:
            raise ValueError(
                "Resolution requires at least "
                "one numeric endpoint."
            )

        if (
            tuple(
                endpoint.address
                for endpoint
                in self.endpoints
            )
            != self.resolved.addresses
        ):
            raise ValueError(
                "Endpoint inventory does not "
                "match validated addresses."
            )

        if any(
            endpoint.port
            != self.target.port
            for endpoint
            in self.endpoints
        ):
            raise ValueError(
                "Endpoint port mismatch."
            )

        expected_query = (
            None
            if self.target.literal_ip
            is not None
            else (
                self.target.hostname
                + "."
            )
        )

        if (
            self.query_host
            != expected_query
        ):
            raise ValueError(
                "Resolution query mismatch."
            )


class GovernedSourceResolver:
    """
    Resolve an RX0.3A-approved hostname into
    validated numeric endpoints.

    This component performs DNS resolution only.
    It never creates or connects a socket.

    The default system resolver is socket.getaddrinfo.
    That API provides no portable wall-clock timeout
    or cancellation guarantee. Therefore RX0.3B1 does
    NOT claim bounded DNS latency. SourceAccessPolicy
    timeout_seconds applies to a later transport layer,
    not to blocking system name resolution.
    """

    def __init__(
        self,
        policy: (
            SourceAccessPolicy | None
        ) = None,
        *,
        getaddrinfo: (
            GetAddrInfo | None
        ) = None,
    ):
        self.policy = (
            policy
            if policy is not None
            else SourceAccessPolicy()
        )

        if not isinstance(
            self.policy,
            SourceAccessPolicy,
        ):
            raise TypeError(
                "policy must be a "
                "SourceAccessPolicy."
            )

        self._getaddrinfo = (
            getaddrinfo
            if getaddrinfo is not None
            else socket.getaddrinfo
        )

        if not callable(
            self._getaddrinfo
        ):
            raise TypeError(
                "getaddrinfo must be "
                "callable."
            )

    @staticmethod
    def _identity(
        target: SourceAccessTarget,
    ) -> tuple[Any, ...]:
        return (
            target.request_url,
            target.scheme,
            target.hostname,
            target.port,
            target.literal_ip,
        )

    def _revalidate_target(
        self,
        target: SourceAccessTarget,
    ) -> SourceAccessTarget:
        if not isinstance(
            target,
            SourceAccessTarget,
        ):
            raise TypeError(
                "target must be a "
                "SourceAccessTarget."
            )

        canonical = (
            self.policy.prepare_url(
                target.request_url
            )
        )

        if (
            self._identity(canonical)
            != self._identity(target)
        ):
            raise SourceResolutionError(
                "SourceAccessTarget does not "
                "match canonical policy output."
            )

        return target

    @staticmethod
    def _endpoint(
        address: str,
        port: int,
    ) -> NumericSourceEndpoint:
        parsed = ip_address(address)

        family = (
            int(socket.AF_INET)
            if parsed.version == 4
            else int(socket.AF_INET6)
        )

        return NumericSourceEndpoint(
            family=family,
            address=parsed.compressed,
            port=port,
        )

    @staticmethod
    def _extract_address(
        record: tuple[Any, ...],
        *,
        port: int,
    ) -> str:
        if (
            not isinstance(
                record,
                tuple,
            )
            or len(record) != 5
        ):
            raise SourceResolutionError(
                "Malformed getaddrinfo record."
            )

        (
            family,
            socktype,
            protocol,
            _canonname,
            sockaddr,
        ) = record

        if family not in (
            socket.AF_INET,
            socket.AF_INET6,
        ):
            raise SourceResolutionError(
                "Resolver returned an "
                "unsupported address family."
            )

        if (
            socktype
            != socket.SOCK_STREAM
        ):
            raise SourceResolutionError(
                "Resolver returned a "
                "non-stream endpoint."
            )

        if protocol not in (
            0,
            socket.IPPROTO_TCP,
        ):
            raise SourceResolutionError(
                "Resolver returned a "
                "non-TCP endpoint."
            )

        if not isinstance(
            sockaddr,
            tuple,
        ):
            raise SourceResolutionError(
                "Resolver sockaddr "
                "must be a tuple."
            )

        if family == socket.AF_INET:
            if len(sockaddr) != 2:
                raise SourceResolutionError(
                    "Malformed IPv4 sockaddr."
                )

            address, resolved_port = (
                sockaddr
            )

        else:
            if len(sockaddr) != 4:
                raise SourceResolutionError(
                    "Malformed IPv6 sockaddr."
                )

            (
                address,
                resolved_port,
                flowinfo,
                scopeid,
            ) = sockaddr

            if (
                flowinfo != 0
                or scopeid != 0
            ):
                raise SourceResolutionError(
                    "Scoped or flow-qualified "
                    "IPv6 endpoints are "
                    "forbidden."
                )

        if (
            isinstance(
                resolved_port,
                bool,
            )
            or resolved_port != port
        ):
            raise SourceResolutionError(
                "Resolver port mismatch."
            )

        if not isinstance(
            address,
            str,
        ):
            raise SourceResolutionError(
                "Resolver address must "
                "be a string."
            )

        try:
            parsed = ip_address(
                address
            )
        except ValueError as exc:
            raise SourceResolutionError(
                "Resolver returned an "
                "invalid numeric address."
            ) from exc

        expected_version = (
            4
            if family == socket.AF_INET
            else 6
        )

        if (
            parsed.version
            != expected_version
        ):
            raise SourceResolutionError(
                "Resolver family/address "
                "mismatch."
            )

        return parsed.compressed

    def resolve_url(
        self,
        url: str,
    ) -> SourceResolution:
        return self.resolve_target(
            self.policy.prepare_url(url)
        )

    def resolve_target(
        self,
        target: SourceAccessTarget,
    ) -> SourceResolution:
        target = self._revalidate_target(
            target
        )

        if target.literal_ip is not None:
            resolved = (
                self.policy
                .validate_resolution(
                    target,
                    (),
                )
            )

            endpoints = tuple(
                self._endpoint(
                    address,
                    target.port,
                )
                for address
                in resolved.addresses
            )

            return SourceResolution(
                target=target,
                query_host=None,
                resolved=resolved,
                endpoints=endpoints,
            )

        query_host = (
            target.hostname + "."
        )

        addresses: list[str] = []

        max_records = (
            self.policy
            .max_resolved_addresses
            * 4
        )

        try:
            records = self._getaddrinfo(
                query_host,
                target.port,
                socket.AF_UNSPEC,
                socket.SOCK_STREAM,
                socket.IPPROTO_TCP,
                0,
            )

            if isinstance(
                records,
                (str, bytes),
            ):
                raise SourceResolutionError(
                    "Resolver returned an "
                    "invalid collection."
                )

            for index, record in enumerate(
                records,
                start=1,
            ):
                if index > max_records:
                    raise SourceResolutionError(
                        "Resolver returned too "
                        "many raw records."
                    )

                address = (
                    self._extract_address(
                        record,
                        port=target.port,
                    )
                )

                if address not in addresses:
                    addresses.append(address)

        except SourceResolutionError:
            raise
        except Exception as exc:
            raise SourceResolutionError(
                "DNS resolution failed."
            ) from exc

        resolved = (
            self.policy
            .validate_resolution(
                target,
                addresses,
            )
        )

        endpoints = tuple(
            self._endpoint(
                address,
                target.port,
            )
            for address
            in resolved.addresses
        )

        return SourceResolution(
            target=target,
            query_host=query_host,
            resolved=resolved,
            endpoints=endpoints,
        )


__all__ = [
    "GovernedSourceResolver",
    "NumericSourceEndpoint",
    "SourceResolution",
    "SourceResolutionError",
]
