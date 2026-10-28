# Make normal batch updates work with migrated recipes

Type: task
Status: open
Triage: ready-for-agent
Blocked by: 42

## Scope

Remove the current explicit-single-app restriction for migrated recipes and make
normal `am -u`/explicit batches work with both catalog and remaining legacy apps.
Build on the common lifecycle interface rather than executing duplicated app
update implementations. Design visible per-app unchanged/updated/refused/failed
results and aggregate nonzero failure status; preserve legacy support still used.

Resolve/pin catalog consistently for the command and avoid unnecessary repeated
lookup transfer where a small shared implementation suffices. No token/proxy/quota
patching or app mutation before accepted metadata for migrated apps. Refusal of
one app must be visible and must not turn into an unconditional direct-API fallback.
Decide/document continuation behavior across failures before implementation.

Exercise actual manager dispatch and both app categories in temporary roots with
controlled operations, including no-argument updates, explicit/mixed batches,
nonzero status propagation, freshness/refusal and current AMREPO handoff. No host
fleet migration, app execution, new collection or schedule work is authorized by
this ticket. Ticket 43 is independent once 42 is complete; it is not a batch-work
prerequisite.
