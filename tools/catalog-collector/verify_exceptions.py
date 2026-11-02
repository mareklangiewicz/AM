"""Apply inert ticket-68 patches only in a disposable source snapshot and verify."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

from exception_batch import DIRECTORY
from identity_batch import ROOT
from storage import digest


def main():
    with tempfile.TemporaryDirectory(prefix='am-exception-candidate-') as temporary:
        root=Path(temporary)
        for directory in ('tools','modules'): shutil.copytree(ROOT/directory,root/directory,ignore=shutil.ignore_patterns('__pycache__'))
        (root/'docs').symlink_to(ROOT/'docs',target_is_directory=True)
        rows=json.loads((DIRECTORY/'prepared/migration.json').read_bytes())['migrated']
        revision=json.loads((DIRECTORY/'queue.json').read_bytes())['source_revision']
        for path in {'programs/x86_64/obsidian',*(item['path'] for item in rows)}:
            dest=root/path;dest.parent.mkdir(parents=True,exist_ok=True)
            dest.write_bytes(subprocess.check_output(['git','show',revision+':'+path],cwd=ROOT))
        path=root/'.github/workflows/catalog-shards.yml';path.parent.mkdir(parents=True);shutil.copyfile(ROOT/'.github/workflows/catalog-shards.yml',path)
        for path in ('.github/workflows/catalog-shards.yml','tools/catalog-collector/scheduled_dispatch.py',
                     'tools/catalog-collector/shard_delivery.py','tools/catalog-collector/test_scheduled_dispatch.py'):
            (root/path).write_bytes(subprocess.check_output(['git','show',revision+':'+path],cwd=ROOT))
        for name in ('enrollment.patch','recipes.patch'):
            subprocess.run(['git','apply',str(DIRECTORY/'prepared'/name)],cwd=root,check=True)
        # Full operational inventory preflight in the patched snapshot before lifecycle tests.
        code="""from pathlib import Path
from shard_delivery import inventory
from storage import digest
p=Path.cwd().parents[1]
raw=(p/'docs/track/release-catalog/research/appimage-exceptions-next-20261102/prepared/inventory.json').read_bytes()
r='a'*40
c=dict(repository='mareklangiewicz/AM',repository_id='1291019762',event='workflow_dispatch',ref='refs/heads/main-marek',sha=r,workflow_sha=r,approved_revision=r,run_id='1',run_attempt='1',inventory_sha256=digest(raw),previous_publication='6f21b8c1d2bf271f570a0177bc1068bb9ca43d0a')
m=inventory(c,raw,r,p)
assert len(m)==16
print('Patched operational inventory preflight passed: 16 shards')
"""
        location=root/'tools/catalog-collector'
        subprocess.run([sys.executable,'-B','-c',code],cwd=location,check=True)
        subprocess.run([sys.executable,'-B','-m','unittest','test_shard_delivery','test_shards','test_scheduled_dispatch'],cwd=location,check=True)
        subprocess.run([sys.executable,'-B','check_exception_lifecycle.py','-v'],cwd=location,check=True)
    print('Candidate snapshot checks passed; production recipes and controls untouched.')


if __name__=='__main__': main()
