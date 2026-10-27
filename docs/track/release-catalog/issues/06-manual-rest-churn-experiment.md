# Run and interpret the bounded REST churn experiment

Type: task
Status: open
Triage: ready-for-human
Blocked by: 04

## Scope

Marek agreed to REST-first comparison and preparation. [04](04-compare-collection-strategies.md) is resolved. Read [experiment instructions](../../../../tools/catalog-probe/CHURN.md) and [comparison](../research/collection-strategy-comparison.md).

Prepared: six fixed endpoints; three manual observations around baseline, +1 hour and +24 hours; exact responses versus an offline stable-field diagnostic; per-body/round/time limits; no extra pagination or retries; preserved hashes, conditional state and actual timestamps; comparison in disposable local Git repos. The existing quota workflow adds three choices and remains manual-only. Repeat runs take a previous run ID and validate the complete prior evidence.

## Authorization boundary

Ask before pushing AM commits. A push is not run authorization. Each observation requires explicit instruction; no schedule or automated follow-up. Before dispatch verify sole active workflow and no pending runs. Unrelated workflows stay disabled. No app scripts or installed apps are changed.

## Acceptance

- Record each authorized run ID, source revision, actual interval, status and evidence hashes. Preserve evidence before seven-day artifact expiry.
- Inspect changed paths against original release/asset order and descriptions; do not equate positional changes with counter churn. Report filter diagnostic mismatches and unsupported events identity.
- Report body/gzip totals, changed-body frequency, loose objects and packed Git history for both layouts under identical index/timestamp policy.
- Treat this as a short-window sample. Record limitations and decide whether to widen measurement or revise representation with Marek; do not claim a fleet/annual growth forecast.

## Validation before live use

Seven offline fixture tests cover three-round chaining/304 reuse and analysis, HTTP failures with no retry, oversize/invalid JSON/unconditional 304/quota stop, prior-body corruption blocking requests, counter projection differences, first/last and description-URL filters, and sanitized transport failures. YAML/manual-only guard assertions and ShellCheck for workflow shell steps pass. Real Actions artifact chaining and live endpoint behavior remain untested.

## Comments

2026-10-27: Marek authorized and completed the push through 6f9648bb2, then explicitly authorized one baseline dispatch. [Run 40499617203 findings and persistent evidence](../research/churn-baseline-40499617203-findings.md): four successful responses, then WezTerm HTTP 301; round stopped at five attempts, SQLite unqueried. complete=false; do not use this run to seed hour/day. No retry, replacement baseline or endpoint-policy change is authorized. Investigate the redirect boundary before proposing the next run.

2026-10-27 follow-up: one separately agreed public read captured [WezTerm redirect evidence](../research/wezterm-redirect-investigation.md). Prepared the explicit repository-ID source from Location and bounded HTTP error evidence retention; redirects remain disabled. Eight offline tests pass, including the actual urllib HTTPError path. The target was not queried and no replacement run was dispatched. Awaiting push and separate replacement-baseline authorization.

2026-10-27: after Marek separately approved the push through 37bdb433c and one replacement dispatch, [baseline 40500475496 succeeded](../research/churn-baseline-40500475496-findings.md). All six responses were 200; body hashes and offline analysis validated. Exact bodies total 4,877,752 bytes, diagnostic projection 622,062; churn remains unmeasured. This complete run is the valid previous_run for a separately authorized churn-hour, targeted around 14:01 Europe/Warsaw today. No repeat or schedule authorized. Evidence preserved locally in tracked research files.

2026-10-27: Marek instructed continuation at the hour sampling point. [Run 40508899451 succeeded](../research/churn-hour-40508899451-findings.md), 63m25.878s after baseline. All six conditional GETs returned 200; all raw bodies changed only in 198 download-count and two reaction-count paths. Ordered identities and projections stayed equal. Packed history grew 4,324 bytes exact / 458 bytes projection. Evidence preserved. Next separately authorized day observation should use previous_run=40508899451 around 2026-10-28 13:01 Europe/Warsaw. No schedule, next dispatch or push authorized.
