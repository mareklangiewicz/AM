"""Positive recipe predicates over exact Git bytes. Never evaluate shell."""
import hashlib
import json
from pathlib import Path
import re
import sys
from contracts import pin
from publication import git

RECONSTRUCTION=Path(__file__).resolve().parents[1]/'recipe-reconstruction'
if str(RECONSTRUCTION) not in sys.path: sys.path.insert(0,str(RECONSTRUCTION))
from reconstruct import from_short, TEMPLATE, Unsupported
from originals import Catalogue, Originals


class Evaluator:
    def __init__(self, repo, inputs, evaluated_at):
        self.repo=repo; self.inputs=inputs; self.at=evaluated_at
        for value in inputs.values(): pin(value)
        self.recipe_pin=inputs['recipes']
        self.paths={}
        for row in git(repo,'ls-tree','-rz',self.recipe_pin,'--','programs/').split(b'\0'):
            if row:
                metadata,path=row.split(b'\t',1); mode,kind,oid=metadata.split(b' ')
                if mode==b'100644' and kind==b'blob': self.paths[path.decode()]=oid.decode()
        self.originals=Originals(repo); self._catalogue=None
        # Bind the complete module/policy tree, including transitive helper inputs.
        module_tree=git(repo,'ls-tree','-rz',inputs['policy'],'--','modules/')
        self.shared_dependencies={'modules':dict(repository='mareklangiewicz/AM',commit=inputs['policy'],
                                                   path='modules/',sha256=hashlib.sha256(module_tree).hexdigest())}

    def dependency(self, commit, path):
        raw=git(self.repo,'show',pin(commit)+':'+path)
        return dict(repository='mareklangiewicz/AM',commit=commit,path=path,sha256=hashlib.sha256(raw).hexdigest())

    def classify(self, app, arch, rid, *, prior=None, review=None):
        result=dict(repository_id=rid,availability='absent',classification='unknown')
        path=f'programs/{arch}/{app}'
        blob=self.paths.get(path)
        if blob is None: return result
        result.update(availability='present',recipe=dict(repository='mareklangiewicz/AM',commit=self.recipe_pin,path=path,blob=blob))
        raw=git(self.repo,'cat-file','blob',blob)
        if len(raw)>1024*1024: return result
        digest=hashlib.sha256(raw).hexdigest()
        try: text=raw.decode('utf-8')
        except UnicodeDecodeError: return result
        evidence=dict(evaluated_at=self.at,recipe_sha256=digest,rules=self.inputs['rules'])
        # A reuse assertion must match the complete pin, rule and dependency set.
        if prior and prior.get('recipe')==result['recipe'] and prior.get('evidence',{}).get('recipe_sha256')==digest and prior['evidence']['rules']==self.inputs['rules']:
            old=prior['evidence']; deps=old['dependencies']
            if prior['classification']=='shared' and deps==self.shared_dependencies:
                return prior
            if prior['classification'] in ('template','custom') and all(self.dependency(v['commit'],v['path'])==v for v in deps.values()):
                return prior
        try:
            declaration=from_short(text,TEMPLATE)
            declared=re.search(r'^CATALOG_REPOSITORY_ID=([1-9][0-9]*)$',text,re.M)
            if declaration['app']!=app or not declared or int(declared[1])!=rid:
                raise Unsupported('source identity')
            evidence.update(method='whole_wrapper',dependencies=self.shared_dependencies)
            return dict(result,classification='shared',evidence=evidence)
        except (ValueError,KeyError): pass
        if self._catalogue is None:
            metadata=json.loads((RECONSTRUCTION/'provenance.json').read_text())
            try: self._catalogue=Catalogue(self.originals,[metadata['fixture_commit'],metadata['upstream_commit']])
            except ValueError: self._catalogue=False
        if self._catalogue:
            classified=self._catalogue.check(text)
            match=next((m for m in classified['matches'] if m['status']=='instance'),None)
            if match:
                commit,template=match['template'].split(':',1)
                deps={'template':self.dependency(commit,template),'generator':self.dependency(commit,'modules/template.am')}
                evidence.update(method='whole_template',dependencies=deps)
                return dict(result,classification='template',evidence=evidence)
        # Custom requires an explicit reviewed record bound to these exact inputs.
        if review and review.get('recipe_sha256')==digest and review.get('rules')==self.inputs['rules'] and review.get('recipe')==result['recipe'] and review.get('description'):
            deps=review.get('dependencies',{})
            if all(self.dependency(v['commit'],v['path'])==v for v in deps.values()):
                evidence.update(method='reviewed_custom',description=review['description'],dependencies=deps)
                return dict(result,classification='custom',evidence=evidence)
        return result


def review_url(binding):
    recipe=binding.get('recipe')
    if not recipe: return None
    return f"https://github.com/{recipe['repository']}/blob/{pin(recipe['commit'])}/{recipe['path']}"
