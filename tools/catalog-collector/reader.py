"""Shared selective lookup policy. No IO, clock lookup or release selection."""
import re
from collector import Refusal, require, timestamp
from storage import content, digest, validate_index

CATALOG_REPOSITORY_ID = 1291019762
FRESHNESS_SECONDS = 48 * 60 * 60


class StaleObservation(Refusal):
    def __init__(self, acceptance):
        super().__init__('stale_acceptance_required')
        self.acceptance = acceptance


def select(index_raw, alias, commit, *, now, stale_acceptance=None):
    require(type(commit) is str and re.fullmatch('[0-9a-f]{40}', commit), 'commit_pin_required')
    index = validate_index(index_raw)
    require(index['workflow_repository_id'] == CATALOG_REPOSITORY_ID, 'catalog_identity_mismatch')
    current = timestamp(now)
    require(timestamp(index['generated_at']) <= current, 'future_publication')
    target = index['aliases'].get(alias)
    require(target is not None and target['active'] is True, 'alias_unavailable')
    rid = target['request_id']; entry = index['entries'][rid]
    require(entry['availability'] == 'available' and entry['observation'] is not None,
            'observation_unavailable')
    obs = entry['observation']
    age = (current - timestamp(obs['validated_at'])).total_seconds()
    require(age >= 0, 'future_observation')
    acceptance = {'commit': commit, 'request_id': rid, 'sha256': obs['sha256']}
    if age > FRESHNESS_SECONDS and stale_acceptance != acceptance:
        raise StaleObservation(acceptance)
    return entry, {'commit': commit, 'request_id': rid, 'sha256': obs['sha256'],
                   'bytes': obs['bytes'], 'received_at': obs['received_at'],
                   'validated_at': obs['validated_at'], 'age_seconds': age,
                   'stale_accepted': age > FRESHNESS_SECONDS, 'source_revision': index['collector_revision'],
                   'run': index['run'], 'scope': obs['scope']}


def verify_body(raw, entry):
    obs = entry['observation']
    require(type(raw) is bytes and len(raw) == obs['bytes'] and digest(raw) == obs['sha256'],
            'body_integrity')
    content(raw, entry['descriptor'])
    return raw
