import unittest

from maestro.research.source_access import (
    SOURCE_ACCESS_POLICY_VERSION,
    ResolvedSourceTarget,
    SourceAccessPolicy,
    SourceAccessViolation,
)


class SourceAccessPolicyTests(
    unittest.TestCase
):
    def setUp(self):
        self.policy = (
            SourceAccessPolicy()
        )

    def test_default_policy_is_bounded(self):
        self.assertEqual(
            SOURCE_ACCESS_POLICY_VERSION,
            "RX0.3A",
        )
        self.assertEqual(
            self.policy.max_redirects,
            5,
        )
        self.assertEqual(
            self.policy.max_response_bytes,
            8 * 1024 * 1024,
        )
        self.assertEqual(
            self.policy.max_resolved_addresses,
            16,
        )
        self.assertEqual(
            self.policy.timeout_seconds,
            10.0,
        )

    def test_policy_rejects_invalid_limits(self):
        with self.assertRaises(
            ValueError
        ):
            SourceAccessPolicy(
                max_redirects=0
            )

        with self.assertRaises(
            TypeError
        ):
            SourceAccessPolicy(
                max_response_bytes=True
            )

        with self.assertRaises(
            ValueError
        ):
            SourceAccessPolicy(
                timeout_seconds=0
            )

        with self.assertRaises(
            ValueError
        ):
            SourceAccessPolicy(
                max_resolved_addresses=33
            )

    def test_https_hostname_normalizes_and_strips_fragment(self):
        target = self.policy.prepare_url(
            "HTTPS://Example.COM/a?q=1#part"
        )

        self.assertEqual(
            target.scheme,
            "https",
        )
        self.assertEqual(
            target.hostname,
            "example.com",
        )
        self.assertEqual(
            target.port,
            443,
        )
        self.assertEqual(
            target.request_url,
            "https://example.com/a?q=1",
        )

    def test_http_hostname_uses_port_80(self):
        target = self.policy.prepare_url(
            "http://example.com:80/"
        )

        self.assertEqual(
            target.port,
            80,
        )
        self.assertEqual(
            target.request_url,
            "http://example.com/",
        )

    def test_rejects_non_http_schemes(self):
        for url in (
            "file:///etc/passwd",
            "ftp://example.com/a",
            "gopher://example.com/a",
            "data:text/plain,x",
        ):
            with self.subTest(url=url):
                with self.assertRaises(
                    SourceAccessViolation
                ):
                    self.policy.prepare_url(
                        url
                    )

    def test_rejects_missing_authority(self):
        with self.assertRaises(
            SourceAccessViolation
        ):
            self.policy.prepare_url(
                "https:///missing-host"
            )

    def test_rejects_userinfo_credentials(self):
        for url in (
            "https://user@example.com/",
            (
                "https://user:pass@"
                "example.com/"
            ),
            "https://@example.com/",
        ):
            with self.subTest(url=url):
                with self.assertRaises(
                    SourceAccessViolation
                ):
                    self.policy.prepare_url(
                        url
                    )

    def test_rejects_nonstandard_or_mismatched_ports(self):
        for url in (
            "https://example.com:8443/",
            "https://example.com:80/",
            "http://example.com:443/",
            "https://example.com:abc/",
            "https://example.com:99999/",
        ):
            with self.subTest(url=url):
                with self.assertRaises(
                    SourceAccessViolation
                ):
                    self.policy.prepare_url(
                        url
                    )

    def test_rejects_raw_control_characters(self):
        for url in (
            "https://example.com/a\nb",
            "https://example.com/a\tb",
            "https://example.com/\x00x",
            " https://example.com/",
        ):
            with self.subTest(
                url=repr(url)
            ):
                with self.assertRaises(
                    SourceAccessViolation
                ):
                    self.policy.prepare_url(
                        url
                    )

    def test_rejects_backslash(self):
        with self.assertRaises(
            SourceAccessViolation
        ):
            self.policy.prepare_url(
                "https://example.com\\@127.0.0.1/"
            )

    def test_rejects_localhost_names(self):
        for url in (
            "http://localhost/",
            "http://localhost./",
            "https://a.localhost/",
            "https://service.local/",
        ):
            with self.subTest(url=url):
                with self.assertRaises(
                    SourceAccessViolation
                ):
                    self.policy.prepare_url(
                        url
                    )

    def test_rejects_single_label_hostname(self):
        with self.assertRaises(
            SourceAccessViolation
        ):
            self.policy.prepare_url(
                "https://intranet/"
            )

    def test_rejects_ambiguous_numeric_hostname(self):
        with self.assertRaises(
            SourceAccessViolation
        ):
            self.policy.prepare_url(
                "http://0177.0.0.1/"
            )

    def test_rejects_non_global_literal_ipv4(self):
        for address in (
            "127.0.0.1",
            "10.0.0.1",
            "172.16.0.1",
            "192.168.1.1",
            "169.254.169.254",
            "100.64.0.1",
            "0.0.0.0",
            "224.0.0.1",
            "192.0.2.1",
        ):
            with self.subTest(
                address=address
            ):
                with self.assertRaises(
                    SourceAccessViolation
                ):
                    self.policy.prepare_url(
                        f"http://{address}/"
                    )

    def test_rejects_non_global_literal_ipv6(self):
        for address in (
            "::1",
            "fc00::1",
            "fe80::1",
            "fec0::1",
            "ff02::1",
            "2001:db8::1",
        ):
            with self.subTest(
                address=address
            ):
                with self.assertRaises(
                    SourceAccessViolation
                ):
                    self.policy.prepare_url(
                        f"https://[{address}]/"
                    )

    def test_allows_global_literal_ips(self):
        ipv4 = self.policy.prepare_url(
            "https://8.8.8.8/"
        )

        ipv6 = self.policy.prepare_url(
            (
                "https://"
                "[2606:4700:4700::1111]/"
            )
        )

        self.assertEqual(
            ipv4.literal_ip,
            "8.8.8.8",
        )

        self.assertEqual(
            ipv6.literal_ip,
            "2606:4700:4700::1111",
        )

    def test_idna_hostname_is_canonicalized(self):
        target = self.policy.prepare_url(
            "https://bücher.example/path"
        )

        self.assertEqual(
            target.hostname,
            "xn--bcher-kva.example",
        )

        self.assertEqual(
            target.request_url,
            (
                "https://"
                "xn--bcher-kva.example/path"
            ),
        )

    def test_resolution_requires_addresses_for_hostname(self):
        target = self.policy.prepare_url(
            "https://example.com/"
        )

        with self.assertRaises(
            SourceAccessViolation
        ):
            self.policy.validate_resolution(
                target,
                [],
            )

    def test_resolution_rejects_any_non_global_address(self):
        target = self.policy.prepare_url(
            "https://example.com/"
        )

        with self.assertRaises(
            SourceAccessViolation
        ):
            self.policy.validate_resolution(
                target,
                [
                    "8.8.8.8",
                    "127.0.0.1",
                ],
            )

    def test_resolution_rejects_too_many_addresses(self):
        policy = SourceAccessPolicy(
            max_resolved_addresses=2
        )

        target = policy.prepare_url(
            "https://example.com/"
        )

        with self.assertRaises(
            SourceAccessViolation
        ):
            policy.validate_resolution(
                target,
                [
                    "8.8.8.8",
                    "1.1.1.1",
                    "9.9.9.9",
                ],
            )

    def test_resolution_deduplicates_preserving_order(self):
        target = self.policy.prepare_url(
            "https://example.com/"
        )

        resolved = (
            self.policy
            .validate_resolution(
                target,
                [
                    "8.8.8.8",
                    "1.1.1.1",
                    "8.8.8.8",
                ],
            )
        )

        self.assertIsInstance(
            resolved,
            ResolvedSourceTarget,
        )

        self.assertEqual(
            resolved.addresses,
            (
                "8.8.8.8",
                "1.1.1.1",
            ),
        )

    def test_literal_ip_resolution_is_bound_to_literal(self):
        target = self.policy.prepare_url(
            "https://8.8.8.8/"
        )

        resolved = (
            self.policy
            .validate_resolution(
                target,
                [],
            )
        )

        self.assertEqual(
            resolved.addresses,
            ("8.8.8.8",),
        )

        with self.assertRaises(
            SourceAccessViolation
        ):
            self.policy.validate_resolution(
                target,
                ["1.1.1.1"],
            )

    def test_relative_redirect_is_revalidated(self):
        current = self.policy.prepare_url(
            "https://example.com/a/b"
        )

        redirected = (
            self.policy
            .prepare_redirect(
                current,
                "../next?q=1#fragment",
            )
        )

        self.assertEqual(
            redirected.request_url,
            (
                "https://example.com/"
                "next?q=1"
            ),
        )

    def test_redirect_to_private_or_bad_scheme_is_rejected(self):
        current = self.policy.prepare_url(
            "https://example.com/"
        )

        for location in (
            "http://127.0.0.1/admin",
            "file:///etc/passwd",
            "//localhost/private",
        ):
            with self.subTest(
                location=location
            ):
                with self.assertRaises(
                    SourceAccessViolation
                ):
                    self.policy.prepare_redirect(
                        current,
                        location,
                    )

    def test_rejects_ipv6_transition_mechanisms(self):
        for address in (
            "::ffff:8.8.8.8",
            "2002:0808:0808::",
            (
                "2001:0000:4136:e378:"
                "8000:63bf:3fff:fdd2"
            ),
        ):
            with self.subTest(
                address=address
            ):
                with self.assertRaises(
                    SourceAccessViolation
                ):
                    self.policy.prepare_url(
                        f"https://[{address}]/"
                    )

    def test_resolution_iteration_is_bounded(self):
        policy = SourceAccessPolicy(
            max_resolved_addresses=2
        )

        target = policy.prepare_url(
            "https://example.com/"
        )

        consumed = []

        def addresses():
            for address in (
                "8.8.8.8",
                "1.1.1.1",
                "9.9.9.9",
                "208.67.222.222",
            ):
                consumed.append(address)
                yield address

        with self.assertRaises(
            SourceAccessViolation
        ):
            policy.validate_resolution(
                target,
                addresses(),
            )

        self.assertEqual(
            consumed,
            [
                "8.8.8.8",
                "1.1.1.1",
                "9.9.9.9",
            ],
        )

    def test_normalized_url_length_is_bounded(self):
        policy = SourceAccessPolicy(
            max_url_chars=24
        )

        # Raw form fits under 24 chars,
        # but IDNA canonicalization expands it.
        url = "https://bücher.example/"

        self.assertLessEqual(
            len(url),
            24,
        )

        with self.assertRaises(
            SourceAccessViolation
        ):
            policy.prepare_url(url)

    def test_url_length_is_bounded(self):
        policy = SourceAccessPolicy(
            max_url_chars=64
        )

        with self.assertRaises(
            SourceAccessViolation
        ):
            policy.prepare_url(
                "https://example.com/"
                + ("a" * 100)
            )


if __name__ == "__main__":
    unittest.main()
