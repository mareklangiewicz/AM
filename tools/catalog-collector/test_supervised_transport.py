"""Fake sockets and local IPC only. Never open network or loopback sockets."""
from dataclasses import replace
from datetime import datetime, timezone
import hashlib
import http.client
import traceback
import io
import json
import os
import subprocess
import sys
import time
import unittest
from unittest.mock import patch

from collector import (BODY_CAP, Chunk, Connected, Descriptor, End, Headers, Limits,
                       Prior, Refusal, Source, collect, plan)
from supervised_transport import (FRAME, FRAME_CAP, SupervisedTransport, Token,
                                  _BoundedReader, _json, _spawn, _worker)

REV = 'a' * 40
SECRET = b'FIXTURE_SECRET_NOT_REAL'
QUOTA = (('x-ratelimit-limit', '1000'), ('x-ratelimit-remaining', '900'),
         ('x-ratelimit-reset', '1793116800'))


def fixture():
    return plan((Source(Descriptor('https://api.github.com/repositories/100/releases'),
                        100, 'docs/track/release-catalog/research/fixture.md#id',
                        ('https://api.github.com/repos/example/reviewed/releases',)),), 1)


def limits(seconds=2, connect=None):
    now = time.monotonic()
    return Limits(now + (seconds if connect is None else connect), now + seconds, now + seconds)


def frame(kind, payload=b''):
    return FRAME.pack(kind, len(payload)) + payload


def valid_frames():
    return (frame(b'C') + frame(b'H', _json({'status':200,'headers':QUOTA,'condition':[]}))
            + frame(b'B', b' []\n') + frame(b'E'))


class Socket:
    def __init__(self, data):
        self.stream, self.sent, self.closed, self.timeout = io.BytesIO(data), b'', False, None

    def makefile(self, mode):
        if mode != 'rb':
            raise AssertionError('invalid mode')
        return self.stream

    def settimeout(self, value):
        self.timeout = value

    def sendall(self, wire):
        self.sent += wire

    def close(self):
        self.closed = True


class AdapterContract(unittest.TestCase):
    def setUp(self):
        # Any accidental production connector invocation in these tests is a failure.
        self.network = patch('supervised_transport.socket.create_connection',
                             side_effect=AssertionError('network forbidden in offline tests'))
        self.network.start()
        self.addCleanup(self.network.stop)
        self.processes = []
        self.addCleanup(self.cleanup)

    def cleanup(self):
        for process in self.processes:
            if process.poll() is None:
                process.kill()
            process.wait(timeout=1)
            for stream in (process.stdin,process.stdout):
                if stream and not stream.closed:
                    stream.close()

    def factory(self, data, *, hang=False, trickle=False, code=None):
        def spawn():
            script = ('import sys,time;sys.stdin.buffer.read();' +
                      (code if code is not None else
                       'sys.stdout.buffer.write('+repr(data)+');sys.stdout.buffer.flush();'+
                       ('time.sleep(10)' if hang else '')))
            if trickle:
                script = ('import sys,time;sys.stdin.buffer.read();\n'
                          f'for b in {data!r}:\n'
                          ' sys.stdout.buffer.write(bytes([b]));sys.stdout.buffer.flush();time.sleep(.01)\n')
            p = subprocess.Popen([sys.executable,'-I','-S','-c',script],
                                 stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,
                                 env={'LANG':'C.UTF-8'},close_fds=True,start_new_session=True)
            self.processes.append(p)
            return p
        return spawn

    def transport(self, factory, value=None, **kwargs):
        return SupervisedTransport(value or fixture(),workflow_identity=1,
                                   source_revision=REV,approved_revision=REV,
                                   worker_factory=factory,**kwargs)

    def run_worker(self, response, *, condition=(), connect=None):
        sock = Socket(response)
        emitted=[]
        cfg={'url':fixture().requests[0].source.descriptor.url,
             'api_version':'2022-11-28','accept':'application/vnd.github+json',
             'condition':[list(p) for p in condition],'token':SECRET.decode(),
             'connect_deadline':time.monotonic()+10,'request_deadline':time.monotonic()+30}
        _worker(cfg,lambda k,p:emitted.append((k,p)),connect=connect or (lambda timeout:sock))
        return sock,emitted

    def test_seven_planned_workers_finish_once_and_eighth_is_rejected(self):
        value = plan(tuple(Source(Descriptor(f'https://api.github.com/repositories/{100+n}/releases'),
                                  100+n, 'docs/track/release-catalog/research/fixture.md#id')
                           for n in range(7)), 1)
        transport = self.transport(self.factory(valid_frames()), value)
        class Clock:
            utcnow = staticmethod(lambda: datetime.now(timezone.utc))
            monotonic = staticmethod(time.monotonic)
        attempts, report = collect(value, transport, Clock(), Token(SECRET), workflow_identity=1)
        self.assertTrue(report['complete'])
        self.assertEqual(len(attempts), 7)
        self.assertEqual(len(self.processes), 7)
        self.assertTrue(all(a['body'] == b' []\n' and a['outcome'] == 'response' for a in attempts))
        with self.assertRaisesRegex(Refusal, 'unplanned_request'):
            list(transport.execute(value.requests[-1], Token(SECRET), limits()))
        self.assertEqual(len(self.processes), 7)
        with self.assertRaisesRegex(Refusal, 'source_count'):
            plan(tuple(r.source for r in value.requests) +
                 (Source(Descriptor('https://api.github.com/repositories/107/releases'),
                         107, 'docs/track/release-catalog/research/fixture.md#id'),), 1)

    def test_preflight_excludes_names_own_ids_and_unapproved_revisions(self):
        calls=[]
        factory=lambda:calls.append(True)
        named=plan((Source(Descriptor('https://api.github.com/repos/example/a/releases'),100,
                           'docs/track/release-catalog/research/fixture.md#id'),),1)
        for value in (named, replace(fixture(),workflow_repository_id=2)):
            with self.assertRaises(Refusal):
                self.transport(factory,value)
        with self.assertRaises(Refusal):
            SupervisedTransport(fixture(),workflow_identity=1,source_revision=REV,
                                approved_revision='b'*40,worker_factory=factory)
        self.assertEqual(calls,[])

    def test_real_process_framing_and_cleanup(self):
        transport=self.transport(self.factory(valid_frames()))
        events=list(transport.execute(fixture().requests[0],Token(SECRET),limits()))
        self.assertEqual([type(e) for e in events],[Connected,Headers,Chunk,End])
        self.assertEqual(events[2].data,b' []\n')
        self.assertEqual(self.processes[0].returncode,0)
        self.assertTrue(self.processes[0].stdout.closed)

    def test_collect_integration_and_transport_cannot_retry_same_request(self):
        class Clock:
            def utcnow(self):return datetime.now(timezone.utc)
            def monotonic(self):return time.monotonic()
        value=fixture()
        transport=self.transport(self.factory(valid_frames()),value)
        attempts,report=collect(value,transport,Clock(),Token(SECRET),workflow_identity=1)
        self.assertTrue(report['complete'])
        self.assertEqual(attempts[0]['body'],b' []\n')
        self.assertIsNotNone(attempts[0]['response_completed_at'])
        with self.assertRaises(Refusal):
            list(transport.execute(value.requests[0],Token(SECRET),limits()))
        self.assertEqual(len(self.processes),1)

    def test_conditional_collector_integration_requires_actual_sent_evidence(self):
        class Clock:
            def utcnow(self):return datetime.now(timezone.utc)
            def monotonic(self):return time.monotonic()
        source=fixture().requests[0].source
        prior=Prior(source.descriptor,b'[]',hashlib.sha256(b'[]').hexdigest(),
                    '2026-01-01T00:00:00+00:00',(('etag','fixture'),))
        value=plan((source,),1,{source.descriptor.request_id:prior})
        for condition,expected in [([['etag','fixture']],True),([],False)]:
            data=frame(b'C')+frame(b'H',_json({'status':304,'headers':QUOTA,'condition':condition}))+frame(b'E')
            transport=self.transport(self.factory(data),value)
            attempts,report=collect(value,transport,Clock(),Token(SECRET),workflow_identity=1)
            self.assertEqual(report['complete'],expected)
            if expected:self.assertEqual(attempts[0]['condition'],{'etag':'fixture'})
            else:self.assertEqual(report['stop_reason'],'protocol_refusal')

    def test_secret_bearing_spawn_exception_is_not_exposed(self):
        def fail():raise RuntimeError(SECRET.decode())
        try:
            list(self.transport(fail).execute(fixture().requests[0],Token(SECRET),limits()))
        except Refusal as error:
            self.assertNotIn(SECRET.decode(),''.join(traceback.format_exception(error)))
        else:self.fail('expected a fixed refusal')

    def test_hung_connection_and_body_are_killed_and_reaped(self):
        for data,request_timeout,connect_timeout in ((b'',2,.15),(frame(b'C'),.15,.15)):
            transport=self.transport(self.factory(data,hang=True))
            start=time.monotonic()
            with self.assertRaises(TimeoutError):
                list(transport.execute(fixture().requests[0],Token(SECRET),
                                       limits(request_timeout,connect=connect_timeout)))
            self.assertLess(time.monotonic()-start,1)
            self.assertIsNotNone(self.processes[-1].returncode)

    def test_trickle_pipe_does_not_reset_deadline(self):
        transport=self.transport(self.factory(valid_frames(),trickle=True))
        start=time.monotonic()
        with self.assertRaises(TimeoutError):
            list(transport.execute(fixture().requests[0],Token(SECRET),limits(.15)))
        self.assertLess(time.monotonic()-start,1)
        self.assertIsNotNone(self.processes[-1].returncode)

    def test_cancel_after_connected_reaps_worker(self):
        transport=self.transport(self.factory(frame(b'C'),hang=True))
        events=transport.execute(fixture().requests[0],Token(SECRET),limits())
        self.assertIsInstance(next(events),Connected)
        events.close()
        self.assertIsNotNone(self.processes[-1].returncode)
        self.assertTrue(self.processes[-1].stdin.closed)

    def test_slow_response_headers_do_not_extend_or_reuse_connect_deadline(self):
        data=valid_frames()
        connected=frame(b'C')
        code=('sys.stdout.buffer.write('+repr(connected)+');sys.stdout.buffer.flush();'
              'time.sleep(.4);sys.stdout.buffer.write('+repr(data[len(connected):])+');sys.stdout.buffer.flush()')
        transport=self.transport(self.factory(b'',code=code))
        events=list(transport.execute(fixture().requests[0],Token(SECRET),limits(2,connect=.3)))
        self.assertIsInstance(events[-1],End)

    def test_end_without_worker_exit_times_out(self):
        transport=self.transport(self.factory(valid_frames(),hang=True))
        with self.assertRaises(TimeoutError):
            list(transport.execute(fixture().requests[0],Token(SECRET),limits(.15)))
        self.assertIsNotNone(self.processes[-1].returncode)

    def test_invalid_frames_refuse_before_large_payload_allocation(self):
        cases=[FRAME.pack(b'H',FRAME_CAP+1),FRAME.pack(b'B',8193),frame(b'X'),
               frame(b'E'),frame(b'C')+frame(b'C'),frame(b'C')+frame(b'H',b'{'),
               valid_frames()+b'extra',frame(b'C')+frame(b'H',b'{"status":200,"status":200}'),
               frame(b'C')+FRAME.pack(b'H',20)+b'short']
        for data in cases:
            with self.subTest(length=len(data)),self.assertRaises(Refusal):
                list(self.transport(self.factory(data)).execute(fixture().requests[0],Token(SECRET),limits()))
            self.assertIsNotNone(self.processes[-1].returncode)

    def test_expired_or_tampered_limits_start_no_worker(self):
        calls=[]
        transport=self.transport(lambda:calls.append(True))
        for lim in [limits(-1), limits(31,connect=5), replace(limits(),body_bytes=BODY_CAP+1)]:
            with self.assertRaises((Refusal,TimeoutError)):
                list(transport.execute(fixture().requests[0],Token(SECRET),lim))
        self.assertEqual(calls,[])

    def test_isolated_spawn_has_no_ambient_auth_or_token_in_argv(self):
        with patch.dict(os.environ,{'GH_TOKEN':SECRET.decode(),'HTTPS_PROXY':'poison','HOME':'poison'}):
            with patch('supervised_transport.subprocess.Popen') as popen:
                _spawn()
        args,kwargs=popen.call_args
        self.assertNotIn(SECRET.decode(),repr(args))
        self.assertEqual(kwargs['env'],{'LANG':'C.UTF-8'})
        self.assertTrue(kwargs['close_fds'])
        self.assertIs(kwargs['stderr'],subprocess.DEVNULL)
        self.assertEqual(args[0][1:3],['-I','-S'])

    def test_internal_bootstrap_invalid_input_emits_only_fixed_failure(self):
        process=_spawn()  # no config/URL can reach the production connector
        self.processes.append(process)
        data=_json({'secret':SECRET.decode()})
        stdout,_=process.communicate(len(data).to_bytes(4,'big')+data,timeout=2)
        self.assertEqual(stdout,frame(b'F'))
        self.assertNotIn(SECRET,stdout)
        self.assertEqual(process.returncode,1)

    def test_worker_connect_event_precedes_send_and_secret_stays_in_request(self):
        sock=Socket(b'HTTP/1.1 200 OK\r\nContent-Length: 4\r\n\r\n []\n')
        emitted=[]
        def connector(timeout):
            self.assertEqual(emitted,[])
            self.assertEqual(sock.sent,b'')
            return sock
        cfg={'url':fixture().requests[0].source.descriptor.url,'api_version':'2022-11-28',
             'accept':'application/vnd.github+json','condition':[],'token':SECRET.decode(),
             'connect_deadline':time.monotonic()+10,'request_deadline':time.monotonic()+30}
        def emit(k,p):
            if k==b'C':self.assertEqual(sock.sent,b'')
            emitted.append((k,p))
        _worker(cfg,emit,connect=connector)
        self.assertEqual(b''.join(p for k,p in emitted if k==b'B'),b' []\n')
        self.assertIn(b'Authorization: Bearer '+SECRET,sock.sent)
        self.assertNotIn(SECRET,repr(emitted).encode())
        self.assertTrue(sock.closed)

    def test_chunked_entity_is_exact_and_condition_comes_from_sent_header(self):
        sock,events=self.run_worker(b'HTTP/1.1 200 OK\r\nTransfer-Encoding: chunked\r\n\r\n2\r\n[]\r\n1\r\n\n\r\n0\r\n\r\n',condition=(('etag','fixture-etag'),))
        self.assertEqual(b''.join(p for k,p in events if k==b'B'),b'[]\n')
        self.assertIn(b'If-None-Match: fixture-etag\r\n',sock.sent)
        header=json.loads(next(p for k,p in events if k==b'H'))
        self.assertEqual(header['condition'],[['etag','fixture-etag']])

    def test_worker_framing_and_header_bounds_refuse(self):
        cases=[b'HTTP/1.1 200 OK\r\nTransfer-Encoding: chunked\r\n\r\n'+b'1\r\nx\r\n'*13000+b'0\r\n\r\n',
               b'HTTP/1.1 200 OK\r\nTransfer-Encoding: chunked\r\n\r\n2\r\n[]XX0\r\n\r\n',
               b'HTTP/1.1 200 OK\r\nContent-Length: 4\r\n\r\nx',
               b'HTTP/1.1 200 OK\r\nContent-Length: 0\r\n',
               b'HTTP/1.1 200 OK\r\nContent-Encoding: gzip\r\n\r\n',
               b'HTTP/1.1 200 OK\r\nContent-Length: 0\r\nTransfer-Encoding: chunked\r\n\r\n',
               b'HTTP/1.1 200 OK\r\nContent-Length: 0\r\nContent-Length: 0\r\n\r\n',
               b'HTTP/1.1 200 OK\r\nTransfer-Encoding: chunked\r\n\r\n0\r\nX-Trailer: bad\r\n\r\n',
               b'HTTP/1.1 200 OK\r\nTransfer-Encoding: chunked\r\n\r\n2;x=y\r\n[]\r\n0\r\n\r\n',
               b'HTTP/1.1 200 OK\r\nX: '+b'x'*8193+b'\r\n\r\n',
               b'HTTP/1.1 200 OK\r\n'+b'X: '+b'y'*8000+b'\r\n'+(b'X: '+b'y'*8000+b'\r\n')*8+b'\r\n']
        for data in cases:
            with self.subTest(length=len(data)),self.assertRaises((Refusal,http.client.HTTPException)):
                self.run_worker(data)

    def test_malformed_headers_cannot_hide_framing(self):
        for fields in (b'Ignored line\r\nContent-Length: 10\r\n',
                       b'Content-Length : 10\r\n', b' Content-Length: 10\r\n',
                       b'X: value\r\n folded\r\n'):
            with self.subTest(fields=fields), self.assertRaises(Refusal):
                self.run_worker(b'HTTP/1.1 200 OK\r\n' + fields + b'\r\nx')
        _, events = self.run_worker(
            b'HTTP/1.1 100 Continue\r\nX: interim\r\n\r\n'
            b'HTTP/1.1 200 OK\r\nContent-Length: 2\r\n\r\n[]')
        self.assertEqual(events[-1], (b'E', b''))

    def test_body_cap_exact_and_overflow(self):
        _,events=self.run_worker(b'HTTP/1.1 200 OK\r\nContent-Length: 8000000\r\n\r\n'+b'x'*BODY_CAP)
        self.assertEqual(sum(len(p) for k,p in events if k==b'B'),BODY_CAP)
        with self.assertRaises(Refusal):
            self.run_worker(b'HTTP/1.1 200 OK\r\nContent-Length: 8000001\r\n\r\n'+b'x'*(BODY_CAP+1))

    def test_bounded_reader_limits_before_underlying_read(self):
        class Spy(io.BytesIO):
            def readline(self,n=-1):
                self.last=n
                return super().readline(n)
        stream=Spy(b'x'*100000)
        with self.assertRaises(Refusal):
            _BoundedReader(stream).readline(999999)
        self.assertLessEqual(stream.last,8193)
        with self.assertRaises(Refusal):
            _BoundedReader(stream).read(999999)


if __name__=='__main__':
    unittest.main()
