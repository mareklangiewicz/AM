#!/usr/bin/env python3
"""Strict offline external-command adapters. Never opens a network connection."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from transport_args import download_destination

fixture = Path(os.environ['E2E_FIXTURE'])
settings = json.loads((fixture/'settings.json').read_text())
args = sys.argv[1:]
tool = Path(sys.argv[0]).name
if tool == 'date':
    if args == ['-u', '+%s.%6N']:
        print(settings['clock'])
    else:
        raise SystemExit(subprocess.call([os.environ.get('PREFIX','/usr')+'/bin/date', *args]))
    raise SystemExit(0)
if tool == 'notify-send':
    raise SystemExit(1)  # Desktop notification absence must be nonfatal.
if tool == 'wget' and args == ['--version']:
    raise SystemExit(subprocess.call([os.environ.get('PREFIX','/usr')+'/bin/wget', '--version']))
url = args[-1]
head = '--head' in args
record = {'tool': tool, 'url': url, 'head': head}
# Reader file-size limits also apply to adapters: one small trace per request.
(fixture/'calls'/f'{time.time_ns()}-{os.getpid()}.json').write_text(json.dumps(record))
source = settings['source']
# Explicit alternate fixture source for repository-switch scenarios. Keep traces
# at their original URLs and accept only the configured additional repository.
alternate = settings.get('alternate_source')
if alternate and url.startswith(alternate+'/'):
    url = source+url[len(alternate):]
alternate_repo = settings.get('alternate_repository')
if alternate_repo:
    for host in ('https://api.github.com/repos/', 'https://raw.githubusercontent.com/'):
        prefix = host+alternate_repo+'/'
        if url.startswith(prefix):
            url = host+settings['repository']+'/'+url[len(prefix):]
raw = None
if url == 'https://raw.githubusercontent.com/ivan-hc/am-extras/main/am-extras':
    raw = b'# Offline extras configuration\nthird_party_flags="--fixtureunused"\nfixtureunused_readme="https://example.invalid/e2e-extras"\n'
elif url == 'https://example.invalid/e2e-extras':
    raw = b'# Empty offline third-party list\n'
elif head and url.startswith('https://github.com/ivan-hc/AM/raw/test-source/translations/'):
    raise SystemExit(22)  # Optional locale is deliberately unavailable.
elif url == source+'/APP-MANAGER':
    raw = Path('/src/APP-MANAGER').read_bytes()
elif url.startswith(source+'/modules/'):
    name=url.removeprefix(source+'/modules/')
    if name in {p.name for p in Path('/src/modules').glob('*.am')}:
        raw=(Path('/src/modules')/name).read_bytes()
elif url == source+'/programs/x86_64-appimages':
    raw = b'\xe2\x97\x86 obsidian : Offline fixture\n\xe2\x97\x86 sqlitebrowser : Offline fixture\n\xe2\x97\x86 nvim : Offline fixture\n\xe2\x97\x86 nvim-nightly : Offline fixture\n'
elif url == source+'/programs/x86_64-portable':
    raw = b''
elif url == source+'/programs/archived-apps':
    raw = b'# ARCHIVED SOURCES\n'
elif url == source+'/programs/obsolete-apps':
    raw = b'# OBSOLETE SOURCES\n'
elif url == source+'/programs/x86_64-apps':
    raw = b'\xe2\x97\x86 obsidian : Offline fixture\n\xe2\x97\x86 sqlitebrowser : Offline fixture\n\xe2\x97\x86 nvim : Offline fixture\n\xe2\x97\x86 nvim-nightly : Offline fixture\n'
elif url.startswith(source+'/programs/x86_64/'):
    app = url.removeprefix(source+'/programs/x86_64/')
    if app == 'e2e-legacy' and (fixture/'legacy-recipe').is_file():
        raw = (fixture/'legacy-recipe').read_bytes()
    elif app in ('obsidian', 'sqlitebrowser', 'nvim', 'nvim-nightly'):
        raw = (Path('/src/programs/x86_64')/app).read_bytes()
elif url == 'https://api.github.com/repos/'+settings['repository']+'/commits/heads/release-catalog':
    raw = (settings['pin']+'\n').encode()
elif url.startswith('https://raw.githubusercontent.com/'+settings['repository']+'/'+settings['pin']+'/'):
    name = url.split('/'+settings['pin']+'/', 1)[1]
    if name in settings['catalog_paths']:
        raw = (fixture/'tree'/name).read_bytes()
elif url in settings['assets']:
    if settings.get('download_partial_fail'):
        output = download_destination(tool, args)
        if output is None:
            raise SystemExit('Partial transfer requires an output path')
        output.write_bytes((fixture/'binary').read_bytes()[:17])
        raise SystemExit(9)
    if settings.get('download_fail'):
        raise SystemExit(9)
    raw = (fixture/'binary').read_bytes()
elif any(url == asset+suffix for asset in settings['assets'] for suffix in
         ('.zsync','.digest','.DIGEST','.sha512','.sha512sum','.sha256','.sha256sum','.sha1','.sha1sum','.md5','.md5sum')):
    if settings.get('digest_missing'):
        raise SystemExit(22)
    digest = '0'*64 if settings.get('bad_digest') else hashlib.sha256((fixture/'binary').read_bytes()).hexdigest()
    raw = ('SHA-256: '+digest+'\n').encode()
if raw is None:
    (fixture/'unexpected'/f'{time.time_ns()}.json').write_text(json.dumps(record))
    print('Unexpected offline request: '+url, file=sys.stderr)
    raise SystemExit(22)
if tool == 'wget':
    download_destination(tool, args).write_bytes(raw)
elif tool == 'curl':
    output = download_destination(tool, args)
    if output:
        output.write_bytes(b'' if head else raw)
    elif not head:
        sys.stdout.buffer.write(raw)
    if '--write-out' in args:
        print('200', end='')
else:
    raise SystemExit('Unsupported adapter: '+tool)
