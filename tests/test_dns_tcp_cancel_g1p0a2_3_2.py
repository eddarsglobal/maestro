"""A2.3.2: fail-closed cancellation of DNS wait and nonblocking TCP connect.

No external network use; fake DNS and synthetic native sockets only.
Blocking OS getaddrinfo may finish after caller abandonment; it is not killed.
"""
import errno
import socket
import threading
import time
import unittest
from unittest.mock import patch

from maestro.research.connector import (BoundSourceConnector,
    SourceConnectionCancelled, SourceConnectionError)
from maestro.research.resolver import GovernedSourceResolver
from maestro.research.source_access import SourceAccessPolicy, SourceAccessViolation
from maestro.research.transport import (GovernedHTTPTransport,
    SourceTransportCancelled, governed_http_cancellation)


def row(ip='8.8.8.8', port=80):
    return (socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP, '', (ip, port))


class NativeSocketFake(socket.socket):
    def __init__(self, *, pending=False, error=0):
        super().__init__(socket.AF_INET, socket.SOCK_STREAM)
        self.pending = pending
        self.error = error
        self.attempts = []
    def connect_ex(self, sockaddr):
        self.attempts.append(sockaddr)
        return errno.EINPROGRESS if self.pending else self.error
    def getsockopt(self, *args):
        return errno.EINPROGRESS if self.pending else 0


def connector(dns, factory, timeout=1):
    policy = SourceAccessPolicy(timeout_seconds=timeout)
    return BoundSourceConnector(
        GovernedSourceResolver(policy, getaddrinfo=dns), socket_factory=factory
    )


class DNSTCPCancelTests(unittest.TestCase):
    def test_pre_cancel_no_dns_no_socket(self):
        signal = threading.Event(); signal.set()
        dns_calls = []; socket_calls = []
        obj = connector(lambda *a: dns_calls.append(a),
                        lambda *a: socket_calls.append(a))
        with governed_http_cancellation(signal):
            with self.assertRaises(SourceConnectionCancelled):
                obj.connect_url('http://example.com/')
        self.assertEqual(dns_calls, [])
        self.assertEqual(socket_calls, [])

    def test_blocked_dns_cancels_promptly_no_tcp(self):
        start, release = threading.Event(), threading.Event()
        created = []
        def dns(*args):
            start.set(); release.wait(5)
            return [row()]
        obj = connector(dns, lambda *args: created.append(args), timeout=2)
        signal = threading.Event(); result = []
        def call():
            try:
                with governed_http_cancellation(signal):
                    obj.connect_url('http://example.com/')
            except BaseException as e:
                result.append(e)
        t = threading.Thread(target=call)
        t.start()
        try:
            self.assertTrue(start.wait(1))
            signal.set()
            t.join(0.6)
            self.assertFalse(t.is_alive())
            self.assertIsInstance(result[0], SourceConnectionCancelled)
            self.assertFalse(created)
        finally:
            release.set(); t.join(1)

    def test_abandoned_dns_result_never_creates_socket(self):
        start, release = threading.Event(), threading.Event()
        created = []
        def dns(*args):
            start.set(); release.wait(5)
            return [row()]
        obj = connector(dns, lambda *args: created.append(args))
        signal = threading.Event()
        result = []
        def run():
            with governed_http_cancellation(signal):
                try: obj.connect_url('http://example.com/')
                except SourceConnectionCancelled as e: result.append(e)
        t = threading.Thread(target=run); t.start()
        try:
            self.assertTrue(start.wait(1)); signal.set(); t.join(1)
            self.assertEqual(len(result), 1)
            release.set(); time.sleep(0.06)
            self.assertEqual(created, [])
        finally:
            release.set(); t.join(1)

    def test_dns_deadline_expires_fail_closed(self):
        release = threading.Event(); created=[]
        obj = connector(lambda *a: (release.wait(3), [row()])[1],
                        lambda *a: created.append(a), timeout=0.12)
        try:
            with governed_http_cancellation(threading.Event()):
                start=time.monotonic()
                with self.assertRaises(SourceConnectionError):
                    obj.connect_url('http://example.com/')
                self.assertLess(time.monotonic()-start, 0.7)
            self.assertEqual(created, [])
        finally: release.set()

    def test_dns_rejects_private_before_connect(self):
        created=[]
        obj=connector(lambda *a: [row('127.0.0.1')],
                      lambda *a: created.append(a))
        with governed_http_cancellation(threading.Event()):
            with self.assertRaises(SourceAccessViolation):
                obj.connect_url('http://example.com/')
        self.assertEqual(created, [])

    def test_numeric_tcp_never_receives_dns_hostname(self):
        made=[]
        def factory(*a):
            sk=NativeSocketFake(); made.append(sk); return sk
        obj=connector(lambda *a: [row()], factory)
        with governed_http_cancellation(threading.Event()):
            bound=obj.connect_url('http://example.com/')
        self.assertEqual(made[0].attempts, [('8.8.8.8',80)])
        bound.close()

    def test_cancel_pending_tcp_closes_native_socket(self):
        made=[]; entered=threading.Event()
        def factory(*a):
            sock=NativeSocketFake(pending=True); made.append(sock); return sock
        obj=connector(lambda *a: [row()], factory, timeout=3)
        signal=threading.Event(); result=[]
        def pseudo_select(r,w,x,deadline):
            entered.set(); time.sleep(min(0.02, deadline)); return ([],[],[])
        def run():
            try:
                with governed_http_cancellation(signal):
                    obj.connect_url('http://example.com/')
            except BaseException as e: result.append(e)
        with patch('maestro.research.connector.select.select', side_effect=pseudo_select):
            t=threading.Thread(target=run); t.start()
            self.assertTrue(entered.wait(1)); signal.set(); t.join(1)
        self.assertFalse(t.is_alive())
        self.assertIsInstance(result[0], SourceConnectionCancelled)
        self.assertEqual(made[0].fileno(), -1)

    def test_two_missions_isolated(self):
        a, b = threading.Event(), threading.Event()
        slow_start, slow_release = threading.Event(), threading.Event()
        output=[]
        def dns(*args):
            if threading.current_thread().name == 'maestro-governed-dns':
                # Both calls use this function, differentiate by original bound instance.
                pass
            return [row()]
        first=connector(lambda *args: (slow_start.set(), slow_release.wait(3), [row()])[2],
                        lambda *args: None,timeout=2)
        ready=[]
        second=connector(dns, lambda *args: (ready.append(NativeSocketFake()), ready[-1])[1])
        def slow():
            try:
                with governed_http_cancellation(a): first.connect_url('http://example.com/')
            except SourceConnectionCancelled: output.append('cancelled')
        thread=threading.Thread(target=slow); thread.start()
        try:
            self.assertTrue(slow_start.wait(1)); a.set()
            with governed_http_cancellation(b):
                bound=second.connect_url('http://example.com/')
            bound.close(); thread.join(1)
            self.assertEqual(output,['cancelled'])
            self.assertEqual(len(ready), 1)
        finally:
            slow_release.set(); thread.join(1)

    def test_transport_maps_connector_cancel_to_http_cancel(self):
        signal=threading.Event(); signal.set()
        obj=connector(lambda *a: [row()],lambda *a: None)
        transport=GovernedHTTPTransport(obj)
        with governed_http_cancellation(signal):
            with self.assertRaises(SourceTransportCancelled):
                transport.request('GET','http://example.com/')

    def test_cancel_during_dns_maps_to_transport(self):
        start=threading.Event(); release=threading.Event(); signal=threading.Event(); result=[]
        obj=connector(lambda *a: (start.set(), release.wait(3), [row()])[2],
                      lambda *a: None)
        def run():
            try:
                with governed_http_cancellation(signal):
                    GovernedHTTPTransport(obj).request('GET','http://example.com/')
            except BaseException as e: result.append(e)
        t=threading.Thread(target=run); t.start()
        try:
            self.assertTrue(start.wait(1)); signal.set(); t.join(1)
            self.assertIsInstance(result[0],SourceTransportCancelled)
        finally:
            release.set();t.join(1)

if __name__ == '__main__': unittest.main()
