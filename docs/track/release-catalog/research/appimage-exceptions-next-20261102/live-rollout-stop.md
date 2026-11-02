# Approved 65-recipe rollout stopped at client acceptance

Marek approved the exact rollout with “go ahead”. Remote controls matched review;
enrollment `ab04b9d8cb65e9ebbd26a5b6d1b530edc5e8263f` was pushed.
Exactly one [run 41479232632](https://github.com/mareklangiewicz/AM/actions/runs/41479232632)
succeeded: plan, all 16 collectors and atomic publisher. No collection retry or
workflow rerun. Published catalog: `e391f35f61a61fde63e9d12ab10b3deb04f2abfb`,
exact parent `6f21b8c1d2bf271f570a0177bc1068bb9ca43d0a`.

## Acceptance and diagnosis

The first read-only acceptance passed artifact provenance/digests, all-shard/root
recomputation, exact Git parent/modes/paths/blobs and all 1,974 selectors for 987
recipe candidates. It refused at a pinned shell reader. The original helper did
not retain shell stderr, so that first refusal's exact cause is unknown. Both
subsequent standalone shell-reader probes returned expected body hashes.

Added diagnostics that retain returncode, stderr, lengths and hashes before
refusing, without changing exact-byte checks, limits or clock policy. One repeat
of full read-only acceptance again passed all artifact/Git/selector checks.
Wealthfolio shell read passed; Atari refused with `future time, regressed clock
or expired read`. A traced standalone Atari read passed. A bounded ten-read
reproduction loop stopped on the ninth read, capturing wall time moving backwards:
`1793636898.963004` -> `1793636898.461754` (0.501250 seconds). Body length/hash
matched before the clock guard correctly refused emission. The underlying reason
for local wall-clock regression remains undetermined. No production reader bug
or corrupt catalog body was demonstrated.

The original failures are retained, not replaced by successful probes. No complete
acceptance exists. No further full acceptance or collection was attempted after
diagnosis. Seven focused diagnostic/source-binding/clock-guard tests pass. No
system time setting or production reader behavior changed.

## Exact stopped state and next action

- Remote source: enrollment `ab04b9d8cb65e9ebbd26a5b6d1b530edc5e8263f`.
- Catalog: published but client-unaccepted `e391f35f61a61fde63e9d12ab10b3deb04f2abfb`.
- Daily pin remains `f6b3c349cf4d590d0591b9c601bb8ac01c4fc629`.
- Recipe delivery `5ab112d256683d0cbf27d7fb46a670f71e66406c` remains local/unpushed.
- Only catalog-shards.yml and catalog-schedule.yml active; no unfinished run.
- Source/pin mismatch intentionally gates daily dispatch until rollout resolution.

Next establish a stable execution clock, recheck controls, then repeat read-only
acceptance for this same run/source/parent into a fresh directory. Existing
approval continues to cover recipe publication and matching daily pin only after
complete acceptance. It does not authorize system time changes, guard weakening,
collection reruns or silently replacing the reviewed source/parent. Source/catalog
drift requires revising the review. No host sync, binary install, installed-updater
rewrite, yadm pointer bump or rollback occurred.

[Original evidence archive](live-evidence-41479232632.tar.gz) retains both attempts'
metadata, original ZIPs, provenance, logs, exact tree listing, diagnostic probes,
clock traces and final controls. Identical files across attempts are stored once
with length/hash mappings in duplicate-files.json. Temporary bare Git copies are
excluded; the original artifacts remain sufficient for recomputation.
Archive SHA256: `3d059fee0346eabe5d4612c9c388c0cd615287f44ac89bb2032eba7cb508ccd1`.
