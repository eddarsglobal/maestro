from __future__ import annotations

import math
import re
from collections.abc import Iterable
from dataclasses import dataclass
from ipaddress import IPv6Address, ip_address
from urllib.parse import (
    urljoin,
    urlsplit,
    urlunsplit,
)


SOURCE_ACCESS_POLICY_VERSION = "RX0.3A"

_DEFAULT_PORTS = {
    "http": 80,
    "https": 443,
}

_HOST_LABEL_RE = re.compile(
    r"^[a-z0-9-]+$"
)

_HARD_MAX_URL_CHARS = 16_384
_HARD_MAX_REDIRECTS = 10
_HARD_MAX_RESPONSE_BYTES = (
    64 * 1024 * 1024
)
_HARD_MAX_RESOLVED_ADDRESSES = 32
_HARD_MAX_TIMEOUT_SECONDS = 60.0


class SourceAccessViolation(ValueError):
    """
    An external source destination failed
    MAESTRO's public-source access policy.
    """


def _bounded_positive_int(
    value: int,
    name: str,
    *,
    maximum: int,
) -> int:
    if (
        isinstance(value, bool)
        or not isinstance(value, int)
    ):
        raise TypeError(
            f"{name} must be an integer."
        )

    if value < 1 or value > maximum:
        raise ValueError(
            f"{name} must be between "
            f"1 and {maximum}."
        )

    return value


def _bounded_positive_float(
    value: float,
    name: str,
    *,
    maximum: float,
) -> float:
    if isinstance(value, bool):
        raise TypeError(
            f"{name} must be numeric."
        )

    try:
        normalized = float(value)
    except (TypeError, ValueError) as exc:
        raise TypeError(
            f"{name} must be numeric."
        ) from exc

    if (
        not math.isfinite(normalized)
        or normalized <= 0.0
        or normalized > maximum
    ):
        raise ValueError(
            f"{name} must be > 0 and "
            f"<= {maximum}."
        )

    return normalized


def _require_url_text(
    value: str,
    *,
    name: str,
    maximum: int,
) -> str:
    if not isinstance(value, str):
        raise TypeError(
            f"{name} must be a string."
        )

    if not value:
        raise SourceAccessViolation(
            f"{name} must not be empty."
        )

    if len(value) > maximum:
        raise SourceAccessViolation(
            f"{name} exceeds maximum length."
        )

    if any(
        ord(character) <= 0x20
        or ord(character) == 0x7F
        for character in value
    ):
        raise SourceAccessViolation(
            f"{name} contains raw control "
            "or whitespace characters."
        )

    if "\\" in value:
        raise SourceAccessViolation(
            f"{name} must not contain "
            "backslashes."
        )

    return value


def _canonical_public_ip(
    value: str,
) -> str:
    if not isinstance(value, str):
        raise TypeError(
            "IP address must be a string."
        )

    if (
        not value
        or value != value.strip()
        or "%"
        in value
    ):
        raise SourceAccessViolation(
            "IP address representation "
            "is not allowed."
        )

    try:
        address = ip_address(value)
    except ValueError as exc:
        raise SourceAccessViolation(
            "Invalid IP address."
        ) from exc

    classification = address

    if isinstance(
        address,
        IPv6Address,
    ):
        if (
            address.ipv4_mapped
            is not None
            or address.sixtofour
            is not None
            or address.teredo
            is not None
        ):
            raise SourceAccessViolation(
                "IPv6 transition-address "
                "representations are forbidden."
            )

    blocked = (
        classification.is_unspecified
        or classification.is_loopback
        or classification.is_link_local
        or classification.is_multicast
        or classification.is_private
        or classification.is_reserved
        or getattr(
            classification,
            "is_site_local",
            False,
        )
        or not classification.is_global
    )

    if blocked:
        raise SourceAccessViolation(
            "External source IP must be "
            "public globally routable "
            "unicast."
        )

    return address.compressed


def _canonical_hostname(
    value: str,
) -> str:
    host = value.rstrip(".").casefold()

    if not host:
        raise SourceAccessViolation(
            "External source hostname "
            "must not be empty."
        )

    if (
        "%"
        in host
        or "\\"
        in host
    ):
        raise SourceAccessViolation(
            "External source hostname "
            "contains a forbidden "
            "representation."
        )

    try:
        ascii_host = (
            host.encode("idna")
            .decode("ascii")
            .lower()
        )
    except UnicodeError as exc:
        raise SourceAccessViolation(
            "External source hostname "
            "cannot be IDNA-normalized."
        ) from exc

    if len(ascii_host) > 253:
        raise SourceAccessViolation(
            "External source hostname "
            "is too long."
        )

    if (
        ascii_host == "localhost"
        or ascii_host.endswith(
            ".localhost"
        )
        or ascii_host.endswith(
            ".local"
        )
    ):
        raise SourceAccessViolation(
            "Local hostnames are forbidden "
            "for external source access."
        )

    # Single-label names may resolve through
    # local search domains and therefore are
    # not valid public-source destinations.
    if "." not in ascii_host:
        raise SourceAccessViolation(
            "External source hostname "
            "must be fully qualified."
        )

    labels = ascii_host.split(".")

    for label in labels:
        if (
            not label
            or len(label) > 63
            or not _HOST_LABEL_RE.fullmatch(
                label
            )
            or label.startswith("-")
            or label.endswith("-")
        ):
            raise SourceAccessViolation(
                "External source hostname "
                "contains an invalid label."
            )

    # Prevent alternative numeric IPv4 forms
    # such as 0177.0.0.1 from falling through
    # to platform resolver interpretation.
    if all(
        character.isdigit()
        or character == "."
        for character in ascii_host
    ):
        raise SourceAccessViolation(
            "Ambiguous numeric hostnames "
            "are forbidden."
        )

    return ascii_host


@dataclass(
    frozen=True,
    slots=True,
)
class SourceAccessTarget:
    original_url: str
    request_url: str
    scheme: str
    hostname: str
    port: int
    literal_ip: str | None = None


@dataclass(
    frozen=True,
    slots=True,
)
class ResolvedSourceTarget:
    target: SourceAccessTarget
    addresses: tuple[str, ...]


@dataclass(
    frozen=True,
    slots=True,
)
class SourceAccessPolicy:
    """
    Pure fail-closed policy for public external
    research destinations.

    RX0.3A performs NO DNS lookup and NO network
    access. Resolution results must be supplied
    by a later governed transport and validated
    here before use.
    """

    max_url_chars: int = 4096
    max_redirects: int = 5
    max_response_bytes: int = (
        8 * 1024 * 1024
    )
    max_resolved_addresses: int = 16
    timeout_seconds: float = 10.0

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "max_url_chars",
            _bounded_positive_int(
                self.max_url_chars,
                "max_url_chars",
                maximum=(
                    _HARD_MAX_URL_CHARS
                ),
            ),
        )

        object.__setattr__(
            self,
            "max_redirects",
            _bounded_positive_int(
                self.max_redirects,
                "max_redirects",
                maximum=(
                    _HARD_MAX_REDIRECTS
                ),
            ),
        )

        object.__setattr__(
            self,
            "max_response_bytes",
            _bounded_positive_int(
                self.max_response_bytes,
                "max_response_bytes",
                maximum=(
                    _HARD_MAX_RESPONSE_BYTES
                ),
            ),
        )

        object.__setattr__(
            self,
            "max_resolved_addresses",
            _bounded_positive_int(
                self.max_resolved_addresses,
                "max_resolved_addresses",
                maximum=(
                    _HARD_MAX_RESOLVED_ADDRESSES
                ),
            ),
        )

        object.__setattr__(
            self,
            "timeout_seconds",
            _bounded_positive_float(
                self.timeout_seconds,
                "timeout_seconds",
                maximum=(
                    _HARD_MAX_TIMEOUT_SECONDS
                ),
            ),
        )

    def prepare_url(
        self,
        url: str,
    ) -> SourceAccessTarget:
        raw = _require_url_text(
            url,
            name="source URL",
            maximum=self.max_url_chars,
        )

        try:
            parsed = urlsplit(raw)
        except ValueError as exc:
            raise SourceAccessViolation(
                "External source URL "
                "cannot be parsed."
            ) from exc

        scheme = parsed.scheme.lower()

        if scheme not in _DEFAULT_PORTS:
            raise SourceAccessViolation(
                "External source URL must "
                "use http or https."
            )

        if (
            not parsed.netloc
            or parsed.hostname is None
        ):
            raise SourceAccessViolation(
                "External source URL "
                "requires a network host."
            )

        if (
            parsed.username is not None
            or parsed.password is not None
            or "@"
            in parsed.netloc
        ):
            raise SourceAccessViolation(
                "External source URL "
                "must not contain userinfo "
                "or credentials."
            )

        try:
            explicit_port = parsed.port
        except ValueError as exc:
            raise SourceAccessViolation(
                "External source URL "
                "contains an invalid port."
            ) from exc

        expected_port = (
            _DEFAULT_PORTS[scheme]
        )

        if (
            explicit_port is not None
            and explicit_port
            != expected_port
        ):
            raise SourceAccessViolation(
                "External source URL "
                "uses a non-approved port."
            )

        raw_host = parsed.hostname

        if "%" in raw_host:
            raise SourceAccessViolation(
                "Scoped or escaped host "
                "representations are forbidden."
            )

        literal_ip = None

        try:
            ip_address(raw_host)
        except ValueError:
            hostname = (
                _canonical_hostname(
                    raw_host
                )
            )
        else:
            literal_ip = (
                _canonical_public_ip(
                    raw_host
                )
            )
            hostname = literal_ip

        if ":" in hostname:
            authority = (
                f"[{hostname}]"
            )
        else:
            authority = hostname

        path = parsed.path or "/"

        request_url = urlunsplit(
            (
                scheme,
                authority,
                path,
                parsed.query,
                "",
            )
        )

        if (
            len(request_url)
            > self.max_url_chars
        ):
            raise SourceAccessViolation(
                "Normalized external source "
                "URL exceeds maximum length."
            )

        return SourceAccessTarget(
            original_url=raw,
            request_url=request_url,
            scheme=scheme,
            hostname=hostname,
            port=expected_port,
            literal_ip=literal_ip,
        )

    def validate_resolution(
        self,
        target: SourceAccessTarget,
        addresses: Iterable[str],
    ) -> ResolvedSourceTarget:
        if not isinstance(
            target,
            SourceAccessTarget,
        ):
            raise TypeError(
                "target must be a "
                "SourceAccessTarget."
            )

        if isinstance(
            addresses,
            (str, bytes),
        ):
            raise TypeError(
                "addresses must be an "
                "iterable of IP strings."
            )

        supplied: list[str] = []

        for value in addresses:
            if (
                len(supplied)
                >= self.max_resolved_addresses
            ):
                raise SourceAccessViolation(
                    "DNS resolution returned too "
                    "many addresses."
                )

            supplied.append(value)

        if target.literal_ip is not None:
            if not supplied:
                supplied = (
                    target.literal_ip,
                )
        elif not supplied:
            raise SourceAccessViolation(
                "External hostname requires "
                "at least one resolved address."
            )

        canonical: list[str] = []

        for value in supplied:
            address = _canonical_public_ip(
                value
            )

            if (
                target.literal_ip
                is not None
                and address
                != target.literal_ip
            ):
                raise SourceAccessViolation(
                    "Literal-IP target cannot "
                    "be rebound to another "
                    "address."
                )

            if address not in canonical:
                canonical.append(
                    address
                )

        if not canonical:
            raise SourceAccessViolation(
                "No approved public address "
                "remains after validation."
            )

        return ResolvedSourceTarget(
            target=target,
            addresses=tuple(canonical),
        )

    def prepare_redirect(
        self,
        current: SourceAccessTarget,
        location: str,
    ) -> SourceAccessTarget:
        if not isinstance(
            current,
            SourceAccessTarget,
        ):
            raise TypeError(
                "current must be a "
                "SourceAccessTarget."
            )

        location = _require_url_text(
            location,
            name="redirect location",
            maximum=self.max_url_chars,
        )

        candidate = urljoin(
            current.request_url,
            location,
        )

        return self.prepare_url(
            candidate
        )


__all__ = [
    "SOURCE_ACCESS_POLICY_VERSION",
    "ResolvedSourceTarget",
    "SourceAccessPolicy",
    "SourceAccessTarget",
    "SourceAccessViolation",
]
