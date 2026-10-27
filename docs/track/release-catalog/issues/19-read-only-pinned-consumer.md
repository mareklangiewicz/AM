# Read-only commit-pinned catalog consumer

Type: task
Status: resolved
Triage: ready-for-agent

## Scope and authorization

Marek asked to continue; existing push/workflow authorization remains. Implement a
small actual consumer API/CLI for the published six-source catalog. Resolve the
fixed publication ref once or accept an explicit full commit, fetch only pinned
index and selected body, enforce the accepted freshness/integrity/refusal policy,
and return exact body bytes to existing filters without selecting releases.
No installer/updater migration, source collection, publication, schedule or added
credential path is needed. Validate offline and against the existing public commit.

## Acceptance

- Share complete index metadata validation with storage and local pinned reads;
  fetch only the requested body, not all six bodies or branch history.
- Inclusive 24-hour boundary; future/unmeasured/unknown/unavailable/retired/removed
  aliases and integrity failures refuse. Stale acceptance binds full commit, request
  ID and body hash and cannot bypass any other refusal.
- Fixed public catalog hosts, unauthenticated isolated HTTPS, bounded headers/body
  and deadlines, no redirects/retries/upstream fallback or ambient auth/proxy config.
- Resolve at most once, use the same full commit for index/body even if branch moves,
  recheck freshness after IO and emit no partial body on refusal.
- Focused fake-transport/process tests plus bounded public catalog verification;
  preserve exact source/publication provenance and evidence in the tracker.

## Answer

Implemented shared index/read policy, isolated bounded public transport and actual
consumer API/CLI. 80 offline tests pass. Two live CLI lookups used five catalog
GETs total at d612ff34b, returned exact saved Obsidian/Neovim body bytes and passed
existing jq tag filters. [Findings and persistent evidence](../research/consumer-read-findings.md)
record source/pin/hash/freshness provenance and independent artifact comparison.
No source collection, workflow dispatch, publication, schedule or installed-app
change. Next is one opt-in consumer/filter integration without installer execution.
