"""Format-2 source candidate; no CLI, token lookup, workflow or remote publication.

The existing collector executes unconditional numeric list requests. The scoped
bridge schedules finite/all pages within shared transport budgets. Reader,
normalization and retained merge are shared with the YAML candidate.
"""
import re
from urllib.parse import parse_qsl, urlsplit

from collector import Descriptor, Refusal, Source, collect, plan, require
from manifest import load_manifest

from attempt_adapter import merge_attempts
from retention import parameters
from yaml_publication import candidate_tree


class IncompleteBootstrap(Refusal):
    """No candidate exists; retain the aggregate report for the caller's logs."""
    def __init__(self, report):
        super().__init__('incomplete_bootstrap')
        self.report = report


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
        if updated[rid]['collection']['status'] == 'ok':
            updated[rid]['schema'] = schema
    tree = candidate_tree(apps, updated, schema=schema, max_file_bytes=max_file_bytes)
    report = dict(report, not_attempted_repositories=[str(r.source.repository_id)
                  for r in value.requests[len(attempts):]], sources={str(a['repository_id']):
                  updated[str(a['repository_id'])]['collection']['status'] for a in attempts})
    return tree, report


def validate_collection_state(apps, repositories, *, schema, max_file_bytes):
    """Validate retained documents and observation-free bootstrap identities."""
    from bounded import integer
    from writer import document
    from yaml_publication import check_references, decode_document
    check_references(apps, repositories)
    retained = {}
    for rid, obj in repositories.items():
        if 'collection' in obj:
            retained[rid] = obj
            continue
        require(set(obj) == {'format', 'schema', 'repository_id', 'repository'}
                and type(obj['format']) is int and obj['format'] == 2
                and obj['schema'] == schema and isinstance(obj['repository'], str)
                and re.fullmatch('[A-Za-z0-9-]+/[A-Za-z0-9_.-]+', obj['repository']),
                'invalid_bootstrap_identity')
        integer(obj['repository_id'], 1)
    candidate_tree({name: rid for name, rid in apps.items() if str(rid) in retained},
                   retained, schema=schema, max_file_bytes=max_file_bytes)
    decode_document(document(dict(format=2, schema=schema, apps=dict(sorted(apps.items())))).encode(),
                    max_file_bytes)


def collect_scoped(value, transport_factory, clock, credential, *, workflow_identity,
                   apps, repositories, source_revision, max_file_bytes,
                   max_run_requests, max_run_bytes, page_limit=1, reconcile=False,
                   run_seconds=300, max_source_requests=64):
    """Lazy finite/all-page collection; factory receives each validated page plan.

    Construct the existing SupervisedTransport per page using reviewed revision
    arguments. One shared budget clamps its deadlines and accounts body chunks;
    source transitions consume pages lazily, so invalid pages cannot trigger more
    acquisition. No transport is created until prior state and options validate.
    """
    from dataclasses import replace
    import math
    from collector import Chunk, mono, validate_plan
    from retention import CollectionFailure

    validate_plan(value, workflow_identity)
    parameters(100, page_limit)
    require(type(reconcile) is bool and (not reconcile or page_limit == 'all'),
            'invalid_reconciliation_scope')
    require(all(type(n) is int and n > 0 for n in
                (max_run_requests, max_run_bytes, max_source_requests)), 'invalid_run_budget')
    require(type(run_seconds) in (int, float) and math.isfinite(run_seconds)
            and 0 < run_seconds <= 300, 'invalid_run_budget')
    schema = schema_url(source_revision)
    validate_collection_state(apps, repositories, schema=schema, max_file_bytes=max_file_bytes)
    sizes = set()
    for request in value.requests:
        source = request.source
        require(str(source.repository_id) in repositories and request.prior is None,
                'invalid_yaml_prior')
        size = int(dict(parse_qsl(urlsplit(source.descriptor.url).query)).get('per_page', '0'))
        parameters(size, page_limit)
        require(source.descriptor.url == list_url(source.repository_id, size),
                'unexpected_list_request')
        sizes.add(size)
    require(len(sizes) == 1, 'mixed_page_sizes')
    page_size = sizes.pop()
    start = mono(clock)
    deadline = start + run_seconds
    used_requests = used_bytes = streak = 0
    stop = None
    outcomes = {}
    updated = dict(repositories)

    def unavailable():
        return (stop is not None or used_requests >= max_run_requests
                or used_bytes >= max_run_bytes or mono(clock) >= deadline)

    class BudgetTransport:
        def __init__(self, transport):
            self.transport = transport

        def execute(self, request, credential, limits):
            nonlocal used_bytes, stop
            limits = replace(limits, connect_deadline=min(limits.connect_deadline, deadline),
                             request_deadline=min(limits.request_deadline, deadline),
                             batch_deadline=min(limits.batch_deadline, deadline))
            events = iter(self.transport.execute(request, credential, limits))
            try:
                for event in events:
                    if type(event) is Chunk and type(event.data) is bytes:
                        used_bytes += len(event.data)
                        if used_bytes > max_run_bytes:
                            stop = 'collection_limit'
                            raise ValueError('collection_limit')
                    yield event
            finally:
                if hasattr(events, 'close'):
                    events.close()

    for initial in value.requests:
        rid = str(initial.source.repository_id)
        if unavailable():
            stop = stop or 'collection_limit'
            continue
        attempted_at = clock.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

        def pages():
            nonlocal used_requests, streak, stop
            number = 1
            while True:
                if unavailable() or number > max_source_requests:
                    raise CollectionFailure('collection_limit')
                source = replace(initial.source, descriptor=Descriptor(
                    list_url(initial.source.repository_id, page_size, number)))
                current = plan((source,), workflow_identity)
                transport = BudgetTransport(transport_factory(current))
                used_requests += 1
                attempts, report = collect(current, transport, clock, credential,
                                           workflow_identity=workflow_identity)
                stop = stop or report['stop_reason']
                if not attempts:
                    raise CollectionFailure('collection_limit')
                attempt = attempts[0]
                # The existing collector enforces per-request bounds. The shared
                # clamp also rejects a response crossing this run's deadline.
                if stop == 'collection_limit' or mono(clock) >= deadline:
                    stop = 'collection_limit'
                    raise CollectionFailure('collection_limit')
                failed = attempt['outcome'] != 'response' or attempt['status'] >= 500
                streak = streak + 1 if failed else 0
                if streak >= 2:
                    stop = stop or 'consecutive_failures'
                try:
                    following = (has_next(attempt, page_size=page_size, page=number)
                                 if attempt['outcome'] == 'response' and attempt['status'] == 200
                                 else False)
                except (ValueError, TypeError, KeyError):
                    attempt = dict(attempt, status=None)
                    following = False
                yield attempt, following
                number += 1

        updated[rid] = merge_attempts(repositories[rid], pages(), attempted_at=attempted_at,
            page_size=page_size, page_limit=page_limit, reconcile=reconcile,
            max_catalog_bytes=max_file_bytes, max_requests=max_source_requests,
            max_bytes=max_run_bytes, max_seconds=run_seconds)
        if updated[rid]['collection']['status'] == 'ok':
            updated[rid]['schema'] = schema
        outcomes[rid] = updated[rid]['collection']['status']
    report = dict(sources=outcomes, requests=used_requests, received_bytes=used_bytes,
                      elapsed_seconds=mono(clock)-start, stop_reason=stop,
                      not_attempted_repositories=[str(r.source.repository_id) for r in value.requests
                                                  if str(r.source.repository_id) not in outcomes])
    missing = sorted((rid for rid, obj in updated.items() if 'collection' not in obj), key=int)
    if missing:
        raise IncompleteBootstrap(dict(report, bootstrap_unattempted_repositories=missing))
    tree = candidate_tree(apps, updated, schema=schema, max_file_bytes=max_file_bytes)
    return tree, report
