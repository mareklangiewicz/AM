#!/usr/bin/env python3
"""Strict field checks and normalization of GitHub releases responses; no I/O."""
import datetime

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
