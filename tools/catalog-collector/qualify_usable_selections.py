"""Count which recipe policies select something usable from a published v3 tree.

Runs the real client (`modules/catalog-yaml.am`) once per policy key against a
local copy of one catalog commit, at the current clock, with `curl` replaced by
a file-serving stand-in. No network, no payload download, no installation.
Outcomes are the client's own: a selection, or its refusal text.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
import threading
import time

ROOT=Path(__file__).resolve().parents[2]
AMREPO='https://raw.githubusercontent.com/mareklangiewicz/AM/main-marek'
CURL='''#!/bin/sh
# Stand-in for the client's fixed curl call: serve one pinned tree from disk.
out='' url=''
while [ "$#" -gt 0 ]; do
    case $1 in
        --output) out=$2; shift 2 ;;
        -H|--noproxy|--proto|--max-redirs|--connect-timeout|--max-time|--max-filesize|--write-out) shift 2 ;;
        -*) shift ;;
        *) url=$1; shift ;;
    esac
done
case $url in
    "https://raw.githubusercontent.com/mareklangiewicz/AM/$QUALIFY_PIN/"*)
        file=$QUALIFY_TREE/${url#"https://raw.githubusercontent.com/mareklangiewicz/AM/$QUALIFY_PIN/"}
        [ -f "$file" ] || { printf 404; exit 22; }
        cp "$file" "$out" && printf 200 ;;
    *) printf 000; exit 7 ;;
esac
'''
OUTPUT={'asset':'--url','release':'--tag','git-tag':'--tag','git-branch':'--git-commit','git-file':'--git-commit'}


def policy_keys(policy):
    """Every key the generated policy accepts, with its selection kind."""
    keys={}
    for match in re.finditer(r'^    recipes_repository\["([^"]+)"\]=',policy,re.M):keys[match[1]]='asset'
    for match in re.finditer(r'^    recipes_selection\["([^"]+)"\]="([a-z-]+)"',policy,re.M):keys[match[1]]=match[2]
    for match in re.finditer(r'if\(recipe=="([^"]+)"\) \{ image_policy=',policy):keys.setdefault(match[1],'asset')
    return keys


def reason(stderr):
    text=stderr.strip().splitlines()[-1] if stderr.strip() else 'no message'
    text=re.sub(r'^(catalog selection|AM YAML catalog): ','',text)
    if text.startswith('stale; retry'):return 'stale'
    return text


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--catalog',default='origin/release-catalog-v3',help='published v3 commit')
    parser.add_argument('--jobs',type=int,default=os.cpu_count() or 4)
    parser.add_argument('--limit',type=int,help='only the first N keys, for a trial')
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args()
    git=lambda *a:subprocess.run(['git','-C',ROOT,*a],check=True,capture_output=True,text=True).stdout.strip()
    pin=git('rev-parse',args.catalog+'^{commit}')
    keys=policy_keys((ROOT/'modules/catalog-yaml-policy.am').read_text())
    names=sorted(keys)[:args.limit]
    with tempfile.TemporaryDirectory(prefix='am-usable-') as temporary:
        base=Path(temporary);tree=base/'tree';tree.mkdir();fake=base/'bin';fake.mkdir()
        archive=subprocess.run(['git','-C',ROOT,'archive',pin],check=True,capture_output=True).stdout
        subprocess.run(['tar','-x','-C',tree],input=archive,check=True)
        (fake/'curl').write_text(CURL);(fake/'curl').chmod(0o755)
        environment=dict(os.environ,PATH=str(fake)+os.pathsep+os.environ['PATH'],AMREPO=AMREPO,
                         QUALIFY_PIN=pin,QUALIFY_TREE=str(tree),LC_ALL='C')
        local=threading.local();counter=iter(range(10**6));lock=threading.Lock()
        def run(key):
            # One command session per worker: the descriptor and app map are
            # fetched and validated once, as within one real `am` command.
            if not hasattr(local,'session'):
                with lock:local.session=base/('session-'+str(next(counter)))
                local.session.mkdir()
            result=subprocess.run(['sh',str(ROOT/'modules/catalog-yaml.am'),key,OUTPUT[keys[key]],'--commit',pin],
                env=dict(environment,AM_CATALOG_SESSION=str(local.session)),capture_output=True,text=True)
            if result.returncode==0 and result.stdout.strip():return key,'selected'
            failed=local.session/'yaml-v3/failed'
            # A transfer or validation refusal latches the session; the next
            # key must not inherit it.
            if failed.exists():failed.unlink()
            return key,reason(result.stderr)
        started=time.time()
        with ThreadPoolExecutor(args.jobs) as pool:rows=list(pool.map(run,names))
    counts={}
    for _,outcome in rows:counts[outcome]=counts.get(outcome,0)+1
    kinds={}
    for key in names:kinds[keys[key]]=kinds.get(keys[key],0)+1
    report=dict(catalog=pin,evaluated_at=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime(started)),
        policy_source=git('rev-parse','HEAD'),policy_keys=len(names),selection_kinds=kinds,
        outcomes=dict(sorted(counts.items(),key=lambda item:-item[1])),
        refused={key:outcome for key,outcome in rows if outcome not in ('selected','stale')})
    args.out.write_text(json.dumps(report,indent=1)+'\n')
    print(json.dumps(dict(policy_keys=len(names),outcomes=report['outcomes'],seconds=round(time.time()-started))))


if __name__=='__main__':main()
