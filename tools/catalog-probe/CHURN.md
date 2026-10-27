# Manual REST churn experiment

Agreed direction: exact REST observations first, with an offline smaller-field
projection as a diagnostic. No GraphQL requests, release ranking, downloads of
app binaries, installer execution, client integration or catalog publication.

The existing **Catalog quota probe** workflow gains choices `churn-baseline`,
`churn-hour`, and `churn-day`; `quota` preserves the earlier probe. It remains
workflow_dispatch only with the fork/event job guard. Pushes do not run it.
No workflow is added and unrelated workflow settings are unchanged.

## Bounds

- Six fixed GET endpoints: Obsidian list/latest, Neovim list/latest,
  WezTerm list?per_page=100 and sqlitebrowser list?per_page=100.
- At most six attempts per observation; no retries, redirects, extra pages,
  GraphQL or rate-limit endpoint requests. Requests are sequential.
- Each body is limited to 10 MiB plus one detection byte; 60-second socket
  timeout, ten-minute workflow job timeout. At most about 60 MiB of accepted
  bodies per round, 180 MiB over all three, plus bounded metadata/reports.
- Stop on HTTP failure, transport error, invalid JSON/shape, body cap or zero
  reported remaining quota. Partial evidence has complete=false and cannot
  seed a later round. Failed dispatches do not authorize another attempt.
- Later observations require the previous successful run ID. The workflow
  downloads only its named artifact, checks the workflow/event/branch/result,
  and the collector validates the preceding round sequence, manifest, body
  hashes, size and shapes before any upstream request. Artifact retrieval uses
  the separate Actions API and is outside the six upstream GET bound.
- Conditional GET uses the preceding ETag, or Last-Modified if no ETag exists.
  A valid 304 reuses exact prior bytes; validators omitted from 304 headers
  carry forward. A 200 retains the new exact bytes, including whitespace.
- Saved metadata contains only selected public response headers, status,
  UTC check time, source revision and body SHA-256. Authorization is not saved.

## Human-controlled sequence

Each dispatch requires Marek's explicit instruction. First review/approve the
prepared changes and push separately. Before an authorized dispatch, verify
the existing probe remains the sole active workflow and there are no pending
runs. Do not restore unrelated workflows.

1. Dispatch `churn-baseline`, leaving previous_run empty.
2. After separately authorized observation around +1 hour, dispatch
   `churn-hour` with the successful baseline run ID.
3. After separately authorized observation around +24 hours from baseline,
   dispatch `churn-day` with the successful hour run ID.

There is no timer, automatic follow-up or schedule. Labels describe intended
sampling points, not enforced delays; actual timestamps and elapsed seconds
are saved. Each artifact contains all completed previous observations plus the
new observation and comparison.json, with seven-day retention. Preserve the
final evidence locally and record run IDs/hashes in docs/track before expiry.

If a round fails, inspect its partial evidence before proposing a new run.
Do not silently reuse an incomplete observation, skip hour, or declare a
one-day interval that was not measured.

## Offline comparison

Run from the repository root:

```sh
python3 -m unittest discover -s tools/catalog-probe -p 'test_churn.py' -v
python3 tools/catalog-probe/churn.py analyze /path/to/artifact/observations
```

Analysis needs no token and makes no network requests. It validates all input
body hashes and creates two disposable Git repositories in the system temp
directory, then removes them. One uses exact bodies; the other keeps release
tag/name/creation/publication/prerelease/draft and asset name/size/digest/download
URL fields, retaining sequence. This projection is neither a GraphQL response
nor a replacement API contract.

Report body bytes, deterministic gzip bytes, byte changes, positional changed
JSON paths, cumulative loose Git object bytes, and final pack plus index bytes.
Both layouts use the same check-status/time index policy. Git ignores global
and system configuration, uses an empty template and fixed commit dates, disables
automatic GC and explicitly repacks with window=10/depth=50. The report records
Git's version; compression/library versions can still affect byte counts.
Loose object sizes measure file contents, not filesystem block allocation.

Two Python transcriptions of reviewed text filters compare Obsidian's first
AppImage match and WezTerm nightly's last match on exact/projected bodies.
They run no recipe code and do not determine collector output. They are
diagnostics for these filters only, not an installer compatibility guarantee.
Description URL matches, missing selections and differences require inspection.
WezTerm events-based identity remains outside release scope.

Changed JSON paths are positional: inserted/reordered releases may cause many
paths to change. Inspect original tag/asset sequences and fields before
attributing paths to counters versus membership/order edits. One short sample
cannot establish fleet coverage, long-term churn, Git retention cost, quota
capacity or annual growth. No annual extrapolation is produced automatically.
