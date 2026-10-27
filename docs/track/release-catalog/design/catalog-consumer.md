# Read-only pinned catalog consumer

Ticket 19, 2026-10-27. Implements the next public-read seam after the two successful
publication runs. It returns exact stored response bytes and does not rank releases,
select assets, modify app scripts, publish, collect upstream metadata or schedule jobs.

## API and CLI

consumer.lookup(alias, commit=None, stale_acceptance=None, fetch, utcnow, monotonic)
returns (exact_body_bytes, observation_metadata). Default scope is the fixed
mareklangiewicz/AM publication branch release-catalog and trusted workflow repository
ID 1291019762. Fetch and clocks are injectable for deterministic tests. There is no
credential argument, ambient token lookup or upstream fallback.

Without a commit, one unauthenticated GitHub ref GET supplies a full publication
SHA. It must identify precisely refs/heads/release-catalog and an object of type
commit. Fetch index.json and only the requested body from raw.githubusercontent.com
at that same full commit. The branch is never resolved a second time, even when a
file is missing or another publisher advances it. Supplying --commit skips ref
resolution and gives two GETs; default lookup uses at most three. The alias is a
consumer lookup key, never a network destination.

From the repository root, for example:

```sh
python3 -B tools/catalog-collector/consumer.py \
  https://api.github.com/repos/obsidianmd/obsidian-releases/releases/latest \
  --metadata /tmp/am-catalog-read.json | jq -r .tag_name
```

The CLI emits only exact body bytes on stdout, after all checks. --metadata is an
optional separate JSON file with commit/request/body/index hashes, original receipt
and validation times, checked time, age, accepted-stale flag, source/run provenance
and pinned URLs. Failure emits a fixed JSON diagnostic on stderr and nonzero exit,
without a partial stdout body. The caller controls output redirection; no cache,
installer state or default file is created by the CLI.

A stale refusal also supplies an exact acceptance object. A user may pass
--accept-stale COMMIT REQUEST_ID BODY_SHA256 to approve those specific bytes in
that specific publication; there is no blanket allow-stale flag. This mechanism
records caller intent in metadata and does not itself provide a persistent consent
store or an installer UI.

## Shared metadata and policy

storage.validate_index validates the full index metadata separately from body IO:
schema, exact embedded manifest/hash, descriptor/repository identities, active and
retired alias states, all times, measured bases, observation statuses, body paths,
length/digest declarations, validators and declared whole-tree byte budget.
validate(tree) reuses it and adds closed-file/body/content checks. This keeps
publisher and selective consumer validation aligned without fetching every body.
The refactor preserves the byte-tree format and requires no republishing.

reader.select is the shared pure policy for this client and local pinned reads.
It requires the trusted catalog repository identity, a full commit and validated
index; unknown/unavailable/retired sources and inactive aliases refuse. The selected
body is checked for exact length/SHA256 and public release content without changing
its bytes. Identity, paths, integrity or time failures cannot be bypassed by stale
acceptance. Hashes prove consistency with the selected trusted publication, not
independent upstream binary authenticity.

Fresh means validation age <=86,400 seconds, inclusive. Receipt and validation
remain distinct; index generation time never refreshes an observation. Future
publication/observation timestamps and unmeasured provenance refuse. Greater age
requires the exact commit/request/hash acceptance tuple; a newer commit requires
new consent even for identical bytes. Evaluate freshness before requesting the
body and again after IO; crossing expiry or regressing the local wall clock refuses
before stdout output. There is no clock-skew tolerance or negative-age clamping.

## Public transport bounds

public_http.get accepts only the fixed ref URL or full-SHA raw catalog index/body
paths. It invokes /usr/bin/curl on POSIX/Linux, with -q first, an allowlisted
PATH/LANG environment, no proxy, no auth/config/netrc options, TLS verification,
identity content encoding, no redirects and no retries. No tokens or installed-app
configuration are read. It never requests a supplied upstream release alias.

A parent nonblocking pipe loop bounds aggregate/interim response headers at 64 KB,
header lines/public values at 8,192 bytes, parses only strict CRLF header fields and
requires HTTP 200. Reject duplicate/ambiguous lengths, compression, malformed fields,
partial bodies and curl failure. Curl handles HTTP transfer decoding; retained body
bytes are independently checked against length/hash. Per-request connect <=10 s,
overall <=30 s; complete lookup <=90 s. The parent kills/reaps deadline or overflow
failures, including a trickling stdout. These are process-supervision bounds, not
hard real-time OS guarantees. Resolve body cap is 64 KB, index cap 2 MB, and selected
body cap is its index length (at most 8 MB). Declared full tree remains <=50 MB.

## Validation envelope

All original collector/storage/delivery tests plus focused selective-reader and
fake-process transport checks run offline. They cover one resolution/two pinned
reads, branch movement, missing resources without fallback, inclusive expiry,
exact stale scope, post-IO expiry/clock regression, future/unmeasured/unavailable/
removed aliases, integrity/metadata mutations, isolated process environment, strict
HTTP framing/bounds, hung/trickling child cleanup and no partial CLI output.

Live verification uses only the current public catalog: one default lookup (three
GETs) and one explicit-commit lookup (two GETs), compare exact bytes/hashes and
existing filter output, then record source and publication commits. No new source
collection, publication or Actions dispatch is necessary. Existing installed
updaters remain unchanged. Broader portability, caching/batching, persistent stale
consent UI and app integration remain separate work.

## Verified result

[Consumer findings](../research/consumer-read-findings.md) record 80 passing offline
tests and two successful actual CLI reads at d612ff34b, with exact byte comparison
to saved publication evidence and jq filter compatibility. No collection or workflow
dispatch was needed; no installed updater changed.
