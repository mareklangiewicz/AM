# Re-point catalog-only rows whose app upstream renamed

Type: task
Label: implementation:task
Status: resolved
Blocked by: none

## Outcome

Each catalog-only row names the app its source serves today, so the catalog
offers facts under the name a user installs.

## Why

The first upstream merge (ticket 18) moved deleted recipes' identities to
`collection-apps.json` and listed their sources as to retire. Nine of those
sources are still downloaded from by an upstream recipe under a new name, so
ticket 21 kept them (`retire_sources.py` refuses them):

| Source | Catalog-only app | Recipe naming it now |
| --- | --- | --- |
| 435470319 iongion/container-desktop | podman-desktop-companion | x86_64/container-desktop |
| 993148803 Dpro-at/Girru | agent-player, dpro-agent | x86_64/girru |
| 1052368841 surajmandalcell/hushpen | asrpro | x86_64/hushpen, aarch64/hushpen |
| 1080370450 ParadevAI/Paradev | superset | x86_64/paradev |
| 1111609705 PiwiTests/piwi | platform | x86_64/piwi |
| 1121867723 Broly1/android-webcam-appimage | scrcpy-webcam | x86_64/android-webcam |
| 1327422926 weihubeats/Miyo | rustfox | x86_64/miyo |
| 1361064935 preppie22/shrewnut | gogstash | x86_64/shrewnut |
| 1406304269 hormuz-labs/agentshot | manul | x86_64/agentshot, aarch64/agentshot |

`dabri` (970408916) is the same case, with a declaration as well: its
`speak-to-ai` row also names an app that no longer exists.

## Scope

- Decide whether a renamed app's row is renamed or dropped, and whether
  `merge.py` should do that itself on the next merge.

## Answer — November 22, 2026

Renamed, by one hand edit of `collection-apps.json` (decided with Marek): each
row's `app` is now the name its recipe uses (`container-desktop`, `girru`,
`hushpen`, `paradev`, `piwi`, `android-webcam`, `miyo`, `shrewnut`,
`agentshot`). Girru's second row `dpro-agent` and dabri's `speak-to-ai` row are
gone; each source stays collected under one name. Dropping rows was not an
option: a source no row names is neither active nor retired, which refuses
collection, and `retire_sources.py` refuses these sources.

`source-names.json` is unchanged (source names are identities, not app
names). `merge.py` gets no rename detection: a future stale row is fixed the
same way, by hand, to keep the catalog system lean.

## Comments

November 22, 2026: opened from ticket 21.
