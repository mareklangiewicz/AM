"""Narrow Git storage probe on the already validated dual-output artifact.

No domain requalification, acquisition, publisher invocation or remote writes.
Creates a new disposable repository; never modifies supplied evidence.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import time

from publication import git


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--artifact', type=Path, required=True)
    parser.add_argument('--work', type=Path, required=True)
    args = parser.parse_args()
    args.work.mkdir(parents=True, exist_ok=False)
    repo = args.work / 'legacy.git'
    git(args.work, 'init', '--bare', '--quiet', '--template=', str(repo))
    report = json.loads((args.artifact / 'report.json').read_text())
    hashes = report['hashes']['format-2']
    sources = sorted(path for path in hashes if path.startswith('repositories/'))
    if len(sources) != 5000:
        raise ValueError('expected qualified 5000-source artifact')
    selected = set(sources[:500])
    started = time.monotonic()

    def commit(refresh):
        process = subprocess.Popen(
            ['git', '-C', str(repo), 'fast-import', '--quiet'],
            stdin=subprocess.PIPE, stdout=subprocess.DEVNULL)
        try:
            stream = process.stdin
            stream.write(b'commit refs/heads/probe\ncommitter Probe <probe@example.invalid> 1794000000 +0000\ndata 5\nprobe\n')
            if refresh:
                stream.write(b'from refs/heads/probe^0\n')
            for path in sorted(selected if refresh else hashes):
                raw = (args.artifact / 'format-2' / path).read_bytes()
                if hashlib.sha256(raw).hexdigest() != hashes[path]:
                    raise ValueError('artifact hash mismatch: ' + path)
                if refresh:
                    raw, count = re.subn(
                        rb'^(\s*(?:attempted_at|completed_at|observed_at): )"[^"]+"$',
                        rb'\1"2026-11-09T00:00:00Z"', raw, flags=re.M)
                    if count < 3:
                        raise ValueError('missing observation fields')
                stream.write(('M 100644 inline ' + path + '\ndata ' + str(len(raw)) + '\n').encode())
                stream.write(raw)
                stream.write(b'\n')
            stream.write(b'\ndone\n')
            stream.close()
            if process.wait() != 0:
                raise ValueError('fast-import failed')
        finally:
            if process.poll() is None:
                process.kill()
                process.wait()

    def pack():
        git(repo, '-c', 'pack.threads=1', '-c', 'pack.compression=6',
            'repack', '-ad', '--window=10', '--depth=50')
        return sum(path.stat().st_size for path in (repo / 'objects/pack').glob('*.pack'))

    commit(False)
    seed = pack()
    print(json.dumps(dict(stage='seed_packed', bytes=seed)), flush=True)
    parent = git(repo, 'rev-parse', 'refs/heads/probe').decode().strip()
    commit(True)
    refreshed = pack()
    if git(repo, 'rev-parse', 'refs/heads/probe^').decode().strip() != parent:
        raise AssertionError('parent not preserved')
    result = dict(
        synthetic=True, storage_probe_only=True, live_acquisition=False,
        source_head=git(Path(__file__).resolve().parents[2], 'rev-parse', 'HEAD').decode().strip(),
        artifact_report_sha256=hashlib.sha256((args.artifact / 'report.json').read_bytes()).hexdigest(),
        script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        source_count=5000, batch_size=500, seed_packed_bytes=seed,
        refreshed_packed_bytes=refreshed, added_packed_bytes=refreshed-seed,
        annual_runs=8760, annual_added_packed_bytes=(refreshed-seed)*8760,
        packing='git repack -ad --window=10 --depth=50; threads=1; compression=6',
        seconds=time.monotonic()-started,
        limits='One timestamp-only sample on repeated saved shapes. All selected observation overrides refreshed synthetically. No new release payloads, status, pre-existing remote history or production packing guarantee. Projection is not a measured year. Fast-import bypasses domain validation/publication; input hashes bind the already validated dual artifact.')
    (args.work / 'receipt.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2), flush=True)


if __name__ == '__main__':
    main()
