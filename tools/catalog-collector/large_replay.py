"""Offline exact-evidence shard/ZIP/Git replay; repeat conditions are synthetic."""
from datetime import datetime, timezone
import io
import json
from pathlib import Path
import subprocess
import tarfile
import tempfile
import zipfile

from collector import require
from delivery import unpack_artifact, verify_artifact, read_git_tree
from identity_batch import ROOT
from large_evidence import DIRECTORY
from shard_delivery import inventory, publish_root_local, read_shard
from shards import compose, split
from storage import apply, canonical, digest, validate


def legacy_tree():
    path = ROOT/'docs/track/release-catalog/research/appimage-52-live-20261102-evidence.tar.gz'
    require(digest(path.read_bytes()) == '9d93bcf5b6ca130f2288c332c34e9b43a9b09fcfeed56ff875e7d940ab97e959',
            'legacy_evidence_digest')
    with tarfile.open(path, 'r:gz') as archive:
        for member in archive.getmembers():
            if not member.name.endswith('.zip'):
                continue
            raw = archive.extractfile(member).read()
            with zipfile.ZipFile(io.BytesIO(raw)) as check:
                if 'candidate/index.json' not in check.namelist():
                    continue
            files = unpack_artifact(raw)
            tree = {p.removeprefix('candidate/'):v for p,v in files.items() if p.startswith('candidate/')}
            validate(tree)
            return tree
    raise ValueError('legacy_candidate_missing')


def build():
    prepared = DIRECTORY/'prepared'
    raw = (prepared/'inventory.json').read_bytes()
    rev = 'a'*40  # explicit synthetic workflow context; never a rollout source claim
    context = dict(repository='mareklangiewicz/AM', repository_id='1291019762',
        event='workflow_dispatch', ref='refs/heads/main-marek', sha=rev, workflow_sha=rev,
        approved_revision=rev, run_id='1', run_attempt='1', inventory_sha256=digest(raw),
        previous_publication='29e37bd9207ae9557e8f57afa010699c649d4cde')
    manifests = inventory(context, raw, rev, ROOT)
    old = legacy_tree()
    generated = datetime.now(timezone.utc).isoformat()
    migration = json.loads((prepared/'migration.json').read_bytes())
    evidence = {s['request_id']:s['evidence'] for s in migration['sources']}
    trees, metrics = {}, []
    for name, manifest in sorted(manifests.items()):
        prior = old if name == '00' else None
        ctx = dict(context, manifest_sha256=digest(manifest))
        if prior is None:
            ctx['previous_publication'] = ''
        attempts = []
        for source in json.loads(manifest)['sources']:
            rid = source['request_id']
            descriptor = {k:getattr(__import__('collector').Descriptor(source['url']), k)
                          for k in ('url','api_version','accept')}
            if prior:
                entry = validate(prior)['entries'][rid]
                report = dict(started_at=generated, completed_at=generated, public_headers={})
                body, status, condition = b'', 304, entry['validators']
            else:
                directory = ROOT/evidence[rid]
                report = json.loads((directory/'report.json').read_bytes())
                body = (directory/'body.json').read_bytes()
                require(digest(body) == report['body_sha256'] and
                        digest((directory/'headers.txt').read_bytes()) == report['headers_sha256'], 'evidence_hash')
                status, condition = 200, {}
            attempts.append(dict(request_id=rid, descriptor=descriptor,
                repository_id=source['repository_id'], request_started_at=report['started_at'],
                response_completed_at=report['completed_at'], attempt_finished_at=report['completed_at'],
                status=status, headers=report['public_headers'], body=body, condition=condition, outcome='response'))
        tree, transitions = apply(prior, manifest, attempts, workflow_identity=1291019762,
            generated_at=generated, revision=rev, run={'id':'1','attempt':'1'})
        records = [{**{k:v for k,v in a.items() if k!='body'},
                    'body_bytes':len(a['body']), 'body_sha256':digest(a['body'])} for a in attempts]
        files = {'candidate/'+p:v for p,v in tree.items()}
        files.update({a['request_id']+'.body':a['body'] for a in attempts})
        files['report.json'] = canonical(dict(context=ctx, run={'complete':True}, attempts=records))
        files['storage-report.json'] = canonical(dict(outcome='validated_candidate', transitions=transitions,
            files={p:dict(bytes=len(v),sha256=digest(v)) for p,v in tree.items()}))
        archive = io.BytesIO()
        with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED) as stream:
            for p,v in files.items(): stream.writestr(p,v)
        packed = archive.getvalue()
        rebuilt = verify_artifact(unpack_artifact(packed), ctx, manifest, rev, prior)
        require(rebuilt == tree, 'replay_artifact_mismatch')
        trees[name] = tree
        metrics.append(dict(shard=name, sources=len(attempts), tree_bytes=sum(map(len,tree.values())), zip_bytes=len(packed)))
    tree = compose(trees, generated_at=generated, revision=rev, run={'id':'1','attempt':'1'})
    require(split(tree) == trees, 'replay_root_mismatch')
    return tree, metrics, generated


def main():
    tree, metrics, generated = build()
    with tempfile.TemporaryDirectory(prefix='am-large-replay-') as directory:
        repo = Path(directory)/'git'
        subprocess.run(['git','init','--bare','--quiet','--template=',str(repo)],check=True)
        commit = publish_root_local(repo, tree, None, shard_count=len(metrics))
        for name in split(tree):
            # read_shard omits the optional derived per-shard lookup.
            actual = read_shard(repo, commit, name)
            require(actual['index.json'] == tree[f'shards/{name}/index.json'], 'replay_git_index')
            for path, raw in actual.items():
                if path.startswith('bodies/'):
                    require(tree[path] == raw, 'replay_git_body')
        try:
            publish_root_local(repo, tree, None, shard_count=len(metrics))
        except ValueError as error:
            require(str(error) == 'stale_parent', 'replay_wrong_refusal')
        else:
            raise ValueError('replay_stale_parent_accepted')
        objects = sum(p.stat().st_size for p in (repo/'objects').rglob('*') if p.is_file())
    report = dict(interpretation='Offline saved-body replay; 52 conditional responses and workflow context synthetic. No live collection/publication.',
        generated_at=generated, shards=metrics, root_tree_bytes=sum(map(len,tree.values())),
        root_index_bytes=len(tree['index.json']), lookup_bytes=len(tree['lookup.tsv']),
        git_objects_bytes=objects, temporary_commit=commit, exact_git_roundtrip=True,
        stale_parent_refused=True)
    (DIRECTORY/'prepared/replay.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))


if __name__ == '__main__':
    main()
