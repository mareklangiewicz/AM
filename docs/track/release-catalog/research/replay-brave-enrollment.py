"""Offline resource replay using retained real bytes and synthetic seven-source 304s."""
from pathlib import Path
import io
import json
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / 'tools/catalog-collector'))
import test_brave_enrollment as candidate
from storage import digest, validate
from delivery import unpack_artifact, verify_artifact
from publication import publish_local, git


def main():
    candidate.BraveEnrollment.setUpClass()
    helper = candidate.BraveEnrollment()
    files, tree = helper.files()
    archive = io.BytesIO()
    with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED) as output:
        for path, raw in files.items():
            member = zipfile.ZipInfo(path, date_time=(2026, 10, 31, 0, 0, 0))
            member.compress_type = zipfile.ZIP_DEFLATED
            output.writestr(member, raw)
    payload = archive.getvalue()
    assert verify_artifact(unpack_artifact(payload), candidate.context(), candidate.RAW,
                           candidate.REV, helper.base) == tree
    index = validate(tree)
    with tempfile.TemporaryDirectory() as directory:
        remote = Path(directory) / 'remote.git'
        git(Path(directory), 'init', '--bare', '--quiet', '--template=', str(remote))
        parent = publish_local(remote, helper.base, None)
        def size():
            return sum(p.stat().st_size for p in (remote / 'objects').rglob('*') if p.is_file())
        before = size()
        commit = publish_local(remote, tree, parent)
        after = size()
        assert git(remote, 'rev-parse', commit+'^').decode().strip() == parent
    report = dict(interpretation='OFFLINE ONLY: retained accepted seven-source tree, real Brave body, synthetic seven 304 events and local Git; no live publication or retention guarantee',
        source_revision='implementation bound by hashes; containing preparation commit supplied separately; activation revision not assigned',
        retained_publication=candidate.PARENT,
        manifest_sha256=digest(candidate.RAW),
        previous_tree_bytes=sum(map(len, helper.base.values())),
        candidate_tree_bytes=sum(map(len, tree.values())), index_bytes=len(tree['index.json']),
        lookup_bytes=len(tree['lookup.tsv']),
        body_bytes=sum(len(raw) for path, raw in tree.items() if path.startswith('bodies/')),
        source_count=len(index['entries']), artifact_members=len(files),
        artifact_uncompressed_bytes=sum(map(len, files.values())), artifact_zip_bytes=len(payload),
        artifact_zip_sha256=digest(payload), local_objects_before_bytes=before,
        local_objects_after_bytes=after, local_object_growth_bytes=after-before,
        caps=dict(body=8_000_000,headers=64_000,index=2_000_000,tree=50_000_000,
                  artifact=105_000_000,history=128_000_000,connect_seconds=10,request_seconds=30,batch_seconds=300),
        nominal_eight_request_seconds=240,
        implementation_sha256={p:digest((ROOT/p).read_bytes()) for p in (
            'tools/catalog-collector/collector.py','tools/catalog-collector/manifest.py',
            'tools/catalog-collector/workflow_adapter.py','tools/catalog-collector/supervised_transport.py',
            'tools/catalog-collector/storage.py','tools/catalog-collector/delivery.py',
            'docs/track/release-catalog/design/staged-manifest-brave.json')})
    (Path(__file__).parent/'brave-eight-source-replay.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))

if __name__ == '__main__': main()
