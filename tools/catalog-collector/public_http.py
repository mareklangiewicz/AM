"""Unauthenticated bounded public catalog GETs through isolated system curl.

POSIX/Linux client transport; fixed hosts/paths only. No token/config discovery.
"""
import os
import re
import select
import subprocess
import time

from collector import HEADER_CAP, Refusal, require, selected_headers

REF_URL = 'https://api.github.com/repos/mareklangiewicz/AM/git/ref/heads/release-catalog'
RAW_ROOT = 'https://raw.githubusercontent.com/mareklangiewicz/AM/'


def allowed(url):
    return type(url) is str and (url == REF_URL or re.fullmatch(
        re.escape(RAW_ROOT)+r'[0-9a-f]{40}/(?:index\.json|bodies/[0-9a-f]{64}\.json)', url))


def get(url, cap, deadline, *, monotonic=time.monotonic, spawn=subprocess.Popen):
    require(allowed(url) and type(cap) is int and 0 < cap <= 8_000_000, 'catalog_request_refused')
    remaining = deadline - monotonic()
    require(0 < remaining <= 90, 'catalog_deadline')
    seconds = min(30, remaining)
    command = ['/usr/bin/curl', '-q', '--silent', '--show-error', '--http1.1', '--include',
        '--noproxy', '*', '--proto', '=https', '--max-redirs', '0',
        '--connect-timeout', str(min(10, seconds)), '--max-time', str(seconds),
        '--max-filesize', str(cap), '--header', 'Accept-Encoding: identity',
        '--header', 'Accept: application/vnd.github+json' if url == REF_URL else 'Accept: application/octet-stream',
        '--header', 'X-GitHub-Api-Version: 2022-11-28', '--user-agent', 'AM-catalog-consumer', url]
    process = None
    body, pending = bytearray(), bytearray()
    header_bytes, headers_done, public = 0, False, {}
    end = min(deadline, monotonic()+seconds)
    try:
        process = spawn(command, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                        stderr=subprocess.DEVNULL, close_fds=True,
                        env={'PATH':'/usr/bin:/bin', 'LANG':'C.UTF-8'})
        os.set_blocking(process.stdout.fileno(), False)
        while True:
            left = end-monotonic()
            require(left > 0, 'catalog_deadline')
            ready, _, _ = select.select([process.stdout], [], [], left)
            require(ready and monotonic() < end, 'catalog_deadline')
            chunk = os.read(process.stdout.fileno(), 8192)
            if not chunk:
                break
            if not headers_done:
                pending.extend(chunk)
                while not headers_done:
                    offset = pending.find(b'\r\n\r\n')
                    if offset < 0:
                        require(header_bytes+len(pending) <= HEADER_CAP, 'catalog_header_bound')
                        break
                    block = bytes(pending[:offset+4]); del pending[:offset+4]
                    header_bytes += len(block)
                    require(header_bytes <= HEADER_CAP, 'catalog_header_bound')
                    lines = block[:-4].split(b'\r\n')
                    require(all(len(line) <= 8192 for line in lines), 'catalog_header_bound')
                    status = re.fullmatch(rb'HTTP/1\.[01] ([0-9]{3})(?: .*)?', lines[0])
                    require(status is not None, 'catalog_header_refusal')
                    status = int(status.group(1)); pairs=[]
                    for line in lines[1:]:
                        require(re.fullmatch(rb"[!#$%&'*+.^_`|~0-9A-Za-z-]+:[^\r\n]*", line),
                                'catalog_header_refusal')
                        key,value=line.split(b':',1)
                        pairs.append((key.decode('ascii'),value.strip(b' \t').decode('latin-1')))
                    public = selected_headers(tuple(pairs))
                    if 100 <= status < 200:
                        continue
                    require(status == 200, 'catalog_http_refusal')
                    encoding=[v.lower() for k,v in pairs if k.lower()=='content-encoding']
                    transfer=[v.lower() for k,v in pairs if k.lower()=='transfer-encoding']
                    length=[v for k,v in pairs if k.lower()=='content-length']
                    require(encoding in ([],['identity']) and transfer in ([],['chunked']) and
                            len(length) <= 1 and not (transfer and length), 'catalog_framing_refusal')
                    require(not length or re.fullmatch('[0-9]{1,16}',length[0]) and int(length[0]) <= cap,
                            'catalog_body_bound')
                    headers_done=True
                    chunk=bytes(pending);pending.clear()
                if not headers_done:
                    continue
            require(len(body)+len(chunk) <= cap, 'catalog_body_bound')
            body.extend(chunk)
        require(headers_done and process.wait(timeout=max(.001,end-monotonic())) == 0
                and monotonic() < end, 'catalog_transport_refusal')
        require('content-length' not in public or int(public['content-length']) == len(body),
                'catalog_truncated_body')
        return bytes(body)
    except Refusal:
        raise
    except Exception:
        raise Refusal('catalog_transport_refusal') from None
    finally:
        if process is not None:
            if process.poll() is None:
                process.kill()
            process.wait(timeout=1)
            process.stdout.close()
