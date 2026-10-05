import hashlib
import os
import socket
import ssl
import unittest
from io import BytesIO
from unittest.mock import patch

from maestro.research.connector import (
    BoundSourceConnector,
)
from maestro.research.resolver import (
    GovernedSourceResolver,
)
from maestro.research.source_access import (
    SourceAccessPolicy,
)
from maestro.research.transport import (
    GovernedHTTPTransport,
    SourceHTTPProtocolError,
    SourceRedirectRequired,
    SourceResponsePolicyError,
    SourceResponseTooLargeError,
    SourceTLSVerificationError,
    _secure_tls_context,
)


class ScriptedSocket:
    def __init__(
        self,
        response_bytes,
    ):
        self.response_bytes = (
            response_bytes
        )

        self.connected_to = None
        self.timeouts = []
        self.sent = []
        self.closed = False
        self.makefile_calls = 0

    def settimeout(
        self,
        value,
    ):
        self.timeouts.append(value)

    def connect(
        self,
        address,
    ):
        self.connected_to = address

    def sendall(
        self,
        data,
    ):
        self.sent.append(
            bytes(data)
        )

    def makefile(
        self,
        mode,
        buffering=None,
    ):
        self.makefile_calls += 1

        return BytesIO(
            self.response_bytes
        )

    def close(self):
        self.closed = True


class FakeTLSContext:
    def __init__(
        self,
        *,
        error=None,
    ):
        self.check_hostname = True
        self.verify_mode = (
            ssl.CERT_REQUIRED
        )
        self.keylog_filename = None
        self.minimum_version = (
            ssl.TLSVersion.TLSv1_2
        )

        self.error = error
        self.calls = []

    def wrap_socket(
        self,
        sock,
        *,
        server_hostname=None,
        **kwargs,
    ):
        self.calls.append(
            (
                sock,
                server_hostname,
            )
        )

        if self.error is not None:
            raise self.error

        return sock


def ipv4(
    address,
    *,
    port,
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


def make_transport(
    response_bytes,
    *,
    url="http://example.com/",
    policy=None,
):
    if policy is None:
        policy = SourceAccessPolicy()

    calls = []

    scheme_port = (
        443
        if url.startswith(
            "https://"
        )
        else 80
    )

    def dns(
        host,
        port,
        family,
        socktype,
        protocol,
        flags,
    ):
        calls.append(
            (
                host,
                port,
                family,
                socktype,
                protocol,
                flags,
            )
        )

        return [
            ipv4(
                "8.8.8.8",
                port=scheme_port,
            )
        ]

    scripted = ScriptedSocket(
        response_bytes
    )

    resolver = GovernedSourceResolver(
        policy=policy,
        getaddrinfo=dns,
    )

    connector = BoundSourceConnector(
        resolver,
        socket_factory=(
            lambda family,
            socktype,
            protocol: scripted
        ),
    )

    transport = GovernedHTTPTransport(
        connector
    )

    return (
        transport,
        scripted,
        calls,
    )


class GovernedHTTPTransportTests(
    unittest.TestCase
):
    def test_only_get_and_head_are_supported(self):
        for method in (
            "POST",
            "PUT",
            "DELETE",
            "PATCH",
        ):
            with self.subTest(
                method=method
            ):
                transport, _, _ = (
                    make_transport(
                        b"HTTP/1.1 200 OK\r\n"
                        b"Content-Length: 0\r\n"
                        b"\r\n"
                    )
                )

                with self.assertRaises(
                    ValueError
                ):
                    transport.request(
                        method,
                        "http://example.com/",
                    )

    def test_http_origin_form_host_and_identity_headers(self):
        transport, sock, _ = (
            make_transport(
                b"HTTP/1.1 200 OK\r\n"
                b"Content-Length: 2\r\n"
                b"Content-Type: text/plain\r\n"
                b"\r\n"
                b"OK",
                url=(
                    "http://example.com/"
                    "research?q=maestro"
                ),
            )
        )

        result = transport.request(
            "GET",
            "http://example.com/"
            "research?q=maestro",
        )

        request = b"".join(
            sock.sent
        )

        self.assertIn(
            b"GET /research?q=maestro "
            b"HTTP/1.1\r\n",
            request,
        )

        self.assertIn(
            b"Host: example.com\r\n",
            request,
        )

        self.assertIn(
            b"Accept-Encoding: identity\r\n",
            request,
        )

        self.assertEqual(
            request.count(
                b"Accept-Encoding: identity\r\n"
            ),
            1,
        )

        self.assertIn(
            b"Connection: close\r\n",
            request,
        )

        self.assertNotIn(
            b"http://example.com",
            request.split(
                b"\r\n",
                1,
            )[0],
        )

        self.assertEqual(
            result.body,
            b"OK",
        )

    def test_https_uses_hostname_for_sni_and_host(self):
        transport, sock, _ = (
            make_transport(
                b"HTTP/1.1 200 OK\r\n"
                b"Content-Length: 0\r\n"
                b"\r\n",
                url=(
                    "https://example.com/"
                ),
            )
        )

        context = FakeTLSContext()

        with patch(
            "maestro.research.transport."
            "_secure_tls_context",
            return_value=context,
        ):
            transport.request(
                "GET",
                "https://example.com/",
            )

        self.assertEqual(
            context.calls,
            [
                (
                    sock,
                    "example.com",
                )
            ],
        )

        request = b"".join(
            sock.sent
        )

        self.assertIn(
            b"Host: example.com\r\n",
            request,
        )

        self.assertNotIn(
            b"Host: example.com:443\r\n",
            request,
        )

    def test_ipv6_literal_host_header(self):
        response = (
            b"HTTP/1.1 200 OK\r\n"
            b"Content-Length: 0\r\n"
            b"\r\n"
        )

        scripted = ScriptedSocket(
            response
        )

        resolver = GovernedSourceResolver(
            getaddrinfo=lambda *args: (
                ()
            )
        )

        connector = BoundSourceConnector(
            resolver,
            socket_factory=(
                lambda *args: scripted
            ),
        )

        transport = GovernedHTTPTransport(
            connector
        )

        transport.request(
            "GET",
            "http://"
            "[2606:4700:4700::1111]/",
        )

        request = b"".join(
            scripted.sent
        )

        self.assertIn(
            b"Host: "
            b"[2606:4700:4700::1111]"
            b"\r\n",
            request,
        )

    def test_no_second_python_dns_lookup(self):
        transport, _, calls = (
            make_transport(
                b"HTTP/1.1 200 OK\r\n"
                b"Content-Length: 0\r\n"
                b"\r\n"
            )
        )

        with patch(
            "socket.getaddrinfo",
            side_effect=AssertionError(
                "unexpected second DNS"
            ),
        ):
            transport.request(
                "GET",
                "http://example.com/",
            )

        self.assertEqual(
            len(calls),
            1,
        )

    def test_secure_tls_context_ignores_sslkeylogfile(self):
        original = os.environ.get(
            "SSLKEYLOGFILE"
        )

        try:
            os.environ[
                "SSLKEYLOGFILE"
            ] = "/tmp/"
            "maestro-rx-keylog-forbidden"

            context = (
                _secure_tls_context()
            )

            self.assertTrue(
                context.check_hostname
            )

            self.assertEqual(
                context.verify_mode,
                ssl.CERT_REQUIRED,
            )

            self.assertIsNone(
                context.keylog_filename
            )

            self.assertGreaterEqual(
                context.minimum_version,
                ssl.TLSVersion.TLSv1_2,
            )

        finally:
            if original is None:
                os.environ.pop(
                    "SSLKEYLOGFILE",
                    None,
                )
            else:
                os.environ[
                    "SSLKEYLOGFILE"
                ] = original

    def test_duplicate_content_length_rejected(self):
        transport, _, _ = (
            make_transport(
                b"HTTP/1.1 200 OK\r\n"
                b"Content-Length: 2\r\n"
                b"Content-Length: 2\r\n"
                b"\r\n"
                b"OK"
            )
        )

        with self.assertRaises(
            SourceHTTPProtocolError
        ):
            transport.request(
                "GET",
                "http://example.com/",
            )

    def test_invalid_content_length_rejected(self):
        transport, _, _ = (
            make_transport(
                b"HTTP/1.1 200 OK\r\n"
                b"Content-Length: 2, 2\r\n"
                b"\r\n"
                b"OK"
            )
        )

        with self.assertRaises(
            SourceHTTPProtocolError
        ):
            transport.request(
                "GET",
                "http://example.com/",
            )

    def test_transfer_encoding_plus_content_length_rejected(self):
        transport, _, _ = (
            make_transport(
                b"HTTP/1.1 200 OK\r\n"
                b"Transfer-Encoding: chunked\r\n"
                b"Content-Length: 2\r\n"
                b"\r\n"
                b"0\r\n\r\n"
            )
        )

        with self.assertRaises(
            SourceHTTPProtocolError
        ):
            transport.request(
                "GET",
                "http://example.com/",
            )

    def test_unsupported_transfer_encoding_rejected(self):
        transport, _, _ = (
            make_transport(
                b"HTTP/1.1 200 OK\r\n"
                b"Transfer-Encoding: gzip\r\n"
                b"\r\n"
            )
        )

        with self.assertRaises(
            SourceHTTPProtocolError
        ):
            transport.request(
                "GET",
                "http://example.com/",
            )

    def test_chunked_body_is_accepted(self):
        transport, _, _ = (
            make_transport(
                b"HTTP/1.1 200 OK\r\n"
                b"Transfer-Encoding: chunked\r\n"
                b"\r\n"
                b"2\r\n"
                b"OK\r\n"
                b"0\r\n"
                b"\r\n"
            )
        )

        result = transport.request(
            "GET",
            "http://example.com/",
        )

        self.assertEqual(
            result.body,
            b"OK",
        )

    def test_compressed_content_is_rejected(self):
        transport, _, _ = (
            make_transport(
                b"HTTP/1.1 200 OK\r\n"
                b"Content-Length: 2\r\n"
                b"Content-Encoding: gzip\r\n"
                b"\r\n"
                b"OK"
            )
        )

        with self.assertRaises(
            SourceResponsePolicyError
        ):
            transport.request(
                "GET",
                "http://example.com/",
            )

    def test_identity_content_encoding_is_accepted(self):
        transport, _, _ = (
            make_transport(
                b"HTTP/1.1 200 OK\r\n"
                b"Content-Length: 2\r\n"
                b"Content-Encoding: identity\r\n"
                b"\r\n"
                b"OK"
            )
        )

        result = transport.request(
            "GET",
            "http://example.com/",
        )

        self.assertEqual(
            result.body,
            b"OK",
        )

    def test_known_oversized_body_rejected(self):
        policy = SourceAccessPolicy(
            max_response_bytes=2
        )

        transport, _, _ = (
            make_transport(
                b"HTTP/1.1 200 OK\r\n"
                b"Content-Length: 3\r\n"
                b"\r\n"
                b"ABC",
                policy=policy,
            )
        )

        with self.assertRaises(
            SourceResponseTooLargeError
        ):
            transport.request(
                "GET",
                "http://example.com/",
            )

    def test_exact_limit_close_delimited_body_accepted(self):
        policy = SourceAccessPolicy(
            max_response_bytes=4
        )

        transport, _, _ = (
            make_transport(
                b"HTTP/1.1 200 OK\r\n"
                b"Connection: close\r\n"
                b"\r\n"
                b"ABCD",
                policy=policy,
            )
        )

        result = transport.request(
            "GET",
            "http://example.com/",
        )

        self.assertEqual(
            result.body,
            b"ABCD",
        )

    def test_limit_plus_one_close_delimited_body_rejected(self):
        policy = SourceAccessPolicy(
            max_response_bytes=4
        )

        transport, _, _ = (
            make_transport(
                b"HTTP/1.1 200 OK\r\n"
                b"Connection: close\r\n"
                b"\r\n"
                b"ABCDE",
                policy=policy,
            )
        )

        with self.assertRaises(
            SourceResponseTooLargeError
        ):
            transport.request(
                "GET",
                "http://example.com/",
            )

    def test_truncated_content_length_rejected(self):
        transport, _, _ = (
            make_transport(
                b"HTTP/1.1 200 OK\r\n"
                b"Content-Length: 4\r\n"
                b"\r\n"
                b"AB"
            )
        )

        with self.assertRaises(
            SourceHTTPProtocolError
        ):
            transport.request(
                "GET",
                "http://example.com/",
            )

    def test_redirect_is_validated_but_not_followed(self):
        transport, _, calls = (
            make_transport(
                b"HTTP/1.1 302 Found\r\n"
                b"Location: "
                b"https://other.example/path\r\n"
                b"Content-Length: 0\r\n"
                b"\r\n"
            )
        )

        with self.assertRaises(
            SourceRedirectRequired
        ) as caught:
            transport.request(
                "GET",
                "http://example.com/",
            )

        self.assertEqual(
            len(calls),
            1,
        )

        self.assertEqual(
            caught.exception.status,
            302,
        )

        self.assertEqual(
            caught.exception
            .target.hostname,
            "other.example",
        )

    def test_duplicate_redirect_location_rejected(self):
        transport, _, _ = (
            make_transport(
                b"HTTP/1.1 302 Found\r\n"
                b"Location: "
                b"https://one.example/\r\n"
                b"Location: "
                b"https://two.example/\r\n"
                b"Content-Length: 0\r\n"
                b"\r\n"
            )
        )

        with self.assertRaises(
            SourceHTTPProtocolError
        ):
            transport.request(
                "GET",
                "http://example.com/",
            )

    def test_head_returns_empty_body(self):
        transport, _, _ = (
            make_transport(
                b"HTTP/1.1 200 OK\r\n"
                b"Content-Length: 999999\r\n"
                b"\r\n"
            )
        )

        result = transport.request(
            "HEAD",
            "http://example.com/",
        )

        self.assertEqual(
            result.body,
            b"",
        )

    def test_invalid_bound_connection_closes_owned_socket(self):
        policy = SourceAccessPolicy()

        scripted = ScriptedSocket(
            b""
        )

        resolver = GovernedSourceResolver(
            policy=policy,
            getaddrinfo=lambda *args: (),
        )

        connector = BoundSourceConnector(
            resolver,
            socket_factory=(
                lambda *args: scripted
            ),
        )

        transport = GovernedHTTPTransport(
            connector
        )

        from maestro.research.connector import (
            BoundSourceConnection,
        )
        from maestro.research.resolver import (
            NumericSourceEndpoint,
        )
        from maestro.research.source_access import (
            SourceAccessTarget,
        )
        from maestro.research.transport import (
            SourceTransportInvariantError,
        )

        tampered_target = SourceAccessTarget(
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

        forged = BoundSourceConnection(
            target=tampered_target,
            endpoint=(
                NumericSourceEndpoint(
                    family=socket.AF_INET,
                    address="8.8.8.8",
                    port=443,
                )
            ),
            socket=scripted,
        )

        with self.assertRaises(
            SourceTransportInvariantError
        ):
            transport._request_bound(
                method="GET",
                bound=forged,
            )

        self.assertTrue(
            scripted.closed
        )

    def test_final_101_switching_protocols_rejected(self):
        transport, sock, _ = (
            make_transport(
                b"HTTP/1.1 101 "
                b"Switching Protocols\r\n"
                b"Connection: Upgrade\r\n"
                b"Upgrade: websocket\r\n"
                b"\r\n"
            )
        )

        with self.assertRaises(
            SourceHTTPProtocolError
        ):
            transport.request(
                "GET",
                "http://example.com/",
            )

        self.assertTrue(
            sock.closed
        )

    def test_final_103_early_hints_rejected(self):
        transport, sock, _ = (
            make_transport(
                b"HTTP/1.1 103 Early Hints\r\n"
                b"Link: </x>; rel=preload\r\n"
                b"\r\n"
            )
        )

        with self.assertRaises(
            SourceHTTPProtocolError
        ):
            transport.request(
                "GET",
                "http://example.com/",
            )

        self.assertTrue(
            sock.closed
        )

    def test_tls_verification_failure_closes_socket(self):
        transport, sock, _ = (
            make_transport(
                b"",
                url=(
                    "https://example.com/"
                ),
            )
        )

        context = FakeTLSContext(
            error=(
                ssl.SSLCertVerificationError(
                    "synthetic cert failure"
                )
            )
        )

        with patch(
            "maestro.research.transport."
            "_secure_tls_context",
            return_value=context,
        ):
            with self.assertRaises(
                SourceTLSVerificationError
            ):
                transport.request(
                    "GET",
                    "https://example.com/",
                )

        self.assertTrue(
            sock.closed
        )

    def test_response_digest_matches_body(self):
        transport, _, _ = (
            make_transport(
                b"HTTP/1.1 200 OK\r\n"
                b"Content-Length: 5\r\n"
                b"\r\n"
                b"HELLO"
            )
        )

        result = transport.request(
            "GET",
            "http://example.com/",
        )

        self.assertEqual(
            result.body_size,
            5,
        )

        self.assertEqual(
            result.body_sha256,
            hashlib.sha256(
                b"HELLO"
            ).hexdigest(),
        )


if __name__ == "__main__":
    unittest.main()
