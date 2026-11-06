"""Discover explicit GitHub recipe sources without executing recipe shell.

Scan output is a review queue, not collection enrollment. Verification produces
proposals using public numeric identities and a release probe; it never edits
recipes, collection lists or client policy. Inputs remain bound to recipe hashes.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import subprocess
import sys
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'tools/recipe-reconstruction'))
from originals import Originals, Catalogue
from bounded import unique_object
from host_catalog import SOURCE_CAP, configuration, utc

REPOSITORY = r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+'
ALIAS = re.compile(r'https://api[.]github[.]com/repos/('+REPOSITORY+r')/releases')


def literals(source, name):
    values = []
    for literal in re.findall(r'^'+name+r'=(.*)$', source, re.M):
        try:
            words = shlex.split(literal)
        except ValueError:
            return []
        if len(words) != 1:
            return []
        values.append(words[0])
    return values


def binding(source, app, catalogue):
    """An explicit shared-runtime alias or a whole verified upstream template."""
    names = literals(source, 'APP')
    if not names or set(names) != {app}:
        return None
    aliases = literals(source, 'CATALOG_ALIAS')
    if aliases:
        matches = [ALIAS.fullmatch(alias) for alias in aliases]
        if ('# AM-CATALOG-RECIPE 1\n' not in source or
                '# shellcheck source=modules/appimage.am\n' not in source or
                any(match is None for match in matches)):
            return None
        repositories = {match[1].lower() for match in matches}
        if len(repositories) == 1:
            return dict(repository=matches[0][1], proof='literal_catalog_alias')
        return None
    sites = literals(source, 'SITE')
    if not sites or len({site.lower() for site in sites}) != 1 or not re.fullmatch(REPOSITORY, sites[0]):
        return None
    result = catalogue.check(source)
    if result['status'] != 'instance':
        return None
    endpoints = {match[1].lower() for match in ALIAS.finditer(source)}
    if endpoints != {sites[0].lower()}:
        return None
    match = next(match for match in result['matches'] if match['status'] == 'instance')
    return dict(repository=sites[0], proof='whole_upstream_template', template=match['template'])


def _catalogue(root):
    metadata = json.loads((root/'tools/recipe-reconstruction/provenance.json').read_text())
    return Catalogue(Originals(root), [metadata['fixture_commit'], metadata['upstream_commit']])


def scan(root=ROOT):
    catalogue = _catalogue(root)
    groups, excluded = {}, []
    for arch in ('x86_64', 'aarch64', 'i686', 'armv7l'):
        for path in sorted((root/'programs'/arch).glob('*')):
            if not path.is_file():
                continue
            body = path.read_bytes()
            found = binding(body.decode('utf-8'), path.name, catalogue)
            if found is None:
                excluded.append(str(path.relative_to(root)))
                continue
            found.update(recipe=str(path.relative_to(root)), sha256=hashlib.sha256(body).hexdigest())
            groups.setdefault(path.name, []).append(found)
    candidates, ambiguous = [], []
    for app, proofs in sorted(groups.items()):
        if len({proof['repository'].lower() for proof in proofs}) != 1:
            ambiguous.append(dict(app=app, bindings=proofs))
        else:
            candidates.append(dict(app=app, repository=proofs[0]['repository'], bindings=proofs))
    return dict(source=subprocess.check_output(['git','-C',str(root),'rev-parse','HEAD'],text=True).strip(),
        observed_at=utc(), candidates=candidates, ambiguous=ambiguous, unsupported_recipes=excluded)


def _get(path):
    headers = {'Accept':'application/vnd.github+json', 'User-Agent':'AM-source-review',
               'X-GitHub-Api-Version':'2022-11-28'}
    if os.environ.get('GH_TOKEN'):
        headers['Authorization'] = 'Bearer '+os.environ['GH_TOKEN']
    request = urllib.request.Request('https://api.github.com/'+path, headers=headers)
    with urllib.request.urlopen(request, timeout=30) as response:
        raw = response.read(16*1024*1024+1)
        if len(raw) > 16*1024*1024:
            raise ValueError('response allowance')
        return json.loads(raw, object_pairs_hook=unique_object), hashlib.sha256(raw).hexdigest()


def verify(queue, *, max_sources, max_requests, root=ROOT, checkpoint=None):
    if type(max_sources) is not int or not 1 <= max_sources <= SOURCE_CAP:
        raise ValueError('source scope')
    if type(max_requests) is not int or not 1 <= max_requests <= 200:
        raise ValueError('request scope')
    if not re.fullmatch(r'[0-9a-f]{40}', queue['source']):
        raise ValueError('source commit')
    current, known = configuration()
    enrolled = {row['app'] for row in current}
    source_names = {name.lower():int(rid) for rid,name in known.items()}
    proposals, deferred = [], []
    used = 0
    catalogue = _catalogue(root)
    def result():
        return dict(source=queue['source'], observed_at=utc(), requests=used,
            proposed_sources=len(known), proposals=proposals, deferred=deferred,
            note='Review proposals only; collection enrollment and recipe policy are unchanged.')
    # The five already screened simple migration candidates lead this review.
    priority = {'agent-skills','agent-smith','agent-switchboard','agent-teams-ai','agent-toolkit'}
    candidates = sorted(queue['candidates'], key=lambda row: (row['app'] not in priority, row['app']))
    for candidate in candidates:
        app, requested = candidate['app'], candidate['repository']
        if (not re.fullmatch(r'[a-z0-9][a-z0-9_.+-]*', app) or
                not re.fullmatch(REPOSITORY, requested) or not candidate['bindings']):
            raise ValueError('invalid discovery identity')
        if app in enrolled:
            continue
        if len(known) >= max_sources or used >= max_requests:
            break
        for proof in candidate['bindings']:
            path = proof['recipe']
            if not re.fullmatch(r'programs/(x86_64|aarch64|i686|armv7l)/[a-z0-9][a-z0-9_.+-]*', path):
                raise ValueError('recipe path')
            raw = subprocess.check_output(['git','-C',str(root),'show',queue['source']+':'+path])
            if (hashlib.sha256(raw).hexdigest() != proof['sha256'] or
                    (root/path).read_bytes() != raw):
                raise ValueError('recipe changed since discovery: '+path)
            found = binding(raw.decode('utf-8'), app, catalogue)
            if found is None or found['repository'].lower() != requested.lower():
                raise ValueError('discovery source binding mismatch')
        # Metadata is checked even for a shared source: no alias is promoted on
        # the strength of an unverified textual mention or a rename redirect.
        try:
            used += 1
            metadata, digest = _get('repos/'+requested)
            if metadata.get('private') is not False or not metadata.get('full_name'):
                deferred.append(dict(app=app, reason='not_public_repository'))
                continue
            if metadata['full_name'].lower() != requested.lower():
                deferred.append(dict(app=app, reason='repository_redirect', canonical=metadata['full_name']))
                continue
            rid = metadata.get('id')
            if type(rid) is not int or rid <= 0:
                raise ValueError('numeric repository identity')
            canonical = metadata['full_name']
            if str(rid) in known and known[str(rid)].lower() != canonical.lower():
                raise ValueError('known source identity mismatch')
            if canonical.lower() in source_names and source_names[canonical.lower()] != rid:
                raise ValueError('known source identity mismatch')
            if used >= max_requests:
                break
            used += 1
            releases, release_digest = _get('repositories/'+str(rid)+'/releases?per_page=1&page=1')
            if not isinstance(releases, list) or not releases or releases[0].get('draft') is not False:
                deferred.append(dict(app=app, reason='no_public_release_in_probe'))
                continue
            row = dict(app=app, repository_id=rid, repository=canonical)
            proposals.append(dict(enrollment=row, requested_repository=requested,
                metadata_sha256=digest, release_probe_sha256=release_digest,
                observed_at=utc(), bindings=candidate['bindings']))
            known[str(rid)] = canonical
            source_names[canonical.lower()] = rid
            print(app+': '+canonical, flush=True)
        except urllib.error.HTTPError as error:
            status = error.code
            error.close()
            deferred.append(dict(app=app, reason='http_'+str(status)))
            if status in (401,403,429):
                break
        finally:
            if checkpoint is not None:
                checkpoint(result())
    return result()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    discover = sub.add_parser('scan')
    discover.add_argument('--out', required=True, type=Path)
    review = sub.add_parser('verify')
    review.add_argument('--scan', required=True, type=Path)
    review.add_argument('--out', required=True, type=Path)
    review.add_argument('--max-sources', type=int, default=SOURCE_CAP)
    review.add_argument('--max-requests', type=int, default=200)
    args = parser.parse_args()
    if args.out.exists():
        raise ValueError('refusing to replace evidence')
    def checkpoint(result):
        staging = args.out.with_suffix(args.out.suffix+'.tmp')
        staging.write_text(json.dumps(result,indent=2)+'\n')
        staging.replace(args.out)
    result = scan() if args.command == 'scan' else verify(json.loads(args.scan.read_text()),
        max_sources=args.max_sources, max_requests=args.max_requests, checkpoint=checkpoint)
    args.out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({key:len(value) if isinstance(value,list) else value
                      for key,value in result.items()},indent=2))


if __name__ == '__main__':
    main()
