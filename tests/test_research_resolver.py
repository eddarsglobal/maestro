import socket
import unittest

from maestro.research.resolver import (
    GovernedSourceResolver,
    NumericSourceEndpoint,
    SourceResolutionError,
)
from maestro.research.source_access import (
    SourceAccessPolicy,
    SourceAccessTarget,
    SourceAccessViolation,
)


def ipv4(
    address,
    *,
    port=443,
    socktype=socket.SOCK_STREAM,
    protocol=socket.IPPROTO_TCP,
):
    return (
        socket.AF_INET,
        socktype,
        protocol,
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
    socktype=socket.SOCK_STREAM,
    protocol=socket.IPPROTO_TCP,
    flowinfo=0,
    scopeid=0,
):
    return (
        socket.AF_INET6,
        socktype,
        protocol,
        "",
        (
            address,
            port,
            flowinfo,
            scopeid,
        ),
    )


class FakeResolver:
    def __init__(
        self,
        rows=(),
        *,
        error=None,
    ):
        self.rows = rows
        self.error = error
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

        if self.error is not None:
            raise self.error

        return self.rows


class GovernedSourceResolverTests(
    unittest.TestCase
):
    def test_hostname_resolution_uses_absolute_fqdn_and_tcp_query(self):
        fake = FakeResolver(
            [
                ipv4("8.8.8.8"),
            ]
        )

        resolver = GovernedSourceResolver(
            getaddrinfo=fake
        )

        result = resolver.resolve_url(
            "https://example.com/a"
        )

        self.assertEqual(
            fake.calls,
            [
                (
                    "example.com.",
                    443,
                    socket.AF_UNSPEC,
                    socket.SOCK_STREAM,
                    socket.IPPROTO_TCP,
                    0,
                )
            ],
        )

        self.assertEqual(
            result.query_host,
            "example.com.",
        )

    def test_public_ipv4_and_ipv6_become_numeric_endpoints(self):
        fake = FakeResolver(
            [
                ipv4("8.8.8.8"),
                ipv6(
                    "2606:4700:4700::1111"
                ),
            ]
        )

        result = GovernedSourceResolver(
            getaddrinfo=fake
        ).resolve_url(
            "https://example.com/"
        )

        self.assertEqual(
            tuple(
                endpoint.address
                for endpoint
                in result.endpoints
            ),
            (
                "8.8.8.8",
                "2606:4700:4700::1111",
            ),
        )

        self.assertEqual(
            result.endpoints[0].sockaddr,
            ("8.8.8.8", 443),
        )

        self.assertEqual(
            result.endpoints[1].sockaddr,
            (
                "2606:4700:4700::1111",
                443,
                0,
                0,
            ),
        )

    def test_http_resolution_preserves_port_80(self):
        fake = FakeResolver(
            [
                ipv4(
                    "8.8.8.8",
                    port=80,
                ),
            ]
        )

        result = GovernedSourceResolver(
            getaddrinfo=fake
        ).resolve_url(
            "http://example.com/path"
        )

        self.assertEqual(
            fake.calls,
            [
                (
                    "example.com.",
                    80,
                    socket.AF_UNSPEC,
                    socket.SOCK_STREAM,
                    socket.IPPROTO_TCP,
                    0,
                )
            ],
        )

        self.assertEqual(
            result.target.port,
            80,
        )

        self.assertEqual(
            result.endpoints[0].sockaddr,
            ("8.8.8.8", 80),
        )

    def test_literal_ip_bypasses_resolver(self):
        fake = FakeResolver(
            error=AssertionError(
                "resolver must not run"
            )
        )

        result = GovernedSourceResolver(
            getaddrinfo=fake
        ).resolve_url(
            "https://8.8.8.8/"
        )

        self.assertEqual(
            fake.calls,
            [],
        )

        self.assertIsNone(
            result.query_host
        )

        self.assertEqual(
            result.endpoints[0].sockaddr,
            ("8.8.8.8", 443),
        )

    def test_duplicate_addresses_deduplicate_preserving_order(self):
        fake = FakeResolver(
            [
                ipv4("8.8.8.8"),
                ipv4("1.1.1.1"),
                ipv4("8.8.8.8"),
            ]
        )

        result = GovernedSourceResolver(
            getaddrinfo=fake
        ).resolve_url(
            "https://example.com/"
        )

        self.assertEqual(
            result.resolved.addresses,
            (
                "8.8.8.8",
                "1.1.1.1",
            ),
        )

    def test_mixed_public_private_resolution_fails_closed(self):
        fake = FakeResolver(
            [
                ipv4("8.8.8.8"),
                ipv4("127.0.0.1"),
            ]
        )

        with self.assertRaises(
            SourceAccessViolation
        ):
            GovernedSourceResolver(
                getaddrinfo=fake
            ).resolve_url(
                "https://example.com/"
            )

    def test_empty_resolution_fails_closed(self):
        with self.assertRaises(
            SourceAccessViolation
        ):
            GovernedSourceResolver(
                getaddrinfo=FakeResolver([])
            ).resolve_url(
                "https://example.com/"
            )

    def test_resolution_limit_is_enforced(self):
        policy = SourceAccessPolicy(
            max_resolved_addresses=2
        )

        fake = FakeResolver(
            [
                ipv4("8.8.8.8"),
                ipv4("1.1.1.1"),
                ipv4("9.9.9.9"),
            ]
        )

        with self.assertRaises(
            SourceAccessViolation
        ):
            GovernedSourceResolver(
                policy,
                getaddrinfo=fake,
            ).resolve_url(
                "https://example.com/"
            )

    def test_malformed_result_rejected(self):
        fake = FakeResolver(
            [
                (
                    socket.AF_INET,
                    socket.SOCK_STREAM,
                )
            ]
        )

        with self.assertRaises(
            SourceResolutionError
        ):
            GovernedSourceResolver(
                getaddrinfo=fake
            ).resolve_url(
                "https://example.com/"
            )

    def test_unexpected_family_rejected(self):
        fake = FakeResolver(
            [
                (
                    999,
                    socket.SOCK_STREAM,
                    socket.IPPROTO_TCP,
                    "",
                    ("8.8.8.8", 443),
                )
            ]
        )

        with self.assertRaises(
            SourceResolutionError
        ):
            GovernedSourceResolver(
                getaddrinfo=fake
            ).resolve_url(
                "https://example.com/"
            )

    def test_unexpected_socktype_rejected(self):
        fake = FakeResolver(
            [
                ipv4(
                    "8.8.8.8",
                    socktype=socket.SOCK_DGRAM,
                )
            ]
        )

        with self.assertRaises(
            SourceResolutionError
        ):
            GovernedSourceResolver(
                getaddrinfo=fake
            ).resolve_url(
                "https://example.com/"
            )

    def test_unexpected_protocol_rejected(self):
        fake = FakeResolver(
            [
                ipv4(
                    "8.8.8.8",
                    protocol=socket.IPPROTO_UDP,
                )
            ]
        )

        with self.assertRaises(
            SourceResolutionError
        ):
            GovernedSourceResolver(
                getaddrinfo=fake
            ).resolve_url(
                "https://example.com/"
            )

    def test_family_address_mismatch_rejected(self):
        fake = FakeResolver(
            [
                ipv4(
                    "2606:4700:4700::1111"
                )
            ]
        )

        with self.assertRaises(
            SourceResolutionError
        ):
            GovernedSourceResolver(
                getaddrinfo=fake
            ).resolve_url(
                "https://example.com/"
            )

    def test_resolver_port_mismatch_rejected(self):
        fake = FakeResolver(
            [
                ipv4(
                    "8.8.8.8",
                    port=444,
                )
            ]
        )

        with self.assertRaises(
            SourceResolutionError
        ):
            GovernedSourceResolver(
                getaddrinfo=fake
            ).resolve_url(
                "https://example.com/"
            )

    def test_ipv6_scope_or_flowinfo_rejected(self):
        for row in (
            ipv6(
                "2606:4700:4700::1111",
                flowinfo=1,
            ),
            ipv6(
                "2606:4700:4700::1111",
                scopeid=1,
            ),
        ):
            with self.subTest(row=row):
                with self.assertRaises(
                    SourceResolutionError
                ):
                    GovernedSourceResolver(
                        getaddrinfo=(
                            FakeResolver([row])
                        )
                    ).resolve_url(
                        "https://example.com/"
                    )

    def test_resolver_exception_wrapped_with_cause(self):
        failure = socket.gaierror(
            "synthetic DNS failure"
        )

        fake = FakeResolver(
            error=failure
        )

        with self.assertRaises(
            SourceResolutionError
        ) as caught:
            GovernedSourceResolver(
                getaddrinfo=fake
            ).resolve_url(
                "https://example.com/"
            )

        self.assertIs(
            caught.exception.__cause__,
            failure,
        )

    def test_tampered_target_is_revalidated(self):
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

        fake = FakeResolver(
            [
                ipv4("8.8.8.8"),
            ]
        )

        with self.assertRaises(
            SourceResolutionError
        ):
            GovernedSourceResolver(
                getaddrinfo=fake
            ).resolve_target(target)

        self.assertEqual(
            fake.calls,
            [],
        )

    def test_numeric_endpoint_sockaddr_is_deterministic(self):
        v4 = NumericSourceEndpoint(
            family=socket.AF_INET,
            address="8.8.8.8",
            port=80,
        )

        v6 = NumericSourceEndpoint(
            family=socket.AF_INET6,
            address=(
                "2606:4700:4700::1111"
            ),
            port=443,
        )

        self.assertEqual(
            v4.sockaddr,
            ("8.8.8.8", 80),
        )

        self.assertEqual(
            v6.sockaddr,
            (
                "2606:4700:4700::1111",
                443,
                0,
                0,
            ),
        )


if __name__ == "__main__":
    unittest.main()
