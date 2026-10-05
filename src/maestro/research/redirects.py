from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .source_access import (
    SourceAccessTarget,
)
from .transport import (
    GovernedHTTPTransport,
    SourceHTTPResponse,
    SourceRedirectRequired,
)


GOVERNED_REDIRECT_VERSION = "RX0.3B2B2"

_REDIRECT_STATUSES = frozenset(
    {
        301,
        302,
        303,
        307,
        308,
    }
)


@dataclass(
    frozen=True,
    slots=True,
)
class SourceRedirectHop:
    """
    Canonical provenance record for one
    governed HTTP redirect.

    No raw Location header is retained here.
    B2B1 already interpreted and validated it
    into a SourceAccessTarget.
    """

    status: int
    source_url: str
    target_url: str

    def __post_init__(
        self,
    ) -> None:
        if self.status not in (
            _REDIRECT_STATUSES
        ):
            raise ValueError(
                "Unsupported redirect status."
            )

        if (
            not isinstance(
                self.source_url,
                str,
            )
            or not self.source_url
        ):
            raise ValueError(
                "source_url must be "
                "non-empty."
            )

        if (
            not isinstance(
                self.target_url,
                str,
            )
            or not self.target_url
        ):
            raise ValueError(
                "target_url must be "
                "non-empty."
            )


@dataclass(
    frozen=True,
    slots=True,
)
class GovernedRedirectResponse:
    response: SourceHTTPResponse
    redirects: tuple[
        SourceRedirectHop,
        ...,
    ]

    def __post_init__(
        self,
    ) -> None:
        if not isinstance(
            self.response,
            SourceHTTPResponse,
        ):
            raise TypeError(
                "response must be a "
                "SourceHTTPResponse."
            )

        if not isinstance(
            self.redirects,
            tuple,
        ):
            raise TypeError(
                "redirects must be a tuple."
            )

        if not all(
            isinstance(
                hop,
                SourceRedirectHop,
            )
            for hop in self.redirects
        ):
            raise TypeError(
                "redirects contain an "
                "invalid hop."
            )


class SourceRedirectChainError(
    RuntimeError
):
    def __init__(
        self,
        message: str,
        *,
        redirects: tuple[
            SourceRedirectHop,
            ...,
        ] = (),
        attempted_hop: (
            SourceRedirectHop | None
        ) = None,
    ):
        super().__init__(
            message
        )

        self.redirects = tuple(
            redirects
        )

        self.attempted_hop = (
            attempted_hop
        )


class SourceRedirectLimitError(
    SourceRedirectChainError
):
    pass


class SourceRedirectLoopError(
    SourceRedirectChainError
):
    pass


class SourceRedirectInvariantError(
    SourceRedirectChainError
):
    pass


class GovernedRedirectTransport:
    """
    Governed redirect-chain orchestrator.

    This layer owns no DNS resolver, socket,
    TCP connection, TLS context, HTTP parser,
    Location parser, or raw response body
    handling.

    Each hop is executed exclusively through
    GovernedHTTPTransport.request(). Therefore
    every followed redirect starts again at the
    governed B2B1 public entry point and must
    obtain a fresh B2A bound connection.

    B2B2 consumes only the already-validated
    SourceRedirectRequired.target produced by
    B2B1. It never interprets a raw Location
    header itself.

    Redirect count is bounded by source policy.
    B2B2 does not claim one portable wall-clock
    deadline across the complete redirect chain:
    each B2B1 hop owns its HTTP/TLS phase deadline,
    while DNS retains the explicit B1 blocking
    resolver limitation.
    """

    def __init__(
        self,
        transport: (
            GovernedHTTPTransport | None
        ) = None,
    ):
        self.transport = (
            transport
            if transport is not None
            else GovernedHTTPTransport()
        )

        if not isinstance(
            self.transport,
            GovernedHTTPTransport,
        ):
            raise TypeError(
                "transport must be a "
                "GovernedHTTPTransport."
            )

        self.policy = (
            self.transport.policy
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

    def _revalidate_redirect_target(
        self,
        target: SourceAccessTarget,
    ) -> SourceAccessTarget:
        if not isinstance(
            target,
            SourceAccessTarget,
        ):
            raise SourceRedirectInvariantError(
                "Redirect signal contains an "
                "invalid target."
            )

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
            raise SourceRedirectInvariantError(
                "Redirect target does not "
                "match canonical source policy."
            )

        return canonical

    def _validate_final_response(
        self,
        response: SourceHTTPResponse,
        *,
        current: SourceAccessTarget,
        method: str,
        redirects: tuple[
            SourceRedirectHop,
            ...,
        ],
    ) -> SourceHTTPResponse:
        if not isinstance(
            response,
            SourceHTTPResponse,
        ):
            raise SourceRedirectInvariantError(
                "B2B1 returned an invalid "
                "final response object.",
                redirects=redirects,
            )

        if not isinstance(
            response.target,
            SourceAccessTarget,
        ):
            raise SourceRedirectInvariantError(
                "Final response contains an "
                "invalid target.",
                redirects=redirects,
            )

        try:
            canonical = (
                self.policy.prepare_url(
                    response.target.request_url
                )
            )
        except Exception as error:
            raise SourceRedirectInvariantError(
                "Final response target "
                "revalidation failed.",
                redirects=redirects,
            ) from error

        if (
            self._target_identity(
                canonical
            )
            != self._target_identity(
                response.target
            )
        ):
            raise SourceRedirectInvariantError(
                "Final response target is "
                "not canonical.",
                redirects=redirects,
            )

        if (
            self._target_identity(
                canonical
            )
            != self._target_identity(
                current
            )
        ):
            raise SourceRedirectInvariantError(
                "Final response target does "
                "not match the requested hop.",
                redirects=redirects,
            )

        if response.method != method:
            raise SourceRedirectInvariantError(
                "Final response method does "
                "not match the request.",
                redirects=redirects,
            )

        status = response.status

        if (
            isinstance(
                status,
                bool,
            )
            or not isinstance(
                status,
                int,
            )
            or status < 200
            or status > 599
        ):
            raise SourceRedirectInvariantError(
                "Final response status is "
                "outside the supported "
                "HTTP response range.",
                redirects=redirects,
            )

        if status in _REDIRECT_STATUSES:
            raise SourceRedirectInvariantError(
                "B2B1 returned a redirect "
                "response instead of a "
                "redirect signal.",
                redirects=redirects,
            )

        return response

    def request(
        self,
        method: str,
        url: str,
    ) -> GovernedRedirectResponse:
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
                "Redirect transport supports "
                "only GET and HEAD."
            )

        current = (
            self.policy.prepare_url(
                url
            )
        )

        visited = {
            current.request_url
        }

        redirects: list[
            SourceRedirectHop
        ] = []

        while True:
            try:
                response = (
                    self.transport.request(
                        normalized_method,
                        current.request_url,
                    )
                )

            except SourceRedirectRequired as exc:
                if (
                    exc.status
                    not in _REDIRECT_STATUSES
                ):
                    raise (
                        SourceRedirectInvariantError(
                            "B2B1 emitted an "
                            "unsupported redirect "
                            "status.",
                            redirects=tuple(
                                redirects
                            ),
                        )
                    ) from exc

                try:
                    target = (
                        self
                        ._revalidate_redirect_target(
                            exc.target
                        )
                    )
                except Exception as error:
                    # Even a malformed or forged
                    # later redirect must preserve
                    # the already-validated chain
                    # for failure provenance.
                    raise (
                        SourceRedirectInvariantError(
                            "Redirect target "
                            "revalidation failed.",
                            redirects=tuple(
                                redirects
                            ),
                        )
                    ) from error

                hop = SourceRedirectHop(
                    status=exc.status,
                    source_url=(
                        current.request_url
                    ),
                    target_url=(
                        target.request_url
                    ),
                )

                if (
                    current.scheme == "https"
                    and target.scheme != "https"
                ):
                    raise (
                        SourceRedirectInvariantError(
                            "HTTPS redirect downgrade "
                            "to HTTP is forbidden.",
                            redirects=tuple(
                                redirects
                            ),
                            attempted_hop=hop,
                        )
                    ) from exc

                if (
                    target.request_url
                    in visited
                ):
                    raise (
                        SourceRedirectLoopError(
                            "Redirect loop "
                            "detected.",
                            redirects=tuple(
                                redirects
                            ),
                            attempted_hop=hop,
                        )
                    ) from exc

                if (
                    len(redirects)
                    >= self.policy
                    .max_redirects
                ):
                    raise (
                        SourceRedirectLimitError(
                            "Redirect limit "
                            "exceeded.",
                            redirects=tuple(
                                redirects
                            ),
                            attempted_hop=hop,
                        )
                    ) from exc

                redirects.append(
                    hop
                )

                visited.add(
                    target.request_url
                )

                current = target
                continue

            redirect_history = tuple(
                redirects
            )

            response = (
                self._validate_final_response(
                    response,
                    current=current,
                    method=normalized_method,
                    redirects=redirect_history,
                )
            )

            return GovernedRedirectResponse(
                response=response,
                redirects=redirect_history,
            )


__all__ = [
    "GOVERNED_REDIRECT_VERSION",
    "GovernedRedirectResponse",
    "GovernedRedirectTransport",
    "SourceRedirectChainError",
    "SourceRedirectHop",
    "SourceRedirectInvariantError",
    "SourceRedirectLimitError",
    "SourceRedirectLoopError",
]
