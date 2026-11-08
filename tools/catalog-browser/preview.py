#!/usr/bin/env python3
"""Loopback-only browser preview with explicitly labelled contract fixtures.

No public reads or publication: GitHub requests in this preview are intercepted
and served from the repository's inert contract test fixtures.
"""
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
import argparse

ROOT = Path(__file__).resolve().parents[2]
PIN = 'a' * 40
FIXTURES = {
    'catalog.yaml': 'catalog', 'apps.yaml': 'apps',
    'provenance.yaml': 'provenance', 'repositories/example.yaml': 'repository',
    'status.yaml': 'status', 'statistics.yaml': 'statistics',
    'runs/123-2/summary.yaml': 'summary', 'runs/123-2/sources/example.yaml': 'source',
}
INJECTION = '''<script>
const originalFetch=globalThis.fetch.bind(globalThis);
globalThis.fetch=(url,options)=>{
 const u=new URL(url,location.href);
 if(u.hostname==='api.github.com')return Promise.resolve(new Response(JSON.stringify({object:{sha:'PIN'}})));
 if(u.hostname==='raw.githubusercontent.com')return originalFetch('/__fixture/'+u.pathname.split('/').slice(4).join('/'),options);
 return originalFetch(url,options);
};
</script>'''.replace('PIN', PIN)

class Preview(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def do_GET(self):
        path = self.path.split('?')[0]
        if path.startswith('/__fixture/'):
            fixture = FIXTURES.get(path.removeprefix('/__fixture/'))
            if fixture is None:
                self.send_error(404)
                return
            data = (ROOT / f'tools/catalog-contract/fixtures/{fixture}.yaml').read_bytes()
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write(data)
            return
        if path in ('/web/catalog/', '/web/catalog/index.html'):
            html = (ROOT / 'web/catalog/index.html').read_text()
            html = html.replace('<script type="module"', INJECTION + '<script type="module"')
            html = html.replace('<h1>', '<p role="status">LOCAL CONTRACT FIXTURES — synthetic identities; no live data.</p><h1>')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(html.encode())
            return
        # This server deliberately exposes only browser source and strict readers.
        if path not in {'/web/catalog/' + f for f in ('app.mjs', 'catalog.mjs', 'keyboard.mjs')} | {'/tools/catalog-contract/reader.mjs', '/tools/catalog-contract/definitions.mjs'}:
            self.send_error(404)
            return
        super().do_GET()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, default=8765)
    args = parser.parse_args()
    print(f'Fixture preview: http://127.0.0.1:{args.port}/web/catalog/?app=example', flush=True)
    ThreadingHTTPServer(('127.0.0.1', args.port), Preview).serve_forever()
