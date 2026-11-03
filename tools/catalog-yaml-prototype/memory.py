#!/usr/bin/env python3
"""Offline resource experiment; one subprocess at a time, bounded synthetic files."""
import copy, json, os, pathlib, subprocess, tempfile
from experiment import repository, document
HERE=pathlib.Path(__file__).resolve().parent

def main():
    results=[]
    with tempfile.TemporaryDirectory() as td:
        root=pathlib.Path(td)
        for interpreter in ('mawk','gawk','busybox'):
            shim=root/interpreter; shim.mkdir()
            (shim/'awk').write_text('#!/bin/sh\nexec '+interpreter+(' awk' if interpreter=='busybox' else '')+' "$@"\n')
            (shim/'awk').chmod(0o755)
            env=dict(os.environ, PATH=str(shim)+':'+os.environ['PATH'])
            subprocess.run(['python3',str(HERE/'experiment.py')],env=dict(env, AM_YAML_AWK_PATH=str(shim)),check=True)
            for shape,count in [('releases',100),('releases',1000),('releases',10000),('assets',8000),('apps',10000)]:
                obj=repository(); example=obj['releases'].pop('456')
                if shape=='releases':
                    example['assets']={str(i):copy.deepcopy(example['assets']['789']) for i in range(1,9)}
                    obj['releases']={str(i):example for i in range(1,count+1)}
                    args=['rows','releases','published_at','prerelease']
                elif shape=='assets':
                    asset=example['assets']['789'];example['assets']={str(i):asset for i in range(1,count+1)}
                    obj['releases']={'456':example};args=['rows','releases/456/assets','name','size']
                else:
                    obj={k:obj[k] for k in ('format','schema')};obj['apps']={f'app{i:05}':123 for i in range(count)};args=['apps']
                text=document(obj); fixture=root/'fixture.yaml';fixture.write_text(text)
                metrics=root/'time'; output=root/'output'
                with output.open('wb') as out:
                    run=subprocess.run(['/usr/bin/time','-f','%M %e','-o',str(metrics),'sh',str(HERE/'reader.sh'),args[0],str(fixture),*args[1:]],stdout=out,stderr=subprocess.PIPE,env=env)
                if run.returncode: raise RuntimeError(run.stderr.decode())
                rss,seconds=metrics.read_text().split()
                lines=sum(1 for _ in output.open('rb'))
                assert lines==count
                results.append(dict(awk=interpreter,shape=shape,records=count,input_bytes=fixture.stat().st_size,output_bytes=output.stat().st_size,peak_rss_kib=int(rss),seconds=float(seconds)))
                print(json.dumps(results[-1]),flush=True)
    (HERE/'memory-results.json').write_text(json.dumps(results,indent=2)+'\n')
if __name__=='__main__': main()
