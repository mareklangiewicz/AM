"""Generate closed editor schemas and reader field tables from one contract."""
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
D = {}
def scalar(type, **kw): return dict(type=type, **kw)
def ref(name): return {'$ref':'#/$defs/'+name}
def obj(name, fields, required=None):
    D[name] = dict(type='object', properties=fields, required=list(fields) if required is None else required,
                   additionalProperties=False)
    return ref(name)
def table(name, pattern, value):
    D[name] = dict(type='object', patternProperties={pattern:value}, additionalProperties=False)
    return ref(name)
S=scalar('string'); B=scalar('boolean'); N=scalar('integer', minimum=0, maximum=9223372036854775807)
ID=scalar('integer',minimum=1,maximum=9223372036854775807)
PIN=scalar('string',pattern='^[0-9a-f]{40}$')
HASH=scalar('string',pattern='^[0-9a-f]{64}$')
TIME=scalar('string',format='date-time',pattern='^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$')
URL=scalar('string',pattern='^https://[^/\\s][^\\s]*$')
NAME='[a-z0-9][a-z0-9_.+-]{0,63}'
PATH=scalar('string',pattern='^repositories/'+NAME+'\\.yaml$')
SCHEMA=lambda version: scalar('string',pattern='^https://raw\\.githubusercontent\\.com/mareklangiewicz/AM/[0-9a-f]{40}/docs/catalog-format-v'+str(version)+'\\.md$')
ENUM=lambda *values: scalar('string',enum=list(values))
INPUTS=obj('inputs',dict(source=PIN,policy=PIN,recipes=PIN,rules=PIN,schemas=PIN))
RUN=obj('run',dict(id=ID,attempt=ID))
MEASUREMENT=obj('measurement',dict(state=ENUM('known','unknown'),value=N),['state'])
COUNTS=obj('counts',{k:MEASUREMENT for k in ('enrolled','selected','attempted','successful','failed','unknown','unattempted','deferred')})
STAGE=ENUM('ok','partial','failed','unknown','not_attempted')
PUB=obj('publication',dict(state=ENUM('confirmed','conflict','failed','unknown','not_attempted'),commit=PIN),['state'])
REASON=ENUM('transport','authentication','quota','request_budget','byte_budget','time_budget','source_validation','document_overflow','candidate_validation','parent_conflict','publication_transport','internal','unknown')
ASSET=obj('asset',dict(name=S,url_suffix=S,url=URL,size=N,media_type=S,digest=S),['name','size'])
ASSETS=table('assets','^[1-9][0-9]*$',ASSET)
RELEASE=obj('release',dict(observed_at=TIME,tag=S,title=S,url=URL,created_at=TIME,published_at=TIME,updated_at=TIME,prerelease=B,source_zip_url=URL,source_tar_url=URL,download_base=URL,assets=ASSETS),['tag','url','prerelease','assets'])
RELEASES=table('releases','^[1-9][0-9]*$',RELEASE)
SCOPE=obj('scope',dict(page_size=scalar('integer',minimum=1,maximum=100),pages_fetched=ID,history_complete=B))
BINDING=obj('binding',dict(repository=scalar('string',pattern='^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$'),commit=PIN,path=scalar('string',pattern='^programs/(x86_64|aarch64|i686|armv7l)/'+NAME+'$'),blob=PIN))
DEPENDENCY=obj('dependency',dict(repository=S,commit=PIN,path=S,sha256=HASH))
DEPENDENCIES=table('dependencies','^'+NAME+'$',DEPENDENCY)
EVIDENCE=obj('evidence',dict(method=ENUM('whole_wrapper','whole_template','reviewed_custom'),evaluated_at=TIME,recipe_sha256=HASH,rules=PIN,dependencies=DEPENDENCIES,description=S),['method','evaluated_at','recipe_sha256','rules','dependencies'])
PROV=obj('provenance_binding',dict(repository_id=ID,availability=ENUM('present','absent','unknown'),classification=ENUM('shared','template','custom','unknown'),recipe=BINDING,evidence=EVIDENCE),['repository_id','availability','classification'])
ARCHES=table('architectures','^(x86_64|aarch64|i686|armv7l)$',PROV)
PROVS=table('provenance_apps','^'+NAME+'$',ARCHES)
RUNREFS=table('run_references','^[1-9][0-9]*-[1-9][0-9]*$',scalar('string',pattern='^runs/[1-9][0-9]*-[1-9][0-9]*/summary\\.yaml$'))
DETAILS=table('detail_references','^[1-9][0-9]*-[1-9][0-9]*$',TIME)
METRICS=obj('metrics',{k:MEASUREMENT for k in ('http_attempts','charged_bytes','received_bytes','acquisition_milliseconds','command_milliseconds','tree_bytes','largest_document_bytes','local_object_bytes','packed_history_bytes','remote_storage_bytes','peak_rss_bytes')})
BUDGETS=obj('budgets',{k:N for k in ('requests','bytes','acquisition_milliseconds','document_bytes')})
FRESH=obj('freshness',dict(catalog=PIN,evaluated_at=TIME,under_24h=MEASUREMENT,from_24_to_48h=MEASUREMENT,at_least_48h=MEASUREMENT,no_success=MEASUREMENT,unknown=MEASUREMENT))
DAILY=obj('daily',dict(reported_attempts=N,successful_sources=N,failed_sources=N,first_report=TIME,last_report=TIME))
DAYS=table('days','^[0-9]{4}-[0-9]{2}-[0-9]{2}$',DAILY)
def root(kind, version, fields):
    return obj(kind,dict(format=scalar('integer',const=version),schema=(SCHEMA(3) if version==3 else scalar('string',pattern='^https://raw\\.githubusercontent\\.com/mareklangiewicz/AM/[0-9a-f]{40}/docs/catalog-status-v1\\.md$')),kind=scalar('string',const=kind),**fields))
root('catalog',3,dict(inputs=INPUTS,producer=RUN,retention=scalar('string',const='32-plus-stable-exact-tag-v1')))
root('apps',3,dict(apps=table('app_paths','^'+NAME+'$',PATH)))
root('repository',3,dict(repository_id=ID,repository=scalar('string',pattern='^[A-Za-z0-9-]+/[A-Za-z0-9_.-]+$'),collected_at=TIME,scope=SCOPE,observed_at=TIME,releases=RELEASES))
root('provenance',3,dict(apps=PROVS))
root('status',1,dict(schemas=PIN,last_report=scalar('string',pattern='^runs/[1-9][0-9]*-[1-9][0-9]*/summary\\.yaml$'),reported_at=TIME,last_confirmed_publication=PUB,summaries=RUNREFS,details=DETAILS))
root('summary',1,dict(run=RUN,inputs=INPUTS,input_catalog=PIN,started_at=TIME,reported_at=TIME,collection=STAGE,validation=STAGE,publication=PUB,compatibility_publication=PUB,counts=COUNTS,stop_reason=REASON,metrics=METRICS,budgets=BUDGETS,actions_url=URL,recent_runs_url=URL))
root('source',1,dict(run=RUN,input_catalog=PIN,repository_id=ID,repository=scalar('string',pattern='^[A-Za-z0-9-]+/[A-Za-z0-9_.-]+$'),outcome=ENUM('ok','failed','unknown','unattempted'),reason=REASON,attempted_at=TIME,completed_at=TIME,output_catalog=PIN))
D['source']['required']=['format','schema','kind','run','input_catalog','repository_id','repository','outcome']
root('statistics',1,dict(measured_at=TIME,freshness=FRESH,days=DAYS))
KINDS=['catalog','apps','repository','provenance','status','summary','source','statistics']
# Editor schemas supplement exact-byte/domain readers; conditional relationships
# are enforced by those readers, including exact integer and timestamp checks.
for kind in KINDS:
    schema={'$schema':'https://json-schema.org/draft/2020-12/schema',
            'title':'AM '+kind,'description':'Closed mapping-only AM contract; canonical order and cross-document semantics require the maintained readers.',
            '$ref':'#/$defs/'+kind,'$defs':D}
    (ROOT/'schemas/catalog'/f'{kind}.schema.json').write_text(json.dumps(schema,indent=2)+'\n')
(ROOT/'tools/catalog-contract/definitions.json').write_text(json.dumps(dict(kinds=KINDS,definitions=D),indent=2)+'\n')
(ROOT/'tools/catalog-contract/definitions.mjs').write_text('// Generated by build.py. Do not edit.\nexport default '+json.dumps(dict(kinds=KINDS,definitions=D),separators=(',',':'))+';\n')
# AWK loads no external schemas at runtime. Translate supported schema predicates
# into POSIX ERE/table data, keeping exact decimal bounds as strings.
def ere(s):
    s=s.replace('\\s','[:space:]') # URL uses a negated bracket expression
    import re
    def expand(m):
        char,count=m.group(1),int(m.group(2)); return char*count
    s=re.sub(r'(\[[^\]]+\]|\\.|[A-Za-z0-9])\{(\d+)\}',expand,s)
    s=s.replace('{0,63}','*') # length <=64 checked separately on table keys
    return s
lines=['# Generated by tools/catalog-contract/build.py.','BEGIN {']
q=lambda x:json.dumps(str(x))
for name,schema in D.items():
    props=schema.get('properties',{})
    lines.append(f' fields[{q(name)}]={q(" ".join(props))}')
    lines.append(f' required_fields[{q(name)}]={q(" ".join(schema.get("required",[])))}')
    rules=props or schema.get('patternProperties',{})
    if not props:
        pattern,value=next(iter(rules.items()))
        lines.append(f' key_pattern[{q(name)}]={q(ere(pattern))}')
        rules={'*':value}
    for field,rule in rules.items():
        key=name+'/'+field
        if '$ref' in rule:
            lines.append(f' child_type[{q(key)}]={q(rule["$ref"].split("/")[-1])}')
        else:
            lines.append(f' scalar_type[{q(key)}]={q(rule["type"])}')
            for predicate in ('pattern','minimum','maximum','const','format'):
                if predicate in rule:
                    val=ere(rule[predicate]) if predicate=='pattern' else rule[predicate]
                    lines.append(f' rule_{predicate}[{q(key)}]={q(val)}')
            if 'enum' in rule:
                lines.append(f' rule_enum[{q(key)}]={q("|"+"|".join(rule["enum"])+"|")}')
lines.append('}')
(ROOT/'modules/catalog-contract-tables.am').write_text('\n'.join(lines)+'\n')
