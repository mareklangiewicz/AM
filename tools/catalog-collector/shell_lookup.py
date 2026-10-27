"""Derived inert TSV for the shell reader; index.json remains canonical."""
from datetime import datetime, timezone
from collector import require, timestamp
from storage import digest

LOOKUP_CAP = 2_000_000


def epoch(value):
    delta = timestamp(value) - datetime(1970, 1, 1, tzinfo=timezone.utc)
    return f'{delta.days * 86400 + delta.seconds}.{delta.microseconds:06d}'


def render(index, index_raw):
    rows = [['AM-CATALOG', '1', epoch(index['generated_at']),
             index['collector_revision'], index['run']['id'], index['run']['attempt'],
             digest(index_raw)]]
    for alias, target in sorted(index['aliases'].items()):
        entry = index['entries'][target['request_id']]
        obs = entry['observation']
        rows.append([alias, str(int(target['active'])), entry['availability'], target['request_id'],
                     obs['sha256'] if obs else '-', str(obs['bytes']) if obs else '-',
                     epoch(obs['received_at']) if obs else '-',
                     epoch(obs['validated_at']) if obs else '-',
                     entry['descriptor']['url'], entry['descriptor']['api_version'],
                     entry['descriptor']['accept'], str(entry['repository_id']),
                     obs['scope'] if obs else '-'])
    require(all(type(field) is str and field and
                all(32 <= ord(c) < 127 for c in field) for row in rows for field in row),
            'unsafe_lookup_field')
    raw = ('\n'.join('\t'.join(row) for row in rows) + '\n').encode('ascii')
    require(len(raw) <= LOOKUP_CAP, 'lookup_bound')
    return raw
