import hashlib
import unittest

from maestro.research.source_access import (
    SourceAccessPolicy,
    SourceAccessTarget,
)
from maestro.research.transport import (
    GovernedHTTPTransport,
    SourceHTTPResponse,
    SourceRedirectRequired,
)
from maestro.research.redirects import (
    GovernedRedirectTransport,
    SourceRedirectInvariantError,
    SourceRedirectLimitError,
    SourceRedirectLoopError,
)


def response(
    url,
    *,
    method="GET",
    status=200,
    body=b"",
):
    policy = SourceAccessPolicy()

    target = policy.prepare_url(
        url
    )

    return SourceHTTPResponse(
        target=target,
        method=method,
        status=status,
        content_type=None,
        body=body,
        body_sha256=(
            hashlib.sha256(
                body
            ).hexdigest()
        ),
    )


def redirect(
    policy,
    status,
    url,
):
    return SourceRedirectRequired(
        status=status,
        target=policy.prepare_url(
            url
        ),
    )


class ScriptedHTTPTransport(
    GovernedHTTPTransport
):
    def __init__(
        self,
        events,
        *,
        policy=None,
    ):
        self.policy = (
            policy
            if policy is not None
            else SourceAccessPolicy()
        )

        self.events = list(
            events
        )

        self.calls = []

    def request(
        self,
        method,
        url,
    ):
        self.calls.append(
            (
                method,
                url,
            )
        )

        if not self.events:
            raise AssertionError(
                "No scripted transport "
                "event remains."
            )

        event = self.events.pop(0)

        if isinstance(
            event,
            BaseException,
        ):
            raise event

        return event


class GovernedRedirectTransportTests(
    unittest.TestCase
):
    def test_requires_governed_http_transport(self):
        with self.assertRaises(
            TypeError
        ):
            GovernedRedirectTransport(
                object()
            )

    def test_only_get_and_head_are_supported(self):
        transport = ScriptedHTTPTransport(
            []
        )

        wrapper = GovernedRedirectTransport(
            transport
        )

        for method in (
            "POST",
            "PUT",
            "PATCH",
            "DELETE",
        ):
            with self.subTest(
                method=method
            ):
                with self.assertRaises(
                    ValueError
                ):
                    wrapper.request(
                        method,
                        "https://example.com/",
                    )

        self.assertEqual(
            transport.calls,
            [],
        )

    def test_method_is_normalized(self):
        final = response(
            "https://example.com/",
        )

        transport = ScriptedHTTPTransport(
            [
                final,
            ]
        )

        wrapper = GovernedRedirectTransport(
            transport
        )

        result = wrapper.request(
            "  get  ",
            "https://example.com/",
        )

        self.assertIs(
            result.response,
            final,
        )

        self.assertEqual(
            transport.calls,
            [
                (
                    "GET",
                    "https://example.com/",
                )
            ],
        )

    def test_invalid_initial_url_is_rejected_before_transport(self):
        transport = ScriptedHTTPTransport(
            []
        )

        wrapper = GovernedRedirectTransport(
            transport
        )

        with self.assertRaises(
            Exception
        ):
            wrapper.request(
                "GET",
                "http://127.0.0.1/",
            )

        self.assertEqual(
            transport.calls,
            [],
        )

    def test_no_redirect_returns_empty_history(self):
        final = response(
            "https://example.com/final",
            body=b"OK",
        )

        transport = ScriptedHTTPTransport(
            [
                final,
            ]
        )

        result = GovernedRedirectTransport(
            transport
        ).request(
            "GET",
            "https://example.com/final",
        )

        self.assertIs(
            result.response,
            final,
        )

        self.assertEqual(
            result.redirects,
            (),
        )

    def test_one_redirect_follows_validated_target(self):
        policy = SourceAccessPolicy()

        final = response(
            "https://other.example/final",
            body=b"OK",
        )

        transport = ScriptedHTTPTransport(
            [
                redirect(
                    policy,
                    302,
                    "https://other.example/final",
                ),
                final,
            ],
            policy=policy,
        )

        result = GovernedRedirectTransport(
            transport
        ).request(
            "GET",
            "https://example.com/start",
        )

        self.assertEqual(
            transport.calls,
            [
                (
                    "GET",
                    "https://example.com/start",
                ),
                (
                    "GET",
                    "https://other.example/final",
                ),
            ],
        )

        self.assertEqual(
            len(result.redirects),
            1,
        )

        hop = result.redirects[0]

        self.assertEqual(
            hop.status,
            302,
        )

        self.assertEqual(
            hop.source_url,
            "https://example.com/start",
        )

        self.assertEqual(
            hop.target_url,
            "https://other.example/final",
        )

    def test_head_is_preserved_across_redirect(self):
        policy = SourceAccessPolicy()

        final = response(
            "https://other.example/",
            method="HEAD",
        )

        transport = ScriptedHTTPTransport(
            [
                redirect(
                    policy,
                    301,
                    "https://other.example/",
                ),
                final,
            ],
            policy=policy,
        )

        GovernedRedirectTransport(
            transport
        ).request(
            "HEAD",
            "https://example.com/",
        )

        self.assertEqual(
            transport.calls,
            [
                (
                    "HEAD",
                    "https://example.com/",
                ),
                (
                    "HEAD",
                    "https://other.example/",
                ),
            ],
        )

    def test_multi_hop_history_is_ordered(self):
        policy = SourceAccessPolicy()

        final = response(
            "https://three.example/final",
        )

        transport = ScriptedHTTPTransport(
            [
                redirect(
                    policy,
                    301,
                    "https://two.example/a",
                ),
                redirect(
                    policy,
                    308,
                    "https://three.example/final",
                ),
                final,
            ],
            policy=policy,
        )

        result = GovernedRedirectTransport(
            transport
        ).request(
            "GET",
            "https://one.example/start",
        )

        self.assertEqual(
            tuple(
                (
                    hop.status,
                    hop.source_url,
                    hop.target_url,
                )
                for hop
                in result.redirects
            ),
            (
                (
                    301,
                    "https://one.example/start",
                    "https://two.example/a",
                ),
                (
                    308,
                    "https://two.example/a",
                    "https://three.example/final",
                ),
            ),
        )

    def test_exact_redirect_limit_is_allowed(self):
        policy = SourceAccessPolicy(
            max_redirects=2
        )

        final = response(
            "https://three.example/",
        )

        transport = ScriptedHTTPTransport(
            [
                redirect(
                    policy,
                    301,
                    "https://two.example/",
                ),
                redirect(
                    policy,
                    302,
                    "https://three.example/",
                ),
                final,
            ],
            policy=policy,
        )

        result = GovernedRedirectTransport(
            transport
        ).request(
            "GET",
            "https://one.example/",
        )

        self.assertEqual(
            len(result.redirects),
            2,
        )

        self.assertEqual(
            len(transport.calls),
            3,
        )

    def test_redirect_limit_exceeded_without_following_extra_hop(self):
        policy = SourceAccessPolicy(
            max_redirects=2
        )

        transport = ScriptedHTTPTransport(
            [
                redirect(
                    policy,
                    301,
                    "https://two.example/",
                ),
                redirect(
                    policy,
                    302,
                    "https://three.example/",
                ),
                redirect(
                    policy,
                    307,
                    "https://four.example/",
                ),
            ],
            policy=policy,
        )

        wrapper = GovernedRedirectTransport(
            transport
        )

        with self.assertRaises(
            SourceRedirectLimitError
        ) as caught:
            wrapper.request(
                "GET",
                "https://one.example/",
            )

        self.assertEqual(
            len(transport.calls),
            3,
        )

        self.assertEqual(
            len(
                caught.exception.redirects
            ),
            2,
        )

        self.assertEqual(
            caught.exception
            .attempted_hop.target_url,
            "https://four.example/",
        )

    def test_minimum_redirect_limit_blocks_second_redirect(self):
        policy = SourceAccessPolicy(
            max_redirects=1
        )

        transport = ScriptedHTTPTransport(
            [
                redirect(
                    policy,
                    302,
                    "https://two.example/",
                ),
                redirect(
                    policy,
                    307,
                    "https://three.example/",
                ),
            ],
            policy=policy,
        )

        with self.assertRaises(
            SourceRedirectLimitError
        ) as caught:
            GovernedRedirectTransport(
                transport
            ).request(
                "GET",
                "https://one.example/",
            )

        self.assertEqual(
            len(transport.calls),
            2,
        )

        self.assertEqual(
            len(
                caught.exception.redirects
            ),
            1,
        )

        self.assertEqual(
            caught.exception
            .attempted_hop.target_url,
            "https://three.example/",
        )

    def test_self_redirect_is_rejected(self):
        policy = SourceAccessPolicy()

        transport = ScriptedHTTPTransport(
            [
                redirect(
                    policy,
                    301,
                    "https://example.com/a",
                ),
            ],
            policy=policy,
        )

        with self.assertRaises(
            SourceRedirectLoopError
        ):
            GovernedRedirectTransport(
                transport
            ).request(
                "GET",
                "https://example.com/a",
            )

        self.assertEqual(
            len(transport.calls),
            1,
        )

    def test_two_node_redirect_loop_is_rejected(self):
        policy = SourceAccessPolicy()

        transport = ScriptedHTTPTransport(
            [
                redirect(
                    policy,
                    302,
                    "https://b.example/",
                ),
                redirect(
                    policy,
                    302,
                    "https://a.example/",
                ),
            ],
            policy=policy,
        )

        with self.assertRaises(
            SourceRedirectLoopError
        ) as caught:
            GovernedRedirectTransport(
                transport
            ).request(
                "GET",
                "https://a.example/",
            )

        self.assertEqual(
            len(transport.calls),
            2,
        )

        self.assertEqual(
            len(
                caught.exception.redirects
            ),
            1,
        )

        self.assertEqual(
            caught.exception
            .attempted_hop.target_url,
            "https://a.example/",
        )

    def test_canonical_equivalent_loop_is_rejected(self):
        policy = SourceAccessPolicy()

        transport = ScriptedHTTPTransport(
            [
                redirect(
                    policy,
                    301,
                    "https://EXAMPLE.COM/a",
                ),
            ],
            policy=policy,
        )

        with self.assertRaises(
            SourceRedirectLoopError
        ):
            GovernedRedirectTransport(
                transport
            ).request(
                "GET",
                "https://example.com/a",
            )

        self.assertEqual(
            len(transport.calls),
            1,
        )

    def test_https_to_http_downgrade_is_rejected(self):
        policy = SourceAccessPolicy()

        transport = ScriptedHTTPTransport(
            [
                redirect(
                    policy,
                    302,
                    "http://other.example/",
                ),
            ],
            policy=policy,
        )

        with self.assertRaises(
            SourceRedirectInvariantError
        ) as caught:
            GovernedRedirectTransport(
                transport
            ).request(
                "GET",
                "https://secure.example/",
            )

        self.assertEqual(
            transport.calls,
            [
                (
                    "GET",
                    "https://secure.example/",
                )
            ],
        )

        self.assertEqual(
            caught.exception.redirects,
            (),
        )

        self.assertIsNotNone(
            caught.exception.attempted_hop
        )

        self.assertEqual(
            caught.exception
            .attempted_hop.source_url,
            "https://secure.example/",
        )

        self.assertEqual(
            caught.exception
            .attempted_hop.target_url,
            "http://other.example/",
        )

    def test_tampered_later_redirect_preserves_prior_history(self):
        policy = SourceAccessPolicy()

        tampered = SourceAccessTarget(
            original_url=(
                "https://c.example/"
            ),
            request_url=(
                "https://c.example/"
            ),
            scheme="https",
            hostname="127.0.0.1",
            port=443,
        )

        transport = ScriptedHTTPTransport(
            [
                redirect(
                    policy,
                    301,
                    "https://b.example/",
                ),
                SourceRedirectRequired(
                    status=302,
                    target=tampered,
                ),
            ],
            policy=policy,
        )

        with self.assertRaises(
            SourceRedirectInvariantError
        ) as caught:
            GovernedRedirectTransport(
                transport
            ).request(
                "GET",
                "https://a.example/",
            )

        self.assertEqual(
            len(transport.calls),
            2,
        )

        self.assertEqual(
            len(
                caught.exception.redirects
            ),
            1,
        )

        first = (
            caught.exception.redirects[0]
        )

        self.assertEqual(
            first.status,
            301,
        )

        self.assertEqual(
            first.source_url,
            "https://a.example/",
        )

        self.assertEqual(
            first.target_url,
            "https://b.example/",
        )

        self.assertIsNone(
            caught.exception.attempted_hop
        )

    def test_invalid_redirect_status_is_rejected(self):
        policy = SourceAccessPolicy()

        invalid = SourceRedirectRequired(
            status=300,
            target=policy.prepare_url(
                "https://other.example/"
            ),
        )

        transport = ScriptedHTTPTransport(
            [
                invalid,
            ],
            policy=policy,
        )

        with self.assertRaises(
            SourceRedirectInvariantError
        ):
            GovernedRedirectTransport(
                transport
            ).request(
                "GET",
                "https://example.com/",
            )

        self.assertEqual(
            len(transport.calls),
            1,
        )

    def test_tampered_redirect_target_is_rejected(self):
        policy = SourceAccessPolicy()

        tampered = SourceAccessTarget(
            original_url=(
                "https://other.example/"
            ),
            request_url=(
                "https://other.example/"
            ),
            scheme="https",
            hostname="127.0.0.1",
            port=443,
        )

        transport = ScriptedHTTPTransport(
            [
                SourceRedirectRequired(
                    status=302,
                    target=tampered,
                ),
            ],
            policy=policy,
        )

        with self.assertRaises(
            SourceRedirectInvariantError
        ):
            GovernedRedirectTransport(
                transport
            ).request(
                "GET",
                "https://example.com/",
            )

        self.assertEqual(
            len(transport.calls),
            1,
        )

    def test_final_response_identity_is_preserved(self):
        policy = SourceAccessPolicy()

        final = response(
            "https://final.example/result",
            body=b"RESULT",
        )

        transport = ScriptedHTTPTransport(
            [
                redirect(
                    policy,
                    303,
                    "https://final.example/result",
                ),
                final,
            ],
            policy=policy,
        )

        result = GovernedRedirectTransport(
            transport
        ).request(
            "GET",
            "https://start.example/",
        )

        self.assertIs(
            result.response,
            final,
        )

        self.assertEqual(
            result.response
            .target.request_url,
            "https://final.example/result",
        )

        self.assertEqual(
            result.response.body,
            b"RESULT",
        )

    def test_final_response_target_must_match_current_hop(self):
        final = response(
            "https://wrong.example/",
        )

        transport = ScriptedHTTPTransport(
            [
                final,
            ]
        )

        with self.assertRaises(
            SourceRedirectInvariantError
        ):
            GovernedRedirectTransport(
                transport
            ).request(
                "GET",
                "https://expected.example/",
            )

        self.assertEqual(
            transport.calls,
            [
                (
                    "GET",
                    "https://expected.example/",
                )
            ],
        )

    def test_final_response_method_must_match_request(self):
        final = response(
            "https://example.com/",
            method="HEAD",
        )

        transport = ScriptedHTTPTransport(
            [
                final,
            ]
        )

        with self.assertRaises(
            SourceRedirectInvariantError
        ):
            GovernedRedirectTransport(
                transport
            ).request(
                "GET",
                "https://example.com/",
            )

    def test_final_redirect_status_must_be_signalled_not_returned(self):
        final = response(
            "https://example.com/",
            status=302,
        )

        transport = ScriptedHTTPTransport(
            [
                final,
            ]
        )

        with self.assertRaises(
            SourceRedirectInvariantError
        ):
            GovernedRedirectTransport(
                transport
            ).request(
                "GET",
                "https://example.com/",
            )

    def test_tampered_final_response_target_is_rejected(self):
        policy = SourceAccessPolicy()

        tampered = SourceAccessTarget(
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

        final = SourceHTTPResponse(
            target=tampered,
            method="GET",
            status=200,
            content_type=None,
            body=b"",
            body_sha256=(
                hashlib.sha256(
                    b""
                ).hexdigest()
            ),
        )

        transport = ScriptedHTTPTransport(
            [
                final,
            ],
            policy=policy,
        )

        with self.assertRaises(
            SourceRedirectInvariantError
        ):
            GovernedRedirectTransport(
                transport
            ).request(
                "GET",
                "https://example.com/",
            )

    def test_redirect_history_is_immutable_tuple(self):
        policy = SourceAccessPolicy()

        final = response(
            "https://b.example/",
        )

        transport = ScriptedHTTPTransport(
            [
                redirect(
                    policy,
                    302,
                    "https://b.example/",
                ),
                final,
            ],
            policy=policy,
        )

        result = GovernedRedirectTransport(
            transport
        ).request(
            "GET",
            "https://a.example/",
        )

        self.assertIsInstance(
            result.redirects,
            tuple,
        )

        self.assertEqual(
            len(result.redirects),
            1,
        )


if __name__ == "__main__":
    unittest.main()
