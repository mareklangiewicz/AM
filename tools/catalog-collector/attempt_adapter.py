"""Candidate bridge from completed collector attempts to retained YAML facts.

No transport. The caller supplies explicit has_next alongside each attempt;
actual Link validation/pagination scheduling are not implemented here.
"""
import datetime
import json

from bounded import boolean, normalize, unique_object
from retention import refresh
from yaml_publication import load_local, publish_local


def utc(value):
    parsed = datetime.datetime.fromisoformat(value)
    if parsed.utcoffset() != datetime.timedelta(0):
        raise ValueError('UTC receipt required')
    return parsed


def merge_attempts(previous, pages, *, attempted_at, **options):
    """Use collector body/outcome/identity and response_completed_at unchanged in meaning."""
    page_size = options.get('page_size',100)
    def responses():
        for attempt, has_next in pages:
            raw = attempt['body']
            size = len(raw)
            try:
                if (attempt['repository_id'] != previous['repository_id'] or
                        attempt['descriptor']['url'].split('?',1)[0] !=
                        f'https://api.github.com/repositories/{previous["repository_id"]}/releases'):
                    raise ValueError('list identity')
                if attempt['outcome'] != 'response':
                    yield dict(error='transport',bytes=size,seconds=0)
                    return
                if (attempt['status'] == 429 or
                        attempt['status'] == 403 and attempt.get('headers',{}).get('x-ratelimit-remaining') == '0'):
                    yield dict(error='rate_limited',bytes=size,seconds=0)
                    return
                # 304 lacks the fetched release membership needed to reobserve
                # a partial retained set. No implicit reuse of all retained facts.
                if attempt['status'] != 200:
                    raise ValueError('complete 200 body required')
                received = utc(attempt['response_completed_at'])
                duration = (received-utc(attempt['request_started_at'])).total_seconds()
                if duration < 0:
                    raise ValueError('response chronology')
                value = json.loads(raw.decode('utf-8'),object_pairs_hook=unique_object,
                                   parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)))
                records = normalize(value,page_size)
                response = dict(received_at=received.strftime('%Y-%m-%dT%H:%M:%SZ'),
                                releases=records,has_next=boolean(has_next),
                                bytes=size,seconds=duration)
            except (ValueError,TypeError,KeyError,UnicodeError,RecursionError):
                yield dict(error='invalid_response',bytes=size,seconds=0)
                return
            yield response
    return refresh(previous,responses(),attempted_at=attempted_at,**options)


def refresh_from_attempts(repo, commit, pages, *, attempted_at, schema,
                          max_file_bytes, **options):
    apps, repositories = load_local(repo,commit,max_file_bytes=max_file_bytes)
    if any(rid not in repositories for rid in pages):
        raise ValueError('unknown selected repository')
    for rid, attempts in pages.items():
        repositories[rid] = merge_attempts(repositories[rid],attempts,attempted_at=attempted_at,
                                          max_catalog_bytes=max_file_bytes,**options)
    return publish_local(repo,apps,repositories,schema=schema,
                         max_file_bytes=max_file_bytes,expected_parent=commit)
