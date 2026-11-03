# Bound YAML reader memory

Type: prototype
Status: resolved
Triage: ready-for-agent

Continue ticket 71 with an isolated resource experiment. Test whether record-scoped
validation and private output spooling preserve full-document refusal while
removing memory growth with release/asset/app counts. Preserve the accepted schema
and selection boundary. No production integration, push, pin, workflow dispatch,
or installed-host mutation.

Compare the existing acceptance corpus on mawk, GNU awk and BusyBox awk. Measure
release-count growth, one asset-heavy release, and app-map growth. Capture source
on a separate research branch and record limits before recommending a strategy.

## Answer

Record-scoped validation plus private output spooling preserves the contract;
nine acceptance groups pass on mawk, GNU awk and BusyBox awk. Memory is roughly
flat on mawk/GNU awk for measured shapes, but BusyBox grows to 54,360 KiB on a
16,379,135-byte fixture. Reusing fixed keys does not remove that growth and is
slower. Portable constant RSS is not established; keep measured file ceilings.

[Findings and limits](../research/yaml-reader-memory-experiment.md).
Prototype: research/yaml-reader-memory at ae1f216b4ce54a730ea38a12aa5c53d822b10d84,
under tools/catalog-yaml-prototype/. No production integration or push.
Ticket 71 remains open for actual budgets, tail measurements and scheduling.
