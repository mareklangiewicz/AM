"""Normalize hash-checked saved responses for offline selector/lifecycle tests."""
from datetime import datetime
import json
from bounded import normalize
from retention import refresh


def utc(value):
    return datetime.fromisoformat(value)


def merge_attempts(previous, pages, *, attempted_at, **options):
    responses = []
    for attempt, following in pages:
        assert attempt['outcome'] == 'response' and attempt['status'] == 200
        raw = attempt['body']
        responses.append(dict(received_at=utc(attempt['response_completed_at']).strftime('%Y-%m-%dT%H:%M:%SZ'),
            releases=normalize(json.loads(raw), options.get('page_size', 100)),
            has_next=following, bytes=len(raw), seconds=0))
    return refresh(previous, responses, attempted_at=attempted_at, **options)
