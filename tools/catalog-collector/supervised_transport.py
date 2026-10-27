"""Numeric-ID HTTPS adapter. No live CLI or workflow wiring.

Only a reviewed caller can construct this transport; tests inject socket/worker
boundaries. The internal child bootstrap is private IPC, not an API collection CLI.
"""
import http.client
import json
import math
import os
from pathlib import Path
import re
import select
import socket
import ssl
import struct
import subprocess
import sys
import time

from collector import (BODY_CAP, HEADER_CAP, Chunk, Connected, End, Headers,
                       Limits, Refusal, require, selected_headers, validate_plan)

FRAME = struct.Struct('!cI')
FRAME_CAP = 100_000
CHUNK_CAP = 8192
BOOTSTRAP_CAP = 65_536


class Token:
    """Explicit bytes from a future trusted adapter, never ambient credentials."""
    __slots__ = ('_value',)

    def __init__(self, value):
        require(type(value) is bytes and 0 < len(value) <= 16_384 and
                re.fullmatch(rb'[A-Za-z0-9_.-]+', value), 'invalid_credential')
        self._value = value

    def __repr__(self):
        return '<opaque credential>'


def _json(value):
    return json.dumps(value, separators=(',', ':'), ensure_ascii=False).encode()


def _unique(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, 'invalid_frame')
        result[key] = value
    return result


def _decode(raw):
    try:
        return json.loads(raw, object_pairs_hook=_unique)
    except Exception:
        raise Refusal('invalid_frame') from None


def _spawn():
    directory = str(Path(__file__).resolve().parent)
    bootstrap = ('import sys;sys.path.insert(0,' + repr(directory) + ');'
                 'from supervised_transport import _worker_main;_worker_main()')
    return subprocess.Popen(
        [sys.executable, '-I', '-S', '-c', bootstrap], stdin=subprocess.PIPE,
        stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
        env={'LANG': 'C.UTF-8'}, close_fds=True, start_new_session=True)


class SupervisedTransport:
    def __init__(self, value, *, workflow_identity, source_revision, approved_revision,
                 worker_factory=_spawn, monotonic=time.monotonic):
        validate_plan(value, workflow_identity)
        require(type(source_revision) is str and
                re.fullmatch(r'[0-9a-f]{40}', source_revision) and
                source_revision == approved_revision, 'unapproved_revision')
        for request in value.requests:
            require(request.source.descriptor.url.startswith(
                f'https://api.github.com/repositories/{request.source.repository_id}/releases'),
                'numeric_fetch_required')
        self._plan, self._workflow = value, workflow_identity
        self._spawn, self._now, self._calls = worker_factory, monotonic, 0
        self._used = set()

    def execute(self, request, credential, limits):
        validate_plan(self._plan, self._workflow)
        require(request in self._plan.requests and self._calls < 6 and
                request.source.descriptor.request_id not in self._used, 'unplanned_request')
        require(type(credential) is Token and type(limits) is Limits, 'invalid_runtime_input')
        require(all(type(v) in (float, int) and math.isfinite(v) for v in
                    (limits.connect_deadline, limits.request_deadline, limits.batch_deadline))
                and limits.connect_deadline <= limits.request_deadline <= limits.batch_deadline
                and limits.body_bytes == BODY_CAP and limits.header_bytes == HEADER_CAP,
                'invalid_limits')
        now = self._now()
        require(limits.connect_deadline - now <= 10 and limits.request_deadline - now <= 30
                and limits.batch_deadline - now <= 300, 'invalid_limits')
        config = _json({'url': request.source.descriptor.url,
                        'api_version': request.source.descriptor.api_version,
                        'accept': request.source.descriptor.accept,
                        'condition': request.condition,
                        'token': credential._value.decode('ascii'),
                        'connect_deadline': limits.connect_deadline,
                        'request_deadline': limits.request_deadline})
        require(len(config) <= BOOTSTRAP_CAP, 'bootstrap_overflow')
        process, connected, headers_seen, body_bytes = None, False, False, 0

        def remaining():
            deadline = min(limits.request_deadline, limits.batch_deadline)
            if not connected:
                deadline = min(deadline, limits.connect_deadline)
            left = deadline - self._now()
            if left <= 0:
                raise TimeoutError('transport_deadline')
            return left

        def transfer(fd, data=None, count=0):
            buffer = bytearray()
            offset = 0
            target = len(data) if data is not None else count
            while offset < target:
                left = remaining()
                readable, writable, _ = select.select(
                    [fd] if data is None else [], [fd] if data is not None else [], [], left)
                remaining()
                if not readable and not writable:
                    raise TimeoutError('transport_deadline')
                try:
                    if data is None:
                        part = os.read(fd, min(CHUNK_CAP, target - offset))
                        require(bool(part), 'worker_eof')
                        buffer.extend(part)
                        offset += len(part)
                    else:
                        offset += os.write(fd, data[offset:offset + 4096])
                except BlockingIOError:
                    continue
            return bytes(buffer)

        remaining()  # stale limits must not create a process
        try:
            self._calls += 1
            self._used.add(request.source.descriptor.request_id)
            process = self._spawn()
            os.set_blocking(process.stdin.fileno(), False)
            os.set_blocking(process.stdout.fileno(), False)
            transfer(process.stdin.fileno(), struct.pack('!I', len(config)) + config)
            process.stdin.close()
            config = b''
            while True:
                kind, length = FRAME.unpack(transfer(process.stdout.fileno(), count=FRAME.size))
                require(kind in (b'C', b'H', b'B', b'E', b'F'), 'invalid_frame')
                require(length <= (CHUNK_CAP if kind == b'B' else FRAME_CAP), 'frame_overflow')
                require(kind in (b'H', b'B') or length == 0, 'invalid_frame')
                payload = transfer(process.stdout.fileno(), count=length)
                if kind == b'C':
                    require(not connected and not headers_seen, 'invalid_frame_order')
                    connected = True
                    yield Connected()
                elif kind == b'H':
                    require(connected and not headers_seen, 'invalid_frame_order')
                    obj = _decode(payload)
                    require(type(obj) is dict and set(obj) == {'status', 'headers', 'condition'},
                            'invalid_frame')
                    require(type(obj['status']) is int and 200 <= obj['status'] <= 599 and
                            type(obj['headers']) is list and type(obj['condition']) is list,
                            'invalid_frame')
                    require(all(type(p) is list and len(p) == 2 for p in obj['headers'] + obj['condition']),
                            'invalid_frame')
                    values = tuple(tuple(p) for p in obj['headers'])
                    sent = tuple(tuple(p) for p in obj['condition'])
                    require(sent == request.condition, 'conditional_evidence_mismatch')
                    public = selected_headers(values)
                    headers_seen = True
                    yield Headers(obj['status'], tuple(public.items()), sent)
                elif kind == b'B':
                    require(headers_seen and length > 0, 'invalid_frame_order')
                    body_bytes += length
                    require(body_bytes <= BODY_CAP, 'body_overflow')
                    yield Chunk(payload)
                elif kind == b'E':
                    require(headers_seen, 'invalid_frame_order')
                    # A worker must exit cleanly, not send End and remain hung.
                    try:
                        status = process.wait(timeout=remaining())
                    except subprocess.TimeoutExpired:
                        raise TimeoutError('transport_deadline') from None
                    remaining()
                    require(status == 0, 'worker_exit')
                    require(not os.read(process.stdout.fileno(), 1), 'trailing_frame')
                    yield End()
                    return
                else:
                    raise Refusal('worker_refusal')
        except TimeoutError:
            raise TimeoutError('transport_deadline') from None
        except Exception:
            raise Refusal('transport_refusal') from None
        finally:
            config = b''
            if process is not None:
                try:
                    if process.poll() is None:
                        process.kill()
                    process.wait(timeout=1)
                finally:
                    for pipe in (process.stdin, process.stdout):
                        if pipe is not None:
                            pipe.close()


class _BoundedReader:
    """Cap reads before HTTPResponse/email parsing; body framing is strict too."""
    def __init__(self, stream):
        self.stream, self.headers, self.header_bytes, self.framing_bytes = stream, True, 0, 0
        self.last_header_line = None
        self.chunked, self.chunk_remaining, self.delimiter = False, None, False

    def readline(self, size=-1):
        remaining = HEADER_CAP - (self.header_bytes if self.headers else self.framing_bytes)
        limit = min(CHUNK_CAP + 1, remaining + 1, size if size >= 0 else CHUNK_CAP + 1)
        require(limit > 0, 'header_overflow')
        line = self.stream.readline(limit)
        require(len(line) <= CHUNK_CAP and len(line) <= remaining, 'header_overflow')
        require(not line or line.endswith(b'\r\n'), 'unsupported_framing')
        if self.headers:
            self.header_bytes += len(line)
            self.last_header_line = line
        else:
            self.framing_bytes += len(line)
            # Deliberately reject chunk extensions and nonempty trailers.
            require(line == b'\r\n' or re.fullmatch(rb'[0-9a-fA-F]{1,16}\r\n', line),
                    'unsupported_framing')
            if self.chunked:
                require(not self.delimiter, 'unsupported_framing')
                self.chunk_remaining = int(line.strip(), 16) if line != b'\r\n' else None
        return line

    def read(self, size=-1):
        require(0 <= size <= CHUNK_CAP, 'unbounded_read')
        data = self.stream.read(size)
        if self.chunked:
            if self.delimiter:
                require(size == 2 and data == b'\r\n', 'unsupported_framing')
                self.framing_bytes += len(data)
                require(self.framing_bytes <= HEADER_CAP, 'header_overflow')
                self.delimiter = False
                self.chunk_remaining = None
            else:
                require(self.chunk_remaining is not None and len(data) <= self.chunk_remaining,
                        'unsupported_framing')
                self.chunk_remaining -= len(data)
                self.delimiter = self.chunk_remaining == 0
        return data

    def flush(self):
        self.stream.flush()

    def close(self):
        self.stream.close()


class _ResponseSocket:
    def __init__(self, reader):
        self.reader = reader

    def makefile(self, mode):
        require(mode == 'rb', 'invalid_socket_mode')
        return self.reader


def _https_connect(timeout):
    raw = socket.create_connection(('api.github.com', 443), timeout=timeout)
    try:
        return ssl.create_default_context().wrap_socket(raw, server_hostname='api.github.com')
    except Exception:
        raw.close()
        raise


def _worker(config, emit, *, connect=_https_connect, monotonic=time.monotonic):
    """One direct HTTPS transaction; injectable socket for offline checks."""
    connection, response = None, None
    try:
        require(type(config) is dict and set(config) == {
            'url', 'api_version', 'accept', 'condition', 'token', 'connect_deadline', 'request_deadline'},
            'invalid_bootstrap')
        token = Token(config['token'].encode('ascii'))
        from collector import Descriptor
        match = re.fullmatch(r'https://api\.github\.com/repositories/([1-9][0-9]*)/releases.*', config['url'])
        require(match is not None, 'numeric_fetch_required')
        desc = Descriptor(config['url'], config['api_version'], config['accept'])
        desc.validate(int(match.group(1)))
        require(type(config['condition']) is list and len(config['condition']) <= 2, 'invalid_condition')
        sent, names = [], set()
        for item in config['condition']:
            require(type(item) is list and len(item) == 2, 'invalid_condition')
            k, v = item
            require(k in {'etag', 'last-modified'} and k not in names and type(v) is str and
                    0 < len(v.encode()) <= 8192 and '\r' not in v and '\n' not in v, 'invalid_condition')
            sent.append((k, v)); names.add(k)
        require(all(type(config[k]) in (float, int) and math.isfinite(config[k])
                    for k in ('connect_deadline', 'request_deadline')), 'invalid_limits')
        remaining = min(config['connect_deadline'], config['request_deadline']) - monotonic()
        require(remaining > 0, 'expired_deadline')
        connection = connect(remaining)
        emit(b'C', b'')  # only after the actual injected DNS/TCP/TLS connector returns
        require(monotonic() < config['request_deadline'], 'expired_deadline')
        connection.settimeout(config['request_deadline'] - monotonic())
        path = desc.url.removeprefix('https://api.github.com')
        lines = [('Host', 'api.github.com'), ('User-Agent', 'AM-restricted-collector'),
                 ('Accept', desc.accept), ('X-GitHub-Api-Version', desc.api_version),
                 ('Accept-Encoding', 'identity'), ('Connection', 'close'),
                 ('Authorization', 'Bearer ' + token._value.decode('ascii'))]
        names_map = {'etag': 'If-None-Match', 'last-modified': 'If-Modified-Since'}
        lines += [(names_map[k], v) for k, v in sent]
        wire = ('GET ' + path + ' HTTP/1.1\r\n' +
                ''.join(k + ': ' + v + '\r\n' for k, v in lines) + '\r\n').encode('latin-1')
        connection.sendall(wire)
        wire, lines = b'', []
        reader = _BoundedReader(connection.makefile('rb'))
        response = http.client.HTTPResponse(_ResponseSocket(reader), method='GET')
        response.begin()
        require(reader.last_header_line == b'\r\n', 'truncated_headers')
        reader.headers = False
        values = tuple(response.getheaders())
        encoding = [v.lower().strip() for k, v in values if k.lower() == 'content-encoding']
        transfer = [v.lower().strip() for k, v in values if k.lower() == 'transfer-encoding']
        length = [v for k, v in values if k.lower() == 'content-length']
        require(encoding in ([], ['identity']) and transfer in ([], ['chunked']) and
                len(length) <= 1 and not (transfer and length), 'unsupported_framing')
        require(not length or re.fullmatch(r'[0-9]{1,16}', length[0]), 'unsupported_framing')
        require(200 <= response.status <= 599, 'unsupported_status')
        require(response.status == 304 or not length or int(length[0]) <= BODY_CAP, 'body_overflow')
        reader.chunked = transfer == ['chunked']
        public = selected_headers(values)
        emit(b'H', _json({'status': response.status, 'headers': list(public.items()), 'condition': sent}))
        total = 0
        while True:
            chunk = response.read(min(CHUNK_CAP, BODY_CAP - total + 1))
            require(total + len(chunk) <= BODY_CAP, 'body_overflow')
            if not chunk:
                break
            total += len(chunk)
            emit(b'B', chunk)
        require(response.status == 304 or not length or int(length[0]) == total,
                'truncated_response')
        emit(b'E', b'')
    finally:
        try:
            if response is not None:
                response.close()
        finally:
            if connection is not None:
                connection.close()


def _worker_main():
    """Private process bootstrap; deliberately no __main__ / public live CLI."""
    def exact(count):
        data = sys.stdin.buffer.read(count)
        require(len(data) == count, 'bootstrap_eof')
        return data

    def emit(kind, payload):
        require(len(payload) <= (CHUNK_CAP if kind == b'B' else FRAME_CAP), 'frame_overflow')
        sys.stdout.buffer.write(FRAME.pack(kind, len(payload)) + payload)
        sys.stdout.buffer.flush()

    try:
        length = struct.unpack('!I', exact(4))[0]
        require(0 < length <= BOOTSTRAP_CAP, 'bootstrap_overflow')
        config = _decode(exact(length))
        _worker(config, emit)
    except BaseException:
        # Do not print exception strings, request headers or tracebacks.
        try:
            emit(b'F', b'')
        except BaseException:
            pass
        raise SystemExit(1) from None
