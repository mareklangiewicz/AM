/* THROWAWAY: pure offline contract. No IO; hash is an injected byte hash. */
const Freshness = (() => {
  const CAPS = {sources:6, body:8000000, index:2000000, tree:50000000, pack:128000000};
  const fail = (ok, reason) => { if (!ok) throw Error(reason); };
  const same = (a,b) => JSON.stringify(a) === JSON.stringify(b);
  const canonical = value => JSON.stringify(Object.fromEntries(Object.entries(value).sort(([a],[b])=>a.localeCompare(b))));
  function timestamp(value) {
    fail(typeof value === 'string' && /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,3})?(?:Z|\+00:00)$/.test(value), 'invalid timestamp');
    const n = Date.parse(value);
    fail(Number.isFinite(n) && new Date(n).toISOString().slice(0,19) === value.slice(0,19), 'invalid timestamp');
    return n;
  }
  function descriptor(d, hash, encode) {
    fail(d && same(Object.keys(d).sort(), ['accept','api_version','url']), 'descriptor fields');
    fail(d.accept === 'application/vnd.github+json' && d.api_version === '2022-11-28', 'representation');
    fail(/^https:\/\/api\.github\.com\/repos\/[A-Za-z0-9_.-]+\/[A-Za-z0-9_.-]+\/releases$/.test(d.url), 'unreviewed descriptor');
    return hash(encode(canonical(d)));
  }
  function caps(counts) {
    for(const k of Object.keys(CAPS)) fail(Number.isSafeInteger(counts[k]) && counts[k]>=0 && counts[k]<=CAPS[k], `limit: ${k}`);
  }
  function lookup(input, hash, encode) {
    const {index, commit, url, body, now, acceptance} = input;
    fail(/^[a-f0-9]{40}$/.test(commit), 'full commit required');
    fail(index.schema_version === 2, 'unsupported experimental schema');
    const generated=timestamp(index.generated_at), clock=timestamp(now);
    fail(generated<=clock,'future publication');
    const alias=index.aliases[url];
    fail(alias && alias.state === 'active', 'alias absent or removed');
    const rid=alias.request_id, entry=index.entries[rid];
    fail(entry && descriptor(entry.descriptor,hash,encode)===rid,'descriptor identity');
    fail(index.manifest.sources[rid] && descriptor(index.manifest.sources[rid],hash,encode)===rid, 'manifest identity');
    fail(index.manifest.aliases[url]===rid, 'alias identity');
    fail(entry.availability==='available','source unavailable');
    const o=entry.observation;
    fail(o && o.path===`bodies/${rid}.json` && o.scope==='single-response', 'observation path/scope');
    fail(o.received_time_basis==='response-completed' && o.validation_time_basis==='response-completed', 'historical timing is not measured freshness');
    const received=timestamp(o.received_at), validated=timestamp(o.validated_at);
    fail(received<=validated && validated<=generated && validated<=clock, 'observation chronology');
    fail(body && body.length===o.bytes && hash(body)===o.sha256, 'body integrity');
    const age=(clock-validated)/1000, key={commit,request_id:rid,sha256:o.sha256};
    const accepted=acceptance && same(Object.keys(acceptance).sort(),['commit','request_id','sha256']) &&
      acceptance.commit===key.commit && acceptance.request_id===key.request_id && acceptance.sha256===key.sha256;
    return {decision:age<=86400?'fresh':accepted?'accepted-stale':'acceptance-required', age_seconds:age,
      received_at:o.received_at,validated_at:o.validated_at,acceptance_key:key,
      latest_attempt:entry.latest_attempt,bytes:body.length};
  }
  function reenroll(entry) {
    return {...entry,availability:'unknown',validators:{},observation:null,
      historical_observation:entry.observation ?? entry.historical_observation ?? null};
  }
  function notModified(entry, at, condition) {
    fail(entry.observation && condition && Object.entries(condition).length>0 &&
      Object.entries(condition).every(([k,v])=>['etag','last-modified'].includes(k) && entry.validators[k]===v), '304 requires current body and matching condition');
    fail(timestamp(at)>=timestamp(entry.observation.validated_at),'304 chronology');
    return {...entry,availability:'available',latest_attempt:{at,status:304},
      observation:{...entry.observation,validated_at:at,validation_time_basis:'response-completed'}};
  }
  return {CAPS,caps,lookup,reenroll,notModified,descriptor,timestamp};
})();
if(typeof module!=='undefined') module.exports=Freshness;
