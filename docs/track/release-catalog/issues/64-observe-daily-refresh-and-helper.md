# Observe natural daily refresh and host freshness helper delivery

Type: task
Status: open
Triage: ready-for-human

## Scope

Daily activation completed in 41, pinned to
`da0bb8b9768856e69db1b9f6c0b5e77c73f27fd5`. Next nominal run after activation is
2026-10-30T03:17:00Z, best-effort delivery. Observe natural controller/child when
available; retain timestamps, six conditional outcomes, publication parent/tree
and actual freshness. No manual replacement dispatch or automatic future repin.

Original delivery instruction (completed October 29; see verification below):

```sh
sudo install -m 644 /home/marek/code/shell/AM/modules/catalog.am /opt/am/modules/catalog.am
```

After he runs it, verify installed hash equals
`5c1ca600e478ef26ec7ff3c70ef4bd61f49f6e86ff66696e722a9e9b90255618`.
Do not claim all installed consumers are updated: embedded/AppMan copies may
need separate delivery. No app install/update/run is part of this task.

Activation evidence is a local follow-up commit, deliberately unpushed to preserve
the exact reviewed remote source pin. A future push requires reviewed repinning.

## Host delivery verified — 2026-10-29

Marek ran the recorded install command at 10:27 Warsaw. Read-only verification
confirms installed catalog.am exactly matches the 48-hour helper SHA256 above.
Natural daily execution remains unobserved; other installed consumers are not
claimed migrated.

The suggested sudo install unintentionally changed the previously marek:marek
file to root:root mode 644 (user's host output). Normal _sync_modules writes
existing modules with unprivileged shell redirection, so future replacement of
this file would fail. Restore previous ownership with user-run
`sudo chown marek:marek /opt/am/modules/catalog.am`, then verify writability.
Ownership restoration has not yet been observed. Prefer normal `am -s` delivery
in future; no privileged copy is needed for this user-owned AM installation.

## Normal synchronization verified — 2026-10-29 10:31 Warsaw

Marek restored catalog.am ownership to marek:marek, then ran `am -s`.
Read-only byte comparison confirms installed APP-MANAGER, catalog.am, appimage.am
and install.am exactly match published revision
`da0bb8b9768856e69db1b9f6c0b5e77c73f27fd5`. Shared runtime delivery is complete
for these system-AM files through normal synchronization. No app reinstall or
installed-updater migration was performed or inferred. Natural daily execution
remains the outstanding observation. Sync output's upstream recipe links are
not evidence that downloads used upstream; exact installed bytes match our fork.
