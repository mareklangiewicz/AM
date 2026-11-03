#!/usr/bin/env python3
"""Bounded metadata-only sample. Raw API bodies and credentials stay in memory."""
import datetime, json, math, os, pathlib, random, re, subprocess, time, urllib.request, urllib.error
ROOT = pathlib.Path(__file__).resolve().parents[5]
OUT = pathlib.Path(__file__).resolve().parent
INVENTORY = ROOT / 'docs/track/release-catalog/research/appimage-exceptions-next-20261102/prepared/inventory.json'
MAX_CALLS, MAX_BODY, MAX_TOTAL, MAX_SECONDS = 24, 16*1024*1024, 96*1024*1024, 120

def quote(value):
    return json.dumps(value, ensure_ascii=False)

def projected(releases):
    # Size experiment only: candidate normalized YAML, not a format implementation.
    lines = ['format: 2', 'releases:']
    fields = ('tag_name', 'name', 'html_url', 'created_at', 'published_at', 'updated_at', 'prerelease')
    afields = ('name', 'browser_download_url', 'size', 'content_type', 'digest')
    for r in sorted(releases, key=lambda x:x['id']):
        lines.append(f'  "{r["id"]}":')
        for key in fields:
            if key in r: lines.append(f'    {key}: {quote(r[key])}')
        lines.append('    assets:')
        for a in sorted(r.get('assets', []), key=lambda x:x['id']):
            lines.append(f'      "{a["id"]}":')
            for key in afields:
                if key in a: lines.append(f'        {key}: {quote(a[key])}')
    return len(('\n'.join(lines)+'\n').encode())

def main():
    ids=set()
    for shard in json.loads(INVENTORY.read_text())['shards'].values():
        for source in json.loads((ROOT/shard['path']).read_text())['sources']:
            ids.add(source['repository_id'])
    # Explicit maintained histories selected for possible frequent releases;
    # identities are verified against the same active inventory.
    sampled=[16408992,984423768,5736080,15379620,162045852]
    assert set(sampled)<=ids
    token=os.environ.get('GH_TOKEN') or os.environ.get('GITHUB_TOKEN')
    if not token:
        auth=subprocess.run(['gh','auth','token'],capture_output=True,text=True,timeout=15)
        if auth.returncode == 0: token=auth.stdout.strip()
    start=time.monotonic(); calls=0; total=0; rows=[]; buffers={}
    report={'started_at':datetime.datetime.now(datetime.timezone.utc).isoformat(), 'selection':'five explicit active histories; not random',
            'inventory_repositories':len(ids), 'sample_size':len(sampled), 'authenticated':bool(token),
            'limits':{'calls':MAX_CALLS,'body_bytes':MAX_BODY,'total_bytes':MAX_TOTAL,'seconds':MAX_SECONDS}, 'rows':rows}
    def fetch(rid,page):
        nonlocal calls,total
        if calls>=MAX_CALLS or time.monotonic()-start>=MAX_SECONDS: raise RuntimeError('budget')
        url=f'https://api.github.com/repositories/{rid}/releases?per_page=100&page={page}'
        headers={'Accept':'application/vnd.github+json','X-GitHub-Api-Version':'2022-11-28','User-Agent':'AM-catalog-history-measurement','Accept-Encoding':'identity'}
        if token: headers['Authorization']='Bearer '+token
        req=urllib.request.Request(url,headers=headers); then=time.monotonic(); calls+=1
        # Direct GitHub API only, no proxy or redirect following.
        class NoRedirect(urllib.request.HTTPRedirectHandler):
            def redirect_request(self,*args,**kwargs): return None
        opener=urllib.request.build_opener(urllib.request.ProxyHandler({}),NoRedirect())
        with opener.open(req,timeout=min(25,max(1,MAX_SECONDS-(time.monotonic()-start)))) as resp:
            cap=min(MAX_BODY,MAX_TOTAL-total)
            declared=resp.headers.get('Content-Length')
            if declared is not None and (not declared.isdigit() or int(declared)>cap):
                raise RuntimeError('declared_byte_budget')
            if resp.headers.get('Content-Encoding', 'identity') != 'identity':
                raise RuntimeError('unsupported_encoding')
            raw=resp.read(cap)
            if declared is None and len(raw)==cap:
                raise RuntimeError('unproven_eof_at_byte_budget')
            if declared is not None and len(raw)!=int(declared):
                raise RuntimeError('incomplete_body')
            total+=len(raw); value=json.loads(raw)
            if type(value) is not list: raise RuntimeError('not_list')
            link=resp.headers.get('Link','')
            last=re.search(r'[?&]page=(\d+)>; rel="last"',link)
            # URLs include per_page before page in this probe.
            return value,{'page':page,'release_count':len(value),'bytes':len(raw),'elapsed_seconds':round(time.monotonic()-then,4),'last_page':int(last[1]) if last else None,'has_next':'rel="next"' in link,'rate_remaining':resp.headers.get('X-RateLimit-Remaining')}
    stop=None
    for rid in sampled:
        row={'repository_id':rid,'pages':[]};rows.append(row)
        try:
            values,meta=fetch(rid,1); row['pages'].append(meta);buffers[rid]=values
            row['page1_yaml_bytes']=projected(values)
            row['complete']=not meta['has_next']
            row['estimated_pages']=meta['last_page'] or (1 if row['complete'] else None)
        except Exception as exc:
            row['error']=type(exc).__name__+(':'+str(exc.code) if isinstance(exc,urllib.error.HTTPError) else '')
            stop=row['error'];break # No retry; do not consume budget after transport/auth/rate refusal.
    if not stop:
        for row in sorted(rows,key=lambda r:r.get('estimated_pages') or 10**9):
            pages=row['estimated_pages'];rid=row['repository_id']
            if row['complete'] or not pages or pages-1>MAX_CALLS-calls: continue
            try:
                for page in range(2,pages+1):
                    values,meta=fetch(rid,page);row['pages'].append(meta);buffers[rid].extend(values)
                row['complete']=not row['pages'][-1]['has_next']
            except Exception as exc:
                row['error']=type(exc).__name__+(':'+str(exc.code) if isinstance(exc,urllib.error.HTTPError) else '')
                stop=row['error'];break
    for row in rows:
        if row['repository_id'] in buffers:
            values=buffers[row['repository_id']]
            row['measured_releases']=len(values);row['distinct_releases']=len({r['id'] for r in values})
            row['measured_assets']=sum(len(r.get('assets',[])) for r in values)
            row['projected_yaml_bytes']=projected(values)
    report.update(calls=calls,total_bytes=total,elapsed_seconds=round(time.monotonic()-start,4),stop_reason=stop)
    (OUT/'results.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:report[k] for k in ('inventory_repositories','sample_size','authenticated','calls','total_bytes','elapsed_seconds','stop_reason')}))
if __name__=='__main__': main()
