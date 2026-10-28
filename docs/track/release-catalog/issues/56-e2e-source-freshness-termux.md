# Verify installed source switching, freshness boundary and Termux recovery

Type: task
Status: resolved
Triage: ready-for-agent

## Scope

User authorized continuing e2e coverage: verify manager repository changes versus
standalone embedded source, inclusive 48-hour CLI freshness limit, and native
Termux partial-transfer/removal/reinstall behavior. Use existing offline containers;
no host delivery, live collection, source push or production workflow changes.

## Answer

Added whole-command source-switch verification using explicit alternate offline
repository routing and original-URL transport traces. Managed updates follow
changed manager configuration; standalone saved recipes retain embedded source.
Exact Decimal-derived 48-hour CLI acceptance passes; one microsecond beyond
refuses and preserves the full installed tree. Native Termux now writes truncated
staging bytes before transfer failure, verifies working binary/version survival
and retry, and runs the shared AppMan removal/reinstall/configuration scenario.

Final selected runs pass 13 Debian + 13 Fedora + 8 Termux scenarios, with zero
unexpected requests. [Results and source/image identity](../research/e2e-source-freshness-termux-checks.json)
record separate successful runs and the initial Debian test-assumption failure.
Successful unchanged manager verification refreshes optional checksum evidence;
the corrected test compares binary/version on success and the full tree on refusal.
No production fix was needed. Python syntax and diff checks pass. No host app
operation, live upstream request, source push or workflow change occurred.
