"""Offline resource replay with genuine saved bodies and synthetic repeat events.

No network, credentials, production branch or remote refs. Temporary local Git only.
"""
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import zipfile

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[4]
sys.path.insert(0, str(ROOT / 'tools/catalog-collector'))
import test_migration_enrollment as fixture
from delivery import ZIP_CAP, unpack_artifact, verify_artifact
from publication import git, publish_local, HISTORY_CAP
from storage import validate, digest, TREE_CAP, INDEX_CAP


def objects(repo):
    directory = repo / 'objects'
    return dict(file_bytes=sum(p.stat().st_size for p in directory.rglob('*') if p.is_file()),
                reachable_objects=len(git(repo, 'rev-list', '--objects', '--all').splitlines()))


def main():
    fixture.MigrationEnrollment.setUpClass()
    harness = fixture.MigrationEnrollment()
    files, tree = harness.files()
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
        for name, raw in files.items():
            # Fixed member times make archive size/hash repeatable.
            member = zipfile.ZipInfo(name, (2026, 10, 28, 19, 20, 32))
            member.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(member, raw)
    archive = stream.getvalue()
    assert verify_artifact(unpack_artifact(archive), fixture.context(), fixture.RAW,
                           fixture.REV, harness.base) == tree
    index = validate(tree)
    with tempfile.TemporaryDirectory() as directory:
        repo = Path(directory) / 'local.git'
        subprocess.run(['git', 'init', '--bare', '--quiet', '--template=', str(repo)], check=True)
        parent = publish_local(repo, harness.base, None)
        before = objects(repo)
        child = publish_local(repo, tree, parent)
        after = objects(repo)
        assert git(repo, 'rev-parse', child+'^').decode().strip() == parent
    sources = {}
    for rid, entry in index['entries'].items():
        sources[rid] = dict(bytes=entry['observation']['bytes'],
                           body_sha256=entry['observation']['sha256'])
    report = dict(
        interpretation='OFFLINE ONLY: retained baseline plus new real body, synthetic six 304 events, temporary local Git. Not live seven-source publication or daily retention.',
        previous_tree_bytes=sum(map(len, harness.base.values())),
        candidate_manifest_sha256=digest(fixture.RAW),
        previous_manifest_sha256=digest(harness.six_raw),
        candidate_tree_bytes=sum(map(len, tree.values())),
        index_bytes=len(tree['index.json']), lookup_bytes=len(tree['lookup.tsv']),
        bodies_bytes=sum(v['bytes'] for v in sources.values()), sources=sources,
        artifact_members=len(files),
        artifact_uncompressed_bytes=sum(map(len, files.values())),
        artifact_zip_bytes=len(archive), artifact_zip_sha256=digest(archive),
        local_history_before=before, local_history_after=after,
        local_object_file_growth_bytes=after['file_bytes']-before['file_bytes'],
        caps=dict(body=8_000_000, index=INDEX_CAP, tree=TREE_CAP,
                  artifact=ZIP_CAP, history=HISTORY_CAP, request_seconds=30, batch_seconds=300),
        implementation_sha256={name:digest((ROOT/'tools/catalog-collector'/name).read_bytes())
                               for name in ('collector.py','manifest.py','supervised_transport.py',
                                            'storage.py','delivery.py')})
    (OUT/'preparation-resources.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k not in ('sources','implementation_sha256')}, indent=2))


if __name__ == '__main__':
    main()
