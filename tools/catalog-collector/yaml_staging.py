"""Inactive YAML workflow/artifact adapter. No token lookup, HTTP or publication."""
import hashlib
from pathlib import Path
import re
import stat

from collector import require
from storage import canonical, decode
from workflow_adapter import preflight
from yaml_adapter import schema_url
from yaml_enrollment import collect_pinned, prepare_pinned
from yaml_publication import candidate_tree, decode_document

POLICY_MAXIMA = dict(max_file_bytes=33554432, max_run_requests=900,
    max_run_bytes=1073741824, run_seconds=300, max_source_requests=900,
    max_tree_bytes=1073741824, max_files=1024, max_receipt_bytes=1048576)


def policy(raw):
    require(type(raw) is bytes and len(raw) <= 64000, 'invalid_yaml_policy')
    obj = decode(raw)
    require(type(obj) is dict and set(obj) == set(POLICY_MAXIMA)
            and all(type(n) is int and 0 < n <= POLICY_MAXIMA[k] for k,n in obj.items()),
            'invalid_yaml_policy')
    return obj


def checked(context, raw, revision, policy_raw):
    preflight(context, raw, revision)
    require(context.get('yaml_policy_sha256') == hashlib.sha256(policy_raw).hexdigest(),
            'unapproved_yaml_policy')
    return policy(policy_raw)


def tree_documents(tree, limits):
    require(type(tree) is dict and 'apps.yaml' in tree and len(tree) <= limits['max_files'],
            'invalid_yaml_tree')
    total = 0
    repositories = {}
    for path, body in tree.items():
        require(path == 'apps.yaml' or re.fullmatch(r'repositories/[1-9][0-9]*\.yaml',path),
                'unexpected_yaml_path')
        require(type(body) is bytes, 'invalid_yaml_bytes')
        total += len(body)
        require(total <= limits['max_tree_bytes'], 'yaml_tree_bound')
        obj = decode_document(body, limits['max_file_bytes'])
        if path == 'apps.yaml':
            apps = obj['apps']
            schema = obj['schema']
        else:
            rid = path.split('/')[1][:-5]
            require(str(obj['repository_id']) == rid, 'yaml_path_identity')
            repositories[rid] = obj
    # Check complete cross-file references, canonical bytes and one shared schema.
    require(candidate_tree(apps,repositories,schema=schema,
            max_file_bytes=limits['max_file_bytes']) == tree, 'noncanonical_yaml_candidate')
    return apps, repositories


def verify(tree, receipt, context, raw, revision, policy_raw, recipes, *, repo):
    """Bind normalized artifact to trusted run/source/policy/prior; do not publish.

    As specified by format 2, upstream facts rely on the trusted collection job.
    No raw response archive or independent API-fact reconstruction is implied.
    """
    limits = checked(context, raw, revision, policy_raw)
    require(type(receipt) is bytes and len(receipt) <= limits['max_receipt_bytes'],
            'yaml_receipt_bound')
    record = decode(receipt)
    require(set(record) == {'context','scope','report'} and record['context'] == context,
            'yaml_artifact_context')
    scope = record['scope']
    require(type(scope) is dict and set(scope) == {'sources','page_size','page_limit','reconcile'}
            and hashlib.sha256(canonical(scope)).hexdigest() == context.get('yaml_scope_sha256'),
            'unapproved_yaml_scope')
    pin = context.get('previous_publication') or None
    value, expected_apps, previous, enrollment = prepare_pinned(repo,pin,raw,
        int(context['repository_id']),recipes, source_revision=revision,
        max_file_bytes=limits['max_file_bytes'],sources=scope['sources'],page_size=scope['page_size'])
    from retention import parameters
    parameters(scope['page_size'],scope['page_limit'])
    require(type(scope['reconcile']) is bool and
            (not scope['reconcile'] or scope['page_limit'] == 'all'), 'invalid_yaml_scope')
    apps, repositories = tree_documents(tree,limits)
    require(apps == expected_apps and set(repositories) == set(previous), 'yaml_enrollment_mismatch')
    expected_schema = schema_url(revision)
    require(all(obj['schema'] == expected_schema for obj in repositories.values())
            and decode_document(tree['apps.yaml'],limits['max_file_bytes'])['schema'] == expected_schema,
            'unapproved_yaml_schema')
    report = record['report']
    require(report['previous_publication'] == pin and report['enrollment'] == enrollment,
            'yaml_prior_or_enrollment_mismatch')
    selected = {str(r.source.repository_id) for r in value.requests}
    outcomes = report['sources']
    require(type(outcomes) is dict and set(outcomes) <= selected
            and report['not_attempted_repositories'] == [str(r.source.repository_id)
                for r in value.requests if str(r.source.repository_id) not in outcomes],
            'yaml_source_report_mismatch')
    for rid, obj in repositories.items():
        before = previous[rid]
        if rid not in outcomes:
            require(obj == dict(before,schema=schema_url(revision)), 'yaml_unattempted_changed')
            continue
        require(obj['repository'] == before['repository'], 'yaml_readable_identity_changed')
        attempt = obj['collection']
        require(attempt['status'] == outcomes[rid] and attempt['page_size'] == scope['page_size']
                and attempt['page_limit'] == scope['page_limit']
                and attempt['reconcile'] == scope['reconcile'], 'yaml_collection_scope_mismatch')
        if outcomes[rid] == 'failed':
            require(all(obj.get(k) == before.get(k) for k in
                        ('last_success','observed_at','releases')), 'yaml_failed_facts_changed')
    return tree


def stage(output, tree, receipt, limits):
    """Create a new private directory; clean it on failure rather than expose partial output."""
    import shutil
    root = Path(output)
    require(not root.exists() and not root.is_symlink(), 'yaml_output_exists')
    tree_documents(tree,limits)
    require(len(receipt) <= limits['max_receipt_bytes'], 'yaml_receipt_bound')
    root.mkdir(mode=0o700)
    try:
        for path, body in tree.items():
            target = root/'candidate'/path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(body)
            target.chmod(0o600)
        (root/'receipt.json').write_bytes(receipt)
        (root/'receipt.json').chmod(0o600)
    except BaseException:
        shutil.rmtree(root)
        raise


def read_staged(directory, limits):
    """Read closed regular files only; never execute or extract artifact paths."""
    root = Path(directory)
    require(root.is_dir() and not root.is_symlink(), 'invalid_yaml_artifact_directory')
    files, total, count = {}, 0, 0
    for path in root.rglob('*'):
        name = path.relative_to(root).as_posix()
        mode = path.lstat().st_mode
        if stat.S_ISDIR(mode):
            require(name in {'candidate','candidate/repositories'}, 'unexpected_yaml_directory')
            continue
        require(stat.S_ISREG(mode) and not mode & 0o111, 'invalid_yaml_artifact_mode')
        require(name == 'receipt.json' or name == 'candidate/apps.yaml'
                or re.fullmatch(r'candidate/repositories/[1-9][0-9]*\.yaml',name),
                'unexpected_yaml_artifact_path')
        count += 1
        require(count <= limits['max_files']+1, 'yaml_artifact_file_bound')
        cap = limits['max_receipt_bytes'] if name == 'receipt.json' else limits['max_file_bytes']
        size = path.lstat().st_size
        total += size
        require(size <= cap and total <= limits['max_tree_bytes']+limits['max_receipt_bytes'],
                'yaml_artifact_byte_bound')
        with path.open('rb') as stream:
            body = stream.read(cap+1)
        require(len(body) == size and len(body) <= cap, 'yaml_artifact_changed')
        files[name] = body
    require('receipt.json' in files, 'yaml_artifact_missing_receipt')
    receipt = files.pop('receipt.json')
    tree = {name.removeprefix('candidate/'):body for name,body in files.items()}
    tree_documents(tree,limits)
    return tree, receipt


def collect_stage(context, raw, revision, policy_raw, recipes, transport_factory,
                  clock, credential, output, *, repo, sources=None,
                  page_size=100, page_limit=1, reconcile=False):
    limits = checked(context,raw,revision,policy_raw)
    destination = Path(output)
    require(not destination.exists() and not destination.is_symlink(), 'yaml_output_exists')
    scope = dict(sources=sources,page_size=page_size,page_limit=page_limit,reconcile=reconcile)
    require(hashlib.sha256(canonical(scope)).hexdigest() == context.get('yaml_scope_sha256'),
            'unapproved_yaml_scope')
    # Materialize the caller's reviewed recipe bytes once for collection + verification.
    recipes = list(recipes)
    tree, report = collect_pinned(repo,context.get('previous_publication') or None,raw,
        int(context['repository_id']),recipes,transport_factory,clock,credential,
        source_revision=revision,max_file_bytes=limits['max_file_bytes'],**scope,
        **{k:limits[k] for k in ('max_run_requests','max_run_bytes','run_seconds','max_source_requests')})
    receipt = canonical(dict(context=context,scope=scope,report=report)) + b'\n'
    verify(tree,receipt,context,raw,revision,policy_raw,recipes,repo=repo)
    stage(output,tree,receipt,limits)
    return report
