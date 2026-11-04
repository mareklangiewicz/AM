# Exact downloads now; future target-respecting updates — November 4, 2026

Ticket 105 follows [104's host rehearsal](yaml-host-rehearsal.md). Marek's answer
to the pending AppImage adapter question: “I guess I like exact catalog downloads
more - it's simpler”, with concern about partial upstream adoption and interest
in possibly better self-updates later.

## Current preferred migration direction

Prepare the remaining AppImage adapters around ordinary downloads of the exact
catalog-selected asset. This resolves the pending preferred transfer direction;
it does not implement the 17 adapters, change an installed updater, accept other
release-selection rules/caps or authorize publication. The previous unreturned-
answer note in ticket 104 describes that earlier checkpoint and is superseded
by this preference. Its audit hashes and frozen package remain unchanged.

Removing embedded self-update from a migrated updater is an intentional behavior
change, not claimed equivalence. In particular, AppImageUpdate's existing patch
records the URL actually used by embedded self-update. A new direct-download
adapter must record the selected/downloaded URL honestly and preserve that patch's
regression case as migration evidence; do not silently delete it in the live
updater or erase its historical explanation. Refresh/channel rules, version
identity, layouts and rollback need their own adapter-specific treatment.

## Keep selection and acquisition distinct

ADR 0001 assigns release/asset choice to clients using catalog facts. Asset
acquisition obtains the already selected asset. Direct download is today's
simple implementation, not a permanent claim that delta transfers or suitable
native updaters cannot work.

A later mechanism may reconstruct the selected asset from the installed bytes
or use an updater that can target it explicitly. It must preserve the selected
record/source/freshness/consent contract and stage its result before replacement.
Embedded metadata must not silently choose a different target or make a stale
selection acceptable. Selecting a target again is a new policy/acceptance step,
not an invisible transfer fallback.

For example, selecting release A must not permit embedded metadata to install
release B. A delta reconstruction that demonstrably produces the selected A
artifact could be compatible. Failure may fall back to an ordinary download of
that same selected asset before installation; it must not install a partial or
unverified reconstruction.

The current six-line shell handoff identifies the publication, repository,
release, asset, observation and URL; it does not carry a target digest or enforce
binary digest verification in the direct-download lifecycle. Matching a URL/tag
alone does not prove byte identity, especially when assets change in place.
A future delta implementation would need an explicit integrity/provenance
contract and probably additional handoff fields. Where a trusted expected digest
is available, verify the reconstructed staged result against it. An upstream-
provided digest establishes consistency with that trusted observation, not
independent publisher authenticity. Without adequate target verification, keep
full download rather than claim the optimization is equivalent.

No plugin interface, backend switches or new checksum guarantee are introduced
by this note. Extract an acquisition seam when there is a concrete second
implementation to test; the conceptual boundary is enough for now.

## Partial upstream adoption remains a viable proposal shape

This is an architectural option, not a prediction about current upstream policy
or maintainer acceptance. No current upstream code or position was queried.
We can propose catalog facts/reader and a few opted-in recipes independently of
converting every installer and updater. Other recipes can keep their existing
mechanisms during that opt-in stage. Existing local mixed managed/legacy manager
routing is evidence that our fork supports incremental migration; it is not a
claim that upstream has accepted that interface or behavior.

Within catalog-controlled recipes, keeping an existing mechanism is compatible
only when its target/acceptance behavior is made explicit. Preserving blind
embedded target overrides would weaken the selected-asset promise. A future
proposal can therefore separate (1) catalog/client selection, (2) adapters that
preserve installation behavior, and later (3) optional verified delta acquisition.
It need not ask upstream to adopt every fork decision as one inseparable change.

This direction is reversible at the acquisition boundary. The immediate migration
can stay simple while avoiding a design that conflates “choose the update” with
“retrieve its bytes.” No runtime or operational action occurred in ticket 105.
