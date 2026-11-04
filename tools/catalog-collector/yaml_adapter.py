"""Format-2 source candidate; no CLI, token lookup, workflow or remote publication.

The first bridge executes the agreed one-page scheduled scope using the existing
collector. Multi-page scheduling is deliberately not implemented by this entry
point. Reader, normalization and retained merge are shared with the YAML candidate.
"""
from pathlib import Path
import re
import sys
from urllib.parse import parse_qsl, urlsplit

from collector import Descriptor, Source, collect, plan, require
from manifest import load_manifest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'catalog-yaml-prototype'))
from attempt_adapter import merge_attempts
from retention import parameters
from yaml_publication import candidate_tree


def list_url(repository_id, page_size, page=1):
    return (f'https://api.github.com/repositories/{repository_id}/releases'
            f'?per_page={page_size}&page={page}')


def list_plan(raw, workflow_identity, *, sources=None, page_size=100):
    """Deduplicate enrolled endpoint variants by numeric identity, without priors."""
    parameters(page_size, 1)
    enrolled = load_manifest(raw, workflow_identity)
    by_id = {}
    for request in enrolled.requests:
        source = request.source
        by_id.setdefault(str(source.repository_id), source)
    selected = list(by_id) if sources is None else list(sources)
    require(bool(selected) and len(set(selected)) == len(selected)
            and all(rid in by_id for rid in selected), 'invalid_source_subset')
    return plan(tuple(Source(Descriptor(list_url(by_id[rid].repository_id, page_size)),
                             by_id[rid].repository_id, by_id[rid].identity_evidence)
                      for rid in selected), workflow_identity)


def has_next(attempt, *, page_size, page=1):
    """Accept GitHub list Link framing, checking every target against this source.

    No links are followed here. Unknown relations, duplicate parameters/relations,
    route switches and inconsistent page numbers refuse the observation.
    """
    base = f'https://api.github.com/repositories/{attempt["repository_id"]}/releases'
    require(attempt['descriptor']['url'] == list_url(attempt['repository_id'], page_size, page),
            'unexpected_list_request')
    link = attempt.get('headers', {}).get('link')
    if link is None:
        return False
    require(isinstance(link, str) and bool(link), 'invalid_pagination')
    relations = {}
    for item in link.split(','):
        match = re.fullmatch(r'\s*<([^<>]+)>;\s*rel="(next|prev|first|last)"\s*', item)
        require(match is not None, 'invalid_pagination')
        target, relation = match.groups()
        require(relation not in relations, 'invalid_pagination')
        parts = urlsplit(target)
        require(target.split('?', 1)[0] == base and not parts.fragment, 'invalid_pagination')
        pairs = parse_qsl(parts.query, keep_blank_values=True, strict_parsing=True)
        query = dict(pairs)
        require(len(pairs) == 2 and len(query) == 2 and set(query) == {'page', 'per_page'}
                and query['per_page'] == str(page_size)
                and re.fullmatch('[1-9][0-9]{0,18}', query['page']), 'invalid_pagination')
        number = int(query['page'])
        require((relation == 'next' and number == page + 1)
                or (relation == 'prev' and page > 1 and number == page - 1)
                or (relation == 'first' and number == 1)
                or (relation == 'last' and number >= page), 'invalid_pagination')
        relations[relation] = number
    require('last' not in relations or relations['last'] == page or 'next' in relations,
            'invalid_pagination')
    require('next' not in relations or 'last' not in relations
            or relations['last'] >= relations['next'], 'invalid_pagination')
    return 'next' in relations


def schema_url(revision):
    require(isinstance(revision, str) and re.fullmatch('[0-9a-f]{40}', revision),
            'invalid_source_revision')
    return ('https://raw.githubusercontent.com/mareklangiewicz/AM/' + revision
            + '/docs/catalog-format-v2.md')


def collect_one_page(value, transport, clock, credential, *, workflow_identity,
                     apps, repositories, source_revision, max_file_bytes):
    """Return a validated candidate tree and report; never publish it.

    Caller loads previous state at an exact pin (load_local) or supplies reviewed
    bootstrap identities/app enrollment. No new aliases or names are inferred.
    File allowance is explicit and remains a caller policy decision.
    """
    schema = schema_url(source_revision)
    # Validate all prior state/app references before invoking transport.
    candidate_tree(apps, repositories, schema=schema, max_file_bytes=max_file_bytes)
    sizes = set()
    for request in value.requests:
        source = request.source
        rid = str(source.repository_id)
        require(rid in repositories and request.prior is None, 'invalid_yaml_prior')
        pairs = dict(parse_qsl(urlsplit(source.descriptor.url).query))
        size = int(pairs.get('per_page', '0'))
        parameters(size, 1)
        require(source.descriptor.url == list_url(source.repository_id, size),
                'unexpected_list_request')
        sizes.add(size)
    require(len(sizes) == 1, 'mixed_page_sizes')
    page_size = sizes.pop()
    attempts, report = collect(value, transport, clock, credential,
                               workflow_identity=workflow_identity)
    updated = dict(repositories)
    for attempt in attempts:
        try:
            following = (has_next(attempt, page_size=page_size)
                         if attempt['outcome'] == 'response' and attempt['status'] == 200 else False)
        except (ValueError, TypeError, KeyError):
            # Invalid metadata must fail this source without changing its facts.
            attempt = dict(attempt, status=None)
            following = False
        rid = str(attempt['repository_id'])
        updated[rid] = merge_attempts(repositories[rid], [(attempt, following)],
            attempted_at=attempt['request_started_at'][:19] + 'Z', page_size=page_size,
            page_limit=1, max_catalog_bytes=max_file_bytes)
    tree = candidate_tree(apps, updated, schema=schema, max_file_bytes=max_file_bytes)
    report = dict(report, not_attempted_repositories=[str(r.source.repository_id)
                  for r in value.requests[len(attempts):]], sources={str(a['repository_id']):
                  updated[str(a['repository_id'])]['collection']['status'] for a in attempts})
    return tree, report
