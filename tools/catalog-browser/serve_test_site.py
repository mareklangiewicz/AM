#!/usr/bin/env python3
"""Serve an actual staged artifact with tiny inert fixtures and native fetch."""
from pathlib import Path
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from tempfile import TemporaryDirectory
import argparse
import hashlib
import json
from stage import ROOT, stage

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--port', type=int, default=8766)
args = parser.parse_args()
with TemporaryDirectory(prefix='am-browser-e2e-') as tmp:
    tmp = Path(tmp)
    data = tmp / 'data'
    files = {'apps.yaml': 'apps', 'repositories/example.yaml': 'repository',
             'status/runs.yaml': 'runs', 'status/statistics.yaml': 'statistics'}
    hashes = {}
    for path, example in files.items():
        raw = (ROOT / f'tools/catalog-contract/examples/{example}.yaml').read_bytes()
        target = data / 'catalog' / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
        hashes[path] = hashlib.sha256(raw).hexdigest()
    (data / 'review.json').write_text(json.dumps(dict(label='Test catalog', document_sha256=hashes)))
    output = tmp / 'public'
    stage(output, data)
    class QuietHandler(SimpleHTTPRequestHandler):
        def __init__(self, *a, **kw):
            super().__init__(*a, directory=str(output), **kw)
        def log_message(self, *args):
            pass
    def handler(*a, **kw):
        return QuietHandler(*a, **kw)
    ThreadingHTTPServer(('127.0.0.1', args.port), handler).serve_forever()
