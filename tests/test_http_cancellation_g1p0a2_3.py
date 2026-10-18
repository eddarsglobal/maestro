"""G1-P0-A2.3: live local socket cancellation without external network.

This does not certify DNS/TCP connector cancellation, crash atomicity,
or all external effects. Those remain separate guardian gates.
"""
import socket
import threading
import time
import unittest
from unittest.mock import patch

from maestro.research.connector import BoundSourceConnection
from maestro.research.resolver import NumericSourceEndpoint
from maestro.research.source_access import SourceAccessPolicy
from maestro.research.transport import (
    GovernedHTTPTransport,
    SourceTransportCancelled,
    governed_http_cancellation,
)


class HTTPCancellationTests(unittest.TestCase):
    def setUp(self):
        self.peers = []

    def tearDown(self):
        for sock in self.peers:
            sock.close()

    def make_transport(self):
        owned, peer = socket.socketpair()
        self.peers.extend((owned, peer))
        peer.settimeout(3)
        target = SourceAccessPolicy().prepare_url('http://example.com/resource')
        bound = BoundSourceConnection(
            target=target,
            endpoint=NumericSourceEndpoint(
                family=socket.AF_INET, address='8.8.8.8', port=80,
            ),
            socket=owned,
        )
        transport = GovernedHTTPTransport()
        connect = patch.object(transport.connector, 'connect_url', return_value=bound)
        validate = patch.object(transport, '_revalidate_bound', return_value=target)
        self.addCleanup(connect.stop)
        self.addCleanup(validate.stop)
        connect.start()
        validate.start()
        return transport, peer

    def run_in_thread(self, transport, cancellation):
        completed = threading.Event()
        outcome = {}
        def run():
            try:
                with governed_http_cancellation(cancellation):
                    outcome['result'] = transport.request('GET', 'http://example.com/resource')
            except BaseException as exc:
                outcome['error'] = exc
            finally:
                completed.set()
        worker = threading.Thread(target=run, daemon=True)
        worker.start()
        return worker, completed, outcome

    def drain_request(self, peer):
        request = b''
        while b'\r\n\r\n' not in request:
            request += peer.recv(4096)
            self.assertLess(len(request), 32_768)
        self.assertIn(b'GET /resource HTTP/1.1', request)

    def test_precancelled_has_no_dns_or_tcp_side_effect(self):
        transport, peer = self.make_transport()
        cancelled = threading.Event()
        cancelled.set()
        with governed_http_cancellation(cancelled):
            with self.assertRaises(SourceTransportCancelled):
                transport.request('GET', 'http://example.com/resource')
        transport.connector.connect_url.assert_not_called()

    def test_cancel_during_blocked_headers_aborts_socket(self):
        transport, peer = self.make_transport()
        cancellation = threading.Event()
        worker, done, outcome = self.run_in_thread(transport, cancellation)
        self.drain_request(peer)
        cancellation.set()
        self.assertTrue(done.wait(2), 'blocked header read did not abort promptly')
        worker.join(0.2)
        self.assertIsInstance(outcome.get('error'), SourceTransportCancelled)
        self.assertNotIn('result', outcome)

    def test_cancel_during_blocked_body_discards_partial_response(self):
        transport, peer = self.make_transport()
        cancellation = threading.Event()
        worker, done, outcome = self.run_in_thread(transport, cancellation)
        self.drain_request(peer)
        peer.sendall(b'HTTP/1.1 200 OK\r\nContent-Length: 100\r\n\r\nX')
        cancellation.set()
        self.assertTrue(done.wait(2), 'blocked body read did not abort promptly')
        worker.join(0.2)
        self.assertIsInstance(outcome.get('error'), SourceTransportCancelled)
        self.assertNotIn('result', outcome)

    def test_successful_response_without_cancellation(self):
        transport, peer = self.make_transport()
        cancellation = threading.Event()
        worker, done, outcome = self.run_in_thread(transport, cancellation)
        self.drain_request(peer)
        peer.sendall(b'HTTP/1.1 200 OK\r\nContent-Length: 2\r\n\r\nOK')
        self.assertTrue(done.wait(2))
        worker.join(0.2)
        self.assertNotIn('error', outcome)
        self.assertEqual(outcome['result'].body, b'OK')

    def test_one_cancel_does_not_kill_concurrent_request(self):
        left, peer_left = self.make_transport()
        right, peer_right = self.make_transport()
        cancel_left = threading.Event()
        cancel_right = threading.Event()
        worker_left, done_left, out_left = self.run_in_thread(left, cancel_left)
        worker_right, done_right, out_right = self.run_in_thread(right, cancel_right)
        self.drain_request(peer_left)
        self.drain_request(peer_right)
        cancel_left.set()
        peer_right.sendall(b'HTTP/1.1 200 OK\r\nContent-Length: 1\r\n\r\nZ')
        self.assertTrue(done_left.wait(2))
        self.assertTrue(done_right.wait(2))
        worker_left.join(0.2)
        worker_right.join(0.2)
        self.assertIsInstance(out_left.get('error'), SourceTransportCancelled)
        self.assertEqual(out_right['result'].body, b'Z')

    def test_scoped_signal_is_restored(self):
        transport, peer = self.make_transport()
        signal = threading.Event()
        signal.set()
        with governed_http_cancellation(signal):
            with self.assertRaises(SourceTransportCancelled):
                transport.request('GET', 'http://example.com/resource')
        # Not cancelled outside scope (no global token left behind).
        worker, done, outcome = self.run_in_thread(transport, None)
        self.drain_request(peer)
        peer.sendall(b'HTTP/1.1 200 OK\r\nContent-Length: 1\r\n\r\nA')
        self.assertTrue(done.wait(2))
        self.assertEqual(outcome['result'].body, b'A')
        worker.join(0.2)

    def test_cancel_while_connector_is_returning_closes_late_socket(self):
        transport, peer = self.make_transport()
        cancellation = threading.Event()
        connector_entered = threading.Event()
        connector_released = threading.Event()
        bound = transport.connector.connect_url.return_value

        def delayed_connect(_url):
            connector_entered.set()
            self.assertTrue(connector_released.wait(2))
            return bound

        transport.connector.connect_url.side_effect = delayed_connect
        worker, done, outcome = self.run_in_thread(transport, cancellation)
        self.assertTrue(connector_entered.wait(2))
        cancellation.set()
        connector_released.set()
        self.assertTrue(done.wait(2))
        worker.join(0.2)
        self.assertIsInstance(outcome.get('error'), SourceTransportCancelled)
        self.assertEqual(bound.socket.fileno(), -1)
        self.assertNotIn('result', outcome)

    def test_cancel_before_response_delivery_discards_complete_body(self):
        transport, peer = self.make_transport()
        cancellation = threading.Event()
        original = transport._read_body

        def read_and_cancel(*args, **kwargs):
            body = original(*args, **kwargs)
            cancellation.set()
            return body

        with patch.object(transport, '_read_body', side_effect=read_and_cancel):
            worker, done, outcome = self.run_in_thread(transport, cancellation)
            self.drain_request(peer)
            peer.sendall(b'HTTP/1.1 200 OK\r\nContent-Length: 2\r\n\r\nOK')
            self.assertTrue(done.wait(2))
            worker.join(0.2)
        self.assertIsInstance(outcome.get('error'), SourceTransportCancelled)
        self.assertNotIn('result', outcome)

    def test_bad_signal_is_rejected(self):
        with self.assertRaises(TypeError):
            with governed_http_cancellation(object()):
                pass


if __name__ == '__main__':
    unittest.main()
