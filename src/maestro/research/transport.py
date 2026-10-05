from __future__ import annotations

import hashlib
import http.client
import socket
import ssl
import time
from dataclasses import dataclass
from ipaddress import ip_address
from typing import Any, Callable
from urllib.parse import urlsplit

from .connector import (
    BoundSourceConnection,
    BoundSourceConnector,
)
from .source_access import (
    SourceAccessTarget,
)


SOURCE_HTTP_TRANSPORT_VERSION = "RX0.3B2B1"

_READ_CHUNK_SIZE = 64 * 1024

_REDIRECT_STATUSES = frozenset(
    {
        int(http.client.MOVED_PERMANENTLY),
        int(http.client.FOUND),
        int(http.client.SEE_OTHER),
        int(http.client.TEMPORARY_REDIRECT),
        int(http.client.PERMANENT_REDIRECT),
    }
)


class SourceTransportError(
    RuntimeError
):
    pass


class SourceTransportInvariantError(
    SourceTransportError
):
    pass


class SourceTransportTimeout(
    SourceTransportError
):
    pass


class SourceTLSVerificationError(
    SourceTransportError
):
    pass


class SourceHTTPProtocolError(
    SourceTransportError
):
    pass


class SourceResponsePolicyError(
    SourceTransportError
):
    pass


class SourceResponseTooLargeError(
    SourceResponsePolicyError
):
    pass


class SourceRedirectRequired(
    SourceTransportError
):
    """
    A safe redirect was observed and validated.

    RX0.3B2B1 never follows it. RX0.3B2B2
    will govern the next hop separately.
    """

    def __init__(
        self,
        *,
        status: int,
        target: SourceAccessTarget,
    ):
        super().__init__(
            "HTTP redirect requires a new "
            "governed transport hop."
        )

        self.status = status
        self.target = target


@dataclass(
    frozen=True,
    slots=True,
)
class SourceHTTPResponse:
    target: SourceAccessTarget
    method: str
    status: int
    content_type: str | None
    body: bytes
    body_sha256: str

    @property
    def body_size(self) -> int:
        return len(self.body)


def _secure_tls_context() -> ssl.SSLContext:
    """
    Create an RX-owned client TLS context.

    Deliberately avoid ssl.create_default_context():
    CPython may honor SSLKEYLOGFILE there.

    No TLS key logging is permitted.
    """

    context = ssl.SSLContext(
        ssl.PROTOCOL_TLS_CLIENT
    )

    context.minimum_version = (
        ssl.TLSVersion.TLSv1_2
    )

    context.verify_mode = (
        ssl.CERT_REQUIRED
    )

    context.check_hostname = True

    context.load_default_certs(
        ssl.Purpose.SERVER_AUTH
    )

    context.set_alpn_protocols(
        [
            "http/1.1",
        ]
    )

    if hasattr(
        ssl,
        "OP_NO_COMPRESSION",
    ):
        context.options |= (
            ssl.OP_NO_COMPRESSION
        )

    if hasattr(
        context,
        "keylog_filename",
    ):
        context.keylog_filename = None

    return context


def _safe_close(
    resource: Any,
) -> None:
    if resource is None:
        return

    try:
        resource.close()
    except Exception:
        pass


class GovernedHTTPTransport:
    """
    Single-hop governed HTTP/HTTPS transport.

    Public entry:
        request(method, url)

    Security boundary:
      - DNS and TCP are delegated exclusively
        to BoundSourceConnector.
      - this class never creates or connects a
        socket itself;
      - HTTP receives an already-connected socket;
      - HTTPS wraps that exact socket with TLS;
      - hostname remains an identity object for
        Host/SNI/certificate verification only;
      - only GET and HEAD are supported;
      - redirects are validated but never followed
        in RX0.3B2B1;
      - response bodies are raw, not decompressed,
        and strictly bounded.

    timeout_seconds is the HTTP/TLS phase
    deadline beginning after the TCP connection has
    been returned by RX0.3B2A. Before blocking I/O,
    the socket timeout is reduced to the remaining
    deadline budget, and completion is checked again.

    This is not a portable hard-cancellation claim
    for work already executing inside CPython,
    OpenSSL, or buffered HTTP parsing.

    DNS remains subject to the explicit RX0.3B1
    blocking-resolver limitation.
    """

    def __init__(
        self,
        connector: (
            BoundSourceConnector | None
        ) = None,
        *,
        monotonic: (
            Callable[[], float] | None
        ) = None,
    ):
        self.connector = (
            connector
            if connector is not None
            else BoundSourceConnector()
        )

        if not isinstance(
            self.connector,
            BoundSourceConnector,
        ):
            raise TypeError(
                "connector must be a "
                "BoundSourceConnector."
            )

        self.policy = (
            self.connector.policy
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

    def _revalidate_bound(
        self,
        bound: BoundSourceConnection,
    ) -> SourceAccessTarget:
        if not isinstance(
            bound,
            BoundSourceConnection,
        ):
            raise TypeError(
                "bound must be a "
                "BoundSourceConnection."
            )

        target = bound.target

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
            raise SourceTransportInvariantError(
                "Bound target does not match "
                "canonical source policy."
            )

        endpoint = bound.endpoint

        if (
            endpoint.port
            != canonical.port
        ):
            raise SourceTransportInvariantError(
                "Bound endpoint port mismatch."
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
            raise SourceTransportInvariantError(
                "Bound endpoint family mismatch."
            )

        validated = (
            self.policy
            .validate_resolution(
                canonical,
                (
                    endpoint.address,
                ),
            )
        )

        if (
            validated.addresses
            != (
                endpoint.address,
            )
        ):
            raise SourceTransportInvariantError(
                "Bound endpoint failed final "
                "transport validation."
            )

        if bound.socket is None:
            raise SourceTransportInvariantError(
                "Bound connection has no socket."
            )

        return canonical

    def _remaining(
        self,
        deadline: float,
    ) -> float:
        remaining = (
            deadline
            - float(
                self._monotonic()
            )
        )

        if remaining <= 0.0:
            raise SourceTransportTimeout(
                "HTTP/TLS phase budget "
                "exhausted."
            )

        return remaining

    def _check_deadline(
        self,
        deadline: float,
    ) -> None:
        if (
            float(
                self._monotonic()
            )
            >= deadline
        ):
            raise SourceTransportTimeout(
                "HTTP/TLS operation completed "
                "after budget deadline."
            )

    def _apply_timeout(
        self,
        stream: Any,
        deadline: float,
    ) -> float:
        remaining = self._remaining(
            deadline
        )

        try:
            stream.settimeout(
                remaining
            )
        except OSError as exc:
            raise SourceTransportError(
                "Unable to apply transport "
                "socket timeout."
            ) from exc

        return remaining

    @staticmethod
    def _origin_form(
        target: SourceAccessTarget,
    ) -> str:
        split = urlsplit(
            target.request_url
        )

        path = split.path or "/"

        if split.query:
            path += "?" + split.query

        if not path.startswith("/"):
            raise SourceTransportInvariantError(
                "HTTP request target is not "
                "origin-form."
            )

        return path

    @staticmethod
    def _header_values(
        response: http.client.HTTPResponse,
        name: str,
    ) -> tuple[str, ...]:
        values = response.headers.get_all(
            name
        )

        if not values:
            return ()

        return tuple(values)

    def _validate_framing(
        self,
        response: http.client.HTTPResponse,
        *,
        method: str,
    ) -> int | None:
        content_lengths = (
            self._header_values(
                response,
                "Content-Length",
            )
        )

        transfer_encodings = (
            self._header_values(
                response,
                "Transfer-Encoding",
            )
        )

        if len(content_lengths) > 1:
            raise SourceHTTPProtocolError(
                "Multiple Content-Length "
                "headers are forbidden."
            )

        if len(transfer_encodings) > 1:
            raise SourceHTTPProtocolError(
                "Multiple Transfer-Encoding "
                "headers are forbidden."
            )

        if (
            content_lengths
            and transfer_encodings
        ):
            raise SourceHTTPProtocolError(
                "Transfer-Encoding combined "
                "with Content-Length is "
                "forbidden."
            )

        if transfer_encodings:
            value = (
                transfer_encodings[0]
                .strip()
                .lower()
            )

            if value != "chunked":
                raise SourceHTTPProtocolError(
                    "Unsupported "
                    "Transfer-Encoding."
                )

            if not response.chunked:
                raise SourceHTTPProtocolError(
                    "HTTP parser framing "
                    "disagrees with headers."
                )

        declared_length = None

        if content_lengths:
            value = (
                content_lengths[0]
                .strip()
            )

            if (
                not value
                or any(
                    character < "0"
                    or character > "9"
                    for character in value
                )
            ):
                raise SourceHTTPProtocolError(
                    "Invalid Content-Length."
                )

            if len(value) > 20:
                raise SourceResponseTooLargeError(
                    "Declared response body "
                    "exceeds supported range."
                )

            declared_length = int(
                value
            )

            if (
                method != "HEAD"
                and declared_length
                > self.policy
                .max_response_bytes
            ):
                raise SourceResponseTooLargeError(
                    "Declared response body "
                    "exceeds policy limit."
                )

        return declared_length

    def _validate_content_encoding(
        self,
        response: http.client.HTTPResponse,
    ) -> None:
        values = self._header_values(
            response,
            "Content-Encoding",
        )

        if len(values) > 1:
            raise SourceResponsePolicyError(
                "Multiple Content-Encoding "
                "headers are forbidden."
            )

        if not values:
            return

        if (
            values[0]
            .strip()
            .lower()
            != "identity"
        ):
            raise SourceResponsePolicyError(
                "Compressed HTTP response "
                "bodies are forbidden in "
                "RX0.3B2B1."
            )

    def _redirect_target(
        self,
        response: http.client.HTTPResponse,
        current: SourceAccessTarget,
    ) -> SourceAccessTarget:
        values = self._header_values(
            response,
            "Location",
        )

        if len(values) != 1:
            raise SourceHTTPProtocolError(
                "Redirect requires exactly "
                "one Location header."
            )

        location = values[0].strip()

        if not location:
            raise SourceHTTPProtocolError(
                "Redirect Location is empty."
            )

        return self.policy.prepare_redirect(
            current,
            location,
        )

    def _read_body(
        self,
        response: http.client.HTTPResponse,
        stream: Any,
        *,
        method: str,
        declared_length: int | None,
        deadline: float,
    ) -> bytes:
        if method == "HEAD":
            return b""

        maximum = (
            self.policy
            .max_response_bytes
        )

        chunks: list[bytes] = []
        total = 0

        while True:
            remaining_capacity = (
                maximum - total
            )

            amount = min(
                _READ_CHUNK_SIZE,
                remaining_capacity + 1,
            )

            self._apply_timeout(
                stream,
                deadline,
            )

            try:
                chunk = response.read(
                    amount
                )
            except http.client.IncompleteRead as exc:
                raise SourceHTTPProtocolError(
                    "Incomplete HTTP body."
                ) from exc
            except TimeoutError as exc:
                raise SourceTransportTimeout(
                    "HTTP body read timed out."
                ) from exc
            except OSError as exc:
                raise SourceTransportError(
                    "HTTP body read failed."
                ) from exc

            self._check_deadline(
                deadline
            )

            if not chunk:
                break

            total += len(chunk)

            if total > maximum:
                raise SourceResponseTooLargeError(
                    "Response body exceeds "
                    "policy limit."
                )

            chunks.append(chunk)

            if (
                declared_length is not None
                and total
                == declared_length
            ):
                break

        body = b"".join(chunks)

        if (
            declared_length is not None
            and len(body)
            != declared_length
        ):
            raise SourceHTTPProtocolError(
                "Response body length does not "
                "match Content-Length."
            )

        return body

    @staticmethod
    def _validate_tls_context(
        context: Any,
    ) -> None:
        if (
            getattr(
                context,
                "check_hostname",
                None,
            )
            is not True
        ):
            raise SourceTransportInvariantError(
                "TLS hostname verification "
                "must be enabled."
            )

        if (
            getattr(
                context,
                "verify_mode",
                None,
            )
            != ssl.CERT_REQUIRED
        ):
            raise SourceTransportInvariantError(
                "TLS certificate verification "
                "must be CERT_REQUIRED."
            )

        if (
            getattr(
                context,
                "keylog_filename",
                None,
            )
            is not None
        ):
            raise SourceTransportInvariantError(
                "TLS key logging is forbidden."
            )

    @staticmethod
    def _forbidden_reconnect(
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        raise SourceTransportInvariantError(
            "http.client attempted an "
            "unexpected reconnect."
        )

    def _request_bound(
        self,
        *,
        method: str,
        bound: BoundSourceConnection,
    ) -> SourceHTTPResponse:
        raw_stream = (
            bound.socket
            if isinstance(
                bound,
                BoundSourceConnection,
            )
            else None
        )

        stream = raw_stream
        connection = None
        response = None
        tls_context = None

        try:
            target = self._revalidate_bound(
                bound
            )

            deadline = (
                float(
                    self._monotonic()
                )
                + self.policy.timeout_seconds
            )

            if target.scheme == "https":
                tls_context = (
                    _secure_tls_context()
                )

                self._validate_tls_context(
                    tls_context
                )

                self._apply_timeout(
                    raw_stream,
                    deadline,
                )

                try:
                    stream = (
                        tls_context
                        .wrap_socket(
                            raw_stream,
                            server_hostname=(
                                target.hostname
                            ),
                        )
                    )
                except (
                    ssl.SSLCertVerificationError
                ) as exc:
                    raise (
                        SourceTLSVerificationError(
                            "TLS certificate "
                            "verification failed."
                        )
                    ) from exc
                except TimeoutError as exc:
                    raise SourceTransportTimeout(
                        "TLS handshake timed out."
                    ) from exc
                except (
                    ssl.SSLError,
                    OSError,
                ) as exc:
                    raise SourceTransportError(
                        "TLS handshake failed."
                    ) from exc

                self._check_deadline(
                    deadline
                )

                connection = (
                    http.client
                    .HTTPSConnection(
                        target.hostname,
                        target.port,
                        timeout=(
                            self._remaining(
                                deadline
                            )
                        ),
                        context=tls_context,
                    )
                )

            else:
                connection = (
                    http.client
                    .HTTPConnection(
                        target.hostname,
                        target.port,
                        timeout=(
                            self._remaining(
                                deadline
                            )
                        ),
                    )
                )

            # Critical invariant:
            # http.client receives a socket which
            # is already connected to the exact
            # numeric endpoint chosen by RX0.3B2A.
            #
            # It never receives authority to make
            # another TCP connection.
            connection.sock = stream

            connection._create_connection = (
                self._forbidden_reconnect
            )

            if connection._tunnel_host is not None:
                raise SourceTransportInvariantError(
                    "HTTP tunnelling/proxy mode "
                    "is forbidden."
                )

            origin = self._origin_form(
                target
            )

            connection.putrequest(
                method,
                origin,
                skip_accept_encoding=True,
            )

            connection.putheader(
                "Accept-Encoding",
                "identity",
            )

            connection.putheader(
                "User-Agent",
                "MAESTRO-RX/0.3B2B1",
            )

            connection.putheader(
                "Connection",
                "close",
            )

            self._apply_timeout(
                stream,
                deadline,
            )

            try:
                connection.endheaders()
            except TimeoutError as exc:
                raise SourceTransportTimeout(
                    "HTTP request send timed out."
                ) from exc
            except OSError as exc:
                raise SourceTransportError(
                    "HTTP request send failed."
                ) from exc
            except http.client.HTTPException as exc:
                raise SourceHTTPProtocolError(
                    "HTTP request framing failed."
                ) from exc

            self._check_deadline(
                deadline
            )

            self._apply_timeout(
                stream,
                deadline,
            )

            try:
                response = (
                    http.client.HTTPResponse(
                        stream,
                        method=method,
                    )
                )

                response.begin()

            except TimeoutError as exc:
                raise SourceTransportTimeout(
                    "HTTP response headers "
                    "timed out."
                ) from exc
            except OSError as exc:
                raise SourceTransportError(
                    "HTTP response headers "
                    "failed."
                ) from exc
            except http.client.HTTPException as exc:
                raise SourceHTTPProtocolError(
                    "Invalid HTTP response."
                ) from exc

            self._check_deadline(
                deadline
            )

            declared_length = (
                self._validate_framing(
                    response,
                    method=method,
                )
            )

            status = int(
                response.status
            )

            if 100 <= status < 200:
                raise SourceHTTPProtocolError(
                    "Final informational HTTP "
                    "responses are unsupported."
                )

            if status in _REDIRECT_STATUSES:
                redirect_target = (
                    self._redirect_target(
                        response,
                        target,
                    )
                )

                raise SourceRedirectRequired(
                    status=status,
                    target=redirect_target,
                )

            self._validate_content_encoding(
                response
            )

            body = self._read_body(
                response,
                stream,
                method=method,
                declared_length=(
                    declared_length
                ),
                deadline=deadline,
            )

            content_types = (
                self._header_values(
                    response,
                    "Content-Type",
                )
            )

            content_type = (
                content_types[0].strip()
                if len(content_types) == 1
                else None
            )

            return SourceHTTPResponse(
                target=target,
                method=method,
                status=status,
                content_type=content_type,
                body=body,
                body_sha256=(
                    hashlib.sha256(
                        body
                    ).hexdigest()
                ),
            )

        finally:
            _safe_close(response)
            _safe_close(connection)

            if connection is None:
                _safe_close(stream)

    def request(
        self,
        method: str,
        url: str,
    ) -> SourceHTTPResponse:
        if not isinstance(
            method,
            str,
        ):
            raise TypeError(
                "method must be a string."
            )

        normalized_method = (
            method.strip().upper()
        )

        if normalized_method not in (
            "GET",
            "HEAD",
        ):
            raise ValueError(
                "RX transport supports only "
                "GET and HEAD."
            )

        bound = (
            self.connector.connect_url(
                url
            )
        )

        return self._request_bound(
            method=normalized_method,
            bound=bound,
        )


__all__ = [
    "GovernedHTTPTransport",
    "SOURCE_HTTP_TRANSPORT_VERSION",
    "SourceHTTPProtocolError",
    "SourceHTTPResponse",
    "SourceRedirectRequired",
    "SourceResponsePolicyError",
    "SourceResponseTooLargeError",
    "SourceTLSVerificationError",
    "SourceTransportError",
    "SourceTransportInvariantError",
    "SourceTransportTimeout",
]
