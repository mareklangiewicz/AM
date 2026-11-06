# Direct catalog browser — throwaway prototype

Three views on one new standalone route (there is no existing catalog UI):
A directory, B split-pane explorer, C release desk. Switch using the floating
arrows, keyboard arrows outside inputs, or `?variant=A|B|C`.

Run from this worktree:

```sh
python3 -m http.server 8765 --bind 127.0.0.1 --directory docs/track/catalog-pages/prototype
```

Open http://localhost:8765/ . Click an app to load its repository YAML.
Shareable URLs retain the exact catalog pin, selected app and variant.
Try `?variant=B&app=rclone` for the largest recorded repository.

## What this answers

The browser resolves release-catalog once through the public GitHub ref API,
then fetches unchanged YAML from immutable raw URLs. No copied data, generated
index, backend proxy, visitor credentials, enrichment calls or external runtime
packages. State/cache lives only in page memory. Ordinary navigation requests
are public read-only requests to GitHub. Latest snapshot explicitly resolves again.

The tiny parser accepts only the publisher's mapping-only subset and retains all
integers as decimal strings. It is **not** a production schema validator. UI uses
text escaping and HTTPS links. Platform matching is a filename heuristic, not AM
selection. No AM install recommendation is shown without pinned recipe policy.
Stable/nightly AM identities remain separate, with shared-repository siblings
shown on their detail pages. Descriptions and logos are absent; initials fill in.
Search covers AM names, not unloaded release bodies or enriched descriptions.

Release lists order by published time then numeric ID. Asset lists retain the
source order; no client selection policy is implied. Details expand on demand;
assets paginate 60 at a time. All upstream assets remain available. Unknown
platform names remain unknown. Observation timestamps and partial-history status
are shown; missing requests preserve pin and show an error. Use reload to retry.

## Measurements — November 6, 2026

Live pin observed: `03f63def325715a2621b5662b797ff967c8e439c`.
Public ref API and raw YAML both returned HTTP 200 and
`Access-Control-Allow-Origin: *` from shell/Node requests.

- apps.yaml: 1,474 bytes; 522 ms fetch; 2.07 ms parse.
- repositories/17803236.yaml (rclone): 1,142,139 bytes, 100 retained releases,
  4,258 assets; 429 ms fetch; 55.33 ms parse.
- 9223372036854775807 survived parsing exactly as decimal text.
- No third-party parser/runtime dependency. Inspect `wc -c` for uncompressed
  HTML/JS source size (approximately 15 KB).

Timings are one Node measurement, **not browser performance or readiness claims**.
No controllable browser was available in the session: visual layout, actual
browser CORS requests, mobile behavior, interactions and DOM responsiveness
still require browser review. Public GitHub API rate limits can block ref lookup;
explicit `?pin=FULL_SHA` skips it. Ref lookup is mutable; subsequent data reads
are pinned. No hidden fallback snapshot is substituted.

Review questions: Which layout works best? Keep stable/nightly entries separate
or group them? Is visible provenance enough? Are partial-history, unknown-platform
and filename-inference labels understandable? Browser measurements, accessibility,
search behavior with missing metadata and final rendering budgets remain open.

No deployment or repository Pages settings change. This code stays on
`prototype/catalog-pages` and is not merged into main.
