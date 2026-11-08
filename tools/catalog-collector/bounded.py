#!/usr/bin/env python3
"""Offline JSON-file adapter. No network I/O; elapsed checks are cooperative.

Trial limits only. Feed lazy responses into the existing atomic retention model.
Regular local files are trusted fixture inputs; this is not a hostile-file reader.
"""
import datetime
import json
import pathlib
import time
from retention import parameters, refresh

def require(ok, code):
    if not ok:
        raise ValueError(code)


MAX_INT = 9223372036854775807


def integer(value, minimum=0):
    if type(value) is not int or not minimum <= value <= MAX_INT:
        raise ValueError('integer')
    return value


def string(value):
    if not isinstance(value, str):
        raise ValueError('string')
    value.encode('utf-8')  # Reject unpaired JSON surrogate escapes.
    if any((ord(c) < 32 and c not in '\n\r\t') or
           (127 <= ord(c) <= 159 and c != '\u0085') or c in '\ufffe\uffff' for c in value):
        raise ValueError('unsupported control')
    return value


def timestamp(value):
    value = string(value)
    parsed = datetime.datetime.strptime(value, '%Y-%m-%dT%H:%M:%SZ')
    if parsed.year < 1970 or parsed.strftime('%Y-%m-%dT%H:%M:%SZ') != value:
        raise ValueError('timestamp')
    return value


def url(value):
    value = string(value)
    if not value.startswith('https://') or not value[8:].split('/')[0] or any(c.isspace() for c in value):
        raise ValueError('https URL')
    return value


def boolean(value):
    if type(value) is not bool:
        raise ValueError('boolean')
    return value


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('duplicate JSON key')
        result[key] = value
    return result


def normalize(raw, page_size, *, allow_missing_published=False):
    if not isinstance(raw, list) or len(raw) > page_size:
        raise ValueError('page shape')
    releases = {}
    seen = set()
    for release in raw:
        rid = str(integer(release['id'], 1))
        if rid in seen:
            raise ValueError('duplicate release ID')
        seen.add(rid)
        if boolean(release['draft']):
            continue
        facts = {'tag': string(release['tag_name'])}
        if release.get('name') is not None:
            facts['title'] = string(release['name'])
        facts['url'] = url(release['html_url'])
        for field in ('created_at', 'published_at', 'updated_at'):
            if release.get(field) is not None or (field == 'published_at' and not allow_missing_published):
                facts[field] = timestamp(release[field])
        facts['prerelease'] = boolean(release['prerelease'])
        for source, target in (('zipball_url', 'source_zip_url'), ('tarball_url', 'source_tar_url')):
            if release.get(source) is not None:
                facts[target] = url(release[source])
        assets = {}
        if not isinstance(release['assets'], list):
            raise ValueError('assets')
        for asset in release['assets']:
            aid = str(integer(asset['id'], 1))
            if aid in assets:
                raise ValueError('duplicate asset ID')
            item = dict(name=string(asset['name']), url=url(asset['browser_download_url']),
                        size=integer(asset['size']), content_type=string(asset['content_type']))
            if asset.get('digest') is not None:
                item['digest'] = string(asset['digest'])
            assets[aid] = item
        facts['assets'] = {aid: assets[aid] for aid in sorted(assets, key=int)}
        releases[rid] = facts
    return releases


class FixtureBudget:
    def __init__(self, requests=64, response_bytes=16*1024*1024,
                 total_bytes=96*1024*1024, seconds=120):
        if any(type(v) is not int or v < 1 for v in (requests, response_bytes, total_bytes)) or seconds <= 0:
            raise ValueError('budget')
        self.requests, self.response_bytes, self.total_bytes, self.seconds = requests, response_bytes, total_bytes, seconds
        self.started = time.monotonic()
        self.used_requests = self.used_bytes = 0

    def check(self):
        if time.monotonic() - self.started > self.seconds:
            raise TimeoutError('elapsed budget')

    def read(self, path):
        self.check()
        if self.used_requests >= self.requests:
            raise TimeoutError('request budget')
        self.used_requests += 1  # Failed opens count too.
        allowance = min(self.response_bytes, self.total_bytes - self.used_bytes)
        if allowance < 0:
            raise TimeoutError('byte budget')
        body = bytearray()
        with pathlib.Path(path).open('rb') as stream:
            while True:
                self.check()
                chunk = stream.read(min(65536, allowance - len(body) + 1))
                self.used_bytes += len(chunk)
                if not chunk:
                    break
                body.extend(chunk)
                if len(body) > allowance:
                    raise TimeoutError('byte budget')
        self.check()
        return body


def collect_files(previous, pages, *, attempted_at, page_size=100, page_limit=1,
                  reconcile=False, budget=None, **limits):
    """Pages contain path and explicit has_next; never infer EOF from list length.

    Pagination metadata is fixture input, not a Link-header implementation.
    One-byte overread detects overflow and is counted. JSON parse/normalization
    and merge may temporarily allocate above input bytes; no RSS claim is made.
    """
    parameters(page_size, page_limit)
    if reconcile and page_limit != 'all':
        raise ValueError('reconciliation requires all')
    budget = budget or FixtureBudget()
    def responses():
        for page in pages:
            start = time.monotonic()
            before = budget.used_bytes
            try:
                body = budget.read(page['path'])
                received = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
                raw = json.loads(body.decode('utf-8'), object_pairs_hook=unique_object,
                                 parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)))
                records = normalize(raw, page_size)
                has_next = boolean(page['has_next'])
                budget.check()
                yield dict(received_at=received, releases=records, has_next=has_next,
                           bytes=budget.used_bytes-before, seconds=time.monotonic()-start)
            except (TimeoutError, OSError, ValueError, TypeError, KeyError, RecursionError) as exc:
                reason = 'collection_limit' if isinstance(exc, TimeoutError) else 'transport' if isinstance(exc, OSError) else 'invalid_response'
                yield dict(error=reason, bytes=budget.used_bytes-before, seconds=time.monotonic()-start)
                return
    result = refresh(previous, responses(), attempted_at=attempted_at, page_size=page_size,
                     page_limit=page_limit, reconcile=reconcile, **limits)
    # Include merge/serialization elapsed time in the cooperative scope check.
    try:
        budget.check()
    except TimeoutError:
        result = refresh(previous, [dict(error='collection_limit')], attempted_at=attempted_at,
                         page_size=page_size, page_limit=page_limit, reconcile=reconcile)
    return result
