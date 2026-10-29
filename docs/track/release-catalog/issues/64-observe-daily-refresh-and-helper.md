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

The installed helper is still the pilot's 24-hour version. Marek prefers running
privileged host commands himself; provide:

```sh
sudo install -m 644 /home/marek/code/shell/AM/modules/catalog.am /opt/am/modules/catalog.am
```

After he runs it, verify installed hash equals
`5c1ca600e478ef26ec7ff3c70ef4bd61f49f6e86ff66696e722a9e9b90255618`.
Do not claim all installed consumers are updated: embedded/AppMan copies may
need separate delivery. No app install/update/run is part of this task.

Activation evidence is a local follow-up commit, deliberately unpushed to preserve
the exact reviewed remote source pin. A future push requires reviewed repinning.
