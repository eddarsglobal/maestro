import socket
import unittest
from unittest.mock import patch

from maestro.research.connector import (
    BoundSourceConnector,
    SourceConnectionError,
    SourceConnectionInvariantError,
)
from maestro.research.resolver import (
    GovernedSourceResolver,
    NumericSourceEndpoint,
    SourceResolution,
)
from maestro.research.source_access import (
    ResolvedSourceTarget,
    SourceAccessPolicy,
    SourceAccessTarget,
    SourceAccessViolation,
)


def ipv4(
    address,
    *,
    port=443,
):
    return (
        socket.AF_INET,
        socket.SOCK_STREAM,
        socket.IPPROTO_TCP,
        "",
        (
            address,
            port,
        ),
    )


def ipv6(
    address,
    *,
    port=443,
):
    return (
        socket.AF_INET6,
        socket.SOCK_STREAM,
        socket.IPPROTO_TCP,
        "",
        (
            address,
            port,
            0,
            0,
        ),
    )


class FakeResolverCall:
    def __init__(
        self,
        rows,
    ):
        self.rows = rows
        self.calls = []

    def __call__(
        self,
        host,
        port,
        family,
        socktype,
        protocol,
        flags,
    ):
        self.calls.append(
            (
                host,
                port,
                family,
                socktype,
                protocol,
                flags,
            )
        )

        return self.rows


class FakeSocket:
    def __init__(
        self,
        *,
        error=None,
    ):
        self.error = error
        self.timeouts = []
        self.connect_calls = []
        self.closed = False

    def settimeout(
        self,
        value,
    ):
        self.timeouts.append(value)

    def connect(
        self,
        address,
    ):
        self.connect_calls.append(
            address
        )

        if self.error is not None:
            raise self.error

    def close(self):
        self.closed = True


class FakeSocketFactory:
    def __init__(
        self,
        errors=(),
    ):
        self.errors = list(errors)
        self.calls = []
        self.sockets = []

    def __call__(
        self,
        family,
        socktype,
        protocol,
    ):
        index = len(
            self.sockets
        )

        error = (
            self.errors[index]
            if index
            < len(self.errors)
            else None
        )

        sock = FakeSocket(
            error=error
        )

        self.calls.append(
            (
                family,
                socktype,
                protocol,
            )
        )

        self.sockets.append(sock)

        return sock


class SequenceClock:
    def __init__(
        self,
        values,
    ):
        self.values = iter(values)

    def __call__(self):
        return next(self.values)


def connector_for(
    rows,
    factory,
    *,
    policy=None,
    monotonic=None,
):
    dns = FakeResolverCall(rows)

    resolver = GovernedSourceResolver(
        policy=policy,
        getaddrinfo=dns,
    )

    kwargs = {
        "socket_factory": factory,
    }

    if monotonic is not None:
        kwargs["monotonic"] = (
            monotonic
        )

    connector = BoundSourceConnector(
        resolver,
        **kwargs,
    )

    return connector, dns


class BoundSourceConnectorTests(
    unittest.TestCase
):
    def test_requires_governed_resolver(self):
        with self.assertRaises(
            TypeError
        ):
            BoundSourceConnector(
                object()
            )

    def test_requires_callable_socket_factory(self):
        resolver = GovernedSourceResolver(
            getaddrinfo=(
                FakeResolverCall(
                    [ipv4("8.8.8.8")]
                )
            )
        )

        with self.assertRaises(
            TypeError
        ):
            BoundSourceConnector(
                resolver,
                socket_factory=object(),
            )

    def test_requires_callable_monotonic(self):
        resolver = GovernedSourceResolver(
            getaddrinfo=(
                FakeResolverCall(
                    [ipv4("8.8.8.8")]
                )
            )
        )

        with self.assertRaises(
            TypeError
        ):
            BoundSourceConnector(
                resolver,
                socket_factory=(
                    FakeSocketFactory()
                ),
                monotonic=object(),
            )

    def test_ipv4_connects_exact_numeric_sockaddr(self):
        factory = FakeSocketFactory()

        connector, _dns = connector_for(
            [ipv4("8.8.8.8")],
            factory,
        )

        connection = (
            connector.connect_url(
                "https://example.com/"
            )
        )

        self.assertEqual(
            factory.calls,
            [
                (
                    int(socket.AF_INET),
                    int(socket.SOCK_STREAM),
                    int(socket.IPPROTO_TCP),
                )
            ],
        )

        self.assertEqual(
            factory.sockets[0]
            .connect_calls,
            [
                ("8.8.8.8", 443)
            ],
        )

        self.assertEqual(
            connection.endpoint.address,
            "8.8.8.8",
        )

    def test_ipv6_connects_exact_numeric_sockaddr(self):
        factory = FakeSocketFactory()

        connector, _dns = connector_for(
            [
                ipv6(
                    "2606:4700:4700::1111"
                )
            ],
            factory,
        )

        connection = (
            connector.connect_url(
                "https://example.com/"
            )
        )

        self.assertEqual(
            factory.sockets[0]
            .connect_calls,
            [
                (
                    "2606:4700:4700::1111",
                    443,
                    0,
                    0,
                )
            ],
        )

        self.assertEqual(
            connection.endpoint.family,
            int(socket.AF_INET6),
        )

    def test_literal_ip_bypasses_dns(self):
        def forbidden_dns(
            *args,
            **kwargs,
        ):
            raise AssertionError(
                "DNS must not run"
            )

        resolver = GovernedSourceResolver(
            getaddrinfo=forbidden_dns
        )

        factory = FakeSocketFactory()

        connection = BoundSourceConnector(
            resolver,
            socket_factory=factory,
        ).connect_url(
            "https://8.8.8.8/"
        )

        self.assertEqual(
            connection.endpoint.sockaddr,
            ("8.8.8.8", 443),
        )

    def test_hostname_uses_one_injected_dns_resolution(self):
        factory = FakeSocketFactory()

        connector, dns = connector_for(
            [ipv4("8.8.8.8")],
            factory,
        )

        connector.connect_url(
            "https://example.com/a"
        )

        self.assertEqual(
            len(dns.calls),
            1,
        )

        self.assertEqual(
            dns.calls[0][0],
            "example.com.",
        )

    def test_first_failure_closes_socket_and_falls_back_in_order(self):
        factory = FakeSocketFactory(
            errors=[
                OSError("first failed"),
                None,
            ]
        )

        connector, _dns = connector_for(
            [
                ipv4("8.8.8.8"),
                ipv4("1.1.1.1"),
            ],
            factory,
        )

        connection = (
            connector.connect_url(
                "https://example.com/"
            )
        )

        self.assertTrue(
            factory.sockets[0].closed
        )

        self.assertFalse(
            factory.sockets[1].closed
        )

        self.assertEqual(
            factory.sockets[0]
            .connect_calls,
            [
                ("8.8.8.8", 443)
            ],
        )

        self.assertEqual(
            factory.sockets[1]
            .connect_calls,
            [
                ("1.1.1.1", 443)
            ],
        )

        self.assertEqual(
            connection.endpoint.address,
            "1.1.1.1",
        )

    def test_successful_socket_remains_open(self):
        factory = FakeSocketFactory()

        connector, _dns = connector_for(
            [ipv4("8.8.8.8")],
            factory,
        )

        connection = (
            connector.connect_url(
                "https://example.com/"
            )
        )

        self.assertFalse(
            factory.sockets[0].closed
        )

        connection.close()

        self.assertTrue(
            factory.sockets[0].closed
        )

    def test_all_failures_raise_bounded_attempt_inventory(self):
        factory = FakeSocketFactory(
            errors=[
                OSError("one"),
                TimeoutError("two"),
            ]
        )

        connector, _dns = connector_for(
            [
                ipv4("8.8.8.8"),
                ipv4("1.1.1.1"),
            ],
            factory,
        )

        with self.assertRaises(
            SourceConnectionError
        ) as caught:
            connector.connect_url(
                "https://example.com/"
            )

        self.assertEqual(
            tuple(
                attempt.error_type
                for attempt
                in caught.exception.attempts
            ),
            (
                "OSError",
                "TimeoutError",
            ),
        )

        self.assertTrue(
            all(
                sock.closed
                for sock
                in factory.sockets
            )
        )

    def test_factory_failure_is_an_attempt_and_falls_back(self):
        sockets = []
        calls = []

        def factory(
            family,
            socktype,
            protocol,
        ):
            calls.append(
                (
                    family,
                    socktype,
                    protocol,
                )
            )

            if len(calls) == 1:
                raise OSError(
                    "factory failed"
                )

            sock = FakeSocket()
            sockets.append(sock)
            return sock

        connector, _dns = connector_for(
            [
                ipv4("8.8.8.8"),
                ipv4("1.1.1.1"),
            ],
            factory,
        )

        connection = (
            connector.connect_url(
                "https://example.com/"
            )
        )

        self.assertEqual(
            len(calls),
            2,
        )

        self.assertEqual(
            connection.endpoint.address,
            "1.1.1.1",
        )

    def test_programming_failure_does_not_trigger_fallback(self):
        calls = []

        def factory(
            family,
            socktype,
            protocol,
        ):
            calls.append(
                (
                    family,
                    socktype,
                    protocol,
                )
            )

            raise ValueError(
                "synthetic programming failure"
            )

        connector, _dns = connector_for(
            [
                ipv4("8.8.8.8"),
                ipv4("1.1.1.1"),
            ],
            factory,
        )

        with self.assertRaises(
            ValueError
        ):
            connector.connect_url(
                "https://example.com/"
            )

        self.assertEqual(
            len(calls),
            1,
        )

    def test_success_after_total_deadline_is_rejected_and_closed(self):
        policy = SourceAccessPolicy(
            timeout_seconds=10.0
        )

        factory = FakeSocketFactory()

        clock = SequenceClock(
            [
                100.0,
                101.0,
                111.0,
            ]
        )

        connector, _dns = connector_for(
            [
                ipv4("8.8.8.8"),
                ipv4("1.1.1.1"),
            ],
            factory,
            policy=policy,
            monotonic=clock,
        )

        with self.assertRaises(
            SourceConnectionError
        ) as caught:
            connector.connect_url(
                "https://example.com/"
            )

        self.assertIn(
            "budget exhausted",
            str(
                caught.exception
            ).lower(),
        )

        self.assertEqual(
            len(factory.sockets),
            1,
        )

        self.assertTrue(
            factory.sockets[0].closed
        )

        self.assertEqual(
            tuple(
                attempt.error_type
                for attempt
                in caught.exception.attempts
            ),
            (
                "TimeoutError",
            ),
        )

    def test_total_connect_budget_stops_later_attempt(self):
        policy = SourceAccessPolicy(
            timeout_seconds=10.0
        )

        factory = FakeSocketFactory(
            errors=[
                OSError("first failed"),
            ]
        )

        clock = SequenceClock(
            [
                100.0,
                100.1,
                111.0,
            ]
        )

        connector, _dns = connector_for(
            [
                ipv4("8.8.8.8"),
                ipv4("1.1.1.1"),
            ],
            factory,
            policy=policy,
            monotonic=clock,
        )

        with self.assertRaises(
            SourceConnectionError
        ) as caught:
            connector.connect_url(
                "https://example.com/"
            )

        self.assertIn(
            "budget exhausted",
            str(
                caught.exception
            ).lower(),
        )

        self.assertEqual(
            len(factory.sockets),
            1,
        )

    def test_private_forged_resolution_rejected_before_socket(self):
        policy = SourceAccessPolicy()

        target = policy.prepare_url(
            "https://example.com/"
        )

        forged = SourceResolution(
            target=target,
            query_host="example.com.",
            resolved=(
                ResolvedSourceTarget(
                    target=target,
                    addresses=(
                        "127.0.0.1",
                    ),
                )
            ),
            endpoints=(
                NumericSourceEndpoint(
                    family=socket.AF_INET,
                    address="127.0.0.1",
                    port=443,
                ),
            ),
        )

        factory = FakeSocketFactory()

        resolver = GovernedSourceResolver(
            policy=policy,
            getaddrinfo=(
                FakeResolverCall(
                    [ipv4("8.8.8.8")]
                )
            ),
        )

        connector = BoundSourceConnector(
            resolver,
            socket_factory=factory,
        )

        with self.assertRaises(
            SourceAccessViolation
        ):
            connector._connect_resolution(
                forged
            )

        self.assertEqual(
            factory.calls,
            [],
        )

    def test_tampered_target_rejected_before_socket(self):
        policy = SourceAccessPolicy()

        target = SourceAccessTarget(
            original_url=(
                "https://example.com/"
            ),
            request_url=(
                "https://example.com/"
            ),
            scheme="https",
            hostname="127.0.0.1",
            port=443,
        )

        forged = SourceResolution(
            target=target,
            query_host=(
                "127.0.0.1."
            ),
            resolved=(
                ResolvedSourceTarget(
                    target=target,
                    addresses=(
                        "8.8.8.8",
                    ),
                )
            ),
            endpoints=(
                NumericSourceEndpoint(
                    family=socket.AF_INET,
                    address="8.8.8.8",
                    port=443,
                ),
            ),
        )

        factory = FakeSocketFactory()

        resolver = GovernedSourceResolver(
            policy=policy,
            getaddrinfo=(
                FakeResolverCall(
                    [ipv4("8.8.8.8")]
                )
            ),
        )

        connector = BoundSourceConnector(
            resolver,
            socket_factory=factory,
        )

        with self.assertRaises(
            SourceConnectionInvariantError
        ):
            connector._connect_resolution(
                forged
            )

        self.assertEqual(
            factory.calls,
            [],
        )

    def test_socket_timeout_uses_remaining_budget(self):
        policy = SourceAccessPolicy(
            timeout_seconds=10.0
        )

        factory = FakeSocketFactory()

        clock = SequenceClock(
            [
                100.0,
                102.0,
                102.1,
            ]
        )

        connector, _dns = connector_for(
            [ipv4("8.8.8.8")],
            factory,
            policy=policy,
            monotonic=clock,
        )

        connector.connect_url(
            "https://example.com/"
        )

        self.assertEqual(
            factory.sockets[0]
            .timeouts,
            [8.0],
        )

    def test_no_second_python_getaddrinfo_lookup(self):
        factory = FakeSocketFactory()

        connector, dns = connector_for(
            [ipv4("8.8.8.8")],
            factory,
        )

        with patch(
            "socket.getaddrinfo",
            side_effect=AssertionError(
                "unexpected second DNS"
            ),
        ):
            connection = (
                connector.connect_url(
                    "https://example.com/"
                )
            )

        self.assertEqual(
            len(dns.calls),
            1,
        )

        self.assertEqual(
            connection.endpoint.address,
            "8.8.8.8",
        )

    def test_http_port_80_reaches_numeric_connect(self):
        factory = FakeSocketFactory()

        connector, dns = connector_for(
            [
                ipv4(
                    "8.8.8.8",
                    port=80,
                )
            ],
            factory,
        )

        connection = (
            connector.connect_url(
                "http://example.com/a"
            )
        )

        self.assertEqual(
            dns.calls[0][1],
            80,
        )

        self.assertEqual(
            connection.endpoint.sockaddr,
            ("8.8.8.8", 80),
        )

        self.assertEqual(
            factory.sockets[0]
            .connect_calls,
            [
                ("8.8.8.8", 80)
            ],
        )


if __name__ == "__main__":
    unittest.main()
