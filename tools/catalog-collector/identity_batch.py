"""Offline-prepared identity batch. Running live requires separate authorization."""
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import selectors
import re
import argparse
import subprocess
import time

CAP = 64_000



def fetch(url, out, deadline, *, validate_value, body_cap=64_000, token=None, curl="/usr/bin/curl"):
    if not (type(body_cap) is int and 0 < body_cap <= 8_000_000):
        raise ValueError("body_cap_refused")
    if not re.fullmatch(r"https://api\.github\.com/(?:repos/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+|repositories/[1-9][0-9]*/releases(?:/latest)?(?:\?(?:page|per_page)=[1-9][0-9]*(?:&(?:page|per_page)=[1-9][0-9]*)*)?)", url):
        raise ValueError("evidence_url_refused")
    seconds = min(30, deadline - time.monotonic())
    if seconds <= 0:
        raise ValueError("batch_deadline")
    out.mkdir()
    read_fd, write_fd = os.pipe()
    command = [curl, '-q', '--silent', '--noproxy', '*', '--proto', '=https',
               '--http1.1', '--max-redirs', '0', '--connect-timeout', '10',
               '--max-time', str(seconds), '--max-filesize', str(body_cap),
               '--header', 'Accept: application/vnd.github+json',
               '--header', 'X-GitHub-Api-Version: 2022-11-28',
               '--header', 'Accept-Encoding: identity',
               '--user-agent', 'AM-reviewed-identity-enrollment',
               '--dump-header', f'/dev/fd/{write_fd}', url]
    auth_fd = None
    if token is not None:
        if type(token) is not bytes or not re.fullmatch(rb'[A-Za-z0-9_.-]{1,4000}', token):
            os.close(read_fd)
            os.close(write_fd)
            raise ValueError('invalid_explicit_credential')
        auth_fd, auth_write = os.pipe()
        os.write(auth_write, b'Authorization: Bearer '+token+b'\n')
        os.close(auth_write)
        command[-1:-1] = ['--header', '@/dev/fd/'+str(auth_fd)]
    started_at = datetime.now(timezone.utc).isoformat()
    start = time.monotonic()
    end = min(deadline, start + seconds)
    buffers = {'headers': bytearray(), 'body': bytearray()}
    reason = None
    try:
        proc = subprocess.Popen(command, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                                stderr=subprocess.DEVNULL, env={'LANG': 'C.UTF-8'},
                                pass_fds=(write_fd,) if auth_fd is None else (write_fd, auth_fd), close_fds=True)
    except Exception:
        os.close(read_fd)
        raise
    finally:
        os.close(write_fd)
        if auth_fd is not None:
            os.close(auth_fd)
    sel = selectors.DefaultSelector()
    sel.register(read_fd, selectors.EVENT_READ, 'headers')
    sel.register(proc.stdout, selectors.EVENT_READ, 'body')
    try:
        while sel.get_map():
            remaining = end - time.monotonic()
            if remaining <= 0:
                reason = 'parent_deadline'
                break
            for key, _ in sel.select(remaining):
                target = buffers[key.data]
                cap = 64_000 if key.data == 'headers' else body_cap
                chunk = os.read(key.fd, min(8192, cap + 1 - len(target)))
                if not chunk:
                    sel.unregister(key.fileobj)
                    continue
                target.extend(chunk)
                if len(target) > cap:
                    reason = key.data + '_overflow'
                    break
            if reason:
                break
        if not reason:
            try:
                proc.wait(timeout=max(0.001, end - time.monotonic()))
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
    report = dict(url=url, authentication=token is not None, method='GET', redirects=False,
                  retries=0, started_at=started_at, completed_at=completed_at,
                  elapsed_seconds=elapsed, curl_exit=proc.returncode,
                  termination=reason, accepted=False,
                  headers_bytes=len(headers), body_bytes=len(body),
                  headers_sha256=hashlib.sha256(headers).hexdigest(),
                  body_sha256=hashlib.sha256(body).hexdigest())
    try:
        if reason or proc.returncode or time.monotonic() >= end:
            raise ValueError('incomplete_transport')
        # HTTP/1.1, direct HTTPS, no redirect following: exactly one final block.
        lines = headers.decode('iso-8859-1').split('\r\n')
        status = re.fullmatch(r'HTTP/1\.1 ([0-9]{3})(?: .*)?', lines[0])
        if status is not None:
            report['status'] = int(status.group(1))
        if headers.count(b'HTTP/1.1 ') != 1:
            raise ValueError('unexpected_status')
        if not headers.endswith(b'\r\n\r\n'):
            raise ValueError('incomplete_headers')
        public = {}
        framing = {}
        allowed = {'etag', 'last-modified', 'date', 'link', 'location', 'retry-after',
                   'content-type', 'content-length', 'x-ratelimit-limit',
                   'x-ratelimit-remaining', 'x-ratelimit-reset', 'x-ratelimit-used',
                   'x-ratelimit-resource'}
        for line in lines[1:]:
            if not line:
                continue
            if not re.fullmatch(r"[!#$%&'*+.^_`|~0-9A-Za-z-]+:[^\r\n]*", line):
                raise ValueError('invalid_header')
            name, value = line.split(':', 1)
            name, value = name.lower(), value.strip()
            if len(value.encode('iso-8859-1')) > 8192:
                raise ValueError('header_value_overflow')
            if name == 'content-encoding' and value.lower() != 'identity':
                raise ValueError('unexpected_encoding')
            if name in {'content-encoding', 'content-length', 'transfer-encoding'}:
                if name in framing:
                    raise ValueError('duplicate_framing')
                framing[name] = value
            if name in allowed:
                if name in public:
                    raise ValueError('duplicate_public_header')
                public[name] = value
        if framing.get('transfer-encoding') not in (None, 'chunked') or (
                'transfer-encoding' in framing and 'content-length' in framing):
            raise ValueError('ambiguous_framing')
        report['public_headers'] = public
        if 'content-length' in public and (not re.fullmatch(r'[0-9]{1,16}', public['content-length'])
                                           or int(public['content-length']) != len(body)):
            raise ValueError('incomplete_body')
        if report.get('status') != 200:
            raise ValueError('unexpected_status')
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
        report.update(validate_value(value, body))
        report['accepted'] = True
    except (ValueError, TypeError, KeyError, UnicodeError) as error:
        report['validation'] = 'refused'
        report['refusal'] = str(error)
    (out / 'headers.txt').write_bytes(headers)
    (out / 'body.json').write_bytes(body)
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    return report


def request(url, out, deadline, *, own_id, curl="/usr/bin/curl", token=None):
    expected_name = url.removeprefix("https://api.github.com/repos/")
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", expected_name):
        raise ValueError("identity_url_refused")
    if url != "https://api.github.com/repos/" + expected_name:
        raise ValueError("identity_url_refused")
    def validate_identity(value, body):
        if not (type(value) is dict and type(value.get('id')) is int and value['id'] > 0
                and type(value.get('full_name')) is str
                and value['full_name'].lower() == expected_name.lower()
                and value['id'] != own_id
                and value['full_name'].lower() != 'mareklangiewicz/am'
                and value.get('private') is False and value.get('visibility') == 'public'):
            raise ValueError('identity_mismatch')
        return dict(identity={k: value[k] for k in ('id', 'full_name', 'private', 'visibility')})
    return fetch(url, out, deadline, validate_value=validate_identity, curl=curl, token=token)


ROOT = Path(__file__).resolve().parents[2]
PAYLOAD = ROOT / "docs/track/release-catalog/research/remaining-appimage-preparation-20261102.json"
# Bound to the reviewed offline inventory, not arbitrary command-line URLs.
PAYLOAD_SHA256 = "5538f32fd32d3e3b5f6d545d6f72e9d5af77bc76a021e6b633c518571a2d7066"
BATCH_SECONDS = 1500
# Accepted run 41429379232, retained brave-live-20261102 archive/run.json.
OWN_REPOSITORY_ID = 1291019762


def load_payload(*, check_recipes=True):
    raw = PAYLOAD.read_bytes()
    if hashlib.sha256(raw).hexdigest() != PAYLOAD_SHA256:
        raise ValueError("payload_hash_mismatch")
    payload = json.loads(raw)
    urls = payload["identity_requests"]
    if len(urls) != 48 or len(set(urls)) != 48:
        raise ValueError("identity_scope_mismatch")
    for row in payload["rows"] if check_recipes else []:
        for recipe in row["recipes"]:
            if hashlib.sha256((ROOT / recipe["path"]).read_bytes()).hexdigest() != recipe["sha256"]:
                raise ValueError("recipe_changed: " + recipe["path"])
    return payload


def run_batch(payload, out, *, own_id, request_fn=request, monotonic=time.monotonic):
    if type(own_id) is not int or own_id <= 0:
        raise ValueError("own_repository_id_required")
    # Exclusive directory creation refuses repeats, including interrupted runs.
    out.mkdir()
    deadline = monotonic() + BATCH_SECONDS
    summary = dict(payload_sha256=PAYLOAD_SHA256, own_repository_id=own_id,
                   started_at=datetime.now(timezone.utc).isoformat(),
                   request_limit=48, batch_seconds=BATCH_SECONDS,
                   completed=[], accepted=False)
    summary_path = out / "batch.json"

    def save():
        temporary = out / "batch.json.tmp"
        temporary.write_text(json.dumps(summary, indent=2) + "\n")
        temporary.replace(summary_path)

    save()
    try:
        for index, url in enumerate(payload["identity_requests"]):
            if monotonic() >= deadline:
                raise ValueError("batch_deadline")
            report = request_fn(url, out / f"{index + 1:02d}", deadline, own_id=own_id)
            summary["completed"].append(dict(url=url, directory=f"{index + 1:02d}",
                                              accepted=report["accepted"]))
            save()
            if not report["accepted"]:
                raise ValueError("identity_refused")
        summary["accepted"] = True
    except Exception as error:
        summary["failure"] = type(error).__name__ + ": " + str(error)
    finally:
        summary["completed_at"] = datetime.now(timezone.utc).isoformat()
        save()
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--own-repository-id", type=int, default=OWN_REPOSITORY_ID)
    parser.add_argument("--execute-approved-identity-batch", action="store_true")
    args = parser.parse_args()
    payload = load_payload()
    if not args.execute_approved_identity_batch:
        print(json.dumps(dict(mode="offline-plan", payload_sha256=PAYLOAD_SHA256,
                              identity_requests=payload["identity_requests"]), indent=2))
        return 0
    if args.output is None or args.own_repository_id != OWN_REPOSITORY_ID:
        parser.error("execution requires fresh --output and the retained own repository ID")
    summary = run_batch(payload, args.output, own_id=args.own_repository_id)
    print(json.dumps(summary, indent=2))
    return 0 if summary["accepted"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
