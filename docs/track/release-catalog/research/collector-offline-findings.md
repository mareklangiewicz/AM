# Restricted collector offline implementation findings

2026-10-27. [Ticket 12](../issues/12-offline-restricted-collector.md).
Implementation: `tools/catalog-collector/collector.py`; runnable synthetic replay:
`tools/catalog-collector/replay.py`; focused checks: `test_collector.py`.
[Replay report](collector-offline-replay.json).

## Result

The pure planner and bounded injected collection loop are implemented. Seventeen
focused offline tests pass, as do the existing eight offline churn tests. The
historical churn collector and workflow were not modified. No network transport,
live CLI, workflow integration, installed-app change or dispatch was introduced.

- Plans and prior inputs use frozen records. The collector revalidates the plan
  against a separately supplied current workflow repository ID before fake calls.
  Missing/own/conflicting numeric and name identities, aliases and invalid prior
  bodies/validators refuse. The current identity must eventually come from a
  trusted workflow adapter, not from an artifact's own assertion.
- Credentials have no default or environment lookup and must be opaque objects.
  Only transport receives the object. Its repr is never invoked and transport
  exception text is discarded, even when the transport raises the core's own
  refusal class with secret text. Public header allowlisting and total/value limits
  apply before retained metadata is emitted.
- Headers include actual conditional-request evidence. Merely planning a validator
  is insufficient for a 304: transport must report the matching condition sent,
  and prior bytes/hash/descriptor must already be valid. Missing current prior or
  evidence refuses without retry. Prior state is never modified.
- Exact bytes, request start, response completion and attempt finish remain distinct.
  Partial/truncated/oversized/timed-out responses have no candidate body or response
  completion time. HTTP errors and invalid JSON remain inert transport data;
  storage is responsible for content/availability acceptance.
- Connect/request/batch deadlines are absolute monotonic deadlines. Slow chunks
  do not restart a request timeout. Every event boundary is checked and the same
  deadlines are supplied to the injected transport. Size equality is allowed;
  deadline equality expires. Consumed chunks count toward received bytes even
  when arriving too late to enter a candidate response.
- Six-attempt maximum, zero implicit redirects/retries/pagination/metadata/quota
  reads, explicit stop reason and not-attempted sources are verified. Quota reserve,
  Retry-After, missing/malformed quota evidence and authentication failure stop
  further attempts. Two consecutive transport/5xx failures stop; other complete
  statuses reset that streak.

## Replay observations

All identities, timestamps and bytes below are synthetic; these are not newly
observed upstream responses.

| Scenario | Attempts | Complete transfers | Bytes received | Elapsed seconds | Stop |
| --- | ---: | ---: | ---: | ---: | --- |
| Baseline fixture | 6 | 6 | 24 | 6 | none |
| Matching conditional fixture | 6 | 6 | 0 | 0 | none |
| Slow-stream fixture | 2 | 0 | 10 | 60 | consecutive failures |

The conditional fixture clock begins after the baseline; zero elapsed time is an
injected fixture property, not a claim that HTTP completes instantly. The slow
fixture reaches the whole-request timeout after 30 seconds twice, leaving four
sources explicitly not attempted. No partial bytes become observations.

## Reproduction

From the AM checkout, Python 3.10+ standard library only:

```sh
python3 -B tools/catalog-collector/replay.py
python3 -B -m unittest discover -s tools/catalog-collector -p 'test_*.py' -v
python3 -B -m unittest discover -s tools/catalog-probe -p 'test_churn.py' -v
```

The replay emits JSON to stdout, without touching files or credentials. The
implementation has no executable collection command. The tests include overflow
and tampered-input cases rather than merely mirroring the happy path.

## Integration limits

The collector cannot interrupt arbitrary Python code blocked inside transport.
A real network adapter must enforce the supplied deadlines around connection and
all body IO, bound allocations before yielding events, report actual conditional
values and avoid ambient credentials/proxies/config. Fake event checks do not
prove socket cancellation. This limitation is explicit in the module and README.

Opaque credential and repository-ID parameters cannot prove their provenance.
The eventual workflow must establish built-in token scope and trusted current ID;
reviewed identity evidence must establish owner/name mappings. No complete real
six-source identity manifest has been enrolled under this contract. Missing IDs
remain unrunnable; the core does not fetch metadata to fill them in.

Reports' `complete` and `outcome=response` mean complete HTTP transfers, not valid
release observations or successful publication. Storage owns shape/draft validation,
availability, index/tree limits and atomic publication; it is not yet integrated
with this collector. Header/body limits are implemented here, while history size
belongs to publication. The previous storage/freshness prototypes remain primary
sources on their separate branches rather than production dependencies.

The next [adapter/manifest review](../issues/13-prepare-adapter-and-enrollment-review.md)
must resolve concrete IO and identity prerequisites before any live wiring/run.
No new throughput, public-visibility or hosting claim follows from these tests.
