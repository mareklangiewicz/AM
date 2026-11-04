"""Static YAML enrollment and pinned-prior bridge. No shell evaluation or HTTP."""
import hashlib
from pathlib import PurePosixPath
import re

from collector import require
from manifest import load_manifest
from yaml_adapter import collect_scoped, list_plan, schema_url, validate_collection_state
from yaml_publication import load_local


def enroll(raw, workflow_identity, recipes, *, source_revision):
    """recipes yields (programs/ARCH/name, bytes) from a reviewed source checkout.

    Only marked shared recipes with an exact enrolled CATALOG_ALIAS contribute.
    App names never encode architecture. A name mapping to different identities
    across architectures is rejected. Report excludes paths outside this manifest.
    """
    value = load_manifest(raw, workflow_identity)
    aliases, identities = {}, {}
    schema = schema_url(source_revision)
    for request in value.requests:
        source = request.source
        rid = str(source.repository_id)
        for alias in (source.descriptor.url, *source.aliases):
            aliases[alias] = source.repository_id
            match = re.match(r'https://api.github.com/repos/([^/]+/[^/]+)/releases', alias)
            if match:
                name = match[1]
                require(rid not in identities or identities[rid]['repository'].lower() == name.lower(),
                        'conflicting_readable_identity')
                identities.setdefault(rid, dict(format=2, schema=schema,
                    repository_id=source.repository_id, repository=name))
    require(set(identities) == {str(r.source.repository_id) for r in value.requests},
            'missing_readable_identity')
    apps, paths, excluded, seen = {}, [], [], set()
    for path, body in recipes:
        require(isinstance(path, str) and re.fullmatch(
            r'programs/(x86_64|aarch64|i686|armv7l)/[a-z0-9][a-z0-9_.+-]*', path)
            and path not in seen and type(body) is bytes, 'invalid_recipe_input')
        seen.add(path)
        text = body.decode('utf-8')
        if '# AM-CATALOG-RECIPE 1' not in text.splitlines():
            continue
        name = PurePosixPath(path).name
        assignment = re.findall(r'^APP=(.*)$', text, re.M)
        matches = re.findall(r'^CATALOG_ALIAS="([^"\n]+)"$', text, re.M)
        require(assignment == [name] and len(matches) == 1, 'nonstatic_recipe_identity')
        if matches[0] not in aliases:
            excluded.append(path)
            continue
        rid = aliases[matches[0]]
        require(name not in apps or apps[name] == rid, 'conflicting_app_identity')
        apps[name] = rid
        paths.append(dict(path=path, sha256=hashlib.sha256(body).hexdigest(), repository_id=rid))
    return dict(sorted(apps.items())), identities, dict(
        manifest_sha256=hashlib.sha256(raw).hexdigest(), source_revision=source_revision,
        recipes=sorted(paths, key=lambda row: row['path']), excluded=sorted(excluded))


def prepare_pinned(repo, commit, raw, workflow_identity, recipes, *, source_revision,
                   max_file_bytes, sources=None, page_size=100):
    """Pin is mandatory for refresh; None explicitly requests initial bootstrap.

    Keep existing apps/repositories, enroll additions, reject app reassignment.
    Retirement is deliberately not inferred from omission in the current inputs.
    """
    apps, identities, evidence = enroll(raw, workflow_identity, recipes,
                                      source_revision=source_revision)
    if commit is None:
        previous_apps, repositories = {}, {}
    else:
        previous_apps, repositories = load_local(repo, commit, max_file_bytes=max_file_bytes)
    for name, rid in apps.items():
        require(name not in previous_apps or previous_apps[name] == rid, 'conflicting_app_identity')
    apps = dict(previous_apps, **apps)
    for rid, identity in identities.items():
        repositories.setdefault(rid, identity)
    schema = schema_url(source_revision)
    validate_collection_state(apps, repositories, schema=schema, max_file_bytes=max_file_bytes)
    value = list_plan(raw, workflow_identity, sources=sources, page_size=page_size)
    return value, apps, repositories, evidence


def collect_pinned(repo, commit, raw, workflow_identity, recipes, transport_factory,
                   clock, credential, *, source_revision, max_file_bytes,
                   sources=None, page_size=100, **scope):
    """Return a candidate tied to a previous pin; no Git ref update or publish."""
    value, apps, repositories, evidence = prepare_pinned(repo, commit, raw, workflow_identity,
        recipes, source_revision=source_revision, max_file_bytes=max_file_bytes,
        sources=sources, page_size=page_size)
    tree, report = collect_scoped(value, transport_factory, clock, credential,
        workflow_identity=workflow_identity, apps=apps, repositories=repositories,
        source_revision=source_revision, max_file_bytes=max_file_bytes, **scope)
    return tree, dict(report, previous_publication=commit, enrollment=evidence)


def shared_recipes(root):
    """Read only the four AM recipe directories; never execute recipe contents."""
    for arch in ('x86_64', 'aarch64', 'i686', 'armv7l'):
        for path in sorted((root/'programs'/arch).iterdir()):
            if path.is_file():
                body = path.read_bytes()
                if b'# AM-CATALOG-RECIPE 1' in body.splitlines():
                    yield path.relative_to(root).as_posix(), body
