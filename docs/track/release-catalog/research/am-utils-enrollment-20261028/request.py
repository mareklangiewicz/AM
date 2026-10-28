"""One approved bounded public identity GET; never retries or follows redirects."""
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import selectors
import shutil
import subprocess
import time

URL = 'https://api.github.com/repos/ivan-hc/am-utils'
CAP = 64_000
OUT = Path(__file__).resolve().parent


def main():
    # Existing evidence prevents accidental repeat execution.
    if (OUT / 'report.json').exists():
        raise SystemExit('refusing_repeat')
    curl = shutil.which('curl')
    if not curl:
        raise SystemExit('curl_unavailable')
    read_fd, write_fd = os.pipe()
    command = [curl, '-q', '--silent', '--noproxy', '*', '--proto', '=https',
               '--http1.1', '--max-redirs', '0', '--connect-timeout', '10',
               '--max-time', '30', '--max-filesize', str(CAP),
               '--header', 'Accept: application/vnd.github+json',
               '--header', 'X-GitHub-Api-Version: 2022-11-28',
               '--header', 'Accept-Encoding: identity',
               '--user-agent', 'AM-reviewed-identity-enrollment',
               '--dump-header', f'/dev/fd/{write_fd}', URL]
    started_at = datetime.now(timezone.utc).isoformat()
    start = time.monotonic()
    buffers = {'headers': bytearray(), 'body': bytearray()}
    reason = None
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                            env={'LANG': 'C.UTF-8'}, pass_fds=(write_fd,), close_fds=True)
    os.close(write_fd)
    sel = selectors.DefaultSelector()
    sel.register(read_fd, selectors.EVENT_READ, 'headers')
    sel.register(proc.stdout, selectors.EVENT_READ, 'body')
    try:
        while sel.get_map():
            remaining = start + 30 - time.monotonic()
            if remaining <= 0:
                reason = 'parent_deadline'
                break
            for key, _ in sel.select(remaining):
                target = buffers[key.data]
                chunk = os.read(key.fd, min(8192, CAP + 1 - len(target)))
                if not chunk:
                    sel.unregister(key.fileobj)
                    continue
                target.extend(chunk)
                if len(target) > CAP:
                    reason = key.data + '_overflow'
                    break
            if reason:
                break
        if not reason:
            try:
                proc.wait(timeout=max(0.001, start + 30 - time.monotonic()))
            except subprocess.TimeoutExpired:
                reason = 'parent_deadline'
    finally:
        if proc.poll() is None:
            proc.kill()
        proc.wait()
        sel.close()
        os.close(read_fd)
        proc.stdout.close()
    completed_at = datetime.now(timezone.utc).isoformat()
    elapsed = time.monotonic() - start
    headers, body = bytes(buffers['headers']), bytes(buffers['body'])
    report = dict(url=URL, authentication=False, method='GET', redirects=False,
                  retries=0, started_at=started_at, completed_at=completed_at,
                  elapsed_seconds=elapsed, curl_exit=proc.returncode,
                  termination=reason, accepted=False,
                  headers_bytes=len(headers), body_bytes=len(body),
                  headers_sha256=hashlib.sha256(headers).hexdigest(),
                  body_sha256=hashlib.sha256(body).hexdigest())
    try:
        if reason or proc.returncode or elapsed >= 30:
            raise ValueError('incomplete_transport')
        # HTTP/1.1, direct HTTPS, no redirect following: exactly one final block.
        lines = headers.decode('iso-8859-1').split('\r\n')
        if not lines[0].startswith('HTTP/1.1 200 ') or headers.count(b'HTTP/1.1 ') != 1:
            raise ValueError('unexpected_status')
        report['status'] = 200
        public = {}
        allowed = {'etag', 'last-modified', 'date', 'link', 'location', 'retry-after',
                   'content-type', 'content-length', 'x-ratelimit-limit',
                   'x-ratelimit-remaining', 'x-ratelimit-reset', 'x-ratelimit-used',
                   'x-ratelimit-resource'}
        for line in lines[1:]:
            if not line:
                continue
            name, value = line.split(':', 1)
            name, value = name.lower(), value.strip()
            if len(value.encode('iso-8859-1')) > 8192:
                raise ValueError('header_value_overflow')
            if name == 'content-encoding' and value.lower() != 'identity':
                raise ValueError('unexpected_encoding')
            if name in allowed:
                if name in public:
                    raise ValueError('duplicate_public_header')
                public[name] = value
        report['public_headers'] = public
        if 'content-length' in public and int(public['content-length']) != len(body):
            raise ValueError('incomplete_body')
        def unique(pairs):
            obj = {}
            for key, value in pairs:
                if key in obj:
                    raise ValueError('duplicate_json_key')
                obj[key] = value
            return obj
        def constant(_):
            raise ValueError('invalid_json_constant')
        value = json.loads(body, object_pairs_hook=unique, parse_constant=constant)
        if not (type(value) is dict and type(value.get('id')) is int and value['id'] > 0
                and type(value.get('full_name')) is str
                and value['full_name'].lower() == 'ivan-hc/am-utils'
                and value.get('private') is False and value.get('visibility') == 'public'):
            raise ValueError('identity_mismatch')
        report['identity'] = {k: value[k] for k in ('id', 'full_name', 'private', 'visibility')}
        report['accepted'] = True
    except (ValueError, TypeError, KeyError, UnicodeError):
        report['validation'] = 'refused'
    (OUT / 'headers.txt').write_bytes(headers)
    (OUT / 'body.json').write_bytes(body)
    (OUT / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))
    return 0 if report['accepted'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
