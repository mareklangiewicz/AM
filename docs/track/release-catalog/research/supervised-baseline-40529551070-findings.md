# First supervised adapter live baseline

2026-10-27. [Run 40529551070](https://github.com/mareklangiewicz/AM/actions/runs/40529551070)
succeeded on attempt 1. Collection ran at 16:17:56–16:18:01 Europe/Warsaw.
Marek explicitly approved pushing enrollment, installing/pushing the prepared
manual workflow and running it once. Exactly one dispatch was issued; no retry,
repeat observation, schedule, publication or installed-app change followed.

## Result

All six planned numeric routes returned complete HTTP 200 responses in manifest
order, unconditionally. No endpoint was skipped; stop_reason is null. The adapter
reported **4,877,758 body bytes** in **5.19837244 seconds**. The full Actions job
(including checkout and artifact upload) succeeded. The candidate numeric latest
routes and SQLite route now have direct successful evidence for this sample.

| Source | HTTP | Exact body bytes | Release objects |
| --- | ---: | ---: | ---: |
| obsidian-list | 200 | 450991 | 30 |
| obsidian-latest | 200 | 13889 | 1 |
| neovim-list | 200 | 822243 | 30 |
| neovim-latest | 200 | 24511 | 1 |
| wezterm-list | 200 | 2935205 | 64 |
| sqlitebrowser-list | 200 | 630919 | 42 |

Counts describe these pages, not full repository release histories. Pagination
links were retained but not followed. Bytes remain exact; no reserialization was
used to preserve responses. Offline verification matched every body length/hash,
Content-Length, request ID, URL, repository ID and monotonic-order wall timestamps.
All bodies parsed as the expected list or latest object with integer release IDs
and string tags. This is basic structural checking, not full content validation or
binary authenticity. Per-attempt elapsed times were below two seconds and each
remained below the 30-second bound.

## Exact provenance and control plane

- Source/checkout/workflow/approved revision:
  `79159ba68f4f4c50bcf050e2e6c908af3a799fd0`.
- Manifest SHA256:
  `1c550b882e9855a7a652e44516d88db95046641da92f4b6e34fd65b9a6da87b9`.
- Runtime repository ID: 1291019762; main-marek; workflow_dispatch; run attempt 1.
- The installed workflow is the approved proposal with only its obsolete inactive
  comment replaced. Manual-only trigger, contents:read, five-minute timeout,
  pinned checkout/upload, no checkout credentials and no publication writer.
- All 49 local offline tests passed before dispatch. Live workflow preflight passed
  before the token-bearing step. No real token was used locally.
- Before dispatch, verified exact remote branch SHA, repository/default-branch,
  manifest preflight and Actions settings. Disabled the historical quota probe.
  Only Restricted catalog validation was active; all six other workflows were
  disabled_manually. No run was pending before dispatch. Rechecked isolation after.

Every response reported the core budget limit as 5,000; remaining values in request
order were 4,999, 4,999, 4,998, 4,998, 4,997 and 4,996. Recorded response counters
and reset times are preserved verbatim; they do not supply one clean global delta
and no extra rate_limit request was made to reconcile them. All exceeded the
collector's 100-point reserve. No auth, quota or timeout refusal occurred.

## Persistent evidence

[Exact response archive](supervised-baseline-40529551070-evidence.tar.gz) includes
six entity bodies, the original adapter report, Actions run/job metadata,
manifest/workflow snapshots and post-run workflow/permission states.
Archive SHA256: `037f19a159d8788fcb95c4d6a8fe182ee44d3c452412bb3da826e3b94ba45dd9`; 321230 bytes.
[Machine checks](supervised-baseline-40529551070-checks.json) record per-body hashes,
coverage, timing and limits. Every body hash was verified again from the archive.
The Actions artifact retains its configured seven-day expiry; these Git-tracked
copies persist independently. No Authorization/request token was written into
these reports or emitted by the workflow.

## What this establishes and what remains

The supervised release adapter completed a real direct HTTPS/DNS/TLS path and six
numeric routes under the restricted workflow wiring, with complete bounded public
responses and successful artifact delivery. It is the first real baseline through
this adapter. The prior historical quota/churn experiments are separate evidence.

One successful sample is not an adversarial audit, fleet-capacity/retention study,
or a Python compatibility matrix. Runner Python version was not explicitly
recorded. Python 3.14.4/Linux remains the local offline-test runtime; this successful
Ubuntu 24.04 job adds one live runner configuration without an exact version claim.
Storage integration, full release-content/publication validation, remote catalog
delivery, freshness lookup and installer migration remain separate work. No day
observation or 24-hour wait is needed before that work. Further live collection
requires a new explicit instruction; this workflow remains manual-only.
