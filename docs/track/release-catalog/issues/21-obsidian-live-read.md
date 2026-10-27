# Obsidian pinned end-to-end read

Type: task
Status: resolved
Triage: ready-for-agent

## Scope

Marek approved the proposed end-to-end read: invoke the actual --catalog-version
mode at retained publication d612ff34b492b337fe51128f769ec9d262d0ee86,
compare URL/metadata with retained publication evidence and record the result.
No installer execution, selected asset download, collection or workflow dispatch.
No implicit stale consent; a stale refusal is a result to report.

## Answer

Actual /bin/sh app mode -> python3 consumer CLI -> public transport -> existing
asset filter succeeded at source c9f74c7dfc8b30f60a337a28ab6c6b9482193cbd.
Pinned publication d612ff34b492b337fe51128f769ec9d262d0ee86 returned
https://github.com/obsidianmd/obsidian-releases/releases/download/v1.14.5/Obsidian-1.14.5.AppImage
with empty stderr. No shim or injected clock/fetch was used for this invocation.
Metadata records two pinned catalog GETs, no ref resolution and no stale acceptance;
observation age was 6,675.990861 seconds at 2026-10-27T17:35:14.624656+00:00.

[Retained stdout, metadata and checks](../research/obsidian-live-read-20261027/checks.json)
record exact source/pin/digests. Independently opened the ticket 18 retained repeat
artifact ZIP: its 450,991-byte Obsidian release-list body's hash and index hash
match live metadata. Ran both original installer/updater filter pipelines as data
on that saved body; their output exactly matches the live opt-in query URL.
The URL output alone is not a retained copy of the full live body; integrity is
checked by the real consumer and compared here through its metadata.

Initial sandbox invocation refused with empty stdout and fixed diagnostic; its
network request count is unmeasured. Repeated with approved unsandboxed network
access and succeeded. Two GETs describe the successful invocation only. No source
release request, selected asset download, installer body execution, workflow
operation, publication or installed-state change occurred. Python 3.14.4/Linux;
this is one pinned live sample, not a broader compatibility or security audit.

The read-only integration is now verified end to end. Adoption into ordinary AM
updates still needs a decision about consumer distribution/location, opt-in UI and
stale-consent handling; it is not enabled by this verification.
