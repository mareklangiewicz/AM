"""Reviewed manifest loader; no network or credential access."""
import json
from collector import Descriptor, Source, SOURCE_CAP, plan, require


def load_manifest(raw, workflow_identity):
    require(type(raw) is bytes and len(raw) <= 64_000, 'invalid_manifest')
    def pairs(items):
        obj = {}
        for key, value in items:
            require(key not in obj, 'duplicate_manifest_key')
            obj[key] = value
        return obj
    def constant(_):
        raise ValueError('invalid_manifest_json')
    obj = json.loads(raw, object_pairs_hook=pairs, parse_constant=constant)
    require(type(obj) is dict and obj.get('schema') == 1 and
            type(obj.get('sources')) is list and len(obj['sources']) in (6, SOURCE_CAP), 'invalid_manifest')
    sources = []
    for row in obj['sources']:
        require(type(row) is dict and type(row.get('repository_id')) is int and
                row['repository_id'] > 0 and type(row.get('url')) is str and
                type(row.get('identity_evidence')) is str, 'unenrolled_source')
        desc = Descriptor(row['url'])
        require(desc.url.startswith(f'https://api.github.com/repositories/{row["repository_id"]}/releases'),
                'numeric_fetch_required')
        require(row.get('request_id') == desc.request_id, 'manifest_request_id_mismatch')
        require(type(row.get('aliases')) is list, 'invalid_aliases')
        sources.append(Source(desc, row['repository_id'], row['identity_evidence'],
                              tuple(row['aliases'])))
    return plan(tuple(sources), workflow_identity)

