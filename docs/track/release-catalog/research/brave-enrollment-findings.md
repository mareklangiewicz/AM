# Brave identity and release evidence

2026-10-31, ticket [47](../issues/47-enroll-scoped-migration-sources.md).
The user explicitly approved proceeding with the bounded identity and release
checks without waiting for a natural seven-source repeat. This supersedes the
wait-before-evidence sequencing in the earlier preparation and enrollment plan;
operational enrollment remains separate. Exactly two unauthenticated GETs ran,
one per stage, with no redirect, retry, pagination or binary download.

## Identity

`https://api.github.com/repos/ivan-hc/Brave-appimage` returned HTTP 200,
repository ID **947512058**, expected full_name, private=false, visibility=public.
The retained [runner, body, headers and report](brave-identity-20261031/report.json)
record 5,249 body bytes, 1,325 header bytes and 0.441100 seconds.
Body SHA256: `eef2bdef68228a54afd5f29fb9980383d0e4d42b02a01891644d36908833751a`.
The reviewed runner changes only URL and expected name from the retained am-utils
identity procedure. Both streams remain capped at 64,000 bytes, header values at
8,192 bytes, with 10-second connect and supervised 30-second total deadline.

## Numeric release evidence

After validating identity and exact body hash, one GET to
`https://api.github.com/repositories/947512058/releases` returned HTTP 200:
639,169 body bytes, 1,445 header bytes, 1.060596 seconds, 30 releases / 336 assets.
[Exact report](brave-release-20261031/report.json), neighboring body/headers and
runner retain provenance. Body SHA256:
`e4600d3b81b1d8cf130b8b510b556bd0681a98caa67aa2c2bf8e56c5adbe7402`.
The unchanged release transport enforces 8,000,000-byte body / 64,000-byte header
limits, 8,192-byte header values and the same connect/absolute deadlines.
Pinned representation is API version 2022-11-28, Accept application/vnd.github+json,
identity encoding. No ambient authentication, proxy, curl config or netrc was used.
The response advertises page 2 through page 14; none was requested. This preserves
the recipes' original unpaginated `/releases` contract.

Request ID: `cc6d925dcd7e84d969cfdd6b8f3413a13855b37dca9fc6e569b38a36a967fff8`.
Consumer alias remains exactly
`https://api.github.com/repos/ivan-hc/Brave-appimage/releases`.
The candidate queue now records the observed mapping; it remains a non-loadable
review queue. Do not reuse the identity response's validators for releases.

## Original selectors and remaining boundary

The reproducible [offline audit](brave-release-20261031/audit-selectors.py) verifies
all six frozen recipe fingerprints and replays each exact install/update pipeline
against the retained body. [Result](brave-release-20261031/selector-report.json):
**12/12** selectors choose actual browser_download_url assets, zero missing.
Stable/beta/nightly and aarch64/x86_64 policies are unchanged. No installer, updater
or downloaded executable was run. Current metadata compatibility is established
for these six paths only; this does not establish AppImage runtime compatibility.

Next is offline preparation/review of an eight-source contract and resource replay,
followed by separately authorized operational publication/source/pin coordination.
No operational manifest/count guard, workflow, source pin, publication, recipe or
host payload changed. Ticket 47 stays partial and ticket 49 remains blocked until
accepted published observations exist. Natural seven-source repeat remains an
independent unobserved item; this baseline cannot establish conditional behavior,
retention/churn or scheduled execution. The other 49 deferred endpoints remain
unrequested in this continuation. All new evidence is local/uncommitted.
