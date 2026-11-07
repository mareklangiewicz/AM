# Prepare the next verified catalog cohort

Type: task
Status: resolved
Triage: ready-for-agent
Assignee: codex
Blocked by: 146

Continue 138 with a bounded cohort targeting at most 320 distinct sources under
the deployed 500-source ceiling. Recheck pinned discovery bindings, public numeric
identities and release probes, with explicit rename checks. Keep proposals separate
from enrollment until verification succeeds. Measure fresh full-scope collection
and exact-current-parent local publication, retaining existing app/source identities,
release IDs and effective observations. Record density and resource bounds before
preparing a concrete push/publication package. No installed-host or recipe changes.

## Answer

Prepared 97 verified catalog-only additions: 325 apps / 320 numeric sources.
198 bounded identity/probe reads check all bindings, one rename and two explicit
exclusions. Fresh full-scope local preflight successfully observes all 320 sources,
zero failures, with exact-parent publication and bounded exact-pin readback.
All prior app/source identities, retained release IDs and effective observation
semantics are preserved. YAML totals 44,626,132 bytes, largest 1,372,340;
240,500,606 response bytes, 365.76 seconds acquisition, 734.92 seconds controller
including readback, 657,068 KiB peak RSS under 1 GiB. Existing bounds are unchanged.
All 159 collector regressions pass. [Report/receipts](../research/next-320-catalog-expansion.md)
record measured history and the corrected initial local wrapper attempt.
[148](148-publish-320-source-cohort.md) awaits Marek's push/publication call.
No remote publication or installed-host changes; broad 138 remains claimed.
